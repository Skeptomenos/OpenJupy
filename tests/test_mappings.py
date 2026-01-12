from openjupy.mappings.error_fixes import ERROR_FIX_MAP, FixSuggestion, get_fix_suggestion
from openjupy.mappings.packages import PACKAGE_NAME_MAP, get_correct_package_name


class TestGetCorrectPackageName:
    def test_cv2_maps_to_opencv_python(self) -> None:
        assert get_correct_package_name("cv2") == "opencv-python"

    def test_sklearn_maps_to_scikit_learn(self) -> None:
        assert get_correct_package_name("sklearn") == "scikit-learn"

    def test_pil_maps_to_pillow(self) -> None:
        assert get_correct_package_name("PIL") == "pillow"

    def test_yaml_maps_to_pyyaml(self) -> None:
        assert get_correct_package_name("yaml") == "pyyaml"

    def test_bs4_maps_to_beautifulsoup4(self) -> None:
        assert get_correct_package_name("bs4") == "beautifulsoup4"

    def test_dotenv_maps_to_python_dotenv(self) -> None:
        assert get_correct_package_name("dotenv") == "python-dotenv"

    def test_submodule_uses_base_module(self) -> None:
        assert get_correct_package_name("sklearn.ensemble") == "scikit-learn"
        assert get_correct_package_name("PIL.Image") == "pillow"

    def test_unknown_module_returns_itself(self) -> None:
        assert get_correct_package_name("numpy") == "numpy"
        assert get_correct_package_name("requests") == "requests"
        assert get_correct_package_name("unknown_module") == "unknown_module"

    def test_package_map_has_common_mismatches(self) -> None:
        expected_mappings = {
            "cv2": "opencv-python",
            "sklearn": "scikit-learn",
            "PIL": "pillow",
            "yaml": "pyyaml",
            "bs4": "beautifulsoup4",
            "dateutil": "python-dateutil",
            "dotenv": "python-dotenv",
            "jwt": "pyjwt",
        }
        for import_name, package_name in expected_mappings.items():
            assert PACKAGE_NAME_MAP[import_name] == package_name


class TestErrorFixMap:
    def test_module_not_found_error_exists(self) -> None:
        assert "ModuleNotFoundError" in ERROR_FIX_MAP
        fix = ERROR_FIX_MAP["ModuleNotFoundError"]
        assert isinstance(fix, FixSuggestion)
        assert "{module}" in fix.message_template

    def test_name_error_exists(self) -> None:
        assert "NameError" in ERROR_FIX_MAP
        fix = ERROR_FIX_MAP["NameError"]
        assert "{name}" in fix.message_template

    def test_key_error_exists(self) -> None:
        assert "KeyError" in ERROR_FIX_MAP
        fix = ERROR_FIX_MAP["KeyError"]
        assert "{key}" in fix.message_template

    def test_file_not_found_error_exists(self) -> None:
        assert "FileNotFoundError" in ERROR_FIX_MAP
        fix = ERROR_FIX_MAP["FileNotFoundError"]
        assert "{path}" in fix.message_template

    def test_all_common_errors_covered(self) -> None:
        common_errors = [
            "ModuleNotFoundError",
            "ImportError",
            "FileNotFoundError",
            "PermissionError",
            "NameError",
            "AttributeError",
            "TypeError",
            "ValueError",
            "KeyError",
            "IndexError",
            "ZeroDivisionError",
            "SyntaxError",
            "IndentationError",
        ]
        for error in common_errors:
            assert error in ERROR_FIX_MAP, f"{error} not in ERROR_FIX_MAP"


class TestGetFixSuggestion:
    def test_returns_fix_for_known_error(self) -> None:
        fix = get_fix_suggestion("ModuleNotFoundError", "No module named 'foo'")
        assert fix is not None
        assert isinstance(fix, FixSuggestion)

    def test_returns_none_for_unknown_error(self) -> None:
        fix = get_fix_suggestion("CustomError", "something happened")
        assert fix is None

    def test_ignores_context_parameter(self) -> None:
        fix = get_fix_suggestion("ValueError", "bad value", _context={"key": "value"})
        assert fix is not None
