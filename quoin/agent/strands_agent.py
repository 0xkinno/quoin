"""Strands Reasoning Agent (Plane A).

Integrates the Strands Agents SDK & Amazon Bedrock for operational request classification,
policy contextual reasoning, and structured proposal formulation.
Strictly isolated from authority commit gates and side-effect dispatch.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import dotenv_values
from .adapter import ProposalAdapter
from .tools import query_policy_context, formulate_proposal
from ..kernel.models import DecisionProposal

class OperationalReasoningAgent:
    """Strands-powered reasoning agent formulating proposals for professional operations."""

    def __init__(self, memory_reader_callable, model_id: Optional[str] = None, enable_bedrock: bool = True):
        self.memory_reader = memory_reader_callable
        self.enable_bedrock = enable_bedrock
        
        env_path = Path(__file__).resolve().parent.parent.parent / ".env.local"
        env_cfg = dotenv_values(env_path) if env_path.exists() else {}

        self.model_id = model_id or env_cfg.get("BEDROCK_MODEL_ID", "us.amazon.nova-lite-v1:0")
        self.region = env_cfg.get("AWS_REGION", "us-east-1")
        self.access_key = env_cfg.get("AWS_ACCESS_KEY_ID")
        self.secret_key = env_cfg.get("AWS_SECRET_ACCESS_KEY")

        self._boto_runtime = None
        if self.enable_bedrock and self.access_key and self.secret_key:
            try:
                import boto3
                session = boto3.Session(
                    aws_access_key_id=self.access_key,
                    aws_secret_access_key=self.secret_key,
                    region_name=self.region,
                )
                self._boto_runtime = session.client("bedrock-runtime")
            except Exception as e:
                self._boto_runtime = None

    def process_request(self, request_payload: Dict[str, Any]) -> DecisionProposal:
        """Process an operational request with live Bedrock reasoning and produce a candidate DecisionProposal."""
        request_id = request_payload["request_id"]
        tenant_id = request_payload.get("tenant_id", "agency_operations")
        action = request_payload.get("action", "apply_discount")
        amount = float(request_payload.get("amount", 0.0))
        client_tier = request_payload.get("client_tier", "standard")
        invoice_id = request_payload.get("invoice_id", "inv_unknown")
        client_id = request_payload.get("client_id", "client_unknown")

        # Step 1: Query currently visible candidate policy from Cognitive Memory
        policy_context = query_policy_context(tenant_id, self.memory_reader)
        observed_gen = policy_context.get("generation", 0)

        # Step 2: Genuinely invoke Amazon Bedrock via Converse API
        rationale = f"Evaluated request for ${amount} under visible policy G{observed_gen}."
        llm_approved = True

        if self._boto_runtime and self.model_id:
            try:
                system_prompt = (
                    "You are the QUOIN Operational Reasoning Agent (Plane A). "
                    "You analyze business requests against visible policy rules and propose action parameters. "
                    "You have NO authority to execute or commit actions. "
                    "Respond with a single concise sentence explaining your reasoning."
                )
                user_content = (
                    f"Request: Client '{client_id}' (Tier: {client_tier}) requests ${amount} discount on Invoice {invoice_id}. "
                    f"Visible Policy Generation: G{observed_gen}. Rules: {policy_context.get('rules', [])}. "
                    f"Does this comply with the visible policy limits? State your rationale."
                )
                
                resp = self._boto_runtime.converse(
                    modelId=self.model_id,
                    messages=[{"role": "user", "content": [{"text": user_content}]}],
                    system=[{"text": system_prompt}],
                    inferenceConfig={"maxTokens": 100, "temperature": 0.0},
                )
                text = resp["output"]["message"]["content"][0]["text"].strip()
                if text:
                    rationale = f"[Bedrock Reasoning]: {text}"
            except Exception as e:
                # Log model attempt and proceed with deterministic fallback
                rationale = f"[Local Reasoning]: Evaluated ${amount} discount for {client_tier} tier under visible G{observed_gen}."

        # Step 3: Formulate structured proposal
        raw_proposal = formulate_proposal(
            request_id=request_id,
            action=action,
            amount=amount,
            rationale=rationale,
            observed_generation=observed_gen,
            client_tier=client_tier,
            additional_params={
                "client_id": client_id,
                "invoice_id": invoice_id,
                "discount_percentage": request_payload.get("discount_percentage", 0.0),
            },
        )

        # Step 4: Strictly adapt output across Plane A -> Plane B boundary
        proposal = ProposalAdapter.adapt(
            request_id=request_id,
            raw_output=raw_proposal,
            candidate_generation=observed_gen,
        )

        return proposal
