from _typeshed import Incomplete

unichr = chr
CHAR_ENTITY_PATTERN: Incomplete
DECIMAL_PATTERN: Incomplete
HEX_PATTERN: Incomplete
QUOTE_PATTERN: Incomplete
ALLOWED_CHARS_PATTERN: Incomplete
ALLOWED_CHARS_PATTERN_WITH_UPPERCASE: Incomplete
DUPLICATE_DASH_PATTERN: Incomplete
NUMBERS_PATTERN: Incomplete
DEFAULT_SEPARATOR: str


def smart_truncate(string,
                   max_length: int = ...,
                   word_boundary: bool = ...,
                   separator: str = ...,
                   save_order: bool = ...,
                   trunc_loc: float = ...,
                   hash_len: Incomplete | None = ...,
                   head: str = ...,
                   tail: str = ...) -> str:
    ...


def slugify(text,
            entities: bool = ...,
            decimal: bool = ...,
            hexadecimal: bool = ...,
            max_length: int = ...,
            word_boundary: bool = ...,
            separator=...,
            save_order: bool = ...,
            stopwords=...,
            regex_pattern: Incomplete | None = ...,
            lowercase: bool = ...,
            replacements=...,
            trunc_loc: float = ...):
    ...
