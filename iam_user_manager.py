#!/usr/bin/env python3

import boto3
import botocore
import click
import sys
import traceback
import yaml
from boto3_type_annotations.iam import Client
from botocore import exceptions
from cerberus import Validator
from typing import List

import template_schema


client: Client = boto3.client('iam')


@click.group()
def cli():
    pass


@cli.command()
@click.argument('template_path')
def update(template_path: str):
    """
    Creates/Updates iam users based on the template file.
    """
    template = load_template(template_path)
    for data in template['Users']:
        update_user(data['Name'], data['Tags'] if 'Tags' in data else [])


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
    except Exception as e:
        exit_failure(''.join(traceback.format_exception_only(type(e), e)))


def update_user(name: str, tags: List):
    try:
        client.create_user(UserName=name)
    except exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            # do nothing
            pass
        else:
            exit_failure(''.join(traceback.format_exception_only(type(e), e)))
    except Exception as e:
        exit_failure(''.join(traceback.format_exception_only(type(e), e)))

    if tags:
        try:
            client.tag_user(UserName=name, Tags=tags)
        except Exception as e:
            exit_failure(''.join(traceback.format_exception_only(type(e), e)))


def exit_failure(message: str) -> None:
    print(message, file=sys.stderr)
    sys.exit(1)


def main() -> None:
    cli()


if __name__ == '__main__':
    main()