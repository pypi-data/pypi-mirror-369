import os


# Base path for EFS-mounted volume
EFS_BASE_PATH = os.getenv("EFS_BASE_PATH", "/datasets_efs_example")

MODEL_VERSION = "v1"


# Model-specific folder
MODEL_NAME = "template_ml_model"

PIPELINE_NUMBER =  os.getenv("PIPELINE_NUMBER", "unknown")


SAGEMAKER_PATH = "/opt/ml"

# training sagemaker channels, the default value is what is expected by sagemaker
DATASET_CHANNEL_PATH = os.getenv(
    "DATASET_CHANNEL_PATH", f"{SAGEMAKER_PATH}/input/data/datasets"
)

MODEL_OUTPUT_PATH =  os.getenv(
    "MODEL_OUTPUT_PATH", f"{SAGEMAKER_PATH}/input/data/datasets"
)