"""Data models for AI Spine SDK."""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime

from ai_spine.utils import parse_datetime


@dataclass
class Flow:
    """Represents an AI Spine flow.
    
    Attributes:
        flow_id: Unique flow identifier
        name: Flow name
        description: Flow description
        nodes: List of flow nodes
        metadata: Optional metadata
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    flow_id: str
    name: str
    description: str
    nodes: List[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Flow":
        """Create Flow instance from dictionary.
        
        Args:
            data: Dictionary containing flow data
            
        Returns:
            Flow instance
        """
        return cls(
            flow_id=data["flow_id"],
            name=data["name"],
            description=data.get("description", ""),
            nodes=data.get("nodes", []),
            metadata=data.get("metadata"),
            created_at=parse_datetime(data.get("created_at")),
            updated_at=parse_datetime(data.get("updated_at")),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Flow to dictionary.
        
        Returns:
            Dictionary representation of Flow
        """
        data = {
            "flow_id": self.flow_id,
            "name": self.name,
            "description": self.description,
            "nodes": self.nodes,
        }
        
        if self.metadata:
            data["metadata"] = self.metadata
        if self.created_at:
            data["created_at"] = self.created_at.isoformat()
        if self.updated_at:
            data["updated_at"] = self.updated_at.isoformat()
        
        return data


@dataclass
class Execution:
    """Represents a flow execution.
    
    Attributes:
        execution_id: Unique execution identifier
        flow_id: Associated flow identifier
        status: Execution status (pending, running, completed, failed, cancelled)
        input_data: Input data for execution
        output_data: Output data from execution
        error_message: Error message if failed
        metadata: Optional metadata
        created_at: Creation timestamp
        updated_at: Last update timestamp
        completed_at: Completion timestamp
    """
    execution_id: str
    flow_id: str
    status: str
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Execution":
        """Create Execution instance from dictionary.
        
        Args:
            data: Dictionary containing execution data
            
        Returns:
            Execution instance
        """
        return cls(
            execution_id=data["execution_id"],
            flow_id=data["flow_id"],
            status=data["status"],
            input_data=data.get("input_data", {}),
            output_data=data.get("output_data"),
            error_message=data.get("error_message"),
            metadata=data.get("metadata"),
            created_at=parse_datetime(data.get("created_at")),
            updated_at=parse_datetime(data.get("updated_at")),
            completed_at=parse_datetime(data.get("completed_at")),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Execution to dictionary.
        
        Returns:
            Dictionary representation of Execution
        """
        data = {
            "execution_id": self.execution_id,
            "flow_id": self.flow_id,
            "status": self.status,
            "input_data": self.input_data,
        }
        
        if self.output_data is not None:
            data["output_data"] = self.output_data
        if self.error_message:
            data["error_message"] = self.error_message
        if self.metadata:
            data["metadata"] = self.metadata
        if self.created_at:
            data["created_at"] = self.created_at.isoformat()
        if self.updated_at:
            data["updated_at"] = self.updated_at.isoformat()
        if self.completed_at:
            data["completed_at"] = self.completed_at.isoformat()
        
        return data
    
    @property
    def is_terminal(self) -> bool:
        """Check if execution is in terminal state.
        
        Returns:
            True if execution is completed, failed, or cancelled
        """
        return self.status in ["completed", "failed", "cancelled"]
    
    @property
    def is_successful(self) -> bool:
        """Check if execution completed successfully.
        
        Returns:
            True if execution status is completed
        """
        return self.status == "completed"
    
    @property
    def is_failed(self) -> bool:
        """Check if execution failed.
        
        Returns:
            True if execution status is failed
        """
        return self.status == "failed"


@dataclass
class Agent:
    """Represents an AI agent.
    
    Attributes:
        agent_id: Unique agent identifier
        name: Agent name
        type: Agent type
        configuration: Agent configuration
        metadata: Optional metadata
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    agent_id: str
    name: str
    type: str
    configuration: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Agent":
        """Create Agent instance from dictionary.
        
        Args:
            data: Dictionary containing agent data
            
        Returns:
            Agent instance
        """
        return cls(
            agent_id=data["agent_id"],
            name=data["name"],
            type=data["type"],
            configuration=data.get("configuration", {}),
            metadata=data.get("metadata"),
            created_at=parse_datetime(data.get("created_at")),
            updated_at=parse_datetime(data.get("updated_at")),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Agent to dictionary.
        
        Returns:
            Dictionary representation of Agent
        """
        data = {
            "agent_id": self.agent_id,
            "name": self.name,
            "type": self.type,
            "configuration": self.configuration,
        }
        
        if self.metadata:
            data["metadata"] = self.metadata
        if self.created_at:
            data["created_at"] = self.created_at.isoformat()
        if self.updated_at:
            data["updated_at"] = self.updated_at.isoformat()
        
        return data


@dataclass
class HealthStatus:
    """Represents API health status.
    
    Attributes:
        status: Health status (healthy, unhealthy)
        version: API version
        timestamp: Status timestamp
        checks: Individual health checks
    """
    status: str
    version: Optional[str] = None
    timestamp: Optional[datetime] = None
    checks: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HealthStatus":
        """Create HealthStatus instance from dictionary.
        
        Args:
            data: Dictionary containing health data
            
        Returns:
            HealthStatus instance
        """
        return cls(
            status=data.get("status", "unknown"),
            version=data.get("version"),
            timestamp=parse_datetime(data.get("timestamp")),
            checks=data.get("checks", {}),
        )
    
    @property
    def is_healthy(self) -> bool:
        """Check if API is healthy.
        
        Returns:
            True if status is healthy
        """
        return self.status.lower() in ["healthy", "ok", "up"]


@dataclass
class Metrics:
    """Represents system metrics.
    
    Attributes:
        timestamp: Metrics timestamp
        executions_total: Total number of executions
        executions_active: Number of active executions
        flows_total: Total number of flows
        agents_total: Total number of agents
        custom_metrics: Additional custom metrics
    """
    timestamp: Optional[datetime] = None
    executions_total: Optional[int] = None
    executions_active: Optional[int] = None
    flows_total: Optional[int] = None
    agents_total: Optional[int] = None
    custom_metrics: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Metrics":
        """Create Metrics instance from dictionary.
        
        Args:
            data: Dictionary containing metrics data
            
        Returns:
            Metrics instance
        """
        # Extract known metrics
        known_metrics = {
            "timestamp": parse_datetime(data.get("timestamp")),
            "executions_total": data.get("executions_total"),
            "executions_active": data.get("executions_active"),
            "flows_total": data.get("flows_total"),
            "agents_total": data.get("agents_total"),
        }
        
        # All other fields go to custom_metrics
        custom_metrics = {
            k: v for k, v in data.items()
            if k not in known_metrics
        }
        
        return cls(
            **{k: v for k, v in known_metrics.items() if v is not None},
            custom_metrics=custom_metrics
        )