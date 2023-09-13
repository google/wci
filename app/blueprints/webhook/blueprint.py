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

import os
from middlewares.auth import auth_required
from helpers.webhook.helpers import (
    generate_a_protocol,
    get_default_messages,
    get_domain_from_url,
)
from partners.partners import Partner
from flask import Blueprint, request, jsonify


webhook_page = Blueprint("webhook", __name__)


@webhook_page.route("/webhook", methods=["GET", "POST"])
def process_protocol():
    """
    Generates a new protocol

    Parameters:
       None
    Output:
       Returns the newly generated protocol number for the received lead
    """

    # Collects gclid, phone from the URL
    identifier = request.args.get("id")
    type = request.args.get("type") or "gclid"

    # Checks if this is a post with a payload to be associated with
    # the protocol number
    payload = None
    if request.is_json:
        payload = request.get_json(silent=True)

    # Always generate a protocol for every request
    has_protocol = generate_a_protocol(identifier, type, payload)

    # Stats of usage
    if os.environ.get("STATS_OPTIN") != "no":
        try:
            from tadau.measurement_protocol import Tadau

            Tadau().process(
                [
                    {
                        "client_id": f"{has_protocol}",
                        "name": "wci",
                        "action": "lead",
                        "context": get_domain_from_url(request.referrer),
                    }
                ]
            )
        except:
            pass

    # Gets url-safe messages
    messages = get_default_messages(has_protocol)

    # Returns the generated protocol + default messages
    return (
        jsonify(
            protocol=has_protocol,
            message=messages.get("message"),
            protocol_message=messages.get("protocol_message"),
            welcome_message=messages.get("welcome_message"),
        ),
        200,
    )


@webhook_page.route("/webhook-wci", methods=["POST"])
def process_message():
    """
    Process message received

    Parameters:
       None
    Output:
       Status code.
    """

    # Collects the payload received
    partner = Partner(os.environ.get("PARTNER_TYPE")).get_partner()
    partner.process_message(request.get_json())

    # Always return success
    return "Success", 200


@webhook_page.route("/webhook-wci", methods=["GET"])
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
    challenge = request.args.get("hub.challenge")

    # Redirects the request
    return challenge, 200


@webhook_page.route("/health_checker", methods=["GET"])
def health_checker():
    return "alive", 200
