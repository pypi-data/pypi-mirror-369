"""
xarchgen - Generate Clean Architecture backend applications from PostgreSQL schemas
"""

__version__ = "0.1.0"
__author__ = "Your Name"

from .generators import FastAPIGenerator, DotNetGenerator
from .database import DatabaseSchemaReader

__all__ = [
    "FastAPIGenerator",
    "DotNetGenerator", 
    "DatabaseSchemaReader",
]