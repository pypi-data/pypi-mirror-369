# Urarovite 🔍

[![PyPI version](https://badge.fury.io/py/urarovite.svg)](https://badge.fury.io/py/urarovite)
[![Python versions](https://img.shields.io/pypi/pyversions/urarovite.svg)](https://pypi.org/project/urarovite/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive Google Sheets validation library with **gspread integration** and **full backward compatibility**. Urarovite provides robust data validation, authentication via service accounts, and seamless integration with existing codebases.

## 🚀 Features

- **Modern Authentication**: Base64-encoded service account credentials (no file storage required)
- **Domain-wide Delegation**: Enterprise-grade user impersonation support
- **gspread Integration**: Modern Python library for Google Sheets access
- **Backward Compatibility**: All existing imports and usage patterns preserved
- **Comprehensive Validation**: Built-in validators for data quality, format validation, and more
- **Client Caching**: Improved performance through intelligent credential caching
- **Type Safety**: Full type hints throughout the codebase
- **Error Handling**: Graceful error handling with structured responses

## 📦 Installation

```bash
pip install urarovite
```

### Optional Dependencies

```bash
# For Excel file support
pip install urarovite[excel]

# For development
pip install urarovite[dev]

# For Jupyter notebook support
pip install urarovite[notebook]

# Install all extras
pip install urarovite[excel,dev,notebook]
```

## 🔑 Authentication Setup

### Service Account (Recommended)

1. **Create a Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one

2. **Enable APIs**:
   - Navigate to "APIs & Services" > "Library"
   - Enable "Google Sheets API" and "Google Drive API"

3. **Create Service Account**:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Download the JSON key file

4. **Prepare Credentials**:
   ```python
   import base64
   import json
   
   # Load your service account JSON
   with open('path/to/service-account.json', 'r') as f:
       service_account = json.load(f)
   
   # Encode for use with urarovite
   encoded_creds = base64.b64encode(json.dumps(service_account).encode()).decode()
   ```

### Domain-wide Delegation (Enterprise)

For enterprise users who need to impersonate other users:

1. **Enable Domain-wide Delegation** in your service account settings
2. **Add OAuth Scopes** in Google Admin Console:
   - `https://www.googleapis.com/auth/spreadsheets`
   - `https://www.googleapis.com/auth/drive.readonly`

## 💻 Usage

### Basic Validation

```python
from urarovite.core.api import execute_validation, get_available_validation_criteria
import base64
import json

# Prepare your base64-encoded service account credentials
encoded_creds = "eyJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsIC4uLn0="

# List available validators
validators = get_available_validation_criteria()
print(validators)
# [{"id": "empty_cells", "name": "Fix Empty Cells"}, ...]

# Execute validation
result = execute_validation(
    check={"id": "empty_cells", "mode": "fix"},
    sheet_url="https://docs.google.com/spreadsheets/d/1ABC123/edit",
    auth_secret=encoded_creds,
    subject="user@domain.com"  # Optional: for domain-wide delegation
)

print(f"Fixed {result['fixes_applied']} issues")
print(f"Found {result['issues_flagged']} additional issues")
print(f"Logs: {result['automated_logs']}")
```

### Advanced Usage with gspread

```python
from urarovite.auth import get_gspread_client, create_sheets_service_from_encoded_creds
from urarovite.utils.sheets import extract_sheet_id, get_sheet_values

# Create gspread client (recommended)
client = get_gspread_client(encoded_creds, subject="user@domain.com")
spreadsheet = client.open_by_key(sheet_id)

# Or create traditional Google Sheets API service
service = create_sheets_service_from_encoded_creds(encoded_creds)

# Use utility functions
sheet_id = extract_sheet_id("https://docs.google.com/spreadsheets/d/1ABC123/edit")
data = get_sheet_values(service, sheet_id, "Sheet1!A1:Z1000")
```

### Legacy Compatibility

```python
# All existing imports still work!
from urarovite.checker import extract_sheet_id, fetch_sheet_tabs
from urarovite.checker.utils import parse_tab_token, split_segments

# URL parsing works exactly as before
sheet_id = extract_sheet_id("https://docs.google.com/spreadsheets/d/1ABC123/edit")
segments = split_segments("'Sheet1'!A1:B2@@'Sheet2'!C3:D4")
```

## 🔧 Migration from OAuth

If you're migrating from OAuth-based authentication:

```python
# OLD: OAuth-based authentication
from urarovite.checker.auth import get_credentials, get_sheets_service
creds = get_credentials()  # Interactive OAuth flow
service = get_sheets_service()

# NEW: Service account with base64 credentials
from urarovite.auth import create_sheets_service_from_encoded_creds
service = create_sheets_service_from_encoded_creds(encoded_creds)

# Or use modern gspread client (recommended)
from urarovite.auth import get_gspread_client
client = get_gspread_client(encoded_creds)
```

## 📚 Documentation

- **Migration Guide**: See [MIGRATION_SUMMARY.md](MIGRATION_SUMMARY.md) for detailed changes
- **API Reference**: Full type hints and docstrings throughout the codebase
- **Examples**: Check the `/tests` directory for comprehensive usage examples

## 🧪 Testing

```bash
# Install with dev dependencies
pip install urarovite[dev]

# Run tests
pytest

# Run with coverage
pytest --cov=urarovite
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Install development dependencies: `pip install urarovite[dev]`
4. Make your changes with proper type hints and tests
5. Run tests and linting: `pytest && ruff check`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **PyPI**: https://pypi.org/project/urarovite/
- **GitHub**: https://github.com/ParetoWorkers/Urarovite
- **Issues**: https://github.com/ParetoWorkers/Urarovite/issues
