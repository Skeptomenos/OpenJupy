
from openjupy.middleware.error_handler import ErrorAnalysis, ErrorHandler


class TestParseTraceback:
    def setup_method(self) -> None:
        self.handler = ErrorHandler()

    def test_parse_module_not_found_error(self) -> None:
        traceback = """Traceback (most recent call last):
  File "test.py", line 1, in <module>
    import cv2
ModuleNotFoundError: No module named 'cv2'"""

        result = self.handler.parse_traceback(traceback)

        assert result.error_type == "ModuleNotFoundError"
        assert result.error_message == "No module named 'cv2'"
        assert result.file_path == "test.py"
        assert result.line_number == 1
        assert result.function_name == "<module>"
        assert result.code_context == "import cv2"
        assert result.extracted_values["module"] == "cv2"
        assert result.extracted_values["package"] == "opencv-python"

    def test_parse_name_error(self) -> None:
        traceback = """Traceback (most recent call last):
  File "script.py", line 10, in main
    print(undefined_var)
NameError: name 'undefined_var' is not defined"""

        result = self.handler.parse_traceback(traceback)

        assert result.error_type == "NameError"
        assert "undefined_var" in result.error_message
        assert result.extracted_values["name"] == "undefined_var"

    def test_parse_attribute_error(self) -> None:
        traceback = """Traceback (most recent call last):
  File "app.py", line 5, in process
    obj.nonexistent_method()
AttributeError: 'str' object has no attribute 'nonexistent_method'"""

        result = self.handler.parse_traceback(traceback)

        assert result.error_type == "AttributeError"
        assert result.extracted_values["type"] == "str"
        assert result.extracted_values["attribute"] == "nonexistent_method"

    def test_parse_key_error(self) -> None:
        traceback = """Traceback (most recent call last):
  File "data.py", line 3, in get_value
    return data['missing_key']
KeyError: 'missing_key'"""

        result = self.handler.parse_traceback(traceback)

        assert result.error_type == "KeyError"
        assert result.extracted_values["key"] == "missing_key"

    def test_parse_file_not_found_error(self) -> None:
        traceback = """Traceback (most recent call last):
  File "loader.py", line 2, in load
    open('/path/to/missing.txt')
FileNotFoundError: [Errno 2] No such file or directory: '/path/to/missing.txt'"""

        result = self.handler.parse_traceback(traceback)

        assert result.error_type == "FileNotFoundError"
        assert result.extracted_values["path"] == "/path/to/missing.txt"

    def test_parse_import_error(self) -> None:
        traceback = """Traceback (most recent call last):
  File "test.py", line 1, in <module>
    from sklearn import nonexistent
ImportError: cannot import name 'nonexistent' from 'sklearn'"""

        result = self.handler.parse_traceback(traceback)

        assert result.error_type == "ImportError"
        assert result.extracted_values["name"] == "nonexistent"

    def test_parse_minimal_traceback(self) -> None:
        traceback = "ValueError: invalid literal"

        result = self.handler.parse_traceback(traceback)

        assert result.error_type == "ValueError"
        assert result.error_message == "invalid literal"
        assert result.file_path is None
        assert result.line_number is None


class TestAnalyzeError:
    def setup_method(self) -> None:
        self.handler = ErrorHandler()

    def test_analyze_module_not_found_suggests_install(self) -> None:
        traceback = """Traceback (most recent call last):
  File "test.py", line 1, in <module>
    import sklearn
ModuleNotFoundError: No module named 'sklearn'"""

        result = self.handler.analyze_error(traceback)

        assert isinstance(result, ErrorAnalysis)
        assert result.parsed_error.error_type == "ModuleNotFoundError"
        assert result.fix_suggestion is not None
        assert "uv add scikit-learn" in result.claude_next
        assert result.suggested_action == "uv add scikit-learn"

    def test_analyze_name_error_suggests_definition(self) -> None:
        traceback = """Traceback (most recent call last):
  File "test.py", line 1, in <module>
    print(x)
NameError: name 'x' is not defined"""

        result = self.handler.analyze_error(traceback)

        assert "Define 'x'" in result.claude_next or "x" in result.claude_next

    def test_analyze_file_not_found_suggests_verify(self) -> None:
        traceback = """Traceback (most recent call last):
  File "test.py", line 1, in <module>
    open('missing.txt')
FileNotFoundError: [Errno 2] No such file or directory: 'missing.txt'"""

        result = self.handler.analyze_error(traceback)

        assert "Verify" in result.claude_next or "path" in result.claude_next.lower()

    def test_analyze_unknown_error_provides_generic_guidance(self) -> None:
        traceback = "CustomError: something went wrong"

        result = self.handler.analyze_error(traceback)

        assert result.parsed_error.error_type == "CustomError"
        assert result.fix_suggestion is None
        assert result.claude_next is not None


class TestEnrichResponse:
    def setup_method(self) -> None:
        self.handler = ErrorHandler()

    def test_enrich_adds_claude_fields(self) -> None:
        response = {"output": "error occurred"}
        traceback = """Traceback (most recent call last):
  File "test.py", line 1, in <module>
    import pandas
ModuleNotFoundError: No module named 'pandas'"""

        result = self.handler.enrich_response(response, traceback)

        assert "claude_tip" in result
        assert "claude_next" in result
        assert "error_details" in result
        assert result["error_details"]["type"] == "ModuleNotFoundError"

    def test_enrich_preserves_original_response(self) -> None:
        response = {"original_key": "original_value", "status": "failed"}
        traceback = "ValueError: bad value"

        result = self.handler.enrich_response(response, traceback)

        assert result["original_key"] == "original_value"
        assert result["status"] == "failed"

    def test_enrich_adds_suggested_action_for_module_error(self) -> None:
        response = {}
        traceback = """Traceback (most recent call last):
  File "test.py", line 1, in <module>
    import PIL
ModuleNotFoundError: No module named 'PIL'"""

        result = self.handler.enrich_response(response, traceback)

        assert "suggested_action" in result
        assert result["suggested_action"] == "uv add pillow"
