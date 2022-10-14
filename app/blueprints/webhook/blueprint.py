# Copyright 2022 Google LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# This module is the Flask blueprint for the sign-in page (/signin).


import os
from helpers.webhook.helpers import generate_a_protocol, get_protocol_by_phone
from flask import Blueprint, redirect, request

ACCOUNT_NUMBER = os.environ.get('ACCOUNT_NUMBER')

webhook_page = Blueprint('webhook', __name__)

@webhook_page.route('/webhook', methods=['GET'])
def process_protocol():
   """
   Generates a new protocol and redirects to whatsapp

   Parameters:
      None
   Output:
      Redirects client to the whatsapp channel
   """

   # Collects gclid, phone from the URL
   identifier = request.args.get('gclid')
   has_protocol = 'N/A'

   # Existing either one of them, generates a protocol for this request
   if(identifier):
      has_protocol = generate_a_protocol(identifier)

   # Redirects the request
   return redirect(f"https://wa.me/{ACCOUNT_NUMBER}?text=Protocol:{has_protocol}")    

@webhook_page.route('/webhook-wci', methods=['POST'])
def process_message():
   """
   Process message received

   Parameters:
      None
   Output:
      Status code.
   """

   # Collects the payload received
   payload = request.get_json()

   if (payload.get("object") == "whatsapp_business_account" and payload.get("entry") is not None):
      for each in payload.get("entry"):
         for change in each['changes']:
            if change['field'] == "messages":
               get_protocol_by_phone(
                  change['value']['messages'][0]['text']['body'], 
                  change['value']['contacts'][0]['wa_id'])

   # Always return success
   return "Success", 200

@webhook_page.route('/webhook-wci', methods=['GET'])
def validates_challenge():
   """
   Validates the webhook verification

   Parameters:
      None
   Output:
      Returns the challenge
   """

   # Collects token and challenge
   token = request.args.get('hub.verify_token')
   challenge = request.args.get('hub.challenge')

   # Redirects the request
   return challenge, 200  