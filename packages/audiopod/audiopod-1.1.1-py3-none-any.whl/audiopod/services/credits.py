"""
Credits Service - User credits and usage tracking
"""

from typing import List, Dict, Any
from .base import BaseService
from ..models import CreditInfo


class CreditService(BaseService):
    """Service for managing user credits and usage"""
    
    def get_credit_balance(self) -> CreditInfo:
        """Get current credit balance and info"""
        if self.async_mode:
            return self._async_get_credit_balance()
        else:
            response = self.client.request("GET", "/api/v1/credits")
            return CreditInfo.from_dict(response)
            
    async def _async_get_credit_balance(self) -> CreditInfo:
        """Async version of get_credit_balance"""
        response = await self.client.request("GET", "/api/v1/credits")
        return CreditInfo.from_dict(response)
        
    def get_usage_history(self) -> List[Dict[str, Any]]:
        """Get credit usage history"""
        if self.async_mode:
            return self._async_get_usage_history()
        else:
            return self.client.request("GET", "/api/v1/credits/usage")
            
    async def _async_get_usage_history(self) -> List[Dict[str, Any]]:
        """Async version of get_usage_history"""
        return await self.client.request("GET", "/api/v1/credits/usage")
        
    def get_credit_multipliers(self) -> Dict[str, float]:
        """Get credit multipliers for different services"""
        if self.async_mode:
            return self._async_get_credit_multipliers()
        else:
            return self.client.request("GET", "/api/v1/credits/multipliers")
            
    async def _async_get_credit_multipliers(self) -> Dict[str, float]:
        """Async version of get_credit_multipliers"""
        return await self.client.request("GET", "/api/v1/credits/multipliers")
