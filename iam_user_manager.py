#!/usr/bin/env python3

import boto3
import botocore
import click
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
        print(v.validate(template))

        return template
    except Exception as e:
        traceback.print_exc()
        raise e


def main() -> None:
    cli()


if __name__ == '__main__':
    main()