import io
import base64
import pandas as pd
import pyarrow as pa
from numpy import ndarray
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema
from typing import Any, Type
from PIL import Image


class DataSeries(pd.Series):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source: Type[Any], _handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:

        return core_schema.is_instance_schema(
            pd.Series,
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: list(instance)
            ),
        )


class DataFrame(pd.DataFrame):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source: Type[Any], _handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:

        return core_schema.is_instance_schema(
            pd.DataFrame,
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: instance.to_dict(orient="records")
            ),
        )


class ArrowTable:

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source: Type[Any], _handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:

        return core_schema.is_instance_schema(
            pa.Table,
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: instance.to_pylist()
            ),
        )


class NDArray:

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source: Type[Any], _handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:

        return core_schema.is_instance_schema(
            ndarray,
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: instance.tolist()
            ),
        )


class BytesIOType:

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source: Type[Any], _handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:

        return core_schema.is_instance_schema(
            io.BytesIO,
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: base64.b64encode(instance.getvalue()).decode("utf-8")
            ),
        )


class PILImage:

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source: Type[Any], _handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:

        def image_to_base64(image):
            img_byte_io = io.BytesIO()

            image.save(img_byte_io, format=image.format)

            return base64.b64encode(img_byte_io.getvalue()).decode("utf-8")

        return core_schema.is_instance_schema(
            Image.Image,
            serialization=core_schema.plain_serializer_function_ser_schema(
                image_to_base64
            ),
        )
