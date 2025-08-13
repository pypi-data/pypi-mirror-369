from .client import IronBookClient
from .types import (
    RegisterAgentOptions,
    GetAuthTokenOptions,
    PolicyDecision,
    PolicyDecisionResult,
    AuthAssertionParams,
    PolicyInput,
    BuildAgentPayloadOptions,
    AgentPayload,
    UploadPolicyOptions,
    UpdateAgentOptions,
    UpdateAgentResponse,
)

__version__ = "0.2.0"
__all__ = [
    "IronBookClient",
    "RegisterAgentOptions",
    "GetAuthTokenOptions", 
    "PolicyDecision",
    "PolicyDecisionResult",
    "AuthAssertionParams",
    "PolicyInput",
    "BuildAgentPayloadOptions",
    "AgentPayload",
    "UploadPolicyOptions",
    "UpdateAgentOptions",
    "UpdateAgentResponse",
]