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
A collection of helper functions for webhook related operations.
"""

import base64
import hashlib
import requests
import os
import uuid
import zlib
import re
import urllib.parse
from flask import Request
from typing import Dict, Optional
from data_sources.factory import DataSourceFactory

data_source = DataSourceFactory(os.environ.get("DATA_SOURCE_TYPE")).get()


def generate_a_protocol() -> Optional[str]:
    """
    Helper function for generating a new protocol for a given request.

    Output:
       a new Protocol.
    """

    # Generates a protocol based on current timestamp
    protocol = zlib.crc32(f"{uuid.uuid1()}".encode())

    # Returns the generated protocol
    return protocol

def save_protocol(
    identifier: str, type: str, protocol: str, payload: Optional[any]) -> Optional[str]:
    """
    Helper function for saving protocols and identifiers.

    Parameters:
       identifier (str): to be associated with the new protocol.
       type (str): type of the identifier. E.g. gclid, device_id, phone_number, etc.
       protocol (str): protocol number

    Output:
       a new Protocol.
    """
    # Sends protocol to db
    data_source.save_protocol(identifier, type, protocol, payload)

    # Returns the generated protocol
    return 200


def get_protocol_by_phone(message: str, sender: str, receiver: str) -> Optional[str]:
    """
    Helper function for getting a generated protocol for a given sender.

    Parameters:
       message (str)
       sender (str)
       receiver (str)

    Output:
       found protocol or none
    """
    # Checks if a protocol is within the given message
    # If not, returns None
    _protocol_message = os.environ.get("PROTOCOL_MESSAGE").strip()
    _ctm_message = os.environ.get("CTM_PROTOCOL_MESSAGE").strip()
    has_protocol = re.search(f"({_protocol_message}|{_ctm_message}) (\w+)", message)
    protocol = None

    # If a protocol was found, creates a match with sender
    if has_protocol:
        # Captures the second group matched
        protocol = has_protocol.group(2)

        # Updates the phone_number by protcol
        data_source.save_phone_protocol_match(sender, protocol)

        # Checks if ECL is enabled
        if os.environ.get("ECL_ENABLED").lower() == "true":
            set_protocol_ecl_for_phone(protocol, sender)

     # Saves a copy of the received message
    data_source.save_message(message, sender, receiver)
        
    # Returns the raw protocol
    return protocol


def get_domain_from_request(request: Request) -> str:
    """
    Helper function to extract domain from Request

    Parameters:
       url: full url that may contain paths, paramerters and achors

    Output:
       Extracted domain or "Not set"
    """

    if request.origin:
        url = request.origin
    elif request.host_url:
        url = request.host_url
    else:
        return "Not set"

    domain = re.match("([^\n\?\=\&\# ]+)", url)

    if domain is None:
        return "Not set"

    return domain.group(1)


def get_default_messages(protocol: str) -> Dict[str, str]:
    """
    Gets defined, standard messages

    Parameters:
       protocol: generated protocol

    """
    _protocol_message = os.environ.get("PROTOCOL_MESSAGE").strip()
    _welcome_message = os.environ.get("WELCOME_MESSAGE").strip()

    return {
        "message": urllib.parse.quote_plus(
            f"{_protocol_message} {protocol}. {_welcome_message}"
        ),
        "protocol_message": _protocol_message,
        "welcome_message": _welcome_message,
    }


def get_safe_phone(phone: str) -> str:
    """
    Gets phone number safely

    Parameters:
       sender: phone who sent the message

    Outputs:
        phone number only - may include + (e.g. +15555555555)

    """

    # Checks if phone number is valid (without +)
    is_valid = re.match(r"\d{8,15}", phone)

    # Returns its raw value if it's not a valid phone number
    if is_valid is None:
        return phone

    # Otherwise, extracts only numbers and includes plus code
    return "+{}".format(re.sub(r"[^0-9]", "", phone))


def to_sha256(string: str) -> str:
    """
    Receives a string and hashes into sha256

    Parameters:
       string: str

    """
    return hashlib.sha256(string.strip().lower().encode("utf-8")).hexdigest()


def to_bytes(hex_digest: str) -> bytes:
    """
    Receives a digested hex from sha256

    Parameters:
       hex_digest: str

    """
    return bytes.fromhex(hex_digest)


def to_base64(from_hex: bytes) -> str:
    """
    Receives a string and hashes into sha256

    Parameters:
       from_hex: str

    """
    return base64.urlsafe_b64encode(from_hex).rstrip(b"=").decode("utf-8")


def set_protocol_ecl_for_phone(protocol: str, sender: str) -> None:
    """
    Fires ECL tag for a given protoco and phone number

    Parameters:
       protocol: matched protocol for processed message
       sender: phone who sent the message

    """
    try:
        # hashes phone number and transfors into base 64
        sha256_phone = to_sha256(get_safe_phone(sender))
        # mimis transformation for firing the tag
        hashed_phone = to_base64(to_bytes(sha256_phone))

        # gets the data for the matched protocol
        matched_protocol = data_source.get_protocol_match(protocol, sender)

        if (
            matched_protocol.get("mapped")
            and matched_protocol.get("mapped")["conversion_id"]
        ):
            if matched_protocol.get("type") == "gclid" and matched_protocol.get(
                "identifier"
            ):
                gclid = matched_protocol.get("identifier")
                conversion_id = matched_protocol.get("mapped")["conversion_id"]
                # Targets ECL beacon endpoint
                url = f"https://google.com/pagead/form-data/{conversion_id}?em=tv.1~pn.{hashed_phone}&gclaw={gclid}"
                response = requests.post(url)

                # Updates a pending lead into ecl after successfully triggering
                # the ECL beacon
                if response.ok:
                    data_source.save_protocol(
                        sha256_phone, "ecl", protocol, matched_protocol.get("mapped")
                    )
                else:
                    print(f"ECL not fired for {protocol}", response)
    except:
        pass
