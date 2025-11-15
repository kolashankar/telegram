"""Platform detection utility for OTT services"""

def detect_platform(url: str) -> str:
    """Detect OTT platform from URL"""
    if not url:
        return "🌐 Unknown Platform"
    
    url_lower = url.lower()
    
    # Indian OTT Platforms
    if 'hotstar' in url_lower:
        return "🇮🇳 Hotstar"
    if 'zee5' in url_lower or 'spapi.zee5' in url_lower:
        return "🇮🇳 Zee5"
    if 'sonyliv' in url_lower or 'sony' in url_lower:
        return "🇮🇳 SonyLIV"
    if 'sunnxt' in url_lower:
        return "🇮🇳 SunNXT"
    if 'aha' in url_lower or 'firstlight' in url_lower:
        return "🇮🇳 Aha Video"
    if 'jiocinema' in url_lower:
        return "🇮🇳 JioCinema"
    if 'voot' in url_lower:
        return "🇮🇳 Voot"
    if 'mxplayer' in url_lower:
        return "🇮🇳 MX Player"
    if 'erosnow' in url_lower:
        return "🇮🇳 Eros Now"
    if 'altbalaji' in url_lower:
        return "🇮🇳 ALTBalaji"
    
    # International OTT Platforms
    if 'netflix' in url_lower:
        return "🌍 Netflix"
    if 'primevideo' in url_lower or 'amazon' in url_lower:
        return "🌍 Prime Video"
    if 'disneyplus' in url_lower:
        return "🌍 Disney+"
    if 'hbomax' in url_lower:
        return "🌍 HBO Max"
    if 'hulu' in url_lower:
        return "🌍 Hulu"
    
    # Demo/Test Platforms
    if 'shaka' in url_lower:
        return "🎬 Shaka Demo"
    if 'bitmovin' in url_lower:
        return "🎬 Bitmovin Demo"
    
    # Generic detection from hostname
    try:
        from urllib.parse import urlparse
        hostname = urlparse(url).hostname
        if hostname:
            domain_parts = hostname.split('.')
            if len(domain_parts) >= 2:
                return f"🌐 {domain_parts[-2].capitalize()}"
    except:
        pass
    
    return "🌐 Unknown Platform"

def is_license_url(url: str) -> bool:
    """Check if URL is a license URL"""
    if not url:
        return False
    
    url_lower = url.lower()
    
    # License URL patterns
    license_patterns = [
        '/license', 'licenseproxy', '/drm/', '/rights/', '/wv/',
        'getlicense', 'widevine', 'drmtoday', 'expressplay',
        'castlabs', 'ezdrm', 'irdeto', 'axinom', 'cwip-shaka-proxy'
    ]
    
    return any(pattern in url_lower for pattern in license_patterns)

def is_manifest_url(url: str) -> bool:
    """Check if URL is a manifest URL"""
    if not url:
        return False
    
    url_lower = url.lower()
    
    # Skip media segments
    skip_patterns = ['.m4s', '.ts', '/chunk_', '/segment_', 'index_']
    if any(pattern in url_lower for pattern in skip_patterns):
        return False
    
    # Manifest patterns
    manifest_patterns = [
        '.mpd', '/manifest', 'manifest.mpd', '.dash', '.m3u8'
    ]
    
    return any(url_lower.endswith(pattern) or pattern in url_lower for pattern in manifest_patterns)