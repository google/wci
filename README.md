# WCI - Conversion Import for Whatsapp

WCI is an open source solution that enables advertisers who offer a WhatsApp channel to measure, attribute, target and optimize their campaigns through signals received in-chat messages. The solution offers a way to integrate and track conversions that happen in business-account WhatsApp chats by linking clicked leads (click to chat) to final conversions (scheduled events, purchased through chat app, etc). As a result, WCI allows advertisers to  bring visibility to the WhatsApp journey; measure in-WhatsApp chat interactions; attribute in-WhatsApp chat conversions and target audience-lists with Customer Match.

**Disclaimer:** This is not an officially supported Google product

## How does it work?
 - User clicks on the Contact via WhatsApp link
 - A cloud function collects an identifier such as gclid and generates a unique protocol
 - The user is redirected to the WhatsApp with a pre-typed message with the generated protocol
 - Once the user sends the message, a cloud function / webhook associated with the WhatsApp Business Account - checks for the protocol and relates it to the gclid and phone number that the message was sent from

 ![image](https://github.com/google/wci/assets/6962758/7fe48295-cfc1-4a26-b8e7-05ca073232bc)

## Prerequisites
 - Whatsapp Business Account

## Deployment
In the Cloud Shell, execute the following command:
``` shell
git clone https://github.com/google/wci && cd wci && sh ./deployment/deploy.sh
```

## Updating WCI to the latest version
In the Cloud Shell, execute the following command:
``` shell
git clone https://github.com/google/wci && cd wci && sh ./deployment/deploy.sh service=update
```

## Guided Deployment
If you want to do a guided deployment through Cloud Shell, click the link below:<br>
[![Open in Cloud Shell](https://gstatic.com/cloudssh/images/open-btn.svg)](https://shell.cloud.google.com/cloudshell/editor?cloudshell_git_repo=https%3A%2F%2Fgithub.com%2Fgoogle%2Fwci&cloudshell_git_branch=main&cloudshell_tutorial=tutorial.md)

## Video-guided Deployment
[![Open on Youtube](https://www.gstatic.com/youtube/img/branding/favicon/favicon_48x48.png)](https://youtu.be/OVXIO5RMHX8)

## Resources
Video-guided deployment<br>
  	https://youtu.be/OVXIO5RMHX8

WCI’s source code<br>
    https://github.com/google/wci


WhatsApp Business Platform Cloud API<br>
    https://developers.facebook.com/docs/whatsapp/cloud-api/guides/set-up-webhooks

Google Cloud’s Artifacts Registry<br>
    https://cloud.google.com/artifact-registry/docs

Google Cloud’s Run<br>
    https://cloud.google.com/run/docs

Google Cloud’s BigQuery<br>
    https://cloud.google.com/bigquery/docs

Google Ads’ Conversion API<br>
    https://developers.google.com/google-ads/api/docs/conversions/overview

Google Ads’ Customer Match API<br>
    https://developers.google.com/google-ads/api/docs/remarketing/audience-types/customer-match

Google Ads’ Enhanced Conversion for Leads API<br>
    https://developers.google.com/google-ads/api/docs/conversions/upload-identifiers
