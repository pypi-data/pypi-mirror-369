from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class EvaluationResponse(BaseModel):
    """Represents the response for an evaluation from the DeepRails API."""
    eval_id: str
    evaluation_status: str
    guardrail_metrics: Optional[List[str]] = None
    model_used: Optional[str] = None
    run_mode: Optional[str] = None
    model_input: Optional[Dict[str, Any]] = None
    model_output: Optional[str] = None
    estimated_cost: Optional[float] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    nametag: Optional[str] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
    start_timestamp: Optional[datetime] = None
    completion_timestamp: Optional[datetime] = None
    error_message: Optional[str] = None
    error_timestamp: Optional[datetime] = None
    evaluation_result: Optional[Dict[str, Any]] = None
    evaluation_total_cost: Optional[float] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None

    class Config:
        extra = 'ignore'