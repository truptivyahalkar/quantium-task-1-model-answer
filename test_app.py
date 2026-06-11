"""
Test suite for the Regional Sales Dashboard Dash app.

Uses Dash's ThreadedRunner (part of the official dash[testing] framework) to
spin up the app in a background thread, then queries:

  • GET /          – verifies the server is healthy (HTTP 200)
  • GET /_dash-layout – returns the full component tree as JSON, used to
                        verify each UI element is present

Three tests are defined:

  1. test_header_is_present       – H1 with id="app-header"
  2. test_visualisation_is_present – dcc.Graph with id="sales-chart"
  3. test_region_picker_is_present – dcc.Dropdown with id="region-picker"
"""

import json
import time

import pytest
import requests
from dash.testing.application_runners import ThreadedRunner

from app import app


# ── Helpers ────────────────────────────────────────────────────────────────

def _collect_ids(node: dict) -> dict:
    """
    Recursively walk a Dash layout tree and return a mapping of
    component_id -> component_type for every node that carries an id.
    """
    result = {}
    if not isinstance(node, dict):
        return result

    props = node.get("props", {})
    component_id = props.get("id")
    if component_id:
        result[component_id] = node.get("type", "Unknown")

    # Children can be a single node, a list, or a scalar
    children = props.get("children", [])
    if isinstance(children, list):
        for child in children:
            result.update(_collect_ids(child))
    elif isinstance(children, dict):
        result.update(_collect_ids(children))

    return result


# ── Fixtures ───────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def running_app():
    """
    Start the Dash app in a background thread for the duration of the module,
    yield the base URL, then stop the server.

    ThreadedRunner is the standard lightweight runner provided by dash[testing]
    for integration tests that do not require a full browser / WebDriver.
    """
    runner = ThreadedRunner()
    runner.start(app, start_timeout=5)

    base_url = f"http://localhost:{runner.port}"

    # Wait until the server is accepting connections
    for _ in range(20):
        try:
            requests.get(base_url, timeout=1)
            break
        except requests.exceptions.ConnectionError:
            time.sleep(0.25)

    yield base_url

    runner.stop()


@pytest.fixture(scope="module")
def layout(running_app):
    """
    Fetch /_dash-layout once and parse it into a dict.

    Dash exposes this endpoint to deliver the full component tree as JSON
    before the React renderer has a chance to hydrate the page.  Querying it
    directly lets us verify component presence without a browser or WebDriver.
    """
    response = requests.get(f"{running_app}/_dash-layout", timeout=5)
    assert response.status_code == 200, (
        f"Expected HTTP 200 from /_dash-layout, got {response.status_code}"
    )
    return response.json()


@pytest.fixture(scope="module")
def component_ids(layout):
    """Return {id: type} for every component that declares an id."""
    return _collect_ids(layout)


# ── Tests ──────────────────────────────────────────────────────────────────

class TestDashApp:
    """Verify the three required UI elements are present in the layout tree."""

    def test_header_is_present(self, component_ids, layout):
        """
        Test 1 – Header
        An H1 element with id='app-header' must exist in the layout, and its
        children prop must contain the expected title text.
        """
        assert "app-header" in component_ids, (
            f"No component with id='app-header' found. "
            f"Available ids: {list(component_ids)}"
        )
        assert component_ids["app-header"] == "H1", (
            f"Expected 'app-header' to be an H1, "
            f"got '{component_ids['app-header']}' instead."
        )
        # Also confirm the title text is carried in the layout JSON
        layout_str = json.dumps(layout)
        assert "Regional Sales Dashboard" in layout_str, (
            "Title text 'Regional Sales Dashboard' not found in layout JSON."
        )

    def test_visualisation_is_present(self, component_ids):
        """
        Test 2 – Visualisation
        A dcc.Graph component with id='sales-chart' must exist in the layout.
        """
        assert "sales-chart" in component_ids, (
            f"No component with id='sales-chart' found. "
            f"Available ids: {list(component_ids)}"
        )
        assert component_ids["sales-chart"] == "Graph", (
            f"Expected 'sales-chart' to be a Graph (dcc.Graph), "
            f"got '{component_ids['sales-chart']}' instead."
        )

    def test_region_picker_is_present(self, component_ids):
        """
        Test 3 – Region picker
        A dcc.Dropdown component with id='region-picker' must exist in the
        layout, nested inside a container div with id='region-picker-container'.
        """
        assert "region-picker" in component_ids, (
            f"No component with id='region-picker' found. "
            f"Available ids: {list(component_ids)}"
        )
        assert component_ids["region-picker"] == "Dropdown", (
            f"Expected 'region-picker' to be a Dropdown (dcc.Dropdown), "
            f"got '{component_ids['region-picker']}' instead."
        )
        assert "region-picker-container" in component_ids, (
            f"No component with id='region-picker-container' found. "
            f"Available ids: {list(component_ids)}"
        )
