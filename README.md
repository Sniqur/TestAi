# Automated PDF to JSON converter

Hello, this one of is my pet projects, namely PDF to JSON Converter.
Shorlty of what was done and how it works. 

## 1) IaaC
   I wrote a needed infrastructure on Azure by using Terraform and then deployed it for two Environments (Development and Production)

## 2) I created an Azure Functions:
   First one is used to check if the new PDF files were added to my **to-do** container (sterted point of process). If something new was added it is being triggered and send this file to Azure Form Recognizer which is also deployed from the first paragraph.
   After processing this file it is being sent to my second **done** container. The second function is also being triggered by adding new file to container (**done** container) so start it`s work. It reads the name of the file and send notification on Deiscord and Telegram. 

## 3) I created two pipelines:
   The first one builds an ifrastructure for **Development** environment and pushes the function to Azure Functions for Develoment environment.
   The second one does the same, but for **Production** Environment. The second pipeline works if only the first one was successfully completed. 
