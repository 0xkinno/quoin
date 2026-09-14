import os
import sys
import json
from pathlib import Path
from dotenv import dotenv_values
import boto3
from botocore.exceptions import ClientError

def test_model(bedrock_runtime, model_id):
    print(f"Testing converse on '{model_id}'...")
    try:
        response = bedrock_runtime.converse(
            modelId=model_id,
            messages=[{"role": "user", "content": [{"text": "Hello, respond with OK"}]}],
            inferenceConfig={"maxTokens": 10, "temperature": 0.0}
        )
        text = response["output"]["message"]["content"][0]["text"].strip()
        print(f"  -> SUCCESS! Response: {text}")
        return {"model": model_id, "status": "SUCCESS", "response": text}
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code")
        msg = e.response.get("Error", {}).get("Message")
        print(f"  -> ClientError ({code}): {msg}")
        return {"model": model_id, "status": "FAIL", "code": code, "error": msg}
    except Exception as e:
        print(f"  -> Error: {e}")
        return {"model": model_id, "status": "FAIL", "error": str(e)}

def main():
    env_path = Path(__file__).resolve().parent.parent / ".env.local"
    config = dotenv_values(env_path)
    aws_region = config.get("AWS_REGION", "us-east-1")
    access_key = config.get("AWS_ACCESS_KEY_ID", "")
    secret_key = config.get("AWS_SECRET_ACCESS_KEY", "")
    configured_model = config.get("BEDROCK_MODEL_ID", "amazon.nova-2-lite-v1:0")

    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=aws_region
    )

    bedrock_runtime = session.client("bedrock-runtime")

    models_to_test = [
        configured_model,
        "amazon.nova-lite-v1:0",
        "amazon.nova-micro-v1:0",
        "amazon.nova-pro-v1:0",
        "anthropic.claude-3-haiku-20240307-v1:0",
        "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    ]
    # Deduplicate while preserving order
    seen = set()
    unique_models = [m for m in models_to_test if not (m in seen or seen.add(m))]

    results = []
    for m in unique_models:
        res = test_model(bedrock_runtime, m)
        results.append(res)
        if res["status"] == "SUCCESS":
            print(f"\nFound WORKING MODEL: {m}")
            break

    # Also test IAM to see what user QUOIN-USER has permissions for
    print("\nChecking IAM permissions for QUOIN-USER...")
    iam = session.client("iam")
    try:
        policies = iam.list_attached_user_policies(UserName="QUOIN-USER")
        print(f"Attached User Policies: {policies.get('AttachedPolicies', [])}")
    except Exception as e:
        print(f"Could not list attached policies (IAM read restricted): {e}")

    try:
        inline = iam.list_user_policies(UserName="QUOIN-USER")
        print(f"Inline User Policies: {inline.get('PolicyNames', [])}")
    except Exception as e:
        print(f"Could not list inline policies: {e}")

    # Check bedrock-agent runtime
    print("\nChecking Bedrock Agent Runtime endpoints...")
    agent_runtime = session.client("bedrock-agent-runtime")
    print(f"bedrock-agent-runtime client created successfully for region {aws_region}.")

if __name__ == "__main__":
    main()
