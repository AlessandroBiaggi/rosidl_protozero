from typing import List

import pathlib

from rosidl_cli.command.helpers import interface_path_as_tuple
from rosidl_cli.command.translate.extensions import TranslateCommandExtension

from .._translate import translate as translate_proto_to_idl


class TranslateProto2Idl(TranslateCommandExtension):
    @property
    def input_format(self) -> str:
        return 'proto'

    def translate(
            self,
            package_name: str,
            interface_files: List[pathlib.Path],
            _include_paths: List[pathlib.Path],
            output_path: pathlib.Path,
    ) -> List[pathlib.Path]:
        translated_interface_files = []

        for interface_file in interface_files:
            prefix, interface_file = interface_path_as_tuple(interface_file)
            output_dir = output_path / interface_file.parent

            output_files = translate_proto_to_idl(
                package_dir=prefix,
                package_name=package_name,
                input_file=interface_file,
                output_dir=output_dir,
            )

            for output_file in output_files:
                output_file = output_file.relative_to(output_path)
                translated_interface_files.append(
                    f'{output_path}:{output_file.as_posix()}'
                )

        return translated_interface_files
