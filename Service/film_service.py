import requests

class FilmService:
    @staticmethod
    def get_now_playing():
        # Mock API call
        return [
            {"title": "Avengers 5", "duration": "150m"},
            {"title": "Frozen 3", "duration": "120m"}
        ]
