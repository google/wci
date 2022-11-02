# WCI - Conversion Import for Whatsapp

WCI offers a sample on how to integrate and track conversions that happen in business-account chats by linking clicked leads (click to chat) to final conversions (purchased through chat app)

**Disclaimer:** This is not an officially supported Google product

## How does it work?
 - User clicks on the Contact via WhatsApp link
 - A cloud function collects an identifier such as gclid and generates a unique protocol
 - The user is redirected to the WhatsApp with a pre-typed message with the generated protocol
 - Once the user sends the message, a cloud function / webhook associated with the WhatsApp Business Account - checks for the protocol and relates it to the gclid and phone number that the message was sent from

## Prerequisites
 - Whatsapp Business Account

## Deployment
In the Cloud Shell, execute the following commands:
``` shell
git clone https://github.com/google/wci
cd wci
. ./deployment/deploy.sh
```