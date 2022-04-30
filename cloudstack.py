'''
Group 22:
    Stamesha Bello
    Bhavya Duvvuri
    Thara Messeroux
    Maharshi Pathak
    Nic Shepard

This script will generate a CloudFormation stack, according to resources needed
by the EKS cluster to be generated
'''

import boto3, logging, os, sys
from botocore.exceptions import ClientError


CLOUD_FORMATION = boto3.client('cloudformation', region_name = 'us-east-1')



def create_stack(name: str, tag: str):
    '''
    Creates a stack with CloudFormation, according to resources needed
    for an EKS cluster

    :param name: The name of the stack to be created
    :param tag: The tag for th stack

    :return: None
    '''
    
    try:
        CLOUD_FORMATION.create_stack(
                StackName = name,
                TemplateURL = "https://s3.us-west-2.amazonaws.com/amazon-eks/cloudformation/2020-10-29/amazon-eks-vpc-private-subnets.yaml")

    except ClientError as client_error:
        logging.error(client_error)



def wait_until_stack_ready(name: str):
    '''
    Stalls the program until the stack has finished forming

    :param name: The name of the stack, whose status must be "CREATE_COMPETE"
                 for successful execution

    :return: None
    '''
    try:
        print("\nWaiting for stack completion...")
        waiter = CLOUD_FORMATION.get_waiter('stack_create_complete')
        waiter.wait(StackName = name)
        print("{} is complete\n".format(name))

    except ClientError as client_error:
        logging.error(client_error)



def get_vpc_subnet_ids(name: str):
    '''
    Retrieves the VPC and associated subnet IDs of the specified CloudFormation stack

    :param name: The name of the stack, whose VPC and subnet IDs will be revealed

    :return: The VPC and subnet IDs of the provided stack
    '''

    try:
        vpc_id = CLOUD_FORMATION.describe_stack_resources(
                StackName = name,
                LogicalResourceId = "VPC")["StackResources"][0]["PhysicalResourceId"]

        public_subnet1_id = CLOUD_FORMATION.describe_stack_resources(
                StackName = name,
                LogicalResourceId = "PublicSubnet01")["StackResources"][0]["PhysicalResourceId"]

        public_subnet2_id = CLOUD_FORMATION.describe_stack_resources(
                StackName = name,
                LogicalResourceId = "PublicSubnet02")["StackResources"][0]["PhysicalResourceId"]

        private_subnet1_id = CLOUD_FORMATION.describe_stack_resources(
                StackName = name,
                LogicalResourceId = "PrivateSubnet01")["StackResources"][0]["PhysicalResourceId"]

        private_subnet2_id = CLOUD_FORMATION.describe_stack_resources(
                StackName = name,
                LogicalResourceId = "PrivateSubnet02")["StackResources"][0]["PhysicalResourceId"]

        return (vpc_id, public_subnet1_id, public_subnet2_id, private_subnet1_id, private_subnet2_id)


    except ClientError as client_error:
        logging.error(client_error)



def get_control_plane_sg_id(name: str):
    '''
    Retrieves the security group ID -- specifically created for an EKS control plane --
    of the specified CloudFormation stack

    :param name: The name of the stack, whose control plane security group ID will be revealed

    :return: The control plane security group ID of the provided stack
    '''

    try:
        return CLOUD_FORMATION.describe_stack_resources(
                StackName = name,
                LogicalResourceId = "ControlPlaneSecurityGroup")["StackResources"][0]["PhysicalResourceId"]

    except ClientError as client_error:
        logging.error(client_error)



def main():
    '''
    Creates a CloudFormation stack, given the following command line arguments:

    cloudformation.py <stack_name> <stack_tag>

    :CLI arg stack_name: The name of the stack to be created
    :CLI arg stack_tag: The tag for the stack

    :return: None
    '''
    stack_name = sys.argv[1]
    stack_tag = sys.argv[2]
    create_stack(stack_name, stack_tag)
    wait_until_stack_ready(stack_name)



if __name__ == "__main__":
    main()
