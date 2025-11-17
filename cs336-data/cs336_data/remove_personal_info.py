import re

def mask_emails(text: str) -> str:
    """
    Replace all email addresses in the given text with '|||EMAIL_ADDRESS|||'.
    """
    # Robust email regex pattern that handles most valid email forms
    email_pattern = re.compile(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    )
    
    # Replace all detected emails
    return email_pattern.subn('|||EMAIL_ADDRESS|||', text)

def mask_phone_numbers(text: str) -> str:
    """
    Replace common U.S.-style phone numbers in the text with '|||PHONE_NUMBER|||'.
    Handles formats like:
    - 1234567890
    - 123-456-7890
    - (123) 456-7890
    - +1 123-456-7890
    - 123.456.7890
    - +1 (123)4567890
    """
    phone_pattern = re.compile(
        r"""
        (?:(?:\+?1[\s.-]*)?)                 # optional country code (+1, 1, +1-)
        (?:\(?\d{3}\)?[\s.-]*)               # area code with or without parentheses
        \d{3}[\s.-]*\d{4}                    # 7-digit local number
        """,
        re.VERBOSE
    )
    
    return phone_pattern.subn("|||PHONE_NUMBER|||", text)

def mask_ip_addresses(text: str) -> str:
    """
    Replace all IPv4 addresses in the text with '|||IP_ADDRESS|||'.
    Matches standard IPv4 patterns with values from 0.0.0.0 to 255.255.255.255.
    """
    # Regex for valid IPv4 address (0–255 per octet)
    ipv4_pattern = re.compile(
        r'\b('
        r'(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.'   # first octet
        r'(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.'   # second octet
        r'(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.'   # third octet
        r'(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)'     # fourth octet
        r')\b'
    )
    
    return ipv4_pattern.subn("|||IP_ADDRESS|||", text)
