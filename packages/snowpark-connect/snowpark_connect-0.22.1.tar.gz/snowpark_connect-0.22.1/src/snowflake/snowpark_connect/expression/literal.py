#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import datetime
import decimal
from zoneinfo import ZoneInfo

import pyspark.sql.connect.proto.expressions_pb2 as expressions_proto
from tzlocal import get_localzone

from snowflake.snowpark_connect.config import global_config
from snowflake.snowpark_connect.utils.telemetry import (
    SnowparkConnectNotImplementedError,
)


def get_literal_field_and_name(literal: expressions_proto.Expression.Literal):
    match literal.WhichOneof("literal_type"):
        case "byte":
            return literal.byte, str(literal.byte)
        case "short":
            return literal.short, str(literal.short)
        case "integer":
            return literal.integer, str(literal.integer)
        case "long":
            return literal.long, str(literal.long)
        case "float":
            return (
                literal.float,
                str(literal.float) if literal.float == literal.float else "NaN",
            )
        case "double":
            return (
                literal.double,
                str(literal.double) if literal.double == literal.double else "NaN",
            )
        case "string":
            return literal.string, str(literal.string)
        case "boolean":
            return literal.boolean, str(literal.boolean)
        case "date":
            # Both snowflake and spark Date type don't consider time zones.
            # Don't use datetime.date.fromtimestamp, which depends on local timezone
            date = datetime.datetime.fromtimestamp(
                literal.date * 86400, tz=datetime.timezone.utc
            ).date()
            return date, f"DATE '{date}'"
        case "timestamp" | "timestamp_ntz" as t:
            # Note - Clients need to ensure local_timezone is the same as spark_sql_session_timeZone config.
            # No need to apply timezone for lit datetime, because we set the TIMEZONE parameter in snowpark session,
            # the snowflake backend would convert the lit datetime correctly. However, for returned column name, the
            # timezone needs to be added. Pyspark has a weird behavior that datetime.datetime always gets converted
            # to local timezone before printing according to spark_sql_session_timeZone setting. Haven't found
            # official doc about it, but this behavior is based on my testings.
            tz = (
                ZoneInfo(global_config.spark_sql_session_timeZone)
                if hasattr(global_config, "spark_sql_session_timeZone")
                else get_localzone()
            )
            if t == "timestamp":
                microseconds = literal.timestamp
            else:
                microseconds = literal.timestamp_ntz
            lit_dt = datetime.datetime.fromtimestamp(
                microseconds // 1_000_000
            ) + datetime.timedelta(microseconds=microseconds % 1_000_000)
            tz_dt = datetime.datetime.fromtimestamp(
                microseconds // 1_000_000, tz=tz
            ) + datetime.timedelta(microseconds=microseconds % 1_000_000)
            if t == "timestamp_ntz":
                lit_dt = lit_dt.astimezone(datetime.timezone.utc)
                tz_dt = tz_dt.astimezone(datetime.timezone.utc)
            return lit_dt, f"{t.upper()} '{tz_dt.strftime('%Y-%m-%d %H:%M:%S')}'"
        case "day_time_interval":
            # TODO(SNOW-1920942): Snowflake SQL is missing an "interval" type.
            timedelta = datetime.timedelta(
                seconds=literal.day_time_interval / 1_000_000
            )
            str_value = f"INTERVAL '{literal.day_time_interval / 1_000_000} SECONDS'"
            return timedelta, str_value
        case "binary":
            return literal.binary, str(literal.binary)
        case "decimal":
            # literal.decimal.precision & scale are ignored, as decimal.Decimal doesn't accept them
            return decimal.Decimal(literal.decimal.value), literal.decimal.value
        case "null" | None:
            return None, "NULL"
        case other:
            raise SnowparkConnectNotImplementedError(f"Other Literal Type {other}")
