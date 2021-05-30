#!/usr/bin/env python3

import boto3
import click
import sys
import traceback
import yaml
from boto3_type_annotations.iam import Client
from botocore import exceptions
from cerberus import Validator
from typing import Dict, List

import template_schema


client: Client = boto3.client('iam')


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.argument('template_path')
def update(template_path: str) -> None:
    """
    Creates/Updates iam users based on the template file.
    """
    template = load_template(template_path)
    for data in template['Users']:
        update_user(data['Name'], data['Tags'] if 'Tags' in data else [])
        update_user_group(data['Name'], data['Groups'] if 'Groups' in data else [])


@cli.command()
@click.argument('template_path')
def delete(template_path: str) -> None:
    """
    Deletes all iam users listed in the template file.
    """
    print('delete: ' + template_path)


def load_template(file_path: str) -> List[Dict]:
    try:
        with open(file_path) as file:
            template = yaml.safe_load(file)

        v = Validator(template_schema.schema)
        if not v.validate(template):
            exit_failure('template format is wrong: {}'.format(file_path))

        return template
    except Exception as e:
        exit_failure(''.join(traceback.format_exception_only(type(e), e)))


def update_user(user_name: str, tags: List[Dict]) -> None:
    try:
        client.create_user(UserName=user_name)
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
            client.tag_user(UserName=user_name, Tags=tags)
        except Exception as e:
            exit_failure(''.join(traceback.format_exception_only(type(e), e)))


def update_user_group(user_name: str, groups: List[str]) -> None:
    try:
        res = client.list_groups_for_user(UserName=user_name)
        current = list(map(lambda x: x['GroupName'], res['Groups']))

        for group_name in groups:
            if group_name in current:
                continue
            client.add_user_to_group(UserName=user_name, GroupName=group_name)

        for group_name in current:
            if group_name in groups:
                continue
            client.remove_user_from_group(UserName=user_name, GroupName=group_name)
    except Exception as e:
        exit_failure(''.join(traceback.format_exception_only(type(e), e)))


def exit_failure(message: str) -> None:
    print(message, file=sys.stderr)
    sys.exit(1)


def main() -> None:
    cli()


if __name__ == '__main__':
    main()