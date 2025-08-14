
import logging
import re


import click

from src import commands



log = logging.getLogger(__name__)




@click.group()
@click.option("--pg-dsn", required=False, envvar="PG_DSN", type=str)
@click.pass_context
def cli(
    ctx,
    pg_dsn,
):
    ctx.ensure_object(dict)
    log_level = logging.INFO


    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=log_level,
    )
    ctx.obj["PG_DSN"] = pg_dsn




@cli.command()
@click.pass_context
def validate(ctx):
    cmd = commands.Validate()
    cmd.do_run()


@cli.command()
@click.pass_context
def publish_package(ctx):
    cmd = commands.PublishPackage()
    cmd.do_run()

    
