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


def main() -> None:
    user_tags = load_user_tags(FILE_NAME)

    client = boto3.client('iam')
    for user in user_tags['Users']:
        try:
            client.tag_user(UserName=user['Name'], Tags=user['Tags'])
        except botocore.exceptions.ClientError as error:
            error_code = error.response['Error']['Code']
            if error_code == 'NoSuchEntity':
                print('{}: does not exist'.format(user['Name']))
                continue
            else:
                raise error

    print('finished')

if __name__ == '__main__':
    main()