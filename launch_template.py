'''
Group 22:
    Stamesha Bello
    Bhavya Duvvuri
    Thara Messeroux
    Maharshi Pathak
    Nic Shepard

This script will create a launch template for EC2 instances, such that the
worker nodes -- for the EKS cluster to be generated -- will be properly
configured.

Reference:
    - Base64 Encoding: https://www.geeksforgeeks.org/encoding-and-decoding-base64-strings-in-python/
'''

import boto3, logging, textwrap, base64, sys
from botocore.exceptions import ClientError


EC2 = boto3.client('ec2', region_name = 'us-east-1')



def create_launch_template(name: str, tag: str, user_data: str, key: str = None):
    '''
    Generates a launch template, such that EC2 worker nodes are
    properly configured.

    :param name: The name of the launch template to be generated
    :param tag: Thec tag for the launch template
    :param user_data: Commands to be executed, upon intialization of the EC2 instances
    :param key: The key to be used when SSHing into the instances

    :return: None
    '''

    try:
        if (key):
            EC2.create_launch_template(
                    LaunchTemplateName = name,
                    VersionDescription = "Launch template for EC2 worker nodes",
                    LaunchTemplateData = {
                        'EbsOptimized': False,
                        'InstanceType': 't2.micro',
                        'KeyName': key,
                        'UserData': user_data
                        },
                    TagSpecifications = [
                        {
                            'ResourceType': 'launch-template',
                            'Tags': [
                                {
                                    'Key': 'Name',
                                    'Value': tag
                                    }
                                ]
                            }
                        ]
                    )

        else:
            EC2.create_launch_template(
                    LaunchTemplateName = name,
                    VersionDescription = "Launch template for EC2 worker nodes",
                    LaunchTemplateData = {
                        'EbsOptimized': False,
                        'InstanceType': 't2.micro',
                        'UserData': user_data
                        },
                    TagSpecifications = [
                        {
                            'ResourceType': 'launch-template',
                            'Tags': [
                                {
                                    'Key': 'Name',
                                    'Value': tag
                                    }
                                ]
                            }
                        ]
                    )


    except ClientError as client_error:
        logging.error(client_error)



def main():
    '''
    Creates a launch template for EC2 instances to be utilized as worker nodes
    within an EKS cluster. This function uses the following command line arguments:

    launch_template.py <template_name> <template_tag> <key> <S3_bucket_name>

    :CLI arg template_name: The name of the launch template to be created
    :CLI arg template_tag: The tag for the launch template
    :CLI arg key: The key to be used for SSHing into EC2 worker nodes generated
                  from the launch template
    "CLI arg S3_bucket_name: The name of the S3 bucket, from which EC2 worker nodes
                             will download configuration files
    '''

    template_name = sys.argv[1]
    template_tag = sys.argv[2]
    key = sys.argv[3]
    S3_bucket_name = sys.argv[4]
    user_data = textwrap.dedent('''\
            MIME-Version: 1.0
            Content-Type: multipart/mixed; boundary="//"

            --//
            Content-Type: text/x-shellscript; charset="us-ascii"
            #!/bin/bash
            sudo curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
            sudo unzip awscliv2.zip
            sudo ./aws/install

            --//
            Content-Type: text/x-shellscript; charset="us-ascii"
            #!/bin/bash
            sudo aws s3 cp s3://{}/configuration.yaml /run_home_assistant/config/configuration.yaml
            sudo aws s3 cp s3://{}/secrets.yaml /run_home_assistant/config/secrets.yaml
            sudo aws s3 cp s3://{}/automations.yaml /run_home_assistant/config/automations.yaml
            sudo aws s3 cp s3://{}/scripts.yaml /run_home_assistant/config/scripts.yaml
            sudo aws s3 cp s3://{}/scenes.yaml /run_home_assistant/config/scenes.yaml

            --//
            Content-Type: text/x-shellscript; charset="us-ascii"
            #!/bin/bash

            --//--
            '''.format(S3_bucket_name, S3_bucket_name, S3_bucket_name, S3_bucket_name, S3_bucket_name))
    user_data_ascii = user_data.encode("ascii")
    user_data_b64_bytes = base64.b64encode(user_data_ascii)
    user_data_b64_str = user_data_b64_bytes.decode("ascii")

    create_launch_template(template_name, template_tag, user_data_b64_str, key)



if __name__ == "__main__":
    main()
