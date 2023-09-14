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
A Whatsapp extension for Partners
"""

from helpers.webhook.helpers import get_protocol_by_phone


class WhatsAppPartner:
    def process_message(self, payload):
        """
        Process message received

        Parameters:
            payload: WhatsApp's webhook payload
                Ref.: https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks/payload-examples


        """
        if (
            payload.get("object") == "whatsapp_business_account"
            and payload.get("entry") is not None
        ):
            for each in payload.get("entry"):
                for change in each["changes"]:
                    if (
                        change["field"] == "messages"
                        and change["value"].get("messages") is not None
                    ):
                        get_protocol_by_phone(
                            change["value"]["messages"][0]["text"]["body"],
                            change["value"]["contacts"][0]["wa_id"],
                            change["value"]["metadata"]["display_phone_number"],
                        )
