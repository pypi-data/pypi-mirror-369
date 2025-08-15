"""
Lace CLI - Minimal command-line interface.
"""

import click
import sys
from pathlib import Path
from . import attest, verify, monitor, about


@click.group()
@click.version_option(version="0.5.3", prog_name="lace")
def main():
    """Lace - AI Training Transparency Protocol"""
    pass


@main.command()
@click.argument('dataset_path', type=click.Path(exists=True))
@click.option('--name', help='Name for the dataset')
def attest_cmd(dataset_path, name):
    """Create attestation for a dataset."""
    try:
        attestation_id = attest(dataset_path, name)
        click.echo(f"✅ Created attestation: {attestation_id}")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('attestation_id')
@click.option('--check-copyright', help='Text to check for copyright')
def verify_cmd(attestation_id, check_copyright):
    """Verify an attestation."""
    try:
        result = verify(attestation_id, check_copyright)
        if result.get('valid'):
            click.echo(f"✅ Attestation {attestation_id} is valid")
        else:
            click.echo(f"❌ Attestation invalid")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command()
def about_cmd():
    """Display information about Lace."""
    about()


if __name__ == '__main__':
    main()