"""Automated creation and discovery script for AWS AgentCore Memory resources.

Attempts to provision or locate Bedrock AgentCore Memory and update .env.local.
"""

import os
import sys
import re
from pathlib import Path
from dotenv import dotenv_values
import boto3
from botocore.exceptions import ClientError

def update_env_local(key: str, value: str, env_path: Path):
    if not env_path.exists():
        return
    content = env_path.read_text(encoding="utf-8")
    pattern = rf"^{key}=.*$"
    new_line = f"{key}={value}"
    if re.search(pattern, content, flags=re.MULTILINE):
        content = re.sub(pattern, new_line, content, flags=re.MULTILINE)
    else:
        content += f"\n{new_line}"
    env_path.write_text(content, encoding="utf-8")
    print(f"  -> Updated {key}={value} in {env_path.name}")

def main():
    root = Path(__file__).resolve().parent.parent
    env_path = root / ".env.local"
    if not env_path.exists():
        print("[ERROR] .env.local not found.")
        sys.exit(1)

    cfg = dotenv_values(env_path)
    access_key = cfg.get("AWS_ACCESS_KEY_ID")
    secret_key = cfg.get("AWS_SECRET_ACCESS_KEY")
    region = cfg.get("AGENTCORE_REGION") or cfg.get("AWS_REGION", "us-east-1")

    print("=" * 60)
    print("QUOIN AGENTCORE RESOURCE DISCOVERY & PROVISIONER")
    print("=" * 60)
    print(f"Target Region: {region}")

    if not access_key or not secret_key:
        print("[ERROR] Missing AWS credentials in .env.local")
        sys.exit(1)

    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )

    client = session.client("bedrock-agent")

    # 1. Attempt to list agents or memory
    try:
        print("\nChecking for existing Bedrock Agents...")
        agents = client.list_agents(maxResults=10)
        summaries = agents.get("agentSummaries", [])
        if summaries:
            target_agent = summaries[0]
            agent_id = target_agent["agentId"]
            agent_arn = target_agent.get("agentArn", f"arn:aws:bedrock:{region}:{session.client('sts').get_caller_identity()['Account']}:agent/{agent_id}")
            print(f"  -> Found active agent: {target_agent.get('agentName')} ({agent_id})")
            update_env_local("AGENTCORE_RUNTIME_ARN", agent_arn, env_path)
        else:
            print("  -> No existing agents found in region.")
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code")
        print(f"  -> [ACCESS RESTRICTED] bedrock-agent:list_agents failed with {code}: {e.response.get('Error', {}).get('Message')}")

    # 2. Check Bedrock Memory Creation
    try:
        print("\nChecking Bedrock Memory capabilities...")
        # Check if client has create_memory or memory API
        if hasattr(client, "create_memory"):
            res = client.create_memory(
                name="quoin-authority-memory",
                description="QUOIN Policy Generation Memory Store"
            )
            memory_id = res.get("memoryId")
            print(f"  -> Provisioned Bedrock Memory: {memory_id}")
            update_env_local("AGENTCORE_MEMORY_ID", memory_id, env_path)
        else:
            print("  -> Bedrock client does not expose direct create_memory; use Console Memory ID or Agent Alias.")
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code")
        print(f"  -> [ACCESS RESTRICTED] Bedrock memory operation failed with {code}: {e.response.get('Error', {}).get('Message')}")

    print("\n" + "=" * 60)
    print("Provisioning check complete.")
    print("=" * 60)

if __name__ == "__main__":
    main()
