#!/bin/bash

# Group 22:
#     Stamesha Bello
#     Bhavya Duvvuri
#     Thara Messeroux
#     Maharshi Pathak
#     Nic Shepard
#
# This script will be used to set the ARN of the user as an environment variable.
# This will be used for the sake of creating roles to be utilized by the EKS control
# group and the EC2 worker nodes.
#
# To store the appropriate value, replace the value below with your own ARN.


# Storing AWS account ARN
GROUP22_ARN="arn:aws:iam::911656642006:user/stameshabello_butnotstameshabello"


# Installing kubectl
echo "Installing kubectl..."
curl -o kubectl https://s3.us-west-2.amazonaws.com/amazon-eks/1.22.6/2022-03-09/bin/linux/amd64/kubectl
chmod +x ./kubectl
mkdir -p $HOME/bin && cp ./kubectl $HOME/bin/kubectl && export PATH=$PATH:$HOME/bin
kubectl version --short --client
echo ""


# Installing eksctl
echo "Installing eksctl..."
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin
eksctl version
echo ""


cluster_role_name="Group22_EKSClusterRole"
cluster_role_tag="cs6620-group22-eks-cluster-role"
node_role_name="Group22_EKSNodeRole"
node_role_tag="cs6620-group22-eks-node-role"
python3 create_roles.py $cluster_role_name $cluster_role_tag $node_role_name $node_role_tag


template_name="Group22_EKS_EC2_launch_template"
template_tag="cs6620-group22-eks-ec2-launch-template"
template_key="stamesha-bello-key"
S3_bucket_name="homeassistant-config"
python3 launch_template.py $template_name $template_tag $template_key $S3_bucket_name


stack_name="Group22-CloudFormation-EKS-Stack"
stack_tag="cs6620-group22-cloudformation-eks-stack"
python3 cloudstack.py $stack_name $stack_tag


db_instance_name="Group22-RDS-database-instance"
db_name="homeassistant"
username="bello"
password="password"
python3 database.py $stack_name $db_instance_name $db_name $username $password




# Creates IAM OIDC for cluster (for autoscaling)
# Uncomment this after creating cluster
#eksctl utils associate-iam-oidc-provider --cluster MY-CLUSTER --approve

