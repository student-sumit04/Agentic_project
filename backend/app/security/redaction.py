import re


LABELED_SECRET_PATTERNS = [
    re.compile(r"\b((?:my\s+)?password\s*(?:is|[:=]))\s*\S+", re.IGNORECASE),
    re.compile(r"\b((?:my\s+)?(?:otp|pin|cvv)\s*(?:code\s*)?(?:is|[:=])?)\s*\d+\b", re.IGNORECASE),
    re.compile(r"\b((?:my\s+)?card\s+number\s*(?:is|[:=])?)\s*\d{12,19}\b", re.IGNORECASE),
]

CARD_NUMBER_PATTERN = re.compile(r"\b\d{12,19}\b")


def mask_transaction_id(value: str) -> str:
    if len(value) <= 4:
        return "****"
    return "*" * (len(value) - 4) + value[-4:]


def redact_sensitive_text(text: str) -> str:
    redacted = text
    for pattern in LABELED_SECRET_PATTERNS:
        redacted = pattern.sub(r"\1 [REDACTED]", redacted)
    return CARD_NUMBER_PATTERN.sub("[REDACTED]", redacted)
