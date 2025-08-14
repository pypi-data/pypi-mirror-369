#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#
import re

from pyspark.errors import AnalysisException

from snowflake.snowpark._internal.analyzer.analyzer_utils import (
    quote_name_without_upper_casing,
)
from snowflake.snowpark_connect.config import (
    auto_uppercase_column_identifiers,
    auto_uppercase_non_column_identifiers,
)

QUOTED_SPARK_IDENTIFIER = re.compile(r"^`[^`]*(?:``[^`]*)*`$")
UNQUOTED_SPARK_IDENTIFIER = re.compile(r"^\w+$")


def unquote_spark_identifier_if_quoted(spark_name: str) -> str:
    if UNQUOTED_SPARK_IDENTIFIER.match(spark_name):
        return spark_name

    if QUOTED_SPARK_IDENTIFIER.match(spark_name):
        return spark_name[1:-1].replace("``", "`")

    raise AnalysisException(f"Invalid name: {spark_name}")


def spark_to_sf_single_id_with_unquoting(name: str) -> str:
    """
    Transforms a spark name to a valid snowflake name by quoting and potentially uppercasing it.
    Unquotes the spark name if necessary. Will raise an AnalysisException if given name is not valid.
    """
    return spark_to_sf_single_id(unquote_spark_identifier_if_quoted(name))


def spark_to_sf_single_id(name: str, is_column: bool = False) -> str:
    """
    Transforms a spark name to a valid snowflake name by quoting and potentially uppercasing it.
    Assumes that the given spark name doesn't contain quotes,
    meaning it's either already unquoted, or didn't need quoting.
    """
    name = quote_name_without_upper_casing(name)
    should_uppercase = (
        auto_uppercase_column_identifiers()
        if is_column
        else auto_uppercase_non_column_identifiers()
    )
    return name.upper() if should_uppercase else name


def split_fully_qualified_spark_name(qualified_name: str | None) -> list[str]:
    """
    Splits a fully qualified Spark identifier into its component parts.

    A dot (.) is used as a delimiter only when occurring outside a quoted segment.
    A quoted segment is wrapped in single backticks. Inside a quoted segment,
    any occurrence of two consecutive backticks is treated as a literal backtick.
    After splitting, any token that was quoted is unescaped:
      - The external backticks are removed.
      - Any double backticks are replaced with a single backtick.

    Examples:
      "a.b.c"
         -> ["a", "b", "c"]

      "`a.somethinh.b`.b.c"
         -> ["a.somethinh.b", "b", "c"]

      "`a$b`.`b#c`.d.e.f.g.h.as"
         -> ["a$b", "b#c", "d", "e", "f", "g", "h", "as"]

      "`a.b.c`"
         -> ["a.b.c"]

      "`a``b``c.d.e`"
         -> ["a`b`c", "d", "e"]

      "asdfasd" -> ["asdfasd"]
    """
    if qualified_name in ("``", "", None):
        # corner case where empty string is denoted by an empty string. We cannot have emtpy string
        # in fully qualified name.
        return [""]
    assert isinstance(qualified_name, str), qualified_name

    parts = []
    token_chars = []
    in_quotes = False
    i = 0
    n = len(qualified_name)

    while i < n:
        ch = qualified_name[i]
        if ch == "`":
            # If current char is a backtick:
            if i + 1 < n and qualified_name[i + 1] == "`":
                # If next char is also a backtick, unescape the backtick character by replacing `` with `.
                token_chars.append("`")
                i += 2
                continue
            else:
                # Toggle the in_quotes state and skip backtick in the token.
                in_quotes = not in_quotes
                i += 1
        elif ch == "." and not in_quotes:
            # Dot encountered outside of quotes: finish the current token.
            parts.append("".join(token_chars))
            token_chars = []
            i += 1
        else:
            token_chars.append(ch)
            i += 1

    if token_chars:
        parts.append("".join(token_chars))

    return parts
