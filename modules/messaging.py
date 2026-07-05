"""
VISION AI Assistant - Messaging Module
WhatsApp and Email messaging with contact resolution.
"""
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config


def _load_contacts() -> dict:
    """Load contacts from contacts.json."""
    if config.CONTACTS_FILE.exists():
        try:
            with open(config.CONTACTS_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _resolve_contact(name: str) -> dict:
    """Resolve a contact name to phone/email."""
    contacts = _load_contacts()
    name_lower = name.lower()

    for contact_name, info in contacts.items():
        if name_lower in contact_name.lower() or contact_name.lower() in name_lower:
            return {"name": contact_name, **info}

    return None


def send_whatsapp(contact: str, message: str) -> str:
    """Send a WhatsApp message to a contact."""
    try:
        import pywhatkit

        # Resolve contact name to phone number
        contact_info = _resolve_contact(contact)

        if contact_info and "phone" in contact_info:
            phone = contact_info["phone"]
            real_name = contact_info["name"]
        elif contact.startswith("+"):
            phone = contact
            real_name = contact
        else:
            return (
                f"Contact '{contact}' not found in contacts.json. "
                f"Please add them first or provide a phone number starting with +."
            )

        # Send instantly (opens WhatsApp Web)
        pywhatkit.sendwhatmsg_instantly(
            phone_no=phone,
            message=message,
            wait_time=15,
            tab_close=True,
        )
        return f"WhatsApp message sent to {real_name}: '{message}'"

    except ImportError:
        return "Error: pywhatkit not installed. Run: pip install pywhatkit"
    except Exception as e:
        return f"WhatsApp error: {str(e)}"


def send_email(to: str, subject: str, body: str) -> str:
    """Send an email via SMTP."""
    if not config.EMAIL_ADDRESS or not config.EMAIL_PASSWORD:
        return "Email not configured. Please set EMAIL_ADDRESS and EMAIL_PASSWORD in .env"

    # Resolve contact if it's a name
    contact_info = _resolve_contact(to)
    if contact_info and "email" in contact_info:
        to_email = contact_info["email"]
        to_name = contact_info["name"]
    elif "@" in to:
        to_email = to
        to_name = to
    else:
        return f"Could not resolve email for '{to}'. Add them to contacts.json or provide a full email."

    try:
        msg = MIMEMultipart()
        msg['From'] = config.EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(config.EMAIL_SMTP_SERVER, config.EMAIL_SMTP_PORT)
        server.starttls()
        server.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()

        return f"Email sent to {to_name} ({to_email}): Subject: '{subject}'"

    except Exception as e:
        return f"Email error: {str(e)}"


def list_contacts() -> str:
    """List all saved contacts."""
    contacts = _load_contacts()
    if not contacts:
        return "No contacts saved. Add contacts to data/contacts.json"

    lines = ["Saved contacts:"]
    for name, info in contacts.items():
        phone = info.get("phone", "N/A")
        email = info.get("email", "N/A")
        lines.append(f"  [CONTACT] {name} -- Phone: {phone} -- Email: {email}")

    return "\n".join(lines)
