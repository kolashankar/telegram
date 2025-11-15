"""Widevine key extraction service"""
import httpx
import logging
from typing import Dict, List, Optional, Any
import base64

logger = logging.getLogger(__name__)

class WidevineExtractor:
    """Widevine DRM key extractor"""
    
    def __init__(self, api_key: str, api_url: str = "https://api.toonverse.icu"):
        self.api_key = api_key
        self.api_url = api_url
    
    async def extract_keys(
        self,
        pssh: str,
        license_url: str,
        headers: Optional[Dict[str, str]] = None,
        challenge: Optional[str] = None
    ) -> Dict[str, Any]:
        """Extract keys from PSSH and license URL"""
        
        try:
            # For now, return mock data since we're using mock API key
            if self.api_key.startswith('wv_mock'):
                logger.info("Using mock Widevine API - returning sample keys")
                return {
                    'success': True,
                    'keys': [
                        {
                            'kid': self._generate_mock_kid(pssh),
                            'key': self._generate_mock_key(pssh)
                        }
                    ],
                    'count': 1
                }
            
            # Real API call (when actual API key is provided)
            payload = {
                'pssh': pssh,
                'license_url': license_url,
                'headers': headers or {}
            }
            
            if challenge:
                payload['challenge'] = challenge
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_url}/api/keys",
                    json=payload,
                    headers={
                        'Content-Type': 'application/json',
                        'X-API-Key': self.api_key
                    }
                )
                
                if response.status_code != 200:
                    error_text = response.text[:200]
                    return {
                        'success': False,
                        'error': f"API Error {response.status_code}: {error_text}",
                        'keys': []
                    }
                
                result = response.json()
                return {
                    'success': True,
                    'keys': result.get('keys', []),
                    'count': len(result.get('keys', []))
                }
                
        except Exception as e:
            logger.error(f"Key extraction failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'keys': []
            }
    
    def _generate_mock_kid(self, pssh: str) -> str:
        """Generate mock KID for demo purposes"""
        # Simple hash of pssh to create consistent mock KID
        hash_val = sum(ord(c) for c in pssh[:16]) % 256
        return f"{hash_val:02x}" * 16
    
    def _generate_mock_key(self, pssh: str) -> str:
        """Generate mock key for demo purposes"""
        # Simple hash of pssh to create consistent mock key
        hash_val = sum(ord(c) for c in pssh[16:32]) % 256
        return f"{hash_val:02x}" * 16