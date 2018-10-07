from .clients import storage_client

BUCKET_NAME = 'raw-events-prod'
bucket = storage_client.get_bucket(BUCKET_NAME)

def save_to_gcs(df, dest_key, ext='.parquet'):
    blob = bucket.blob(dest_key)
    if ext == '.parquet':
        df.to_parquet('tmp.parquet')
    elif ext == '.csv':
        df.to_csv('tmp.csv')
    blob.upload_from_filename('tmp'+ext)
    print('Uploaded to: ', dest_key)