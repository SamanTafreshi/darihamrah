# import pandas as pd
#
# from data_loader import get_csv
# from celery import shared_task
# from forms import filter_name
#
# import json
# from io import StringIO
# from celery_tasks import cache_dataframe, get_cached_dataframe
# from celery.result import AsyncResult
#
# @shared_task
# def amazon_csv(filter_name=None):
#     # Convert filter_name to JSON string only if it's not None
#     filter_name_json = json.dumps(filter_name) if filter_name else None
#
#     # Check if filter_name_json is valid and retrieve cached DataFrame if so
#     if filter_name_json:
#         # Directly interact with the cache to get the DataFrame CSV string
#         df_csv_str = get_cached_dataframe(filter_name_json)
#         print(f'df_csv_str ################## {df_csv_str}')
#
#         if df_csv_str:
#             if filter_name == json.loads(filter_name_json):
#                 # Decode and load DataFrame if the filter names match
#                 df = pd.read_csv(StringIO(df_csv_str.decode('utf-8')))
#                 print('DataFrame found in cache and matches the filter.')
#                 print(df.head())
#                 return  # Exit function if data is found and valid
#             else:
#                 print('Filter name does not match, generating a new one.')
#                 df_csv_str = None
#         else:
#             print('No stored DataFrame found, generating a new one.')
#             df_csv_str = None
#     else:
#         print('Filter name is None, generating a new one.')
#         df_csv_str = None
#
#     # If no cached DataFrame or filter doesn't match, generate a new one
#     if not df_csv_str:
#         df = get_csv()
#         df = df[["name", "discount_price", "actual_price", "date"]]
#         print('Generated new DataFrame.')
#
#         if filter_name:
#             df = df[df["name"].isin(filter_name)]
#             print(f'Filtered DataFrame with filter_name {filter_name}:')
#             print(df['name'].head())
#
#             # Store the filtered DataFrame in the cache using filter_name as the key
#             cache_dataframe.apply_async(args=[filter_name_json], kwargs={'df_csv_str': df.to_csv(index=False)})
#             print(f'DataFrame stored in cache with filter_name_json key: {filter_name_json}')
#
#     if df.empty:
#         raise ValueError(f"No data available after filtering with filter_name: {filter_name}")
#
#     # Continue processing the DataFrame as needed
#     df[["discount_price", "actual_price"]] = df[["discount_price", 'actual_price']].fillna(0).astype("int64")
#     df["discount_price"] = df.groupby(["date"])["discount_price"].transform("sum").fillna(0).astype("int64")
#     df["actual_price"] = df.groupby(["date"])["actual_price"].transform("sum").fillna(0).astype("int64")
#     df = df.drop_duplicates(subset=["date"], keep="last").reset_index()
#
#     x_df = df["date"]
#     y_df = [
#         df["discount_price"].fillna(0).astype("int64"),
#         df["actual_price"].fillna(0).astype("int64")
#     ]
#
#     return x_df, y_df



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
        print(f'df_csv_str ################## {df_csv_str}')

    # Check if the DataFrame CSV string is found in the cache
    if df_csv_str:
        df = pd.read_csv(StringIO(df_csv_str.decode('utf-8')))
        print('DataFrame found in cache and matches the filter.')
    else:
        # Call get_csv() only if the DataFrame is not found in the cache
        df = get_csv()
        df = df[["name", "discount_price", "actual_price", "date"]]
        print('Generated new DataFrame.')

        if filter_name:
            df = df[df["name"].isin(filter_name)]
            print(f'Filtered DataFrame with filter_name {filter_name}:')
            print(df['name'].head())
            # Store the filtered DataFrame in the cache using filter_name as the key
            cache_dataframe.apply_async(args=[filter_name_json], kwargs={'df_csv_str': df.to_csv(index=False)})
            print(f'DataFrame stored in cache with filter_name_json key: {filter_name_json}')

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


