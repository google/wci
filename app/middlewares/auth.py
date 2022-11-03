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
This module includes decorators for authenticating requests.
"""

import os
from functools import wraps
from flask import request, abort

API_KEY = os.environ.get('API_KEY')

def auth_required(f):
    """
    A decorator for view functions that require authentication.
    If signed in, pass the request to the decorated view function with
    authentication context; otherwise redirect the request.

    Parameters:
       f (func): The view function to decorate.

    Output:
       decorated (func): The decorated function.
    """
    @wraps(f)
    def decorated(*args, **kwargs):       
        token = request.args.get('hub.verify_token')

        # In case the request comes from the challenge route
        if API_KEY != token:
            return abort(403)

        return f(auth_context=True, *args, **kwargs)
    return decorated

