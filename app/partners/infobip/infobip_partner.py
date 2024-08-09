# Copyright 2024 Google LLC.
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
A Infobip extension for Partners
"""


from partners import Partner
from helpers.webhook.helpers import get_protocol_by_phone


class InfobipPartner(Partner):
    """
    Process message received

    Parameters:
        payload: Infobip's webhook payload
            Ref.: https://www.infobip.com/docs/api/channels/whatsapp/whatsapp-inbound-messages/receive-whatsapp-inbound-messages

    """

    def process_message(self, payload):
        if payload.get("results") is not None:
            for message in payload.get("results"):
                try:
                    if message.get("integrationType") == "WHATSAPP":
                        # Only processes text messages
                        _msg = message.get("message")
                        if _msg and _msg.get("type") == "TEXT":
                            get_protocol_by_phone(
                                _msg.get("text"), message.get("from"), message.get("to")
                            )
                except:
                    continue
