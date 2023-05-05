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
from flask import Blueprint, request, redirect, jsonify

PROTOCOL_MESSAGE = os.environ.get('PROTOCOL_MESSAGE')
WELCOME_MESSAGE = os.environ.get('WELCOME_MESSAGE')
STATS_OPTIN = os.environ.get('STATS_OPTIN') 
ACCOUNT_NUMBER = os.environ.get('ACCOUNT_NUMBER')

webhook_page = Blueprint('webhook', __name__)

@webhook_page.route('/webhook', methods=['GET', 'POST'])
def process_protocol():
   """
   Generates a new protocol

   Parameters:
      None
   Output:
      Returns the newly generated protocol number for the received lead
   """

   # Collects gclid, phone from the URL
   identifier = request.args.get('id') 
   type = request.args.get('type') or 'gclid'
   
   # Checks if this is a post with a payload to be associated with
   # the protocol number
   payload = None
   if request.is_json:
      payload = request.get_json(silent=True)

   # Always generate a protocol for every request
   has_protocol = generate_a_protocol(identifier, type, payload)

   # Stats of usage
   if STATS_OPTIN != 'no':
      try:
         from tadau.measurement_protocol import Tadau
         Tadau().process([{
            'client_id': f"{has_protocol}",
            'name': 'wci',
            'action': 'lead',
            'context': request.referrer,
         }])
      except:
         pass

   # Redirects the request
   return jsonify(protocol=has_protocol,
                  message=f"{PROTOCOL_MESSAGE.strip()} {has_protocol}. {WELCOME_MESSAGE.strip()}"
                  ), 200 

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
         if  message.get('fromCustomer') == True:
            get_protocol_by_phone(
               message.get('message'), 
               payload.get('contactId'),
               ACCOUNT_NUMBER) 
         else:
            get_protocol_by_phone(
               message.get('message'),
               ACCOUNT_NUMBER, 
               payload.get('contactId')) 
          
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