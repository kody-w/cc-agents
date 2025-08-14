"""
Tests for can_analyze_our_agent
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from can_analyze_our_agent import CanAnalyzeOurAgent


@pytest.fixture
def agent():
    """Create agent instance for testing"""
    config = {
        "mode": "test",
        "logging": {"level": "DEBUG"}
    }
    return CanAnalyzeOurAgent(config)


@pytest.fixture
def sample_input():
    """Sample input data for testing"""
    return {
        "data": "test_data",
        "timestamp": "2024-01-01T00:00:00"
    }


class TestCanAnalyzeOurAgent:
    """Test suite for CanAnalyzeOurAgent"""
    
    def test_initialization(self, agent):
        """Test agent initialization"""
        assert agent is not None
        assert agent.config["mode"] == "test"
        assert agent.components is not None
    
    @pytest.mark.asyncio
    async def test_process_success(self, agent, sample_input):
        """Test successful processing"""
        result = await agent.process(sample_input)
        
        assert result["status"] == "success"
        assert "result" in result
        assert "metadata" in result
    
    @pytest.mark.asyncio
    async def test_process_empty_input(self, agent):
        """Test processing with empty input"""
        result = await agent.process({})
        
        assert result["status"] == "error"
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_process_invalid_input(self, agent):
        """Test processing with invalid input"""
        result = await agent.process(None)
        
        assert result["status"] == "error"
        assert "Input data is required" in result["error"]
    
    def test_health_check(self, agent):
        """Test health check"""
        health = agent.health_check()
        
        assert health["status"] == "healthy"
        assert "timestamp" in health
    
    def test_get_status(self, agent):
        """Test status retrieval"""
        status = agent.get_status()
        
        assert status["status"] == "running"
        assert "components" in status
        assert "metrics" in status

    
    @pytest.mark.asyncio
    async def test_capability_analyze(self, agent, sample_input):
        """Test analyze capability"""
        # Test the analyze functionality
        result = await agent._execute_analyze(sample_input)
        assert result is not None

    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_performance_test_003(self, agent, sample_input):
        """Performance test: Test agent performance"""
        import time
        
        start = time.time()
        result = await agent.process(sample_input)
        duration = time.time() - start
        
        assert result["status"] == "success"
        assert duration < 1.0  # Max 1 second



if __name__ == "__main__":
    pytest.main([__file__, "-v"])
