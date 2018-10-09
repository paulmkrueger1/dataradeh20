# Imports the Google Cloud client library
from google.cloud import bigquery
from google.cloud import storage
import json

PROJECT = 'manymoons-215635'

# Instantiates a client
bigquery_client = bigquery.Client(project=PROJECT)

storage_client = storage.Client(project=PROJECT)

# %%%%% AppSee API Configurations %%%%%
APPSEE_URL = "https://api.appsee.com/sessions"
APPSEE_CREDENTIALS_PATH='./dataradeh/appsee_credentials.json'
APPSEE_CREDENTIALS = json.load(open(APPSEE_CREDENTIALS_PATH, 'r'))
APPSEE_API_KEY = APPSEE_CREDENTIALS['API_KEY']
APPSEE_API_SECRET = APPSEE_CREDENTIALS['API_SECRET']
# -------------------------------------

# %%%%% Amplitude API Config %%%%%
AMPLITUDE_URL = "https://amplitude.com/api/2/"
AMPLITUDE_CREDENTIALS_PATH = './dataradeh/amplitude_credentials.json'
AMPLITUDE_CREDENTIALS = json.load(open(AMPLITUDE_CREDENTIALS_PATH, 'r'))
AMPLITUDE_API_KEY = AMPLITUDE_CREDENTIALS['API_KEY']
AMPLITUDE_API_SECRET = AMPLITUDE_CREDENTIALS['API_SECRET']