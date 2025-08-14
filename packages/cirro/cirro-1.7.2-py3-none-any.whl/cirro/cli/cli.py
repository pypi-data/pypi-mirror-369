import click
from cirro_api_client.v1.errors import CirroException

from cirro.cli import run_ingest, run_download, run_configure, run_list_datasets, run_create_pipeline_config
from cirro.cli.controller import handle_error, run_upload_reference
from cirro.cli.interactive.utils import InputError


def check_required_args(args):
    if args.get('interactive'):
        return
    if any(value is None for value in args.values()):
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        ctx.exit()


@click.group(help="Cirro CLI - Tool for interacting with datasets")
@click.version_option()
def run():
    pass  # Print out help text, nothing to do


@run.command(help='List datasets', no_args_is_help=True)
@click.option('--project',
              help='Name or ID of the project')
@click.option('-i', '--interactive',
              help='Gather arguments interactively',
              is_flag=True, default=False)
def list_datasets(**kwargs):
    check_required_args(kwargs)
    run_list_datasets(kwargs, interactive=kwargs.get('interactive'))


@run.command(help='Download dataset files', no_args_is_help=True)
@click.option('--project',
              help='Name or ID of the project')
@click.option('--dataset',
              help='ID of the dataset')
@click.option('--file',
              help='Name and relative path of the file (optional)',
              default=[],
              multiple=True)
@click.option('--data-directory',
              help='Directory to store the files')
@click.option('-i', '--interactive',
              help='Gather arguments interactively',
              is_flag=True, default=False)
def download(**kwargs):
    check_required_args(kwargs)
    run_download(kwargs, interactive=kwargs.get('interactive'))


@run.command(help='Upload and create a dataset', no_args_is_help=True)
@click.option('--name',
              help='Name of the dataset')
@click.option('--description',
              help='Description of the dataset (optional)',
              default='')
@click.option('--project',
              help='Name or ID of the project')
@click.option('--process',
              help='Name or ID of the ingest process')
@click.option('--data-directory',
              help='Directory you wish to upload')
@click.option('-i', '--interactive',
              help='Gather arguments interactively',
              is_flag=True, default=False)
@click.option('--include-hidden',
              help='Include hidden files in the upload (e.g., files starting with .)',
              is_flag=True, default=False)
def upload(**kwargs):
    check_required_args(kwargs)
    run_ingest(kwargs, interactive=kwargs.get('interactive'))


@run.command(help='Upload a reference to a project', no_args_is_help=True)
@click.option('--name',
              help='Name of the reference')
@click.option('--reference-type',
              help='Type of the reference (e.g., Reference Genome (FASTA))')
@click.option('--project',
              help='Name or ID of the project')
@click.option('--reference-file',
              help='Location of reference file to upload (can specify multiple files)',
              multiple=True)
@click.option('-i', '--interactive',
              help='Gather arguments interactively',
              is_flag=True, default=False)
def upload_reference(**kwargs):
    check_required_args(kwargs)
    run_upload_reference(kwargs, interactive=kwargs.get('interactive'))


@run.command(help='Configure authentication')
def configure():
    run_configure()


@run.command(help='Create pipeline configuration files', no_args_is_help=True)
@click.option('-p', '--pipeline-dir',
              required=True,
              metavar='DIRECTORY',
              help='Directory containing the pipeline definition files (e.g., WDL or Nextflow)',
              default='.',
              show_default=True)
@click.option('-e', '--entrypoint',
              help=(
                  'Entrypoint WDL file (optional, if not specified, the first WDL file found will be used).'
                  ' Ignored for Nextflow pipelines.'),
              default='main.wdl')
@click.option('-o', '--output-dir',
              help='Directory to store the generated configuration files (default: current directory)',
              default='.cirro',
              show_default=True)
@click.option('-i', '--interactive',
              help='Gather arguments interactively',
              is_flag=True, default=False)
def create_pipeline_config(**kwargs):
    check_required_args(kwargs)
    run_create_pipeline_config(kwargs, interactive=kwargs.get('interactive'))


def main():
    try:
        run()
    except InputError as e:
        handle_error(e)
    except CirroException as e:
        handle_error(e)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
