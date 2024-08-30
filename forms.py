from data_loader import get_csv

def filter_name():
    df = get_csv()
    return df['name'].unique().tolist()