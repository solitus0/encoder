import logging

from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings

config = Config(".env")

LOG_LEVEL = config("LOG_LEVEL", default=logging.DEBUG)
ENV = config("ENV", default="local")
TEMP_FOLDER = config("TEMP_FOLDER", default=None)
FAILED_DIR = config("FAILED_DIR", default=None)
EXCLUDE_FOLDERS = config("EXCLUDE_FOLDERS", default=None, cast=CommaSeparatedStrings)
MEDIA_EXTENSIONS = config("MEDIA_EXTENSIONS", default=None, cast=CommaSeparatedStrings)
API_PORT = config("API_PORT", default=None, cast=int)
RABBITMQ_HOST = config("RABBITMQ_HOST", default=None)
RABBITMQ_USER = config("RABBITMQ_USER", default=None)
RABBITMQ_PASS = config("RABBITMQ_PASS", default=None)
RABBITMQ_MANAGEMENT_URL = f"http://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}:15672/api/healthchecks/node"

RABBITMQ_ENCODE_QUEUE = config("RABBITMQ_ENCODE_QUEUE", default=None)
RABBITMQ_ENCODE_RESULTS_QUEUE = config("RABBITMQ_ENCODE_RESULTS_QUEUE", default=None)
RABBITMQ_PROBE_QUEUE = config("RABBITMQ_PROBE_QUEUE", default=None)
RABBITMQ_PROBE_RESULT_QUEUE = config("RABBITMQ_PROBE_RESULT_QUEUE", default=None)
RABBITMQ_ENCODE_PROGRESS_QUEUE = config("RABBITMQ_ENCODE_PROGRESS_QUEUE", default=None)
