"""Unit/example tests for generate.py.

Tests run the generator via subprocess (for exit-code tests) or import
generate directly (for unit-level tests).
"""

import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest
import yaml

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

WORKSPACE_ROOT = Path(__file__).parent.parent


def run_generator(cwd: Path, capture_output: bool = True) -> subprocess.CompletedProcess:
    """Run generate.py from *cwd* and return the CompletedProcess result."""
    return subprocess.run(
        [sys.executable, str(WORKSPACE_ROOT / "generate.py")],
        cwd=str(cwd),
        capture_output=capture_output,
        text=True,
    )


def build_html(tmp_workspace: Path) -> str:
    """Copy data.yml into tmp_workspace, run the generator, return rendered HTML."""
    shutil.copy(WORKSPACE_ROOT / "data.yml", tmp_workspace / "data.yml")
    result = run_generator(tmp_workspace)
    assert result.returncode == 0, (
        f"Generator failed.\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )
    return (tmp_workspace / "index.html").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def rendered_html(tmp_workspace):
    """Return the rendered HTML produced from the real data.yml."""
    return build_html(tmp_workspace)


# ---------------------------------------------------------------------------
# 1. Smoke test
# ---------------------------------------------------------------------------

def test_smoke_generates_index_html_with_name(tmp_workspace):
    """Generator creates index.html and it contains the portfolio owner's name."""
    shutil.copy(WORKSPACE_ROOT / "data.yml", tmp_workspace / "data.yml")
    result = run_generator(tmp_workspace)

    assert result.returncode == 0
    index_html = tmp_workspace / "index.html"
    assert index_html.exists(), "index.html was not created"
    content = index_html.read_text(encoding="utf-8")
    assert "Kiran Thakur" in content


# ---------------------------------------------------------------------------
# 2. Nav links test
# ---------------------------------------------------------------------------

def test_nav_links_present(rendered_html):
    """Rendered HTML contains all five expected navigation anchor links."""
    for anchor in ("#about", "#experience", "#skills", "#education", "#contact"):
        assert anchor in rendered_html, f"Nav link '{anchor}' not found in rendered HTML"


# ---------------------------------------------------------------------------
# 3. Employer names test
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("employer", [
    "Infinite Computer Solutions",
    "Extrapreneurs India",
    "I2E Consulting",
    "KayaDev AI Pvt. Ltd",
])
def test_employer_names_present(rendered_html, employer):
    """Rendered HTML contains each employer name from the experience section."""
    assert employer in rendered_html, f"Employer '{employer}' not found in rendered HTML"


# ---------------------------------------------------------------------------
# 4. Education institutions test
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("institution", [
    "BITS Pilani",
    "CDAC Chennai",
    "Pune University",
    "MSBTE",
])
def test_education_institutions_present(rendered_html, institution):
    """Rendered HTML contains each education institution name."""
    assert institution in rendered_html, f"Institution '{institution}' not found in rendered HTML"


# ---------------------------------------------------------------------------
# 5. Email link test
# ---------------------------------------------------------------------------

def test_email_link_present(rendered_html):
    """Rendered HTML contains a mailto link for the portfolio owner's email."""
    assert "mailto:kiranthakur1001@gmail.com" in rendered_html


# ---------------------------------------------------------------------------
# 6. GitHub link test
# ---------------------------------------------------------------------------

def test_github_link_has_target_blank(rendered_html):
    """Rendered HTML contains a GitHub link that opens in a new tab."""
    assert "github.com/Kiran193" in rendered_html
    # The GitHub anchor must carry target="_blank"
    assert 'target="_blank"' in rendered_html


# ---------------------------------------------------------------------------
# 7. Semantic elements test
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tag", ["<header", "<main", "<section", "<nav", "<footer"])
def test_semantic_elements_present(rendered_html, tag):
    """Rendered HTML uses the expected semantic HTML5 elements."""
    assert tag in rendered_html, f"Semantic element '{tag}' not found in rendered HTML"


# ---------------------------------------------------------------------------
# 8. Attribution test
# ---------------------------------------------------------------------------

def test_html5up_attribution_present(rendered_html):
    """Rendered HTML contains the HTML5 UP attribution credit."""
    assert "HTML5 UP" in rendered_html


# ---------------------------------------------------------------------------
# 9. Performance test
# ---------------------------------------------------------------------------

def test_generator_completes_within_5_seconds(tmp_workspace):
    """Generator finishes in under 5 seconds."""
    shutil.copy(WORKSPACE_ROOT / "data.yml", tmp_workspace / "data.yml")

    start = time.time()
    result = run_generator(tmp_workspace)
    elapsed = time.time() - start

    assert result.returncode == 0
    assert elapsed < 5.0, f"Generator took {elapsed:.2f}s — exceeded 5-second limit"


# ---------------------------------------------------------------------------
# 10. Missing required field error test
# ---------------------------------------------------------------------------

def test_missing_required_field_exits_with_error(tmp_workspace):
    """Generator exits with code 1 and names the missing field when 'personal' is absent."""
    # Load real data and remove the 'personal' top-level key
    data = yaml.safe_load((WORKSPACE_ROOT / "data.yml").read_text(encoding="utf-8"))
    del data["personal"]

    broken_data_path = tmp_workspace / "data.yml"
    broken_data_path.write_text(yaml.dump(data), encoding="utf-8")

    result = run_generator(tmp_workspace)

    assert result.returncode == 1, (
        f"Expected exit code 1, got {result.returncode}.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    combined_output = result.stdout + result.stderr
    assert "personal" in combined_output, (
        f"Expected field name 'personal' in output, got:\n{combined_output}"
    )
