"""
IMDB Service for OTT Bot
Fetch movie/series information for OTT content
"""
import logging
import httpx
from typing import Optional, Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)

class IMDBService:
    """Service to fetch IMDB/TMDb data for OTT content"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize IMDB service with optional TMDb API key"""
        self.api_key = api_key or "mock_tmdb_key"  # Mock key for now
        self.base_url = "https://api.themoviedb.org/3"
        self.image_base_url = "https://image.tmdb.org/t/p/w500"
    
    async def search_content(self, query: str, content_type: str = "multi") -> List[Dict]:
        """
        Search for movies/series
        content_type: 'movie', 'tv', or 'multi'
        """
        try:
            # Mock response for now (in production, use actual TMDb API)
            mock_results = [
                {
                    "id": 12345,
                    "title": query,
                    "original_title": query,
                    "overview": f"A compelling story about {query}. Available on multiple OTT platforms.",
                    "release_date": "2024-01-15",
                    "vote_average": 7.8,
                    "vote_count": 1250,
                    "popularity": 156.4,
                    "poster_path": "/mock_poster.jpg",
                    "backdrop_path": "/mock_backdrop.jpg",
                    "media_type": "movie",
                    "genre_ids": [28, 12, 878],
                    "genres": ["Action", "Adventure", "Sci-Fi"],
                    "runtime": 142,
                    "languages": ["English", "Hindi", "Tamil"]
                }
            ]
            
            return mock_results
            
        except Exception as e:
            logger.error(f"Error searching content: {e}")
            return []
    
    async def get_content_details(self, content_id: int, content_type: str = "movie") -> Optional[Dict]:
        """
        Get detailed information about a movie or series
        content_type: 'movie' or 'tv'
        """
        try:
            # Mock detailed response
            mock_detail = {
                "id": content_id,
                "title": "Sample OTT Content",
                "original_title": "Sample OTT Content",
                "tagline": "The best entertainment experience",
                "overview": "An amazing story that captivates audiences worldwide. Now available on your favorite OTT platforms.",
                "release_date": "2024-01-15",
                "runtime": 142,
                "vote_average": 7.8,
                "vote_count": 1250,
                "popularity": 156.4,
                "poster_path": "/mock_poster.jpg",
                "backdrop_path": "/mock_backdrop.jpg",
                "genres": [
                    {"id": 28, "name": "Action"},
                    {"id": 12, "name": "Adventure"},
                    {"id": 878, "name": "Sci-Fi"}
                ],
                "production_companies": [
                    {"name": "Major Studio", "logo_path": "/logo.png"}
                ],
                "spoken_languages": [
                    {"english_name": "English", "name": "English"},
                    {"english_name": "Hindi", "name": "हिन्दी"},
                    {"english_name": "Tamil", "name": "தமிழ்"}
                ],
                "status": "Released",
                "budget": 150000000,
                "revenue": 500000000,
                "imdb_id": "tt1234567",
                "homepage": "https://example.com/movie",
                "credits": {
                    "cast": [
                        {"name": "Lead Actor", "character": "Hero", "profile_path": "/actor.jpg"},
                        {"name": "Lead Actress", "character": "Heroine", "profile_path": "/actress.jpg"}
                    ],
                    "crew": [
                        {"name": "Director Name", "job": "Director"},
                        {"name": "Producer Name", "job": "Producer"}
                    ]
                }
            }
            
            return mock_detail
            
        except Exception as e:
            logger.error(f"Error fetching content details: {e}")
            return None
    
    async def get_streaming_availability(self, content_id: int, content_type: str = "movie") -> List[Dict]:
        """Get OTT platform availability for content"""
        try:
            # Mock streaming availability
            mock_platforms = [
                {
                    "platform": "Netflix",
                    "logo": "netflix_logo.png",
                    "available": True,
                    "quality": "4K HDR",
                    "subscription_required": True
                },
                {
                    "platform": "Amazon Prime Video",
                    "logo": "prime_logo.png",
                    "available": True,
                    "quality": "4K",
                    "subscription_required": True
                },
                {
                    "platform": "Disney+ Hotstar",
                    "logo": "hotstar_logo.png",
                    "available": True,
                    "quality": "1080p",
                    "subscription_required": True
                },
                {
                    "platform": "Zee5",
                    "logo": "zee5_logo.png",
                    "available": False,
                    "quality": None,
                    "subscription_required": True
                }
            ]
            
            return mock_platforms
            
        except Exception as e:
            logger.error(f"Error fetching streaming availability: {e}")
            return []
    
    def format_imdb_message(self, content: Dict, long_description: bool = False) -> str:
        """Format content details into a nice message"""
        try:
            title = content.get("title", "Unknown")
            year = content.get("release_date", "")[:4] if content.get("release_date") else "N/A"
            rating = content.get("vote_average", 0)
            overview = content.get("overview", "No description available")
            runtime = content.get("runtime", 0)
            genres = ", ".join([g.get("name", "") for g in content.get("genres", [])])
            
            # Truncate overview if not long description
            if not long_description and len(overview) > 200:
                overview = overview[:200] + "..."
            
            message = f"""
🎬 <b>{title}</b> ({year})

⭐ <b>Rating:</b> {rating}/10
🎭 <b>Genre:</b> {genres}
⏱ <b>Runtime:</b> {runtime} minutes

📝 <b>Overview:</b>
{overview}

🎥 <b>Available on:</b> Netflix, Prime Video, Hotstar

💎 <i>Subscribe to Premium for instant access to all OTT platforms!</i>
"""
            
            return message.strip()
            
        except Exception as e:
            logger.error(f"Error formatting message: {e}")
            return "Error formatting content information"
    
    async def get_trending(self, content_type: str = "movie", time_window: str = "week") -> List[Dict]:
        """
        Get trending content
        content_type: 'movie', 'tv', or 'all'
        time_window: 'day' or 'week'
        """
        try:
            # Mock trending content
            mock_trending = [
                {
                    "id": 11111,
                    "title": "Trending Movie 1",
                    "vote_average": 8.5,
                    "release_date": "2024-11-01",
                    "poster_path": "/trending1.jpg"
                },
                {
                    "id": 22222,
                    "title": "Trending Movie 2",
                    "vote_average": 8.2,
                    "release_date": "2024-10-15",
                    "poster_path": "/trending2.jpg"
                },
                {
                    "id": 33333,
                    "title": "Trending Series 1",
                    "vote_average": 9.0,
                    "first_air_date": "2024-09-20",
                    "poster_path": "/trending3.jpg"
                }
            ]
            
            return mock_trending
            
        except Exception as e:
            logger.error(f"Error fetching trending content: {e}")
            return []
