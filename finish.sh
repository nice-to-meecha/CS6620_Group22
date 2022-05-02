#!/bin/bash

# Group 22:
#     Stamesha Bello
#     Bhavya Duvvuri
#     Thara Messeroux
#     Maharshi Pathak
#     Nic Shepard
#
# This script will finish the creation of resources necessary to use Home Assistant
#
# Store the instance profile ARN of Group22_EKSNodeRole within instance_profile_arn


instance_profile_arn=""


stack_name="Group22-CloudFormation-EKS-Stack-Final-Please"
s3_bucket_name="group22-home-assistant-config-bucket"
efs_creation_token="Group22_EKS_EFS_token"
ec2_tag="cs6620-group22-ec2-helper"
python3 ec2_helper.py ${stack_name} ${s3_bucket_name} ${efs_creation_token} ${ec2_tag} ${instance_profile_arn}

kubectl apply -f kube_ha/

