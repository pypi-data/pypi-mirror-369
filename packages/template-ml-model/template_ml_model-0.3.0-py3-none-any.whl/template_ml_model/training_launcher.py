import boto3
from sagemaker.estimator import Estimator
import sagemaker

from template_ml_model.config import PIPELINE_NUMBER

training_job_run_policy_arn = (
    f"arn:aws:iam::455315867910:role/sagemaker-training-role"
)

image_uri = f"455315867910.dkr.ecr.us-east-2.amazonaws.com/template_ml_model:latest"


def launch_bandit_training():
    session = sagemaker.Session(default_bucket="linia")
    # role = "arn:aws:iam::<pip install tensorflow==2.9.1account_id>:role/SageMakerExecutionRole"
    role = training_job_run_policy_arn

    # # EFS path for dataset
    # datasets_input = FileSystemInput(
    #     file_system_id="fs-12345678",
    #     file_system_type="EFS",
    #     directory_path=f"/{MODEL_NAME}/{MODEL_VERSION}",
    #     file_system_access_mode="ro"
    # )

    output_path = f"s3://linia/models/template_ml_model/v1/results"
    estimator = Estimator(
        image_uri=image_uri,
        role=role,
        instance_count=1,
        base_job_name="template-ml-model",
        instance_type="ml.m5.large",
        hyperparameters={
            "num_arms": 5,
            "epsilon": 0.1
        },
        sagemaker_session=session,
        output_path=output_path,
    )
    inputs = {
        "datasets"  : "s3://linia/models/template_ml_model/v1/data",
    }
    estimator.fit(inputs=inputs)

if __name__ == "__main__":
    launch_bandit_training()
    # print("oi")