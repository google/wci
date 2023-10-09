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
from flask_cors import CORS
from blueprints import *

import os

app = Flask(__name__)
# Enables CORS on the app
# For safety, origins can be set into CORS
# reference: https://flask-cors.readthedocs.io/en/latest/configuration.html
CORS(app)

# Generates a random, safe secret key
app.secret_key = os.urandom(12).hex()
app.register_blueprint(webhook_page)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
