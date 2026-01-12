from openjupy.middleware.response_wrapper import ResponseWrapper


class TestWrapExecutionSuccess:
    def setup_method(self) -> None:
        self.wrapper = ResponseWrapper()

    def test_success_with_output(self) -> None:
        response = {"result": "data"}
        result = self.wrapper.wrap_execution_success(response, output="Hello World")

        assert result["status"] == "success"
        assert "claude_tip" in result
        assert "successfully" in result["claude_tip"]
        assert "claude_next" in result

    def test_success_without_output(self) -> None:
        response = {}
        result = self.wrapper.wrap_execution_success(response, output=None)

        assert result["status"] == "success"
        assert "no output" in result["claude_tip"]

    def test_success_with_dataframe_vars(self) -> None:
        response = {}
        namespace_vars = ["df", "results_df", "x", "y"]
        result = self.wrapper.wrap_execution_success(
            response, output="done", namespace_vars=namespace_vars
        )

        assert "DataFrames available" in result["claude_tip"]
        assert "df" in result["claude_tip"]
        assert ".head()" in result["claude_next"] or ".describe()" in result["claude_next"]

    def test_success_with_namespace_vars(self) -> None:
        response = {}
        namespace_vars = ["x", "y", "z"]
        result = self.wrapper.wrap_execution_success(
            response, output="done", namespace_vars=namespace_vars
        )

        assert "3 variable(s)" in result["claude_tip"]

    def test_preserves_original_response(self) -> None:
        response = {"original": "value", "count": 42}
        result = self.wrapper.wrap_execution_success(response)

        assert result["original"] == "value"
        assert result["count"] == 42


class TestWrapExecutionError:
    def setup_method(self) -> None:
        self.wrapper = ResponseWrapper()

    def test_error_sets_status(self) -> None:
        response = {}
        traceback = "ValueError: invalid"
        result = self.wrapper.wrap_execution_error(response, traceback)

        assert result["status"] == "error"

    def test_error_adds_claude_fields(self) -> None:
        response = {}
        traceback = """Traceback (most recent call last):
  File "test.py", line 1, in <module>
    import pandas
ModuleNotFoundError: No module named 'pandas'"""

        result = self.wrapper.wrap_execution_error(response, traceback)

        assert "claude_tip" in result
        assert "claude_next" in result
        assert "error_details" in result

    def test_error_preserves_original_response(self) -> None:
        response = {"original": "data"}
        traceback = "TypeError: bad type"
        result = self.wrapper.wrap_execution_error(response, traceback)

        assert result["original"] == "data"


class TestWrapNotebookCreated:
    def setup_method(self) -> None:
        self.wrapper = ResponseWrapper()

    def test_notebook_created_basic(self) -> None:
        response = {}
        result = self.wrapper.wrap_notebook_created(
            response, notebook_path="/path/to/notebook.ipynb"
        )

        assert result["status"] == "success"
        assert "/path/to/notebook.ipynb" in result["claude_tip"]
        assert (
            "jupyter_add_cell" in result["claude_next"]
            or "jupyter_execute_cell" in result["claude_next"]
        )

    def test_notebook_created_with_kernel(self) -> None:
        response = {}
        result = self.wrapper.wrap_notebook_created(
            response, notebook_path="test.ipynb", kernel_name="python3"
        )

        assert "python3" in result["claude_tip"]


class TestWrapCellAdded:
    def setup_method(self) -> None:
        self.wrapper = ResponseWrapper()

    def test_code_cell_added(self) -> None:
        response = {}
        result = self.wrapper.wrap_cell_added(response, cell_type="code", cell_index=0)

        assert result["status"] == "success"
        assert "Code cell" in result["claude_tip"]
        assert "index 0" in result["claude_tip"]
        assert "execute" in result["claude_next"].lower()

    def test_markdown_cell_added(self) -> None:
        response = {}
        result = self.wrapper.wrap_cell_added(response, cell_type="markdown", cell_index=1)

        assert "Markdown cell" in result["claude_tip"]
        assert "index 1" in result["claude_tip"]


class TestWrapKernelStatus:
    def setup_method(self) -> None:
        self.wrapper = ResponseWrapper()

    def test_kernel_running(self) -> None:
        response = {}
        result = self.wrapper.wrap_kernel_status(response, is_alive=True)

        assert result["status"] == "running"
        assert "running" in result["claude_tip"]

    def test_kernel_running_with_execution_count(self) -> None:
        response = {}
        result = self.wrapper.wrap_kernel_status(response, is_alive=True, execution_count=5)

        assert "5" in result["claude_tip"]

    def test_kernel_stopped(self) -> None:
        response = {}
        result = self.wrapper.wrap_kernel_status(response, is_alive=False)

        assert result["status"] == "stopped"
        assert "not running" in result["claude_tip"]


class TestWrapGenericSuccess:
    def setup_method(self) -> None:
        self.wrapper = ResponseWrapper()

    def test_generic_success_basic(self) -> None:
        response = {}
        result = self.wrapper.wrap_generic_success(response, operation="File saved")

        assert result["status"] == "success"
        assert "File saved" in result["claude_tip"]
        assert "successfully" in result["claude_tip"]

    def test_generic_success_with_details(self) -> None:
        response = {}
        result = self.wrapper.wrap_generic_success(
            response, operation="Export", details="Saved to output.csv"
        )

        assert "Export" in result["claude_tip"]
        assert "output.csv" in result["claude_tip"]
