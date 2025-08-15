from typing import Dict, Any
import logging

class Base:
    """Base class for VSChart classes with Rich logging configuration."""
    
    def __init__(self):
        self.logger = logging.getLogger("vschart")
        self.id = ''
        
    def get_options(self) -> Dict[str, Any]:
        """Get chart options"""
        result = self.send_request("getOptions", [self.id])
        if result['success']:
            return result['options']
        else:
            self.logger.error(f"Failed to get chart options")
            return {}
        
    def set_options(self, options: Dict[str, Any]):
        result = self.send_request('applyOptions', [self.id, options])
        if result['success']:
            self.logger.info("Options set successfully")
        else:
            self.logger.error("Failed to set options")
