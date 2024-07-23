import os

from aws_cdk import Stack
from aws_cdk import aws_apigateway as apigateway
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_s3 as s3
from constructs import Construct


class CdkStack(Stack):
    """
    A CDK Stack that sets up AWS resources for a serverless application.

    This stack provisions the following AWS resources:
    - An S3 bucket for storing files.
    - An IAM role with necessary permissions for Lambda functions.
    - A Lambda function that processes files and interacts with the S3 bucket.
    - An API Gateway to expose the Lambda function via HTTP endpoints.

    Attributes:
        bucket (s3.Bucket): The S3 bucket used for storing files.
        lambda_role (iam.Role): The IAM role assumed by the Lambda function.
        lambda_function (_lambda.Function): The Lambda function that processes files.
        api (apigateway.RestApi): The API Gateway for the Lambda function.
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket = s3.Bucket(
            self,
            "MiniSedricBucket",
            bucket_name=os.getenv("AWS_S3_BUCKETNAME_MINISEDRIC"),
        )

        lambda_role = iam.Role(
            self,
            "LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonTranscribeFullAccess"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
            ],
        )

        lambda_function = _lambda.Function(
            self,
            "MiniSedricLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("../../lambda"),
            role=lambda_role,
            environment={"BUCKET_NAME": bucket.bucket_name},
            reserved_concurrent_executions=5,
        )

        # Add this line for lambda provisioned concurrency
        # lambda_alias = _lambda.Alias(
        #     self,
        #     "LambdaAlias",
        #     alias_name="live",
        #     version=lambda_function.current_version,
        #     provisioned_concurrent_executions=1
        # )

        api = apigateway.RestApi(
            self,
            "AudioInteractions",
            rest_api_name="Audio Interactions",
            description="Retrives insights from a given MP3 file, based on trackers values",
            endpoint_configuration={"types": [apigateway.EndpointType.REGIONAL]},
        )

        # Add this line for lambda provisioned concurrency
        # lambda_integration = apigateway.LambdaIntegration(lambda_alias)
        lambda_integration = apigateway.LambdaIntegration(lambda_function)

        interactions = api.root.add_resource("interactions")
        interactions.add_method("POST", lambda_integration)
