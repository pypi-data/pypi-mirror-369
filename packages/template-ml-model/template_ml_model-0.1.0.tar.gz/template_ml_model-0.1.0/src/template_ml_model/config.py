import os

from potato_common.env import environ_str

# Base path for EFS-mounted volume
EFS_BASE_PATH = os.getenv("EFS_BASE_PATH", "/datasets_efs_example")

MODEL_VERSION = "v1"


# Model-specific folder
MODEL_NAME = "template_ml_model"

PIPELINE_NUMBER = environ_str("PIPELINE_NUMBER", "unknown")


SAGEMAKER_PATH = "/opt/ml"

# training sagemaker channels, the default value is what is expected by sagemaker
DATASET_CHANNEL_PATH = environ_str(
    "DATASET_CHANNEL_PATH", f"{SAGEMAKER_PATH}/input/data/datasets"
)

MODEL_OUTPUT_PATH = environ_str(
    "MODEL_OUTPUT_PATH", f"{SAGEMAKER_PATH}/input/data/datasets"
)