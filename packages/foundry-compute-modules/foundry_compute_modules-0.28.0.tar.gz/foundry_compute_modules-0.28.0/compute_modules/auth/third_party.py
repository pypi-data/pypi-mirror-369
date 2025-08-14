#  Copyright 2024 Palantir Technologies, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


import http.client
import json
import os
import ssl
import time
import urllib.parse
from typing import Any, List, Optional, Tuple


def retrieve_third_party_id_and_creds() -> Tuple[Optional[str], Optional[str]]:
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    return CLIENT_ID, CLIENT_SECRET


def oauth(hostname: str, scope: List[str]) -> Any:
    CLIENT_ID, CLIENT_SECRET = retrieve_third_party_id_and_creds()
    if CLIENT_ID and CLIENT_SECRET:
        params = urllib.parse.urlencode(
            {
                "grant_type": "client_credentials",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "scope": " ".join(scope),
            }
        )
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        ssl_context = ssl.create_default_context(cafile=os.environ.get("DEFAULT_CA_PATH"))
        conn = http.client.HTTPSConnection(hostname, context=ssl_context)
        conn.request("POST", "/multipass/api/oauth2/token", params, headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        if response.status == 200:
            try:
                token_data = json.loads(data)
                if isinstance(token_data, dict):
                    return token_data.get("access_token")
            except (ValueError, KeyError):
                return None
    return None


class RefreshingOauthToken:
    def __init__(self, hostname: str, scope: List[str], refresh_interval: int = 1800) -> None:
        self.hostname = hostname
        self.scope = scope
        self.refresh_interval = refresh_interval
        self.last_refresh_time = 0.0
        self.token = None

    def get_token(self) -> Any:
        current_time = time.time()
        if not self.token or current_time - self.last_refresh_time > self.refresh_interval:
            self.token = self._fetch_token()
            self.last_refresh_time = current_time
        return self.token

    def _fetch_token(self) -> Any:
        return oauth(self.hostname, self.scope)
