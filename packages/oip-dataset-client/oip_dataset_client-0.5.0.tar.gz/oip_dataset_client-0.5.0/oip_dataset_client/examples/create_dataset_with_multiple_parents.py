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

europe_dataset = DatasetClient.create(name="europe_dataset")
europe_dataset.add_files(
    "/Users/mohamed/projects/oip-mlops-be/client/oip_ml_dataset/examples/countries_dataset/europe"
)
europe_dataset.upload()
europe_dataset.finalize()

asia_dataset = DatasetClient.create(name="asia_dataset")
asia_dataset.add_files(
    "/Users/mohamed/projects/oip-mlops-be/client/oip_ml_dataset/examples/countries_dataset/asia",
    parent_datasets=[europe_dataset.id],
)
asia_dataset.upload()
asia_dataset.finalize()

africa_dataset = DatasetClient.create(name="africa_dataset")
africa_dataset.add_files(
    "/Users/mohamed/projects/oip-mlops-be/client/oip_ml_dataset/examples/countries_dataset/africa",
    parent_datasets=[asia_dataset.id],
)
africa_dataset.upload()
africa_dataset.finalize()

north_america_dataset = DatasetClient.create(name="north_america_dataset")
africa_dataset.add_files(
    "/Users/mohamed/projects/oip-mlops-be/client/oip_ml_dataset/examples/countries_dataset/north_america",
    parent_datasets=[africa_dataset.id],
)
north_america_dataset.upload()
north_america_dataset.finalize()
