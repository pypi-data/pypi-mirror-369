import os
from ..dataset import DatasetClient

api_host = "http://192.168.1.35:8002"
workspace_name = "default_workspace"
api_key = "4fc086fe-d64b-4ac8-816a-0dcbf34f7368"
workspace_id = "8fb7c66a-a49d-46a8-8044-51a94cee1a36"
DatasetClient.connect(api_host=api_host, api_key=api_key, workspace_name=workspace_name)
assert os.environ["OIP_API_HOST"] == api_host
assert os.environ["WORKSPACE_ID"] == workspace_id
assert os.environ["ML_DATASET_AUTHENTICATION_TOKEN"] == api_key
# we need to create it first
dataset = DatasetClient.create(name="my_dataset")
dataset.add_files(
    "/Users/mohamed/projects/appbuilder/client/ml_dataset_client/examples/countries_dataset/europe"
)
dataset.upload()
dataset.finalize()


dataset = DatasetClient.get(dataset_name="north_america_dataset")
dataset.get_local_copy()
