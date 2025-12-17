#!/usr/bin/env python3
"""
Aviation ADS-B Data Checker
Monitors and displays aviation ADS-B (Automatic Dependent Surveillance-Broadcast) data 
from the most recent time period.
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import time


class ADSBChecker:
    """Checks aviation ADS-B data from recent time periods."""
    
    # Using OpenSky Network free API
    BASE_URL = "https://opensky-network.org/api"
    
    def __init__(self, lookback_minutes: int = 15):
        """
        Initialize the ADS-B checker.
        
        Args:
            lookback_minutes: How far back to look for data (default: 15 minutes)
        """
        self.lookback_minutes = lookback_minutes
        self.session = requests.Session()
    
    def get_recent_flights(self) -> List[Dict[str, Any]]:
        """
        Fetch recent flight data from the most recent period.
        
        Returns:
            List of flight data dictionaries
        """
        try:
            # Calculate time window
            now = datetime.utcnow()
            start_time = int((now - timedelta(minutes=self.lookback_minutes)).timestamp())
            end_time = int(now.timestamp())
            
            print(f"Fetching ADS-B data from {self.lookback_minutes} minutes ago...")
            print(f"Time range: {datetime.fromtimestamp(start_time)} to {datetime.fromtimestamp(end_time)}")
            
            # Fetch states from OpenSky API
            url = f"{self.BASE_URL}/states/all"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            states = data.get('states', [])
            
            # Filter and format flight data
            flights = []
            for state in states:
                if state[0] is not None:  # Only include aircraft with callsigns
                    flight = {
                        'callsign': state[1].strip() if state[1] else 'Unknown',
                        'icao24': state[0],
                        'country': state[2],
                        'latitude': state[5],
                        'longitude': state[6],
                        'altitude': state[7],
                        'velocity': state[9],
                        'heading': state[10],
                        'vertical_rate': state[11],
                        'timestamp': datetime.fromtimestamp(state[3]).isoformat()
                    }
                    flights.append(flight)
            
            return flights
            
        except requests.RequestException as e:
            print(f"Error fetching ADS-B data: {e}")
            return []
    
    def display_flights(self, flights: List[Dict[str, Any]]) -> None:
        """
        Display flight information in a formatted table.
        
        Args:
            flights: List of flight data
        """
        if not flights:
            print("No aircraft data available")
            return
        
        print(f"\n{'Callsign':<10} {'Country':<20} {'Altitude':<10} {'Velocity':<10} {'Heading':<10}")
        print("-" * 70)
        
        for flight in flights[:50]:  # Show top 50 flights
            callsign = flight['callsign']
            country = flight['country'] or 'Unknown'
            altitude = f"{flight['altitude']:.0f}m" if flight['altitude'] else 'N/A'
            velocity = f"{flight['velocity']:.1f}m/s" if flight['velocity'] else 'N/A'
            heading = f"{flight['heading']:.0f}°" if flight['heading'] is not None else 'N/A'
            
            print(f"{callsign:<10} {country:<20} {altitude:<10} {velocity:<10} {heading:<10}")
        
        if len(flights) > 50:
            print(f"\n... and {len(flights) - 50} more aircraft")
        
        print(f"\nTotal aircraft tracked: {len(flights)}")
    
    def save_data(self, flights: List[Dict[str, Any]], filename: str = None) -> None:
        """
        Save flight data to a JSON file.
        
        Args:
            flights: List of flight data
            filename: Output filename (default: adsb_data_TIMESTAMP.json)
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"adsb_data_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(flights, f, indent=2)
        
        print(f"\nData saved to {filename}")
    
    def run_continuous(self, interval_seconds: int = 60) -> None:
        """
        Run continuous monitoring of ADS-B data.
        
        Args:
            interval_seconds: Interval between checks (default: 60 seconds)
        """
        try:
            iteration = 0
            while True:
                iteration += 1
                print(f"\n{'='*70}")
                print(f"Check #{iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print('='*70)
                
                flights = self.get_recent_flights()
                self.display_flights(flights)
                
                print(f"\nNext check in {interval_seconds} seconds. Press Ctrl+C to stop.")
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped.")


def main():
    """Main entry point for the ADS-B checker."""
    import sys
    
    # Parse command line arguments
    lookback = 15  # Default: 15 minutes
    continuous = False
    interval = 60  # Default: 60 seconds
    save_data = False
    
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg.startswith('--lookback='):
                lookback = int(arg.split('=')[1])
            elif arg == '--continuous':
                continuous = True
            elif arg.startswith('--interval='):
                interval = int(arg.split('=')[1])
            elif arg == '--save':
                save_data = True
            elif arg == '--help':
                print("""
Usage: python adsb_checker.py [OPTIONS]

Options:
  --lookback=N       Look back N minutes (default: 15)
  --continuous       Run continuous monitoring
  --interval=N       Check interval in seconds (default: 60)
  --save             Save data to JSON file
  --help             Show this help message
                """)
                return
    
    checker = ADSBChecker(lookback_minutes=lookback)
    
    if continuous:
        checker.run_continuous(interval_seconds=interval)
    else:
        flights = checker.get_recent_flights()
        checker.display_flights(flights)
        
        if save_data:
            checker.save_data(flights)


if __name__ == "__main__":
    main()
