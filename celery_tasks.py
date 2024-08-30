from celery import Celery, shared_task

app = Celery('tasks', broker='pyamqp://guest@localhost//', backend='cache+memory://')


# Task to cache DataFrame CSV strings with filter_name as the key
@shared_task
def cache_dataframe(filter_name_json, df_csv_str):
    if not df_csv_str:
        return False
    app.backend.set(filter_name_json, df_csv_str)
    return True

# Function to retrieve cached DataFrame CSV strings based on filter_name
def get_cached_dataframe(filter_name_json):
    cached_data = app.backend.get(filter_name_json)
    if cached_data is None:
        return None
    return cached_data