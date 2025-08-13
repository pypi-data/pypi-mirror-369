from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

class PolicyDecisionResult(str, Enum):
    """Policy decision result enumeration"""
    ALLOW = "allow"
    DENY = "deny"

@dataclass
class RegisterAgentOptions:
    """Options for registering a new agent"""
    agent_name: str
    capabilities: List[str]
    developer_did: Optional[str] = None

@dataclass
class AuthAssertionParams:
    """Parameters for agent authentication assertion"""
    agent_did: str
    vc: str  # Verifiable Credential for this agent
    audience: str  # e.g. https://api.identitymachines.com
    developer_did: Optional[str] = None

@dataclass
class GetAuthTokenOptions:
    """Options for getting authentication token"""
    agent_did: str
    vc: str
    audience: str
    developer_did: Optional[str] = None

@dataclass
class PolicyInput:
    """Input parameters for policy decision"""
    agent_did: str  # agent DID (subject)
    policy_id: str  # specific policy ID to use
    token: str  # short-lived access token (JWT)
    action: str  # e.g. "query"
    resource: str  # e.g. "db://finance/tx"
    context: Optional[Dict[str, Any]] = None  # optional: amount, ticker, etc.

@dataclass
class PolicyDecision:
    """Result of a policy decision"""
    allow: bool
    evaluation: Optional[List[Any]] = None
    reason: Optional[str] = None

@dataclass
class BuildAgentPayloadOptions:
    """Options for building agent payload"""
    agent_name: str
    capabilities: List[str]
    developer_did: str  # DID identifying the agent's owner/issuer

@dataclass
class AgentPayload:
    """Structure sent to Iron Book API and returned to caller"""
    agent_did: str  # did:web:...
    developer_did: str  # did:web:...
    vc: str  # detached JWS VC (compact)
    public_jwk: Dict[str, Any]  # to persist in agent registry for auth token verification
    private_jwk: Dict[str, Any]  # returned for caller to securely store

@dataclass
class UploadPolicyOptions:
    """Options for uploading a policy"""
    config_type: str
    policy_content: str
    metadata: Any
    developer_did: Optional[str] = None

@dataclass
class UpdateAgentOptions:
    """Options for updating an agent"""
    description: Optional[str] = None
    status: Optional[str] = None  # 'active' or 'inactive'

@dataclass
class UpdateAgentResponse:
    """Response from updating an agent"""
    agent_did: str
    developer_did: str
    updated: List[str]  # List of updated field names

# Type aliases for backward compatibility and convenience
RegisterAgentOptions = RegisterAgentOptions
GetAuthTokenOptions = GetAuthTokenOptions
PolicyDecision = PolicyDecision