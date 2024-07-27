#!/usr/bin/env zsh

# get the profile name from the first argument
#profile_name=$1
profile_name='sie-cloud-laco-sandbox-nonprod-zz-sjohal'

# extract the access key ID, secret access key, and session token for the profile
aws_access_key_id=$(aws configure get ${profile_name}.aws_access_key_id)
aws_secret_access_key=$(aws configure get ${profile_name}.aws_secret_access_key)
aws_session_token=$(aws configure get ${profile_name}.aws_session_token)

# print the extracted credentials
echo "aws_access_key_id=${aws_access_key_id}"
echo "aws_secret_access_key=${aws_secret_access_key}"
echo "aws_session_token=${aws_session_token}"
