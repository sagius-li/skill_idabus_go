#!/usr/bin/env python3

from __future__ import annotations

import argparse
import mimetypes
import os
import smtplib
import sys
from email.message import EmailMessage
from pathlib import Path

from env_utils import ConfigError, default_env_path, get_int_env, load_dotenv, require_env


def get_bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name, "").strip().lower()
    if not value:
        return default
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    raise ConfigError(f"Environment variable {name} must be a boolean.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send a plain-text email with optional attachments via SMTP.")
    parser.add_argument("--to", action="append", required=True, default=[], help="Recipient email address. Repeat for multiple recipients.")
    parser.add_argument("--subject", required=True, help="Email subject.")
    parser.add_argument("--body", help="Inline plain-text email body.")
    parser.add_argument("--body-file", help="Path to a plain-text file used as the email body.")
    parser.add_argument(
        "--attachment",
        action="append",
        default=[],
        help="Attachment file path. Repeat for multiple attachments.",
    )
    parser.add_argument("--env-file", default=str(default_env_path()), help="Path to the .env file.")
    return parser.parse_args()


def validate_email_address(value: str) -> str:
    candidate = value.strip()
    if not candidate or "@" not in candidate:
        raise ConfigError(f"Invalid email address: {value}")
    local_part, domain = candidate.rsplit("@", 1)
    if not local_part or not domain or "." not in domain or any(char.isspace() for char in candidate):
        raise ConfigError(f"Invalid email address: {value}")
    return candidate


def resolve_body(args: argparse.Namespace) -> str:
    if args.body is not None and args.body_file:
        raise ConfigError("Use either --body or --body-file, not both.")
    if args.body is None and not args.body_file:
        raise ConfigError("Provide either --body or --body-file.")
    if args.body is not None:
        return args.body

    body_path = Path(args.body_file)
    if not body_path.exists():
        raise ConfigError(f"Body file not found: {body_path}")
    if not body_path.is_file():
        raise ConfigError(f"Body file is not a regular file: {body_path}")
    try:
        return body_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigError(f"Unable to read body file {body_path}: {exc}") from exc


def add_attachments(message: EmailMessage, attachments: list[str]) -> None:
    for raw_path in attachments:
        attachment_path = Path(raw_path)
        if not attachment_path.exists():
            raise ConfigError(f"Attachment file not found: {attachment_path}")
        if not attachment_path.is_file():
            raise ConfigError(f"Attachment path is not a regular file: {attachment_path}")
        try:
            payload = attachment_path.read_bytes()
        except OSError as exc:
            raise ConfigError(f"Unable to read attachment file {attachment_path}: {exc}") from exc

        mime_type, _ = mimetypes.guess_type(attachment_path.name)
        if mime_type:
            maintype, subtype = mime_type.split("/", 1)
        else:
            maintype, subtype = "application", "octet-stream"

        message.add_attachment(payload, maintype=maintype, subtype=subtype, filename=attachment_path.name)


def build_message(sender: str, recipients: list[str], subject: str, body: str, attachments: list[str]) -> EmailMessage:
    message = EmailMessage()
    message["From"] = sender
    message["To"] = ", ".join(recipients)
    message["Subject"] = subject
    message.set_content(body)
    add_attachments(message, attachments)
    return message


def send_message(message: EmailMessage, recipients: list[str]) -> None:
    smtp_host = require_env("SMTP_HOST")
    smtp_port = get_int_env("SMTP_PORT", 587)
    smtp_username = os.getenv("SMTP_USERNAME", "").strip()
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    smtp_use_tls = get_bool_env("SMTP_USE_TLS", True)

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
            server.ehlo()
            if smtp_use_tls:
                server.starttls()
                server.ehlo()
            if smtp_username:
                server.login(smtp_username, smtp_password)
            server.send_message(message, to_addrs=recipients)
    except smtplib.SMTPAuthenticationError as exc:
        raise ConfigError(f"SMTP authentication failed: {exc}") from exc
    except smtplib.SMTPException as exc:
        raise ConfigError(f"SMTP send failed: {exc}") from exc
    except OSError as exc:
        raise ConfigError(f"SMTP connection failed: {exc}") from exc


def main() -> int:
    args = parse_args()

    env_file = Path(args.env_file)
    if not env_file.is_absolute():
        env_file = Path.cwd() / env_file

    try:
        load_dotenv(env_file)
        sender = validate_email_address(require_env("SMTP_FROM_EMAIL"))
        recipients = [validate_email_address(value) for value in args.to]
        body = resolve_body(args)
        message = build_message(sender, recipients, args.subject, body, args.attachment)
        send_message(message, recipients)
    except ConfigError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"Email sent to {', '.join(recipients)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
