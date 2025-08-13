"""
AWS Lightsail Mini AI Infrastructure Stack (Simplified)
======================================================

This module extends the AWS Lightsail Mini Infrastructure Stack with basic AI preparation
for future AWS Bedrock integration.

The stack includes:
    * All features from BBAWSLightsailMiniV1a
    * S3 bucket configured for AI document storage
    * IAM roles prepared for Bedrock integration
    * Training URL processing setup
    * Configuration for future Bedrock knowledge base

:author: Generated with GitHub Copilot
:version: 1.0.0
:license: MIT
"""

import json
from constructs import Construct
from cdktf import TerraformOutput

# Import base class
from BBAWSLightsailMiniV1aStack.bb_aws_lightsail_mini_v1a import BBAWSLightsailMiniV1a, ArchitectureFlags

# AWS services
from cdktf_cdktf_provider_aws import (
    iam_role,
    iam_role_policy_attachment,
    iam_policy,
    data_aws_caller_identity,
    s3_bucket_object,
)

# Null provider for training scripts
from cdktf_cdktf_provider_null.resource import Resource as NullResource


class BBAWSLightsailMiniAIV1a(BBAWSLightsailMiniV1a):
    """
    AWS Lightsail Mini AI Infrastructure Stack (Simplified).
    
    Extends BBAWSLightsailMiniV1a with AI preparation including:
        * AI-ready S3 bucket structure
        * IAM roles prepared for future Bedrock integration
        * Training from provided URLs
        * Configuration ready for AI services
        * Placeholders for future Bedrock knowledge base
        
    :param scope: The construct scope
    :param id: The construct ID
    :param kwargs: Configuration parameters including model, training_urls, etc.
    
    Additional kwargs:
        * model: Bedrock model ID (default: "anthropic.claude-v2")
        * training_urls: List of URLs to train the model with
        * embedding_model: Embedding model for vector search (default: "amazon.titan-embed-text-v1")
        * chunk_size: Document chunk size for processing (default: 1000)
        * chunk_overlap: Chunk overlap for processing (default: 200)
    
    Example:
        >>> stack = BBAWSLightsailMiniAIV1a(
        ...     app, "my-ai-stack",
        ...     region="us-east-1",
        ...     model="anthropic.claude-3-sonnet-20240229-v1:0",
        ...     training_urls=[
        ...         "https://docs.example.com/api",
        ...         "https://blog.example.com/tutorials"
        ...     ],
        ...     embedding_model="amazon.titan-embed-text-v1"
        ... )
    """

    def __init__(self, scope, id, **kwargs):
        """
        Initialize the AWS Lightsail Mini AI Infrastructure Stack.
        
        :param scope: The construct scope
        :param id: Unique identifier for this stack
        :param kwargs: Configuration parameters including AI-specific options
        """
        # Extract AI-specific configuration
        self.model = kwargs.get("model", "anthropic.claude-v2")
        self.training_urls = kwargs.get("training_urls", [])
        self.embedding_model = kwargs.get("embedding_model", "amazon.titan-embed-text-v1")
        self.chunk_size = kwargs.get("chunk_size", 1000)
        self.chunk_overlap = kwargs.get("chunk_overlap", 200)
        
        # Initialize base class
        super().__init__(scope, id, **kwargs)
        
        # Create AI-specific resources after base infrastructure
        self._create_ai_infrastructure()

    def _create_ai_infrastructure(self):
        """Create AI-specific infrastructure components."""
        # Get current AWS account ID
        self.current_identity = data_aws_caller_identity.DataAwsCallerIdentity(
            self, "current_identity"
        )
        
        self.create_ai_ready_s3_structure()
        self.create_bedrock_iam_role()
        self.create_training_resources()
        self.create_ai_outputs()

    def create_ai_ready_s3_structure(self):
        """
        Create S3 folder structure for AI document processing.
        
        Creates organized folders for:
            * Training documents
            * Knowledge base documents  
            * Processed documents
            * AI metadata
        """
        # Create folder structure for AI documents
        ai_folders = [
            "training/",
            "documents/",
            "processed/",
            "ai-metadata/"
        ]
        
        for folder in ai_folders:
            s3_bucket_object.S3BucketObject(
                self,
                f"ai_folder_{folder.replace('/', '_').replace('-', '_')}",
                bucket=self.s3_bucket.bucket,
                key=f"{folder}.gitkeep",
                content="# AI documents folder",
                content_type="text/plain"
            )

    def create_bedrock_iam_role(self):
        """Create IAM role for future Bedrock services."""
        # Trust policy for Bedrock
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {
                    "Service": "bedrock.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }]
        }
        
        # IAM role for Bedrock
        self.bedrock_role = iam_role.IamRole(
            self,
            "bedrock_service_role",
            name=f"{self.project_name}-bedrock-role",
            assume_role_policy=json.dumps(trust_policy),
            tags={
                "Environment": self.environment,
                "Project": self.project_name,
                "Stack": self.__class__.__name__
            }
        )
        
        # S3 access policy
        s3_policy_doc = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObject",
                        "s3:ListBucket",
                        "s3:PutObject",
                        "s3:DeleteObject"
                    ],
                    "Resource": [
                        self.s3_bucket.arn,
                        f"{self.s3_bucket.arn}/*"
                    ]
                }
            ]
        }
        
        s3_policy = iam_policy.IamPolicy(
            self,
            "bedrock_s3_policy",
            name=f"{self.project_name}-bedrock-s3-policy",
            policy=json.dumps(s3_policy_doc)
        )
        
        # Bedrock access policy
        bedrock_policy_doc = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "bedrock:*",
                        "aoss:*"
                    ],
                    "Resource": "*"
                }
            ]
        }
        
        bedrock_policy = iam_policy.IamPolicy(
            self,
            "bedrock_service_policy",
            name=f"{self.project_name}-bedrock-service-policy",
            policy=json.dumps(bedrock_policy_doc)
        )
        
        # Attach policies to role
        iam_role_policy_attachment.IamRolePolicyAttachment(
            self,
            "bedrock_s3_policy_attachment",
            role=self.bedrock_role.name,
            policy_arn=s3_policy.arn
        )
        
        iam_role_policy_attachment.IamRolePolicyAttachment(
            self,
            "bedrock_service_policy_attachment",
            role=self.bedrock_role.name,
            policy_arn=bedrock_policy.arn
        )
        
        self.resources["bedrock_role"] = self.bedrock_role
        return self.bedrock_role

    def create_training_resources(self):
        """
        Create resources for training the model with provided URLs.
        
        Creates scripts to download content from training URLs and
        upload them to S3 for future processing by AI services.
        """
        if not self.training_urls:
            # Create a placeholder file for future training
            s3_bucket_object.S3BucketObject(
                self,
                "training_readme",
                bucket=self.s3_bucket.bucket,
                key="training/README.md",
                content=f"""# AI Training Documents

This folder is ready for AI training documents.

## Configuration
- Model: {self.model}
- Embedding Model: {self.embedding_model}
- Chunk Size: {self.chunk_size}
- Chunk Overlap: {self.chunk_overlap}

## Usage
Upload training documents to this folder for future AI processing.
""",
                content_type="text/markdown"
            )
            return
        
        # Create training script that downloads URLs and uploads to S3
        training_commands = [
            "echo 'Starting AI model training preparation with provided URLs'",
            "mkdir -p /tmp/training_data",
        ]
        
        # Add commands to download each URL
        for i, url in enumerate(self.training_urls):
            safe_filename = f"training_doc_{i + 1}.html"
            training_commands.extend([
                f"echo 'Downloading {url}'",
                f"curl -L -o /tmp/training_data/{safe_filename} '{url}' || echo 'Failed to download {url}'",
            ])
        
        # Add commands to upload to S3
        training_commands.extend([
            f"echo 'Uploading training data to S3 bucket {self.s3_bucket.bucket}'",
            f"aws s3 sync /tmp/training_data s3://{self.s3_bucket.bucket}/training/ --region {self.region}",
            "echo 'Training data upload completed'",
            "echo 'AI training data is ready for future Bedrock integration'",
            "rm -rf /tmp/training_data",
            "echo 'AI training preparation completed'"
        ])
        
        # Create null resource for training
        NullResource(
            self,
            "ai_training_setup",
            depends_on=[self.s3_bucket],
            provisioners=[{
                "type": "local-exec",
                "command": " && ".join(training_commands),
                "on_failure": "continue"
            }]
        )

    def create_ai_outputs(self):
        """Create Terraform outputs for AI resources."""
        # AI configuration outputs
        TerraformOutput(
            self,
            "ai_model_id",
            value=self.model,
            description="Configured AI model ID"
        )
        
        TerraformOutput(
            self,
            "ai_embedding_model",
            value=self.embedding_model,
            description="Configured embedding model"
        )
        
        TerraformOutput(
            self,
            "bedrock_role_arn",
            value=self.bedrock_role.arn,
            description="IAM role ARN for Bedrock services"
        )
        
        TerraformOutput(
            self,
            "ai_s3_bucket",
            value=self.s3_bucket.bucket,
            description="S3 bucket configured for AI document storage"
        )
        
        TerraformOutput(
            self,
            "training_urls_count",
            value=len(self.training_urls),
            description="Number of URLs used for training"
        )

        # Update secrets with AI configuration
        ai_secrets = {
            "ai_model_id": self.model,
            "ai_embedding_model_id": self.embedding_model,
            "bedrock_role_arn": self.bedrock_role.arn,
            "ai_s3_bucket": self.s3_bucket.bucket,
            "aws_account_id": self.current_identity.account_id
        }
        
        # Add AI secrets to the existing secrets
        self.secrets.update(ai_secrets)

    def get_ai_config(self):
        """
        Get AI configuration for external use.
        
        Returns a dictionary with all AI-related configuration
        that can be used by other applications or services.
        """
        return {
            "model": self.model,
            "embedding_model": self.embedding_model,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "training_urls": self.training_urls,
            "s3_bucket": self.s3_bucket.bucket,
            "bedrock_role_arn": self.bedrock_role.arn,
            "aws_account_id": self.current_identity.account_id,
            "region": self.region
        }
