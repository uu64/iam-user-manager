#!/usr/bin/env python3
import boto3
import botocore
import traceback
import yaml
from typing import List


FILE_NAME = 'user_tags.yml'


def load_user_tags(filename: str) -> List:
    try:
        with open(filename) as file:
            user_tags = yaml.safe_load(file)
        return user_tags
    except Exception as e:
        traceback.print_exc()
        raise e


def main():
    iam = boto3.client('iam')
    user_tags = load_user_tags(FILE_NAME)

    try:
        for user in iam.list_users()['Users']:
            name = user['UserName']
            if name in user_tags['users']:
                tags = user_tags['users'][name]
                print('{}: has tags {}'.format(name, tags))
            else:
                print('{}: does not exist in \'{}\''.format(name, FILE_NAME))
    except botocore.exceptions.ClientError as error:
        traceback.print_exc()
        raise error

if __name__ == '__main__':
    main()