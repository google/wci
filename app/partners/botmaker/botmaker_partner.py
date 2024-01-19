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

"""
A Botmaker extension for Partners
"""

import os
from helpers.webhook.helpers import get_protocol_by_phone

ACCOUNT_NUMBER = os.environ.get("ACCOUNT_NUMBER")


class BotmakerPartner:
    """
    Process message received

    Parameters:
        payload: Botmaker's webhook payload
            Ref.: https://botmaker.com/en/developers/

    """

    def process_message(self, payload):
        if payload.get("contactId") is not None and payload.get("type") == "message":
            for message in payload.get("messages"):
                try:
                    if message.get("fromCustomer") == True:
                        get_protocol_by_phone(
                            message.get("message"), payload.get("contactId"), ACCOUNT_NUMBER
                        )
                    else:
                        get_protocol_by_phone(
                            message.get("message"), ACCOUNT_NUMBER, payload.get("contactId")
                        )
                except:
                    continue        
