# CS6620_Group22

This repo contains the necessary files to launch Home Assistant, IoT automation and management software,
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
    
    
2. Determine if you want to use a database retaining saved information or an empty one.
   - If you want to reproduce the dashboard shown during the presentation, use the pre-existing database.
        - You will not have to make any changes, in this case.
        
   - If you want to start with a blank slate, you must do 2 things:
        1. Change the value of "new_database" to "true"
         
           ![Location of new_database variable](https://i.imgur.com/q6nsYZE.jpg)
           
        2. Go to the "ha_config_files" directory. Delete the ".storage" directory within it,
           with the following command:
           
           ```rm -r .storage```
           
           #### This is very important. If you do not delete the .storage directory, you won't be able to create
           #### an account, once Home Assistant starts
           
           ![Location of .storage file](https://i.imgur.com/rCEAhaD.jpg)
           
           
3. 
