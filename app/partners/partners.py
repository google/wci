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
A generic partner class to ease the process of integrating with bot managing companies
"""

from enum import Enum
from partners.whatsapp.whatsapp_partner import WhatsAppPartner
from partners.botmaker.botmaker_partner import BotmakerPartner
from partners.take.take_partner import TakePartner


class PartnerType(Enum):
    (BOTMAKER, TAKE, WHATSAPP) = range(3)


class Partner:
    def __init__(self, partner_type: PartnerType):
        self._partner_type = PartnerType[partner_type]

    def get_partner(self):
        match self._partner_type:
            case PartnerType.BOTMAKER:
                return BotmakerPartner()

            case PartnerType.TAKE:
                return TakePartner()

            case PartnerType.WHATSAPP:
                return WhatsAppPartner()

            case _:
                raise NotImplementedError(
                    "Partner not implemented. Please check your configuration."
                )
