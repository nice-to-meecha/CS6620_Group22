'''
Group 22:
    Stamesha Bello
    Bhavya Duvvuri
    Thara Messeroux
    Maharshi Pathak
    Nic Shepard

This script will create an EC2 instance specifically used to transfer files
to an EFS file system
'''

import boto3, logging, textwrap, sys
from botocore.exceptions import ClientError
from cloudstack import get_vpc_subnet_ids
from efs_file_system import get_ip
from string import Template


EC2 = boto3.client('ec2', 'us-east-1')



def create_ec2_helper(bucket: str, efs_ip: str, subnet_id: str, instance_profile: str, tag: str):
    '''
    Creates a simple EC2 instance, which will transfer files from an
    S3 bucket, to an EFS file system

    :param bucket: The name of the S3 bucket, from which files will be
                   transferred
    :param efs_ip: The IP address of the EFS, to which the files will be added
    :param instance_profile: The name of the instance profile to be attached to the EC2
                             instance (same as name of role that's attached)
    :param tag: The tag for the new EC2 instance

    :return: The ID of the new EC2 instance
    '''

    try:

        user_data_template = Template(textwrap.dedent('''\
                #!/bin/bash
                sudo curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
                sudo unzip awscliv2.zip
                sudo ./aws/install

                sudo yum -y install nfs-utils

                sudo mkdir /efs-mount-point

                sudo mount -t nfs -o nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport ${efs_ip}:/  /efs-mount-point

                sudo aws s3 cp s3://${bucket}/ha_config_files /efs-mount-point/run_home_assistant/config/ --recursive
                '''))

        user_data = user_data_template.substitute(
                {
                    "bucket": bucket,
                    "efs_ip": efs_ip
                    }
                )

        return EC2.run_instances(
                ImageId = "ami-0f9fc25dd2506cf6d",
                InstanceType = "t2.micro",
                MaxCount = 1,
                MinCount = 1,
                SubnetId = subnet_id,
                UserData = user_data,
                IamInstanceProfile = {
                    'Name': instance_profile
                    },
                TagSpecifications = [
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': tag
                                }
                            ]
                        }
                    ]
                )['Instances'][0]['InstanceId']

    except ClientError as client_error:
        logging.error(client_error)



def wait_until_active(ec2_id: str):
    '''
    Holds the process, until the provided EC2 instance is available

    :param ec2_id: The instance ID of the EC2 instance, for which the
                   program will wait

    :return: None
    '''

    try:
        waiter = EC2.get_waiter('instance_running')

        print("\nWaiting for EC2 helper to finish transferring files")
        waiter.wait(
                InstanceIds = [
                    ec2_id
                    ]
                )

        print("\nThe EC2 helper is finished")

    except ClientError as client_error:
        logging.error(client_error)



def main():
    '''
    Generates an EC2 instance within a public subnet of the provided cloud stack.
    Then, transfers configuration files from an S3 bucket to an EFS system

    ec2_helper.py <cloud_stack> <bucket> <efs_creation_token> <ec2_tag>
        <instance_profile_name> <instance_profile_tag> <instance_profile_role>

    :CLI arg cloud_stack: The name of the cloud stack, from which the VPC and subnet
                          IDs used by the EKS cluster will be revealed
    :CLI arg bucket: The name of the S3 bucket, from which files will be drawn
    :CLI arg efs_creation_token: The creation token of the EFS system, to which files will be copied
    :CLI arg ec2_tag: The tag for the new EC2 instance
    :CLI arg instance_profile_name: The name of the instance profile to be attached to the
                                    EC2 instance, allowing it to necessary duties.
                                    (Same name as role created)
    '''

    cloud_stack = sys.argv[1]
    vpc_id, subnet1, subnet2, subnet3, subnet4 = get_vpc_subnet_ids(cloud_stack)

    bucket = sys.argv[2]
    efs_creation_token = sys.argv[3]
    efs_ip = get_ip(efs_creation_token)

    ec2_tag = sys.argv[4]
    instance_profile_name = sys.argv[5]
    helper_id = create_ec2_helper(bucket, efs_ip, subnet1, instance_profile_name, ec2_tag)

    wait_until_active(helper_id)


if __name__ == "__main__":
    main()
