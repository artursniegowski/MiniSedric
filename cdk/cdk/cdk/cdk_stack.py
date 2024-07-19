from aws_cdk import (
    aws_s3 as s3,
    aws_apigateway as apigateway,
    aws_lambda as _lambda,
    aws_iam as iam,
    Stack,
)
from constructs import Construct
import os


class CdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        
        bucket = s3.Bucket(
            self, 
            "MiniSedricBucket",
            bucket_name=os.getenv('AWS_S3_BUCKETNAME_MINISEDRIC')
        )

        lambda_role = iam.Role(
            self,
            "LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonTranscribeFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
            ]
        )
        
        lambda_function = _lambda.Function(
            self,
            "MiniSedricLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("../../lambda"),
            role=lambda_role,
            environment={
                'BUCKET_NAME': bucket.bucket_name
            },
        )
        
        api = apigateway.RestApi(
            self,
            "AudioInteractions",
            rest_api_name="Audio Interactions",
            description="Retrives insights from a given MP3 file, based on trackers values",
            endpoint_configuration={
                "types": [apigateway.EndpointType.REGIONAL]
            },
        )

        lambda_integration = apigateway.LambdaIntegration(lambda_function)
        
        interactions = api.root.add_resource("interactions")
        interactions.add_method("POST", lambda_integration)