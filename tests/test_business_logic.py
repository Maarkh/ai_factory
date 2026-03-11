"""
Tests for business logic: deterministic checks (phases.py), contract validation (contract.py),
and safety valves. Run: source .venv_factory/bin/activate && pytest tests/test_business_logic.py -v
"""

import json
import logging
import tempfile
import unittest
from pathlib import Path

import pytest


# =====================================================
# 1. _sanitize_llm_code (phases.py)
# =====================================================

class TestSanitizeLlmCode:
    def setup_method(self):
        from checks import sanitize_llm_code
        self.sanitize = sanitize_llm_code

    def test_strips_markdown_fences(self):
        code = "```python\nprint('hello')\n```"
        assert self.sanitize(code) == "print('hello')"

    def test_strips_bare_fences(self):
        code = "```\nprint('hello')\n```"
        assert self.sanitize(code) == "print('hello')"

    def test_strips_garbage_tokens(self):
        code = "img<|begin_of_sentence|>img_bytes = read()"
        result = self.sanitize(code)
        assert "<|" not in result
        assert "img_bytes" in result

    def test_strips_unicode_garbage_tokens(self):
        code = "result<\uff5cbegin\u2581of\u2581sentence\uff5c>result = process()"
        result = self.sanitize(code)
        assert "\uff5c" not in result

    def test_strips_json_wrapper_fields(self):
        code = "import os\n\nimports_from_project = ['models', 'utils']\ndef main(): pass"
        result = self.sanitize(code)
        assert "imports_from_project" not in result
        assert "def main(): pass" in result

    def test_preserves_normal_code(self):
        code = "import os\n\ndef main():\n    print('hello')\n"
        assert self.sanitize(code) == code.strip()


# =====================================================
# 2. _check_function_preservation (phases.py)
# =====================================================

class TestCheckFunctionPreservation:
    def setup_method(self):
        from checks import check_function_preservation
        self.check = check_function_preservation

    def test_no_old_code_returns_empty(self):
        assert self.check("def foo(): pass", "", "", None) == []

    def test_no_change_returns_empty(self):
        old = "def foo(): pass\ndef bar(): pass"
        new = "def foo(): pass\ndef bar(): return 1"
        assert self.check(new, old, "", None) == []

    def test_removed_function_detected(self):
        old = "def foo(): pass\ndef bar(): pass"
        new = "def foo(): pass"
        warnings = self.check(new, old, "", [{"name": "bar"}])
        assert len(warnings) == 1
        assert "bar" in warnings[0]

    def test_removed_function_mentioned_in_feedback_ok(self):
        old = "def foo(): pass\ndef bar(): pass"
        new = "def foo(): pass"
        assert self.check(new, old, "remove bar function", None) == []

    def test_private_function_removal_ignored(self):
        old = "def _helper(): pass\ndef public(): pass"
        new = "def public(): pass"
        assert self.check(new, old, "", None) == []

    def test_function_not_in_contract_ignored(self):
        old = "def foo(): pass\ndef bar(): pass"
        new = "def foo(): pass"
        # bar not in contract -> removal is allowed (A5 may have changed)
        contract = [{"name": "foo"}]
        assert self.check(new, old, "", contract) == []

    def test_class_removal_detected(self):
        old = "class Foo:\n    pass\nclass Bar:\n    pass"
        new = "class Foo:\n    pass"
        warnings = self.check(new, old, "", [{"name": "Bar"}])
        assert any("Bar" in w for w in warnings)


# =====================================================
# 3. _check_class_duplication (phases.py)
# =====================================================

class TestCheckClassDuplication:
    def setup_method(self):
        from checks import check_class_duplication
        self.check = check_class_duplication

    def test_no_context_returns_empty(self):
        assert self.check("class Foo: pass", "", None) == []

    def test_no_duplication(self):
        code = "class Foo: pass"
        context = "--- other.py PUBLIC API ---\nclass Bar: pass"
        assert self.check(code, context, None) == []

    def test_duplication_detected(self):
        code = "class Camera: pass"
        context = "--- models.py PUBLIC API ---\nclass Camera: pass"
        warnings = self.check(code, context, None)
        assert len(warnings) == 1
        assert "Camera" in warnings[0]

    def test_expected_by_contract_not_flagged(self):
        code = "class Camera: pass"
        context = "--- models.py PUBLIC API ---\nclass Camera: pass"
        contract = [{"class": "Camera"}]
        assert self.check(code, context, contract) == []

    def test_private_class_ignored(self):
        code = "class _Internal: pass"
        context = "--- other.py PUBLIC API ---\nclass _Internal: pass"
        assert self.check(code, context, None) == []


# =====================================================
# 4. _check_import_shadowing (phases.py)
# =====================================================

class TestCheckImportShadowing:
    def setup_method(self):
        from checks import check_import_shadowing
        self.check = check_import_shadowing

    def test_no_shadowing(self):
        code = "from os import path\ndef my_func(): pass"
        assert self.check(code) == []

    def test_shadowing_detected(self):
        code = "from models import Camera\nclass Camera: pass"
        warnings = self.check(code)
        assert len(warnings) == 1
        assert "Camera" in warnings[0]

    def test_function_shadowing_detected(self):
        code = "from utils import process_frame\ndef process_frame(): pass"
        warnings = self.check(code)
        assert len(warnings) == 1
        assert "process_frame" in warnings[0]

    def test_alias_import_no_shadow(self):
        code = "from models import Camera as Cam\nclass Camera: pass"
        # Cam is the alias, Camera is the original — no shadow since Cam != Camera in scope
        # Actually: alias is Cam, but Camera is defined → Cam in imported_names, Camera in defined
        # So no overlap → no warning
        assert self.check(code) == []

    def test_syntax_error_returns_empty(self):
        code = "this is not valid python!!!"
        assert self.check(code) == []


# =====================================================
# 5. _check_data_only_violations (phases.py)
# =====================================================

class TestCheckDataOnlyViolations:
    def setup_method(self):
        from checks import check_data_only_violations
        self.check = check_data_only_violations

    def test_non_data_file_returns_empty(self):
        code = "from models import Camera\ndef process(): pass"
        assert self.check(code, "main.py", ["main.py", "models.py"]) == []

    def test_models_file_project_import_detected(self):
        code = "from main import run\nclass Camera: pass"
        warnings = self.check(code, "models.py", ["main.py", "models.py"])
        assert any("main" in w for w in warnings)

    def test_models_file_public_function_detected(self):
        code = "class Camera: pass\ndef process_image(): pass"
        warnings = self.check(code, "models.py", ["main.py", "models.py"])
        assert any("process_image" in w for w in warnings)

    def test_models_file_private_function_ok(self):
        code = "class Camera: pass\ndef _helper(): pass"
        assert self.check(code, "models.py", ["main.py", "models.py"]) == []

    def test_data_models_file_also_checked(self):
        code = "from main import run"
        warnings = self.check(code, "data_models.py", ["main.py", "data_models.py"])
        assert len(warnings) > 0

    def test_stdlib_import_ok(self):
        code = "from dataclasses import dataclass\nclass Camera: pass"
        assert self.check(code, "models.py", ["main.py", "models.py"]) == []


# =====================================================
# 6. _check_stub_functions (phases.py)
# =====================================================

class TestCheckStubFunctions:
    def setup_method(self):
        from checks import check_stub_functions
        self.check = check_stub_functions

    def test_pass_stub_detected(self):
        code = "def process(data):\n    pass"
        warnings = self.check(code)
        assert len(warnings) == 1
        assert "process" in warnings[0]

    def test_ellipsis_stub_detected(self):
        code = "def process(data):\n    ..."
        warnings = self.check(code)
        assert len(warnings) == 1

    def test_not_implemented_stub_detected(self):
        code = "def process(data):\n    raise NotImplementedError()"
        warnings = self.check(code)
        assert len(warnings) == 1

    def test_not_implemented_bare_detected(self):
        code = "def process(data):\n    raise NotImplementedError"
        warnings = self.check(code)
        assert len(warnings) == 1

    def test_try_pass_stub_detected(self):
        code = "def process(data):\n    try:\n        pass\n    except Exception:\n        pass"
        warnings = self.check(code)
        assert len(warnings) == 1

    def test_real_implementation_ok(self):
        code = "def process(data):\n    return data.upper()"
        assert self.check(code) == []

    def test_empty_function_with_docstring_detected(self):
        code = 'def process(data):\n    """Process data."""'
        warnings = self.check(code)
        assert any("process" in w for w in warnings)

    def test_hardcoded_return_stub_detected(self):
        code = "def recognize(image: bytes) -> str:\n    return 'ABC123'"
        warnings = self.check(code)
        assert len(warnings) == 1
        assert "recognize" in warnings[0]

    def test_hardcoded_return_no_params_ok(self):
        code = "def get_version() -> str:\n    return '1.0'"
        assert self.check(code) == []

    def test_empty_list_return_stub_detected(self):
        code = "def detect(image):\n    vehicles = []\n    return vehicles"
        warnings = self.check(code)
        assert len(warnings) == 1

    def test_param_used_not_flagged(self):
        code = "def process(x):\n    return x.upper()"
        assert self.check(code) == []

    def test_syntax_error_returns_empty(self):
        assert self.check("def broken(") == []


# =====================================================
# 7. _check_contract_compliance (phases.py)
# =====================================================

class TestCheckContractCompliance:
    def setup_method(self):
        from checks import check_contract_compliance
        self.check = check_contract_compliance

    def test_empty_contract_returns_empty(self):
        assert self.check("def foo(): pass", []) == []
        assert self.check("def foo(): pass", None) == []

    def test_all_required_present(self):
        code = "def process_frame(img): pass\nclass Camera: pass"
        contract = [
            {"name": "process_frame", "signature": "def process_frame(img)", "required": True},
            {"name": "Camera", "signature": "class Camera", "required": True},
        ]
        assert self.check(code, contract) == []

    def test_missing_required_function(self):
        code = "def foo(): pass"
        contract = [
            {"name": "process_frame", "signature": "def process_frame(img)", "required": True},
        ]
        missing = self.check(code, contract)
        assert len(missing) == 1
        assert "process_frame" in missing[0]

    def test_missing_required_class(self):
        code = "def foo(): pass"
        contract = [
            {"name": "Camera", "signature": "class Camera", "required": True},
        ]
        missing = self.check(code, contract)
        assert len(missing) == 1
        assert "Camera" in missing[0]

    def test_non_required_not_flagged(self):
        code = "def foo(): pass"
        contract = [
            {"name": "optional_func", "signature": "def optional_func()", "required": False},
        ]
        assert self.check(code, contract) == []

    def test_indented_method_found(self):
        code = "class MyClass:\n    def process(self, data): pass"
        contract = [
            {"name": "process", "signature": "def process(self, data)", "required": True},
        ]
        assert self.check(code, contract) == []

    def test_async_function_found(self):
        code = "async def fetch_data(url): pass"
        contract = [
            {"name": "fetch_data", "signature": "async def fetch_data(url)", "required": True},
        ]
        assert self.check(code, contract) == []

    def test_fuzzy_match_hint(self):
        code = "def proccess_frame(img): pass"
        contract = [
            {"name": "process_frame", "signature": "def process_frame(img)", "required": True},
        ]
        missing = self.check(code, contract)
        assert len(missing) == 1
        assert "proccess_frame" in missing[0]  # fuzzy hint


# =====================================================
# 8. _ensure_a5_imports (phases.py)
# =====================================================

class TestEnsureA5Imports:
    def setup_method(self):
        from checks import ensure_a5_imports
        self.ensure = ensure_a5_imports

    def test_adds_missing_import(self):
        code = "def process(): pass"
        result = self.ensure(code, ["import numpy as np"])
        assert "import numpy as np" in result

    def test_existing_import_not_duplicated(self):
        code = "import numpy as np\ndef process(): pass"
        result = self.ensure(code, ["import numpy as np"])
        assert result.count("import numpy as np") == 1

    def test_merges_typing_imports(self):
        code = "from typing import List\ndef process(): pass"
        result = self.ensure(code, ["from typing import Dict"])
        assert "Dict" in result
        assert "List" in result

    def test_empty_code_returns_unchanged(self):
        assert self.ensure("", ["import os"]) == ""

    def test_empty_imports_returns_unchanged(self):
        code = "def foo(): pass"
        assert self.ensure(code, []) == code

    def test_non_string_imports_skipped(self):
        code = "def foo(): pass"
        result = self.ensure(code, [None, 42, "import os"])
        assert "import os" in result


# =====================================================
# 9. _is_hardcoded_return_stub (phases.py)
# =====================================================

class TestIsHardcodedReturnStub:
    def setup_method(self):
        from checks import _is_hardcoded_return_stub
        import ast
        self.check = _is_hardcoded_return_stub
        self.ast = ast

    def _parse_func(self, code):
        tree = self.ast.parse(code)
        for node in self.ast.walk(tree):
            if isinstance(node, (self.ast.FunctionDef, self.ast.AsyncFunctionDef)):
                return node
        raise ValueError("No function found")

    def test_hardcoded_string_return(self):
        func = self._parse_func("def f(x): return 'hello'")
        assert self.check(func) is True

    def test_hardcoded_number_return(self):
        func = self._parse_func("def f(x): return 42")
        assert self.check(func) is True

    def test_param_used_not_stub(self):
        func = self._parse_func("def f(x): return x.upper()")
        assert self.check(func) is False

    def test_no_params_not_stub(self):
        func = self._parse_func("def get_version(): return '1.0'")
        assert self.check(func) is False

    def test_self_only_not_stub(self):
        func = self._parse_func("def get_name(self): return 'test'")
        assert self.check(func) is False

    def test_empty_list_return_stub(self):
        func = self._parse_func("def f(data):\n    results = []\n    return results")
        assert self.check(func) is True

    def test_empty_dict_return_stub(self):
        func = self._parse_func("def f(data):\n    result = {}\n    return result")
        assert self.check(func) is True


# =====================================================
# 10. Contract validation: _validate_global_imports
# =====================================================

class TestValidateGlobalImports:
    def setup_method(self):
        from contract_validation import _validate_global_imports
        self.validate = _validate_global_imports
        self.logger = logging.getLogger("test_contract")

    def test_keeps_stdlib_imports(self):
        contract = {"global_imports": {"main.py": ["import os", "import json"]}}
        result = self.validate(contract, {}, ["main.py"], self.logger)
        assert "import os" in result["global_imports"]["main.py"]
        assert "import json" in result["global_imports"]["main.py"]

    def test_keeps_project_imports(self):
        contract = {"global_imports": {"main.py": ["from models import Camera"]}}
        result = self.validate(contract, {}, ["main.py", "models.py"], self.logger)
        assert len(result["global_imports"]["main.py"]) == 1

    def test_removes_phantom_project_import(self):
        contract = {"global_imports": {"main.py": ["from nonexistent_module import Foo"]}}
        result = self.validate(contract, {}, ["main.py", "models.py"], self.logger)
        assert len(result["global_imports"]["main.py"]) == 0

    def test_keeps_pip_dependency(self):
        contract = {"global_imports": {"main.py": ["import flask"]}}
        arch = {"dependencies": ["flask"]}
        result = self.validate(contract, arch, ["main.py"], self.logger)
        assert "import flask" in result["global_imports"]["main.py"]

    def test_removes_bare_name(self):
        contract = {"global_imports": {"main.py": ["flask"]}}
        result = self.validate(contract, {}, ["main.py"], self.logger)
        assert len(result["global_imports"]["main.py"]) == 0

    def test_fixes_wrong_pip_package(self):
        contract = {"global_imports": {"main.py": ["import opencv"]}}
        result = self.validate(contract, {}, ["main.py"], self.logger)
        imports = result["global_imports"]["main.py"]
        # opencv should be corrected to cv2
        assert any("cv2" in imp for imp in imports)

    def test_fixes_invalid_identifier(self):
        contract = {"global_imports": {"main.py": ["from opencv-python import cv2"]}}
        result = self.validate(contract, {}, ["main.py"], self.logger)
        imports = result["global_imports"]["main.py"]
        assert any("cv2" in imp for imp in imports)

    def test_auto_adds_to_requirements(self):
        with tempfile.TemporaryDirectory() as td:
            req = Path(td) / "requirements.txt"
            req.write_text("flask\n", encoding="utf-8")
            contract = {"global_imports": {"main.py": ["import requests"]}}
            self.validate(contract, {}, ["main.py"], self.logger, requirements_path=req)
            content = req.read_text(encoding="utf-8")
            assert "requests" in content


# =====================================================
# 11. Contract validation: _validate_import_consistency
# =====================================================

class TestValidateImportConsistency:
    def setup_method(self):
        from contract_validation import _validate_import_consistency
        self.validate = _validate_import_consistency
        self.logger = logging.getLogger("test_contract")

    def test_keeps_valid_cross_file_import(self):
        contract = {
            "file_contracts": {
                "models.py": [{"name": "Camera"}],
                "main.py": [{"name": "main"}],
            },
            "global_imports": {
                "main.py": ["from models import Camera"],
            },
        }
        result = self.validate(contract, self.logger)
        assert "from models import Camera" in result["global_imports"]["main.py"]

    def test_removes_invalid_cross_file_import(self):
        contract = {
            "file_contracts": {
                "models.py": [{"name": "Camera"}],
                "main.py": [{"name": "main"}],
            },
            "global_imports": {
                "main.py": ["from models import NonExistent"],
            },
        }
        result = self.validate(contract, self.logger)
        assert len(result["global_imports"]["main.py"]) == 0

    def test_keeps_non_project_imports(self):
        contract = {
            "file_contracts": {
                "main.py": [{"name": "main"}],
            },
            "global_imports": {
                "main.py": ["from flask import Flask"],
            },
        }
        result = self.validate(contract, self.logger)
        assert "from flask import Flask" in result["global_imports"]["main.py"]

    def test_partial_import_kept(self):
        contract = {
            "file_contracts": {
                "models.py": [{"name": "Camera"}, {"name": "Vehicle"}],
                "main.py": [],
            },
            "global_imports": {
                "main.py": ["from models import Camera, NonExistent"],
            },
        }
        result = self.validate(contract, self.logger)
        imports = result["global_imports"]["main.py"]
        assert len(imports) == 1
        assert "Camera" in imports[0]
        assert "NonExistent" not in imports[0]


# =====================================================
# 12. Contract validation: _validate_requirements_txt
# =====================================================

class TestValidateRequirementsTxt:
    def setup_method(self):
        from contract_validation import validate_requirements_txt
        self.validate_fn = validate_requirements_txt
        self.logger = logging.getLogger("test_contract")

    def test_fixes_wrong_pip_package(self):
        with tempfile.TemporaryDirectory() as td:
            req = Path(td) / "requirements.txt"
            req.write_text("flask\nopencv\nrequests\n", encoding="utf-8")
            self.validate_fn(req, self.logger)
            content = req.read_text(encoding="utf-8")
            assert "opencv" not in content.split("\n")
            assert "opencv-python-headless" in content

    def test_removes_duplicates(self):
        with tempfile.TemporaryDirectory() as td:
            req = Path(td) / "requirements.txt"
            req.write_text("flask\nFlask\nrequests\n", encoding="utf-8")
            self.validate_fn(req, self.logger)
            content = req.read_text(encoding="utf-8")
            lines = [l for l in content.splitlines() if l.strip()]
            # Should keep only one flask entry
            flask_lines = [l for l in lines if "flask" in l.lower()]
            assert len(flask_lines) == 1

    def test_preserves_comments(self):
        with tempfile.TemporaryDirectory() as td:
            req = Path(td) / "requirements.txt"
            req.write_text("# requirements\nflask\n", encoding="utf-8")
            self.validate_fn(req, self.logger)
            content = req.read_text(encoding="utf-8")
            assert "# requirements" in content

    def test_nonexistent_path_no_error(self):
        self.validate_fn(Path("/nonexistent/path/requirements.txt"), self.logger)

    def test_none_path_no_error(self):
        self.validate_fn(None, self.logger)


# =====================================================
# 13. Contract validation: _normalize_file_contracts
# =====================================================

class TestNormalizeFileContracts:
    def setup_method(self):
        from contract_validation import _normalize_file_contracts
        self.normalize = _normalize_file_contracts

    def test_dict_unchanged(self):
        contract = {"file_contracts": {"main.py": [{"name": "main"}]}, "global_imports": {}}
        result = self.normalize(contract)
        assert result["file_contracts"]["main.py"] == [{"name": "main"}]

    def test_list_converted_to_dict(self):
        contract = {
            "file_contracts": [
                {"file": "main.py", "functions": [{"name": "main"}]},
                {"file": "utils.py", "functions": [{"name": "helper"}]},
            ],
            "global_imports": {},
        }
        result = self.normalize(contract)
        assert isinstance(result["file_contracts"], dict)
        assert "main.py" in result["file_contracts"]
        assert "utils.py" in result["file_contracts"]

    def test_removes_non_ascii_entries(self):
        contract = {
            "file_contracts": {
                "main.py": [
                    {"name": "Camera"},
                    {"name": "\u0412\u0438\u0434\u0435\u043e"},  # Russian: Video
                ],
            },
            "global_imports": {},
        }
        result = self.normalize(contract)
        names = [item["name"] for item in result["file_contracts"]["main.py"]]
        assert "Camera" in names
        assert "\u0412\u0438\u0434\u0435\u043e" not in names


# =====================================================
# 14. Contract validation: _inject_signature_type_imports
# =====================================================

class TestInjectSignatureTypeImports:
    def setup_method(self):
        from contract_validation import _inject_signature_type_imports
        self.inject = _inject_signature_type_imports
        self.logger = logging.getLogger("test_contract")

    def test_adds_typing_imports(self):
        contract = {
            "file_contracts": {
                "main.py": [{"name": "f", "signature": "def f(x: List[int]) -> Dict[str, Any]"}],
            },
            "global_imports": {"main.py": []},
        }
        result = self.inject(contract, self.logger)
        imports = result["global_imports"]["main.py"]
        assert any("typing" in imp and "List" in imp for imp in imports)
        assert any("Dict" in imp for imp in imports)
        assert any("Any" in imp for imp in imports)

    def test_adds_numpy_import(self):
        contract = {
            "file_contracts": {
                "main.py": [{"name": "f", "signature": "def f(img: np.ndarray) -> np.ndarray"}],
            },
            "global_imports": {"main.py": []},
        }
        result = self.inject(contract, self.logger)
        imports = result["global_imports"]["main.py"]
        assert "import numpy as np" in imports

    def test_no_duplicate_imports(self):
        contract = {
            "file_contracts": {
                "main.py": [{"name": "f", "signature": "def f(x: np.ndarray)"}],
            },
            "global_imports": {"main.py": ["import numpy as np"]},
        }
        result = self.inject(contract, self.logger)
        imports = result["global_imports"]["main.py"]
        assert imports.count("import numpy as np") == 1


# =====================================================
# 15. Contract validation pipeline order
# =====================================================

class TestContractPipelineOrder:
    """Verifies that the A5 contract validation pipeline applies checks
    in the correct order and that all stages are called."""

    def test_normalize_before_validate(self):
        """List-format file_contracts must be normalized before validation."""
        from contract_validation import _normalize_file_contracts, _validate_import_consistency
        contract = {
            "file_contracts": [
                {"file": "main.py", "functions": [{"name": "main"}]},
            ],
            "global_imports": {"main.py": ["from models import Foo"]},
        }
        # Normalize first
        contract = _normalize_file_contracts(contract)
        assert isinstance(contract["file_contracts"], dict)

    def test_validate_global_imports_removes_phantoms(self):
        """Phantom imports removed before consistency check."""
        from contract_validation import _validate_global_imports, _validate_import_consistency
        logger = logging.getLogger("test")
        contract = {
            "file_contracts": {"main.py": [{"name": "main"}]},
            "global_imports": {"main.py": ["from phantom_module import Foo"]},
        }
        contract = _validate_global_imports(contract, {}, ["main.py"], logger)
        # phantom_module looks like a project import (snake_case) and file doesn't exist
        assert len(contract["global_imports"]["main.py"]) == 0

    def test_full_pipeline_e2e(self):
        """Simulate the full A5 validation pipeline order."""
        from contract_validation import (
            _normalize_file_contracts,
            _validate_global_imports,
            _inject_signature_type_imports,
            _validate_import_consistency,
            _sanitize_implementation_hints,
        )
        logger = logging.getLogger("test")

        contract = {
            "file_contracts": {
                "models.py": [{"name": "Camera", "signature": "class Camera", "required": True}],
                "main.py": [
                    {
                        "name": "process",
                        "signature": "def process(img: np.ndarray) -> List[Camera]",
                        "required": True,
                        "implementation_hints": "Use Camera from models",
                    }
                ],
            },
            "global_imports": {
                "main.py": ["from models import Camera"],
                "models.py": [],
            },
        }

        # Apply pipeline in order
        contract = _normalize_file_contracts(contract)
        contract = _validate_global_imports(contract, {}, ["main.py", "models.py"], logger)
        contract = _inject_signature_type_imports(contract, logger)
        contract = _validate_import_consistency(contract, logger)
        contract = _sanitize_implementation_hints(contract, logger)

        # Verify: Camera import preserved, typing added
        main_imports = contract["global_imports"]["main.py"]
        assert any("Camera" in imp for imp in main_imports)
        assert any("List" in imp for imp in main_imports)


# =====================================================
# 16. Safety valves
# =====================================================

class TestSafetyValves:
    """Test force-approve thresholds and phase skip limits."""

    def test_max_cumulative_threshold(self):
        """MAX_CUMULATIVE = MAX_FILE_ATTEMPTS * 3 = 45."""
        from phase_develop import MAX_CUMULATIVE
        from config import MAX_FILE_ATTEMPTS
        assert MAX_CUMULATIVE == MAX_FILE_ATTEMPTS * 3

    def test_max_file_attempts_escalation(self):
        """File should be escalated after MAX_FILE_ATTEMPTS."""
        from config import MAX_FILE_ATTEMPTS
        assert MAX_FILE_ATTEMPTS == 15

    def test_max_spec_revisions(self):
        """revise_spec limited to MAX_SPEC_REVISIONS."""
        from config import MAX_SPEC_REVISIONS
        assert MAX_SPEC_REVISIONS == 9

    def test_max_test_attempts(self):
        from config import MAX_TEST_ATTEMPTS
        assert MAX_TEST_ATTEMPTS == 6

    def test_bump_phase_fail_counts(self):
        from supervisor import bump_phase_fail
        state = {"phase_fail_counts": {}, "phase_total_fails": {}}
        n = bump_phase_fail(state, "develop")
        assert n == 1
        assert state["phase_total_fails"]["develop"] == 1
        n2 = bump_phase_fail(state, "develop")
        assert n2 == 2
        assert state["phase_total_fails"]["develop"] == 2

    def test_reset_phase_fail_preserves_total(self):
        from supervisor import bump_phase_fail, reset_phase_fail
        state = {"phase_fail_counts": {}, "phase_total_fails": {}}
        bump_phase_fail(state, "develop")
        bump_phase_fail(state, "develop")
        reset_phase_fail(state, "develop")
        assert state["phase_fail_counts"]["develop"] == 0
        assert state["phase_total_fails"]["develop"] == 2  # total not reset

    def test_max_phase_total_fails_threshold(self):
        from config import MAX_PHASE_TOTAL_FAILS
        assert MAX_PHASE_TOTAL_FAILS == 90

    def test_feedback_history_limit(self):
        from state import push_feedback
        from config import MAX_FEEDBACK_HISTORY
        st = {"feedbacks": {}, "feedback_history": {}}
        for i in range(10):
            push_feedback(st, "a.py", f"feedback {i}")
        assert len(st["feedback_history"]["a.py"]) == MAX_FEEDBACK_HISTORY

    def test_cycling_detection_in_feedback(self):
        from state import get_feedback_ctx
        from config import MAX_FEEDBACK_HISTORY
        st = {
            "feedbacks": {},
            "feedback_history": {"a.py": ["same error"] * MAX_FEEDBACK_HISTORY},
        }
        ctx = get_feedback_ctx(st, "a.py")
        assert "КРИТИЧЕСКОЕ ПРЕДУПРЕЖДЕНИЕ" in ctx
        assert "ПРИНЦИПИАЛЬНО ДРУГУЮ" in ctx


# =====================================================
# 17. _parse_import_line (contract.py)
# =====================================================

class TestParseImportLine:
    def setup_method(self):
        from contract_validation import _parse_import_line
        self.parse = _parse_import_line

    def test_simple_import(self):
        result = self.parse("from models import Camera")
        assert result == ("models", ["Camera"])

    def test_multi_import(self):
        result = self.parse("from models import Camera, Vehicle, Plate")
        assert result == ("models", ["Camera", "Vehicle", "Plate"])

    def test_import_with_alias(self):
        result = self.parse("from models import Camera as Cam")
        assert result == ("models", ["Camera"])

    def test_bare_import_returns_none(self):
        assert self.parse("import os") is None

    def test_non_string_returns_none(self):
        assert self.parse(42) is None
        assert self.parse(None) is None

    def test_empty_string_returns_none(self):
        assert self.parse("") is None


# =====================================================
# 18. code_context: validate_imports
# =====================================================

class TestValidateImports:
    def setup_method(self):
        from code_context import validate_imports
        self.validate = validate_imports

    def test_stdlib_import_ok(self):
        code = "import os\nimport json\nimport sys"
        assert self.validate(code, "main.py", ["main.py"], None, "python") == []

    def test_project_import_ok(self):
        code = "from models import Camera"
        assert self.validate(code, "main.py", ["main.py", "models.py"], None, "python") == []

    def test_unknown_module_detected(self):
        code = "import nonexistent_package"
        warnings = self.validate(code, "main.py", ["main.py"], None, "python")
        assert len(warnings) > 0
        assert "nonexistent_package" in warnings[0]

    def test_pip_import_ok_with_requirements(self):
        with tempfile.TemporaryDirectory() as td:
            req = Path(td) / "requirements.txt"
            req.write_text("flask\nrequests\n", encoding="utf-8")
            code = "import flask\nimport requests"
            assert self.validate(code, "main.py", ["main.py"], req, "python") == []


# =====================================================
# 19. code_context: validate_cross_file_names
# =====================================================

class TestValidateCrossFileNames:
    def setup_method(self):
        from code_context import validate_cross_file_names
        self.validate = validate_cross_file_names

    def test_valid_cross_file_import(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td)
            (src / "models.py").write_text("class Camera:\n    pass\n", encoding="utf-8")
            code = "from models import Camera\ncam = Camera()"
            assert self.validate(code, "main.py", ["main.py", "models.py"], src) == []

    def test_invalid_cross_file_import(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td)
            (src / "models.py").write_text("class Vehicle:\n    pass\n", encoding="utf-8")
            code = "from models import Camera"
            warnings = self.validate(code, "main.py", ["main.py", "models.py"], src)
            assert len(warnings) > 0
            assert "Camera" in warnings[0]

    def test_same_file_import_skipped(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td)
            code = "from main import something"
            # Self-import is checked by validate_imports, not cross_file_names
            warnings = self.validate(code, "main.py", ["main.py"], src)
            assert warnings == [], f"Self-import should be skipped, got: {warnings}"

    def test_non_project_import_ignored(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td)
            (src / "main.py").write_text("from flask import Flask", encoding="utf-8")
            code = "from flask import Flask\napp = Flask(__name__)"
            issues = self.validate(code, "main.py", ["main.py"], src)
            assert issues == []


# =====================================================
# 20. code_context: _get_top_level_names
# =====================================================

# =====================================================
# 21. code_context: _find_name_in_classes
# =====================================================

class TestFindNameInClasses:
    def setup_method(self):
        from code_context import find_name_in_classes
        self.find = find_name_in_classes

    def test_finds_method(self):
        code = "class Camera:\n    def take_photo(self): pass"
        assert self.find(code, "take_photo") == "Camera"

    def test_finds_attribute(self):
        code = "class Camera:\n    resolution: int = 1080"
        assert self.find(code, "resolution") == "Camera"

    def test_not_found_returns_none(self):
        code = "class Camera:\n    def take_photo(self): pass"
        assert self.find(code, "nonexistent") is None

    def test_syntax_error_returns_none(self):
        assert self.find("not valid python!!!", "foo") is None


# =====================================================
# 22. _auto_add_requirement (contract.py)
# =====================================================

# =====================================================
# 23. json_utils: _repair_truncated_json
# =====================================================

class TestRepairTruncatedJson:
    def setup_method(self):
        from json_utils import repair_truncated_json
        self.repair = repair_truncated_json

    def test_repairs_truncated_object(self):
        text = '{"code": "def foo(): pass", "status": "ok'
        result = self.repair(text)
        assert result is not None
        assert "code" in result

    def test_repairs_truncated_array(self):
        text = '{"items": [1, 2, 3'
        result = self.repair(text)
        assert result is not None
        assert "items" in result

    def test_balanced_json_returns_none(self):
        text = '{"key": "value"}'
        assert self.repair(text) is None

    def test_deeply_nested(self):
        text = '{"a": {"b": {"c": "val'
        result = self.repair(text)
        assert result is not None
        assert "a" in result


# =====================================================
# 24. _parse_requirements (code_context.py)
# =====================================================

class TestParseRequirements:
    def setup_method(self):
        from code_context import parse_requirements
        self.parse = parse_requirements

    def test_basic_requirements(self):
        with tempfile.TemporaryDirectory() as td:
            req = Path(td) / "requirements.txt"
            req.write_text("flask\nrequests>=2.0\n", encoding="utf-8")
            result = self.parse(req)
            assert "flask" in result
            assert "requests" in result

    def test_wrong_pip_corrected(self):
        with tempfile.TemporaryDirectory() as td:
            req = Path(td) / "requirements.txt"
            req.write_text("opencv\n", encoding="utf-8")
            result = self.parse(req)
            assert "cv2" in result
            assert "opencv_python_headless" in result

    def test_transitive_deps(self):
        with tempfile.TemporaryDirectory() as td:
            req = Path(td) / "requirements.txt"
            req.write_text("tensorflow\n", encoding="utf-8")
            result = self.parse(req)
            assert "tensorflow" in result
            assert "numpy" in result
            assert "keras" in result

    def test_pip_to_import_mapping(self):
        with tempfile.TemporaryDirectory() as td:
            req = Path(td) / "requirements.txt"
            req.write_text("Pillow\npyyaml\n", encoding="utf-8")
            result = self.parse(req)
            assert "pil" in result  # Pillow -> PIL -> pil (lowered)
            assert "yaml" in result

    def test_comments_and_blanks_skipped(self):
        with tempfile.TemporaryDirectory() as td:
            req = Path(td) / "requirements.txt"
            req.write_text("# comment\n\nflask\n", encoding="utf-8")
            result = self.parse(req)
            assert "flask" in result
            assert len(result) > 0

    def test_nonexistent_file(self):
        result = self.parse(Path("/nonexistent/requirements.txt"))
        assert result == set()


# =====================================================
# contract_validation: _auto_add_requirement
# =====================================================

class TestAutoAddRequirement:
    def setup_method(self):
        from contract_validation import _auto_add_requirement
        self.add = _auto_add_requirement
        self.logger = logging.getLogger("test")

    def test_adds_new_package(self):
        with tempfile.TemporaryDirectory() as td:
            req = Path(td) / "requirements.txt"
            req.write_text("flask\n", encoding="utf-8")
            self.add(req, "requests", self.logger)
            content = req.read_text()
            assert "requests" in content

    def test_skips_existing_package(self):
        with tempfile.TemporaryDirectory() as td:
            req = Path(td) / "requirements.txt"
            req.write_text("requests\n", encoding="utf-8")
            self.add(req, "requests", self.logger)
            assert req.read_text().count("requests") == 1

    def test_skips_existing_normalized(self):
        with tempfile.TemporaryDirectory() as td:
            req = Path(td) / "requirements.txt"
            req.write_text("opencv-python\n", encoding="utf-8")
            self.add(req, "opencv_python", self.logger)
            lines = [l for l in req.read_text().splitlines() if l.strip()]
            assert len(lines) == 1

    def test_nonexistent_path(self):
        self.add(Path("/nonexistent/req.txt"), "flask", self.logger)

    def test_corrects_wrong_pip_name(self):
        with tempfile.TemporaryDirectory() as td:
            req = Path(td) / "requirements.txt"
            req.write_text("flask\n", encoding="utf-8")
            self.add(req, "opencv", self.logger)
            content = req.read_text(encoding="utf-8")
            assert "opencv-python-headless" in content


# =====================================================
# contract_validation: _detect_and_fix_circular_imports
# =====================================================

class TestDetectAndFixCircularImports:
    def setup_method(self):
        from contract_validation import _detect_and_fix_circular_imports
        self.detect = _detect_and_fix_circular_imports
        self.logger = logging.getLogger("test")

    def test_no_cycles_unchanged(self):
        contract = {
            "file_contracts": {
                "main.py": [{"name": "main", "signature": "def main()"}],
                "utils.py": [{"name": "helper", "signature": "def helper()"}],
            },
            "global_imports": {
                "main.py": ["from utils import helper"],
                "utils.py": [],
            },
        }
        result = self.detect(contract, ["main.py", "utils.py"], self.logger)
        assert result["global_imports"]["main.py"] == ["from utils import helper"]

    def test_class_cycle_resolved_via_models(self):
        contract = {
            "file_contracts": {
                "a.py": [{"name": "AClass", "signature": "class AClass"}],
                "b.py": [{"name": "BClass", "signature": "class BClass"}],
            },
            "global_imports": {
                "a.py": ["from b import BClass"],
                "b.py": ["from a import AClass"],
            },
        }
        files = ["a.py", "b.py"]
        result = self.detect(contract, files, self.logger)
        # At least one class should be moved to models.py
        assert "models.py" in result["file_contracts"]

    def test_empty_contract(self):
        result = self.detect({"file_contracts": {}, "global_imports": {}}, [], self.logger)
        assert result == {"file_contracts": {}, "global_imports": {}}


# =====================================================
# contract_validation: _inject_cross_file_imports
# =====================================================

class TestInjectCrossFileImports:
    def setup_method(self):
        from contract_validation import _inject_cross_file_imports
        self.inject = _inject_cross_file_imports
        self.logger = logging.getLogger("test")

    def test_injects_missing_import(self):
        contract = {
            "file_contracts": {
                "models.py": [{"name": "Camera", "signature": "class Camera"}],
                "main.py": [{"name": "process", "signature": "def process(cam: Camera) -> str"}],
            },
            "global_imports": {"models.py": [], "main.py": []},
        }
        result = self.inject(contract, self.logger)
        assert any("Camera" in imp for imp in result["global_imports"]["main.py"])

    def test_no_self_import(self):
        contract = {
            "file_contracts": {
                "main.py": [
                    {"name": "MyClass", "signature": "class MyClass"},
                    {"name": "use_it", "signature": "def use_it(x: MyClass)"},
                ],
            },
            "global_imports": {"main.py": []},
        }
        result = self.inject(contract, self.logger)
        assert result["global_imports"]["main.py"] == []

    def test_existing_import_not_duplicated(self):
        contract = {
            "file_contracts": {
                "models.py": [{"name": "Camera", "signature": "class Camera"}],
                "main.py": [{"name": "process", "signature": "def process(cam: Camera)"}],
            },
            "global_imports": {"models.py": [], "main.py": ["from models import Camera"]},
        }
        result = self.inject(contract, self.logger)
        assert result["global_imports"]["main.py"].count("from models import Camera") == 1


# =====================================================
# contract_validation: _validate_data_model_coverage
# =====================================================

class TestValidateDataModelCoverage:
    def setup_method(self):
        from contract_validation import _validate_data_model_coverage
        self.check = _validate_data_model_coverage
        self.logger = logging.getLogger("test")

    def test_all_covered(self):
        contract = {
            "file_contracts": {
                "models.py": [{"name": "Camera", "signature": "class Camera"}],
            },
        }
        specs = {"data_models": [{"name": "Camera"}]}
        assert self.check(contract, specs, self.logger) == []

    def test_missing_model(self):
        contract = {"file_contracts": {"main.py": [{"name": "main", "signature": "def main()"}]}}
        specs = {"data_models": [{"name": "Vehicle"}]}
        missing = self.check(contract, specs, self.logger)
        assert "Vehicle" in missing

    def test_camelcase_match(self):
        contract = {
            "file_contracts": {
                "models.py": [{"name": "LicensePlate", "signature": "class LicensePlate"}],
            },
        }
        specs = {"data_models": [{"name": "license_plate"}]}
        assert self.check(contract, specs, self.logger) == []

    def test_empty_specs(self):
        assert self.check({"file_contracts": {}}, {}, self.logger) == []
        assert self.check({"file_contracts": {}}, {"data_models": []}, self.logger) == []


# =====================================================
# contract_validation: _validate_signature_types
# =====================================================

class TestValidateSignatureTypes:
    def setup_method(self):
        from contract_validation import _validate_signature_types
        self.validate = _validate_signature_types
        self.logger = logging.getLogger("test")

    def test_defined_type_ok(self):
        contract = {
            "file_contracts": {
                "models.py": [{"name": "Camera", "signature": "class Camera"}],
                "main.py": [{"name": "process", "signature": "def process(cam: Camera)"}],
            },
            "global_imports": {"models.py": [], "main.py": []},
        }
        result = self.validate(contract, ["models.py", "main.py"], self.logger)
        # Camera already defined in models.py — no auto-created duplicate should appear
        models_items = result["file_contracts"]["models.py"]
        auto_created = [i for i in models_items if isinstance(i, dict)
                        and i.get("name") == "Camera" and "авто-создан" in i.get("description", "")]
        assert auto_created == [], f"Camera was auto-created despite already existing: {auto_created}"
        # Original Camera item should still be there
        assert any(i.get("name") == "Camera" for i in models_items if isinstance(i, dict))

    def test_undefined_type_creates_class(self):
        contract = {
            "file_contracts": {
                "main.py": [{"name": "process", "signature": "def process(x: FooBar)"}],
            },
            "global_imports": {"main.py": []},
        }
        result = self.validate(contract, ["main.py"], self.logger)
        assert "models.py" in result["file_contracts"]
        names = [i["name"] for i in result["file_contracts"]["models.py"] if isinstance(i, dict)]
        assert "FooBar" in names

    def test_builtin_types_skipped(self):
        contract = {
            "file_contracts": {
                "main.py": [{"name": "process", "signature": "def process(x: str, y: int) -> bool"}],
            },
            "global_imports": {"main.py": []},
        }
        result = self.validate(contract, ["main.py"], self.logger)
        assert "models.py" not in result.get("file_contracts", {}) or \
               result["file_contracts"].get("models.py", []) == []

    def test_pip_imported_types_skipped(self):
        contract = {
            "file_contracts": {
                "main.py": [{"name": "create_app", "signature": "def create_app() -> Flask"}],
            },
            "global_imports": {"main.py": ["from flask import Flask"]},
        }
        result = self.validate(contract, ["main.py"], self.logger)
        # Flask is imported from pip, should NOT be created in models.py
        fc = result["file_contracts"]
        if "models.py" in fc:
            names = [i["name"] for i in fc["models.py"] if isinstance(i, dict)]
            assert "Flask" not in names, f"Flask was auto-created in models.py despite being a pip import: {names}"
        # Either way, main.py should still have create_app
        assert any(i.get("name") == "create_app" for i in fc["main.py"] if isinstance(i, dict))


# =====================================================
# contract_validation: run_a5_validation_pipeline
# =====================================================

class TestRunA5ValidationPipeline:
    def setup_method(self):
        from contract_validation import run_a5_validation_pipeline
        self.run = run_a5_validation_pipeline
        self.logger = logging.getLogger("test")

    def test_basic_contract_passes(self):
        contract = {
            "file_contracts": {
                "main.py": [{"name": "main", "signature": "def main()"}],
            },
            "global_imports": {"main.py": ["import os"]},
        }
        result = self.run(contract, {}, ["main.py"], self.logger)
        assert "main.py" in result["file_contracts"]
        assert isinstance(result["global_imports"]["main.py"], list)

    def test_removes_phantom_imports(self):
        contract = {
            "file_contracts": {"main.py": [{"name": "main", "signature": "def main()"}]},
            "global_imports": {"main.py": ["from phantom_module import Foo"]},
        }
        result = self.run(contract, {}, ["main.py"], self.logger)
        assert len(result["global_imports"]["main.py"]) == 0


# =====================================================
# code_context: get_top_level_names
# =====================================================

class TestGetTopLevelNames:
    def setup_method(self):
        from code_context import get_top_level_names
        self.get = get_top_level_names

    def test_functions_and_classes(self):
        code = "def foo(): pass\nclass Bar: pass\nx = 1"
        names = self.get(code)
        assert "foo" in names
        assert "Bar" in names
        assert "x" in names

    def test_nested_not_included(self):
        code = "def outer():\n    def inner(): pass"
        names = self.get(code)
        assert "outer" in names
        assert "inner" not in names

    def test_syntax_error_uses_regex_fallback(self):
        names = self.get("def broken(")
        # Regex fallback still finds the name
        assert isinstance(names, set)

    def test_assignments(self):
        code = "X = 42\ny, z = 1, 2"
        names = self.get(code)
        assert "X" in names
        assert "y" in names
        assert "z" in names

    def test_import_aliases(self):
        code = "import os\nfrom pathlib import Path\nimport numpy as np"
        names = self.get(code)
        assert "os" in names
        assert "Path" in names
        assert "np" in names


# =====================================================
# code_context: validate_cross_file_names
# =====================================================

# =====================================================
# phase_test: _deapprove_file
# =====================================================

class TestDeapproveFile:
    def setup_method(self):
        from phase_test import _deapprove_file
        self.deapprove = _deapprove_file

    def test_removes_from_approved(self):
        state = {"approved_files": ["main.py"], "feedbacks": {}, "cumulative_file_attempts": {}}
        self.deapprove(state, "main.py", "broken")
        assert "main.py" not in state["approved_files"]
        assert state["feedbacks"]["main.py"] == "broken"
        assert state["cumulative_file_attempts"]["main.py"] == 3

    def test_cumulative_increments(self):
        state = {"approved_files": [], "feedbacks": {}, "cumulative_file_attempts": {"x.py": 5}}
        self.deapprove(state, "x.py", "err", cumulative_bump=3)
        assert state["cumulative_file_attempts"]["x.py"] == 8

    def test_not_in_approved_no_error(self):
        state = {"approved_files": ["other.py"], "feedbacks": {}, "cumulative_file_attempts": {}}
        self.deapprove(state, "main.py", "msg")
        assert state["feedbacks"]["main.py"] == "msg"
        assert "other.py" in state["approved_files"]


# =====================================================
# 18. sync_files_with_a5 (state.py)
# =====================================================

class TestSyncFilesWithA5:
    def setup_method(self):
        from state import sync_files_with_a5
        self.sync = sync_files_with_a5
        self.logger = logging.getLogger("test")

    def test_adds_new_files(self):
        state = {"files": ["main.py"], "feedbacks": {"main.py": ""}}
        self.sync(state, {"main.py", "utils.py"}, self.logger)
        assert "utils.py" in state["files"]
        assert state["feedbacks"]["utils.py"] == ""

    def test_removes_ghost_files(self):
        state = {
            "files": ["main.py", "old.py"],
            "feedbacks": {"main.py": "", "old.py": "fb"},
            "approved_files": ["old.py"],
            "file_attempts": {"old.py": 3},
            "cumulative_file_attempts": {"old.py": 5},
        }
        self.sync(state, {"main.py"}, self.logger)
        assert "old.py" not in state["files"]
        assert "old.py" not in state["feedbacks"]
        assert "old.py" not in state["approved_files"]
        assert "old.py" not in state["file_attempts"]
        assert "old.py" not in state["cumulative_file_attempts"]

    def test_noop_when_synced(self):
        state = {"files": ["a.py", "b.py"], "feedbacks": {"a.py": "", "b.py": ""}}
        self.sync(state, {"a.py", "b.py"}, self.logger)
        assert len(state["files"]) == 2


# =====================================================
# apply_search_replace (checks.py)
# =====================================================

class TestApplySearchReplace:
    def setup_method(self):
        from checks import apply_search_replace
        self.apply = apply_search_replace

    def test_simple_replace(self):
        code = "def foo():\n    return 1\n"
        changes = [{"search": "return 1", "replace": "return 2"}]
        result = self.apply(code, changes)
        assert result is not None
        assert "return 2" in result
        assert "return 1" not in result

    def test_multiple_changes(self):
        code = "a = 1\nb = 2\nc = 3\n"
        changes = [
            {"search": "a = 1", "replace": "a = 10"},
            {"search": "c = 3", "replace": "c = 30"},
        ]
        result = self.apply(code, changes)
        assert result is not None
        assert "a = 10" in result
        assert "b = 2" in result
        assert "c = 30" in result

    def test_search_not_found_returns_none(self):
        code = "x = 1\n"
        changes = [{"search": "y = 2", "replace": "y = 3"}]
        assert self.apply(code, changes) is None

    def test_empty_changes_returns_none(self):
        assert self.apply("code", []) is None

    def test_multiline_search(self):
        code = "def foo():\n    x = 1\n    return x\n"
        changes = [{"search": "    x = 1\n    return x", "replace": "    x = 2\n    return x"}]
        result = self.apply(code, changes)
        assert result is not None
        assert "x = 2" in result

    def test_add_code_via_replace(self):
        code = "import os\n\ndef main():\n    pass\n"
        changes = [{"search": "import os", "replace": "import os\nimport sys"}]
        result = self.apply(code, changes)
        assert result is not None
        assert "import sys" in result

    def test_trailing_whitespace_tolerance(self):
        code = "def foo():  \n    return 1  \n"
        changes = [{"search": "def foo():\n    return 1", "replace": "def foo():\n    return 2"}]
        result = self.apply(code, changes)
        assert result is not None
        assert "return 2" in result


# =====================================================
# get_a5_deps (code_context.py)
# =====================================================

class TestGetA5Deps:
    def setup_method(self):
        from code_context import get_a5_deps
        self.get_deps = get_a5_deps

    def test_deps_first_rest_after(self):
        files = ["main.py", "models.py", "utils.py", "service.py"]
        imports = ["from models import User", "from utils import helper"]
        result = self.get_deps("service.py", imports, files)
        # service.py excluded, deps (models, utils) first, then rest (main)
        assert result[0] == "models.py"
        assert result[1] == "utils.py"
        assert result[2] == "main.py"
        assert "service.py" not in result

    def test_no_deps(self):
        files = ["main.py", "models.py"]
        imports = ["import os", "import sys"]
        result = self.get_deps("main.py", imports, files)
        assert result == ["models.py"]

    def test_self_excluded(self):
        files = ["a.py", "b.py"]
        imports = ["from a import X"]
        result = self.get_deps("a.py", imports, files)
        assert "a.py" not in result
        assert result == ["b.py"]

    def test_empty_imports(self):
        files = ["a.py", "b.py"]
        result = self.get_deps("a.py", [], files)
        assert result == ["b.py"]

    def test_non_project_imports_ignored(self):
        files = ["main.py", "utils.py"]
        imports = ["from flask import Flask", "from utils import helper"]
        result = self.get_deps("main.py", imports, files)
        assert result[0] == "utils.py"  # dep first


# =====================================================
# Experience Memory (experience.py)
# =====================================================

class TestExperienceMemory:
    def setup_method(self):
        import experience
        self._mod = experience
        self._orig_path = experience._EXPERIENCE_PATH
        # Use temp file to avoid polluting real experience store
        import tempfile
        self._tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self._tmp.close()
        experience._EXPERIENCE_PATH = Path(self._tmp.name)
        # Start clean
        Path(self._tmp.name).write_text("[]", encoding="utf-8")

    def teardown_method(self):
        self._mod._EXPERIENCE_PATH = self._orig_path
        Path(self._tmp.name).unlink(missing_ok=True)

    def test_record_and_search(self):
        self._mod.record_experience(
            "ImportError: cannot import name 'Foo' from 'bar'",
            "Added Foo class to bar.py",
            category="develop",
            file="bar.py",
        )
        results = self._mod.search_experience("ImportError cannot import Foo bar")
        assert len(results) == 1
        assert "Foo" in results[0]["fix"]

    def test_deduplication(self):
        self._mod.record_experience("SyntaxError: invalid syntax", "Fixed missing colon")
        self._mod.record_experience("SyntaxError: invalid syntax", "Fixed missing bracket")
        data = self._mod._load()
        assert len(data) == 1
        assert "bracket" in data[0]["fix"]  # Updated to latest fix

    def test_empty_query_returns_nothing(self):
        self._mod.record_experience("some error", "some fix")
        assert self._mod.search_experience("") == []
        assert self._mod.search_experience("   ") == []

    def test_empty_error_not_recorded(self):
        self._mod.record_experience("", "some fix")
        self._mod.record_experience("  ", "some fix")
        assert self._mod._load() == []

    def test_category_filter(self):
        self._mod.record_experience("error A", "fix A", category="develop")
        self._mod.record_experience("error B", "fix B", category="test")
        results = self._mod.search_experience("error", category="develop")
        assert len(results) == 1
        assert results[0]["category"] == "develop"

    def test_format_experience_context_empty(self):
        assert self._mod.format_experience_context([]) == ""

    def test_format_experience_context(self):
        exps = [{"error": "ImportError X", "fix": "add import X"}]
        ctx = self._mod.format_experience_context(exps)
        assert "ImportError X" in ctx
        assert "add import X" in ctx
        assert ctx.startswith("ОПЫТ ПРОШЛЫХ ПРОЕКТОВ")

    def test_max_query_results(self):
        for i in range(10):
            self._mod.record_experience(f"error keyword_{i}", f"fix_{i}")
        results = self._mod.search_experience("error keyword")
        assert len(results) <= 5  # _MAX_QUERY_RESULTS = 5

    def test_scoring_error_field_weighted_higher(self):
        self._mod.record_experience("ImportError numpy missing", "installed numpy")
        self._mod.record_experience("fixed something", "ImportError numpy workaround")
        results = self._mod.search_experience("ImportError numpy")
        # First result should be the one with keywords in error field (score 2 per kw vs 1)
        assert "numpy missing" in results[0]["error"]


# =====================================================
# Dynamic File Priority (build_dependency_order)
# =====================================================

class TestBuildDependencyOrderPriority:
    def setup_method(self):
        from code_context import build_dependency_order
        self.build = build_dependency_order

    def test_more_dependents_first(self):
        """File with more dependents should come before file with fewer dependents."""
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp)
            # core.py: no imports (depended on by both a.py and b.py)
            (src / "core.py").write_text("x = 1", encoding="utf-8")
            # helpers.py: no imports (depended on by only a.py)
            (src / "helpers.py").write_text("y = 2", encoding="utf-8")
            # a.py: imports both core and helpers
            (src / "a.py").write_text("from core import x\nfrom helpers import y", encoding="utf-8")
            # b.py: imports only core
            (src / "b.py").write_text("from core import x", encoding="utf-8")

            files = ["a.py", "b.py", "core.py", "helpers.py"]
            order = self.build(files, src)
            # core.py has 2 dependents, helpers.py has 1 → core first
            assert order.index("core.py") < order.index("helpers.py")
            # Both come before their dependents
            assert order.index("core.py") < order.index("a.py")
            assert order.index("core.py") < order.index("b.py")

    def test_fewer_attempts_first(self):
        """Files with fewer past rejects should be prioritized when dependents are equal."""
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp)
            # Two independent files, same dependents (0)
            (src / "alpha.py").write_text("a = 1", encoding="utf-8")
            (src / "beta.py").write_text("b = 2", encoding="utf-8")

            files = ["alpha.py", "beta.py"]
            # alpha has 5 past attempts, beta has 0
            order = self.build(files, src, file_attempts={"alpha.py": 5, "beta.py": 0})
            assert order.index("beta.py") < order.index("alpha.py")

    def test_backward_compatible_without_attempts(self):
        """Calling without file_attempts still works (backward compatibility)."""
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp)
            (src / "a.py").write_text("x = 1", encoding="utf-8")
            order = self.build(["a.py"], src)
            assert order == ["a.py"]


# =====================================================
# Deterministic Runtime Debugger (diagnose_runtime_error)
# =====================================================

class TestDiagnoseRuntimeError:
    def setup_method(self):
        from checks import diagnose_runtime_error
        self.diagnose = diagnose_runtime_error

    def test_module_not_found(self):
        stderr = 'Traceback (most recent call last):\n  File "main.py", line 1\nModuleNotFoundError: No module named \'numpy\''
        with tempfile.TemporaryDirectory() as tmp:
            result = self.diagnose(stderr, "", ["main.py"], Path(tmp))
        assert result is not None
        assert result["missing_package"] == "numpy"
        assert "numpy" in result["fix"]

    def test_module_not_found_pip_mapping(self):
        """cv2 should map to opencv-python-headless pip package."""
        stderr = "ModuleNotFoundError: No module named 'cv2'"
        with tempfile.TemporaryDirectory() as tmp:
            result = self.diagnose(stderr, "", ["main.py"], Path(tmp))
        assert result is not None
        assert "opencv" in result["missing_package"]

    def test_cannot_import_name(self):
        stderr = "ImportError: cannot import name 'Foo' from 'models'"
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp)
            (src / "models.py").write_text("class Bar:\n    pass\n", encoding="utf-8")
            result = self.diagnose(stderr, "", ["main.py", "models.py"], src)
        assert result is not None
        assert "Foo" in result["fix"]
        assert "Bar" in result["fix"]  # Shows available names

    def test_name_error(self):
        stderr = "NameError: name 'process_data' is not defined"
        with tempfile.TemporaryDirectory() as tmp:
            result = self.diagnose(stderr, "", ["main.py"], Path(tmp))
        assert result is not None
        assert "process_data" in result["fix"]

    def test_attribute_error_module(self):
        stderr = "AttributeError: module 'utils' has no attribute 'helper'"
        with tempfile.TemporaryDirectory() as tmp:
            result = self.diagnose(stderr, "", ["main.py", "utils.py"], Path(tmp))
        assert result is not None
        assert "helper" in result["fix"]
        assert "utils" in result["fix"]

    def test_type_error_missing_arg(self):
        stderr = "TypeError: process() missing 1 required positional argument: 'data'"
        with tempfile.TemporaryDirectory() as tmp:
            result = self.diagnose(stderr, "", ["main.py"], Path(tmp))
        assert result is not None
        assert "argument" in result["fix"].lower()

    def test_syntax_error(self):
        stderr = "SyntaxError: invalid syntax"
        with tempfile.TemporaryDirectory() as tmp:
            result = self.diagnose(stderr, "", ["main.py"], Path(tmp))
        assert result is not None
        assert "синтаксис" in result["fix"].lower() or "Syntax" in result["fix"]

    def test_unknown_error_returns_none(self):
        stderr = "some random output without exceptions"
        with tempfile.TemporaryDirectory() as tmp:
            result = self.diagnose(stderr, "", ["main.py"], Path(tmp))
        assert result is None

    def test_type_error_unexpected_kwarg(self):
        stderr = "TypeError: foo() got an unexpected keyword argument 'bar'"
        with tempfile.TemporaryDirectory() as tmp:
            result = self.diagnose(stderr, "", ["main.py"], Path(tmp))
        assert result is not None
        assert "аргумент" in result["fix"].lower() or "argument" in result["fix"].lower()


# ─────────────────────────────────────────────
# check_truncated_code
# ─────────────────────────────────────────────

class TestCheckTruncatedCode(unittest.TestCase):
    def setUp(self):
        from checks import check_truncated_code
        self.check = check_truncated_code

    def test_normal_code_passes(self):
        code = "def foo():\n    return 42\n"
        assert self.check(code) == ""

    def test_trailing_ellipsis_comment(self):
        code = "def foo():\n    x = 1\n    # ..."
        result = self.check(code)
        assert result != ""
        assert "обрезан" in result

    def test_trailing_bare_ellipsis(self):
        code = "def foo():\n    x = 1\n..."
        result = self.check(code)
        assert result != ""

    def test_empty_code(self):
        assert self.check("") == ""
        assert self.check("   ") == ""

    def test_syntax_error_at_end(self):
        code = "import os\nimport sys\n\ndef foo():\n    x = 1\n    y = 2\n    if x"
        result = self.check(code)
        assert "обрезан" in result or "Код" in result

    def test_syntax_error_not_at_end_passes(self):
        # SyntaxError in the middle — not truncation
        code = "x = (\ndef foo():\n    return 1\n\ndef bar():\n    return 2\n"
        result = self.check(code)
        assert result == ""  # error is on line 2 of 6, not near end


# ─────────────────────────────────────────────
# _normalize_file_contracts — class signature cleanup
# ─────────────────────────────────────────────

class TestNormalizeClassSignatures(unittest.TestCase):
    def setUp(self):
        from contract_validation import _normalize_file_contracts
        self.normalize = _normalize_file_contracts

    def test_strips_ellipsis_from_class(self):
        contract = {
            "file_contracts": {
                "foo.py": [
                    {"name": "Foo", "signature": "class Foo: ... "},
                ]
            }
        }
        result = self.normalize(contract)
        sig = result["file_contracts"]["foo.py"][0]["signature"]
        assert sig == "class Foo", f"Expected 'class Foo', got '{sig}'"

    def test_strips_bare_dots(self):
        contract = {
            "file_contracts": {
                "foo.py": [
                    {"name": "Bar", "signature": "class Bar ..."},
                ]
            }
        }
        result = self.normalize(contract)
        sig = result["file_contracts"]["foo.py"][0]["signature"]
        assert sig == "class Bar", f"Expected 'class Bar', got '{sig}'"

    def test_preserves_class_with_base(self):
        contract = {
            "file_contracts": {
                "foo.py": [
                    {"name": "Child", "signature": "class Child(Base)"},
                ]
            }
        }
        result = self.normalize(contract)
        sig = result["file_contracts"]["foo.py"][0]["signature"]
        assert sig == "class Child(Base)"

    def test_preserves_def_signature(self):
        contract = {
            "file_contracts": {
                "foo.py": [
                    {"name": "run", "signature": "def run() -> None"},
                ]
            }
        }
        result = self.normalize(contract)
        sig = result["file_contracts"]["foo.py"][0]["signature"]
        assert sig == "def run() -> None"


# ─────────────────────────────────────────────
# _generate_skeleton — methods inside class
# ─────────────────────────────────────────────

class TestGenerateSkeleton(unittest.TestCase):
    def test_method_inside_class(self):
        """send_event(self, ...) should be indented inside ExternalSystem."""
        from phase_develop import _generate_skeleton
        import logging
        logger = logging.getLogger("test")
        file_contract = [
            {
                "name": "ExternalSystem",
                "signature": "class ExternalSystem",
                "description": "External system class",
                "implementation_hints": "Use requests",
            },
            {
                "name": "send_event",
                "signature": "def send_event(self, event: dict) -> None",
                "description": "Send event",
                "implementation_hints": "Use requests.post",
            },
        ]
        with tempfile.TemporaryDirectory() as td:
            fp = Path(td) / "external_system.py"
            code = _generate_skeleton(logger, file_contract, [], fp, "external_system.py")
        # send_event should be indented (method of class)
        assert "    def send_event(self" in code, f"Method not indented:\n{code}"
        # class should NOT have literal ...
        assert "class ExternalSystem: ..." not in code

    def test_module_function_not_indented(self):
        """A function without self should stay at module level."""
        from phase_develop import _generate_skeleton
        import logging
        logger = logging.getLogger("test")
        file_contract = [
            {
                "name": "helper",
                "signature": "def helper(x: int) -> int",
                "description": "Helper function",
                "implementation_hints": "",
            },
        ]
        with tempfile.TemporaryDirectory() as td:
            fp = Path(td) / "utils.py"
            code = _generate_skeleton(logger, file_contract, [], fp, "utils.py")
        assert "def helper(x: int)" in code
        # Should NOT be indented
        lines = [l for l in code.splitlines() if "def helper" in l]
        assert lines[0].startswith("def "), f"Should not be indented: {lines[0]}"

    def test_ellipsis_cleaned_from_class(self):
        """class ExternalSystem: ... should become class ExternalSystem:"""
        from phase_develop import _generate_skeleton
        import logging
        logger = logging.getLogger("test")
        file_contract = [
            {
                "name": "Foo",
                "signature": "class Foo: ... ",
                "description": "Foo class",
                "implementation_hints": "",
            },
        ]
        with tempfile.TemporaryDirectory() as td:
            fp = Path(td) / "foo.py"
            code = _generate_skeleton(logger, file_contract, [], fp, "foo.py")
        assert "class Foo:" in code
        assert "class Foo: ..." not in code


# ─────────────────────────────────────────────
# _dedup_global_imports
# ─────────────────────────────────────────────

class TestDedupGlobalImports(unittest.TestCase):
    def setUp(self):
        from contract_validation import _dedup_global_imports
        import logging
        self.dedup = _dedup_global_imports
        self.logger = logging.getLogger("test")

    def test_removes_exact_duplicates(self):
        contract = {
            "global_imports": {
                "foo.py": ["import os", "import os", "import sys"],
            }
        }
        result = self.dedup(contract, self.logger)
        assert result["global_imports"]["foo.py"] == ["import os", "import sys"]

    def test_removes_bare_import_when_from_exists(self):
        contract = {
            "global_imports": {
                "foo.py": [
                    "from cv2 import VideoCapture",
                    "import cv2",
                ],
            }
        }
        result = self.dedup(contract, self.logger)
        imports = result["global_imports"]["foo.py"]
        assert "import cv2" not in imports
        assert "from cv2 import VideoCapture" in imports

    def test_keeps_different_from_imports(self):
        contract = {
            "global_imports": {
                "foo.py": [
                    "from typing import List",
                    "from typing import Dict",
                ],
            }
        }
        result = self.dedup(contract, self.logger)
        imports = result["global_imports"]["foo.py"]
        assert len(imports) == 2


# ─────────────────────────────────────────────
# WRONG_PIP_PACKAGES — opencv_python
# ─────────────────────────────────────────────

class TestWrongPipPackagesOpencv(unittest.TestCase):
    def test_opencv_python_variant_exists(self):
        from code_context import WRONG_PIP_PACKAGES
        assert "opencv_python" in WRONG_PIP_PACKAGES
        assert WRONG_PIP_PACKAGES["opencv_python"][1] == "cv2"

    def test_opencv_python_headless_variant_exists(self):
        from code_context import WRONG_PIP_PACKAGES
        assert "opencv_python_headless" in WRONG_PIP_PACKAGES
        assert WRONG_PIP_PACKAGES["opencv_python_headless"][1] == "cv2"
