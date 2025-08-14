#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import pyspark.sql.connect.proto.relations_pb2 as relation_proto
from pyspark.sql.connect.proto.expressions_pb2 import CommonInlineUserDefinedFunction

import snowflake.snowpark.functions as snowpark_fn
from snowflake import snowpark
from snowflake.snowpark.types import StructType
from snowflake.snowpark_connect.config import global_config
from snowflake.snowpark_connect.constants import MAP_IN_ARROW_EVAL_TYPE
from snowflake.snowpark_connect.dataframe_container import DataFrameContainer
from snowflake.snowpark_connect.relation.map_relation import map_relation
from snowflake.snowpark_connect.type_mapping import proto_to_snowpark_type
from snowflake.snowpark_connect.utils.pandas_udtf_utils import create_pandas_udtf
from snowflake.snowpark_connect.utils.udf_helper import (
    SnowparkUDF,
    process_udf_in_sproc,
    require_creating_udf_in_sproc,
    udf_check,
)
from snowflake.snowpark_connect.utils.udf_utils import (
    ProcessCommonInlineUserDefinedFunction,
)
from snowflake.snowpark_connect.utils.udtf_helper import (
    create_pandas_udtf_in_sproc,
    require_creating_udtf_in_sproc,
)
from snowflake.snowpark_connect.utils.udxf_import_utils import (
    get_python_udxf_import_files,
)


def map_map_partitions(
    rel: relation_proto.Relation,
) -> DataFrameContainer:
    """
    Map a function over the partitions of the input DataFrame.

    This is a simple wrapper around the `mapInPandas` method in Snowpark.
    """
    input_container = map_relation(rel.map_partitions.input)
    input_df = input_container.dataframe
    udf_proto = rel.map_partitions.func
    udf_check(udf_proto)

    # Check if this is mapInArrow (eval_type == 207)
    eval_type = udf_proto.python_udf.eval_type

    if eval_type == MAP_IN_ARROW_EVAL_TYPE:
        return _map_in_arrow_with_pandas_udtf(input_container, udf_proto)
    else:
        return _map_partitions_with_udf(input_df, udf_proto)


def _call_udtf(
    udtf_name: str, input_df: snowpark.DataFrame, return_type: StructType | None = None
) -> snowpark.DataFrame:
    # Add a dummy column with random 1-10 values for partitioning
    input_df_with_dummy = input_df.withColumn(
        "_DUMMY_PARTITION_KEY",
        (
            snowpark_fn.uniform(
                snowpark_fn.lit(1), snowpark_fn.lit(10), snowpark_fn.random()
            )
            * 10
        ).cast("int"),
    )

    udtf_columns = input_df.columns + [snowpark_fn.col("_DUMMY_PARTITION_KEY")]

    result_df_with_dummy = input_df_with_dummy.select(
        snowpark_fn.call_table_function(udtf_name, *udtf_columns).over(
            partition_by=[snowpark_fn.col("_DUMMY_PARTITION_KEY")]
        )
    )

    output_cols = [field.name for field in return_type.fields]

    # Only return the output columns.
    result_df = result_df_with_dummy.select(*output_cols)

    return DataFrameContainer.create_with_column_mapping(
        dataframe=result_df,
        spark_column_names=output_cols,
        snowpark_column_names=output_cols,
        snowpark_column_types=[field.datatype for field in return_type.fields],
    )


def _map_in_arrow_with_pandas_udtf(
    input_df_container: DataFrameContainer,
    udf_proto: CommonInlineUserDefinedFunction,
) -> snowpark.DataFrame:
    """
    Handle mapInArrow using pandas_udtf for partition-level Arrow processing.
    """
    input_df = input_df_container.dataframe
    input_schema = input_df.schema
    spark_column_names = input_df_container.column_map.get_spark_columns()
    return_type = proto_to_snowpark_type(udf_proto.python_udf.output_type)
    if require_creating_udtf_in_sproc(udf_proto):
        udtf_name = create_pandas_udtf_in_sproc(
            udf_proto, spark_column_names, input_schema, return_type
        )
    else:
        map_in_arrow_udtf = create_pandas_udtf(
            udf_proto, spark_column_names, input_schema, return_type
        )
        udtf_name = map_in_arrow_udtf.name
    return _call_udtf(udtf_name, input_df, return_type)


def _map_partitions_with_udf(
    input_df: snowpark.DataFrame, udf_proto
) -> snowpark.DataFrame:
    """
    Original UDF-based approach for non-mapInArrow map_partitions cases.
    """
    input_column_names = input_df.columns
    kwargs = {
        "common_inline_user_defined_function": udf_proto,
        "input_types": [f.datatype for f in input_df.schema.fields],
        "called_from": "map_map_partitions",
        "udf_name": "spark_map_partitions_udf",
        "input_column_names": input_column_names,
        "replace": True,
        "return_type": proto_to_snowpark_type(udf_proto.python_udf.output_type),
        "udf_packages": global_config.get("snowpark.connect.udf.packages", ""),
        "udf_imports": get_python_udxf_import_files(input_df.session),
    }

    if require_creating_udf_in_sproc(udf_proto):
        snowpark_udf = process_udf_in_sproc(**kwargs)
    else:
        udf_processor = ProcessCommonInlineUserDefinedFunction(**kwargs)
        udf = udf_processor.create_udf()
        snowpark_udf = SnowparkUDF(
            name=udf.name,
            input_types=udf._input_types,
            return_type=udf._return_type,
            original_return_type=None,
        )
    udf_column_name = "UDF_OUTPUT"
    snowpark_columns = [snowpark_fn.col(name) for name in input_df.columns]
    result = input_df.select(snowpark_fn.call_udf(snowpark_udf.name, *snowpark_columns))
    return DataFrameContainer.create_with_column_mapping(
        dataframe=result,
        spark_column_names=[udf_column_name],
        snowpark_column_names=[udf_column_name],
        snowpark_column_types=[snowpark_udf.return_type],
    )
