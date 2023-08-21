from typing import Enum, Optional
from data_sources.bigquery.bigquery_data_source import BigQueryDataSource

class SourceType(Enum):
    BIG_QUERY = range(1)

class DataSource():
    def __init__(self, source_type: SourceType, db_authentication: Optional[dict], db_options: Optional[dict]):
        self._source_type = source_type
        self._db_authentication = db_authentication
        self._db_options = db_options

    def get_data_source(self):
        if self._source_type == SourceType.BIG_QUERY:
            return BigQueryDataSource(self._db_authentication, self._db_options)
        else:
            raise NotImplementedError("Source Type not implemented. Please check your configuration.")
        return data_source