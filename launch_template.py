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
from string import Template


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

    launch_template.py <template_name> <template_tag> <key> <s3_bucket_name> <object_path>

    :CLI arg template_name: The name of the launch template to be created
    :CLI arg template_tag: The tag for the launch template
    :CLI arg key: The key to be used for SSHing into EC2 worker nodes generated
                  from the launch template
    :CLI arg bucket_name: The name of the S3 bucket, from which EC2 worker nodes
                          will download configuration files
    :CLI arg object_path: The relative directory of Home Assistant's config files
    '''

    template_name = sys.argv[1]
    template_tag = sys.argv[2]
    key = sys.argv[3]
    bucket_name = sys.argv[4]
    object_path = sys.argv[5]

    if (object_path[-1] == "/"):
        object_path = object_path[:len(object_path) - 1]

    user_data_template = Template(textwrap.dedent('''\
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
            sudo aws s3 cp s3://${bucket_name}/${object_path}/configuration.yaml /run_home_assistant/config/configuration.yaml
            sudo aws s3 cp s3://${bucket_name}/${object_path}/secrets.yaml /run_home_assistant/config/secrets.yaml
            sudo aws s3 cp s3://${bucket_name}/${object_path}/automations.yaml /run_home_assistant/config/automations.yaml
            sudo aws s3 cp s3://${bucket_name}/${object_path}/scripts.yaml /run_home_assistant/config/scripts.yaml
            sudo aws s3 cp s3://${bucket_name}/${object_path}/scenes.yaml /run_home_assistant/config/scenes.yaml
            sudo aws s3 cp s3://${bucket_name}/${object_path}/.storage/core.config /run_home_assistant/config/.storage/core.config
            sudo aws s3 cp s3://${bucket_name}/${object_path}/.storage/core.restore_state /run_home_assistant/config/.storage/restore_state
            sudo aws s3 cp s3://${bucket_name}/${object_path}/.storage/frontend.user_data_80211d0edaca4b42b9ff98047ab6db4f /run_home_assistant/config/.storage/frontend.user_data_80211d0edaca4b42b9ff98047ab6db4f
            sudo aws s3 cp s3://${bucket_name}/${object_path}/.storage/core.uuid /run_home_assistant/config/.storage/core.uuid
            sudo aws s3 cp s3://${bucket_name}/${object_path}/.storage/core.device_registry /run_home_assistant/config/.storage/core.device_registry
            sudo aws s3 cp s3://${bucket_name}/${object_path}/.storage/auth /run_home_assistant/config/.storage/auth
            sudo aws s3 cp s3://${bucket_name}/${object_path}/.storage/http /run_home_assistant/config/.storage/http
            sudo aws s3 cp s3://${bucket_name}/${object_path}/.storage/lovelace /run_home_assistant/config/.storage/lovelace
            sudo aws s3 cp s3://${bucket_name}/${object_path}/.storage/core.area_registry /run_home_assistant/config/.storage/core.area_registry
            sudo aws s3 cp s3://${bucket_name}/${object_path}/.storage/core.entity_registry /run_home_assistant/config/.storage/core.entity_registry
            sudo aws s3 cp s3://${bucket_name}/${object_path}/.storage/core.analytics /run_home_assistant/config/.storage/core.analytics
            sudo aws s3 cp s3://${bucket_name}/${object_path}/.storage/auth_provider.homeassistant /run_home_assistant/config/.storage/auth_provider.homeassistant
            sudo aws s3 cp s3://${bucket_name}/${object_path}/.storage/person /run_home_assistant/config/.storage/person
            sudo aws s3 cp s3://${bucket_name}/${object_path}/.storage/onboarding /run_home_assistant/config/.storage/onboarding
            sudo aws s3 cp s3://${bucket_name}/${object_path}/.storage/core.config_entries /run_home_assistant/config/.storage/core.config_entries
            sudo aws s3 cp s3://${bucket_name}/${object_path}/.storage/http.auth /run_home_assistant/config/.storage/http.auth

            --//
            Content-Type: text/x-shellscript; charset="us-ascii"
            #!/bin/bash

            --//--
            '''))
    user_data = user_data_template.substitute(
            {
                'bucket_name': bucket_name,
                'object_path': object_path
                }
        )
    user_data_ascii = user_data.encode("ascii")
    user_data_b64_bytes = base64.b64encode(user_data_ascii)
    user_data_b64_str = user_data_b64_bytes.decode("ascii")

    create_launch_template(template_name, template_tag, user_data_b64_str, key)



if __name__ == "__main__":
    main()
