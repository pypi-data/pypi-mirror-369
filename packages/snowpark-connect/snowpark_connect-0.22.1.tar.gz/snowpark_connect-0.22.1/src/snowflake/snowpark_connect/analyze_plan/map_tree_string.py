#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import pyspark.sql.connect.proto.base_pb2 as proto_base

from snowflake.snowpark_connect.relation.map_relation import map_relation
from snowflake.snowpark_connect.type_mapping import (
    SNOWPARK_TYPE_NAME_TO_PYSPARK_TYPE_NAME,
)


def map_tree_string(
    request: proto_base.AnalyzePlanRequest,
) -> proto_base.AnalyzePlanResponse:
    # TODO: tracking the difference with pyspark in SNOW-1853347
    tree_string = request.tree_string
    snowpark_df_container = map_relation(tree_string.plan.root)
    snowpark_df = snowpark_df_container.dataframe
    column_map = snowpark_df_container.column_map

    snowpark_tree_string = snowpark_df._format_schema(
        level=tree_string.level if tree_string.HasField("level") else None,
        translate_columns=column_map.snowpark_to_spark_map(),
        translate_types=SNOWPARK_TYPE_NAME_TO_PYSPARK_TYPE_NAME,
    )
    # workaround for the capitalization of nullable boolean value.
    snowpark_tree_string = snowpark_tree_string.replace(
        "nullable = True", "nullable = true"
    )
    snowpark_tree_string = snowpark_tree_string.replace(
        "nullable = False", "nullable = false"
    )
    proto_tree_string = proto_base.AnalyzePlanResponse.TreeString(
        tree_string=f"{snowpark_tree_string}\n",
    )
    return proto_base.AnalyzePlanResponse(
        session_id=request.session_id, tree_string=proto_tree_string
    )
