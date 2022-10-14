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
This module is the main flask application.
"""

from flask import Flask
from blueprints import *

import os

SECRET_KEY = os.environ.get('SECRET_KEY')

# Enable Google Cloud Debugger
# See https://cloud.google.com/debugger/docs/setup/python for more information.
try:
    import googleclouddebugger
    googleclouddebugger.enable()
except ImportError:
    pass

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.register_blueprint(webhook_page)

if __name__ == '__main__':
    app.run(debug=True)
