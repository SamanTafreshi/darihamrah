import pandas as pd

from data_loader import get_csv
from celery import shared_task
from forms import filter_name

import json
from io import StringIO
from celery_tasks import cache_dataframe, get_cached_dataframe
from celery.result import AsyncResult

@shared_task
def amazon_csv(filter_name=None):
    df_csv_str = None

    # Convert filter_name to JSON string only if it's not None
    filter_name_json = json.dumps(filter_name) if filter_name else None

    if filter_name_json:
        # Directly interact with the cache to get the DataFrame CSV string
        df_csv_str = get_cached_dataframe(filter_name_json)

    # Check if the DataFrame CSV string is found in the cache
    if df_csv_str:
        df = pd.read_csv(StringIO(df_csv_str.decode('utf-8')))
    else:
        # Call get_csv() only if the DataFrame is not found in the cache
        df = get_csv()
        df = df[["name", "discount_price", "actual_price", "date"]]

        if filter_name:
            df = df[df["name"].isin(filter_name)]
            # Store the filtered DataFrame in the cache using filter_name as the key
            cache_dataframe.apply_async(args=[filter_name_json], kwargs={'df_csv_str': df.to_csv(index=False)})

    if df.empty:
        raise ValueError(f"No data available after filtering with filter_name: {filter_name}")

    # Continue processing the DataFrame as needed
    df[["discount_price", "actual_price"]] = df[["discount_price", 'actual_price']].fillna(0).astype("int64")
    df["discount_price"] = df.groupby(["date"])["discount_price"].transform("sum").fillna(0).astype("int64")
    df["actual_price"] = df.groupby(["date"])["actual_price"].transform("sum").fillna(0).astype("int64")
    df = df.drop_duplicates(subset=["date"], keep="last").reset_index()

    x_df = df["date"]
    y_df = [
        df["discount_price"].fillna(0).astype("int64"),
        df["actual_price"].fillna(0).astype("int64")
    ]

    return x_df, y_df


