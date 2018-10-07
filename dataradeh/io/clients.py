# Imports the Google Cloud client library
from google.cloud import bigquery
from google.cloud import storage

PROJECT = 'manymoons-215635'

# Instantiates a client
bigquery_client = bigquery.Client(project=PROJECT)

storage_client = storage.Client(project=PROJECT)