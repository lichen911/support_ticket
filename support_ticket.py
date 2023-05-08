#!/usr/bin/env python3

import os
import argparse
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()


class BaseSupportTicketException(Exception):
    """Base exception for support ticket errors."""


class MissingConfiguration(BaseSupportTicketException):
    """Raised when a configuration variable is missing."""


class TicketCreationError(BaseSupportTicketException):
    """Raised when the ticket cannot be created."""


class SupportTicket:
    def __init__(self, store_number, message):
        self.store_number = store_number
        self.message = message

        self._get_env_variables()

    def _get_env_variables(self):
        try:
            self.email_address = os.environ["EMAIL_ADDRESS"]
            self.email_password = os.environ["EMAIL_PASSWORD"]
            self.smtp_server = os.environ["SMTP_SERVER"]
            self.smtp_port = int(os.environ["SMTP_PORT"])
            self.template_file_path = os.environ["TEMPLATE_FILE_PATH"]
            self.support_team_email = os.environ["SUPPORT_TEAM_EMAIL"]
        except KeyError as e:
            raise MissingConfiguration(f"Missing configuration variable: {e}")

    def _get_body(self) -> str:
        """Get the body of the email from the template file."""
        with open(self.template_file_path, "r") as f:
            template = f.read()

        body = template.replace("STORE_NUMBER", self.store_number).replace(
            "SUPPORT_MESSAGE", self.message
        )

        return body

    def _get_subject(self) -> str:
        """Get the subject of the email."""
        subject = f"Request support for store {self.store_number}"
        return subject

    def _get_message(self) -> MIMEText:
        """Create the full email that wil be used to generate the ticket."""
        msg = MIMEText(self._get_body(), "html")
        msg["From"] = self.email_address
        msg["To"] = self.support_team_email
        msg["Subject"] = self._get_subject()
        return msg

    def create(self):
        """Create the support ticket by sending an email to the designated email address."""
        try:
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as smtp:
                smtp.login(self.email_address, self.email_password)
                smtp.send_message(self._get_message())
        except Exception as e:
            raise TicketCreationError(f"Unable to send email: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Create a support ticket via a template based email."
    )
    parser.add_argument("store_number", type=str, help="The store number.")
    parser.add_argument("message", type=str, help="The support request message.")
    args = parser.parse_args()

    try:
        SupportTicket(args.store_number, args.message).create()
    except BaseSupportTicketException as e:
        print(f"Error creating ticket: {e}")


if __name__ == "__main__":
    main()
