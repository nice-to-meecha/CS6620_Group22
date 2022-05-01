'''
Group 22:
    Stamesha Bello
    Bhavya Duvvuri
    Thara Messeroux
    Maharshi Pathak
    Nic Shepard

This script will produce an EFS system.
'''

import boto3, logging, sys, time
from botocore.exceptions import ClientError
from cloudstack import get_vpc_subnet_ids


EFS = boto3.client('efs', 'us-east-1')



def create_file_system(token: str, tag: str):
    '''
    Generates an EFS system, with the provided arguments

    :param token: The token to be utilized
    :param tag: The tag provided 

    :return: The ID of the new file system
    '''

    try:
        return EFS.create_file_system(
                CreationToken = token,
                Tags = [
                    {
                        'Key': 'Name',
                        'Value': tag
                        }
                    ]
                )['FileSystemId']
    except ClientError as client_error:
        logging.error(client_error)


def create_mount_target(file_system_id: str, subnet_id: str, sg_id: str):
    '''
    Create a mount target, onto which EC2 instances can attach

    :param file_system_id: The ID of the file system for which the mount target
                           will be created
    :param subnet_id: The ID of the subnet, in which the mount target will be
                      attached
    :param sg_id: The security group ID of the security group to be applied
                  to the file system

    :return: None
    '''

    try:
        EFS.create_mount_target(
                FileSystemId = file_system_id,
                SubnetId = subnet_id,
                SecurityGroups = [
                    sg_id
                    ]
                )

    except ClientError as client_error:
        logging.error(client_error)



def wait_until_active(efs_creation_token: str):
    '''
    Pauses the process, until the EFS system is available

    :param efs_creation_token: The token used to create the EFS system, for which the process
                               is waiting

    :return: The ID of the speciied file system
    '''

    try:
        print("Waiting for {} to become available".format(efs_creation_token))

        while (EFS.describe_file_systems(CreationToken = efs_creation_token)['FileSystems'][0]['LifeCycleState'] !=
                "available"):
            time.sleep(1)

        print("{} is now available".format(efs_creation_token))

        return EFS.describe_file_systems(CreationToken = efs_creation_token)['FileSystems'][0]['FileSystemId']

    except ClientError as client_error:
        logging.error(client_error)



def get_ip(efs_creation_token: str):
    '''
    Returns the IP address of the provided EFS system

    :param efs_creation_token: The creation token of the EFS system, for which the IP address
                                will be reported

    :return: The IP address of the provided EFS system
    '''

    try:
        efs_id = wait_until_active(efs_creation_token)

        return EFS.describe_mount_targets(
                FileSystemId = efs_id
                )['MountTargets'][0]['IpAddress']

    except ClientError as client_error:
        logging.error(client_error)



def main():
    '''
    Creates an EFS file system and establishes mount targets in relevant subnets

    efs_file_system.py <token> <tag> <sg_id>

    :CLI arg token: The token for the EFS file system to be created
    :CLI arg tag: The tag for the file system
    :CLI arg cloud_stack_name: The name of the cloud stack, from which the VPC
                               and subnets were produced
    :CLI arg sg_id: The ID of the security group, providing the necessary rules
                    for access of the file system
    '''

    token = sys.argv[1]
    tag = sys.argv[2]
    file_system_id = create_file_system(token, tag)

    cloud_stack_name = sys.argv[3]
    vpc_id, pub_sub1_id, pub_sub2_id, priv_sub1_id, priv_sub2 = get_vpc_subnet_ids(cloud_stack_name)

    wait_until_active(file_system_id)

    sg_id = sys.argv[4]
    for subnet_id in [pub_sub1_id, pub_sub2_id, priv_sub1_id, priv_sub2]:
        create_mount_target(file_system_id, subnet_id, sg_id)



if __name__ == "__main__":
    main()
