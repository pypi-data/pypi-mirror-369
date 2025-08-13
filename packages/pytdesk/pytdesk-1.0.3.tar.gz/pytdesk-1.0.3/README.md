# pytdesk

A lightweight, robust Python client for interacting with the TalentDesk API. Pytdesk provides a comprehensive interface to manage users, projects, tasks, expenses, invoices, and more within the TalentDesk platform.

## Features

- **Complete API Coverage**: Full access to all TalentDesk API endpoints
- **Automatic Pagination**: Handles paginated responses automatically
- **Robust Error Handling**: Comprehensive error handling with retry logic
- **Type Safety**: Built with Python 3.10+ type hints
- **Flexible Filtering**: Support for all API filters with validation
- **Session Management**: Efficient HTTP session handling with retry capabilities
- **Environment Support**: Production and development environment support

## Installation

```bash
pip install pytdesk
```

### Requirements

- Python 3.10 or higher
- requests >= 2.32.4
- urllib3 >= 2.5.0

## Quick Start

```python
from pytdesk import TalentDeskClient

# Initialize the client
client = TalentDeskClient(
    token="your_api_token_here",
    mode="production"  # or "development"
)

# Get current user information
me = client.users.me()
print(f"Logged in as: {me['data']['name']}")

# Get all projects
projects = client.projects.get_all_projects()
print(f"Found {len(projects)} projects")

# Get users with filters
users = client.users.get_all_users(
    status="active",
    role="provider",
    country="US"
)
```

## API Modules

### Users API (`client.users`)

Manage user information and profiles:

```python
# Get all users with optional filters
users = client.users.get_all_users(
    status="active",
    role="provider",
    country="US",
    min_rating=4.0
)

# Get current user
me = client.users.me()

# Get specific user by ID
user = client.users.get_user_by_id(user_id=123)

# Get user skills, notes, languages, availability
skills = client.users.get_user_skills(user_id=123)
notes = client.users.get_user_notes(user_id=123)
languages = client.users.get_user_languages(user_id=123)
availability = client.users.get_user_availability(user_id=123)
```

**Available Filters:**
- `page` - Page number for pagination
- `kw` - Keyword search
- `status` - User status (active, inactive, etc.)
- `role` - User role (provider, client, etc.)
- `employment` - Employment type
- `country` - ISO-2 country code
- `language` - ISO-2 language code
- `incorporated` - Incorporation status (0 or 1)
- `min_rating` - Minimum rating filter
- `min_rate` / `max_rate` - Rate range filters

### Projects API (`client.projects`)

Manage projects and project-related data:

```python
# Get all projects
projects = client.projects.get_all_projects(
    status="posted",
    currency="USD"
)

# Get specific project
project = client.projects.get_project_by_id(project_id=456)

# Get project worksheets
worksheets = client.projects.get_project_worksheets(
    project_id=456,
    status="submitted",
    min_date="2024-01-01"
)

# Get project expenses
expenses = client.projects.get_project_expenses(
    project_id=456,
    currency="USD"
)

# Get project tasks
tasks = client.projects.get_project_tasks(project_id=456)

# Get project team
team = client.projects.get_project_team(project_id=456)

# Create new project
new_project = client.projects.create_project(
    title="New Project",
    brief="Project description",
    owner_id=123,
    started_at="2024-01-01"
)

# Update project
updated = client.projects.update_project(
    project_id=456,
    title="Updated Title",
    brief="Updated description"
)

# Add project members
client.projects.add_project_members(
    project_id=456,
    user_ids=[123, 124, 125],
    send_invitations=True
)
```

### Tasks API (`client.tasks`)

Manage tasks within projects:

```python
# Get all tasks
tasks = client.tasks.get_all_tasks(
    status="posted",
    kw="urgent"
)

# Get specific task
task = client.tasks.get_task_by_id(task_id=789)

# Create new task
new_task = client.tasks.create_task(
    project_id=456,
    title="New Task",
    description="Task description"
)

# Update task
updated = client.tasks.update_task(
    id=789,
    title="Updated Task",
    deadline="2024-12-31"
)

# Add task assignees
client.tasks.add_task_assignees(
    task_id=789,
    assignments=[
        {"user_id": 123, "rate": 50.0},
        {"user_id": 124, "rate": 45.0}
    ]
)

# Stop task
client.tasks.stop_task(
    task_id=789,
    message="Task completed"
)
```

### Expenses API (`client.expenses`)

Manage expense approvals and workflows:

```python
# Get all expenses
expenses = client.expenses.get_all_expenses(
    status="pending",
    project_id=456,
    min_amount=100.0
)

# Get specific expense
expense = client.expenses.get_expense_by_id(expense_id=101)

# Approve expense
client.expenses.approve_expense(
    expense_id=101,
    message="Approved",
    process_at="2024-01-15"
)

# Reject expense
client.expenses.reject_expense(
    expense_id=101,
    message="Rejected - missing receipt"
)

# Cancel expense
client.expenses.cancel_expense(
    expense_id=101,
    message="Cancelled by user"
)

# Request amendment
client.expenses.request_amendment(
    expense_id=101,
    message="Please provide additional documentation"
)
```

### Invoices API (`client.invoices`)

Manage invoices and payment status:

```python
# Get all invoices
invoices = client.invoices.get_all_invoices(
    status="pending",
    currency="USD",
    min_amount=1000.0
)

# Get specific invoice
invoice = client.invoices.get_invoice_by_id(invoice_id=202)

# Mark invoice as paid
client.invoices.mark_invoice_as_paid(invoice_id=202)
```

### Organizations API (`client.organizations`)

Access organization-level information:

```python
# Get organization details
org = client.organizations.get_org()
```

### Webhooks API (`client.webhooks`)

Manage webhook subscriptions:

```python
# Create webhook
webhook = client.webhooks.create_webhook(
    url="https://your-domain.com/webhook",
    event="service-order-event"
)

# Delete webhook
client.webhooks.delete_webhook(
    url="https://your-domain.com/webhook",
    event="service-order-event"
)

# Get webhook example payload
example = client.webhooks.get_webhook_example(event="invitation-event")
```

**Available Webhook Events:**
- `service-order-event`
- `invitation-event`
- `user-event`

## Configuration

### Client Initialization

```python
client = TalentDeskClient(
    token="your_api_token",
    mode="production",        # "production" or "development"
    timeout=10,              # Request timeout in seconds
    max_retries=3,           # Maximum retry attempts
    backoff_factor=0.3       # Exponential backoff factor
)
```

### Environment Modes

- **Production**: Uses `https://api.talentdesk.io/`
- **Development**: Uses `https://api-demo.talentdesk.dev/`

## Error Handling

The client provides comprehensive error handling that normalizes all API responses into a consistent format. It automatically handles HTTP errors (4xx, 5xx), network timeouts, connection issues, and validation errors. The client includes built-in retry logic with exponential backoff for transient failures (429, 500, 502, 503, 504 status codes). All responses are normalized to include success status, data payload, and error messages, making it easy to handle both successful and failed requests consistently across all API endpoints.

## Response Format

All API responses follow a consistent format:

```python
{
    "success": True/False,
    "data": response_data or None,
    "error": error_message or None
}
```

## Pagination

The client automatically handles pagination for list endpoints. All results are aggregated and returned as a single list:

```python
# This automatically fetches all pages
all_projects = client.projects.get_all_projects()
print(f"Total projects: {len(all_projects)}")
```

## Rate Limiting and Retries

The client includes built-in retry logic with exponential backoff:

- **Retry Conditions**: 429, 500, 502, 503, 504 status codes
- **Default Retries**: 3 attempts
- **Backoff Factor**: 0.3 (configurable)
- **Supported Methods**: GET, POST, PUT, DELETE, HEAD, OPTIONS

## Development

### Installation from Source

```bash
git clone https://github.com/scottmurray2789/pytdesk.git
cd pytdesk
pip install -e .
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Scott Murray** - [scottmurray2789@gmail.com](mailto:scottmurray2789@gmail.com)

## Support

For support and questions:
- Create an issue on GitHub
- Contact the author directly

## Changelog

### Version 1.0.0
- Initial release
- Complete API coverage for all TalentDesk endpoints
- Automatic pagination support
- Comprehensive error handling
- Type hints and documentation
