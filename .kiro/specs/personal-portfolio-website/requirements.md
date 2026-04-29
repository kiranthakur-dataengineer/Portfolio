# Requirements Document

## Introduction

A personal portfolio website for Kiran Thakur — Senior Software Developer and Data Scientist with 6 years of experience. The site will be built on top of the existing HTML5 UP "Dimension" template (one-page, modal-based layout) and hosted on GitHub Pages. A Python-based static site generator script will render the final `index.html` from a structured data file, so that content updates (resume changes, new projects) require only data edits rather than HTML edits. The site showcases Kiran's professional profile, work experience, technical skills, education, and contact information.

## Glossary

- **Portfolio_Site**: The complete personal portfolio website delivered as static files hosted on GitHub Pages.
- **Generator**: The Python script (`generate.py`) that reads structured resume data and renders the final `index.html` using a Jinja2 template.
- **Template**: The Jinja2 HTML template (`template.html`) derived from the HTML5 UP "Dimension" base that defines the visual structure of the Portfolio_Site.
- **Data_File**: The YAML or JSON file (`data.yml` or `data.json`) containing all resume content — personal info, experience, skills, education, and projects.
- **Section**: A modal panel within the one-page layout representing a distinct content area (About, Experience, Skills, Education, Contact).
- **Visitor**: Any person who opens the Portfolio_Site in a web browser.
- **GitHub_Pages**: The static hosting service at `https://<username>.github.io/<repo>` used to serve the Portfolio_Site.

---

## Requirements

### Requirement 1: Hero / Landing Section

**User Story:** As a Visitor, I want to see Kiran's name, title, and navigation links immediately on landing, so that I can quickly understand who this person is and navigate to the section I care about.

#### Acceptance Criteria

1. THE Portfolio_Site SHALL display Kiran Thakur's full name as the primary heading on the landing view.
2. THE Portfolio_Site SHALL display the professional title "Senior Software Developer | Data Scientist" beneath the name.
3. THE Portfolio_Site SHALL render navigation links for About, Experience, Skills, Education, and Contact sections on the landing view.
4. WHEN a Visitor clicks a navigation link, THE Portfolio_Site SHALL open the corresponding Section modal without a full page reload.
5. WHEN a Visitor resizes the browser window to a viewport width below 736px, THE Portfolio_Site SHALL reflow the navigation links into a vertically stacked layout.

---

### Requirement 2: About Section

**User Story:** As a Visitor, I want to read a professional summary about Kiran, so that I can quickly assess background and suitability.

#### Acceptance Criteria

1. THE Portfolio_Site SHALL display a professional bio summarising Kiran's 6 years of experience in Data Science and web development.
2. THE Portfolio_Site SHALL display location (Pune, Maharashtra, India) within the About Section.
3. THE Portfolio_Site SHALL provide a downloadable link to Kiran's resume PDF within the About Section.
4. WHEN a Visitor clicks the resume download link, THE Portfolio_Site SHALL initiate a file download of the resume PDF.

---

### Requirement 3: Work Experience Section

**User Story:** As a Visitor, I want to browse Kiran's work history in reverse-chronological order, so that I can evaluate career progression and relevant project experience.

#### Acceptance Criteria

1. THE Portfolio_Site SHALL display work experience entries in reverse-chronological order (most recent first).
2. THE Portfolio_Site SHALL display, for each experience entry: company name, job title, employment period, and a list of key responsibilities and technologies used.
3. THE Portfolio_Site SHALL include the following employers in the Experience Section:
   - Infinite Computer Solutions (Feb 2025 – Present)
   - Extrapreneurs India (Aug 2022 – Oct 2024)
   - I2E Consulting (Apr 2021 – May 2022)
   - KayaDev AI Pvt. Ltd (Mar 2019 – Jul 2020)
4. THE Portfolio_Site SHALL display the technology stack (e.g., AWS Lambda, Django, Flask, OpenCV) for each experience entry.

---

### Requirement 4: Technical Skills Section

**User Story:** As a Visitor, I want to see Kiran's technical skills organised by category, so that I can quickly identify relevant expertise.

#### Acceptance Criteria

1. THE Portfolio_Site SHALL display technical skills grouped into the following categories: Languages, Cloud, Frameworks, Databases, Tools, Operating Systems, and Domains.
2. THE Portfolio_Site SHALL list the following skills per category:
   - Languages: Python
   - Cloud: AWS (S3, DynamoDB, Lambda, CloudWatch)
   - Frameworks: Flask, Django, FastAPI
   - Databases: SQL, PL-SQL, MSSQL, PostgreSQL, MySQL 8.0, MongoDB 4.x
   - Tools: JIRA, Git, MS-Office, Postman
   - Operating Systems: Windows, Ubuntu
   - Domains: Stock Market, Healthcare, Management, Banking
3. THE Portfolio_Site SHALL visually distinguish skill categories from individual skill items.

---

### Requirement 5: Education Section

**User Story:** As a Visitor, I want to see Kiran's educational background, so that I can verify academic qualifications.

#### Acceptance Criteria

1. THE Portfolio_Site SHALL display education entries in reverse-chronological order.
2. THE Portfolio_Site SHALL display, for each education entry: institution name, degree/diploma title, year(s), and result (CGPA or percentage where available).
3. THE Portfolio_Site SHALL include the following education entries:
   - Masters in Data Science and Engineering — BITS Pilani (Pursuing, CGPA: 6)
   - PG Diploma in Big Data Analytics — CDAC Chennai (2018–19, 70%)
   - B.E. Computer Engineering — Pune University (2016, 60.40%)
   - Diploma in Computer Technology — MSBTE (2012, 68.06%)

---

### Requirement 6: Contact Section

**User Story:** As a Visitor, I want to find Kiran's contact details and social/professional links, so that I can reach out directly.

#### Acceptance Criteria

1. THE Portfolio_Site SHALL display Kiran's email address (kiranthakur1001@gmail.com) as a clickable `mailto:` link.
2. THE Portfolio_Site SHALL display Kiran's phone number (+91 8888012961) in the Contact Section.
3. THE Portfolio_Site SHALL include a link to Kiran's GitHub profile in the Contact Section.
4. WHEN a Visitor clicks the email link, THE Portfolio_Site SHALL open the Visitor's default email client pre-addressed to kiranthakur1001@gmail.com.
5. WHEN a Visitor clicks the GitHub link, THE Portfolio_Site SHALL open the GitHub profile in a new browser tab.

---

### Requirement 7: Python Static Site Generator

**User Story:** As Kiran, I want to maintain my portfolio content in a single structured data file and regenerate the site with a Python script, so that updating the portfolio does not require editing raw HTML.

#### Acceptance Criteria

1. THE Generator SHALL read all portfolio content from a single Data_File (YAML or JSON format).
2. WHEN the Data_File contains valid content, THE Generator SHALL produce a complete, valid `index.html` file by rendering the Template.
3. WHEN the Data_File is missing a required field, THE Generator SHALL print a descriptive error message identifying the missing field and exit with a non-zero status code.
4. THE Generator SHALL require no external runtime dependencies beyond Python 3.x standard library and Jinja2.
5. WHEN the Generator is executed, THE Generator SHALL complete rendering and write `index.html` within 5 seconds on a standard development machine.
6. THE Data_File SHALL support the following top-level keys: `personal`, `experience`, `skills`, `education`, `contact`.
7. FOR ALL valid Data_Files, running the Generator twice on the same Data_File SHALL produce byte-identical `index.html` output (idempotence property).

---

### Requirement 8: GitHub Pages Compatibility

**User Story:** As Kiran, I want the portfolio to be deployable to GitHub Pages without a build server, so that hosting is free and maintenance-free.

#### Acceptance Criteria

1. THE Portfolio_Site SHALL consist exclusively of static files: `index.html`, CSS, JavaScript, images, and fonts — with no server-side runtime required.
2. THE Portfolio_Site SHALL load correctly when served from a GitHub Pages URL of the form `https://<username>.github.io/<repo>/`.
3. THE Portfolio_Site SHALL load correctly when all asset paths are relative (not absolute), so that the site functions under a sub-path on GitHub Pages.
4. WHEN a Visitor loads the Portfolio_Site over HTTPS, THE Portfolio_Site SHALL not generate mixed-content browser warnings.

---

### Requirement 9: Accessibility and Performance

**User Story:** As a Visitor, I want the portfolio to be readable and usable regardless of device or assistive technology, so that the content is accessible to everyone.

#### Acceptance Criteria

1. THE Portfolio_Site SHALL include descriptive `alt` attributes on all `<img>` elements.
2. THE Portfolio_Site SHALL use semantic HTML5 elements (`<header>`, `<main>`, `<section>`, `<nav>`, `<footer>`) to structure content.
3. THE Portfolio_Site SHALL maintain a colour contrast ratio of at least 4.5:1 between body text and its background, in accordance with WCAG 2.1 AA.
4. WHEN a Visitor navigates the Portfolio_Site using only a keyboard, THE Portfolio_Site SHALL allow focus to reach all interactive elements (navigation links, modal close buttons, contact links).
5. WHEN a Visitor loads the Portfolio_Site on a mobile device with a viewport width of 375px, THE Portfolio_Site SHALL render all content without horizontal scrolling.

---

### Requirement 10: Template Attribution

**User Story:** As a user of the HTML5 UP "Dimension" template, I want the required Creative Commons attribution to be preserved, so that the site complies with the CCA 3.0 license.

#### Acceptance Criteria

1. THE Portfolio_Site SHALL retain the HTML5 UP "Dimension" template credit in the page footer or in an HTML comment, in compliance with the Creative Commons Attribution 3.0 license.
