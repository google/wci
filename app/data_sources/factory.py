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
A generic data source class to ease the process of integrating with other databases
"""

from enum import Enum
from data_sources import DataSource
from data_sources.bigquery.bigquery_data_source import BigQueryDataSource


class SourceType(Enum):
    (BIG_QUERY, FILE) = range(2)


AVAILABLE_DATA_SOURCES = {SourceType.BIG_QUERY: BigQueryDataSource()}


class DataSourceFactory:
    def __init__(self, source_type: SourceType):
        self._source = SourceType[source_type]

    def get(self) -> DataSource:
        if self._source:
            return AVAILABLE_DATA_SOURCES.get(self._source)
        else:
            raise NotImplementedError(
                "Data Source not implemented. Please check your configuration."
            )
