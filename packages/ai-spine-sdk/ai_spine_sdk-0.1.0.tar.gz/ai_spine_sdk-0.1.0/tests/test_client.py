"""Tests for AI Spine client."""

import pytest
import responses
import json
from ai_spine import AISpine, ValidationError, AuthenticationError, APIError


class TestClientInitialization:
    """Test client initialization."""
    
    def test_default_initialization(self):
        """Test client with default settings."""
        client = AISpine()
        assert client.base_url == "https://ai-spine-api-production.up.railway.app"
        assert client.timeout == 30
        assert client.api_key is None
        assert client.debug is False
    
    def test_custom_initialization(self):
        """Test client with custom settings."""
        client = AISpine(
            api_key="test-key",
            base_url="https://custom.ai-spine.com",
            timeout=60,
            max_retries=5,
            debug=True
        )
        assert client.api_key == "test-key"
        assert client.base_url == "https://custom.ai-spine.com"
        assert client.timeout == 60
        assert client.debug is True
    
    def test_context_manager(self):
        """Test client as context manager."""
        with AISpine() as client:
            assert client.session is not None


class TestFlowExecution:
    """Test flow execution methods."""
    
    @responses.activate
    def test_execute_flow_success(self, client, base_url):
        """Test successful flow execution."""
        responses.add(
            responses.POST,
            f"{base_url}/flows/execute",
            json={"execution_id": "exec-123", "status": "pending"},
            status=200
        )
        
        result = client.execute_flow("test-flow", {"input": "data"})
        assert result["execution_id"] == "exec-123"
        assert result["status"] == "pending"
    
    @responses.activate
    def test_execute_flow_with_metadata(self, client, base_url):
        """Test flow execution with metadata."""
        responses.add(
            responses.POST,
            f"{base_url}/flows/execute",
            json={"execution_id": "exec-123", "status": "pending"},
            status=200
        )
        
        result = client.execute_flow(
            "test-flow",
            {"input": "data"},
            metadata={"user": "test"}
        )
        assert result["execution_id"] == "exec-123"
    
    def test_execute_flow_invalid_flow_id(self, client):
        """Test flow execution with invalid flow ID."""
        with pytest.raises(ValidationError):
            client.execute_flow("", {"input": "data"})
    
    def test_execute_flow_invalid_input_data(self, client):
        """Test flow execution with invalid input data."""
        with pytest.raises(ValidationError):
            client.execute_flow("test-flow", None)
    
    @responses.activate
    def test_get_execution_success(self, client, base_url, sample_execution):
        """Test getting execution status."""
        responses.add(
            responses.GET,
            f"{base_url}/executions/exec-456",
            json=sample_execution,
            status=200
        )
        
        result = client.get_execution("exec-456")
        assert result["execution_id"] == "exec-456"
        assert result["status"] == "pending"
    
    @responses.activate
    def test_wait_for_execution_success(self, client, base_url):
        """Test waiting for execution completion."""
        # First call returns running
        responses.add(
            responses.GET,
            f"{base_url}/executions/exec-123",
            json={"execution_id": "exec-123", "status": "running"},
            status=200
        )
        # Second call returns completed
        responses.add(
            responses.GET,
            f"{base_url}/executions/exec-123",
            json={
                "execution_id": "exec-123",
                "status": "completed",
                "output_data": {"result": "success"}
            },
            status=200
        )
        
        result = client.wait_for_execution("exec-123", timeout=5, interval=0.1)
        assert result["status"] == "completed"
        assert result["output_data"]["result"] == "success"
    
    @responses.activate
    def test_wait_for_execution_failure(self, client, base_url):
        """Test waiting for failed execution."""
        responses.add(
            responses.GET,
            f"{base_url}/executions/exec-123",
            json={
                "execution_id": "exec-123",
                "status": "failed",
                "error_message": "Processing failed"
            },
            status=200
        )
        
        with pytest.raises(ExecutionError) as exc_info:
            client.wait_for_execution("exec-123", timeout=5, interval=0.1)
        assert "Processing failed" in str(exc_info.value)


class TestFlowManagement:
    """Test flow management methods."""
    
    @responses.activate
    def test_list_flows_array_response(self, client, base_url, sample_flow):
        """Test listing flows with array response."""
        responses.add(
            responses.GET,
            f"{base_url}/flows",
            json=[sample_flow],
            status=200
        )
        
        flows = client.list_flows()
        assert len(flows) == 1
        assert flows[0]["flow_id"] == "test-flow-123"
    
    @responses.activate
    def test_list_flows_object_response(self, client, base_url, sample_flow):
        """Test listing flows with object response."""
        responses.add(
            responses.GET,
            f"{base_url}/flows",
            json={"flows": [sample_flow]},
            status=200
        )
        
        flows = client.list_flows()
        assert len(flows) == 1
        assert flows[0]["flow_id"] == "test-flow-123"
    
    @responses.activate
    def test_get_flow_success(self, client, base_url, sample_flow):
        """Test getting flow details."""
        responses.add(
            responses.GET,
            f"{base_url}/flows/test-flow-123",
            json=sample_flow,
            status=200
        )
        
        flow = client.get_flow("test-flow-123")
        assert flow["flow_id"] == "test-flow-123"
        assert flow["name"] == "Test Flow"


class TestAgentManagement:
    """Test agent management methods."""
    
    @responses.activate
    def test_list_agents(self, client, base_url, sample_agent):
        """Test listing agents."""
        responses.add(
            responses.GET,
            f"{base_url}/agents",
            json=[sample_agent],
            status=200
        )
        
        agents = client.list_agents()
        assert len(agents) == 1
        assert agents[0]["agent_id"] == "agent-789"
    
    @responses.activate
    def test_create_agent(self, client, base_url, sample_agent):
        """Test creating an agent."""
        responses.add(
            responses.POST,
            f"{base_url}/agents",
            json=sample_agent,
            status=201
        )
        
        agent_config = {
            "name": "Test Agent",
            "type": "processor",
            "configuration": {"model": "gpt-4"}
        }
        
        agent = client.create_agent(agent_config)
        assert agent["agent_id"] == "agent-789"
    
    @responses.activate
    def test_delete_agent_success(self, client, base_url):
        """Test deleting an agent."""
        responses.add(
            responses.DELETE,
            f"{base_url}/agents/agent-789",
            status=204
        )
        
        result = client.delete_agent("agent-789")
        assert result is True
    
    @responses.activate
    def test_delete_agent_not_found(self, client, base_url):
        """Test deleting non-existent agent."""
        responses.add(
            responses.DELETE,
            f"{base_url}/agents/agent-999",
            json={"message": "Agent not found"},
            status=404
        )
        
        result = client.delete_agent("agent-999")
        assert result is False


class TestSystemOperations:
    """Test system operation methods."""
    
    @responses.activate
    def test_health_check(self, client, base_url):
        """Test health check."""
        responses.add(
            responses.GET,
            f"{base_url}/health",
            json={"status": "healthy", "version": "1.0.0"},
            status=200
        )
        
        health = client.health_check()
        assert health["status"] == "healthy"
    
    @responses.activate
    def test_get_metrics(self, client, base_url):
        """Test getting metrics."""
        responses.add(
            responses.GET,
            f"{base_url}/metrics",
            json={"executions_total": 100, "flows_total": 10},
            status=200
        )
        
        metrics = client.get_metrics()
        assert metrics["executions_total"] == 100
    
    @responses.activate
    def test_get_status(self, client, base_url):
        """Test getting status."""
        responses.add(
            responses.GET,
            f"{base_url}/status",
            json={"status": "operational", "uptime": 3600},
            status=200
        )
        
        status = client.get_status()
        assert status["status"] == "operational"


class TestErrorHandling:
    """Test error handling."""
    
    @responses.activate
    def test_authentication_error(self, client, base_url):
        """Test authentication error handling."""
        responses.add(
            responses.GET,
            f"{base_url}/flows",
            json={"message": "Invalid API key"},
            status=401
        )
        
        with pytest.raises(AuthenticationError) as exc_info:
            client.list_flows()
        assert "Invalid API key" in str(exc_info.value)
    
    @responses.activate
    def test_validation_error(self, client, base_url):
        """Test validation error from API."""
        responses.add(
            responses.POST,
            f"{base_url}/flows/execute",
            json={"message": "Invalid input data"},
            status=400
        )
        
        with pytest.raises(ValidationError) as exc_info:
            client.execute_flow("test-flow", {"invalid": "data"})
        assert "Invalid input data" in str(exc_info.value)
    
    @responses.activate
    def test_rate_limit_error(self, client, base_url):
        """Test rate limit error handling."""
        responses.add(
            responses.GET,
            f"{base_url}/flows",
            json={"message": "Rate limit exceeded"},
            headers={"Retry-After": "60"},
            status=429
        )
        
        with pytest.raises(RateLimitError) as exc_info:
            client.list_flows()
        assert exc_info.value.retry_after == 60
    
    @responses.activate
    def test_server_error(self, client, base_url):
        """Test server error handling."""
        responses.add(
            responses.GET,
            f"{base_url}/flows",
            json={"message": "Internal server error"},
            status=500
        )
        
        with pytest.raises(APIError) as exc_info:
            client.list_flows()
        assert exc_info.value.status_code == 500