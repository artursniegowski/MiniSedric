# MiniSedric
MiniSedric is a minimal backend service designed to analyze human interactions from audio files. This project provides an API that processes audio interactions in the form of MP3 files by transcribing them, extracting insights, and returning those insights in a structured format.

## Project Overview
The service utilizes AWS infrastructure to handle audio transcription and storage:

AWS S3 for storing audio files.
AWS Transcribe for converting audio to text.
AWS Lambda for orchestrating the process of transcription and insight extraction.
AWS API Gateway for providing an HTTP endpoint to interact with the Lambda functions.
Features
Transcription: Converts MP3 files into text using AWS Transcribe.
Insight Extraction: Extracts specified values from the transcribed text using regular expressions (or Spacy NLP in future enhancements).
API Gateway: Provides an HTTP endpoint for interaction.
API Response: Returns insights in a structured JSON format.
Setup Instructions
Prerequisites
AWS Account: Ensure you have an AWS account with access to S3, Transcribe, Lambda, and API Gateway.
AWS CLI: Install and configure the AWS CLI with your credentials.
Python: Ensure Python 3.7 or later is installed.
Terraform (optional): If using Terraform for infrastructure setup.
Infrastructure Setup
Clone the Repository

bash
Skopiuj kod
git clone https://github.com/yourusername/minisedric.git
cd minisedric
Install Dependencies

Install required Python packages using pip:

bash
Skopiuj kod
pip install -r requirements.txt
Deploy Infrastructure

Using Terraform

If you are using Terraform, navigate to the Terraform configuration directory and apply the configuration:

bash
Skopiuj kod
terraform init
terraform apply
Ensure your Terraform configuration includes resources for S3, Lambda, Transcribe, and API Gateway.

Manual Setup

Create S3 Bucket: Create an S3 bucket to store audio files and transcription results.
Create Lambda Functions: Deploy Lambda functions for handling transcription and insight extraction.
Create API Gateway: Set up an API Gateway to expose the Lambda functions via HTTP endpoints.
Integrate Lambda with API Gateway: Configure API Gateway to trigger Lambda functions on HTTP requests.
Configure Environment Variables

Create a .env file in the root directory with the following variables:

env
Skopiuj kod
AWS_REGION=us-east-1
AWS_S3_BUCKETNAME_MINISEDRIC=your-bucket-name
AWS_ENDPOINT_URL=http://localhost.localstack.cloud:4566
API_GATEWAY_ENDPOINT=https://your-api-id.execute-api.your-region.amazonaws.com/prod
Adjust the values based on your setup.

Usage
Upload an MP3 File

Upload your MP3 files to the specified S3 bucket using the AWS CLI or the AWS Management Console.

bash
Skopiuj kod
aws s3 cp path/to/your/file.mp3 s3://your-bucket-name/
Invoke the API

Make a POST request to the API endpoint with a JSON payload:

json
Skopiuj kod
{
  "interaction_url": "s3://your-bucket-name/file.mp3",
  "trackers": ["value1", "value2"]
}
API Endpoint: https://your-api-id.execute-api.your-region.amazonaws.com/prod

Example Request Using curl:

bash
Skopiuj kod
curl -X POST $API_GATEWAY_ENDPOINT -H "Content-Type: application/json" -d '{
  "interaction_url": "s3://your-bucket-name/file.mp3",
  "trackers": ["value1", "value2"]
}'
Check the Response

The response will contain the extracted insights:

json
Skopiuj kod
{
  "insights": [
    {
      "sentence_index": 4,
      "start_word_index": 5,
      "end_word_index": 7,
      "tracker_value": "How are you doing today Sir?",
      "transcribe_value": "How are you feeling?"
    }
    // More insights...
  ]
}
Code Quality
Linting: The project uses flake8 for code linting. Run the linter with:

bash
Skopiuj kod
flake8 src/
Type Checking: The project uses mypy for type checking. Run the type checker with:

bash
Skopiuj kod
mypy src/
Future Enhancements
NLP Integration: Replace regex-based insight extraction with Spacy's NLP models for more advanced text analysis.
Error Handling: Improve error handling and validation in the Lambda functions.
Contributing
Feel free to open issues or submit pull requests. Contributions are welcome!

License
This project is licensed under the MIT License. See the LICENSE file for details.