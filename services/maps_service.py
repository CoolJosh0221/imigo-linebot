"""Google Maps integration for location services"""
import logging
from typing import Optional, List, Dict
import googlemaps
from config import BotConfig

logger = logging.getLogger(__name__)


class MapsService:
    """Google Maps API wrapper for location queries"""

    def __init__(self, config: BotConfig):
        self.config = config
        self.client = None
        if config.google_maps_api_key:
            self.client = googlemaps.Client(key=config.google_maps_api_key)
            logger.info("Google Maps client initialized")
        else:
            logger.warning("Google Maps API key not configured")

    def is_available(self) -> bool:
        """Check if Maps service is available"""
        return self.client is not None

    def find_nearby_places(
        self,
        latitude: float,
        longitude: float,
        keyword: str = "indonesian restaurant",
        radius: int = 1000,
        language: str = "zh-TW",
    ) -> List[Dict]:
        """
        Find nearby places using Google Places API

        Args:
            latitude: Location latitude
            longitude: Location longitude
            keyword: Search keyword (e.g., "indonesian restaurant")
            radius: Search radius in meters (default: 1000m)
            language: Response language (default: zh-TW for Traditional Chinese)

        Returns:
            List of places with name, address, rating, distance
        """
        if not self.is_available():
            logger.error("Maps service not available")
            return []

        try:
            # Use Places API (Nearby Search)
            places_result = self.client.places_nearby(
                location=(latitude, longitude),
                radius=radius,
                keyword=keyword,
                language=language,
            )

            results = []
            for place in places_result.get("results", [])[:5]:  # Limit to top 5
                place_info = {
                    "name": place.get("name"),
                    "address": place.get("vicinity"),
                    "rating": place.get("rating"),
                    "location": place.get("geometry", {}).get("location"),
                    "place_id": place.get("place_id"),
                }
                results.append(place_info)

            logger.info(
                f"Found {len(results)} places for keyword '{keyword}' near ({latitude}, {longitude})"
            )
            return results

        except Exception as e:
            logger.error(f"Error finding nearby places: {e}")
            return []

    def geocode_address(self, address: str, language: str = "zh-TW") -> Optional[Dict]:
        """
        Convert address to coordinates using Geocoding API

        Args:
            address: Address string (e.g., "台北市中山區南京東路")
            language: Response language

        Returns:
            Dict with lat, lng, formatted_address or None
        """
        if not self.is_available():
            logger.error("Maps service not available")
            return None

        try:
            geocode_result = self.client.geocode(address, language=language)

            if geocode_result:
                location = geocode_result[0]["geometry"]["location"]
                formatted_address = geocode_result[0].get("formatted_address")

                return {
                    "lat": location["lat"],
                    "lng": location["lng"],
                    "formatted_address": formatted_address,
                }

            return None

        except Exception as e:
            logger.error(f"Error geocoding address '{address}': {e}")
            return None

    def get_directions(
        self,
        origin: str,
        destination: str,
        mode: str = "transit",
        language: str = "zh-TW",
    ) -> Optional[Dict]:
        """
        Get directions between two locations

        Args:
            origin: Starting location (address or lat,lng)
            destination: Ending location (address or lat,lng)
            mode: Travel mode (driving, walking, transit, bicycling)
            language: Response language

        Returns:
            Dict with distance, duration, steps or None
        """
        if not self.is_available():
            logger.error("Maps service not available")
            return None

        try:
            directions_result = self.client.directions(
                origin=origin, destination=destination, mode=mode, language=language
            )

            if directions_result:
                route = directions_result[0]
                leg = route["legs"][0]

                return {
                    "distance": leg["distance"]["text"],
                    "duration": leg["duration"]["text"],
                    "start_address": leg["start_address"],
                    "end_address": leg["end_address"],
                    "steps": [
                        {
                            "instruction": step.get("html_instructions", "")
                            .replace("<b>", "")
                            .replace("</b>", ""),
                            "distance": step["distance"]["text"],
                            "duration": step["duration"]["text"],
                        }
                        for step in leg["steps"][:5]  # Limit to first 5 steps
                    ],
                }

            return None

        except Exception as e:
            logger.error(f"Error getting directions: {e}")
            return None

    def reverse_geocode(
        self, latitude: float, longitude: float, language: str = "zh-TW"
    ) -> Optional[str]:
        """
        Convert coordinates to address

        Args:
            latitude: Location latitude
            longitude: Location longitude
            language: Response language

        Returns:
            Formatted address or None
        """
        if not self.is_available():
            logger.error("Maps service not available")
            return None

        try:
            result = self.client.reverse_geocode(
                (latitude, longitude), language=language
            )

            if result:
                return result[0].get("formatted_address")

            return None

        except Exception as e:
            logger.error(f"Error reverse geocoding ({latitude}, {longitude}): {e}")
            return None
