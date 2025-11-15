"""Google Maps service for location queries (MVP)"""

import logging
import os
from typing import Optional
import aiohttp

log = logging.getLogger(__name__)


class MapsService:
    """Google Maps integration for finding nearby places"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_MAPS_API_KEY", "")
        self.base_url = "https://maps.googleapis.com/maps/api"

    async def find_nearby_places(
        self,
        category: str,
        latitude: float,
        longitude: float,
        radius: int = 5000,
        language: str = "id",
    ) -> list[dict]:
        """
        Find nearby places using Google Maps Places API.

        Args:
            category: Place category (e.g., "restaurant", "hospital", "mosque")
            latitude: User's latitude
            longitude: User's longitude
            radius: Search radius in meters (default: 5000m = 5km)
            language: Response language (id, zh, en)

        Returns:
            List of place dictionaries with name, address, rating, etc.
        """
        if not self.api_key:
            log.warning("Google Maps API key not configured")
            return []

        # Map category to Google Places type
        type_mapping = {
            "food": "restaurant",
            "indonesian_restaurant": "restaurant",
            "halal_food": "restaurant",
            "health": "hospital",
            "hospital": "hospital",
            "clinic": "doctor",
            "pharmacy": "pharmacy",
            "community": "place_of_worship",
            "mosque": "mosque",
            "church": "church",
            "emergency": "police",
            "police": "police",
            "fire_station": "fire_station",
            "immigration": "local_government_office",
            "services": "bank",
            "atm": "atm",
            "bank": "bank",
            "remittance": "money_transfer",
        }

        place_type = type_mapping.get(category.lower(), category)

        # Build search query
        query_params = {
            "location": f"{latitude},{longitude}",
            "radius": str(radius),
            "type": place_type,
            "language": language,
            "key": self.api_key,
        }

        # Add keyword for specific searches
        if category.lower() in ["indonesian_restaurant", "halal_food"]:
            query_params["keyword"] = (
                "indonesian" if category.lower() == "indonesian_restaurant" else "halal"
            )

        url = f"{self.base_url}/place/nearbysearch/json"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=query_params) as response:
                    if response.status != 200:
                        log.error(f"Google Maps API error: {response.status}")
                        return []

                    data = await response.json()

                    if data.get("status") != "OK":
                        log.warning(
                            f"Google Maps API returned status: {data.get('status')}"
                        )
                        return []

                    results = data.get("results", [])

                    # Parse and return top 5 results
                    places = []
                    for place in results[:5]:
                        places.append(
                            {
                                "name": place.get("name", "Unknown"),
                                "address": place.get("vicinity", "No address"),
                                "rating": place.get("rating", 0.0),
                                "user_ratings_total": place.get(
                                    "user_ratings_total", 0
                                ),
                                "location": place.get("geometry", {}).get(
                                    "location", {}
                                ),
                                "place_id": place.get("place_id", ""),
                                "open_now": place.get("opening_hours", {}).get(
                                    "open_now", None
                                ),
                            }
                        )

                    log.info(f"Found {len(places)} places for category: {category}")
                    return places

        except Exception as e:
            log.error(f"Error searching places: {e}")
            return []

    def format_places_message(
        self, places: list[dict], category: str, language: str = "id"
    ) -> str:
        """
        Format list of places into a LINE message.

        Args:
            places: List of place dictionaries
            category: Category name for the message
            language: Language for the message

        Returns:
            Formatted message string
        """
        if not places:
            if language == "id":
                return f"❌ Tidak menemukan {category} di sekitar Anda"
            elif language == "zh":
                return f"❌ 找不到附近的 {category}"
            else:
                return f"❌ Could not find {category} near you"

        # Language-specific labels
        labels = {
            "id": {
                "found": "Ditemukan",
                "nearby": "terdekat",
                "rating": "Rating",
                "reviews": "ulasan",
                "open": "Buka sekarang",
                "closed": "Tutup",
                "view_map": "Lihat di Google Maps",
            },
            "zh": {
                "found": "找到",
                "nearby": "附近的",
                "rating": "評分",
                "reviews": "則評論",
                "open": "營業中",
                "closed": "休息中",
                "view_map": "在 Google Maps 查看",
            },
            "en": {
                "found": "Found",
                "nearby": "nearby",
                "rating": "Rating",
                "reviews": "reviews",
                "open": "Open now",
                "closed": "Closed",
                "view_map": "View on Google Maps",
            },
        }

        lang_labels = labels.get(language, labels["id"])

        message_lines = [
            f"📍 {lang_labels['found']} {len(places)} {category} {lang_labels['nearby']}:\n"
        ]

        for i, place in enumerate(places, 1):
            name = place["name"]
            address = place["address"]
            rating = place["rating"]
            reviews = place["user_ratings_total"]
            place_id = place["place_id"]

            # Rating stars
            stars = "⭐" * int(rating) if rating > 0 else "—"

            # Open/closed status
            open_status = ""
            if place["open_now"] is not None:
                open_status = (
                    f" • {lang_labels['open']}"
                    if place["open_now"]
                    else f" • {lang_labels['closed']}"
                )

            # Google Maps link
            maps_url = (
                f"https://www.google.com/maps/place/?q=place_id:{place_id}"
            )

            message_lines.append(
                f"{i}. {name}\n"
                f"   📍 {address}\n"
                f"   {stars} {rating:.1f} ({reviews} {lang_labels['reviews']}){open_status}\n"
                f"   🔗 {maps_url}\n"
            )

        return "\n".join(message_lines)
