import fnmatch
import os
import re
import zipfile
from pathlib import Path

import click
from jsonschema import validate
from prompt_toolkit.validation import ValidationError, Validator

from template_manager.config import TEMPLATES_DIR


class TemplateNameParamType(click.ParamType):
    name = 'template name'

    def __init__(self, exists=False):
        super().__init__()
        self.exists = exists

    def convert(self, value, param, ctx):
        template_exists = (TEMPLATES_DIR / f'{value}.zip').exists()
        if self.exists and not template_exists:
            self.fail(f"'{value}' does not exist.", param, ctx)

        if not self.exists and template_exists:
            self.fail(f"'{value}' already exists.", param, ctx)

        return value


class TemplateNameValidator(Validator):
    def validate(self, document):
        value = document.text
        if not value:
            raise ValidationError(
                message='Please enter the template name.',
                cursor_position=document.cursor_position,
            )

        if (TEMPLATES_DIR / f'{value}.zip').exists():
            raise ValidationError(
                message=f'{value} already exists.',
                cursor_position=document.cursor_position,
            )


def print_error(message: str, start='') -> None:
    click.echo(start + click.style(f'Error: {message}', fg='red'), err=True)


def print_process(message: str, start='') -> None:
    click.echo(start + click.style('i ', fg='cyan') + message)


def print_success(message: str, start='') -> None:
    click.echo(start + click.style('✓ ', fg='green') + message)


def validate_config(instance: dict) -> None:
    schema = {
        '$schema': 'http://json-schema.org/draft-07/schema#',
        'type': 'object',
        'properties': {
            'placeholders': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string'},
                        'prompt': {'type': 'string'},
                        'default': {'type': 'string'},
                        'short_instruction': {'type': 'string'},
                        'long_instruction': {'type': 'string'},
                        'paths': {'type': 'array', 'items': {'type': 'string'}},
                    },
                    'required': ['name', 'prompt', 'paths'],
                },
            },
            'exclude': {'type': 'array', 'items': {'type': 'string'}},
        },
        'required': ['placeholders'],
    }

    validate(instance=instance, schema=schema)


def _compile_path_patterns(patterns: list[str]) -> list[re.Pattern]:
    compiled_patterns: list[re.Pattern] = []
    for pattern in patterns:
        pattern = Path(pattern).as_posix()
        compiled_patterns.append(re.compile(fnmatch.translate(pattern)))

    return compiled_patterns


def _should_exclude(root: str, basename: str, patterns: list[re.Pattern]) -> bool:
    for pattern in patterns:
        if pattern.match(basename) or pattern.match(os.path.join(root, basename)):
            return True
    return False


def zip_dir(output: str | Path, target_dir: str | Path, exclude: list[str]) -> None:
    exclude_patterns = _compile_path_patterns(exclude)

    with zipfile.ZipFile(output, 'w') as zf:
        for root, dirs, files in os.walk(target_dir):
            rel_root = os.path.relpath(root)

            for dirname in dirs:
                if _should_exclude(rel_root, dirname, exclude_patterns):
                    dirs.remove(dirname)
                else:
                    zf.writestr(os.path.join(rel_root, dirname) + '/', '')

            for file in files:
                if not _should_exclude(rel_root, file, exclude_patterns):
                    zf.write(os.path.join(root, file), os.path.join(rel_root, file))
