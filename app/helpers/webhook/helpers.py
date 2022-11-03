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

import os
import uuid
import zlib
import uuid
import time
import re
from typing import Optional
from google.cloud import bigquery

BQ_LEAD_TABLE = os.environ.get('BQ_LEAD_TABLE')
BQ_LINKED_TABLE  = os.environ.get('BQ_LINKED_TABLE')
BQ_CHAT_TABLE = os.environ.get('BQ_CHAT_TABLE')
PROTOCOL_MESSAGE = os.environ.get('PROTOCOL_MESSAGE')
BQ_CLIENT = bigquery.Client()

def generate_a_protocol(identifier: str, type: str) -> Optional[str]:
   """
    Helper function for generating a new protocol for a given request.

    Parameters:
       identifier (str): to be associated with the new protocol. E.g. gclid, device_id, phone_number, etc.

    Output:
       a new Protocol.
   """
    
   # Generates a protocol based on current timestamp
   protocol = zlib.crc32(f'{uuid.uuid1()}'.encode())

   # Gets the table to be used within BQ
   table = BQ_CLIENT.get_table(BQ_LEAD_TABLE)

   # Verifies for errors
   errors = BQ_CLIENT.insert_rows(
      table, 
      [(identifier, type, protocol, time.time())]
   )  
   
   # Returns the generated protocol, or None if anything goes wrong
   return protocol if errors == [] else None

def get_protocol_by_phone(message:str, phone:str) -> Optional[str]:
   """
    Helper function for getting a generated protocol by a given phone number.

    Parameters:
       phone number (str)

    Output:
       found protocol or none
   """
   # Checks if a protocol is within the given message
   # If not, returns None
   has_protocol = re.match(f"{PROTOCOL_MESSAGE} (\w+)", message)
   
   # If no protocol was found, returns empty
   if has_protocol is None:
      # Saves a copy of the received message
      __save_message(message, phone)
      return None

   # Captures the first group matched
   protocol = has_protocol.group(1)

   # Updates the phone_number by protcol
   query = f"""
      INSERT INTO `{BQ_LINKED_TABLE}` (protocol, identifier, phone, timestamp)
      SELECT 
         protocol,
         identifier,
         @phone as phone,
         CURRENT_TIMESTAMP() as timestamp
      FROM `{BQ_LEAD_TABLE}`
      WHERE protocol = @protocol
      """
   # Sets phone_number parameter   
   job_config = bigquery.QueryJobConfig(
      query_parameters=[
         bigquery.ScalarQueryParameter("phone", "STRING", phone),
         bigquery.ScalarQueryParameter("protocol", "STRING", protocol)
      ]
   )
   # Executes the query
   BQ_CLIENT.query(query, job_config=job_config).result()

   # Returns the raw protocol
   return protocol

def __save_message(message:str, phone:str) -> Optional[str]:
   """
    Saves a copy of the received message

    Parameters:
       message (str)
       phone number (str)

    Output:
       none
   """

   # Updates the phone_number by protcol
   query = f"""
      INSERT INTO `{BQ_CHAT_TABLE}` (phone, message, timestamp)
      VALUES (
         @phone,
         @message,
         CURRENT_TIMESTAMP()
      ) 
      """
   # Sets phone_number parameter   
   job_config = bigquery.QueryJobConfig(
      query_parameters=[
         bigquery.ScalarQueryParameter("phone", "STRING", phone),
         bigquery.ScalarQueryParameter("message", "STRING", message)
      ]
   )
   # Executes the query
   BQ_CLIENT.query(query, job_config=job_config).result()

