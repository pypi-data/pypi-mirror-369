"""
WeatherLink API v2 Client

Main API client for accessing WeatherLink v2 meteorological and air quality data.
"""

import requests
import time
from typing import Dict, List, Optional


class WeatherLinkAPI:
    """
    WeatherLink API v2 client for accessing meteorological and air quality data.
    
    This class provides methods to authenticate with the WeatherLink API and retrieve
    station information, current weather data, and historical weather data.
    
    Attributes:
        api_key (str): WeatherLink API key
        api_secret (str): WeatherLink API secret
        base_url (str): Base URL for WeatherLink API v2
        demo_mode (bool): Whether to use demo mode
        demo_station_id (str): Default demo station ID
    """
    
    def __init__(self, api_key: str, api_secret: str, demo_mode: bool = False):
        """
        Initialize WeatherLink API client.
        
        Args:
            api_key (str): WeatherLink API key
            api_secret (str): WeatherLink API secret
            demo_mode (bool): Whether to use demo mode. If True, uses demo station
                            for educational/testing purposes. If False, uses real stations.
            
        Raises:
            ValueError: If api_key or api_secret is None or empty
        """
        if not api_key or not api_secret:
            raise ValueError("API key and secret are required")
            
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.weatherlink.com/v2"
        self.demo_mode = demo_mode
        self.demo_station_id = "9722cfc3-a4ef-47b9-befb-72f52592d6ed"
        
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make authenticated request to WeatherLink API.
        
        This is a private method that handles the authentication and request logic
        for all API calls. It automatically adds the API key to parameters and
        the API secret to headers.
        
        Args:
            endpoint (str): API endpoint (without base URL)
            params (dict, optional): Additional parameters for the request
            
        Returns:
            dict: JSON response from the API
            
        Raises:
            requests.exceptions.RequestException: If the API request fails
            requests.exceptions.HTTPError: If the API returns an HTTP error status
        """
        if params is None:
            params = {}
        
        # Add authentication
        params['api-key'] = self.api_key
        
        # Only add demo parameter if demo mode is enabled
        if self.demo_mode:
            params['demo'] = 'true'
        
        headers = {'X-Api-Secret': self.api_secret}
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(f"API request failed: {e}")
    
    def get_stations(self) -> List[Dict]:
        """
        Get list of available weather stations.
        
        Returns:
            list: List of station dictionaries containing station information
            
        Example:
            >>> api = WeatherLinkAPI(api_key, api_secret)
            >>> stations = api.get_stations()
            >>> print(f"Found {len(stations)} stations")
        """
        try:
            data = self._make_request('stations')
            return data.get('stations', [])
        except Exception as e:
            print(f"Error getting stations: {e}")
            return []
    
    def get_sensors(self) -> List[Dict]:
        """
        Get list of available sensors across all stations.
        
        Returns:
            list: List of sensor dictionaries containing sensor information
            
        Example:
            >>> api = WeatherLinkAPI(api_key, api_secret)
            >>> sensors = api.get_sensors()
            >>> print(f"Found {len(sensors)} sensors")
        """
        try:
            data = self._make_request('sensors')
            return data.get('sensors', [])
        except Exception as e:
            print(f"Error getting sensors: {e}")
            return []
    
    def get_current_data(self, station_id: Optional[str] = None) -> Dict:
        """
        Get current weather data from a station.
        
        Args:
            station_id (str, optional): Station ID. If None and demo_mode is True,
                                      uses demo station. If demo_mode is False,
                                      you must provide a station_id.
            
        Returns:
            dict: Current weather data from the station
            
        Raises:
            ValueError: If station_id is None and demo_mode is False
            
        Example:
            >>> api = WeatherLinkAPI(api_key, api_secret, demo_mode=True)
            >>> current = api.get_current_data()  # Uses demo station
            >>> 
            >>> api = WeatherLinkAPI(api_key, api_secret, demo_mode=False)
            >>> current = api.get_current_data("your_station_id")  # Uses your station
        """
        if station_id is None:
            if self.demo_mode:
                station_id = self.demo_station_id
            else:
                raise ValueError("station_id is required when demo_mode is False")
        
        try:
            return self._make_request(f'current/{station_id}')
        except Exception as e:
            print(f"Error getting current data: {e}")
            return {}
    
    def get_historic_data(self, 
                         station_id: Optional[str] = None, 
                         hours_back: int = 24,
                         start_timestamp: Optional[int] = None,
                         end_timestamp: Optional[int] = None) -> Dict:
        """
        Get historical weather data from a station.
        
        Note: The WeatherLink API demo has limitations for historical data.
        The maximum time range is 24 hours (86400 seconds) for demo mode.
        
        Args:
            station_id (str, optional): Station ID. If None and demo_mode is True,
                                      uses demo station. If demo_mode is False,
                                      you must provide a station_id.
            hours_back (int): Hours of historical data to retrieve (max 24 for demo)
            start_timestamp (int, optional): Start time as Unix timestamp
            end_timestamp (int, optional): End time as Unix timestamp
            
        Returns:
            dict: Historical weather data from the station
            
        Raises:
            ValueError: If station_id is None and demo_mode is False
            
        Example:
            >>> api = WeatherLinkAPI(api_key, api_secret, demo_mode=True)
            >>> historic = api.get_historic_data(hours_back=12)  # Uses demo station
            >>> 
            >>> api = WeatherLinkAPI(api_key, api_secret, demo_mode=False)
            >>> historic = api.get_historic_data("your_station_id", hours_back=168)  # 7 days
        """
        if station_id is None:
            if self.demo_mode:
                station_id = self.demo_station_id
            else:
                raise ValueError("station_id is required when demo_mode is False")
            
        # Apply demo limitations only in demo mode
        if self.demo_mode and hours_back > 24:
            print("Warning: Demo API limited to 24 hours. Adjusting to 24 hours.")
            hours_back = 24
            
        # Use provided timestamps or calculate from hours_back
        if start_timestamp is None or end_timestamp is None:
            end_time = int(time.time())
            start_time = end_time - (hours_back * 3600)
        else:
            start_time = start_timestamp
            end_time = end_timestamp
        
        params = {
            'start-timestamp': start_time,
            'end-timestamp': end_time
        }
        
        try:
            return self._make_request(f'historic/{station_id}', params)
        except Exception as e:
            print(f"Error getting historic data: {e}")
            return {}

    def get_station_info(self, station_id: Optional[str] = None) -> Dict:
        """
        Get detailed information about a specific station.
        
        Args:
            station_id (str, optional): Station ID. If None and demo_mode is True,
                                      uses demo station. If demo_mode is False,
                                      you must provide a station_id.
            
        Returns:
            dict: Station information including name, location, sensors, etc.
            
        Raises:
            ValueError: If station_id is None and demo_mode is False
        """
        if station_id is None:
            if self.demo_mode:
                station_id = self.demo_station_id
            else:
                raise ValueError("station_id is required when demo_mode is False")
        
        try:
            data = self._make_request(f'stations/{station_id}')
            stations = data.get('stations', [])
            return stations[0] if stations else {}
        except Exception as e:
            print(f"Error getting station info: {e}")
            return {}

    def get_sensors_info(self, sensor_id: str) -> Dict:
        """
        Get detailed information about a specific sensor.
        
        Args:
            sensor_id (str): Sensor ID (lsid)
            
        Returns:
            dict: Sensor information including type, location, capabilities, etc.
            
        Example:
            >>> api = WeatherLinkAPI(api_key, api_secret)
            >>> sensor_info = api.get_sensors_info("12345")
            >>> print(f"Sensor type: {sensor_info.get('sensor_type')}")
        """
        try:
            data = self._make_request(f'sensors/{sensor_id}')
            sensors = data.get('sensors', [])
            return sensors[0] if sensors else {}
        except Exception as e:
            print(f"Error getting sensor info: {e}")
            return {}

    def test_connection(self) -> bool:
        """
        Test the API connection and authentication.
        
        Returns:
            bool: True if connection successful, False otherwise
            
        Example:
            >>> api = WeatherLinkAPI(api_key, api_secret)
            >>> if api.test_connection():
            ...     print("API connection successful!")
            ... else:
            ...     print("API connection failed!")
        """
        try:
            stations = self.get_stations()
            return len(stations) > 0
        except Exception:
            return False
