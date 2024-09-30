import json
import os
import shutil
from pathlib import Path

import click
import jsonschema
from click.exceptions import Abort, ClickException
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from jinja2 import Template

from template_manager.config import TEMPLATES_DIR
from template_manager.utils import (
    TemplateNameParamType,
    TemplateNameValidator,
    print_error,
    print_process,
    print_success,
    validate_config,
)


@click.group()
@click.version_option()
def cli():
    """A command-line tool used to create reusable template for different
    programming stack.
    """
    pass


@cli.command(short_help='Initialize new template.')
def init():
    """Initialize a new template by creating '_template.json' in the current
    directory which will serve as the config file for the template.
    """
    config_file = Path.cwd() / '_template.json'
    if config_file.exists():
        click.echo(f'Already have config file at {config_file}')
        return

    with config_file.open('w') as f:
        json.dump(
            {
                '$schema': 'https://raw.githubusercontent.com/angeloyana/template-manager/main/schema.json',
                'placeholders': [],
            },
            f,
            indent=2,
        )
        click.echo(f'Initialized a config file at {config_file}')


@cli.command(short_help='Save the template.')
@click.option(
    '-t',
    '--template-name',
    type=TemplateNameParamType(exists=False),
    help='Save the template with this name.',
)
def save(template_name: str | None):
    """Save the template so it can be used later to generate customized projects."""
    config_file = Path.cwd() / '_template.json'
    if not config_file.exists():
        raise ClickException(
            "Missing '_template.json' in the current directory. Try 'tpm init'."
        )

    if template_name is None:
        template_name = inquirer.text(
            message='Save as:',
            instruction='Template name',
            default=Path.cwd().name,
            validate=TemplateNameValidator(),
        ).execute()

    print_process('Validating the template config...', start='\n')
    with config_file.open() as f:
        config = json.load(f)
        validate_config(config)  # Raises jsonschema.ValidationError for invalid config.

    print_process('Compressing the template...')
    shutil.make_archive(str(TEMPLATES_DIR / template_name), 'zip', Path.cwd())

    print_success(f"'{template_name}' has been saved!", start='\n')


@cli.command(short_help='Generate a project.')
@click.option(
    '-t',
    '--template-name',
    type=TemplateNameParamType(exists=True),
    help='Template to generate from.',
)
@click.option(
    '-o',
    '--output',
    metavar='DIRECTORY',
    type=click.Path(resolve_path=True, path_type=Path),
    help='Directory where template will be generated.',
)
def generate(template_name: str | None, output: Path | None):
    """Generate a project using the chosen template.

    This generates a fully customized project using the values provided for
    each placeholders.
    """
    if not list(TEMPLATES_DIR.glob('*.zip')):
        click.echo('There are no template(s) yet.')
        return

    if template_name is None:
        template_name = inquirer.rawlist(
            message='Pick a template',
            choices=[
                Choice(name=template_file.stem, value=template_file.stem)
                for template_file in TEMPLATES_DIR.glob('*.zip')
            ],
        ).execute()

    if output is None:
        output = Path.cwd() / f'new-{template_name}'
    output.mkdir(parents=True, exist_ok=True)

    print_process('Uncompressing the template...', start='\n')
    shutil.unpack_archive(TEMPLATES_DIR / f'{template_name}.zip', output)

    print_process('Processing placeholders...\n')
    config_file = output / '_template.json'
    with config_file.open() as f:
        config = json.load(f)
        templates_context: dict[str, dict] = {}

        for placeholder in config['placeholders']:
            name = placeholder['name']
            prompt = placeholder['prompt']
            paths = placeholder['paths']
            default_value = placeholder.get('default', '')
            instruction = placeholder.get('short_instruction', '')
            long_instruction = placeholder.get('long_instruction', '')

            value = inquirer.text(
                prompt,
                instruction=instruction,
                long_instruction=long_instruction,
                default=default_value,
            ).execute()

            for path in paths:
                if path in templates_context:
                    templates_context[path][name] = value
                else:
                    templates_context[path] = {name: value}

        for pathname, context in templates_context.items():
            path = output / pathname
            processed_template = Template(path.read_text()).render(**context)
            path.write_text(processed_template)

    print_process('Cleaning up...', start='\n')
    os.remove(config_file)

    print_success(f"'{template_name}' has been generated in {output}", start='\n')


@cli.command(name='list', short_help='Show all the templates.')
def list_command():
    """Show all the saved templates."""
    template_files = list(TEMPLATES_DIR.glob('*.zip'))
    if not template_files:
        click.echo('There are no template(s) yet.')
        return

    click.echo('Templates')
    click.echo('---------')
    for template_file in template_files:
        click.echo(template_file.stem)


def main() -> None:
    try:
        cli(standalone_mode=False)
    # Catch all exceptions here.
    except (ClickException, jsonschema.ValidationError) as e:
        print_error(e.message)
        raise SystemExit(1)
    except Abort:
        click.echo('Aborted.', err=True)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
