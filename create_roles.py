'''
Group 22:
    Stamesha Bello
    Bhavya Duvvuri
    Thara Messeroux
    Maharshi Pathak
    Nic Shepard

This will create the roles necessary to for the EKS control group and worker nodes
to operate properly.
'''

import os, boto3, logging, textwrap, sys
from botocore.exceptions import ClientError


IAM = boto3.client('iam', region_name = 'us-east-1')


def create_cluster_role(name: str, tag: str):
    '''
    Creates an IAM role to be used by the EKS control group.

    :param name: The name of the EKS cluster role to be created
    :param tag: The tag for the EKS cluster role

    :return: None
    '''

    try:
        IAM.create_role(
                RoleName = name,
                AssumeRolePolicyDocument = textwrap.dedent('''\
                        {
                          "Version": "2012-10-17",
                          "Statement": [
                            {
                              "Effect": "Allow",
                              "Principal": {
                              "Service": "eks.amazonaws.com"
                              },
                              "Action": "sts:AssumeRole"
                            }
                          ]
                        }'''),
                Tags = [
                    {
                        'Key': 'Name',
                        'Value': tag
                        }
                    ])

        IAM.attach_role_policy(
                RoleName = name,
                PolicyArn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy")

    except ClientError as client_error:
        logging.error(client_error)



def create_node_role(name: str, tag: str):
    '''
    Creates an IAM role to be used by the EKS worker nodes.

    :param name: The name of the EKS node role to be created
    :param tag: The tag for the EKS node role

    :return: None
    '''

    try:
        IAM.create_role(
                RoleName = name,
                AssumeRolePolicyDocument = textwrap.dedent('''\
                        {
                          "Version": "2012-10-17",
                          "Statement": [
                            {
                              "Effect": "Allow",
                              "Principal": {
                              "Service": "ec2.amazonaws.com"
                              },
                              "Action": "sts:AssumeRole"
                            }
                          ]
                        }'''),
                Tags = [
                    {
                        'Key': 'Name',
                        'Value': tag
                        }
                    ])

        IAM.attach_role_policy(
                RoleName = name,
                PolicyArn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy")
        IAM.attach_role_policy(
                RoleName = name,
                PolicyArn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly")
        IAM.attach_role_policy(
                RoleName = name,
                PolicyArn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy")
        IAM.attach_role_policy(
                RoleName = name,
                PolicyArn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess")


    except ClientError as client_error:
        logging.error(client_error)



def main():
    '''
    Utilizes 4 command line arguments to create IAM roles for the EKS cluster
    control group and worker nodes:

    create_roles.py <cluster_role_name> <cluster_role_tag> <node_role_name> <node_role_tag>

    :CLI arg cluster_role_name: The name of the EKS cluster role to be created
    :CLI arg cluster_role_tag: The tag for the EKS cluster role
    :CLI arg node_role_name: The name of the EKS worker node role to be created
    :CLI arg node_role_tag: The tag for the EKS worker node role

    :return: None
    '''

    cluster_role_name = sys.argv[1]
    cluster_role_tag = sys.argv[2]
    create_cluster_role(cluster_role_name, cluster_role_tag)
    
    node_role_name = sys.argv[3]
    node_role_tag = sys.argv[4]
    create_node_role(node_role_name, node_role_tag)



main()
