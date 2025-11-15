"""Video quality detection from manifests and streams"""
import re
import logging
from typing import List, Optional, Dict, Any
import httpx
from ...models.extraction import VideoQuality

logger = logging.getLogger(__name__)


class QualityDetector:
    """Detect available video qualities from manifests"""
    
    QUALITY_PATTERNS = {
        '4k': ['3840x2160', '4096x2160', '2160p'],
        '1440p': ['2560x1440', '1440p'],
        '1080p': ['1920x1080', '1080p'],
        '720p': ['1280x720', '720p'],
        '480p': ['854x480', '720x480', '480p'],
        '360p': ['640x360', '360p'],
        '240p': ['426x240', '240p']
    }
    
    @staticmethod
    def detect_from_pssh(pssh: str) -> List[VideoQuality]:
        """Extract quality info from PSSH data"""
        # For mock implementation, return common qualities
        return [
            VideoQuality(
                quality_id="360p",
                resolution="640x360",
                bitrate=800,
                codec="h264",
                fps=30,
                file_size_mb=50.0
            ),
            VideoQuality(
                quality_id="480p",
                resolution="854x480",
                bitrate=1500,
                codec="h264",
                fps=30,
                file_size_mb=120.0
            ),
            VideoQuality(
                quality_id="720p",
                resolution="1280x720",
                bitrate=3000,
                codec="h264",
                fps=30,
                file_size_mb=250.0
            ),
            VideoQuality(
                quality_id="1080p",
                resolution="1920x1080",
                bitrate=5000,
                codec="h264",
                fps=30,
                file_size_mb=450.0
            ),
            VideoQuality(
                quality_id="1440p",
                resolution="2560x1440",
                bitrate=8000,
                codec="h265",
                fps=60,
                file_size_mb=700.0
            ),
            VideoQuality(
                quality_id="4k",
                resolution="3840x2160",
                bitrate=15000,
                codec="h265",
                fps=60,
                file_size_mb=1200.0
            )
        ]
    
    @staticmethod
    async def detect_from_manifest(manifest_url: str, headers: Optional[Dict] = None) -> List[VideoQuality]:
        """Detect qualities from DASH/HLS manifest"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(manifest_url, headers=headers or {})
                
                if response.status_code != 200:
                    logger.warning(f"Failed to fetch manifest: {response.status_code}")
                    return QualityDetector.detect_from_pssh("")  # Return default
                
                content = response.text
                qualities = []
                
                # Parse DASH manifest
                if '.mpd' in manifest_url.lower() or 'dash' in content.lower():
                    qualities = QualityDetector._parse_dash_manifest(content)
                
                # Parse HLS manifest
                elif '.m3u8' in manifest_url.lower() or '#EXTM3U' in content:
                    qualities = QualityDetector._parse_hls_manifest(content)
                
                return qualities if qualities else QualityDetector.detect_from_pssh("")
                
        except Exception as e:
            logger.error(f"Error detecting qualities from manifest: {e}")
            return QualityDetector.detect_from_pssh("")  # Return default
    
    @staticmethod
    def _parse_dash_manifest(content: str) -> List[VideoQuality]:
        """Parse DASH MPD manifest for quality information"""
        qualities = []
        
        # Extract resolution patterns
        resolution_pattern = r'width="(\d+)"\s+height="(\d+)"'
        bitrate_pattern = r'bandwidth="(\d+)"'
        codec_pattern = r'codecs="([^"]+)"'
        
        resolutions = re.findall(resolution_pattern, content)
        bitrates = re.findall(bitrate_pattern, content)
        codecs = re.findall(codec_pattern, content)
        
        for i, (width, height) in enumerate(resolutions):
            quality_id = QualityDetector._get_quality_label(f"{width}x{height}")
            bitrate = int(bitrates[i]) // 1000 if i < len(bitrates) else None
            codec = codecs[i].split('.')[0] if i < len(codecs) else None
            
            qualities.append(VideoQuality(
                quality_id=quality_id,
                resolution=f"{width}x{height}",
                bitrate=bitrate,
                codec=codec,
                fps=30
            ))
        
        return qualities
    
    @staticmethod
    def _parse_hls_manifest(content: str) -> List[VideoQuality]:
        """Parse HLS M3U8 manifest for quality information"""
        qualities = []
        
        # Extract resolution and bandwidth from #EXT-X-STREAM-INF
        stream_pattern = r'#EXT-X-STREAM-INF:.*?BANDWIDTH=(\d+).*?RESOLUTION=(\d+x\d+)'
        matches = re.findall(stream_pattern, content, re.DOTALL)
        
        for bandwidth, resolution in matches:
            quality_id = QualityDetector._get_quality_label(resolution)
            bitrate = int(bandwidth) // 1000
            
            qualities.append(VideoQuality(
                quality_id=quality_id,
                resolution=resolution,
                bitrate=bitrate,
                codec="h264",
                fps=30
            ))
        
        return qualities
    
    @staticmethod
    def _get_quality_label(resolution: str) -> str:
        """Get quality label from resolution string"""
        for quality, patterns in QualityDetector.QUALITY_PATTERNS.items():
            if any(pattern in resolution for pattern in patterns):
                return quality
        return resolution  # Return resolution if no match
    
    @staticmethod
    def get_recommended_quality(qualities: List[VideoQuality]) -> Optional[str]:
        """Get recommended quality (usually 720p for balance)"""
        if not qualities:
            return None
        
        # Prefer 720p for best balance
        for q in qualities:
            if '720p' in q.quality_id:
                return q.quality_id
        
        # If no 720p, return middle quality
        if len(qualities) > 0:
            return qualities[len(qualities) // 2].quality_id
        
        return None
