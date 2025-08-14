from abc import ABC, abstractmethod
from typing import Dict, Any


class BasicAgent(ABC):
    """
    Base class for all agents in the Azure Functions system.
    Provides a standardized interface for agent metadata and execution.
    """
    
    def __init__(self, name: str, metadata: Dict[str, Any]):
        self.name = name
        self.metadata = metadata
    
    @abstractmethod
    def perform(self, **kwargs) -> str:
        """
        Execute the agent's main functionality.
        
        Args:
            **kwargs: Agent-specific parameters
            
        Returns:
            str: Result of the agent's operation
        """
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get the agent's metadata including name, description, and parameters.
        
        Returns:
            Dict[str, Any]: Agent metadata
        """
        return self.metadata