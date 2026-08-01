# File: __init__.py
#
# Copyright 2025-2026 Infoblox Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions
# and limitations under the License.

from urllib.parse import unquote

from phantom.action_result import ActionResult


class BaseAction:
    """Base Action class to generate the action objects."""

    def __init__(self, connector, param):
        """Prepare constructor for actions.

        :param connector: Infoblox NIOS connector object
        :param param: Parameter dictionary
        """
        self._connector = connector
        self._action_result = connector.add_action_result(ActionResult(dict(param)))
        self._param = param

    @staticmethod
    def is_valid_reference(reference_id, expected_prefix):
        """Validate an Infoblox object reference before using it as a URL path."""
        if (
            not isinstance(reference_id, str)
            or "\\" in reference_id
            or any(char in reference_id for char in "?#")
            or any(ord(char) < 32 for char in reference_id)
        ):
            return False

        segments = reference_id.split("/")
        prefix_matches = segments[0].startswith(expected_prefix) if expected_prefix.endswith(":") else segments[0] == expected_prefix
        if len(segments) < 2 or not prefix_matches:
            return False

        decoded_segments = [unquote(unquote(segment)) for segment in segments]
        return all(segment not in {"", ".", ".."} for segment in decoded_segments)
