from typing import List

import argparse
import json
import os
import pathlib
import sys

from ament_index_python import get_package_share_directory

from ._translate import translate


def main(argv: List[str] = sys.argv[1:]) -> int:
    parser = argparse.ArgumentParser(
        description="Convert Protobuf files to .idl",
    )

    parser.add_argument(
        '--package-name', type=str, default=None,
        help='The name of the package',
    )
    parser.add_argument(
        '--arguments-file', type=pathlib.Path, required=True,
        help='The JSON file containing the non-idl tuples to convert to .idl',
    )
    parser.add_argument(
        '--output-dir', type=pathlib.Path, default=None,
        help='The base directory to create .idl files in',
    )
    parser.add_argument(
        '--template-dir', type=pathlib.Path, default=None,
        help='The directory containing the templates',
    )
    parser.add_argument(
        '--idl-output-file', type=pathlib.Path, required=True,
        help='The output file containing the tuples for the generated .idl files'
    )
    parser.add_argument(
        '--pkt-output-file', type=pathlib.Path, required=True,
        help='The output file containing the tuples for the generated .idl files'
    )
    parser.add_argument(
        '--spk-output-file', type=pathlib.Path, required=True,
        help='The output file containing the tuples for the generated .idl files'
    )
    parser.add_argument(
        '--pb-output-file', type=pathlib.Path, required=True,
        help='The output .pb file'
    )

    args = parser.parse_args(argv)
    if not (args.arguments_file.exists() and args.arguments_file.is_file()):
        print(
            f"Arguments file {args.arguments_file} does not exist or is not a file",
            file=sys.stderr,
        )
        return -1

    with open(str(args.arguments_file), 'r') as h:
        arguments = json.load(h)

    if args.package_name:
        arguments['package_name'] = args.package_name
    elif 'package_name' not in arguments:
        print(
            f"Package name is required",
            file=sys.stderr,
        )
        return -1

    if args.output_dir:
        arguments['output_dir'] = args.output_dir
    elif 'output_dir' in arguments:
        arguments['output_dir'] = pathlib.Path(arguments['output_dir'])
    else:
        print(
            f"Output directory is required",
            file=sys.stderr,
        )
        return -1

    arguments['output_dir'].mkdir(parents=True, exist_ok=True)

    if args.template_dir:
        arguments['template_dir'] = args.template_dir
    elif 'template_dir' in arguments:
        arguments['template_dir'] = pathlib.Path(arguments['template_dir'])

    if 'interface_tuples' not in arguments:
        print(
            f"Arguments file {args.arguments_file} is not valid: 'interface_tuples' is required",
            file=sys.stderr,
        )
        return -1

    if 'include_dir_tuples' not in arguments:
        print(
            f"Arguments file {args.arguments_file} is not valid: 'include_dir_tuples' is required",
            file=sys.stderr,
        )
        return -1

    idl_tuples = []
    interface_tuples = []
    include_dir_tuples = []
    include_pb_tuples = []

    for interface_tuple in arguments['interface_tuples']:
        base_path, relative_path = map(pathlib.Path, interface_tuple.rsplit(':', 1))
        interface_tuples.append((base_path, relative_path))

    for include_dir_tuple in arguments['include_dir_tuples']:
        base_path, relative_path = map(pathlib.Path, include_dir_tuple.rsplit(':', 1))
        include_dir_tuples.append((base_path, relative_path))

    if 'dependency_tuples' in arguments:
        for dependency_tuple in arguments['dependency_tuples']:
            dependency_package, relative_path = dependency_tuple.split(':', 1)
            dependency_share = get_package_share_directory(dependency_package)
            dependency_share = pathlib.Path(dependency_share)

            include_pb_tuples.append((dependency_package, dependency_share / relative_path))

    try:
        paths_names_and_idl_files = translate(
            package_name=arguments['package_name'],
            input_tuples=interface_tuples,
            output_dir=arguments['output_dir'],
            output_file=args.pb_output_file,
            template_dir=arguments.get('template_dir', None),
            include_dir_tuples=include_dir_tuples,
            include_tuples=include_pb_tuples,
            message_tuples=arguments.get('message_tuples', None),
        )
        idl_tuples.extend([
            (proto_path, '.'.join(message_name), *map(lambda f: f.relative_to(args.output_dir), abs_idl_files))
            for proto_path, message_name, *abs_idl_files in paths_names_and_idl_files
        ])
    except Exception as e:
        raise RuntimeError(f"Could not translate tuples: {interface_tuples}") from e

    try:
        args.idl_output_file.parent.mkdir(parents=True, exist_ok=True)
        args.pkt_output_file.parent.mkdir(parents=True, exist_ok=True)
        args.spk_output_file.parent.mkdir(parents=True, exist_ok=True)

        with (
            args.idl_output_file.open('w') as f,
            args.pkt_output_file.open('w') as g,
            args.spk_output_file.open('w') as h,
        ):
            for proto_path_parts, message_name, interface_relpath, stamped_interface_relpath in idl_tuples:
                f.write(f"{args.output_dir}:{interface_relpath}\n".replace(os.sep, '/'))
                f.write(f"{args.output_dir}:{stamped_interface_relpath}\n".replace(os.sep, '/'))

                g.write(f"{':'.join(map(str, proto_path_parts))}:{message_name}:{args.output_dir}:{interface_relpath}\n".replace(os.sep, '/'))
                h.write(f"{':'.join(map(str, proto_path_parts))}:{message_name}:{args.output_dir}:{stamped_interface_relpath}\n".replace(os.sep, '/'))
    except Exception as e:
        raise RuntimeError(f"Could not write output file") from e

    return 0
