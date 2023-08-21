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
A collection of helper functions for webhook related operations.
"""

import json
import os
import uuid
import zlib
import time
import re
from typing import Optional
from data_sources.data_source import DataSource

PROTOCOL_MESSAGE = os.environ.get('PROTOCOL_MESSAGE')
data_source = DataSource(os.environ.get('DATA_SOURCE_TYPE')).get_data_source()

def generate_a_protocol(identifier: str, type: str, payload:Optional[any]) -> Optional[str]:
   """
    Helper function for generating a new protocol for a given request.

    Parameters:
       identifier (str): to be associated with the new protocol. E.g. gclid, device_id, phone_number, etc.

    Output:
       a new Protocol.
   """
   
   # Generates a protocol based on current timestamp
   protocol = zlib.crc32(f'{uuid.uuid1()}'.encode())

   # Collects mapping identifiers if any
   mapped = json.dumps(payload) if payload else None

   # Sends protocol to db
   errors = data_source.store_protocol(identifier, type, protocol, mapped)

   # Returns the generated protocol, or None if anything goes wrong
   return protocol if errors == [] else None

def get_protocol_by_phone(message:str, sender:str, receiver: bool) -> Optional[str]:
   """
    Helper function for getting a generated protocol for a given sender.

    Parameters:
       message (str)
       sender (str)
       receiver (str)

    Output:
       found protocol or none
   """
   # Checks if a protocol is within the given message
   # If not, returns None
   has_protocol = re.match(f"{PROTOCOL_MESSAGE} (\w+)", message)
   
   # If no protocol was found, returns empty
   if has_protocol is None:
      # Saves a copy of the received message
      __save_message(message, sender, receiver)
      return None

   # Captures the first group matched
   protocol = has_protocol.group(1)

   # Updates the phone_number by protcol
   data_source.store_lead(sender, protocol)

   # Returns the raw protocol
   return protocol

def __save_message(message:str, sender:str, receiver:str) -> Optional[str]:
   """
    Saves a copy of the received message

    Parameters:
       message (str)
       sender (str)
       receiver (str)
    Output:
       none
   """

   # Updates the phone_number by protcol
   data_source.store_message(message, sender, receiver)

