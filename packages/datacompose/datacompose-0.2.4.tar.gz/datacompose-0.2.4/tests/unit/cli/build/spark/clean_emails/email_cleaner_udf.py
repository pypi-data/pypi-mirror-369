"""
Generated email_cleaner UDF from spec: email_cleaner
Auto-generated on: 2025-07-19T16:54:44.537369
Spec hash: e52aaa1b
"""

import re
from typing import Any, Optional, Union
import numpy as np
import pandas as pd
from pyspark.sql.functions import pandas_udf
from pyspark.sql.types import StringType


# Regex patterns for email validation
USER_REGEX = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*$"
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"$)',
    re.IGNORECASE,
)

DOMAIN_REGEX = re.compile(
    r"(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?$)"
    r"|^\[(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\]$",
    re.IGNORECASE,
)

DOMAIN_WHITELIST = {"localhost"}

# Known valid domains for domain fixing
DOMAINS = {
    "aol.com", "att.net", "comcast.net", "facebook.com", "gmail.com", "gmx.com",
    "googlemail.com", "google.com", "hotmail.com", "hotmail.co.uk", "mac.com",
    "me.com", "mail.com", "msn.com", "live.com", "sbcglobal.net", "verizon.net",
    "yahoo.com", "yahoo.co.uk", "email.com", "fastmail.fm", "games.com", "gmx.net",
    "hush.com", "hushmail.com", "icloud.com", "iname.com", "inbox.com", "lavabit.com",
    "love.com", "outlook.com", "pobox.com", "protonmail.ch", "protonmail.com",
    "tutanota.de", "tutanota.com", "tutamail.com", "tuta.io", "keemail.me",
    "rocketmail.com", "safe-mail.net", "wow.com", "ygm.com", "ymail.com", "zoho.com",
    "yandex.com", "bellsouth.net", "charter.net", "cox.net", "earthlink.net", "juno.com",
    "btinternet.com", "virginmedia.com", "blueyonder.co.uk", "freeserve.co.uk",
    "live.co.uk", "ntlworld.com", "o2.co.uk", "orange.net", "sky.com", "talktalk.co.uk",
    "tiscali.co.uk", "virgin.net", "wanadoo.co.uk", "bt.com", "sina.com", "sina.cn",
    "qq.com", "naver.com", "hanmail.net", "daum.net", "nate.com", "yahoo.co.jp",
    "yahoo.co.kr", "yahoo.co.id", "yahoo.co.in", "yahoo.com.sg", "yahoo.com.ph",
    "163.com", "yeah.net", "126.com", "21cn.com", "aliyun.com", "foxmail.com"
}

# Custom rules from spec
CORPORATE_DOMAINS = ["company.com", "corp.internal", "localhost"]

BLOCKED_DOMAINS = ["spam.com", "fake.net", "temporary.email"]

REQUIRED_TLDS = []


@pandas_udf(returnType=StringType())
def email_cleaner_udf(emails: pd.Series) -> pd.Series:
    """
    Clean email addresses using pandas vectorized operations.
    
    Args:
        emails: Series of email addresses to clean
        
    Returns:
        Series of cleaned email addresses
    """
    
    def _check_email(val: Any, *, clean: bool) -> Union[str, bool]:
        """Check whether a value is a valid email."""
        # Handle null values
        if pd.isna(val) or val is None:
            return "null" if clean else False

        val_str = str(val)
        
        # Check for @ symbol
        if "@" not in val_str:
            return "bad_format" if clean else False

        # Split into user and domain parts
        try:
            user_part, domain_part = val_str.rsplit("@", 1)
        except ValueError:
            return "bad_format" if clean else False

        # Check for blocked domains first
        if domain_part.lower() in [d.lower() for d in BLOCKED_DOMAINS]:
            return "blocked" if clean else False

        # Corporate domains bypass normal validation
        if domain_part.lower() in [d.lower() for d in CORPORATE_DOMAINS]:
            return "valid" if clean else True

        # Check required TLDs if specified
        if REQUIRED_TLDS:
            domain_lower = domain_part.lower()
            if not any(domain_lower.endswith(tld.lower()) for tld in REQUIRED_TLDS):
                return "invalid_tld" if clean else False

        # Validate user part
        if not USER_REGEX.match(user_part):
            return "bad_format" if clean else False

        # Check user part length (RFC 5321 limit)
        if len(user_part.encode("utf-8")) > 64:
            return "overflow" if clean else False

        # Validate domain part
        if domain_part in DOMAIN_WHITELIST:
            return "valid" if clean else True
        
        if DOMAIN_REGEX.match(domain_part):
            return "valid" if clean else True
        
        # Try IDN (internationalized domain name) conversion
        try:
            ascii_domain = domain_part.encode("idna").decode("ascii")
            if DOMAIN_REGEX.match(ascii_domain):
                return "valid" if clean else True
        except UnicodeError:
            pass
        
        return "unknown" if clean else False
    
    def _fix_domain_name(domain: str) -> str:
        """Attempt to fix common domain name typos."""
        if domain in DOMAINS:
            return domain
        
        # Strategy 1: Remove single character at each position
        for i in range(len(domain)):
            candidate = domain[:i] + domain[i + 1:]
            if candidate in DOMAINS:
                return candidate

        # Strategy 2: Insert single character at each position
        for i in range(len(domain) + 1):
            for char in "abcdefghijklmnopqrstuvwxyz":
                candidate = domain[:i] + char + domain[i:]
                if candidate in DOMAINS:
                    return candidate

        # Strategy 3: Swap adjacent characters
        for i in range(len(domain) - 1):
            candidate = (domain[:i] + 
                        domain[i + 1] + 
                        domain[i] + 
                        domain[i + 2:])
            if candidate in DOMAINS:
                return candidate

        return domain
    
    def _normalize_user_part(user_part: str, domain_part: str) -> str:
        """Apply user part normalization rules."""
        # Remove dots from Gmail usernames
        if domain_part.lower() in ['gmail.com', 'googlemail.com']:
            user_part = user_part.replace('.', '')
        
        
        return user_part
    
    def _format_email(val: Any) -> Optional[str]:
        """Transform an email address into a clean format."""
        # Pre-process: remove whitespace if requested
        if val is not None:
            val = re.sub(r"[\s\u180B\u200B\u200C\u200D\u2060\uFEFF]+", "", str(val))

        validation_result = _check_email(val, clean=True)

        if validation_result not in ["valid"]:
            return None

        # Normalize the email
        user_part, domain_part = str(val).lower().rsplit("@", 1)

        # Apply domain fixing if requested
        domain_part = _fix_domain_name(domain_part)

        # Apply user part normalization
        user_part = _normalize_user_part(user_part, domain_part)

        email = f"{user_part}@{domain_part}"
        
        # Length validation
        if len(email) < 6:
            return None
        
        if len(email) > 254:
            return None

        return email
    
    # Apply cleaning function to all emails
    return emails.apply(_format_email)