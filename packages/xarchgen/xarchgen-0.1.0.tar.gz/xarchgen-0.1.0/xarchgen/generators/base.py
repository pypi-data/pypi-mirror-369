"""
Base generator class
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable

class BaseGenerator(ABC):
    """Base class for all code generators"""
    
    @abstractmethod
    def generate_application(
        self,
        schema: Dict[str, Any],
        connection_string: str = "",
        table_groups: Optional[Dict[str, List[str]]] = None,
        solution_name: str = "GeneratedApp",
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> Dict[str, str]:
        """
        Generate application files based on database schema
        
        Args:
            schema: Database schema information
            connection_string: Database connection string
            table_groups: Optional table grouping
            solution_name: Name of the generated application
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dictionary of file paths to file contents
        """
        pass