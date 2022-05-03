# CS6620_Group22

This repo contains the necessary files to launch Home Assistant -- IoT automation and management software --
with some of AWS' many cloud services. In order to run properly, there are a few steps you must follow.


### Steps
1. Locate your 12-digit Amazon account ID and store it within the *group22_account_id* variable of the "run.sh" file.
   Only include the numbers; do not add the hyphens.

    This can be found in a multitude of locations. When in the console, you can see your account ID to the right
    of your username (followed by the '@' symbol).
    
    ![Account ID in the home page of the console](https://i.imgur.com/WcPgIK2.jpg)
    
    This will be used for referencing ARN's of IAM roles, created by the scripts.
    
    The *group22_account_id* variable can be found at the top of the "run.sh" file. Insert your ID accordingly.
    
    ![Location to store account ID in run.sh script](https://i.imgur.com/bVoX6Yv.jpg)
    
    <br />
2. Determine if you want to use a database retaining saved information or an empty one.
   - If you want to reproduce the dashboard shown during the presentation, use the pre-existing database.
        - You will not have to make any changes, in this case.
        
   - If you want to start with a blank slate, you must do two things:
        - Change the value of "new_database" to "true".
         
           ![Location of new_database variable](https://i.imgur.com/q6nsYZE.jpg)
           
        - Go to the "ha_config_files" directory. Delete the ".storage" directory within it,
          with the following command:
           ```
           rm -r .storage
           ```
           
           **This is very important. If you do not delete the ".storage" directory, you won't be able to create**
           **an account, once Home Assistant starts.**
           
           ![Location of .storage file](https://i.imgur.com/rCEAhaD.jpg)
           
           <br />
3. After that, go back to the home directory of the cloned repository (if not already there). Use the following command
   to execute the run.sh script: 
   ```
   sh run.sh
   ```
   
   This step will take quite a bit of time -- even more so if you elected to create a new database.
   The resource stack (made by CloudFormation) and the EKS cluster each take around 10 minutes to become available.
   The database usually takes even more time.
   If you are using the CloudShell to run this, make sure to interact with the environment (click, tap keys, etc)
   every 10 minutes, to prevent it from timing out.
   
   <br />
4. Toward the end of execution of the script, another file will be opened. Under the "spec.template.spec.containers"
   section (near the bottom of the file), add the following lines:
   ```
   - --balance-similar-node-groups
   - --skip-nodes-with-system-pods=false
   ```
   
   ![Location of container section](https://i.imgur.com/EHjdB4s.jpg)
   
   This is what the section should look like, following the addition:
   
   ![What the file should look like after adding the two lines](https://i.imgur.com/X0k4t6w.jpg)
   
   Make sure to save the file, prior to exiting. If using the CloudShell, use ":x" or ":wq" to save and close the file.
   A few more processes will run afterward. This entails more waiting. A warning will arise, indicating deprecation
   of the EFS CSI driver currently in use. Ignore that.
   
   The appearance of "fs-### is now ready" indicates the end of the run.sh script.
   
   ![Picture showing the end of run.sh script](https://i.imgur.com/vNaUNd6.jpg)

    <br /> 
5. Go to the IAM service. Under "Roles", select the newly created "Group22_EKSNodeRole". Refresh the page and then copy
   the **Instance Profile ARN**.
   - It is suggested that you refresh the page, in case the provided Instance Profile ARN is not up-to-date. If running
     this script more than once, it will often retain the old ARN, until the page is refreshed.
     
    ![Location of the Group22_EKSNodeRole](https://i.imgur.com/tkSoOQo.jpg)
    
    ![Location of the instance_profile_name variable](https://i.imgur.com/0sW69am.jpg)
    
    <br />
6. Paste the "Group22_EKSNodeRole" Instance Profile ARN within the *instance_profile_arn* variable of the "finish.sh" file.

    ![Location of the instance_profile_name variable](https://i.imgur.com/FbnqkVw.jpg)
    
    <br />
7. Run the finish.sh file with the following command:
   ```
   sh finish.sh
   ```
   
8. Once that is done (which will be much shorter than the first), you will wait for the pods to finish creating.
   You can check the status of the Home Assistant pod with the following command:
   ```
   kubectl get pods
   ```
   
   If you want to see all of the pods being created, use:
   ```
   kubectl get pods -A
   ```
   
   Keep using the "kubectl get pods" command every so often, until the Home Assistant pod has a final status of "Running".
   
   ![Image showing Home Assistant pod at ready](https://i.imgur.com/V16tWtT.jpg)
   
   <br />
9. Once Home Assistant is ready for connections, use the following command to get the external IP address
   used to access Home Assistant:
   ```
   kubectl get svc
   ```
   - Add the 8123 port to the address, to access Home Assistant. In the case below, you would use the following:

     "a63aade5a322644d49583980c4e3c842-1145205109.us-east-1.elb.amazonaws.com:8123"
   
   ![Image showing external address](https://i.imgur.com/eQXeedt.jpg)
   
   <br />
10. Once available, Home Assistant will start by showing one of two screens:
    1. The onboarding screen, in case a new database was created. Sign in using whatever credentials you'd like.
    
       ![Home Assistant onboarding screen](https://i.imgur.com/4b1odkx.png)   
    
    2. Or the sign-in screen, if you used the pre-existing database. You must sign in with the following credentials:
       - Username: bello
       - Password: 1234

       ![Home Assistant sign-in screen](https://i.imgur.com/iOSvB6K.png)
       
       <br />
11. Set up is complete. Use Home Assistant however you'd like. :smile:


<br />
