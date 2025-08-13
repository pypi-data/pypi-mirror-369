import json
import os

DATA_URL        = os.environ.get("DATA_URL"         , "https://stream-staging.aceler.ai")
QUERY_MANAGER   = os.environ.get("QUERY_MANAGER"    , "https://stream-staging.aceler.ai")  
APIGW           = os.environ.get("APIGW"            , "https://apigw-staging.aceler.ai")
VERIFY_HTTPS    = os.environ.get("VERIFY_HTTPS", "true").lower().strip() == "true"

from acelerai_pipelines.pipelines_client import PipelinesClient
from acelerai_pipelines.models.run import Run
from acelerai_pipelines.models.deploy import Deploy

__results_path = os.environ.get("A2G_RESULT_PATH","a2g_results")
__payload_path = os.environ.get("A2G_PAYLOAD_PATH", "payload.json")

__mode = os.environ.get("EXEC_LOCATION", "LOCAL")

def save_result(key:str, value, path = None):
    """
    Save the result in the file
    :param key: The key to be used to save the result
    :param value: The value to be saved
    :param path: The path to save the result, if None, the default path is used
    """
    result_path = __results_path
    if path is not None and __mode == "LOCAL":
        result_path = path

    if __mode == "LOCAL":
        if not os.path.exists(result_path): os.makedirs(result_path)

    open(f"{result_path}/{key}", 'w+').write(json.dumps(value))

def get_payload(path = None) -> dict | None:
    """
    Get the payload from the file, if the file does not exist, return None
    :param path: The path to the payload file, if None, the default path is used
    """
    payload_path = __payload_path
    if path is not None and __mode == "LOCAL":
        payload_path = path

    if not os.path.exists(payload_path): return None
    return json.loads(open(payload_path).read())