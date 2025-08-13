import httpx
from typing import List, Optional, Dict, Any
from urllib.parse import quote

from .models import Player, Clan, War, ClanMember, League, Location
from .exceptions import (
    ClasherJKException, 
    PlayerNotFound, 
    ClanNotFound, 
    InvalidTag, 
    RateLimitExceeded, 
    APIError
)
from .config import Config


class ClasherJK:
    
    def __init__(self, base_url: str = None):

        # Get proxy URL using configuration system
        self.base_url = Config.get_proxy_url(base_url).rstrip('/')
        self._client = httpx.Client(timeout=30.0)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def close(self):
        self._client.close()
    
    def _make_request(self, endpoint: str) -> Dict[str, Any]:
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = self._client.get(url)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                raise APIError(404, "Resource not found")
            elif response.status_code == 429:
                raise RateLimitExceeded()
            else:
                raise APIError(response.status_code, response.text)
                
        except httpx.RequestError as e:
            raise ClasherJKException(f"Request failed: {str(e)}")
    
    @staticmethod
    def _format_tag(tag: str) -> str:

        if not tag:
            raise InvalidTag(tag)
            
        # Remove # if present, then add %23 for URL encoding
        clean_tag = tag.lstrip('#').upper()
        if not clean_tag:
            raise InvalidTag(tag)
            
        return f"%23{clean_tag}"
    
    # Player Methods
    def get_player(self, player_tag: str) -> Player:

        formatted_tag = self._format_tag(player_tag)
        
        try:
            data = self._make_request(f"players/{formatted_tag}")
            return Player.from_dict(data)
        except APIError as e:
            if e.status_code == 404:
                raise PlayerNotFound(player_tag)
            raise
    
    # Clan Methods
    def get_clan(self, clan_tag: str) -> Clan:
        
        formatted_tag = self._format_tag(clan_tag)
        
        try:
            data = self._make_request(f"clans/{formatted_tag}")
            return Clan.from_dict(data)
        except APIError as e:
            if e.status_code == 404:
                raise ClanNotFound(clan_tag)
            raise
    
    def get_clan_members(self, clan_tag: str) -> List[ClanMember]:

        formatted_tag = self._format_tag(clan_tag)
        
        try:
            data = self._make_request(f"clans/{formatted_tag}/members")
            return [ClanMember.from_dict(member) for member in data.get('items', [])]
        except APIError as e:
            if e.status_code == 404:
                raise ClanNotFound(clan_tag)
            raise
    
    def get_clan_war(self, clan_tag: str) -> War:

        formatted_tag = self._format_tag(clan_tag)
        
        try:
            data = self._make_request(f"clans/{formatted_tag}/currentwar")
            return War.from_dict(data)
        except APIError as e:
            if e.status_code == 404:
                raise ClanNotFound(clan_tag)
            raise
    
    def get_clan_warlog(self, clan_tag: str, limit: Optional[int] = None) -> List[War]:

        formatted_tag = self._format_tag(clan_tag)
        endpoint = f"clans/{formatted_tag}/warlog"
        
        if limit:
            endpoint += f"?limit={limit}"
        
        try:
            data = self._make_request(endpoint)
            return [War.from_dict(war) for war in data.get('items', [])]
        except APIError as e:
            if e.status_code == 404:
                raise ClanNotFound(clan_tag)
            raise
    
    # Search Methods
    def search_clans(self, 
                    name: Optional[str] = None,
                    war_frequency: Optional[str] = None,
                    location_id: Optional[int] = None,
                    min_members: Optional[int] = None,
                    max_members: Optional[int] = None,
                    min_clan_points: Optional[int] = None,
                    min_clan_level: Optional[int] = None,
                    limit: Optional[int] = None) -> List[Clan]:

        params = []
        
        if name:
            params.append(f"name={quote(name)}")
        if war_frequency:
            params.append(f"warFrequency={war_frequency}")
        if location_id:
            params.append(f"locationId={location_id}")
        if min_members:
            params.append(f"minMembers={min_members}")
        if max_members:
            params.append(f"maxMembers={max_members}")
        if min_clan_points:
            params.append(f"minClanPoints={min_clan_points}")
        if min_clan_level:
            params.append(f"minClanLevel={min_clan_level}")
        if limit:
            params.append(f"limit={limit}")
        
        endpoint = "clans"
        if params:
            endpoint += "?" + "&".join(params)
        
        data = self._make_request(endpoint)
        return [Clan.from_dict(clan) for clan in data.get('items', [])]
    
    # League Methods
    def get_leagues(self) -> List[League]:

        data = self._make_request("leagues")
        return [League.from_dict(league) for league in data.get('items', [])]
    
    def get_league_seasons(self, league_id: int) -> List[Dict[str, Any]]:

        data = self._make_request(f"leagues/{league_id}/seasons")
        return data.get('items', [])
    
    def get_league_season_rankings(self, league_id: int, season_id: str, limit: Optional[int] = None) -> List[Player]:

        endpoint = f"leagues/{league_id}/seasons/{season_id}"
        if limit:
            endpoint += f"?limit={limit}"
        
        data = self._make_request(endpoint)
        return [Player.from_dict(player) for player in data.get('items', [])]
    
    # Location Methods
    def get_locations(self) -> List[Location]:

        data = self._make_request("locations")
        return [Location.from_dict(location) for location in data.get('items', [])]
    
    def get_location_clan_rankings(self, location_id: int, limit: Optional[int] = None) -> List[Clan]:
        
        endpoint = f"locations/{location_id}/rankings/clans"
        if limit:
            endpoint += f"?limit={limit}"
        
        data = self._make_request(endpoint)
        return [Clan.from_dict(clan) for clan in data.get('items', [])]
    
    def get_location_player_rankings(self, location_id: int, limit: Optional[int] = None) -> List[Player]:
        
        endpoint = f"locations/{location_id}/rankings/players"
        if limit:
            endpoint += f"?limit={limit}"
        
        data = self._make_request(endpoint)
        return [Player.from_dict(player) for player in data.get('items', [])]
    
    # Global Rankings
    def get_global_player_rankings(self, limit: Optional[int] = None) -> List[Player]:
        """
        Get global player rankings.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of Player objects with global ranking information
        """
        endpoint = "locations/global/rankings/players"
        if limit:
            endpoint += f"?limit={limit}"
        
        data = self._make_request(endpoint)
        return [Player.from_dict(player) for player in data.get('items', [])]
    
    def get_global_clan_rankings(self, limit: Optional[int] = None) -> List[Clan]:
        
        endpoint = "locations/global/rankings/clans"
        if limit:
            endpoint += f"?limit={limit}"
        
        data = self._make_request(endpoint)
        return [Clan.from_dict(clan) for clan in data.get('items', [])]