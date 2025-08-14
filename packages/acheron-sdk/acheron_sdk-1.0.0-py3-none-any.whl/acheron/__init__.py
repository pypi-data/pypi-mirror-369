"""
Acheron AI Governance Platform - Python SDK

Comprehensive AI governance and compliance for Python applications.
Provides real-time threat detection, PII/PHI protection, and regulatory compliance.
"""

from .agent_sdk import (
    AcheronAgent,
    AcheronHealthcare,
    AcheronFinancial, 
    AcheronGeneral,
    AcheronAgentConfig,
    ProtectionResult,
    UserContext,
    AgentType,
    Regulation,
    SecurityLevel
)

from .client import (
    AcheronClient,
    AcheronConfig,
    AcheronError
)

__version__ = "1.0.0"
__author__ = "Acheron AI"
__email__ = "sdk@acheron.ai"
__description__ = "Official Python SDK for Acheron AI Governance Platform"

# Make the main classes easily accessible
__all__ = [
    # Agent Protection SDK (Primary)
    "AcheronAgent",
    "AcheronHealthcare", 
    "AcheronFinancial",
    "AcheronGeneral",
    
    # Core Client
    "AcheronClient",
    
    # Configuration Classes
    "AcheronAgentConfig",
    "AcheronConfig",
    
    # Response Types
    "ProtectionResult",
    "UserContext",
    
    # Enums
    "AgentType",
    "Regulation",
    "SecurityLevel",
    
    # Exceptions
    "AcheronError"
]

# Package metadata
__package_info__ = {
    "name": "acheron-sdk",
    "version": __version__,
    "description": __description__,
    "author": __author__,
    "author_email": __email__,
    "url": "https://github.com/acheron-ai/acheron-python-sdk",
    "license": "MIT",
    "keywords": ["ai", "governance", "compliance", "security", "hipaa", "gdpr", "pii", "phi"]
}