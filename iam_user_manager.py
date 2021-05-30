#!/usr/bin/env python3

import boto3
import click
import sys
import traceback
import yaml
from boto3_type_annotations.iam import Client
from botocore import exceptions
from cerberus import Validator
from typing import List

import template_schema
from user import User


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
    users = load_users(template_path)
    for user in users:
        update_user(user)
        update_user_group(user)


@cli.command()
@click.argument('template_path')
def delete(template_path: str) -> None:
    """
    Deletes all iam users listed in the template file.
    """
    print('delete: ' + template_path)


def load_users(file_path: str) -> List[User]:
    try:
        with open(file_path) as file:
            template = yaml.safe_load(file)

        v = Validator(template_schema.schema)
        if not v.validate(template):
            exit_failure('template format is wrong: {}'.format(file_path))

        users = []
        for data in template.get('Users'):
            user = User(
                data.get('Name'),
                data.get('Tags', {}),
                data.get('Groups', [])
            )
            users.append(user)

        return users
    except Exception as e:
        exit_failure(''.join(traceback.format_exception_only(type(e), e)))


def update_user(user: User) -> None:
    try:
        client.create_user(UserName=user.name)
    except exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            # do nothing
            pass
        else:
            exit_failure(''.join(traceback.format_exception_only(type(e), e)))
    except Exception as e:
        exit_failure(''.join(traceback.format_exception_only(type(e), e)))

    tags = [{'Key': k, 'Value': v} for k, v in user.tags.items()]
    if tags:
        try:
            client.tag_user(UserName=user.name, Tags=tags)
        except Exception as e:
            exit_failure(''.join(traceback.format_exception_only(type(e), e)))


def update_user_group(user: User) -> None:
    try:
        res = client.list_groups_for_user(UserName=user.name)
        current = list(map(lambda x: x['GroupName'], res['Groups']))

        for group_name in user.groups:
            if group_name in current:
                continue
            client.add_user_to_group(UserName=user.name, GroupName=group_name)

        for group_name in current:
            if group_name in user.groups:
                continue
            client.remove_user_from_group(UserName=user.name, GroupName=group_name)
    except Exception as e:
        exit_failure(''.join(traceback.format_exception_only(type(e), e)))


def exit_failure(message: str) -> None:
    print(message, file=sys.stderr)
    sys.exit(1)


def main() -> None:
    cli()


if __name__ == '__main__':
    main()