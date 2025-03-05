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
    filter_messages, \
    filter_tuples

import rosidl_protozero.options_pb2

from ._cpp_naming_convention import CppNamingConvention


def list_generated(
        *,
        package_name: str,
        input_tuples: Iterable[str],
        output_dir: pathlib.Path,
        message_tuples: Iterable[str] = None,
) -> Iterable[pathlib.Path]:
    all_fdescs = {}
    for tuple in input_tuples:
        base_path_or_pkg, relative_path = tuple.rsplit(':', 1)

        if pathlib.Path(base_path_or_pkg).is_absolute():
            base_path = pathlib.Path(base_path_or_pkg)
        else:
            pkg_share_dir = get_package_share_directory(base_path_or_pkg)
            base_path = pathlib.Path(pkg_share_dir)

        with (base_path / relative_path).open('rb') as f:
            data = f.read()

        fdescs = descriptor_pb2.FileDescriptorSet.FromString(data).file
        for fdesc in fdescs:
            if fdesc.name in all_fdescs:
                raise RuntimeError(f"Duplicate file '{fdesc.name}'")

            all_fdescs[fdesc.name] = fdesc

    all_messages = set()  # List[Tuple[str, ...]]
    for fdesc in all_fdescs.values():
        proto_pkg_name = fdesc.package.split('.')

        for dep_msg in itertools.chain(fdesc.message_type, fdesc.enum_type):
            msg_name = *proto_pkg_name, dep_msg.name
            if msg_name in all_messages:
                raise RuntimeError(f"Duplicate message '{'.'.join(msg_name)}'")

            all_messages.add(msg_name)

        nested_msg_stack = []
        for dep_msg in fdesc.message_type:
            nested_msg_stack.extend([(dep_msg.name, m) for m in dep_msg.nested_type])
            nested_msg_stack.extend([(dep_msg.name, m) for m in dep_msg.enum_type])

        while nested_msg_stack:
            *parent_names, dep_msg = nested_msg_stack.pop()
            msg_name = *proto_pkg_name, *parent_names, dep_msg.name
            if msg_name in all_messages:
                raise RuntimeError(f"Duplicate message '{'.'.join(msg_name)}'")

            all_messages.add(msg_name)

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

    generated_files = [
        *map(lambda m: output_dir / naming_convention.struct_interface_header_path(m), all_messages),
        *map(lambda m: output_dir / naming_convention.struct_tags_header_path(m), all_messages),
        *map(lambda m: output_dir / naming_convention.struct_encode_header_path(m), all_messages),
        *map(lambda m: output_dir / naming_convention.struct_decode_header_path(m), all_messages),
    ]

    generated_files = map(pathlib.Path.resolve, generated_files)
    generated_files = map(pathlib.Path.absolute, generated_files)

    return generated_files
