from .clients import bigquery_client

from ..processing.extractors import extract_event_types
from ..processing.session_processing import process_appsee_sessions

import requests
import pandas as pd
import json
import os

try:
	from .clients import APPSEE_URL, APPSEE_API_KEY, APPSEE_API_SECRET
	def get_appsee_sessions(user_id, start_date, end_date):
		payload = {
			'apikey': APPSEE_API_KEY, 
			'apisecret': APPSEE_API_SECRET, 
			'fromdate': start_date, 
			'todate': end_date, 
			'userid': user_id
		}

		r = requests.get(url = APPSEE_URL, params=payload)
		if r.status_code == 200:
			print('Session data received. Processing output...')
			sessions_json = r.json()
			output_dfs = process_appsee_sessions(sessions_json)
			print('Returning {} sessions'.format(len(output_dfs)))
			return output_dfs
		else:
			print('Returning error..')
			return r
except:
	print('No AppSee Credentials detected. Cannot use get_appsee_sessions()')

def schema_row_to_dict(schema_row):
	"""
	Converts a BigQuery SchemaRow-type into a Python dict. Used by describe_table
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
	"""
	Describes the schema of a BigQuery table
	"""
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

def generate_event_type_map(limit=100000):
	out_df = query_BQ("""
	    SELECT event_properties, event_type FROM dataset_dev.bq_events_all ORDER BY RAND() LIMIT {}
	""".format(limit))

	return extract_event_types(out_df)

def get_random_amplitude_session(event_types, 
	columns = ['insert_id', 'uuid', 'client_event_time', 'session_id', 'event_type', 'event_properties', 'user_properties']):
	"""
	Grabs all Amplitude events (via bigQuery) from random user session with at least 1 event being of the specified input types

	Args:
	  event_types -- <[]str> list of event_types

	Return:
	  out_df -- <pd.DataFrame> pandas DF of user session with 1 row per event
	"""
	assert len(event_types) > 0, 'Must pass at least 1 specified event_type'
	query = """
	    SELECT {column_str} FROM `dataset_dev.bq_events_all`
	    WHERE session_id = (SELECT session_id FROM dataset_dev.bq_events_all WHERE event_type IN ({event_type_str}) ORDER BY RAND() LIMIT 1) 
	    AND user_properties NOT LIKE '%anonymousId%' ORDER BY client_event_time;
	""".format(
		column_str=', '.join(columns), 
		event_type_str=', '.join(["'{}'".format(i) for i in event_types])
	)
	out_df = query_BQ(query)
	return out_df