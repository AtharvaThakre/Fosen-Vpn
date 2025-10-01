import json
import random
from typing import Dict, List, Tuple

class VPNServerLocation:
    """Manages VPN server locations and countries"""
    
    def __init__(self):
        self.locations = {
            "United States": {
                "servers": [
                    {"name": "US-East-1", "city": "New York", "ip": "198.51.100.10", "load": 45},
                    {"name": "US-East-2", "city": "Miami", "ip": "198.51.100.11", "load": 32},
                    {"name": "US-West-1", "city": "Los Angeles", "ip": "198.51.100.12", "load": 67},
                    {"name": "US-West-2", "city": "San Francisco", "ip": "198.51.100.13", "load": 28},
                    {"name": "US-Central", "city": "Chicago", "ip": "198.51.100.14", "load": 52}
                ],
                "flag": "🇺🇸"
            },
            "United Kingdom": {
                "servers": [
                    {"name": "UK-London-1", "city": "London", "ip": "203.0.113.20", "load": 41},
                    {"name": "UK-London-2", "city": "London", "ip": "203.0.113.21", "load": 35},
                    {"name": "UK-Manchester", "city": "Manchester", "ip": "203.0.113.22", "load": 28}
                ],
                "flag": "🇬🇧"
            },
            "Germany": {
                "servers": [
                    {"name": "DE-Frankfurt-1", "city": "Frankfurt", "ip": "203.0.113.30", "load": 38},
                    {"name": "DE-Frankfurt-2", "city": "Frankfurt", "ip": "203.0.113.31", "load": 45},
                    {"name": "DE-Berlin", "city": "Berlin", "ip": "203.0.113.32", "load": 33}
                ],
                "flag": "🇩🇪"
            },
            "Japan": {
                "servers": [
                    {"name": "JP-Tokyo-1", "city": "Tokyo", "ip": "203.0.113.40", "load": 55},
                    {"name": "JP-Tokyo-2", "city": "Tokyo", "ip": "203.0.113.41", "load": 62},
                    {"name": "JP-Osaka", "city": "Osaka", "ip": "203.0.113.42", "load": 43}
                ],
                "flag": "🇯🇵"
            },
            "Canada": {
                "servers": [
                    {"name": "CA-Toronto", "city": "Toronto", "ip": "203.0.113.50", "load": 29},
                    {"name": "CA-Vancouver", "city": "Vancouver", "ip": "203.0.113.51", "load": 36}
                ],
                "flag": "🇨🇦"
            },
            "France": {
                "servers": [
                    {"name": "FR-Paris-1", "city": "Paris", "ip": "203.0.113.60", "load": 44},
                    {"name": "FR-Paris-2", "city": "Paris", "ip": "203.0.113.61", "load": 51}
                ],
                "flag": "🇫🇷"
            },
            "Netherlands": {
                "servers": [
                    {"name": "NL-Amsterdam-1", "city": "Amsterdam", "ip": "203.0.113.70", "load": 39},
                    {"name": "NL-Amsterdam-2", "city": "Amsterdam", "ip": "203.0.113.71", "load": 47}
                ],
                "flag": "🇳🇱"
            },
            "Singapore": {
                "servers": [
                    {"name": "SG-Singapore-1", "city": "Singapore", "ip": "203.0.113.80", "load": 58},
                    {"name": "SG-Singapore-2", "city": "Singapore", "ip": "203.0.113.81", "load": 41}
                ],
                "flag": "🇸🇬"
            },
            "Australia": {
                "servers": [
                    {"name": "AU-Sydney", "city": "Sydney", "ip": "203.0.113.90", "load": 34},
                    {"name": "AU-Melbourne", "city": "Melbourne", "ip": "203.0.113.91", "load": 42}
                ],
                "flag": "🇦🇺"
            },
            "Switzerland": {
                "servers": [
                    {"name": "CH-Zurich", "city": "Zurich", "ip": "203.0.113.100", "load": 25}
                ],
                "flag": "🇨🇭"
            }
        }
        
        # Simulate server loads changing over time
        self._update_server_loads()
    
    def _update_server_loads(self):
        """Simulate dynamic server load changes"""
        for country in self.locations.values():
            for server in country["servers"]:
                # Add some randomness to server loads
                server["load"] += random.randint(-5, 5)
                server["load"] = max(10, min(90, server["load"]))  # Keep between 10-90%
    
    def get_countries(self) -> List[str]:
        """Get list of available countries"""
        return list(self.locations.keys())
    
    def get_servers_by_country(self, country: str) -> List[Dict]:
        """Get servers for a specific country"""
        if country in self.locations:
            return self.locations[country]["servers"]
        return []
    
    def get_best_server(self, country: str = None) -> Tuple[str, Dict]:
        """Get the best server (lowest load) for a country or globally"""
        if country and country in self.locations:
            servers = self.locations[country]["servers"]
            best_server = min(servers, key=lambda x: x["load"])
            return country, best_server
        else:
            # Find globally best server
            best_country = None
            best_server = None
            min_load = 100
            
            for country_name, country_data in self.locations.items():
                for server in country_data["servers"]:
                    if server["load"] < min_load:
                        min_load = server["load"]
                        best_server = server
                        best_country = country_name
            
            return best_country, best_server
    
    def get_country_flag(self, country: str) -> str:
        """Get flag emoji for country"""
        if country in self.locations:
            return self.locations[country]["flag"]
        return "🌍"
    
    def get_server_info(self, country: str, server_name: str) -> Dict:
        """Get detailed info for a specific server"""
        if country in self.locations:
            servers = self.locations[country]["servers"]
            for server in servers:
                if server["name"] == server_name:
                    return server
        return {}
    
    def simulate_ping(self, server_ip: str) -> int:
        """Simulate ping time to server (in ms)"""
        # Simulate different ping times based on "location"
        base_ping = {
            "198.51.100": 25,  # US servers
            "203.0.113.2": 85,  # UK servers  
            "203.0.113.3": 95,  # German servers
            "203.0.113.4": 180, # Japan servers
            "203.0.113.5": 45,  # Canada servers
            "203.0.113.6": 105, # France servers
            "203.0.113.7": 90,  # Netherlands servers
            "203.0.113.8": 220, # Singapore servers
            "203.0.113.9": 195, # Australia servers
            "203.0.113.10": 110 # Switzerland servers
        }
        
        # Get base ping from IP prefix
        for prefix, ping in base_ping.items():
            if server_ip.startswith(prefix):
                return ping + random.randint(-10, 20)
        
        return random.randint(50, 200)
    
    def get_location_stats(self) -> Dict:
        """Get statistics for all locations"""
        stats = {}
        for country, data in self.locations.items():
            total_servers = len(data["servers"])
            avg_load = sum(s["load"] for s in data["servers"]) / total_servers
            stats[country] = {
                "servers": total_servers,
                "avg_load": round(avg_load, 1),
                "flag": data["flag"]
            }
        return stats