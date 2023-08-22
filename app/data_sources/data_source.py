from enum import Enum
from typing import Optional
from data_sources.bigquery.bigquery_data_source import BigQueryDataSource

class SourceType(Enum):
    (BIG_QUERY, FILE) = range(1)

class DataSource:
    def __init__(self, source_type: SourceType):
        self._source_type = SourceType[source_type]

    def get_data_source(self):
        data_source = None
        if self._source_type == SourceType.BIG_QUERY:
            return BigQueryDataSource()
        else:
            raise NotImplementedError("Source Type not implemented. Please check your configuration.")
        return data_source