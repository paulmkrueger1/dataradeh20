"""
Inspired by: https://cloud.google.com/ml-engine/docs/tensorflow/distributed-tensorflow-mnist-cloud-datalab

*Hopefully this works w/ Pytorch

TODOS
- Create monitoring jobs for currently-running training jobs (https://cloud.google.com/ml-engine/docs/tensorflow/monitor-training)
- Validate that this actually works for Pytorch (https://discuss.pytorch.org/t/pytorch-in-google-cloud-ml-engine/12818/3)
"""

import tarfile
from subprocess import call
from googleapiclient import discovery
from google.cloud import storage
import os
from shutil import copyfile
ml = discovery.build('ml', 'v1')

PROJECT_ID = 'manymoons-215635'
BUCKET = 'ss-model-dev'

storage_client = storage.Client(project=PROJECT_ID)

bucket = storage_client.get_bucket(BUCKET)

def make_tarfile(source_dir, source_adds_dir):
    """
    Creates a distribution-ready source package (named 'tmp.tar.gz') for distributed training package (pytorch model functions) 
    """
    try:
        os.mkdir('tmp')
    except:
        shutil.rmtree('tmp')
        os.mkdir('tmp')
    
    for fn in os.listdir(source_adds_dir):
        src = os.path.join(source_adds_dir, fn)
        dst = os.path.join('tmp', fn)
        copyfile(src, dst)

    shutil.copytree(source_dir, 'tmp/trainer')
        
    with tarfile.open('tmp.tar.gz', "w:gz") as tar:
        tar.add('tmp', arcname=os.path.basename(source_dir))

def create_model(name, description):
    """
    Creates a new ML Engine Model
    """
    requestDict = {
        'name': name,
        'description': description
    }
    
    request = ml.projects() \
    .models() \
    .create(parent=projectID, body=requestDict)
    res = request.execute()
    return res

def run_training_job(job_name, package_path, source_adds_dir, project='manymoons-215635', 
                     **training_input_kwargs):
    """
    Runs a training job on specified package path

    Todo: remove source_adds_dir (just include addt'l files in the package)
    """
    make_tarfile(package_path, source_adds_dir)
    
    package_path = package_path.replace('.','')
    if package_path.startswith('/'):
        package_path = package_path[1:]
    
    gs_key = job_name + '/' + package_path + '.tar.gz'
    blob = bucket.blob(gs_key)
    blob.upload_from_filename('tmp.tar.gz')
    
    training_inputs = {
      "scaleTier": "STANDARD_1", # Can update this to use CUSTOM training resource settings (https://cloud.google.com/ml-engine/docs/tensorflow/machine-types)
      "packageUris": [
        "gs://ss-model-dev/{}".format(gs_key) # url to training package
      ],
      "pythonModule": "trainer.task",
      "args": [
        "--data_dir",
        "gs://ss-model-dev/data",
        "--output_dir",
        "gs://ss-model-dev/{}".format(job_name),
        "--train_steps",
        "10000"
      ],
      "region": "us-central1",
      "runtimeVersion": "1.2",
      "jobDir": "gs://ss-model-dev/{}".format(job_name)
    }
    
    if len(training_input_kwargs) > 0:
        training_inputs.update(training_input_kwargs) # allows the training_inputs dict to be updated by passed kwargs
        
    job_spec = {'jobId': job_name, 'trainingInput': training_inputs}
    
    request = ml.projects().jobs().create(body=job_spec, parent='projects/'+project)
    response = request.execute()
    return response
        
def retrieve_trained_model_uri(job_name):
	"""
	Retrieves the Google Storage URI of the trained model directory
	"""
    blobs = bucket.list_blobs(prefix='{}/export/Servo'.format(job_name))
    blob_list = [i for i in blobs]
    blob = blob_list[1] # Grab the folder containing the model output
    gs_uri = 'gs://' + '/'.join(blob.public_url.split('/')[3:-1])
    return gs_uri

def create_model_version(job_name, model_name, version_name, version_description='', projectID='manymoons-215635'):
	"""
	Creates a new model version from a specified training job and model name (Assigns the trained model to a GCloud ML Model)
	"""
    requestDict = {
        'name': version_name,
        'description': version_description,
        'deploymentUri': retrieve_trained_model_uri(job_name)
    }
    
    request = ml.projects().models().versions().create(
        parent='projects/{project_id}/models/{model_name}'.format(
            project_id=projectID,
            model_name=model_name
        ),
        body=requestDict
    ).execute()
    
    response = request.execute()
    return response

def set_default_model(model_name, version_name, projectID='manymoons-215635', **kwargs):
	"""
	Sets specified version of model as the default model (the one that will be used when called)
	"""
    request = ml.projects().models().versions().setDefault(
        name='projects/{project_id}/models/{model_name}/versions/{version}'.format(
            project_id=projectID,
            model_name=model_name,
            version=version_name
        )
    )
    
    response = request.execute()
    return response

def call_model_predictions(model_name, version_name, prediction_input_data, projectID='manymoons-215635'):
	"""
	Make an online prediction call

	For more info: https://cloud.google.com/ml-engine/docs/tensorflow/online-vs-batch-prediction
	"""
    requestDict = {
        'instances': prediction_input_data
    }
    
    request = ml.projects().predict(
        name='projects/{project_id}/models/{model_name}/versions/{version}'.format(
            project_id=projectID,
            model_name=model_name,
            version=version_name
        ),
        body=requestDict
    )
    
    response = request.execute()
    
    return response
    