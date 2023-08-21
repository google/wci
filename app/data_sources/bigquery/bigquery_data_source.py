import os
import time
from typing import Optional

from google.cloud import bigquery
from data_sources.data_source import DataSource

BQ_LEAD_TABLE = os.environ.get('BQ_LEAD_TABLE')
BQ_LINKED_TABLE  = os.environ.get('BQ_LINKED_TABLE')
BQ_CHAT_TABLE = os.environ.get('BQ_CHAT_TABLE')
PROTOCOL_MESSAGE = os.environ.get('PROTOCOL_MESSAGE')

class BigQueryDataSource (DataSource):

    def __init__ (self, db_options: Optional[dict]):
        # continue later authenticate with BQ and set options ex. if locations, project_id --> set location,
        # return bigquery.Client(location=self._bq_location)
        self._bq_client = bigquery.Client()

    def store_protocol (self, identifier, type, protocol, mapped):
              # Gets the table to be used within BQ
        table = self._bq_client.get_table(BQ_LEAD_TABLE)
        # Verifies for errors
        errors = self._bq_client.insert_rows(
            table, 
            [(identifier, type, protocol, mapped, time.time())]
        )
        return errors
    
    def store_lead (self, sender: str, protocol: str):
        query = f"""
        INSERT INTO `{BQ_LINKED_TABLE}` (protocol, phone, timestamp)
        SELECT 
            protocol,
            @phone as phone,
            CURRENT_TIMESTAMP() as timestamp
        FROM `{BQ_LEAD_TABLE}`
        WHERE protocol = @protocol
        """
        # Sets phone_number parameter   
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("phone", "STRING", sender),
                bigquery.ScalarQueryParameter("protocol", "STRING", protocol)
            ]
        )
        # Executes the query
        self._bq_client.query(query, job_config=job_config).result()

    def store_message (self, message:str, sender:str, receiver:str) -> Optional[str]:
        # Updates the phone_number by protcol
        query = f"""
            INSERT INTO `{BQ_CHAT_TABLE}` (sender, receiver, message, timestamp)
            VALUES (
                @sender,
                @receiver,
                @message,
                CURRENT_TIMESTAMP()
            ) 
            """
        # Sets phone_number parameter   
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("sender", "STRING", sender),
                bigquery.ScalarQueryParameter("receiver", "STRING", receiver),
                bigquery.ScalarQueryParameter("message", "STRING", message)
            ]
        )
        # Executes the query
        self._bq_client.query(query, job_config=job_config).result()