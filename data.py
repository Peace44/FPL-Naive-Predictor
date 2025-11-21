import requests
import logging

logger = logging.getLogger(__name__)

class FPLDataFetcher:
    API_BASE_URL = "https://fantasy.premierleague.com/api"

    def fetch_general_info(self):
        """Fetch general FPL info (teams, players, positions)"""
        url = f"{self.API_BASE_URL}/bootstrap-static/"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error("Error fetching general FPL info: %s", e)
            return None
    


    def fetch_fixture_data(self):
        """Fetch fixture data (past and upcoming gameweeks)"""
        url = f"{self.API_BASE_URL}/fixtures/"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error("Error fetching fixture data: %s", e)
            return None
    
