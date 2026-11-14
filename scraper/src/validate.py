import re
from typing import Literal, Optional

from pydantic import BaseModel, ValidationError, field_validator


class BookRecord(BaseModel):
    """The shape of one finished record. description is the only optional field."""

    title: str
    product_url: str
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: Literal["One", "Two", "Three", "Four", "Five"]
    description: Optional[str] = None
    source_page: str
    fetched_at: str

    @field_validator("title", "price_text", "availability_text")
    @classmethod
    def not_empty(cls, value):
        if not value.strip():
            raise ValueError("must not be empty")
        return value

    @field_validator("product_url", "source_page")
    @classmethod
    def must_be_https(cls, value):
        if not value.startswith("https://"):
            raise ValueError("must start with https://")
        return value

    @field_validator("price_gbp")
    @classmethod
    def price_not_negative(cls, value):
        if value < 0:
            raise ValueError("must not be negative")
        return value


def parse_price(price_text):
    """'£51.77' -> 51.77"""
    match = re.search(r"\d[\d,]*(?:\.\d+)?", price_text or "")
    if not match:
        raise ValueError(f"no number found in price_text {price_text!r}")
    return float(match.group().replace(",", ""))


def _reason(error):
    if isinstance(error, ValidationError):
        return "; ".join(f"{'.'.join(str(p) for p in e['loc'])}: {e['msg']}" for e in error.errors())
    return str(error)


def validate_records(raw_records):
    """Normalize + validate. Returns (valid_records, errors). Duplicates (same product_url) count once."""
    valid, errors, seen = [], [], set()
    for raw in raw_records:
        url = raw.get("product_url")
        try:
            record = dict(raw)
            record["price_gbp"] = parse_price(record.get("price_text"))
            book = BookRecord(**record)
        except (ValueError, TypeError) as e:
            errors.append({"url": url, "reason": _reason(e)})
            continue
        if book.product_url in seen:
            continue
        seen.add(book.product_url)
        valid.append(book.model_dump())
    return valid, errors
