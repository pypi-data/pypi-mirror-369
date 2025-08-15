"""
Utility functions for DHIS2 operations
"""

from typing import Dict, Any, List
from datetime import datetime


class DHISUtils:
    """
    Utility class for DHIS2 data processing and manipulation
    """
    
    @staticmethod
    def format_date(date: datetime, dhis_format: bool = True) -> str:
        """
        Format date for DHIS2 API
        
        Args:
            date: Date to format
            dhis_format: Whether to use DHIS2 date format
            
        Returns:
            Formatted date string
        """
        if dhis_format:
            return date.strftime('%Y-%m-%d')
        return date.isoformat()
    
    @staticmethod
    def validate_data_element(data_element: Dict[str, Any]) -> bool:
        """
        Validate DHIS2 data element structure
        
        Args:
            data_element: Data element to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['id', 'name', 'valueType']
        return all(field in data_element for field in required_fields)
    
    @staticmethod
    def batch_data_values(data_values: List[Dict[str, Any]], batch_size: int = 1000) -> List[List[Dict[str, Any]]]:
        """
        Batch data values for bulk import
        
        Args:
            data_values: List of data values
            batch_size: Size of each batch
            
        Returns:
            List of batched data values
        """
        batches = []
        for i in range(0, len(data_values), batch_size):
            batches.append(data_values[i:i + batch_size])
        return batches
