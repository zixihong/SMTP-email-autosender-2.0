# Mailgun Email Sender

A general-purpose email sending tool using the Mailgun API. This tool allows you to send personalized emails to multiple recipients from a CSV file with customizable templates and robust error handling.

## Features

- 📧 **Bulk Email Sending**: Send emails to multiple recipients from CSV files
- 🎨 **Customizable Templates**: Use HTML templates with variable substitution
- 🔄 **Retry Logic**: Automatic retry mechanism for failed emails
- 📊 **Detailed Logging**: Comprehensive logging with success/failure statistics
- ⚙️ **Configuration Management**: JSON-based configuration for easy setup
- 🖥️ **CLI Interface**: Command-line interface for easy usage
- 🛡️ **Error Handling**: Robust error handling and recovery

## Installation

1. **Clone or download this repository**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Mailgun account**:
   - Sign up at [mailgun.com](https://www.mailgun.com/)
   - Get your API key and domain from the Mailgun dashboard
   - Verify your domain (for production use)

## Quick Start

1. **Create a configuration file**:
   ```bash
   python newsender.py --create-config
   ```

2. **Edit the configuration** (`config.json`):
   ```json
   {
     "domain": "your-mailgun-domain.com",
     "api_key": "your-mailgun-api-key",
     "sender_email": "your-email@example.com",
     "subject": "Your Email Subject",
     "template": "<html><body><p>Hello {name},<br><br>Your research on {title} is impressive!<br><br>Best regards,<br>Your Team</p></body></html>",
     "registration_link": "https://example.com/register",
     "delay_between_emails": 1.0,
     "max_retries": 3,
     "retry_delay": 20.0
   }
   ```

3. **Prepare your CSV file** with recipient data (see example below)

4. **Send emails**:
   ```bash
   python newsender.py example_recipients.csv --template-vars name:name title:title
   ```

## CSV File Format

Your CSV file should contain at least an email column. Additional columns can be used as template variables.

**Example CSV structure**:
```csv
email,name,title,company
john.doe@example.com,John Doe,Advanced Machine Learning Techniques,TechCorp Inc
jane.smith@university.edu,Jane Smith,Quantum Computing Applications,State University
```

## Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `domain` | Your Mailgun domain | Required |
| `api_key` | Your Mailgun API key | Required |
| `sender_email` | Email address to send from | Required |
| `subject` | Email subject line | Required |
| `template` | HTML email template with variables | Required |
| `registration_link` | Optional registration link | "" |
| `delay_between_emails` | Delay between emails (seconds) | 1.0 |
| `max_retries` | Maximum retry attempts | 3 |
| `retry_delay` | Delay between retries (seconds) | 20.0 |

## Template Variables

Use `{variable_name}` in your template to insert dynamic content from your CSV file.

**Example template**:
```html
<html>
<body>
  <p>Hello {name},<br><br>
  We're interested in your research: <strong>{title}</strong>.<br><br>
  Please register at: <a href="{registration_link}">Register Here</a><br><br>
  Your unique code: <strong>{unique_code}</strong><br><br>
  Best regards,<br>
  Your Team</p>
</body>
</html>
```

## Command Line Usage

### Basic Usage
```bash
python newsender.py recipients.csv
```

### Advanced Usage
```bash
python newsender.py recipients.csv \
  --config my_config.json \
  --email-column email_address \
  --template-vars name:full_name title:paper_title \
  --dry-run
```

### Command Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--config` | `-c` | Configuration file path (default: config.json) |
| `--email-column` | | Name of email column in CSV (default: email) |
| `--template-vars` | | Template variable mappings (format: var_name:csv_column) |
| `--create-config` | | Create default configuration file |
| `--dry-run` | | Show what would be sent without actually sending |

## Examples

### Example 1: Conference Invitations
```bash
# Create config
python newsender.py --create-config

# Edit config.json with your settings

# Send conference invitations
python newsender.py conference_attendees.csv \
  --template-vars name:attendee_name title:paper_title
```

### Example 2: Newsletter with Company Info
```bash
python newsender.py newsletter_subscribers.csv \
  --template-vars name:subscriber_name company:company_name \
  --config newsletter_config.json
```

### Example 3: Dry Run (Test Mode)
```bash
python newsender.py recipients.csv --dry-run
```

## Logging

The tool creates detailed logs in `email_sender.log` and displays progress in the console. Logs include:
- Successful email sends
- Failed attempts with error details
- Retry attempts
- Final statistics

## Error Handling

- **Network errors**: Automatic retry with exponential backoff
- **Invalid emails**: Logged and skipped
- **API errors**: Detailed error messages with status codes
- **File errors**: Clear error messages for missing or invalid files

## Security Notes

- Keep your API keys secure and never commit them to version control
- Use environment variables for sensitive data in production
- Verify your domain with Mailgun for production use
- Consider rate limiting for large email campaigns

## Troubleshooting

### Common Issues

1. **"Configuration file not found"**
   - Run `python newsender.py --create-config` to create a default config

2. **"Invalid JSON in configuration file"**
   - Check your JSON syntax in config.json

3. **"CSV file not found"**
   - Ensure the CSV file path is correct

4. **"Failed to send email"**
   - Check your Mailgun API key and domain
   - Verify your sender email is authorized
   - Check the logs for detailed error messages

### Getting Help

- Check the logs in `email_sender.log` for detailed error information
- Verify your Mailgun account settings
- Test with a small CSV file first
- Use `--dry-run` to test without sending emails

## License

This project is open source. Feel free to modify and distribute as needed.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.
