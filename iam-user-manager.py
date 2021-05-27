#!/usr/bin/env python3

import boto3
import botocore
import click
import traceback
import yaml
from typing import List


client = boto3.client('iam')


@click.group()
def cli():
    pass


@cli.command()
@click.argument("template_path")
def update(template_path: str):
    """
    Creates/Updates iam users based on the template file.
    """
    print("update: " + template_path)


@cli.command()
@click.argument("template_path")
def delete(template_path: str):
    """
    Deletes all iam users listed in the template file.
    """
    print("delete: " + template_path)


def main() -> None:
    cli()


if __name__ == '__main__':
    main()