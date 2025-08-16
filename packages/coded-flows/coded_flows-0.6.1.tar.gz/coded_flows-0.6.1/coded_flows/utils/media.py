import os
import uuid
import tempfile
import json
import pyarrow as pa
import pyarrow.parquet as pq
import numpy as np
import pandas as pd
from typing import Union, List, Dict, Any
from io import BytesIO
from PIL import Image


def save_image_to_temp(image, filename=None):
    random_filename = f"cfimg_{filename if filename else uuid.uuid4().hex}.png"
    temp_dir = os.path.join(tempfile.gettempdir(), "coded-flows-media")
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, random_filename)

    try:

        if isinstance(image, bytes):
            image = BytesIO(image)

        if isinstance(image, BytesIO):
            image = Image.open(image)

        if isinstance(image, np.ndarray):
            if image.dtype != np.uint8:
                image = (image * 255).astype(np.uint8)
            image = Image.fromarray(image)

        if isinstance(image, Image.Image):
            image.save(file_path, format="PNG")
        else:
            raise ValueError("Unsupported image type provided.")

    except Exception as e:
        raise ValueError(f"Failed to save image: {e}")

    return file_path


def _save_df_to_json(df: pd.DataFrame, filename: str = None) -> str:
    random_filename = f"cfdata_{filename if filename else uuid.uuid4().hex}.json"
    temp_dir = os.path.join(tempfile.gettempdir(), "coded-flows-media")
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, random_filename)
    df.to_json(file_path, orient="records", lines=False, indent=None)
    return file_path


def _save_arrow_table_to_json(table: pa.Table, filename: str = None) -> str:
    random_filename = f"cfdata_{filename if filename else uuid.uuid4().hex}.json"
    temp_dir = os.path.join(tempfile.gettempdir(), "coded-flows-media")
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, random_filename)
    records = table.to_pylist()
    with open(file_path, "w") as f:
        json.dump(records, f, separators=(",", ":"))

    return file_path


# List, DataSeries, NDArray, DataRecords, DataFrame, Arrow
def save_data_to_json(
    *data_args: Union[
        pd.DataFrame, pd.Series, pa.Table, np.ndarray, List[Dict[str, Any]], List[Any]
    ],
    labels: List[str] = [],
    is_table: bool = False,
    filename: str = None,
) -> str:
    labels = ["values"] if is_table else labels

    if not is_table and len(data_args) != len(labels):
        raise ValueError(
            "The number of data arguments must match the number of labels."
        )
    elif is_table and len(data_args) != 1:
        raise ValueError("The number of data arguments for a table must equal to 1.")

    if is_table:
        data = data_args[0]

    if is_table and (
        isinstance(data, pd.DataFrame)
        or isinstance(data, pa.Table)
        or (
            isinstance(data, list) and all(isinstance(item, dict) for item in data[:50])
        )
    ):
        table_df = None
        if isinstance(data, pd.DataFrame):
            table_df = data
        elif isinstance(data, pa.Table):
            return _save_arrow_table_to_json(data, filename)
        else:
            table_df = pd.DataFrame.from_records(data)

        return _save_df_to_json(table_df, filename)

    normalized_data = []
    max_length = 0

    for data, label in zip(data_args, labels):
        if isinstance(data, pd.DataFrame):
            if label not in data.columns:
                raise ValueError(f"Label '{label}' not found in DataFrame columns.")
            col_data = data[label].values
        elif isinstance(data, pa.Table):
            if label not in data.column_names:
                raise ValueError(f"Label '{label}' not found in Arrow table columns.")
            col_data = data.column(label).to_pylist()
        elif isinstance(data, pd.Series):
            col_data = data.values
        elif isinstance(data, np.ndarray):
            if data.ndim != 1:
                raise ValueError(
                    f"NumPy array for label '{label}' must be one-dimensional."
                )
            col_data = data
        elif isinstance(data, list) and all(
            isinstance(item, dict) for item in data[:50]
        ):
            col_data = [item.get(label, None) for item in data]
        elif isinstance(data, list):
            col_data = data
        elif isinstance(data, tuple):
            col_data = list(data)
        else:
            raise TypeError(f"Unsupported data type: {type(data)}")

        normalized_data.append(pd.Series(col_data, name=label))
        max_length = max(max_length, len(col_data))

    combined_df = pd.concat(normalized_data, axis=1)
    combined_df = combined_df.reindex(range(max_length)).reset_index(drop=True)

    return _save_df_to_json(combined_df, filename)


def save_data_to_parquet(
    data: Union[
        pd.DataFrame, pd.Series, pa.Table, np.ndarray, List[Dict[str, Any]], List[Any]
    ],
    filename=None,
) -> str:

    if (
        isinstance(data, pd.DataFrame)
        or isinstance(data, pa.Table)
        or (
            isinstance(data, list) and all(isinstance(item, dict) for item in data[:50])
        )
    ):

        random_filename = f"cfdata_{filename if filename else uuid.uuid4().hex}.parquet"
        temp_dir = os.path.join(tempfile.gettempdir(), "coded-flows-media")
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, random_filename)

        try:

            # Handle different data types
            if isinstance(data, pd.DataFrame):
                data.to_parquet(
                    file_path, row_group_size=50000, index=False, engine="pyarrow"
                )

            elif isinstance(data, pa.Table):
                pq.write_table(data, file_path, row_group_size=50000)

            else:
                table = pa.Table.from_pylist(data)
                pq.write_table(table, file_path, row_group_size=50000)

            return file_path

        except Exception as e:
            raise Exception(f"❌ Error saving data to parquet: {str(e)}")
    else:
        raise TypeError(f"Unsupported data type: {type(data)}")
