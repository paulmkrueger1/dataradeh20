# dataradeh20
dataradeh package modules:

io
- Clients: Connections to API Clients (GCloud, AppSee, Syte, Amplitude, etc.)
- Readers: Get functions from API Clients)
- Writers: Create/Update functions from API Clients (e.g., save data to Google Storage )

processing
- Extractors: JSON parsing and extracting functions
- Session Processing: Functions for processing and aligning session data
- Image Processing: Image readers and vectorizers

To use:
1. Place appsee credentials file in dataradeh folder

Example:

from dataradeh.io.readers import get_appsee_sessions

START_DATE = '2018-09-01'
END_DATE = '2018-09-02'
USER_ID = '34E60899-5992-4D56-B58B-C5EDC4F65E2B'

sessions = get_appsee_sessions(USER_ID, START_DATE, END_DATE)

Other examples can be found in the Template Workbook


### Links
1. BigQuery UI: https://console.cloud.google.com/bigquery?project=manymoons-215635&p=manymoons-215635&d=dataset_dev&t=bq_events_all&page=table

2. Raw Data: https://console.cloud.google.com/storage/browser/raw-events-prod/data/?project=manymoons-215635

3. Amplitude Dashboard REST API Docs - https://amplitude.zendesk.com/hc/en-us/articles/205469748-Dashboard-Rest-API-Export-Amplitude-Dashboard-Data/

4. AppSee API Docs - https://www.appsee.com/docs/serverapi

#### Continuous Amplitude-to-GoogleStorage Job is on Google VM 'instance-2', running hourly and saving data to raw-events-prod Bucket.