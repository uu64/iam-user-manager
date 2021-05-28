#!/usr/bin/env python3

import boto3
import botocore
import click
import sys
import traceback
import yaml
from cerberus import Validator
from typing import List

import template_schema


client = boto3.client('iam')


@click.group()
def cli():
    pass


@cli.command()
@click.argument('template_path')
def update(template_path: str):
    """
    Creates/Updates iam users based on the template file.
    """
    print('update: ' + template_path)
    template = load_template(template_path)
    print(template)


@cli.command()
@click.argument('template_path')
def delete(template_path: str):
    """
    Deletes all iam users listed in the template file.
    """
    print('delete: ' + template_path)


def load_template(file_path: str) -> List:
    try:
        with open(file_path) as file:
            template = yaml.safe_load(file)

        v = Validator(template_schema.schema)
        if not v.validate(template):
            exit_failure('template format is wrong: {}'.format(file_path))

        return template
    except yaml.YAMLError:
        exit_failure('invalid yaml file: {}'.format(file_path))
    except FileNotFoundError:
        exit_failure('no such file: {}'.format(file_path))



def exit_failure(message: str) -> None:
    print('[Error] {}'.format(message), file=sys.stderr)
    sys.exit(1)


def main() -> None:
    cli()


if __name__ == '__main__':
    main()