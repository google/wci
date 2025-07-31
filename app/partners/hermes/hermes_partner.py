# Copyright 2025 Google LLC.
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
A Hermes extension for Partners
"""

from partners import Partner
from helpers.webhook.helpers import get_protocol_by_phone

class HermesPartner(Partner):

    def process_message(self, payload):
        """
        Process message received

        Parameters:
            payload: Hermes's webhook payload

        """
        
        if payload.get("message") and payload.get("message").get("text"):
            get_protocol_by_phone(
                payload.get("message").get("text"), payload.get("sender"), payload.get("receiver")
            )
