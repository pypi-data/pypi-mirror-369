# ironbook/client.py
import httpx
import json
from typing import Dict, Any, Optional
from .types import (
    RegisterAgentOptions, 
    GetAuthTokenOptions, 
    PolicyDecision, 
    PolicyInput,
    UploadPolicyOptions,
    UpdateAgentOptions,
    UpdateAgentResponse
)

class IronBookError(Exception):
    """IronBook SDK error with structured fields."""
    def __init__(self, message: str, *, status: int, code: Optional[str] = None, request_id: Optional[str] = None, details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.status = status
        self.code = code
        self.request_id = request_id
        self.details = details

class IronBookClient:
    """IronBook Trust Service client"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.ironbook.identitymachines.com", timeout: float = 10.0):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=httpx.Timeout(timeout))
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get common headers for API requests"""
        return {
            'Content-Type': 'application/json',
            'x-ironbook-key': self.api_key
        }

    async def _request(self, method: str, path: str, *, json_body: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        req_headers = self._get_headers()
        if headers:
            req_headers.update(headers)
        try:
            resp = await self.client.request(method, url, headers=req_headers, json=json_body)
            ct = resp.headers.get('content-type', '')
            is_json = 'json' in ct
            if resp.is_success:
                return resp.json() if is_json else { 'data': resp.text }
            # Build structured error
            body: Any = None
            if is_json:
                try:
                    body = resp.json()
                except json.JSONDecodeError:
                    body = None
            else:
                body = resp.text
            title = body.get('title') if isinstance(body, dict) else None
            fallback = (body.get('error') or body.get('message')) if isinstance(body, dict) else None
            code = body.get('code') or body.get('type') if isinstance(body, dict) else None
            request_id = body.get('requestId') if isinstance(body, dict) else None
            message = title or fallback or f"HTTP {resp.status_code}"
            raise IronBookError(message, status=resp.status_code, code=code, request_id=request_id, details=body)
        except httpx.TimeoutException as e:
            raise IronBookError("Request timed out", status=408, code="REQUEST_TIMEOUT") from e
        except httpx.RequestError as e:
            raise IronBookError(f"Network error: {e}", status=0) from e
        except json.JSONDecodeError as e:
            # successful response but not valid JSON
            raise IronBookError(f"Invalid JSON response: {e}", status=200) from e
    
    async def register_agent(self, opts: RegisterAgentOptions) -> Dict[str, Any]:
        """
        Registers a new agent with the Iron Book Trust Service
        
        Args:
            opts: Registration options including agent name, capabilities, and developer DID
            
        Returns:
            Dict[str, Any]: Response containing vc (Verifiable Credential as a compact-format signed JWT string for this agent), agentDid, and developerDid
            
        Raises:
            IronBookError: If registration fails
        """
        payload = {
            'agentName': opts.agent_name,
            'capabilities': opts.capabilities,
            'developerDID': opts.developer_did
        }
        return await self._request('POST', '/agents/register', json_body=payload)
    
    async def get_auth_token(self, opts: GetAuthTokenOptions) -> Dict[str, Any]:
        """
        Gets a short-lived one-shot JIT access token for the agent to perform an action
        
        Args:
            opts: Authentication options including agent DID, developer DID, VC, and audience
            
        Returns:
            Dict[str, Any]: Response containing access_token and expires_in
            
        Raises:
            IronBookError: If authentication fails
        """
        payload = {
            'agentDid': opts.agent_did,
            'developerDid': opts.developer_did,
            'vc': opts.vc,
            'audience': opts.audience
        }
        return await self._request('POST', '/auth/token', json_body=payload)
    
    async def policy_decision(self, opts: PolicyInput) -> PolicyDecision:
        """
        Gets a policy decision from the Iron Book Trust Service and consumes the one-shot JIT access token
        
        Args:
            opts: Policy decision input including agent DID, token, action, resource, and context
            
        Returns:
            PolicyDecision: Policy decision result with allow/deny and additional details
            
        Raises:
            IronBookError: If policy decision fails
        """
        headers = {'Authorization': f'Bearer {opts.token}'}
        payload = {
            'agentDid': opts.agent_did,  # agent DID
            'policyId': opts.policy_id,   # policy ID
            'action': opts.action,  # e.g. "query"
            'resource': opts.resource,  # e.g. "db://finance/tx"
            'context': opts.context or {}  # optional: amount, ticker, etc.
        }
        data = await self._request('POST', '/policy/decision', json_body=payload, headers=headers)
        return PolicyDecision(
            allow=data.get('allow', False),
            evaluation=data.get('evaluation'),
            reason=data.get('reason')
        )

    async def upload_policy(self, opts: UploadPolicyOptions) -> Dict[str, Any]:
        """
        Uploads a new access control policy to the Iron Book Trust Service
        
        Args:
            opts: Policy upload options including developer DID,
                config type, policy content, metadata, and API key
            
        Returns:
            Response from the policy upload endpoint
            
        Raises:
            IronBookError: If the upload fails
        """
        payload = {
            'developerDid': opts.developer_did,
            'configType': opts.config_type,
            'policyContent': opts.policy_content,
            'metadata': opts.metadata
        }
        return await self._request('POST', '/policies', json_body=payload)

    async def update_agent(self, agent_did: str, opts: UpdateAgentOptions) -> UpdateAgentResponse:
        """
        Updates an agent's description and/or status
        
        Args:
            agent_did: The DID of the agent to update
            opts: Update options including description and/or status
            
        Returns:
            UpdateAgentResponse: Response containing agent DID, developer DID, and updated fields
            
        Raises:
            IronBookError: If update fails
        """
        # Build request body with only provided fields
        request_body: Dict[str, Any] = {}
        if opts.description is not None:
            request_body['description'] = opts.description
        if opts.status is not None:
            request_body['status'] = opts.status
        if not request_body:
            raise IronBookError("At least one of description or status must be provided", status=400, code="VALIDATION_ERROR")

        data = await self._request('PUT', f"/agents/{agent_did}", json_body=request_body)
        return UpdateAgentResponse(
            agent_did=data.get('agentDid'),
            developer_did=data.get('developerDid'),
            updated=data.get('updated', [])
        )

# Convenience functions for backward compatibility and simpler usage
async def register_agent(opts: RegisterAgentOptions, api_key: str, base_url: str = "https://dev.identitymachines.com") -> Dict[str, Any]:
    """Convenience function for registering an agent"""
    async with IronBookClient(api_key, base_url) as client:
        return await client.register_agent(opts)

async def get_auth_token(opts: GetAuthTokenOptions, api_key: str, base_url: str = "https://dev.identitymachines.com") -> Dict[str, Any]:
    """Convenience function for getting one-shot JIT authentication token"""
    async with IronBookClient(api_key, base_url) as client:
        return await client.get_auth_token(opts)

async def policy_decision(opts: PolicyInput, api_key: str, base_url: str = "https://dev.identitymachines.com") -> PolicyDecision:
    """Convenience function for getting policy decision"""
    async with IronBookClient(api_key, base_url) as client:
        return await client.policy_decision(opts)

async def upload_policy(opts: UploadPolicyOptions, api_key: str, base_url: str = "https://dev.identitymachines.com") -> Dict[str, Any]:
    """Convenience function for uploading a new policy"""
    async with IronBookClient(api_key, base_url) as client:
        return await client.upload_policy(opts)

async def update_agent(agent_did: str, opts: UpdateAgentOptions, api_key: str, base_url: str = "https://dev.identitymachines.com") -> UpdateAgentResponse:
    """Convenience function for updating an agent"""
    async with IronBookClient(api_key, base_url) as client:
        return await client.update_agent(agent_did, opts)