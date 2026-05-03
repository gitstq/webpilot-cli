"""
YAML workflow engine for WebPilot-CLI.

Parses YAML workflow files and executes browser automation steps
sequentially.  Supported step types:
  - navigate: Open a URL
  - extract: Extract content from the current page
  - screenshot: Take a screenshot
  - wait: Pause for a number of seconds
  - condition: Execute steps based on a variable condition
  - loop: Repeat steps a number of times

Variables can be passed between steps using the ``${var}`` syntax.
"""

import re
import time
from typing import Any, Dict, List, Optional

from .browser import Browser
from .extractor import extract_content
from .utils import ProgressBar, parse_yaml, validate_url


# ---------------------------------------------------------------------------
# Variable substitution
# ---------------------------------------------------------------------------

def substitute_variables(text: str, variables: Dict[str, Any]) -> str:
    """Replace ``${var}`` placeholders in *text* with values from *variables*.

    Args:
        text: The template string.
        variables: A dict mapping variable names to values.

    Returns:
        The string with all placeholders replaced.
    """
    def replacer(match: re.Match) -> str:
        var_name = match.group(1)
        value = variables.get(var_name, match.group(0))
        return str(value)

    return re.sub(r"\$\{(\w+)\}", replacer, text)


def substitute_in_dict(data: Dict[str, Any], variables: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively substitute variables in a dict's string values.

    Args:
        data: The input dict.
        variables: Variable bindings.

    Returns:
        A new dict with substituted values.
    """
    result: Dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, str):
            result[key] = substitute_variables(value, variables)
        elif isinstance(value, dict):
            result[key] = substitute_in_dict(value, variables)
        elif isinstance(value, list):
            result[key] = [
                substitute_variables(v, variables) if isinstance(v, str) else v
                for v in value
            ]
        else:
            result[key] = value
    return result


# ---------------------------------------------------------------------------
# Workflow engine
# ---------------------------------------------------------------------------

class WorkflowEngine:
    """Execute YAML-defined browser automation workflows.

    Args:
        browser: A Browser instance to use for automation.
        verbose: Whether to print verbose output.
    """

    def __init__(self, browser: Optional[Browser] = None, verbose: bool = False) -> None:
        self.browser = browser or Browser()
        self.verbose = verbose
        self.variables: Dict[str, Any] = {}
        self.results: List[Dict[str, Any]] = []

    def load_workflow(self, yaml_text: str) -> Dict[str, Any]:
        """Parse a YAML workflow document.

        Args:
            yaml_text: The YAML workflow content.

        Returns:
            The parsed workflow dict.
        """
        workflow = parse_yaml(yaml_text)
        if not isinstance(workflow, dict):
            raise ValueError("Workflow must be a YAML mapping (dict)")
        return workflow

    def load_workflow_file(self, filepath: str) -> Dict[str, Any]:
        """Load and parse a YAML workflow file.

        Args:
            filepath: Path to the YAML file.

        Returns:
            The parsed workflow dict.
        """
        with open(filepath, "r", encoding="utf-8") as f:
            return self.load_workflow(f.read())

    def run(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow.

        Args:
            workflow: The parsed workflow dict.

        Returns:
            A result dict with status, steps, and variables.
        """
        # Initialize variables from workflow 'vars' section
        initial_vars = workflow.get("vars", {})
        if isinstance(initial_vars, dict):
            self.variables.update(initial_vars)

        # Get steps
        steps = workflow.get("steps", [])
        if not steps:
            return {
                "status": "error",
                "error": "No steps defined in workflow",
                "steps": [],
                "variables": self.variables,
            }

        # Execute steps
        total = len(steps)
        progress = ProgressBar(total, prefix="Workflow", width=30)

        for i, step in enumerate(steps, 1):
            if not isinstance(step, dict):
                self.results.append({
                    "name": f"Step {i}",
                    "status": "error",
                    "error": "Invalid step format",
                })
                continue

            # Substitute variables in step definition
            step = substitute_in_dict(step, self.variables)

            step_name = step.get("name", f"Step {i}")
            step_type = step.get("type", "")

            if self.verbose:
                progress.set(i - 1)

            try:
                result = self._execute_step(step, step_name, step_type)
                self.results.append(result)

                # Store output in variables if 'save' is specified
                save_as = step.get("save")
                if save_as and result.get("output") is not None:
                    self.variables[save_as] = result["output"]

            except Exception as e:
                self.results.append({
                    "name": step_name,
                    "type": step_type,
                    "status": "error",
                    "error": str(e),
                })
                # Check if workflow should stop on error
                if workflow.get("stop_on_error", True):
                    progress.finish()
                    return {
                        "status": "error",
                        "steps": self.results,
                        "variables": self.variables,
                        "error": f"Step '{step_name}' failed: {e}",
                    }

            progress.set(i)

        progress.finish()

        return {
            "status": "success",
            "steps": self.results,
            "variables": self.variables,
        }

    def _execute_step(
        self, step: Dict[str, Any], name: str, step_type: str
    ) -> Dict[str, Any]:
        """Execute a single workflow step.

        Args:
            step: The step definition dict.
            name: The step name.
            step_type: The step type string.

        Returns:
            A result dict with name, type, status, and optional output.
        """
        if step_type == "navigate":
            return self._step_navigate(step, name)
        elif step_type == "extract":
            return self._step_extract(step, name)
        elif step_type == "screenshot":
            return self._step_screenshot(step, name)
        elif step_type == "wait":
            return self._step_wait(step, name)
        elif step_type == "condition":
            return self._step_condition(step, name)
        elif step_type == "loop":
            return self._step_loop(step, name)
        elif step_type == "set_variable":
            return self._step_set_variable(step, name)
        else:
            return {
                "name": name,
                "type": step_type,
                "status": "error",
                "error": f"Unknown step type: {step_type}",
            }

    # -- Individual step handlers ------------------------------------------

    def _step_navigate(self, step: Dict[str, Any], name: str) -> Dict[str, Any]:
        """Navigate to a URL."""
        url = step.get("url", "")
        if not url:
            return {"name": name, "type": "navigate", "status": "error", "error": "No URL specified"}

        html = self.browser.fetch(url)
        info = self.browser.get_page_info()

        return {
            "name": name,
            "type": "navigate",
            "status": "success",
            "output": {"url": url, "title": info.get("title", ""), "content_length": len(html)},
        }

    def _step_extract(self, step: Dict[str, Any], name: str) -> Dict[str, Any]:
        """Extract content from the current page."""
        html = self.browser._last_html
        if not html:
            return {"name": name, "type": "extract", "status": "error", "error": "No page loaded"}

        url = self.browser._last_url
        data = extract_content(html, url)

        # Filter what to extract if 'fields' is specified
        fields = step.get("fields")
        if fields and isinstance(fields, list):
            data = {k: v for k, v in data.items() if k in fields}

        return {
            "name": name,
            "type": "extract",
            "status": "success",
            "output": data,
        }

    def _step_screenshot(self, step: Dict[str, Any], name: str) -> Dict[str, Any]:
        """Take a screenshot of the current page."""
        html = self.browser._last_html
        if not html:
            return {"name": name, "type": "screenshot", "status": "error", "error": "No page loaded"}

        output_path = step.get("output", "screenshot.html")
        stype = step.get("format", "html")

        if stype == "ascii":
            ascii_art = self.browser.ascii_screenshot()
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(ascii_art)
        else:
            output_path = self.browser.html_screenshot(output_path)

        return {
            "name": name,
            "type": "screenshot",
            "status": "success",
            "output": {"path": output_path, "format": stype},
        }

    def _step_wait(self, step: Dict[str, Any], name: str) -> Dict[str, Any]:
        """Wait for a specified number of seconds."""
        seconds = step.get("seconds", 1)
        try:
            seconds = float(seconds)
        except (ValueError, TypeError):
            seconds = 1.0

        time.sleep(seconds)

        return {
            "name": name,
            "type": "wait",
            "status": "success",
            "output": {"waited": seconds},
        }

    def _step_condition(self, step: Dict[str, Any], name: str) -> Dict[str, Any]:
        """Execute sub-steps based on a condition."""
        variable = step.get("variable", "")
        operator = step.get("operator", "exists")
        value = step.get("value", "")
        then_steps = step.get("then", [])
        else_steps = step.get("else", [])

        var_value = self.variables.get(variable)

        # Evaluate condition
        condition_met = False
        if operator == "exists":
            condition_met = var_value is not None
        elif operator == "equals":
            condition_met = str(var_value) == str(value)
        elif operator == "not_equals":
            condition_met = str(var_value) != str(value)
        elif operator == "contains":
            condition_met = str(value) in str(var_value) if var_value else False
        elif operator == "greater_than":
            try:
                condition_met = float(var_value) > float(value)
            except (ValueError, TypeError):
                condition_met = False
        elif operator == "less_than":
            try:
                condition_met = float(var_value) < float(value)
            except (ValueError, TypeError):
                condition_met = False
        elif operator == "is_true":
            condition_met = bool(var_value)
        elif operator == "is_false":
            condition_met = not bool(var_value)

        # Execute appropriate branch
        steps_to_run = then_steps if condition_met else else_steps
        sub_results = []
        for sub_step in steps_to_run:
            if isinstance(sub_step, dict):
                sub_step = substitute_in_dict(sub_step, self.variables)
                sub_name = sub_step.get("name", "sub-step")
                sub_type = sub_step.get("type", "")
                result = self._execute_step(sub_step, sub_name, sub_type)
                sub_results.append(result)

                save_as = sub_step.get("save")
                if save_as and result.get("output") is not None:
                    self.variables[save_as] = result["output"]

        return {
            "name": name,
            "type": "condition",
            "status": "success",
            "output": {
                "condition_met": condition_met,
                "sub_steps": len(sub_results),
            },
        }

    def _step_loop(self, step: Dict[str, Any], name: str) -> Dict[str, Any]:
        """Execute sub-steps in a loop."""
        count = step.get("count", 1)
        try:
            count = int(count)
        except (ValueError, TypeError):
            count = 1

        loop_steps = step.get("steps", [])
        loop_var = step.get("index_var", "i")

        all_results = []
        for i in range(count):
            self.variables[loop_var] = i
            for sub_step in loop_steps:
                if isinstance(sub_step, dict):
                    sub_step = substitute_in_dict(sub_step, self.variables)
                    sub_name = sub_step.get("name", f"loop-{i}")
                    sub_type = sub_step.get("type", "")
                    result = self._execute_step(sub_step, sub_name, sub_type)
                    all_results.append(result)

                    save_as = sub_step.get("save")
                    if save_as and result.get("output") is not None:
                        self.variables[save_as] = result["output"]

        return {
            "name": name,
            "type": "loop",
            "status": "success",
            "output": {
                "iterations": count,
                "total_steps": len(all_results),
            },
        }

    def _step_set_variable(self, step: Dict[str, Any], name: str) -> Dict[str, Any]:
        """Set a workflow variable."""
        var_name = step.get("name", "")
        var_value = step.get("value", "")

        if not var_name:
            return {"name": name, "type": "set_variable", "status": "error", "error": "No variable name"}

        self.variables[var_name] = var_value

        return {
            "name": name,
            "type": "set_variable",
            "status": "success",
            "output": {"variable": var_name, "value": var_value},
        }
