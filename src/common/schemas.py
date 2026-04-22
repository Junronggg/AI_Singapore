from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ProcessedTelemetryMessage(BaseModel):
    timestamp: datetime
    split: str
    values: Dict[str, float]
    label: Optional[int] = None


class AnomalyResultMessage(BaseModel):
    timestamp: datetime
    split: str
    anomaly_score: float
    is_anomaly: bool
    label: Optional[int] = None
    top_contributing_features: List[str] = Field(default_factory=list)


class IncidentSummaryMessage(BaseModel):
    incident_id: str
    timestamp: datetime
    severity: str
    summary: str
    affected_features: List[str] = Field(default_factory=list)
    recommendation: Optional[str] = None


class DashboardResponseMessage(BaseModel):
    timestamp: datetime
    system_status: str
    anomaly_score: Optional[float] = None
    risk_level: Optional[str] = None
    affected_components: List[str] = Field(default_factory=list)
    recommendation: Optional[str] = None