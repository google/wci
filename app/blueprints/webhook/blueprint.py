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
from middlewares.auth import auth_required
from helpers.webhook.helpers import generate_a_protocol, get_protocol_by_phone
from flask import Blueprint, redirect, request

ACCOUNT_NUMBER = os.environ.get('ACCOUNT_NUMBER')
PROTOCOL_MESSAGE = os.environ.get('PROTOCOL_MESSAGE')
WELCOME_MESSAGE = os.environ.get('WELCOME_MESSAGE')

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
   type = request.args.get('type')
   
   # Always generate a protocol for every request
   has_protocol = generate_a_protocol(identifier, type)

   # Redirects the request
   return redirect(f"https://wa.me/{ACCOUNT_NUMBER}?text={PROTOCOL_MESSAGE} {has_protocol}. {WELCOME_MESSAGE}")    

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

   if (payload.get("contactId") is not None and payload.get("type") == "message"):
      for message in payload.get("messages"):
         get_protocol_by_phone(
            message.get('message'), 
            payload.get('contactId'),
            message.get('fromCustomer') == "true") 
          
   # Always return success
   return "Success", 200

@webhook_page.route('/webhook-wci', methods=['GET'])
@auth_required
def validates_challenge(auth_context):
   """
   Validates the webhook verification

   Parameters:
      None
   Output:
      Returns the challenge
   """

   # Collects token and challenge
   challenge = request.args.get('hub.challenge')

   # Redirects the request
   return challenge, 200  