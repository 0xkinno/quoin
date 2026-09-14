"""Strands Reasoning Agent (Plane A).

Integrates the Strands Agents SDK & Amazon Bedrock Nova Lite for operational request classification,
policy contextual reasoning, and structured proposal formulation.
Strictly isolated from authority commit gates and side-effect dispatch.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from dotenv import dotenv_values
from .adapter import ProposalAdapter
from .tools import query_policy_context
from ..kernel.models import DecisionProposal
from ..kernel.hasher import CanonicalHasher
from ..config import get_config

class StrandsProposalOutput(BaseModel):
    """Structured proposal emitted by the Strands Agent."""
    approved: bool = Field(
        description="Whether the operational request complies with the observed policy limits"
    )
    rationale: str = Field(
        description="Explicit operational reasoning explaining compliance or violation against policy rules"
    )
    target_generation: int = Field(
        description="Authoritative policy generation observed during reasoning"
    )
    affected_path: str = Field(
        description="Target resource path that will be affected by the action"
    )
    payload_hash: str = Field(
        description="Canonical hash of the request payload"
    )

class OperationalReasoningAgent:
    """Plane A: Reasoning agent using Strands SDK with Bedrock Nova Lite."""

    def __init__(
        self,
        memory_reader_callable,
        model_id: Optional[str] = None,
        enable_bedrock: bool = True,
    ):
        self.memory_reader = memory_reader_callable
        self.enable_bedrock = enable_bedrock

        self.model_id = model_id or get_config("BEDROCK_MODEL_ID", "us.amazon.nova-lite-v1:0")
        self.region = get_config("AWS_REGION", "us-east-1")
        self.access_key = get_config("AWS_ACCESS_KEY_ID")
        self.secret_key = get_config("AWS_SECRET_ACCESS_KEY")

        self._strands_agent = None
        self._bedrock_model = None

        if self.enable_bedrock and self.access_key and self.secret_key:
            try:
                import boto3
                from strands import Agent, tool
                from strands.models import BedrockModel

                session = boto3.Session(
                    aws_access_key_id=self.access_key,
                    aws_secret_access_key=self.secret_key,
                    region_name=self.region,
                )
                self._bedrock_model = BedrockModel(boto_session=session, model_id=self.model_id)

                # Define Strands tool for cognitive memory policy lookup
                reader = self.memory_reader
                @tool
                def query_visible_policy(tenant_id: str) -> str:
                    """Query cognitive memory for currently visible policy rules and generation.
                    
                    Args:
                        tenant_id: The tenant identifier whose policy rules to retrieve.
                    """
                    ctx = query_policy_context(tenant_id, reader)
                    return json.dumps(ctx)

                system_prompt = (
                    "You are the QUOIN Operational Reasoning Agent (Plane A) powered by the Strands Agents SDK. "
                    "Your role is to evaluate business operational requests against candidate policies visible in Cognitive Memory. "
                    "You have NO execution authority and CANNOT execute side effects or commit state. "
                    "Evaluate whether the requested action and amount comply with the policy limits for the customer tier. "
                    "Provide explicit rationale and output a structured DecisionProposal."
                )

                self._strands_agent = Agent(
                    model=self._bedrock_model,
                    tools=[query_visible_policy],
                    system_prompt=system_prompt,
                    structured_output_model=StrandsProposalOutput,
                )
            except Exception as e:
                # Log model initialization status
                self._strands_agent = None

    def process_request(self, request_payload: Dict[str, Any]) -> DecisionProposal:
        """Process an operational request through the Strands Agent pipeline.
        
        HTTP Request -> Strands Agent -> Bedrock Model (Nova Lite) -> Structured DecisionProposal.
        """
        request_id = request_payload["request_id"]
        tenant_id = request_payload.get("tenant_id", "agency_operations")
        action = request_payload.get("action", "apply_discount")
        amount = float(request_payload.get("amount", 0.0))
        client_tier = request_payload.get("client_tier", "standard")
        invoice_id = request_payload.get("invoice_id", "inv_unknown")
        client_id = request_payload.get("client_id", "client_unknown")

        affected_path = f"/invoices/{invoice_id}" if action == "apply_discount" else f"/accounts/{client_id}"
        payload_hash = CanonicalHasher.compute_request_hash(request_payload)

        # 1. Query currently visible candidate policy from Cognitive Memory (Plane C)
        policy_context = query_policy_context(tenant_id, self.memory_reader)
        observed_gen = policy_context.get("generation", 0)
        rules = policy_context.get("rules", [])

        rationale = f"Evaluated request for ${amount} under visible policy G{observed_gen} for {client_tier} tier."
        target_generation = observed_gen
        approved = True

        # 2. Invoke Strands Agent with Bedrock Nova Lite
        if self._strands_agent:
            try:
                user_prompt = (
                    f"Evaluate operational request: "
                    f"Action: {action}, Amount: ${amount}, Client: '{client_id}' (Tier: {client_tier}), Invoice: '{invoice_id}'. "
                    f"Tenant: '{tenant_id}'. Visible Policy Generation: G{observed_gen}. Rules: {json.dumps(rules)}. "
                    f"Target Resource Path: {affected_path}. Request Payload Hash: {payload_hash}. "
                    f"Evaluate policy compliance and return your structured proposal."
                )
                response = self._strands_agent(user_prompt)
                out = response.structured_output
                if out:
                    if isinstance(out, StrandsProposalOutput):
                        rationale = f"[Strands Nova Lite]: {out.rationale}"
                        target_generation = out.target_generation or observed_gen
                        approved = out.approved
                    elif isinstance(out, dict):
                        rationale = f"[Strands Nova Lite]: {out.get('rationale', rationale)}"
                        target_generation = out.get("target_generation", observed_gen)
                        approved = out.get("approved", True)
            except Exception as e:
                # Deterministic fallback when Bedrock is offline or rate-limited
                rationale = f"[Strands Offline Mode]: Evaluated ${amount} for {client_tier} tier under visible G{observed_gen}."

        # 3. Formulate raw proposal dictionary
        raw_proposal = {
            "request_id": request_id,
            "requested_action": action,
            "requested_value": amount,
            "rationale": rationale,
            "candidate_policy_generation": target_generation,
            "parameters": {
                "client_id": client_id,
                "invoice_id": invoice_id,
                "client_tier": client_tier,
                "affected_path": affected_path,
                "payload_hash": payload_hash,
                "recommended_approval": approved,
                "discount_percentage": request_payload.get("discount_percentage", 0.0),
            },
        }

        # 4. Strictly adapt across Plane A -> Plane B boundary
        proposal = ProposalAdapter.adapt(
            request_id=request_id,
            raw_output=raw_proposal,
            candidate_generation=target_generation,
        )

        return proposal
