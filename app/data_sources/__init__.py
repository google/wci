# Copyright 2024 Google LLC.
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
A generic data source class to ease the process data
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional


class DataSource(ABC):
    @abstractmethod
    def save_protocol(
        self,
        identifier: str,
        type: str,
        protocol: str,
        mapped: Optional[Dict[str, str]],
    ):
        pass

    def save_phone_protocol_match(self, phone: str, protocol: str):
        pass

    def save_message(self, message: str, sender: str, receiver: str):
        pass

    def get_protocol_match(self, protocol: str, sender: str):
        pass
