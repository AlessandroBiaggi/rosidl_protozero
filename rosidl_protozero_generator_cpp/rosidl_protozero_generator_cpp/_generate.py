from typing import Iterable
from typing import Tuple

import pathlib
import itertools

import google.protobuf.text_format as text_format
import google.protobuf.descriptor_pb2 as descriptor_pb2
import google.protobuf.compiler.plugin_pb2 as plugin_pb2
import google.protobuf.descriptor as descriptor
import google.protobuf.message_factory as message_factory

from ament_index_python import get_package_share_directory

from rosidl_protozero_pycommon import \
    TemplateContext, \
    filter_messages, \
    filter_tuples

import rosidl_protozero.options_pb2

from rosidl_protozero_adapter import PROTOBUF_WELL_KNOWN_TYPES_TO_IDL

from ._cpp_naming_convention import CppNamingConvention


def generate(
        *,
        package_name: str,
        input_tuples: Iterable[str],
        output_dir: pathlib.Path,
        template_dir: pathlib.Path = None,
        include_tuples: Iterable[str] = None,
        message_tuples: Iterable[str] = None,
) -> Iterable[pathlib.Path]:
    all_fdescs = {}
    for input_tuple in input_tuples:
        base_path, relative_path = input_tuple.rsplit(':', 1)

        with pathlib.Path(base_path, relative_path).open('rb') as f:
            data = f.read()

        fdescs = descriptor_pb2.FileDescriptorSet.FromString(data).file
        for fdesc in fdescs:
            if fdesc.name in all_fdescs:
                raise RuntimeError(f"Duplicate file '{fdesc.name}'")

            all_fdescs[fdesc.name] = fdesc

    all_messages = {}  # Dict[Tuple[str, ...], Tuple[descriptor_pb2.DescriptorProto or descriptor_pb2.EnumDescriptorProto]]
    for fdesc in all_fdescs.values():
        proto_pkg_name = tuple(fdesc.package.split('.')) if fdesc.package else ()

        for dep_msg in itertools.chain(fdesc.message_type, fdesc.enum_type):
            msg_name = *proto_pkg_name, dep_msg.name
            if msg_name in all_messages:
                raise RuntimeError(f"Duplicate message '{'.'.join(msg_name)}'")

            all_messages[msg_name] = dep_msg

        nested_msg_stack = []
        for dep_msg in fdesc.message_type:
            nested_msg_stack.extend([(dep_msg.name, m) for m in dep_msg.nested_type])
            nested_msg_stack.extend([(dep_msg.name, m) for m in dep_msg.enum_type])

        while nested_msg_stack:
            *parent_names, dep_msg = nested_msg_stack.pop()
            msg_name = *proto_pkg_name, *parent_names, dep_msg.name
            if msg_name in all_messages:
                raise RuntimeError(f"Duplicate message '{'.'.join(msg_name)}'")

            all_messages[msg_name] = dep_msg

            if isinstance(dep_msg, descriptor_pb2.DescriptorProto):
                nested_msg_stack.extend([(*parent_names, dep_msg.name, m) for m in dep_msg.nested_type])
                nested_msg_stack.extend([(*parent_names, dep_msg.name, m) for m in dep_msg.enum_type])

    if template_dir is None:
        share_dir = get_package_share_directory('rosidl_candb_generator_cpp')
        share_dir = pathlib.Path(share_dir)
        template_dir = share_dir / 'resource'
        assert template_dir.is_dir(), f"Template directory '{template_dir}' does not exist"
    elif not template_dir.is_dir():
        raise RuntimeError(f"Template directory '{template_dir}' does not exist")

    """
    message_names = None
    if message_tuples is not None:
        message_names = filter_tuples(
            str(encodeage_dir),
            str(input_file),
            allowed=[m.name for m in db.messages],
            tuples=message_tuples,
        )

    messages = filter_messages(
        messages=db.messages,
        node_names=node_names,
        message_names=message_names,
        strict=strict,
    )
    """

    naming_convention = CppNamingConvention(
        package_name=package_name,
    )

    proto_types = PROTOBUF_WELL_KNOWN_TYPES_TO_IDL.copy()
    for package_and_message_name in all_messages.keys():
        if package_and_message_name in proto_types:
            raise RuntimeError(f"Duplicate message {'.'.join(package_and_message_name)}")

        proto_types[package_and_message_name] = package_name, 'msg', naming_convention.struct(package_and_message_name)

    if include_tuples is not None:
        for include_tuple in include_tuples:
            dep_pkg_name, relpath = include_tuple.rsplit(':', 1)

            dep_shared_dir = get_package_share_directory(dep_pkg_name)
            dep_shared_dir = pathlib.Path(dep_shared_dir)

            with (dep_shared_dir / relpath).open('rb') as f:
                data = f.read()

            dep_fdescs = descriptor_pb2.FileDescriptorSet.FromString(data).file
            for dep_fdesc in dep_fdescs:
                dep_proto_pkg_name = tuple(dep_fdesc.package.split('.')) if dep_fdescs.package else ()

                for dep_msg in itertools.chain(dep_fdesc.message_type, dep_fdesc.enum_type):
                    dep_msg_name_parts = *dep_proto_pkg_name, dep_msg.name
                    if dep_msg_name_parts in proto_types:
                        raise RuntimeError(f"Duplicate message {'.'.join(dep_msg_name_parts)}")

                    proto_types[dep_msg_name_parts] = dep_pkg_name, 'msg', naming_convention.struct(dep_msg_name_parts)

                dep_nested_msg_stack = []
                for dep_msg in dep_fdesc.message_type:
                    dep_nested_msg_stack.extend([(dep_msg.name, m) for m in dep_msg.nested_type])
                    dep_nested_msg_stack.extend([(dep_msg.name, m) for m in dep_msg.enum_type])

                while dep_nested_msg_stack:
                    *dep_parent_names, dep_msg = dep_nested_msg_stack.pop()

                    dep_msg_name = *dep_proto_pkg_name, *dep_parent_names, dep_msg.name
                    if dep_msg_name in proto_types:
                        raise RuntimeError(f"Duplicate message {'.'.join(dep_msg_name)}")

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
            'all_messages': all_messages,
        },
    )

    output_files = []
    for pkg_and_msg_name, message in all_messages.items():
        interface_header_output_file = output_dir / naming_convention.struct_interface_header_path(pkg_and_msg_name)
        interface_header_output_file = interface_header_output_file.resolve().absolute()

        tags_header_output_file = output_dir / naming_convention.struct_tags_header_path(pkg_and_msg_name)
        tags_header_output_file = tags_header_output_file.resolve().absolute()

        encode_header_output_file = output_dir / naming_convention.struct_encode_header_path(pkg_and_msg_name)
        encode_header_output_file = encode_header_output_file.resolve().absolute()

        decode_header_output_file = output_dir / naming_convention.struct_decode_header_path(pkg_and_msg_name)
        decode_header_output_file = decode_header_output_file.resolve().absolute()

        ctx_locals = {
            'pkg_and_msg_name': pkg_and_msg_name,
            'message': message,
        }

        try:
            template_ctx.expand_template(
                template_name='msg.hpp.em',
                output_file=interface_header_output_file,
                locals=ctx_locals,
            )

            template_ctx.expand_template(
                template_name='msg__tags.hpp.em',
                output_file=tags_header_output_file,
                locals=ctx_locals,
            )

            template_ctx.expand_template(
                template_name='msg__encode.hpp.em',
                output_file=encode_header_output_file,
                locals=ctx_locals,
            )

            template_ctx.expand_template(
                template_name='msg__decode.hpp.em',
                output_file=decode_header_output_file,
                locals=ctx_locals,
            )
        except Exception as e:
            raise RuntimeError(f"Error processing message {message.name}") from e

        output_files.append(interface_header_output_file)
        output_files.append(tags_header_output_file)
        output_files.append(encode_header_output_file)
        output_files.append(decode_header_output_file)

    return output_files
