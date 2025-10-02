import csv
import time
import random
import requests
import json
import argparse
import logging
from os import getenv
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class EmailConfig:
    """Configuration for email sending"""
    domain: str
    api_key: str
    sender_email: str
    subject: str
    template: str
    registration_link: str = ""
    delay_between_emails: float = 1.0
    max_retries: int = 3
    retry_delay: float = 20.0


class MailgunEmailSender:
    """A general-purpose email sender using Mailgun API"""
    
    def __init__(self, config: EmailConfig):
        self.config = config
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('email_sender.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def send_email_via_mailgun(self, recipient_email: str, **template_vars) -> bool:
        """
        Send email via Mailgun API
        
        Args:
            recipient_email: Email address of the recipient
            **template_vars: Variables to substitute in the email template
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Generate unique code if not provided
            if 'unique_code' not in template_vars:
                template_vars['unique_code'] = random.randint(10000, 99999)
            
            # Format the email body with template variables
            body = self.config.template.format(**template_vars)
            
            response = requests.post(
                f"https://api.mailgun.net/v3/{self.config.domain}/messages",
                auth=("api", self.config.api_key),
                data={
                    "from": self.config.sender_email,
                    "to": recipient_email,
                    "subject": self.config.subject,
                    "html": body
                },
                timeout=30
            )
            
            if response.status_code == 200:
                self.logger.info(f"Email sent successfully to {recipient_email}")
                return True
            else:
                self.logger.error(f"Failed to send email to {recipient_email}. Status: {response.status_code}, Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error sending email to {recipient_email}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error sending email to {recipient_email}: {e}")
            return False

    def send_emails_from_csv(self, csv_filename: str, email_column: str = 'email', **template_columns) -> Dict[str, int]:
        """
        Send emails from CSV file
        
        Args:
            csv_filename: Path to CSV file
            email_column: Name of the column containing email addresses
            **template_columns: Mapping of template variable names to CSV column names
            
        Returns:
            Dict with success/failure counts
        """
        stats = {'success': 0, 'failed': 0, 'total': 0}
        
        try:
            with open(csv_filename, 'r', newline='', encoding='UTF-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    stats['total'] += 1
                    recipient_email = row[email_column]
                    
                    # Prepare template variables
                    template_vars = {}
                    for template_var, csv_column in template_columns.items():
                        if csv_column in row:
                            template_vars[template_var] = row[csv_column]
                    
                    # Add registration link if configured
                    if self.config.registration_link:
                        template_vars['registration_link'] = self.config.registration_link
                    
                    # Send email with retries
                    success = self._send_with_retries(recipient_email, template_vars)
                    
                    if success:
                        stats['success'] += 1
                    else:
                        stats['failed'] += 1
                    
                    # Delay between emails
                    if stats['total'] < len(list(csv.DictReader(open(csv_filename, 'r', encoding='UTF-8')))):
                        time.sleep(self.config.delay_between_emails)
                        
        except FileNotFoundError:
            self.logger.error(f"CSV file not found: {csv_filename}")
        except Exception as e:
            self.logger.error(f"Error reading CSV file: {e}")
        
        return stats
    
    def _send_with_retries(self, recipient_email: str, template_vars: Dict) -> bool:
        """Send email with retry logic"""
        retries = self.config.max_retries
        
        while retries > 0:
            if self.send_email_via_mailgun(recipient_email, **template_vars):
                return True
            
            retries -= 1
            if retries > 0:
                self.logger.warning(f"Retrying email to {recipient_email}... {retries} attempts left")
                time.sleep(self.config.retry_delay)
            else:
                self.logger.error(f"Maximum retries reached for {recipient_email}")
        
        return False


def load_config_from_file(config_file: str) -> EmailConfig:
    """Load configuration from JSON file"""
    try:
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        return EmailConfig(**config_data)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {config_file}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in configuration file: {e}")
    except TypeError as e:
        raise ValueError(f"Invalid configuration format: {e}")


def create_default_config():
    """Create a default configuration file"""
    default_config = {
        "domain": "your-mailgun-domain.com",
        "api_key": "your-mailgun-api-key",
        "sender_email": "your-email@example.com",
        "subject": "Your Email Subject",
        "template": """<html><body>
        <p>Hello,<br><br>
        This is a template email. You can use variables like {name}, {title}, etc.<br><br>
        Best regards,<br>
        Your Team</p>
        </body></html>""",
        "registration_link": "",
        "delay_between_emails": 1.0,
        "max_retries": 3,
        "retry_delay": 20.0
    }
    
    with open('config.json', 'w') as f:
        json.dump(default_config, f, indent=2)
    
    print("Default configuration file 'config.json' created. Please update it with your settings.")


def main():
    """Main function with CLI interface"""
    parser = argparse.ArgumentParser(description='Send emails using Mailgun API')
    parser.add_argument('csv_file', help='CSV file containing recipient data')
    parser.add_argument('--config', '-c', default='config.json', help='Configuration file (default: config.json)')
    parser.add_argument('--email-column', default='email', help='Name of email column in CSV (default: email)')
    parser.add_argument('--template-vars', nargs='*', help='Template variable mappings (format: var_name:csv_column)')
    parser.add_argument('--create-config', action='store_true', help='Create default configuration file')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be sent without actually sending')
    
    args = parser.parse_args()
    
    if args.create_config:
        create_default_config()
        return
    
    try:
        # Load configuration
        config = load_config_from_file(args.config)
        sender = MailgunEmailSender(config)
        
        # Parse template variable mappings
        template_columns = {}
        if args.template_vars:
            for mapping in args.template_vars:
                if ':' in mapping:
                    var_name, csv_column = mapping.split(':', 1)
                    template_columns[var_name] = csv_column
                else:
                    print(f"Invalid template variable mapping: {mapping}. Use format: var_name:csv_column")
                    return
        
        if args.dry_run:
            print("Dry run mode - no emails will be sent")
            # TODO: Implement dry run functionality
            return
        
        # Send emails
        print(f"Sending emails from {args.csv_file}...")
        stats = sender.send_emails_from_csv(args.csv_file, args.email_column, **template_columns)
        
        print(f"\nEmail sending completed!")
        print(f"Total: {stats['total']}")
        print(f"Successful: {stats['success']}")
        print(f"Failed: {stats['failed']}")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
