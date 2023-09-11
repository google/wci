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
from data_sources.bigquery.bigquery_data_source import BigQueryDataSource

class SourceType(Enum):
    (BIG_QUERY, FILE) = range(2)

class DataSource:
    def __init__(self, source_type: SourceType):
        self._source_type = SourceType[source_type]

    def get_data_source(self):
        if self._source_type == SourceType.BIG_QUERY:
            return BigQueryDataSource()
        else:
            raise NotImplementedError("Source Type not implemented. Please check your configuration.")
      