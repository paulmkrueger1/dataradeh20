from .clients import storage_client
import json

BUCKET_NAME = 'raw-events-prod'
bucket = storage_client.get_bucket(BUCKET_NAME)

def save_to_gcs(df, dest_key, ext='.parquet'):
    """
    Todo: Update name to save_df_to_gcs
    """
    blob = bucket.blob(dest_key)
    if ext == '.parquet':
        df.to_parquet('tmp.parquet')
    elif ext == '.csv':
        df.to_csv('tmp.csv')
    blob.upload_from_filename('tmp'+ext)
    print('Uploaded to: ', dest_key)

def save_json_to_gcs(obj, dest_key):
    blob = bucket.blob(dest_key)
    json.dumps(obj, open('tmp.json', 'w'))
    blob.upload_from_filename('tmp.json')
    print('Uploaded to: ', dest_key)