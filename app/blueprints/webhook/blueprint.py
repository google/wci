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
from flask import Blueprint, request, jsonify
from tadau.measurement_protocol import Tadau

PROTOCOL_MESSAGE = os.environ.get('PROTOCOL_MESSAGE')
WELCOME_MESSAGE = os.environ.get('WELCOME_MESSAGE')
STATS_OPTIN = os.environ.get('STATS_OPTIN') 

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
      Tadau().process([{
         'client_id': has_protocol,
         'name': 'wci',
         'action': 'lead',
         'context': request.referrer,
      }])

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

   if (payload.get("object") == "whatsapp_business_account" and payload.get("entry") is not None):
      for each in payload.get("entry"):
         for change in each['changes']:
            if change['field'] == "messages" and change['value'].get("messages") is not None:
               get_protocol_by_phone(
                  change['value']['messages'][0]['text']['body'], 
                  change['value']['contacts'][0]['wa_id'],
                  change['value']['metadata']['display_phone_number']) 
                  #TODO - this should be adapted to your logic

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