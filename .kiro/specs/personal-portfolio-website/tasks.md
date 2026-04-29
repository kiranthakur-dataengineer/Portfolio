# Implementation Plan: Personal Portfolio Website — Kiran Thakur

## Overview

Implement a Python static site generator that reads `data.yml` and renders `index.html` using a Jinja2 template derived from the HTML5 UP "Dimension" layout. All CSS, JS, image, and font assets are already present in the workspace; only the generator, template, data file, and tests need to be created.

## Tasks

- [x] 1. Create project dependencies and data file
  - [x] 1.1 Create `requirements.txt` listing pinned dependencies
    - Include `Jinja2==3.1.4`, `PyYAML==6.0.2`, `hypothesis==6.131.15`, `pytest==8.3.5`
    - _Requirements: 7.4_

  - [x] 1.2 Create `data.yml` with all portfolio content
    - Populate `personal` key: name, title, bio, location, resume_pdf path
    - Populate `experience` list in reverse-chronological order: Infinite Computer Solutions (Feb 2025–Present), Extrapreneurs India (Aug 2022–Oct 2024), I2E Consulting (Apr 2021–May 2022), KayaDev AI Pvt. Ltd (Mar 2019–Jul 2020) — each with company, title, period, responsibilities, technologies
    - Populate `skills` list with categories: Languages, Cloud, Frameworks, Databases, Tools, Operating Systems, Domains — each with items as specified in requirements
    - Populate `education` list in reverse-chronological order: BITS Pilani (Pursuing, CGPA 6), CDAC Chennai (2018–19, 70%), Pune University (2016, 60.40%), MSBTE (2012, 68.06%) — each with institution, degree, year, result
    - Populate `contact` key: email, phone, github
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 4.1, 4.2, 5.1, 5.2, 5.3, 6.1, 6.2, 6.3, 7.1, 7.6_

- [x] 2. Create the Jinja2 HTML template
  - [x] 2.1 Create `template.html` derived from the Dimension layout
    - Write `<head>` with relative CSS links (`assets/css/main.css`, `assets/css/fontawesome-all.min.css`, `assets/css/noscript.css`), `<title>` using `{{ personal.name }}`, and viewport meta tag
    - Write `#header` hero section rendering `{{ personal.name }}` as `<h1>`, `{{ personal.title }}` as subtitle, and `<nav>` with links to `#about`, `#experience`, `#skills`, `#education`, `#contact`
    - Write `#about` article with bio, location, and resume download link using `{{ personal.bio }}`, `{{ personal.location }}`, `{{ personal.resume_pdf }}`
    - Write `#experience` article with a `{% for %}` loop over `experience` entries rendering company, title, period, responsibilities list, and technologies list
    - Write `#skills` article with a `{% for %}` loop over `skills` entries rendering category heading and items list
    - Write `#education` article with a `{% for %}` loop over `education` entries rendering institution, degree, year, result
    - Write `#contact` article with `mailto:` link for `{{ contact.email }}`, phone display for `{{ contact.phone }}`, and GitHub link with `target="_blank"` for `{{ contact.github }}`
    - Write `#footer` with HTML5 UP attribution credit
    - Write closing `<script>` tags with relative JS paths (`assets/js/jquery.min.js`, `assets/js/breakpoints.min.js`, `assets/js/browser.min.js`, `assets/js/util.js`, `assets/js/main.js`)
    - Use semantic HTML5 elements: `<header>`, `<main>`, `<section>`, `<nav>`, `<footer>`
    - Include descriptive `alt` attributes on all `<img>` elements (background image, overlay)
    - Include `<noscript>` block linking `assets/css/noscript.css`
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 3.1, 3.2, 4.1, 4.2, 4.3, 5.1, 5.2, 6.1, 6.2, 6.3, 8.3, 9.1, 9.2, 10.1_

- [x] 3. Implement the static site generator
  - [x] 3.1 Create `generate.py` with data loading and validation
    - Import `sys`, `yaml`, `jinja2`; define `REQUIRED_FIELDS` list: `['personal', 'experience', 'skills', 'education', 'contact']` and nested required fields under `personal` and `contact`
    - Implement `load_data(path)` function: open and parse `data.yml` with `yaml.safe_load`; handle `FileNotFoundError` (print `Error: data.yml not found.`, exit 1) and `yaml.YAMLError` (print `Error: data.yml is not valid YAML: <error>`, exit 1)
    - Implement `validate_data(data)` function: check all required top-level and nested keys; for any missing key print `Error: Missing required field in data.yml: '<field>'` and exit 1
    - _Requirements: 7.1, 7.3, 7.6_

  - [x] 3.2 Add template rendering and output writing to `generate.py`
    - Implement `render_template(data)` function: create `jinja2.Environment` with `FileSystemLoader('.')`, load `template.html` (handle `TemplateNotFound`: print `Error: template.html not found.`, exit 1), render with data context (handle `jinja2.TemplateError`: print `Error: Template rendering failed: <error>`, exit 1)
    - Implement `main()` function: call `load_data`, `validate_data`, `render_template`; write result to `index.html` with UTF-8 encoding; print `Generated index.html successfully.`; exit 0
    - Add `if __name__ == '__main__': main()` guard
    - _Requirements: 7.2, 7.4, 7.5_

- [ ] 4. Checkpoint — run the generator manually to verify output
  - Execute `python generate.py` and confirm `index.html` is produced without errors.
  - Open `index.html` in a browser and verify the hero section, all five nav links, and modal panels render correctly using the Dimension layout.
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Set up the test suite
  - [x] 5.1 Create `tests/conftest.py` with shared fixtures
    - Define `minimal_data()` fixture returning a Python dict with all required fields populated with minimal valid values (one experience entry, one skill category, one education entry)
    - Define `tmp_workspace(tmp_path)` fixture that copies `template.html` into a temp directory and returns the path, so generator tests can run in isolation
    - _Requirements: 7.1, 7.2_

  - [x] 5.2 Create `tests/fixtures/valid_data.yml` as a minimal valid YAML file
    - Include all required top-level keys with at least one entry each
    - _Requirements: 7.1_

  - [x] 5.3 Create `tests/test_generator.py` with unit/example tests
    - Smoke test: run generator against actual `data.yml`; assert `index.html` is created and contains "Kiran Thakur"
    - Assert rendered HTML contains all five nav links (`#about`, `#experience`, `#skills`, `#education`, `#contact`)
    - Assert rendered HTML contains all four employer names
    - Assert rendered HTML contains all four education institution names
    - Assert rendered HTML contains `mailto:kiranthakur1001@gmail.com`
    - Assert rendered HTML contains GitHub link with `target="_blank"`
    - Assert rendered HTML contains semantic elements: `<header>`, `<main>`, `<section>`, `<nav>`, `<footer>`
    - Assert rendered HTML contains HTML5 UP attribution credit
    - Assert generator completes within 5 seconds (use `time.time()` around the call)
    - Assert generator exits with code 1 and prints field name when a required field is missing
    - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 3.3, 5.3, 6.1, 6.3, 7.2, 7.3, 7.5, 9.2, 10.1_

- [x] 6. Add property-based tests using Hypothesis
  - [x] 6.1 Write property test for ordering preservation (Property 1)
    - Use `@given` with `st.lists` of experience/education entry dicts in a known order; run generator; parse output; assert entries appear in the same order as the input list
    - **Property 1: Reverse-Chronological Ordering**
    - **Validates: Requirements 3.1, 5.1**

  - [x] 6.2 Write property test for experience entry completeness (Property 2)
    - Use `@given` with `st.fixed_dictionaries` generating random experience entries with all five required fields; run generator; assert all five fields appear in rendered HTML
    - **Property 2: Experience Entry Completeness**
    - **Validates: Requirements 3.2, 3.4**

  - [x] 6.3 Write property test for education entry completeness (Property 3)
    - Use `@given` with `st.fixed_dictionaries` generating random education entries with all four required fields; run generator; assert all four fields appear in rendered HTML
    - **Property 3: Education Entry Completeness**
    - **Validates: Requirements 5.2**

  - [x] 6.4 Write property test for valid data producing valid HTML (Property 4)
    - Use `@given` with a strategy that builds a complete valid data dict with random string values; run generator; parse output with `html.parser`; assert five section articles (`#about`, `#experience`, `#skills`, `#education`, `#contact`) are present
    - **Property 4: Valid Data Produces Valid HTML**
    - **Validates: Requirements 7.2**

  - [x] 6.5 Write property test for missing required field causing descriptive error (Property 5)
    - Use `@given` with `st.sampled_from` over the list of required field names; remove that field from a valid data dict; run generator; assert exit code 1 and field name appears in stderr
    - **Property 5: Missing Required Field Causes Descriptive Error**
    - **Validates: Requirements 7.3**

  - [x] 6.6 Write property test for generator idempotence (Property 6)
    - Use `@given` with a valid data dict strategy; run generator twice on the same data; read both `index.html` outputs; assert byte-identical content
    - **Property 6: Generator Idempotence**
    - **Validates: Requirements 7.7**

  - [x] 6.7 Write property test for relative asset paths (Property 7)
    - Use `@given` with a valid data dict strategy; render; parse all `src` and `href` attributes with `html.parser`; assert none of the local asset references start with `http://`, `https://`, or `/`
    - **Property 7: All Asset Paths Are Relative**
    - **Validates: Requirements 8.3, 8.4**

  - [x] 6.8 Write property test for non-empty alt attributes (Property 8)
    - Use `@given` with a valid data dict strategy; render; parse all `<img>` tags; assert every `<img>` has a non-empty `alt` attribute
    - **Property 8: All Images Have Non-Empty Alt Attributes**
    - **Validates: Requirements 9.1**

- [ ] 7. Final checkpoint — run the full test suite
  - Run `pytest tests/ -v` and confirm all non-optional tests pass.
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP
- Each task references specific requirements for traceability
- Property tests use Hypothesis with default `max_examples=100`; tag each test with `# Feature: personal-portfolio-website, Property N: <property_text>`
- The generator is a pure function (data → HTML), making it well-suited for property-based testing
- WCAG 2.1 AA colour contrast and keyboard navigation (Requirements 9.3, 9.4) require manual verification with browser tools (axe DevTools, Lighthouse) and are not automated in this test suite
- All asset paths in `template.html` must be relative (no leading `/`) to satisfy GitHub Pages sub-path hosting
