'''
Group 22:
    Stamesha Bello
    Bhavya Duvvuri
    Thara Messeroux
    Maharshi Pathak
    Nic Shepard

This script will generate an EKS cluster, which will later host Home Assistant.
'''

import boto3, logging, sys
from botocore.exceptions import ClientError
from cloudstack import get_vpc_subnet_ids, get_control_plane_sg_id

EKS = boto3.client('eks', region_name = 'us-east-1')



def create_cluster(name: str, arn: str, subnet_ids: list, sg_ids: list, tag: str):
    '''
    Creates an EKS cluster, with the provided name, role arn and tag.

    :param name: The name of the EKS cluster to be generated
    :param arn: The Amazon Resource Name of the control plane IAM role
    :param subnet_ids: List of subnet IDs, in which the EKS cluster will create
                       elastic network interfaces
    :param sg_ids: List of security group IDs, with which the EKS cluster will use
                   to establish communication rules between the components of its
                   control plane
    :param tag: The tag for the EKS cluser

    :return None:
    '''

    try:
        EKS.create_cluster(
                name = name,
                version = '1.21',
                roleArn = arn,
                resourcesVpcConfig = {
                    'subnetIds': subnet_ids,
                    'securityGroupIds': sg_ids
                    },
                tags = {
                    'Name': tag
                    }
                )

    except ClientError as client_error:
        logging.error(client_error)



def create_node_group(cluster_name: str, node_group_name: str, subnet_ids: list,
        node_role_arn: str, tag: str):
    '''
    Creates an EKS-managed node group, which will host the Home Assistant pods

    :param cluster_name: The name of the cluster, to which the node group will be added
    :param node_group_name: The name of the node group to be created
    :param subnet_ids: The subnets within which the node group autoscaler will operate
    :param node_role_arn: The Amazon Resource Name for the IAM role (previously created),
                          allowing EC2 worker nodes to perform appropriate actions
    :param tag: The tag for the node group

    :return: None
    '''

    try:
        EKS.create_nodegroup(
                clusterName = cluster_name,
                nodegroupName = node_group_name,
                scalingConfig = {
                    'minSize': 1,
                    'maxSize': 10,
                    'desiredSize': 2
                    },
                subnets = subnet_ids,
                amiType = 'AL2_x86_64',
                nodeRole = node_role_arn,
                tags = {
                    'Name': tag
                    },
                updateConfig = {
                    'maxUnavailable': 1
                    }
                )

    except ClientError as client_error:
        logging.error(client_error)



def get_cluster_oidc(cluster_name: str):
    '''
    Returns the EKS cluster OpenID Connect Provider URL
    '''

    try:
        print("\nWaiting for {} to be active".format(cluster_name))

        waiter = EKS.get_waiter('cluster_active')
        waiter.wait(name = cluster_name)

        print("\n{} is now active".format(cluster_name))

        return EKS.describe_cluster(name = cluster_name)['cluster']['identity']['oidc']['issuer']\
                .replace("https://", "")


    except ClientError as client_error:
        logging.error(client_error)



def main():
    '''
    Creates an EKS cluster, using the provided values (via CLI arguments):

    eks_cluster.py <cluster_name> <control_panel_arn> <vpc_id> <cluster_tag> <stack_name>

    :CLI arg cluster_name: The name of the EKS cluster to be generated
    :CLI arg control_panel_arn: The Amazon Resource Name of the IAM role
                                used to provide the EKS control panel with
                                proper permissions to perform necessary actions
    :CLI arg cluster_tag: The tag for the EKS cluster
    :CLI arg stack_name: The name of the cloud stack, from which networking
                         resources will be utilized for the EKS cluster components
                         to communicate
    :CLI arg node_group_name: The name of the node group to be created
    :CLI arg node_role_arn: The Amazon Resource Name for the IAM role used
                            to provide the EC2 worker nodes with permissions
                            to perform necessary actions
    :CLI arg node_group_tag: The tag for the EC2 worker node group
    '''

    cluster_name = sys.argv[1]
    control_panel_arn = sys.argv[2]
    cluster_tag = sys.argv[3]
    stack_name = sys.argv[4]

    vpc_id, public_subnet1_id, public_subnet2_id, private_subnet1_id, private_subnet2_id = \
            get_vpc_subnet_ids(stack_name)
    subnet_ids = [public_subnet1_id, public_subnet2_id, private_subnet1_id, private_subnet2_id]

    control_plane_sg_id = get_control_plane_sg_id(stack_name)
    create_cluster(cluster_name, control_panel_arn, subnet_ids, [control_plane_sg_id], cluster_tag)

    # Waiting until cluster finished creating
    get_cluster_oidc(cluster_name)

    node_group_name = sys.argv[5]
    node_role_arn = sys.argv[6]
    node_group_tag = sys.argv[7]
    create_node_group(cluster_name, node_group_name, subnet_ids, node_role_arn, node_group_tag)



if __name__ == "__main__":
    main()
