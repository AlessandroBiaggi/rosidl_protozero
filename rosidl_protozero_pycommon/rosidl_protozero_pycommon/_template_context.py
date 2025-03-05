from typing import Any
from typing import Dict
from typing import Iterable
from typing import Set

import os
import em
import pathlib

from io import StringIO

from .utils import mix_dicts


class TemplateContext:
    def __init__(
            self, *,
            resolve_paths: Iterable[str or pathlib.Path] = None,
            globals: Dict[str, Any] = None,
    ) -> None:
        self._resolve_paths: Set[pathlib.Path] = (
            set((pathlib.Path(p).absolute() for p in resolve_paths))
            if resolve_paths is not None
            else set()
        )
        self._globals = globals if globals is not None else {}

    def expand_template(
            self,
            template_name: str or pathlib.Path,
            output_file: str or pathlib.Path,
            locals: Any = None,
            resolve_paths: Iterable[str or pathlib.Path] = None,
            encoding: str = 'utf-8',
    ) -> None:
        content = self.evaluate_template(
            template_name,
            locals,
            resolve_paths,
        )

        output_file = pathlib.Path(output_file)

        try:
            if not output_file.exists():
                os.makedirs(str(output_file.parent), exist_ok=True)

            output_file.write_text(content, encoding=encoding)
        except Exception as e:
            raise RuntimeError(f"Error processing template {template_name}") from e

    def evaluate_template(
            self,
            template_name: str or pathlib.Path,
            ctx_locals: Any or None,
            resolve_paths: Iterable[str or pathlib.Path] or None,
    ) -> str:
        ctx_locals = dict(ctx_locals) if ctx_locals is not None else dict()

        all_resolve_paths = (
            {*[pathlib.Path(p).absolute() for p in resolve_paths], *self._resolve_paths}
            if resolve_paths is not None
            else self._resolve_paths
        )

        output = StringIO()
        interpreter = em.Interpreter(
            output=output,
            options={
                em.BUFFERED_OPT: True,
                em.RAW_OPT: True,
            },
        )

        try:
            if (
                    'TEMPLATE' not in self._globals
                    and
                    'TEMPLATE' not in ctx_locals
            ):
                ctx_locals['TEMPLATE'] = (
                    lambda recursive_template_name, *, recursive_resolve_paths=None, **kwargs:
                    self._recursively_evaluate_template(
                        interpreter=interpreter,
                        template_name=recursive_template_name,
                        resolve_paths=(
                            {*recursive_resolve_paths, *all_resolve_paths}
                            if recursive_resolve_paths is not None
                            else all_resolve_paths
                        ),
                        **mix_dicts(ctx_locals, kwargs),
                    )
                )

            ctx_locals = mix_dicts(self._globals, ctx_locals)

            template_path = self._resolve_absolute_template_path(template_name, resolve_paths=all_resolve_paths)
            template_path = str(template_path)

            with open(template_path, 'r') as h:
                content = h.read()

            interpreter.invoke(
                'beforeFile',
                name=template_name,
                file=h,
                locals=ctx_locals,
            )
            interpreter.string(
                data=content,
                name=template_path,
                locals=ctx_locals,
            )
            interpreter.invoke(
                'afterFile',
            )

            return output.getvalue()
        except Exception as e:
            raise RuntimeError(f"Error processing template {template_name}") from e
        finally:
            interpreter.shutdown()

    def _recursively_evaluate_template(
            self, *,
            interpreter: em.Interpreter,
            template_name: str or pathlib.Path,
            resolve_paths: Set[str or pathlib.Path],
            **kwargs: dict,
    ) -> None:
        try:
            template_path = self._resolve_absolute_template_path(template_name, resolve_paths=resolve_paths)
            template_path = str(template_path)

            ctx_locals = mix_dicts(self._globals, kwargs)

            with open(template_path, 'r') as h:
                content = h.read()

            interpreter.invoke(
                'beforeInclude',
                file=h,
                name=template_path,
                locals=ctx_locals,
            )
            interpreter.string(
                data=content,
                name=template_path,
                locals=ctx_locals,
            )
            interpreter.invoke(
                'afterInclude',
            )
        except Exception as e:
            raise RuntimeError(f"Error processing recursive template {template_name}") from e

    def _resolve_absolute_template_path(
            self,
            template_name: str or pathlib.Path,
            *,
            resolve_paths: Set[pathlib.Path],
    ) -> pathlib.Path:
        template_path = pathlib.Path(template_name)
        if template_path.is_absolute():
            return template_path

        for path in resolve_paths:
            abs_template_path = (path / template_path).absolute()
            if abs_template_path.exists():
                return abs_template_path
        else:
            raise RuntimeError(f"Could not resolve template '{template_name}' in {resolve_paths}")
