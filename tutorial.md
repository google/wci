# WCI - Conversion Import for Whatsapp

## Welcome
Welcome to the guide deployment of the WhatsApp Conversion Import (WCI). We will deploy the solution on Google Cloud.

WCI offers a sample on how to integrate and track conversions that happen in business-account chats by linking clicked leads (click to chat) to final conversions (purchased through chat app)

**Disclaimer:** This is not an officially supported Google product

## Setup

First of all, you will need to configure the Google Cloud project you're going to use.
<walkthrough-project-setup></walkthrough-project-setup>

After selecting the project in the menu above,  execute the following command:

``` bash
gcloud config set project <walkthrough-project-id/>
```

## WCI Deployment - Step 1
In the Cloud Shell, execute the following command:

``` bash
. ./deployment/deploy.sh
```

WCI will be deployed in the Google Cloud Project, and it will choose by default the current active project you're at. 
If you want to deploy to the Active project, type Y/y to Continue

```bash
Y
```

## WCI Deployment - Step 2

During the App deployment, it will ask for a few specific information:
- The Whatsapp Business Account number (e.g. 5511999888777)
- The API Key (This is the WhatsApp API Key)
- The message to be sent with the protocol number (E.g. *Your protocol is* XXXXXXXX)
- Type the message to be sent AFTER the protocol number (E.g. Your protocol is 98765432. *Hello, Customer*)

## Confirmation

The solution will then prompt you to accept the services that will be deployed. 
If they are all correct, please write Y/y to continue

``` bash
Y
```
