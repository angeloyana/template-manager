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
            }
        },
        'required': ['placeholders'],
    }

    validate(instance=instance, schema=schema)
