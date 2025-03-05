from typing import Dict
from typing import Iterable
from typing import Tuple

import itertools
import pathlib
import subprocess

from ament_index_python import get_package_share_directory

import google.protobuf.text_format as text_format
import google.protobuf.descriptor_pb2 as descriptor_pb2
import google.protobuf.compiler.plugin_pb2 as plugin_pb2
import google.protobuf.descriptor as descriptor
import google.protobuf.message_factory as message_factory

import rosidl_protozero.options_pb2

from rosidl_protozero_pycommon import \
    TemplateContext, \
    filter_messages, \
    filter_tuples

from ._idl_naming_convention import IdlNamingConvention
from ._deduce_idl_type import PROTOBUF_WELL_KNOWN_TYPES_TO_IDL


def translate(
        *,
        package_name: str,
        input_tuples: Iterable[Tuple[pathlib.Path, pathlib.Path]],
        output_dir: pathlib.Path,
        output_file: pathlib.Path,
        template_dir: pathlib.Path = None,
        include_dir_tuples: Iterable[Tuple[pathlib.Path, pathlib.Path]],
        include_tuples: Iterable[Tuple[str, pathlib.Path]] = None,
        message_tuples: Iterable[str] = None,
) -> Iterable[Tuple[pathlib.Path, str, pathlib.Path, pathlib.Path]]:
    assert all(d.is_absolute() and not f.is_absolute() for d, f in input_tuples)
    assert all(f.is_absolute() for _, f in include_tuples)

    pb_files = []
    proto_files = []

    for base_path, interface_file_path in input_tuples:
        if interface_file_path.suffix == '.proto':
            proto_files.append(base_path / interface_file_path)
        elif interface_file_path.suffix == '.pb':
            pb_files.append(pathlib.Path(base_path / interface_file_path))
        else:
            raise RuntimeError(f"Unsupported file extension '{interface_file_path.suffix}'")

    if proto_files:
        argv = ["protoc"]

        share_dir = get_package_share_directory('rosidl_protozero_adapter')
        share_dir = pathlib.Path(share_dir)

        argv.append(f"-I{share_dir / 'proto'}")

        for base_path, interface_file_path in include_dir_tuples:
            argv.append(f'-I{base_path / interface_file_path}')

        for file in pb_files:
            argv.append(f"--descriptor_set_in={file}")

        if include_tuples:
            for _, path in include_tuples:
                argv.append(f"--descriptor_set_in={path}")

        argv.append(f"--descriptor_set_out={output_file}")

        for file in proto_files:
            argv.append(str(file))

        result = subprocess.run(argv, capture_output=True)
        if result.returncode != 0:
            raise RuntimeError(f"Protoc failed with return code {result.returncode}: {result.stderr.decode()}")

        pb_files.append(output_file)

    all_fdescs = {}
    for pb_file in pb_files:
        with pb_file.open('rb') as f:
            data = f.read()

        fdescs = descriptor_pb2.FileDescriptorSet.FromString(data).file
        for fdesc in fdescs:
            if fdesc.name in all_fdescs:
                raise RuntimeError(f"Duplicate file descriptor '{fdesc.name}'")

            all_fdescs[fdesc.name] = fdesc

    all_messages = {}  # Dict[Tuple[str, ...], Tuple[pathlib.Path, descriptor_pb2.DescriptorProto or descriptor_pb2.EnumDescriptorProto]]
    for fdesc in all_fdescs.values():
        for path_parts in include_dir_tuples:
            if (pathlib.Path(*path_parts) / fdesc.name).is_file():
                fdesc_tuple = *path_parts, fdesc.name
                break
        else:
            raise RuntimeError(f"Could not find file for descriptor '{fdesc.name}'")

        proto_pkg_name = tuple(fdesc.package.split('.')) if fdesc.package else ()

        for dep_msg in itertools.chain(fdesc.message_type, fdesc.enum_type):
            msg_name = *proto_pkg_name, dep_msg.name
            if msg_name in all_messages:
                raise RuntimeError(f"Duplicate message '{'.'.join(msg_name)}'")

            all_messages[msg_name] = fdesc_tuple, dep_msg

        nested_msg_stack = []
        for dep_msg in fdesc.message_type:
            nested_msg_stack.extend([(dep_msg.name, m) for m in dep_msg.nested_type])
            nested_msg_stack.extend([(dep_msg.name, m) for m in dep_msg.enum_type])

        while nested_msg_stack:
            *parent_names, dep_msg = nested_msg_stack.pop()
            msg_name = *proto_pkg_name, *parent_names, dep_msg.name
            if msg_name in all_messages:
                raise RuntimeError(f"Duplicate message '{'.'.join(msg_name)}'")

            all_messages[msg_name] = fdesc_tuple, dep_msg

            if isinstance(dep_msg, descriptor_pb2.DescriptorProto):
                nested_msg_stack.extend([(*parent_names, dep_msg.name, m) for m in dep_msg.nested_type])
                nested_msg_stack.extend([(*parent_names, dep_msg.name, m) for m in dep_msg.enum_type])

    """
    message_names = None
    if message_tuples is not None:
        message_names = filter_tuples(
            str(package_dir),
            str(input_file),
            allowed=[m.name for m in db.messages],
            tuples=message_tuples
        )
    """

    if template_dir is None:
        share_dir = get_package_share_directory('rosidl_protozero_adapter')
        share_dir = pathlib.Path(share_dir)
        template_dir = share_dir / 'resource'
        assert template_dir.exists(), f"Template directory '{template_dir}' does not exist"
    elif not template_dir.exists():
        raise RuntimeError(f"Template directory '{template_dir}' does not exist")

    """
    messages = filter_messages(
        messages=db.messages,
        message_names=message_names,
        strict=strict,
    )
    """

    naming_convention = IdlNamingConvention()

    proto_types = PROTOBUF_WELL_KNOWN_TYPES_TO_IDL.copy()
    for pkg_and_msg_name in all_messages.keys():
        if pkg_and_msg_name in proto_types:
            raise RuntimeError(f"Duplicate message {'.'.join(pkg_and_msg_name)}")

        proto_types[pkg_and_msg_name] = package_name, 'msg', naming_convention.struct(pkg_and_msg_name)

    for dep_pkg_name, interface_file_path in include_tuples:
        with interface_file_path.open('rb') as f:
            data = f.read()

        dep_fdescs = descriptor_pb2.FileDescriptorSet.FromString(data).file
        for dep_fdesc in dep_fdescs:
            dep_proto_pkg_name = tuple(dep_fdesc.package.split('.')) if dep_fdescs.package else ()

            for dep_msg in itertools.chain(dep_fdesc.message_type, dep_fdesc.enum_type):
                dep_msg_name_parts = *dep_proto_pkg_name, dep_msg.name
                if dep_msg_name_parts in proto_types:
                    raise RuntimeError(f"Duplicate message '{'.'.join(dep_msg_name_parts)}'")

                proto_types[dep_msg_name_parts] = dep_pkg_name, 'msg', naming_convention.struct(dep_msg_name_parts)

            dep_nested_msg_stack = []
            for dep_msg in dep_fdesc.message_type:
                dep_nested_msg_stack.extend([(dep_msg.name, m) for m in dep_msg.nested_type])
                dep_nested_msg_stack.extend([(dep_msg.name, m) for m in dep_msg.enum_type])

            while dep_nested_msg_stack:
                *dep_parent_names, dep_msg = dep_nested_msg_stack.pop()

                dep_msg_name = *dep_proto_pkg_name, *dep_parent_names, dep_msg.name
                if dep_msg_name in proto_types:
                    raise RuntimeError(f"Duplicate message '{'.'.join(dep_msg_name)}'")

                proto_types[dep_msg_name] = dep_pkg_name, 'msg', naming_convention.struct(dep_msg_name)

                if isinstance(dep_msg, descriptor_pb2.DescriptorProto):
                    dep_nested_msg_stack.extend([(*dep_parent_names, dep_msg.name, m) for m in dep_msg.nested_type])
                    dep_nested_msg_stack.extend([(*dep_parent_names, dep_msg.name, m) for m in dep_msg.enum_type])

    template_ctx = TemplateContext(
        resolve_paths=[template_dir],
        globals={
            'package_name': package_name,
            'naming_convention': naming_convention,
            'proto_types': proto_types,
        },
    )

    output_paths_names_and_files = []
    for pkg_and_msg_name, (path_parts, message) in all_messages.items():
        included_messages = set()
        if isinstance(message, descriptor_pb2.DescriptorProto):
            for field in message.field:
                if field.type in (descriptor.FieldDescriptor.TYPE_MESSAGE, descriptor.FieldDescriptor.TYPE_ENUM):
                    _, *field_pkg_and_msg_name = field.type_name.split('.')
                    field_pkg_and_msg_name = tuple(field_pkg_and_msg_name)

                    if field_pkg_and_msg_name not in proto_types:
                        raise RuntimeError(f"Unknown message '{field.type_name}'")

                    included_messages.add(f"{'/'.join(proto_types[field_pkg_and_msg_name])}.idl")
                elif field.type == descriptor.FieldDescriptor.TYPE_BYTES:
                    included_messages.add('std_msgs/msg/ByteMultiArray.idl')

        output_file = (output_dir / 'msg' / naming_convention.struct(pkg_and_msg_name)).with_suffix('.idl')
        output_file = output_file.resolve().absolute()

        stamped_output_file = (output_dir / 'msg' / naming_convention.stamped_struct(pkg_and_msg_name)).with_suffix('.idl')
        stamped_output_file = stamped_output_file.resolve().absolute()

        ctx_locals = {
            'pkg_and_msg_name': pkg_and_msg_name,
            'included_messages': included_messages,
            'message': message,
        }

        try:
            template_ctx.expand_template(
                template_name='msg.idl.em',
                output_file=output_file,
                locals=ctx_locals,
            )

            template_ctx.expand_template(
                template_name='msg_stamped.idl.em',
                output_file=stamped_output_file,
                locals=ctx_locals,
            )
        except Exception as e:
            raise RuntimeError(f"Error processing message {message.name}") from e

        output_paths_names_and_files.append((path_parts, pkg_and_msg_name, output_file, stamped_output_file))

    return output_paths_names_and_files
