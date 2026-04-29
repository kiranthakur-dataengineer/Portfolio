import shutil
from pathlib import Path

import pytest


@pytest.fixture
def minimal_data():
    """Return a dict with all required fields populated with minimal valid values."""
    return {
        "personal": {
            "name": "Test User",
            "title": "Software Developer",
            "bio": "A short bio.",
            "location": "Test City",
            "resume_pdf": "resume.pdf",
        },
        "experience": [
            {
                "company": "Test Corp",
                "title": "Developer",
                "period": "2020 – Present",
                "responsibilities": ["Built things"],
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


@pytest.fixture
def tmp_workspace(tmp_path):
    """Copy template.html into a temp directory and return the temp path."""
    workspace_root = Path(__file__).parent.parent
    shutil.copy(workspace_root / "template.html", tmp_path / "template.html")
    return tmp_path
