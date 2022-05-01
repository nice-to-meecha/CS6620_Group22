'''
Group 22:
    Stamesha Bello
    Bhavya Duvvuri
    Thara Messeroux
    Maharshi Pathak
    Nic Shepard

This script will produce an EFS.
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

    # Forcing process to sleep, since no available waiter for EFS
    time.sleep(5)
    sg_id = sys.argv[4]
    for subnet_id in [pub_sub1_id, pub_sub2_id, priv_sub1_id, priv_sub2]:
        create_mount_target(file_system_id, subnet_id, sg_id)



if __name__ == "__main__":
    main()
