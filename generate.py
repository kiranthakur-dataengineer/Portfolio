import sys
import yaml
import jinja2

REQUIRED_FIELDS = ['personal', 'experience', 'skills', 'education', 'contact']

REQUIRED_PERSONAL_FIELDS = ['name', 'title', 'bio', 'location', 'resume_pdf']

REQUIRED_CONTACT_FIELDS = ['email', 'phone', 'github']


def load_data(path):
    """Load and parse a YAML data file.

    Args:
        path: Path to the YAML file to load.

    Returns:
        Parsed data as a Python dict.

    Exits with code 1 if the file is not found or contains invalid YAML.
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print('Error: data.yml not found.')
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f'Error: data.yml is not valid YAML: {e}')
        sys.exit(1)


def validate_data(data):
    """Validate that all required fields are present in the data dict.

    Checks top-level required keys as well as nested required keys under
    'personal' and 'contact'.

    Args:
        data: Parsed data dict from load_data.

    Exits with code 1 if any required field is missing.
    """
    # Check top-level required fields
    for field in REQUIRED_FIELDS:
        if field not in data:
            print(f"Error: Missing required field in data.yml: '{field}'")
            sys.exit(1)

    # Check nested required fields under 'personal'
    for field in REQUIRED_PERSONAL_FIELDS:
        if field not in data['personal']:
            print(f"Error: Missing required field in data.yml: '{field}'")
            sys.exit(1)

    # Check nested required fields under 'contact'
    for field in REQUIRED_CONTACT_FIELDS:
        if field not in data['contact']:
            print(f"Error: Missing required field in data.yml: '{field}'")
            sys.exit(1)


def render_template(data):
    """Render the Jinja2 template with the provided data context.

    Args:
        data: Validated data dict from load_data/validate_data.

    Returns:
        Rendered HTML string.

    Exits with code 1 if template.html is not found or rendering fails.
    """
    env = jinja2.Environment(loader=jinja2.FileSystemLoader('.'))
    try:
        template = env.get_template('template.html')
    except jinja2.TemplateNotFound:
        print('Error: template.html not found.')
        sys.exit(1)

    try:
        return template.render(
            personal=data['personal'],
            experience=data['experience'],
            skills=data['skills'],
            education=data['education'],
            contact=data['contact'],
        )
    except jinja2.TemplateError as e:
        print(f'Error: Template rendering failed: {e}')
        sys.exit(1)


def main():
    """Main entry point: load data, validate, render, and write index.html."""
    data = load_data('data.yml')
    validate_data(data)
    html = render_template(data)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('Generated index.html successfully.')
    sys.exit(0)


if __name__ == '__main__':
    main()
