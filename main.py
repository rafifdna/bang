#!/usr/bin/env python3

import argparse
import boto3
import configparser
import datetime
import os
import sys
import time
from botocore.exceptions import ClientError


def parse_arguments():
    parser = argparse.ArgumentParser(description='Bang: AWS IAM access key rotation tool')
    parser.add_argument('--profile', default='default',
                        help='AWS profile name (default: default)')
    parser.add_argument('--credentials-file', default='~/.aws/credentials',
                        help='Path to AWS credentials file (default: ~/.aws/credentials)')
    parser.add_argument('--user', help='IAM username (default: current user)')
    parser.add_argument('--grace-period', type=int, default=7,
                        help='Number of days to wait before deleting old key (default: 7)')
    parser.add_argument('--force', action='store_true',
                        help='Force rotation even if the user already has two access keys')
    return parser.parse_args()


def get_current_user(session):
    iam = session.client('iam')
    try:
        return iam.get_user()['User']['UserName']
    except ClientError as e:
        print(f"Error getting user: {e}")
        sys.exit(1)


def get_access_keys(iam, username):
    try:
        response = iam.list_access_keys(UserName=username)
        return response['AccessKeyMetadata']
    except ClientError as e:
        print(f"Error listing access keys: {e}")
        sys.exit(1)


def create_new_access_key(iam, username):
    try:
        response = iam.create_access_key(UserName=username)
        return response['AccessKey']
    except ClientError as e:
        print(f"Error creating new access key: {e}")
        sys.exit(1)


def update_credentials_file(credentials_file, profile, access_key):
    credentials_file = os.path.expanduser(credentials_file)
    config = configparser.ConfigParser()
    
    if os.path.exists(credentials_file):
        config.read(credentials_file)
    
    if not config.has_section(profile):
        config.add_section(profile)
    
    config[profile]['aws_access_key_id'] = access_key['AccessKeyId']
    config[profile]['aws_secret_access_key'] = access_key['SecretAccessKey']
    
    os.makedirs(os.path.dirname(credentials_file), exist_ok=True)
    with open(credentials_file, 'w') as f:
        config.write(f)
    
    os.chmod(credentials_file, 0o600)


def deactivate_access_key(iam, username, access_key_id):
    try:
        iam.update_access_key(
            UserName=username,
            AccessKeyId=access_key_id,
            Status='Inactive'
        )
        print(f"Access key {access_key_id} has been deactivated")
    except ClientError as e:
        print(f"Error deactivating access key: {e}")


def delete_access_key(iam, username, access_key_id):
    try:
        iam.delete_access_key(
            UserName=username,
            AccessKeyId=access_key_id
        )
        print(f"Access key {access_key_id} has been deleted")
    except ClientError as e:
        print(f"Error deleting access key: {e}")


def main():
    args = parse_arguments()
    
    credentials_file = os.path.expanduser(args.credentials_file)
    
    session = boto3.Session(profile_name=args.profile)
    
    iam = session.client('iam')
    
    username = args.user or get_current_user(session)
    print(f"Bang: Rotating access keys for user: {username}")
    
    existing_keys = get_access_keys(iam, username)
    
    if len(existing_keys) >= 2 and not args.force:
        print("User already has two access keys. Delete one manually or use --force to automatically deactivate the oldest key.")
        sys.exit(1)
    
    print("Creating new access key...")
    new_key = create_new_access_key(iam, username)
    print(f"New access key created: {new_key['AccessKeyId']}")
    
    print(f"Updating credentials file at {credentials_file}...")
    update_credentials_file(credentials_file, args.profile, new_key)
    print("Credentials file updated with new access key")
    
    print("Waiting 10 seconds for new key to propagate...")
    time.sleep(10)
    
    if len(existing_keys) >= 2 and args.force:
        existing_keys.sort(key=lambda k: k['CreateDate'])
        old_key = existing_keys[0]
        print(f"Deactivating oldest key: {old_key['AccessKeyId']}...")
        deactivate_access_key(iam, username, old_key['AccessKeyId'])
    
    for key in existing_keys:
        if key['AccessKeyId'] != new_key['AccessKeyId']:
            print(f"Deactivating previous key: {key['AccessKeyId']}...")
            deactivate_access_key(iam, username, key['AccessKeyId'])
            
            if args.grace_period > 0:
                deletion_date = datetime.datetime.now() + datetime.timedelta(days=args.grace_period)
                print(f"The key will be permanently deleted after {args.grace_period} days (on {deletion_date.strftime('%Y-%m-%d')})")
                print(f"To delete it manually, run: aws iam delete-access-key --access-key-id {key['AccessKeyId']} --user-name {username}")
            else:
                print(f"Deleting previous key: {key['AccessKeyId']}...")
                delete_access_key(iam, username, key['AccessKeyId'])
    
    print("\nBang! Access key rotation completed successfully!")
    print(f"New Access Key ID: {new_key['AccessKeyId']}")
    print("Note: Keep the Secret Access Key secure, it won't be accessible again.")


if __name__ == "__main__":
    main()