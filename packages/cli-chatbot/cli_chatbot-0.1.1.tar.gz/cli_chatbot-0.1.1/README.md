# ai-chat

A Python project for generating and using S3 presigned URLs with a chat interface powered by AWS Bedrock and Claude. This project includes:

- **S3 presigned URL generation** for secure upload/download operations
- **File upload/download** using presigned URLs
- **MCP (Model Context Protocol) server** for tool integration
- **Chat client** that interacts with Claude via LiteLLM and AWS Bedrock
- **AWS integration** for both S3 operations and AI model access

## Features

- Generate presigned URLs for S3 bucket operations
- Upload and download files securely using presigned URLs
- Interactive chat interface with AI assistance
- Tool calling capabilities through MCP protocol
- Support for both direct Anthropic API and AWS Bedrock

## Requirements

- Python 3.12+
- AWS account with appropriate permissions for:
  - S3 bucket access
  - AWS Bedrock model access (for Claude models)
- AWS credentials configured

## Installation

### Using pip with requirements.txt:
```bash
pip install -r requirements.txt
```

### Using pyproject.toml:
```bash
pip install .
```

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# AWS Credentials for S3 and Bedrock
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_SESSION_TOKEN=your-aws-session-token  # Optional for temporary credentials
AWS_DEFAULT_REGION=us-east-1

# LiteLLM Configuration for AWS Bedrock
LITELLM_LOG=INFO
AWS_REGION_NAME=us-east-1

# Optional: Anthropic API Key (if using direct API instead of Bedrock)
ANTHROPIC_API_KEY=your-anthropic-api-key
```

### AWS Permissions

Ensure your AWS credentials have the following permissions:

**For S3 operations:**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:GeneratePresignedUrl"
            ],
            "Resource": "arn:aws:s3:::your-bucket-name/*"
        }
    ]
}
```

**For AWS Bedrock:**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel"
            ],
            "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.claude-*"
        }
    ]
}
```

## Usage

### 1. Start the MCP Server

The presigned_url.py script can function as both a library and an MCP server:

```bash
python presigned_url.py --mcp-server
```

### 2. Run the Chat Client

Start the interactive chat client that connects to the MCP server:

```bash
python client.py presigned_url.py --mcp-server
```

### 3. Using the Tools

Once the chat client is running, you can use natural language to:

- Generate presigned URLs: "Create a presigned URL for uploading to bucket 'my-bucket' with key 'file.txt'"
- Upload files: "Upload 'local-file.txt' to the presigned URL"
- Download files: "Download from the presigned URL and save as 'downloaded-file.txt'"

## Model Configuration

### Using AWS Bedrock (Recommended)

To use Claude models through AWS Bedrock, update the model name in `client.py`:

```python
# Replace this line in client.py
model="claude-3-5-sonnet-20241022"

# With this for Bedrock
model="bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0"
```

### Using Direct Anthropic API

If you prefer to use the direct Anthropic API, ensure you have set the `ANTHROPIC_API_KEY` in your `.env` file and use the standard model names.

## Project Structure

```
ai-chat/
├── client.py                 # Interactive chat client
├── presigned_url.py          # Merged S3 utilities and MCP server
├── app.py                    # Additional application logic
├── requirements.txt          # Python dependencies
├── pyproject.toml           # Project configuration
├── .env                     # Environment variables (create this)
└── README.md                # This file
```

## Troubleshooting

### Common Issues

1. **AWS Credentials Error**: Ensure your AWS credentials are correctly set in the `.env` file and have the necessary permissions.

2. **Bedrock Access Denied**: Make sure you have enabled the Claude models in your AWS Bedrock console and have the appropriate IAM permissions.

3. **S3 Bucket Access**: Verify that your AWS credentials have access to the S3 bucket you're trying to use.

4. **Region Mismatch**: Ensure the AWS region in your `.env` file matches where your resources are located.

## License

MIT
