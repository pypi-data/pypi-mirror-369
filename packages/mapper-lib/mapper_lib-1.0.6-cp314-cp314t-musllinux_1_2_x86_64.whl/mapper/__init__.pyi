# Minimal type stub for testing
from typing import Dict, Any, Optional

class Mapper:
    sep: str
    parent_key: str
    
    def __init__(self, sep: str = ..., parent_key: str = ...) -> None: ...
    def map_dict(self, input_dict: Dict[str, Any], config_path: str, trigger: Optional[str] = ...) -> Dict[str, Any]: ...
    def _flatten_dict(self, input_dict: Dict[str, Any]) -> Dict[str, Any]: ...
    def _mapping_fields(self, input_fields: Dict[str, Any], flatten_fields: Dict[str, Any]) -> Dict[str, Any]: ...

# Module metadata
__version__: str
__author__: str
__email__: str
__description__: str

# Compatibility alias
mapper: type[Mapper]

__all__ = ['Mapper']