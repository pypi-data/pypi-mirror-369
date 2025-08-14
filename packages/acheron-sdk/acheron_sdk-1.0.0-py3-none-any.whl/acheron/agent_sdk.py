"""
Acheron Agent Protection SDK
Plug-and-play security for AI agents

Simple, powerful, compliant.
"""

from typing import Dict, List, Optional, Union, Literal, Any
from dataclasses import dataclass, asdict
import asyncio
import aiohttp
import time
from enum import Enum


class AgentType(str, Enum):
    HEALTHCARE = "healthcare"
    FINANCIAL = "financial"
    GENERAL = "general"
    EDUCATION = "education"
    LEGAL = "legal"


class Regulation(str, Enum):
    GDPR = "GDPR"
    HIPAA = "HIPAA"
    CCPA = "CCPA"
    SOX = "SOX"
    PCI_DSS = "PCI_DSS"
    EU_AI_ACT = "EU_AI_ACT"
    COLORADO_AI_ACT = "COLORADO_AI_ACT"


class SecurityLevel(str, Enum):
    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
    MAXIMUM = "maximum"


@dataclass
class AcheronAgentConfig:
    """Configuration for Acheron Agent Protection"""
    api_key: str
    agent_id: str
    agent_type: AgentType
    regulations: List[Regulation]
    endpoint: str = "https://api.acheron.ai"
    security_level: SecurityLevel = SecurityLevel.STANDARD
    organization_id: Optional[str] = None


@dataclass
class UserContext:
    """User context for validation requests"""
    role: Optional[str] = None
    permissions: Optional[List[str]] = None
    session_id: Optional[str] = None
    subject_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Threat:
    """Detected security threat"""
    type: Literal["prompt_injection", "pii", "phi", "toxic", "compliance_violation"]
    severity: Literal["low", "medium", "high", "critical"]
    details: str


@dataclass
class ComplianceStatus:
    """Compliance framework status"""
    framework: str
    status: Literal["compliant", "violation", "warning"]
    details: Optional[str] = None


@dataclass
class ProtectionResult:
    """Result of security validation"""
    safe: bool
    reason: Optional[str] = None
    sanitized: Optional[str] = None
    threats: Optional[List[Threat]] = None
    compliance: Optional[List[ComplianceStatus]] = None
    audit_id: Optional[str] = None


class AcheronAgent:
    """
    Acheron Agent Protection SDK
    
    ONE LINE to protect your AI agent:
    acheron = AcheronAgent(config)
    
    TWO CALLS to secure everything:
    1. input_check = await acheron.validate_input(user_input, context)
    2. output_check = await acheron.validate_output(agent_response, context)
    """
    
    def __init__(self, config: AcheronAgentConfig):
        self.config = config
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()
    
    async def validate_input(
        self, 
        user_input: str, 
        context: Optional[UserContext] = None
    ) -> ProtectionResult:
        """Validate user input BEFORE processing"""
        try:
            session = await self._ensure_session()
            
            payload = {
                "input": user_input,
                "context": self._build_context(context)
            }
            
            async with session.post("/agent/validate-input", json=payload) as response:
                data = await response.json()
                return self._process_protection_result(data)
                
        except Exception as e:
            # Fail secure - if validation fails, block by default
            return ProtectionResult(
                safe=False,
                reason="Security validation unavailable - request blocked for safety",
                audit_id=f"error_{int(time.time())}"
            )
    
    async def validate_output(
        self, 
        agent_output: str, 
        context: Optional[UserContext] = None
    ) -> ProtectionResult:
        """Validate agent output BEFORE returning to user"""
        try:
            session = await self._ensure_session()
            
            payload = {
                "output": agent_output,
                "context": self._build_context(context)
            }
            
            async with session.post("/agent/validate-output", json=payload) as response:
                data = await response.json()
                return self._process_protection_result(data)
                
        except Exception as e:
            return ProtectionResult(
                safe=False,
                reason="Output validation unavailable - response blocked for safety",
                audit_id=f"error_{int(time.time())}"
            )
    
    async def quick_check(self, text: str) -> bool:
        """Quick security check (lightweight, for high-frequency calls)"""
        try:
            session = await self._ensure_session()
            
            payload = {
                "text": text,
                "agent_id": self.config.agent_id,
                "regulations": [reg.value for reg in self.config.regulations]
            }
            
            async with session.post("/agent/quick-check", json=payload) as response:
                data = await response.json()
                return data.get("safe", False)
                
        except Exception:
            return False  # Fail secure
    
    # Private methods (hidden from customer)
    
    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Ensure HTTP session is available"""
        if self._session is None or self._session.closed:
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "User-Agent": "Acheron-Agent-SDK-Python/1.0.0",
                "Content-Type": "application/json"
            }
            
            timeout = aiohttp.ClientTimeout(total=10)
            
            self._session = aiohttp.ClientSession(
                base_url=self.config.endpoint,
                headers=headers,
                timeout=timeout
            )
        
        return self._session
    
    def _build_context(self, context: Optional[UserContext]) -> Dict[str, Any]:
        """Build request context"""
        base_context = {
            "agent_id": self.config.agent_id,
            "agent_type": self.config.agent_type.value,
            "regulations": [reg.value for reg in self.config.regulations],
            "security_level": self.config.security_level.value,
            "organization_id": self.config.organization_id
        }
        
        if context:
            base_context.update(asdict(context))
        
        return base_context
    
    def _process_protection_result(self, data: Dict[str, Any]) -> ProtectionResult:
        """Process API response into ProtectionResult"""
        threats = []
        if "threats" in data:
            threats = [
                Threat(
                    type=t["type"],
                    severity=t["severity"],
                    details=t["details"]
                )
                for t in data["threats"]
            ]
        
        compliance = []
        if "compliance" in data:
            compliance = [
                ComplianceStatus(
                    framework=c["framework"],
                    status=c["status"],
                    details=c.get("details")
                )
                for c in data["compliance"]
            ]
        
        return ProtectionResult(
            safe=data.get("safe", False),
            reason=data.get("reason"),
            sanitized=data.get("sanitized"),
            threats=threats if threats else None,
            compliance=compliance if compliance else None,
            audit_id=data.get("audit_id")
        )


class AcheronHealthcare(AcheronAgent):
    """Pre-configured Acheron agent for healthcare applications"""
    
    def __init__(
        self, 
        api_key: str, 
        agent_id: str,
        organization_id: Optional[str] = None,
        regulations: Optional[List[Regulation]] = None,
        **kwargs
    ):
        config = AcheronAgentConfig(
            api_key=api_key,
            agent_id=agent_id,
            agent_type=AgentType.HEALTHCARE,
            regulations=regulations or [Regulation.HIPAA, Regulation.GDPR],
            organization_id=organization_id,
            **kwargs
        )
        super().__init__(config)


class AcheronFinancial(AcheronAgent):
    """Pre-configured Acheron agent for financial applications"""
    
    def __init__(
        self, 
        api_key: str, 
        agent_id: str,
        organization_id: Optional[str] = None,
        regulations: Optional[List[Regulation]] = None,
        **kwargs
    ):
        config = AcheronAgentConfig(
            api_key=api_key,
            agent_id=agent_id,
            agent_type=AgentType.FINANCIAL,
            regulations=regulations or [Regulation.SOX, Regulation.PCI_DSS, Regulation.GDPR],
            organization_id=organization_id,
            **kwargs
        )
        super().__init__(config)


class AcheronGeneral(AcheronAgent):
    """Pre-configured Acheron agent for general applications"""
    
    def __init__(
        self, 
        api_key: str, 
        agent_id: str,
        organization_id: Optional[str] = None,
        regulations: Optional[List[Regulation]] = None,
        **kwargs
    ):
        config = AcheronAgentConfig(
            api_key=api_key,
            agent_id=agent_id,
            agent_type=AgentType.GENERAL,
            regulations=regulations or [Regulation.GDPR],
            organization_id=organization_id,
            **kwargs
        )
        super().__init__(config) 