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
from string import Template
from eks_cluster import get_cluster_oidc


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



def create_autoscaler_role(policy_name: str, policy_tag: str, role_name: str, role_tag: str,
        account_id: str, cluster_name: str):
    '''
    Creates an IAM policy and role for the Kubernetes Autoscaler, to be used in conjunction
    with AWS EC2 Auto Scaling Groups.

    :param policy_name: The name of the autoscaler policy to be created
    :param policy_tag: The tag for the autoscaler policy
    :param role_name: The name of the autoscaler role to be created
    :param role_tag: The tag for the autoscaler role
    :param account_id: The 12 digit account ID for the AWS account, with which this
                       script will be run
    :param cluster_name: The name of the EKS cluster to which the autoscaler will be added
    :param autoscaler_oidc: The OpenID Connect Provider URL generated for the autoscaler, via command line

    :return: None
    '''

    try:
        autoscaler_policy = textwrap.dedent('''\
                {
                  "Version": "2012-10-17",
                  "Statement": [
                    {
                      "Action": [
                        "autoscaling:DescribeAutoScalingGroups",
                        "autoscaling:DescribeAutoScalingInstances",
                        "autoscaling:DescribeLaunchConfigurations",
                        "autoscaling:DescribeTags",
                        "autoscaling:SetDesiredCapacity",
                        "autoscaling:TerminateInstanceInAutoScalingGroup",
                        "ec2:DescribeLaunchTemplateVersions"
                        ],
                      "Resource": "*",
                      "Effect": "Allow"
                      }
                    ]
                  }''')

        IAM.create_policy(
                PolicyName = policy_name,
                PolicyDocument = autoscaler_policy,
                Tags = [
                    {
                        'Key': 'Name',
                        'Value': policy_tag
                        }
                    ]
                )

        cluster_oidc = get_cluster_oidc(cluster_name)

        assume_role_policy_template = Template(textwrap.dedent('''\
                {
                  "Version": "2012-10-17",
                  "Statement": [
                    {
                      "Effect": "Allow",
                      "Action": "sts:AssumeRoleWithWebIdentity",
                      "Principal": {
                        "Federated": "arn:aws:iam::${account_id}:oidc-provider/${cluster_oidc}"
                        },
                      "Condition": {
                        "StringEquals": {
                          "${cluster_oidc}:sub": [
                            "system:serviceaccount:kube-system:cluster-autoscaler"
                            ]
                          }
                        }
                      }
                    ]
                  }'''))

        assume_role_policy_dict = {
                'account_id': account_id,
                'cluster_oidc': cluster_oidc
                }
        
        assume_role_policy = assume_role_policy_template.substitute(assume_role_policy_dict)

        IAM.create_role(
                RoleName = role_name,
                AssumeRolePolicyDocument = assume_role_policy,
                Tags = [
                    {
                        'Key': 'Name',
                        'Value': role_tag
                        }
                    ])

        IAM.attach_role_policy(
                RoleName = role_name,
                PolicyArn = "arn:aws:iam::{}:policy/{}".format(account_id, policy_name)
                )

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



if __name__ == "__main__":
    main()
