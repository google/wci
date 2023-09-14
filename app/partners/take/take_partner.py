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
A Take extension for Partners
"""

from helpers.webhook.helpers import get_protocol_by_phone


class TakePartner:
    """
    Process message received

    Parameters:
        payload: Take | Blip's webhook payload
            Ref.: https://help.blip.ai/hc/en-us/articles/4474381206423-Submitting-data-for-analysis-through-Webhooks

    """

    def process_message(self, payload):
        if payload.get("type") == "text/plain":
            get_protocol_by_phone(
                payload.get("content"), payload.get("from"), payload.get("to")
            )
