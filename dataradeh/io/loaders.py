from .clients import bigquery_client
from google.cloud.bigquery import Dataset, Table, LoadJobConfig, QueryJobConfig, SourceFormat

"""
BIGQUERY LOADERS

BigQuery Python Client Docs
---------------------------
https://googleapis.github.io/google-cloud-python/latest/bigquery/index.html
"""

def create_bq_dataset(dataset_name, description=''):
    dataset_ref = bigquery_client.dataset(dataset_name)
	dataset = Dataset(dataset_ref)
	dataset.description = str(description)
	bigquery_client.create_dataset(dataset)
	return dataset

def create_bq_table(table_name, dataset_name, gs_data_uri='gs://raw-events-prod/data/*'):
    dataset_ref = bigquery_client.dataset(dataset_name)
	dataset = Dataset(dataset_ref)

	table_ref = dataset.table(table_name)
	table = Table(table_ref)
	bigquery_client.create_table(table)

	job_config = LoadJobConfig()
	job_config.source_format = SourceFormat.PARQUET
	load_job = bigquery_client.load_table_from_uri(
		gs_data_uri,
		dataset_ref.table(table_name),
		job_config=job_config
	)
	print('Starting job {}'.format(load_job.job_id))

	load_job.result()  # Waits for table load to complete.
	print('Job finished.')

	destination_table = bigquery_client.get_table(dataset_ref.table(table_name))
	print('Loaded {} rows.'.format(destination_table.num_rows))

	return destination_table

def create_bq_table_from_query(table_name, dataset_name, query):
	job_config = QueryJobConfig()
	dataset_ref = bigquery_client.dataset(dataset_name)
	table_ref = dataset_ref.table(table_name)
	job_config.destination = table_ref

	query_job = bigquery_client.query(
		query,
		location='US',
		job_config=job_config
	)

	query_job.result() #Waits for query to finish

	destination_table = bigquery_client.get_table(dataset_ref.table(table_name))
	return destination_table

def load_df_into_bq(df, table_name, dataset_name):
	dataset_ref = bigquery_client.dataset(dataset_name)
	table_ref = dataset_ref.table(table_name)
	job = bigquery_client.load_table_from_dataframe(
		df, 
		table_ref,
		location='US'
	)

	job.result()

	assert job.state == 'DONE'
	table = bigquery_client.get_table(table_ref)

	return table

"""
END BIGQUERY LOADERS
"""




