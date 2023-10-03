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
A BigQuery extension for Data Sources
"""

import os
from typing import Dict, Optional
from google.cloud import bigquery
import datetime

BQ_LEAD_TABLE = os.environ.get("BQ_LEAD_TABLE")
BQ_LINKED_TABLE = os.environ.get("BQ_LINKED_TABLE")
BQ_CHAT_TABLE = os.environ.get("BQ_CHAT_TABLE")


class BigQueryDataSource:
    """BigQuery as datasource"""

    def __init__(self):
        # TODO(mr-lopes): adds client settings such as location
        self._bq_client = bigquery.Client()

    def save_protocol(
        self,
        identifier: str,
        type: str,
        protocol: str,
        mapped: Optional[Dict[str, str]],
    ):
        """
        Saves a protocol number with identifier and mapped values

        Parameters:
            identifier: gclid, client_id, etc
            type: indicates the type of identifier (gclid, etc)
            protocol: a generated protocol
            mapped: any additional value[s] to be associated with the protocol
        """

        query = f"""
            INSERT INTO `{BQ_LEAD_TABLE}` (identifier, type, protocol, mapped, timestamp)
            VALUES (
                @identifier,
                @type,
                @protocol,
                @mapped,
                CURRENT_TIMESTAMP()
            ) 
            """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("identifier", "STRING", identifier),
                bigquery.ScalarQueryParameter("type", "STRING", type),
                bigquery.ScalarQueryParameter("protocol", "STRING", protocol),
                bigquery.ScalarQueryParameter("mapped", "JSON", mapped),
            ]
        )

        self._bq_client.query(query, job_config=job_config).result()

    def save_phone_protocol_match(self, phone: str, protocol: str):
        """
        Saves a protocol matched to a number (phone)

        Parameters:
            phone: phone number
            protocol: protocol sent by phone number
        """

        query = f"""
            INSERT INTO `{BQ_LINKED_TABLE}` (protocol, phone, timestamp)
            VALUES ( 
                @protocol,
                @phone,
                CURRENT_TIMESTAMP()
            )
            """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("protocol", "STRING", protocol),
                bigquery.ScalarQueryParameter("phone", "STRING", phone),          
            ]
        )

        self._bq_client.query(query, job_config=job_config).result()

    def save_message(self, message: str, sender: str, receiver: str):
        """
        Saves menssage sent by phone number (sender)

        Parameters:
            message: content of message
            sender: emitter
            receiver: recipient
        """

        query = f"""
            INSERT INTO `{BQ_CHAT_TABLE}` (sender, receiver, message, timestamp)
            VALUES (
                @sender,
                @receiver,
                @message,
                CURRENT_TIMESTAMP()
            ) 
            """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("sender", "STRING", sender),
                bigquery.ScalarQueryParameter("receiver", "STRING", receiver),
                bigquery.ScalarQueryParameter("message", "STRING", message),
            ]
        )

        self._bq_client.query(query, job_config=job_config).result()

class BigQueryDataStream:
    """BigQuery Data Stream as datasource"""

    def __init__(self):
        # TODO(mr-lopes): adds client settings such as location
        self._bq_client = bigquery.Client()
        self._current_time = datetime.datetime.now()

    def save_protocol(
        self,
        identifier: str,
        type: str,
        protocol: str,
        mapped: Optional[Dict[str, str]],
    ):
        """
        Saves a protocol number with identifier and mapped values

        Parameters:
            identifier: gclid, client_id, etc
            type: indicates the type of identifier (gclid, etc)
            protocol: a generated protocol
            mapped: any additional value[s] to be associated with the protocol
        """
        rows_to_insert = [
            {"identifier": identifier, "type": type, "protocol": protocol, "mapped": mapped, "timestamp": self._current_time.timestamp()}
        ]

        errors = self._bq_client.insert_rows_json(BQ_LEAD_TABLE, rows_to_insert)  

        if errors == []:
            print("New rows have been added.")
        else:
            print("Encountered errors while inserting rows: {}".format(errors))

    def save_phone_protocol_match(self, phone: str, protocol: str):
        """
        Saves a protocol matched to a number (phone)

        Parameters:
            phone: phone number
            protocol: protocol sent by phone number
        """
        rows_to_insert = [
            {"phone": phone, "protocol": protocol, "timestamp": self._current_time.timestamp()}
        ]

        errors = self._bq_client.insert_rows_json(BQ_LINKED_TABLE, rows_to_insert)  

        if errors == []:
            print("New rows have been added.")
        else:
            print("Encountered errors while inserting rows: {}".format(errors))

    def save_message(self, message: str, sender: str, receiver: str):
        """
        Saves menssage sent by phone number (sender)

        Parameters:
            message: content of message
            sender: emitter
            receiver: recipient
        """

        rows_to_insert = [
            {"sender": sender, "receiver": receiver, "message": message, "timestamp": self._current_time.timestamp()}
        ]

        errors = self._bq_client.insert_rows_json(BQ_CHAT_TABLE, rows_to_insert)  

        if errors == []:
            print("New rows have been added.")
        else:
            print("Encountered errors while inserting rows: {}".format(errors))