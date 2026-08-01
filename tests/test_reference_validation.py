# Copyright (c) 2026 Splunk Inc.
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
import ast
import unittest
from pathlib import Path
from urllib.parse import unquote


ACTIONS_INIT = Path(__file__).resolve().parents[1] / "actions" / "__init__.py"


def _load_base_action():
    source = ACTIONS_INIT.read_text()
    tree = ast.parse(source)
    class_node = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "BaseAction")
    module = ast.fix_missing_locations(ast.Module(body=[class_node], type_ignores=[]))
    namespace = {"ActionResult": object, "unquote": unquote}
    exec(compile(module, str(ACTIONS_INIT), "exec"), namespace)
    return namespace["BaseAction"]


class ReferenceValidationTests(unittest.TestCase):
    def test_accepts_expected_reference_shapes(self):
        validate = _load_base_action().is_valid_reference

        self.assertTrue(validate("zone_rp/opaque-reference", "zone_rp"))
        self.assertTrue(validate("record:rpz:a/opaque-reference", "record:rpz:"))

    def test_rejects_encoded_separator_traversal(self):
        validate = _load_base_action().is_valid_reference
        payloads = (
            "zone_rp/opaque%2f..%2f..%2fgrid",
            "zone_rp/opaque%252f..%252fgrid",
            "record:rpz:a/opaque%2f..%2fadminuser",
            "record:rpz:a/opaque%255c..%255cadminuser",
            "zone_rp/opaque%25252f..%25252fgrid",
        )

        for payload in payloads:
            with self.subTest(payload=payload):
                self.assertFalse(validate(payload, "record:rpz:" if payload.startswith("record:") else "zone_rp"))


if __name__ == "__main__":
    unittest.main()
