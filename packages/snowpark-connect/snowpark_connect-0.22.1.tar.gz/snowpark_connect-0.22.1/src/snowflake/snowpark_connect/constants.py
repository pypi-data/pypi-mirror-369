#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

DEFAULT_CONNECTION_NAME = "spark-connect"
DEFAULT_CONNECTION_NAME_IN_SPCS = "default"
DEFAULT_SNOWPARK_SUBMIT_CONNECTION_NAME = "snowpark-submit"

SERVER_SIDE_SESSION_ID = "321"

STRUCTURED_TYPES_ENABLED = True

# UDF evaluation types
MAP_IN_ARROW_EVAL_TYPE = 207  # eval_type for mapInArrow operations

SPARK_TZ_ABBREVIATIONS_OVERRIDES = {
    "ACT": "Australia/Darwin",
    "AET": "Australia/Sydney",
    "AGT": "America/Argentina/Buenos_Aires",
    "ART": "Africa/Cairo",
    "AST": "America/Anchorage",
    "BET": "America/Sao_Paulo",
    "BST": "Asia/Dhaka",
    "CAT": "Africa/Harare",
    "CNT": "America/St_Johns",
    "CST": "America/Chicago",
    "CTT": "Asia/Shanghai",
    "EAT": "Africa/Addis_Ababa",
    "ECT": "Europe/Paris",
    "IET": "America/Indiana/Indianapolis",
    "IST": "Asia/Kolkata",
    "JST": "Asia/Tokyo",
    "MIT": "Pacific/Apia",
    "NET": "Asia/Yerevan",
    "NST": "Pacific/Auckland",
    "PLT": "Asia/Karachi",
    "PNT": "America/Phoenix",
    "PRT": "America/Puerto_Rico",
    "PST": "America/Los_Angeles",
    "SST": "Pacific/Guadalcanal",
    "VST": "Asia/Ho_Chi_Minh",
}


COLUMN_METADATA_COLLISION_KEY = "{expr_id}_{key}"

DUPLICATE_KEY_FOUND_ERROR_TEMPLATE = "Duplicate key found: {key}. You can set spark.sql.mapKeyDedupPolicy to LAST_WIN to deduplicate map keys with last wins policy."
