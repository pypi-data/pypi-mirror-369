"""
Code generators for different frameworks
"""

from .base import BaseGenerator
from .dotnet import DotNetGenerator
from .fastapi import FastAPIGenerator

def create_generator(framework: str):
    """
    Factory function to create appropriate code generator based on framework.
    
    Args:
        framework: Either 'dotnet' or 'fastapi'
        
    Returns:
        Code generator instance
    """
    if framework.lower() == 'fastapi':
        return FastAPIGenerator()
    elif framework.lower() == 'dotnet':
        return DotNetGenerator()
    else:
        raise ValueError(f"Unsupported framework: {framework}. Choose 'dotnet' or 'fastapi'.")

__all__ = [
    "BaseGenerator",
    "DotNetGenerator", 
    "FastAPIGenerator",
    "create_generator"
]