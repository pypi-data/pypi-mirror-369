"""
Data models for ZKAuth SDK
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class User(BaseModel):
    """User model"""
    id: str
    email: str
    created_at: datetime
    last_login: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AuthResult(BaseModel):
    """Authentication result model"""
    success: bool
    user: Optional[User] = None
    token: Optional[str] = None
    error: Optional[str] = None
    requires_device_verification: bool = False


class DeviceInfo(BaseModel):
    """Device information model"""
    fingerprint: str
    timestamp: int
    platform: str
    python_version: str
    hostname: str
    hardware_info: Dict[str, Any] = Field(default_factory=dict)


class SessionInfo(BaseModel):
    """Session information model"""
    id: str
    user_id: str
    expires_at: datetime
    is_active: bool
    device_fingerprint: Optional[str] = None


class ZKProof(BaseModel):
    """Zero-knowledge proof model"""
    pi_a: List[str]
    pi_b: List[List[str]]
    pi_c: List[str]
    protocol: str = "groth16"
    curve: str = "bn128"


class ProofData(BaseModel):
    """Proof data container"""
    proof: ZKProof
    public_signals: List[str]


class ProofInput(BaseModel):
    """Input data for proof generation"""
    password: str
    salt: str
    commitment: str


class SignUpData(BaseModel):
    """Sign up data with ZKP format"""
    email: str
    password: str
    cognitive_question: str
    cognitive_answer: str
    metadata: Optional[Dict[str, Any]] = None


class SignInData(BaseModel):
    """Sign in data"""
    email: str
    password: str
