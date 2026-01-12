from openjupy.middleware.response_wrapper import ResponseWrapper


class TestMultimodalOutputHandling:
    def setup_method(self) -> None:
        self.wrapper = ResponseWrapper()

    def test_success_with_image_output(self) -> None:
        response = {
            "output": "Plot generated",
            "images": [{"type": "image/png", "data": "base64encodeddata..."}],
        }
        result = self.wrapper.wrap_execution_success(response, output="Plot generated")

        assert result["status"] == "success"
        assert result["images"] == response["images"]
        assert "claude_tip" in result

    def test_success_with_dataframe_display(self) -> None:
        response = {
            "output": "   col1  col2\n0     1     2\n1     3     4",
            "html": "<table>...</table>",
        }
        namespace_vars = ["df", "result_df"]
        result = self.wrapper.wrap_execution_success(
            response, output=response["output"], namespace_vars=namespace_vars
        )

        assert result["status"] == "success"
        assert "DataFrames available" in result["claude_tip"]
        assert result["html"] == response["html"]

    def test_error_with_partial_output(self) -> None:
        response = {
            "partial_output": "Some data was processed before error",
        }
        traceback = """Traceback (most recent call last):
  File "test.py", line 5, in <module>
    result = data / 0
ZeroDivisionError: division by zero"""

        result = self.wrapper.wrap_execution_error(response, traceback)

        assert result["status"] == "error"
        assert result["partial_output"] == "Some data was processed before error"
        assert "error_details" in result
        assert result["error_details"]["type"] == "ZeroDivisionError"


class TestJupyterWorkflowSimulation:
    def setup_method(self) -> None:
        self.wrapper = ResponseWrapper()

    def test_notebook_creation_to_execution_flow(self) -> None:
        create_response = self.wrapper.wrap_notebook_created(
            {}, notebook_path="analysis.ipynb", kernel_name="python3"
        )
        assert create_response["status"] == "success"
        assert "analysis.ipynb" in create_response["claude_tip"]

        cell_response = self.wrapper.wrap_cell_added({}, cell_type="code", cell_index=0)
        assert cell_response["status"] == "success"
        assert "execute" in cell_response["claude_next"].lower()

        exec_response = self.wrapper.wrap_execution_success(
            {}, output="Hello World", namespace_vars=["greeting"]
        )
        assert exec_response["status"] == "success"

    def test_error_recovery_flow(self) -> None:
        error_traceback = """Traceback (most recent call last):
  File "test.py", line 1, in <module>
    import nonexistent_package
ModuleNotFoundError: No module named 'nonexistent_package'"""

        error_response = self.wrapper.wrap_execution_error({}, error_traceback)
        assert error_response["status"] == "error"
        assert "suggested_action" in error_response
        assert "uv add nonexistent_package" in error_response["suggested_action"]

        success_response = self.wrapper.wrap_execution_success(
            {}, output="Package installed and imported successfully"
        )
        assert success_response["status"] == "success"
