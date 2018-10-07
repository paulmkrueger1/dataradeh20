import requests
import json
import pandas as pd
import numpy as np
# from snowflake.sqlalchemy import URL
import unidecode
import zipfile
import io
import pyarrow
import gzip
import os
import shutil
from datetime import datetime, timedelta

# Imports the Google Cloud client library
from google.cloud import storage
storage_client = storage.Client(project='manymoons-215635')
bucket_name = 'raw-events-prod'
bucket = storage_client.get_bucket(bucket_name)

KEY = "API_KEY"
SECRET = "API_SECRET"

def make_request(endpoint, params = ()):
    """
    Generic request function for making API requests to the amplitude API
    
    Example Endpoints: https://amplitude.zendesk.com/hc/en-us/articles/205469748-Dashboard-Rest-API-Export-Amplitude-Dashboard-Data
    """
    res = requests.get('https://amplitude.com/api/2/'+endpoint, params=params, auth=(KEY, SECRET))
    if res.status_code == 200:
        return res.content
    else:
        print('Error', res.status_code)
        return res

def datetime_string(dt):
    return str(dt).replace(' ','T').replace('-','').split(':')[0]

# Function to check and clear current exported data
def clear_raw_data(data_path='.'):
    if '180337' in os.listdir(data_path):
        shutil.rmtree(os.path.join(data_path,'180337'))
            
def prep_columns(df):
    df.columns = [col.strip('$') for col in list(df.columns)]
    to_str = ['insert_id', 'schema', 'adid', 'amplitude_event_type', 'city',
          'client_event_time', 'client_upload_time', 'country', 'data',
          'device_brand', 'device_carrier', 'device_family', 'device_id',
          'device_manufacturer', 'device_model', 'device_type', 'dma',
          'event_properties', 'event_time', 'event_type', 'group_properties',
          'groups', 'idfa', 'ip_address', 'language', 'library', 'location_lat',
          'location_lng', 'os_name', 'os_version', 'paying', 'platform', 
          'processed_time', 'region', 'sample_rate', 'server_received_time',
          'server_upload_time', 'start_version', 'user_creation_time',
          'user_id', 'user_properties', 'uuid', 'version_name'
         ]

    to_list = ['amplitude_attribution_ids']

    to_int = ['amplitude_id', 'app', 'event_id', 'session_id']

    to_bool = ['is_attribution_event']
    
    for col in df.columns:
        # if col in to_str:
        df[col] = df[col].astype(str)
        # elif col in to_list:
            # df[col] = df[col].astype(list)
        # elif col in to_int:
            # df[col] = df[col].astype(int)
        # elif col in to_bool:
            # df[col] = df[col].astype(bool)
    
    return df

def load_zip(zip_fp, raw=False):
    """
    Loads compressed zip binary into a pandas DataFrame
    """
    failures = []
    success = 0
    print(zip_fp)
    with gzip.GzipFile(zip_fp, 'r') as fin:
        raw_data = fin.readlines()
        
    if raw: return raw_data
#     str(i)
    raw_data = [x.strip() for x in raw_data]
        
#     raw_data_split = str(raw_data)[2:].split('\\n')
    
    parsed_data = []
    for n, i in enumerate(raw_data):
        if len(i) > 1:
            try:
                parsed_data.append(json.loads(str(i).strip('b\\').strip("'").strip('\\').replace('\\','')))
                success += 1
            except Exception as e:
#                 print(e)
                failures.append(n)
            
#     parsed_data = [json.loads(i.replace('\\','')) for i in raw_data_split if len(i) > 1]
    print('Success: {}, Failed: {}'.format(success, len(failures)))
    df = pd.DataFrame(parsed_data)
    return df, failures

def load_zip_dir(zip_dir, save_individual=False):
    """
    Loads all contents of a zip directory into a pandas DataFrame (via load_zip())
    """
    dfs = []
    failures_list = []
    for n, zip_fp in enumerate(os.listdir(zip_dir)):
        loaded_percent = round(100.*(n+1)/len(os.listdir(zip_dir)),2)
        print('Parsing data: {}% complete ...'.format(loaded_percent), end="\r")
        df, failures = load_zip(os.path.join(zip_dir,zip_fp))
        if save_individual:
            df = prep_columns(df)
            zip_fp = format_gcs_key(zip_fp) + '.parquet'
#             print('Uploading to: ', zip_fp, '...')
            
#             output_name = 
            save_to_gcs(df, zip_fp)
        else:
            dfs.append(df)
        failures_list.append(failures)
    
    if save_individual:
        return dfs, failures_list
    else:
        print('Successfully parsed raw data. Concatenating and returning DF')
        return pd.concat(dfs), failures_list

def format_gcs_key(zip_fp):
    return 'data/' + zip_fp[7:-8].replace('-','/').replace('_','/').replace('#','/')


def extract_data(start='20180921T07', end='20180921T08', clear_data=True, save_individual=False):
    """
    Extracts raw data, decompresses, and loads into pandas DataFrame
    
    Kwargs:
      start -- <str> start date in 'YYYYMMDDTHH' format
      end -- <str> end date in 'YYYYMMDDTHH' format
      clear_data -- <bool> whether or not to clear the loaded data before exracting more (Default: True)
      
    Return:
      parsed_data -- <pd.DataFrame> pandas DataFrame of parsed raw data
    """
    if clear_data: 
        print('Clearing workspace ...')
        clear_raw_data()
        
    params = (
        ('start', start),
        ('end', end)
    )
    print('Exporting data from API ...')
    data = make_request('export', params)
    if type(data) == bytes:
        z = zipfile.ZipFile(io.BytesIO(data))
        z.extractall() 
        print('Successfully exported raw data. \nParsing raw data ...')
        parsed_data, failures = load_zip_dir('180337', save_individual=save_individual)
        return parsed_data, failures
    else:
        print('No data in requested timeframe')
    

def save_to_gcs(df, dest_key, ext='.parquet'):
    blob = bucket.blob(dest_key)
    if ext == '.parquet':
        df.to_parquet('tmp.parquet')
    elif ext == '.csv':
        df.to_csv('tmp.csv')
    blob.upload_from_filename('tmp'+ext)
    print('Uploaded to: ', dest_key)

def run_historical_job(start_date=(2017, 9, 17, 12), end_date=(2018, 9, 25, 23), save_individual=True):
    start_date = datetime(*start_date)
    end_date = datetime(*end_date)
    tot_dt = (end_date - start_date).total_seconds() / 3600.
    all_data = []
    all_failures = {}
    for i in range(int(tot_dt)+1):
        if i % 2 == 0:
            print(i)
            start = start_date + timedelta(hours=i)
            end = start_date + timedelta(hours=i+1)
            start_str = datetime_string(start)
            end_str = datetime_string(end)
            print(start_str, end_str)
            date_key = str(start).replace('-','/').replace(' ','/').split(':')[0] + '/data.csv'
            print(date_key)
            try:
                loaded_data, failures = extract_data(start_str, end_str, save_individual=save_individual)
                all_failures[start_date] = failures
    #             if loaded_data is not None:
    #                 print(f'Adding {len(loaded_data)} rows', data_key)
    #                 save_to_gcs(loaded_data, data_key)
    #                 all_failures[start_date] = failures
    # #                 all_data.append(loaded_data)
    #             else:
    #                 all_failures[start_date] = 'No Data'
            except Exception as e:
                print(e)
                all_failures[start_date] = 'Failed'

            print('-'*20 + '\n')
#     with open('failures.json', 'w') as fi:
#         fi.write(json.dump)
    return all_failures
    
if __name__ == '__main__':
	run_historical_job((2018, 2, 22, 2))