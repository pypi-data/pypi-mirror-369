# Type stub file for mapper package
from typing import Dict, Optional, Any

class mapper:
    """
    Class for mapping and transforming JSON dictionaries.
    
    This class allows flattening nested dictionaries and mapping fields
    according to a specific configuration. It's useful for transforming data
    between different formats or structures.
    
    Attributes:
        sep (str): Separator used to concatenate nested keys. Default: "|"
        parent_key (str): Optional parent key to prefix all keys. Default: ""
    
    Example:
        >>> mapper_instance = mapper(sep=".", parent_key="data")
        >>> result = mapper_instance.map_dict(input_data, "config.json", "trigger_name")
    """
    
    sep: str
    parent_key: str
    
    def __init__(self, sep: str = "|", parent_key: str = "") -> None:
        """
        Initialize the mapper instance.
        
        Args:
            sep (str, optional): Separator for nested keys. Default: "|"
            parent_key (str, optional): Parent key to prefix all keys. Default: ""
        """
        ...
    
    def map_dict(self, input_dict: Dict[str, Any], config_path: str, trigger: Optional[str] = None) -> Dict[str, Any]:
        """
        Map an input dictionary using file configuration.
        
        This is the main method that combines flattening and field mapping.
        First flattens the input dictionary, then loads the configuration
        from the specified file and applies the mapping.
        
        Args:
            input_dict (dict): Input dictionary to be mapped
            config_path (str): Path to the JSON configuration file
            trigger (str, optional): Specific key in configuration to use. Default: None
            
        Returns:
            dict: Dictionary with mapped data according to configuration
            
        Raises:
            Exception: If input_dict or config_path are empty or None
            FileNotFoundError: If configuration file is not found
            json.JSONDecodeError: If configuration file is not valid JSON
            
        Example:
            >>> input_data = {"user": {"name": "João", "age": 30}}
            >>> result = mapper_instance.map_dict(input_data, "mapping_config.json", "user_mapping")
        """
        ...

__all__ = ['mapper']
