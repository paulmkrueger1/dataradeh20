# Imports the Google Cloud client library
from google.cloud import bigquery

# Instantiates a client
bigquery_client = bigquery.Client(project='manymoons-215635')

# Import pandas for output format as DataFrame
import pandas as pd
import json

from PIL import Image
import requests
import numpy as np

def schema_row_to_dict(schema_row):
	"""
	schema_row -- <bigquery.table.SchemaRow>
	"""
	return {
        'colname': schema_row.name,
        'type': schema_row.field_type,
        'mode': schema_row.mode,
        'description': schema_row.description,
        'fields': schema_row.fields
	}

def describe_table(table='bq_events_all', dataset='dataset_dev'):
    dataset_ref = bigquery_client.dataset(dataset)
    bq_events = dataset_ref.table(table)
    tab = bigquery_client.get_table(bq_events)
    return pd.DataFrame([schema_row_to_dict(row) for row in tab.schema])

def query_BQ(query):
    """
    Main Query Function 
    
    Available datasets: 'dataset_dev'
    
    Available tables: 'bq_events_all'
    
    Example Query: "SELECT DISTINCT(event_type), COUNT(event_type) event_count FROM dataset_dev.bq_events_all GROUP BY event_type"
    """
    query_job = bigquery_client.query(query)
    results = query_job.result()
    return pd.DataFrame([dict(row) for row in results])

def image_url_to_vector(img_url):
    """
    s/o to https://stackoverflow.com/questions/15612373/convert-image-png-to-matrix-and-then-to-1d-array
    """
    response = requests.get(img_url, stream=True)
    response.raw.decode_content = True
    original_image = Image.open(response.raw)
    rgba_image = original_image.convert('RGBA')
    arr = np.array(rgba_image)

    # record the original shape
    shape = arr.shape

    # make a 1-dimensional view of arr
    flat_arr = arr.ravel()

    # convert it to a matrix
    vector = np.matrix(flat_arr)

    # do something to the vector
    vector[:,::10] = 128

    # reform a numpy array of the original shape
    arr2 = np.asarray(vector).reshape(shape)

    # make a PIL image
    img2 = Image.fromarray(arr2, 'RGBA')
    return arr2

def extract_event_types(out_df, verbose = False):
    event_type_map = {}
    failed_event_types = []
    for event_type in out_df.event_type.unique():
        event_type_df = out_df[out_df.event_type == event_type]
        if event_type not in event_type_map:
            event_type_map[event_type] = []
        for idx, row in event_type_df.iterrows():
            try:
                loaded = json.loads(row["event_properties"].replace("'",'"').replace('n"s',"n's").replace('False', '"False"').replace('True', '"True"'))
            except Exception as e:
                if verbose: 
                    print(e)
                    print(event_type, row['event_properties'], type(row["event_properties"]))
                failed_event_types.append(event_type)
                
            for key in loaded.keys():
                if key not in event_type_map[event_type]:
                    event_type_map[event_type].append(key)
                    
    unlanded_types = [e_type for e_type in failed_event_types if e_type not in event_type_map]
    
    return {
        'event_type_map': event_type_map,
        'failed_event_types': failed_event_types, # event types with at least 1 fail (could still be present in event_type_map)
        'unlanded_types': unlanded_types # event types that were in the out_df but failed on parsing the keys
    }

def generate_event_type_map(limit=100000):
	out_df = query_BQ("""
	    SELECT event_properties, event_type FROM dataset_dev.bq_events_all ORDER BY RAND() LIMIT {}
	""".format(limit))

	return extract_event_types(out_df)

def get_random_session(event_types):
	query = """
	    SELECT insert_id, client_event_time, session_id, event_type, event_properties, user_properties FROM `dataset_dev.bq_events_all`
	    WHERE session_id = (SELECT session_id FROM dataset_dev.bq_events_all WHERE event_type IN ({}) ORDER BY RAND() LIMIT 1) 
	    AND user_properties NOT LIKE '%anonymousId%' ORDER BY client_event_time;
	""".format(', '.join(["'{}'".format(i) for i in event_types]))
	out_df = query_BQ(query)
	return out_df
