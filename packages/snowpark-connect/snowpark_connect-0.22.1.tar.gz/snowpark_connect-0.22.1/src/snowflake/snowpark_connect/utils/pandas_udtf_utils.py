#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

from typing import Any, Callable, Iterator

import cloudpickle
import pandas as pd
import pyarrow as pa
from pyspark.sql.connect.proto.expressions_pb2 import CommonInlineUserDefinedFunction

import snowflake.snowpark.functions as snowpark_fn
from snowflake import snowpark
from snowflake.snowpark.types import IntegerType, PandasDataFrameType, StructType


def get_map_in_arrow_udtf(
    user_function: Callable,
    spark_column_names: list[str],
    output_column_names: list[str],
) -> Any:
    """
    Create and return a MapInArrowUDTF class with the given parameters.

    Args:
        user_function: Arrow function that processes RecordBatch iterators
        spark_column_names: List of spark column names of the given dataframe.
        output_column_names: List of expected output column names

    Returns:
        MapInArrowUDTF class that can be used with pandas_udtf
    """

    class MapInArrowUDTF:
        def __init__(self) -> None:
            self.user_function = user_function
            self.output_column_names = output_column_names
            self.spark_column_names = spark_column_names

        def end_partition(self, df: pd.DataFrame):
            if df.empty:
                empty_df = pd.DataFrame(columns=self.output_column_names)
                yield empty_df
                return

            df_without_dummy = df.drop(
                columns=["_DUMMY_PARTITION_KEY"], errors="ignore"
            )
            df_without_dummy.columns = self.spark_column_names

            # Convert pandas DataFrame to Arrow format
            table = pa.Table.from_pandas(df_without_dummy, preserve_index=False)
            batch_iterator = table.to_batches()

            result_iterator = self.user_function(batch_iterator)

            result_batches = []

            if not isinstance(result_iterator, Iterator) and not hasattr(
                result_iterator, "__iter__"
            ):
                raise RuntimeError(
                    f"snowpark_connect::UDF_RETURN_TYPE Return type of the user-defined function should be "
                    f"iterator of pyarrow.RecordBatch, but is {type(result_iterator).__name__}"
                )

            for batch in result_iterator:
                if not isinstance(batch, pa.RecordBatch):
                    raise RuntimeError(
                        f"snowpark_connect::UDF_RETURN_TYPE Return type of the user-defined function should "
                        f"be iterator of pyarrow.RecordBatch, but is iterator of {type(batch).__name__}"
                    )
                if batch.num_rows > 0:
                    result_batches.append(batch)

            if result_batches:
                combined_table = pa.Table.from_batches(result_batches)
                result_df = combined_table.to_pandas()
                yield result_df
            else:
                empty_df = pd.DataFrame(columns=self.output_column_names)
                yield empty_df

    return MapInArrowUDTF


def create_pandas_udtf(
    udtf_proto: CommonInlineUserDefinedFunction,
    spark_column_names: list[str],
    input_schema: StructType | None = None,
    return_schema: StructType | None = None,
) -> str | snowpark.udtf.UserDefinedTableFunction:
    user_function, _ = cloudpickle.loads(udtf_proto.python_udf.command)
    output_column_names = [field.name for field in return_schema.fields]

    MapInArrowUDTF = get_map_in_arrow_udtf(
        user_function, spark_column_names, output_column_names
    )

    return snowpark_fn.pandas_udtf(
        MapInArrowUDTF,
        output_schema=PandasDataFrameType(
            [field.datatype for field in return_schema.fields],
            [field.name for field in return_schema.fields],
        ),
        input_types=[
            PandasDataFrameType(
                [field.datatype for field in input_schema.fields] + [IntegerType()]
            )
        ],
        input_names=[field.name for field in input_schema.fields]
        + ["_DUMMY_PARTITION_KEY"],
        name="mapinarrow_udtf",
        replace=True,
        packages=["pyarrow", "pandas"],
        is_permanent=False,
    )
