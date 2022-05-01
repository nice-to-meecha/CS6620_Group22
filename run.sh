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


# Store appropriate AWS account ID (12-digit account identifier)
group22_account_id="911656642006"

# If want to use new database (without saved data), change the following to "true"
new_database="false"


# Installing kubectl
#echo "Installing kubectl..."
#curl -o kubectl https://s3.us-west-2.amazonaws.com/amazon-eks/1.22.6/2022-03-09/bin/linux/amd64/kubectl
#chmod +x ./kubectl
#mkdir -p $HOME/bin && cp ./kubectl $HOME/bin/kubectl && export PATH=$PATH:$HOME/bin
#kubectl version --short --client
#echo ""


# Installing eksctl
#echo "Installing eksctl..."
#curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
#sudo mv /tmp/eksctl /usr/local/bin
#eksctl version
#echo ""


# Creates roles needed for EKS control panel and worker nodes
cluster_role_name="Group22_EKSClusterRole"
cluster_role_tag="cs6620-group22-eks-cluster-role"
node_role_name="Group22_EKSNodeRole"
node_role_tag="cs6620-group22-eks-node-role"
#python3 create_roles.py $cluster_role_name $cluster_role_tag $node_role_name $node_role_tag


# Creates cloud stack, with networking resources (e.g. VPC, subnets, security groups, igw, etc)
stack_name="Group22-CloudFormation-EKS-Stack"
stack_tag="cs6620-group22-cloudformation-eks-stack"
#python3 cloudstack.py $stack_name $stack_tag


# Database credentials
db_name="homeassistant"
username="bello"
password="password"


# COME BACK TO THIS -- IF NEW DATABASE, NEED TO CHANGE ENDPOINT FOR SECRETS.YAML
# PUT NEW DATABASE IN ***PRIVATE*** SUBNETS FOR SECURITY
if [ $new_database == "true" ]
then
	# Creates database to store Home Assistant's data
	db_instance_name="Group22-RDS-database-instance"
	#python3 database.py $stack_name $db_instance_name $db_name $username $password

else
	db_instance_name="mariadb"
	
fi


# Creates S3 bucket to store Home Assistant's config files
s3_bucket_name="group22-home-assistant-config-bucket"
s3_bucket_tag="cs6620-group22-config-s3-bucket"
config_file_dir="ha_config_files/"
#python3 s3_bucket.py $s3_bucket_name $s3_bucket_tag $config_file_dir


# Creates EC2 Launch Template (for EKS worker nodes)
template_name="Group22_EKS_EC2_launch_template"
template_tag="cs6620-group22-eks-ec2-launch-template"
template_key="stamesha-bello-key"
#python3 launch_template.py $template_name $template_tag $template_key $s3_bucket_name $config_file_dir


# Creates EKS cluster
cluster_name="Group22-EKS-cluster"
cluster_role_arn="arn:aws:iam::${group22_account_id}:role/${cluster_role_name}"
cluster_tag="cs6620-group22-eks-cluster"
node_group_name="Group22-EKS-EC2-node-group"
node_role_arn="arn:aws:iam::${group22_account_id}:role/${node_role_name}"
node_group_tag="cs6620-group22-eks-ec2-node-group"
#python3 eks_cluster.py $cluster_name $cluster_role_arn $cluster_tag $stack_name $node_group_name \
#	$node_role_arn $node_group_tag $template_name


# Configures kubectl to communicate with EKS cluster
#aws eks update-kubeconfig --region us-east-1 --name $cluster_name


# Creates IAM OIDC for cluster (for autoscaling and EFS CSI)
#eksctl utils associate-iam-oidc-provider --cluster $cluster_name --approve
#aws eks update-kubeconfig --region us-east-1 --name $cluster_name

autoscaler_policy_name="Group22_EKSAutoscalerPolicy"
autoscaler_policy_tag="cs6620-group22-eks-autoscaler-policy"
autoscaler_role_name="Group22_EKSAutoscalerRole"
autoscaler_role_tag="cs6620-group22-eks-autoscaler-role"

create_autoscaler_role=$(cat <<EOF
from create_roles import create_autoscaler_role

create_autoscaler_role('${autoscaler_policy_name}', '${autoscaler_policy_tag}',
        '${autoscaler_role_name}', '${autoscaler_role_tag}',
        '${group22_account_id}', '${cluster_name}')

EOF
)
#python3 -c "${create_autoscaler_role}"


#kubectl apply -f cluster-autoscaler-autodiscover.yaml

#kubectl annotate serviceaccount cluster-autoscaler -n kube-system \
#	eks.amazonaws.com/role-arn=arn:aws:iam::${group22_account_id}:role/${autoscaler_role_name}

#kubectl patch deployment cluster-autoscaler -n kube-system \
#	-p '{"spec":{"template":{"metadata":{"annotations":{"cluster-autoscaler.kubernetes.io/safe-to-evict": "false"}}}}}'

#kubectl -n kube-system edit deployment.apps/cluster-autoscaler

#kubectl set image deployment cluster-autoscaler -n kube-system \
#	cluster-autoscaler=k8s.gcr.io/autoscaling/cluster-autoscaler:v1.21.2

#kubectl -n kube-system logs -f deployment.apps/cluster-autoscaler

efs_csi_policy_name="Group22_EKS_EFS_CSI_Policy"
efs_csi_policy_tag="cs6620-group22-eks-efs-csi-policy"
efs_csi_role_name="Group22_EKS_EFS_CSI_Role"
efs_csi_role_tag="cs6620-group22-eks-efs-csi-role"

create_efs_csi_role=$(cat <<EOF
from create_roles import create_efs_csi_role

create_efs_csi_role('${efs_csi_policy_name}', '${efs_csi_policy_tag}',
        '${efs_csi_role_name}', '${efs_csi_role_tag}',
        '${group22_account_id}', '${cluster_name}')

EOF
)
#python3 -c "${create_efs_csi_role}"


cat << EOF > efs-service-account.yaml
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: efs-csi-controller-sa
  namespace: kube-system
  labels:
    app.kubernetes.io/name: aws-efs-csi-driver
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::${group22_account_id}:role/${efs_csi_role_name}
EOF

#kubectl apply -f efs-service-account.yaml

#kubectl apply -k "github.com/kubernetes-sigs/aws-efs-csi-driver/deploy/kubernetes/overlays/stable/ecr/?ref=release-1.1"

vpc_id=$(aws eks describe-cluster --name ${cluster_name} --query "cluster.resourcesVpcConfig.vpcId" --output text)
cidr_block=$(aws ec2 describe-vpcs --vpc-ids ${vpc_id} --query "Vpcs[].CidrBlock" --output text)

efs_sg_name="Group22_EKS_EFS"
efs_sg_tag="cs6620-group22-eks-efs-sg"
efs_sg_desc="Security group for EKS EFS"
create_efs_csi_sg=$(cat <<EOF
from database import create_security_group

print(create_security_group('${vpc_id}', '${efs_sg_name}',
        '${efs_sg_tag}', '${efs_sg_desc}'))

EOF
)
efs_sg_id=$(python3 -c "${create_efs_csi_sg}")

efs_sg_rule_tag="ca6620-group22-eks-efs-sg-inbound-rule"
efs_csi_sg_inbound_rule=$(cat <<EOF
from database import add_inbound_rule

add_inbound_rule('${efs_sg_id}', 'tcp', 2049, '${cidr_block}', '${efs_sg_rule_tag}')

EOF
)
#python3 -c "${efs_csi_sg_inbound_rule}"

efs_creation_token="Group22_EKS_EFS_token"
efs_file_tag="cs6620-group22-eks-efs-file-system"
#python3 efs_file_system.py ${efs_creation_token} ${efs_file_tag} ${stack_name} ${efs_sg_id}

kubectl -f kube_ha/ha_depl_serv.yaml
