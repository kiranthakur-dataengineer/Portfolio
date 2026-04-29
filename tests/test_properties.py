"""Property-based tests for generate.py using Hypothesis.

Each test is tagged with the design property it validates.
"""

# Feature: personal-portfolio-website, Property 1: Reverse-Chronological Ordering

import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

import yaml
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

WORKSPACE_ROOT = Path(__file__).parent.parent

# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

# A non-empty text string safe for use in HTML/YAML (printable ASCII letters,
# digits, and a few punctuation chars — no leading/trailing whitespace to
# avoid HTML text-node stripping discrepancies).
safe_text = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_",
    min_size=1,
    max_size=40,
)

experience_entry_strategy = st.fixed_dictionaries(
    {
        "company": safe_text,
        "title": safe_text,
        "period": safe_text,
        "responsibilities": st.lists(safe_text, min_size=1, max_size=3),
        "technologies": st.lists(safe_text, min_size=1, max_size=3),
    }
)


def build_data_dict(experience_entries):
    """Wrap a list of experience entries in a complete valid data dict."""
    return {
        "personal": {
            "name": "Test User",
            "title": "Developer",
            "bio": "A bio.",
            "location": "Test City",
            "resume_pdf": "resume.pdf",
        },
        "experience": experience_entries,
        "skills": [
            {
                "category": "Languages",
                "items": ["Python"],
            }
        ],
        "education": [
            {
                "institution": "Test University",
                "degree": "B.Sc. Computer Science",
                "year": "2020",
                "result": "First Class",
            }
        ],
        "contact": {
            "email": "test@example.com",
            "phone": "+1 555 000 0000",
            "github": "https://github.com/testuser",
        },
    }


# ---------------------------------------------------------------------------
# HTML parsing helper
# ---------------------------------------------------------------------------

class CompanyNameCollector(HTMLParser):
    """Collect text content of all <h3> tags inside the #experience article."""

    def __init__(self):
        super().__init__()
        self._in_experience = False
        self._in_h3 = False
        self._depth = 0          # nesting depth inside #experience article
        self.companies = []
        self._current_text = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "article" and attrs_dict.get("id") == "experience":
            self._in_experience = True
            self._depth = 0
        elif self._in_experience:
            self._depth += 1
            if tag == "h3":
                self._in_h3 = True
                self._current_text = []

    def handle_endtag(self, tag):
        if self._in_experience:
            if tag == "h3" and self._in_h3:
                self.companies.append("".join(self._current_text).strip())
                self._in_h3 = False
                self._current_text = []
            if tag == "article":
                self._in_experience = False

    def handle_data(self, data):
        if self._in_h3:
            self._current_text.append(data)


def extract_company_names(html: str) -> list:
    """Return company names in the order they appear in the #experience section."""
    parser = CompanyNameCollector()
    parser.feed(html)
    return parser.companies


# ---------------------------------------------------------------------------
# Helper: run generator in a temp workspace
# ---------------------------------------------------------------------------

def run_generator_raw(data: dict) -> subprocess.CompletedProcess:
    """Write data.yml to a fresh temp dir, run generate.py, return the raw result.

    Unlike run_generator_in_workspace, this does NOT assert returncode == 0.
    Use this when testing error conditions (e.g. missing required fields).
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # Copy template.html into the temp workspace
        shutil.copy(WORKSPACE_ROOT / "template.html", tmp_path / "template.html")

        # Write the data dict as YAML
        data_yml_path = tmp_path / "data.yml"
        data_yml_path.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")

        # Run the generator and return the full CompletedProcess result
        return subprocess.run(
            [sys.executable, str(WORKSPACE_ROOT / "generate.py")],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
        )


def run_generator_in_workspace(data: dict) -> str:
    """Write data.yml to a fresh temp dir, run generate.py, return rendered HTML.

    Creates and cleans up its own temporary directory so it is safe to call
    multiple times within a single Hypothesis test run (avoids the
    function-scoped fixture reuse issue).
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # Copy template.html into the temp workspace
        shutil.copy(WORKSPACE_ROOT / "template.html", tmp_path / "template.html")

        # Write the data dict as YAML
        data_yml_path = tmp_path / "data.yml"
        data_yml_path.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")

        # Run the generator
        result = subprocess.run(
            [sys.executable, str(WORKSPACE_ROOT / "generate.py")],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"Generator failed.\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )

        return (tmp_path / "index.html").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Property 1: Reverse-Chronological Ordering
# Validates: Requirements 3.1, 5.1
# ---------------------------------------------------------------------------

@given(
    entries=st.lists(experience_entry_strategy, min_size=1, max_size=8)
)
@settings(max_examples=100, deadline=None)
def test_ordering_preserved(entries):
    """Property 1: Reverse-Chronological Ordering.

    For any list of experience entries, the rendered HTML presents those
    entries in the same order they appear in the input list.

    Validates: Requirements 3.1, 5.1
    """
    data = build_data_dict(entries)
    html = run_generator_in_workspace(data)

    rendered_companies = extract_company_names(html)
    expected_companies = [entry["company"] for entry in entries]

    assert rendered_companies == expected_companies, (
        f"Ordering mismatch.\n"
        f"Expected: {expected_companies}\n"
        f"Got:      {rendered_companies}"
    )


# ---------------------------------------------------------------------------
# Property 2: Experience Entry Completeness
# Validates: Requirements 3.2, 3.4
# ---------------------------------------------------------------------------

@given(
    entry=experience_entry_strategy
)
@settings(max_examples=100, deadline=None)
def test_experience_entry_completeness(entry):
    """Property 2: Experience Entry Completeness.

    For any experience entry containing company, title, period,
    responsibilities, and technologies fields, the rendered HTML SHALL
    include all five fields for that entry.

    # Feature: personal-portfolio-website, Property 2: Experience Entry Completeness
    Validates: Requirements 3.2, 3.4
    """
    data = build_data_dict([entry])
    html = run_generator_in_workspace(data)

    # Assert all five field values appear in the rendered HTML
    assert entry["company"] in html, (
        f"company '{entry['company']}' not found in rendered HTML"
    )
    assert entry["title"] in html, (
        f"title '{entry['title']}' not found in rendered HTML"
    )
    assert entry["period"] in html, (
        f"period '{entry['period']}' not found in rendered HTML"
    )
    for responsibility in entry["responsibilities"]:
        assert responsibility in html, (
            f"responsibility '{responsibility}' not found in rendered HTML"
        )
    for tech in entry["technologies"]:
        assert tech in html, (
            f"technology '{tech}' not found in rendered HTML"
        )


# ---------------------------------------------------------------------------
# Property 3: Education Entry Completeness
# Validates: Requirements 5.2
# ---------------------------------------------------------------------------

education_entry_strategy = st.fixed_dictionaries(
    {
        "institution": safe_text,
        "degree": safe_text,
        "year": safe_text,
        "result": safe_text,
    }
)


def build_data_dict_with_education(education_entries):
    """Wrap a list of education entries in a complete valid data dict."""
    return {
        "personal": {
            "name": "Test User",
            "title": "Developer",
            "bio": "A bio.",
            "location": "Test City",
            "resume_pdf": "resume.pdf",
        },
        "experience": [
            {
                "company": "Test Corp",
                "title": "Engineer",
                "period": "2020-2021",
                "responsibilities": ["Did things"],
                "technologies": ["Python"],
            }
        ],
        "skills": [
            {
                "category": "Languages",
                "items": ["Python"],
            }
        ],
        "education": education_entries,
        "contact": {
            "email": "test@example.com",
            "phone": "+1 555 000 0000",
            "github": "https://github.com/testuser",
        },
    }


@given(entry=education_entry_strategy)
@settings(max_examples=100, deadline=None)
def test_education_entry_completeness(entry):
    """Property 3: Education Entry Completeness.

    For any education entry containing institution, degree, year, and result
    fields, the rendered HTML SHALL include all four fields for that entry.

    # Feature: personal-portfolio-website, Property 3: Education Entry Completeness
    Validates: Requirements 5.2
    """
    data = build_data_dict_with_education([entry])
    html = run_generator_in_workspace(data)

    assert entry["institution"] in html, (
        f"institution '{entry['institution']}' not found in rendered HTML"
    )
    assert entry["degree"] in html, (
        f"degree '{entry['degree']}' not found in rendered HTML"
    )
    assert entry["year"] in html, (
        f"year '{entry['year']}' not found in rendered HTML"
    )
    assert entry["result"] in html, (
        f"result '{entry['result']}' not found in rendered HTML"
    )


# ---------------------------------------------------------------------------
# Property 4: Valid Data Produces Valid HTML
# Feature: personal-portfolio-website, Property 4: Valid Data Produces Valid HTML
# Validates: Requirements 7.2
# ---------------------------------------------------------------------------

class SectionArticleCollector(HTMLParser):
    """Collect the id attributes of all <article> elements."""

    def __init__(self):
        super().__init__()
        self.article_ids = []

    def handle_starttag(self, tag, attrs):
        if tag == "article":
            attrs_dict = dict(attrs)
            article_id = attrs_dict.get("id")
            if article_id:
                self.article_ids.append(article_id)


valid_data_strategy = st.fixed_dictionaries(
    {
        "personal": st.fixed_dictionaries(
            {
                "name": safe_text,
                "title": safe_text,
                "bio": safe_text,
                "location": safe_text,
                "resume_pdf": safe_text,
            }
        ),
        "experience": st.lists(
            st.fixed_dictionaries(
                {
                    "company": safe_text,
                    "title": safe_text,
                    "period": safe_text,
                    "responsibilities": st.lists(safe_text, min_size=1, max_size=3),
                    "technologies": st.lists(safe_text, min_size=1, max_size=3),
                }
            ),
            min_size=1,
            max_size=3,
        ),
        "skills": st.lists(
            st.fixed_dictionaries(
                {
                    "category": safe_text,
                    "items": st.lists(safe_text, min_size=1, max_size=3),
                }
            ),
            min_size=1,
            max_size=3,
        ),
        "education": st.lists(
            st.fixed_dictionaries(
                {
                    "institution": safe_text,
                    "degree": safe_text,
                    "year": safe_text,
                    "result": safe_text,
                }
            ),
            min_size=1,
            max_size=3,
        ),
        "contact": st.fixed_dictionaries(
            {
                "email": safe_text,
                "phone": safe_text,
                "github": safe_text,
            }
        ),
    }
)


@given(data=valid_data_strategy)
@settings(max_examples=100, deadline=None)
def test_valid_data_produces_valid_html(data):
    """Property 4: Valid Data Produces Valid HTML.

    For any data.yml that satisfies the required field schema, the generator
    SHALL produce an index.html that is well-formed HTML containing the five
    expected section articles (#about, #experience, #skills, #education,
    #contact).

    # Feature: personal-portfolio-website, Property 4: Valid Data Produces Valid HTML
    Validates: Requirements 7.2
    """
    html = run_generator_in_workspace(data)

    # Parse the output with html.parser and collect article ids
    collector = SectionArticleCollector()
    collector.feed(html)

    expected_sections = {"about", "experience", "skills", "education", "contact"}
    found_sections = set(collector.article_ids)

    missing = expected_sections - found_sections
    assert not missing, (
        f"Missing section article(s) in rendered HTML: {missing}\n"
        f"Found article ids: {found_sections}"
    )


# ---------------------------------------------------------------------------
# Property 5: Missing Required Field Causes Descriptive Error
# Feature: personal-portfolio-website, Property 5: Missing Required Field Causes Descriptive Error
# Validates: Requirements 7.3
# ---------------------------------------------------------------------------

REQUIRED_TOP_LEVEL_FIELDS = ['personal', 'experience', 'skills', 'education', 'contact']


@given(field=st.sampled_from(REQUIRED_TOP_LEVEL_FIELDS))
@settings(max_examples=100, deadline=None)
def test_missing_required_field_causes_descriptive_error(field):
    """Property 5: Missing Required Field Causes Descriptive Error.

    For any data.yml that is missing any single required top-level key
    (personal, experience, skills, education, contact), the generator SHALL
    exit with a non-zero status code and print an error message that names
    the missing field.

    # Feature: personal-portfolio-website, Property 5: Missing Required Field Causes Descriptive Error
    Validates: Requirements 7.3
    """
    # Start with a complete valid data dict
    data = {
        "personal": {
            "name": "Test User",
            "title": "Developer",
            "bio": "A bio.",
            "location": "Test City",
            "resume_pdf": "resume.pdf",
        },
        "experience": [
            {
                "company": "Test Corp",
                "title": "Engineer",
                "period": "2020-2021",
                "responsibilities": ["Did things"],
                "technologies": ["Python"],
            }
        ],
        "skills": [
            {
                "category": "Languages",
                "items": ["Python"],
            }
        ],
        "education": [
            {
                "institution": "Test University",
                "degree": "B.Sc. Computer Science",
                "year": "2020",
                "result": "First Class",
            }
        ],
        "contact": {
            "email": "test@example.com",
            "phone": "+1 555 000 0000",
            "github": "https://github.com/testuser",
        },
    }

    # Remove the sampled required field
    del data[field]

    # Run the generator without asserting success
    result = run_generator_raw(data)

    # Assert exit code is non-zero (specifically 1)
    assert result.returncode == 1, (
        f"Expected exit code 1 when '{field}' is missing, "
        f"got {result.returncode}.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )

    # Assert the missing field name appears in stdout or stderr
    combined_output = result.stdout + result.stderr
    assert field in combined_output, (
        f"Expected field name '{field}' to appear in generator output, "
        f"but it was not found.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


# ---------------------------------------------------------------------------
# Property 6: Generator Idempotence
# Feature: personal-portfolio-website, Property 6: Generator Idempotence
# Validates: Requirements 7.7
# ---------------------------------------------------------------------------


@given(data=valid_data_strategy)
@settings(max_examples=100, deadline=None)
def test_generator_idempotence(data):
    """Property 6: Generator Idempotence.

    For any valid data.yml, running generate.py twice in succession on the
    same data file SHALL produce byte-identical index.html output on both runs.

    # Feature: personal-portfolio-website, Property 6: Generator Idempotence
    Validates: Requirements 7.7
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # Copy template.html into the temp workspace
        shutil.copy(WORKSPACE_ROOT / "template.html", tmp_path / "template.html")

        # Write data.yml once
        data_yml_path = tmp_path / "data.yml"
        data_yml_path.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")

        generator_cmd = [sys.executable, str(WORKSPACE_ROOT / "generate.py")]

        # First run
        result1 = subprocess.run(
            generator_cmd,
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
        )
        assert result1.returncode == 0, (
            f"First generator run failed.\nstdout: {result1.stdout}\nstderr: {result1.stderr}"
        )
        output1 = (tmp_path / "index.html").read_text(encoding="utf-8")

        # Second run (same data.yml, same directory)
        result2 = subprocess.run(
            generator_cmd,
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
        )
        assert result2.returncode == 0, (
            f"Second generator run failed.\nstdout: {result2.stdout}\nstderr: {result2.stderr}"
        )
        output2 = (tmp_path / "index.html").read_text(encoding="utf-8")

        # Assert byte-identical output
        assert output1 == output2, (
            "Generator is not idempotent: two runs on the same data.yml produced "
            "different index.html content."
        )


# ---------------------------------------------------------------------------
# Property 7: All Asset Paths Are Relative
# Feature: personal-portfolio-website, Property 7: All Asset Paths Are Relative
# Validates: Requirements 8.3, 8.4
# ---------------------------------------------------------------------------

EXTERNAL_DOMAINS = ("github.com", "html5up.net")


class AssetPathCollector(HTMLParser):
    """Collect all src and href attribute values from an HTML document."""

    def __init__(self):
        super().__init__()
        self.src_values: list = []
        self.href_values: list = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        src = attrs_dict.get("src")
        if src is not None:
            self.src_values.append(src)
        href = attrs_dict.get("href")
        if href is not None:
            self.href_values.append(href)


def _is_external_href(value: str) -> bool:
    """Return True if the href value is an external link that is allowed to be absolute."""
    # mailto: links are not local asset references
    if value.startswith("mailto:"):
        return True
    # Links to known external domains (github.com, html5up.net) are expected to be absolute
    for domain in EXTERNAL_DOMAINS:
        if domain in value:
            return True
    # Hash-only links (#about, #experience, etc.) are internal anchors, not assets
    if value.startswith("#"):
        return True
    return False


@given(data=valid_data_strategy)
@settings(max_examples=100, deadline=None)
def test_asset_paths_are_relative(data):
    """Property 7: All Asset Paths Are Relative.

    For any generated index.html, every src and href attribute referencing a
    local asset (CSS, JS, image, font) SHALL use a relative path — no absolute
    URLs (http://, https://, or paths starting with /) for local assets.

    External links (github.com, html5up.net) and mailto: links are allowed to
    be absolute; all other src and href values must be relative.

    # Feature: personal-portfolio-website, Property 7: All Asset Paths Are Relative
    Validates: Requirements 8.3, 8.4
    """
    html = run_generator_in_workspace(data)

    collector = AssetPathCollector()
    collector.feed(html)

    # All src attributes are local asset references (CSS, JS, images) — must be relative
    for src in collector.src_values:
        assert not src.startswith("http://"), (
            f"src attribute uses absolute http:// URL: {src!r}"
        )
        assert not src.startswith("https://"), (
            f"src attribute uses absolute https:// URL: {src!r}"
        )
        assert not src.startswith("/"), (
            f"src attribute uses absolute path starting with /: {src!r}"
        )

    # href attributes: filter out external links and mailto:, then assert remaining are relative
    for href in collector.href_values:
        if _is_external_href(href):
            continue
        assert not href.startswith("http://"), (
            f"Local asset href uses absolute http:// URL: {href!r}"
        )
        assert not href.startswith("https://"), (
            f"Local asset href uses absolute https:// URL: {href!r}"
        )
        assert not href.startswith("/"), (
            f"Local asset href uses absolute path starting with /: {href!r}"
        )


# ---------------------------------------------------------------------------
# Property 8: All Images Have Non-Empty Alt Attributes
# Feature: personal-portfolio-website, Property 8: All Images Have Non-Empty Alt Attributes
# Validates: Requirements 9.1
# ---------------------------------------------------------------------------


class ImgTagCollector(HTMLParser):
    """Collect all <img> tag attribute dicts from an HTML document."""

    def __init__(self):
        super().__init__()
        self.img_attrs: list = []

    def handle_starttag(self, tag, attrs):
        if tag == "img":
            self.img_attrs.append(dict(attrs))


@given(data=valid_data_strategy)
@settings(max_examples=100, deadline=None)
def test_all_images_have_non_empty_alt(data):
    """Property 8: All Images Have Non-Empty Alt Attributes.

    For any generated index.html, every <img> element SHALL have a non-empty
    alt attribute (not None, not empty string "").

    # Feature: personal-portfolio-website, Property 8: All Images Have Non-Empty Alt Attributes
    Validates: Requirements 9.1
    """
    html = run_generator_in_workspace(data)

    collector = ImgTagCollector()
    collector.feed(html)

    for attrs in collector.img_attrs:
        alt = attrs.get("alt")
        assert alt is not None, (
            f"<img> element is missing an alt attribute entirely. "
            f"img attrs: {attrs}"
        )
        assert alt != "", (
            f"<img> element has an empty alt attribute. "
            f"img attrs: {attrs}"
        )
