import json
import os
import logging
logger = logging.getLogger(__name__)

DATA_URL        = os.environ.get("DATA_URL"         , "https://stream-staging.aceler.ai")
QUERY_MANAGER   = os.environ.get("QUERY_MANAGER"    , "https://stream-staging.aceler.ai")  
APIGW           = os.environ.get("APIGW"            , "https://apigw-staging.aceler.ai")
VERIFY_HTTPS    = os.environ.get("VERIFY_HTTPS", "true").lower().strip() == "true"

from acelerai_inputstream.models.inputstream import INSERTION_MODE, Inputstream
from acelerai_inputstream.inputstream_client import InputstreamClient