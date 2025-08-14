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


from typing import Any, Dict

from ..auth import retrieve_third_party_id_and_creds
from ..sources_v2._back_compat import get_mounted_source_secrets, get_mounted_sources


def get_extra_context_parameters() -> Dict[str, Any]:
    formatted_source_configurations = {key: value.source_configuration for key, value in get_mounted_sources().items()}

    context_parameters: Dict[str, Any] = {
        "sources": get_mounted_source_secrets(),
        "source_configs": formatted_source_configurations,
    }

    CLIENT_ID, CLIENT_SECRET = retrieve_third_party_id_and_creds()

    if CLIENT_ID and CLIENT_SECRET:
        context_parameters.update({"CLIENT_ID": CLIENT_ID, "CLIENT_SECRET": CLIENT_SECRET})

    return context_parameters
