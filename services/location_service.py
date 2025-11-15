"""Location service for finding nearby places"""
import logging
from typing import Optional, List
from services.maps_service import MapsService
from config import BotConfig

logger = logging.getLogger(__name__)


class LocationService:
    """High-level location service combining Maps API"""

    def __init__(self, config: BotConfig):
        self.config = config
        self.maps = MapsService(config)

        # Default Taiwan coordinates (Taipei Main Station)
        self.default_location = {"lat": 25.0478, "lng": 121.5170}

    def format_places_response(
        self, places: List[dict], language: str = "zh"
    ) -> Optional[str]:
        """
        Format nearby places into a readable message

        Args:
            places: List of places from Google Maps
            language: Response language (id, zh, en)

        Returns:
            Formatted message string
        """
        if not places:
            messages = {
                "id": "Maaf, tidak ada tempat yang ditemukan di sekitar lokasi Anda.",
                "zh": "抱歉，附近沒有找到相關地點。",
                "en": "Sorry, no places found near your location.",
            }
            return messages.get(language, messages["en"])

        # Header based on language
        headers = {
            "id": "📍 TEMPAT TERDEKAT:",
            "zh": "📍 附近地點：",
            "en": "📍 NEARBY PLACES:",
        }

        lines = [headers.get(language, headers["en"]), ""]

        for i, place in enumerate(places, 1):
            name = place.get("name", "Unknown")
            address = place.get("address", "No address")
            rating = place.get("rating")

            # Format rating
            rating_str = ""
            if rating:
                stars = "⭐" * int(rating)
                rating_str = f" {stars} ({rating})"

            lines.append(f"{i}. {name}{rating_str}")
            lines.append(f"   📍 {address}")
            lines.append("")

        return "\n".join(lines).strip()

    def format_directions_response(
        self, directions: dict, language: str = "zh"
    ) -> Optional[str]:
        """
        Format directions into a readable message

        Args:
            directions: Directions from Google Maps
            language: Response language

        Returns:
            Formatted message string
        """
        if not directions:
            messages = {
                "id": "Maaf, tidak dapat menemukan rute.",
                "zh": "抱歉，無法找到路線。",
                "en": "Sorry, cannot find directions.",
            }
            return messages.get(language, messages["en"])

        headers = {
            "id": "🚶 PETUNJUK ARAH:",
            "zh": "🚶 路線指引：",
            "en": "🚶 DIRECTIONS:",
        }

        distance_labels = {"id": "Jarak", "zh": "距離", "en": "Distance"}
        time_labels = {"id": "Waktu", "zh": "時間", "en": "Time"}

        lines = [
            headers.get(language, headers["en"]),
            "",
            f"{distance_labels.get(language, 'Distance')}: {directions['distance']}",
            f"{time_labels.get(language, 'Time')}: {directions['duration']}",
            "",
        ]

        # Add first few steps
        if "steps" in directions:
            step_labels = {"id": "Langkah", "zh": "步驟", "en": "Step"}
            step_label = step_labels.get(language, "Step")

            for i, step in enumerate(directions["steps"][:5], 1):
                instruction = step.get("instruction", "")
                # Clean HTML tags if any remain
                instruction = instruction.replace("<div", " <div").replace("</div>", " ")
                lines.append(f"{step_label} {i}: {instruction}")
                lines.append(
                    f"   ({step.get('distance', '')} - {step.get('duration', '')})"
                )
                lines.append("")

        return "\n".join(lines).strip()

    async def find_indonesian_restaurants(
        self, latitude: float, longitude: float, language: str = "zh"
    ) -> str:
        """Find nearby Indonesian restaurants"""
        if not self.maps.is_available():
            return self._get_maps_unavailable_message(language)

        places = self.maps.find_nearby_places(
            latitude=latitude,
            longitude=longitude,
            keyword="indonesian restaurant",
            radius=2000,  # 2km radius
            language="zh-TW" if language == "zh" else "en",
        )

        return self.format_places_response(places, language)

    async def find_nearby_hospitals(
        self, latitude: float, longitude: float, language: str = "zh"
    ) -> str:
        """Find nearby hospitals"""
        if not self.maps.is_available():
            return self._get_maps_unavailable_message(language)

        places = self.maps.find_nearby_places(
            latitude=latitude,
            longitude=longitude,
            keyword="hospital",
            radius=3000,  # 3km radius
            language="zh-TW" if language == "zh" else "en",
        )

        return self.format_places_response(places, language)

    async def find_nearby_mosques(
        self, latitude: float, longitude: float, language: str = "zh"
    ) -> str:
        """Find nearby mosques (for Indonesian Muslim workers)"""
        if not self.maps.is_available():
            return self._get_maps_unavailable_message(language)

        places = self.maps.find_nearby_places(
            latitude=latitude,
            longitude=longitude,
            keyword="mosque masjid",
            radius=5000,  # 5km radius
            language="zh-TW" if language == "zh" else "en",
        )

        return self.format_places_response(places, language)

    async def get_directions_to_place(
        self,
        origin_lat: float,
        origin_lng: float,
        destination: str,
        language: str = "zh",
    ) -> str:
        """Get directions from current location to destination"""
        if not self.maps.is_available():
            return self._get_maps_unavailable_message(language)

        origin = f"{origin_lat},{origin_lng}"
        directions = self.maps.get_directions(
            origin=origin,
            destination=destination,
            mode="transit",  # Use public transport by default in Taiwan
            language="zh-TW" if language == "zh" else "en",
        )

        return self.format_directions_response(directions, language)

    def _get_maps_unavailable_message(self, language: str) -> str:
        """Get message when Maps service is unavailable"""
        messages = {
            "id": "⚠️ Layanan lokasi tidak tersedia. Google Maps API key belum dikonfigurasi.",
            "zh": "⚠️ 位置服務暫時無法使用。Google Maps API key 尚未設定。",
            "en": "⚠️ Location service is unavailable. Google Maps API key not configured.",
        }
        return messages.get(language, messages["en"])
