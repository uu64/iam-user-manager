#!/usr/bin/env python3

import boto3
import click
import csv
import secrets
import string
import sys
import traceback
import yaml
from boto3_type_annotations.iam import Client
from botocore import exceptions
from cerberus import Validator
from typing import List, Tuple

import template_schema
from user import User


client: Client = boto3.client("iam")


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.argument("template_path")
def update(template_path: str) -> None:
    """
    Creates/Updates iam users based on the template file.
    """
    try:
        users = load_users(template_path)
    except Exception as e:
        exit_failure("".join(traceback.format_exception_only(type(e), e)))

    for user in users:
        print("{}:".format(user.name))
        is_created = is_tagged = is_group_updated = False
        try:
            is_created, password = create_user(user)
            if is_created:
                output_user_profile(user.name, password)
            is_tagged = tag_user(user)
            is_group_updated = update_user_group(user)
        except Exception as e:
            exit_failure("".join(traceback.format_exception_only(type(e), e)))
        finally:
            show_result(user, is_created, is_tagged, is_group_updated)
            print()


@cli.command()
@click.argument("template_path")
def delete(template_path: str) -> None:
    """
    Deletes all iam users listed in the template file.
    """
    # TODO: implement
    print("delete: " + template_path)


def show_result(
    user: User, is_created: bool, is_tagged: bool, is_group_updated: bool
) -> None:
    if is_created:
        print("IAM user {} has been created.".format(user.name))
    if is_tagged:
        print("{}'s tags has been changed.".format(user.name))
    if is_group_updated:
        print("The group to which {} belongs has been changed.".format(user.name))
    if not (is_created or is_tagged or is_group_updated):
        print("No changes.")


def load_users(file_path: str) -> List[User]:
    with open(file_path) as file:
        template = yaml.safe_load(file)

    v = Validator(template_schema.schema)
    if not v.validate(template):
        exit_failure("template format is wrong: {}".format(file_path))

    users = []
    for data in template.get("Users"):
        user = User(data.get("Name"), data.get("Tags", {}), data.get("Groups", []))
        users.append(user)

    return users


def create_user(user: User) -> Tuple[bool, str]:
    is_created = False
    password = ""

    try:
        client.create_user(UserName=user.name)
        is_created = True
        password = generate_password(8)
        # NOTE: Whether the IAM user should be deleted when create_login_profile fails
        client.create_login_profile(
            UserName=user.name,
            Password=generate_password(8),
            PasswordResetRequired=True,
        )

    except exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "EntityAlreadyExists":
            # do nothing
            pass
        else:
            raise e

    return is_created, password


def tag_user(user: User) -> bool:
    is_tagged = False

    res = client.list_user_tags(UserName=user.name)
    current = {d["Key"]: d["Value"] for d in res["Tags"]}

    if not current.items() >= user.tags.items():
        tags = [{"Key": k, "Value": v} for k, v in user.tags.items()]
        client.tag_user(UserName=user.name, Tags=tags)
        is_tagged = True

    return is_tagged


def update_user_group(user: User) -> bool:
    is_updated = False

    res = client.list_groups_for_user(UserName=user.name)
    current = list(map(lambda x: x["GroupName"], res["Groups"]))

    for group_name in user.groups:
        if group_name in current:
            continue
        client.add_user_to_group(UserName=user.name, GroupName=group_name)
        is_updated = True

    for group_name in current:
        if group_name in user.groups:
            continue
        client.remove_user_from_group(UserName=user.name, GroupName=group_name)
        is_updated = True

    return is_updated


def generate_password(count: int) -> str:
    characters = string.ascii_letters + string.digits
    while True:
        password = "".join(secrets.choice(characters) for _ in range(count))
        if (
            any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and any(c.isdigit() for c in password)
        ):
            break
    return password


def output_user_profile(user_name, password):
    try:
        # TODO: call only once
        account_id = boto3.client("sts").get_caller_identity().get("Account")
        with open("{}.csv".format(user_name), "w") as f:
            writer = csv.writer(f)
            writer.writerow(["username", "password", "url"])
            writer.writerow(
                [
                    user_name,
                    password,
                    "https://{}.signin.aws.amazon.com/console".format(account_id),
                ]
            )
    except Exception as e:
        exit_failure("".join(traceback.format_exception_only(type(e), e)))


def exit_failure(message: str) -> None:
    print(message, file=sys.stderr)
    sys.exit(1)


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
