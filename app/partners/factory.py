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
A factory partner class to ease the process of integrating with bot managing companies
"""

from enum import Enum
from partners import Partner
from partners.whatsapp.whatsapp_partner import WhatsAppPartner
from partners.botmaker.botmaker_partner import BotmakerPartner
from partners.infobip.infobip_partner import InfobipPartner
from partners.take.take_partner import TakePartner
from partners.hermes.hermes_partner import HermesPartner


class PartnerType(Enum):
    (BOTMAKER, TAKE, WHATSAPP, INFOBIP, HERMES) = range(5)


AVAILABLE_PARTNERS = {
    PartnerType.BOTMAKER: BotmakerPartner(),
    PartnerType.TAKE: TakePartner(),
    PartnerType.WHATSAPP: WhatsAppPartner(),
    PartnerType.INFOBIP: InfobipPartner(),
    PartnerType.HERMES: HermesPartner(),
}


class PartnerFactory:
    def __init__(self, partner_type: PartnerType):
        self._partner = PartnerType[partner_type]

    def get(self) -> Partner:
        if self._partner:
            return AVAILABLE_PARTNERS.get(self._partner)
        
        else:
            raise NotImplementedError(
                "Partner not implemented. Please check your configuration."
            )
