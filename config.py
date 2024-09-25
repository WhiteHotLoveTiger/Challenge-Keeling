import os

# Endpoint is set in compose.yaml. The default value is used for unit test patching.
graph_data_endpoint = os.getenv("GRAPH_DATA_ENDPOINT", "http://default.endpoint")
