#!/usr/bin/env python3
"""
Data Display - Complete OpenTTD Game State Monitor
================================================================

This example demonstrates how to retrieve and display all available 
real-time game state data from an OpenTTD server, matching what's 
shown in the OpenTTD GUI.

Features Demonstrated:
- Real-time game date and calendar information
- Complete company and client listings
- Financial data for all companies
- Server configuration and map information  
- Vehicle statistics and tracking
- Economic indicators and performance metrics

Usage:
    python examples/data_display.py
"""

import time
import logging
import uuid
from pyttd import OpenTTDClient

# Set up clean logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Reduce protocol noise for cleaner output
logging.getLogger('pyttd.protocol').setLevel(logging.WARNING)
logging.getLogger('pyttd.connection').setLevel(logging.WARNING)


class OpenTTDDataMonitor:
    """OpenTTD game state data monitor"""
    
    def __init__(self, server="127.0.0.1", port=3979):
        self.unique_id = str(uuid.uuid4())[:8]
        self.client = OpenTTDClient(
            server=server,
            port=port,
            player_name=f"DataMonitor_{self.unique_id}",
            company_name=f"MonitorCorp_{self.unique_id}"
        )
        
    def connect_and_monitor(self):
        """Connect to server and start monitoring"""
        logger.info("Connecting to OpenTTD server...")
        
        # Set up event handlers
        self.client.on('game_joined', self.on_game_joined)
        
        success = self.client.connect()
        if not success:
            logger.error("Failed to connect to server")
            return False
            
        logger.info("Connected successfully!")
        return True
        
    def on_game_joined(self):
        """Called when we successfully join the game"""
        logger.info("Joined game! Starting data collection...")
        
        # Wait a moment for initial data packets to arrive
        time.sleep(3)
        
        # Display all available data
        self.display_comprehensive_data()
        
        # Send summary to chat
        self.broadcast_data_summary()
        
    def display_comprehensive_data(self):
        """Display all available game state data"""
        print("\n" + "=" * 80)
        print("OPENTTD GAME STATE DATA")
        print("=" * 80)
        
        # 1. Server and Connection Information
        self.display_server_info()
        
        # 2. Game Calendar and Time
        self.display_calendar_info()
        
        # 3. Map Information
        self.display_map_info()
        
        # 4. Company Information
        self.display_company_info()
        
        # 5. Client Information
        self.display_client_info()
        
        # 6. Financial Analysis
        self.display_financial_info()
        
        # 7. Vehicle Information
        self.display_vehicle_info()
        
        # 8. Economic Indicators
        self.display_economic_info()
        
        # 9. Performance Metrics
        self.display_performance_info()
        
        print("=" * 80)
        print("Data collection completed!")
        print("=" * 80 + "\n")
        
    def display_server_info(self):
        """Display server configuration and connection details"""
        print("\nSERVER INFORMATION")
        print("-" * 50)
        
        game_info = self.client.get_game_info()
        
        print(f"Server Name: {game_info.get('server_name', 'Unknown')}")
        print(f"Client ID: {game_info.get('client_id', 'Unknown')}")
        print(f"Connection Status: {game_info.get('status', 'Unknown')}")
        print(f"Game Synchronized: {game_info.get('synchronized', False)}")
        
        # Show real-time data availability
        has_real_data = hasattr(self.client, '_real_game_data') and self.client._real_game_data
        print(f"Real-time Data Available: {'Yes' if has_real_data else 'No'}")
        
    def display_calendar_info(self):
        """Display game calendar and time information"""
        print("\nCALENDAR & TIME INFORMATION")
        print("-" * 50)
        
        game_info = self.client.get_game_info()
        
        current_year = game_info.get('current_year', 'Unknown')
        start_year = game_info.get('start_year', 'Unknown')
        ticks_playing = game_info.get('ticks_playing', 0)
        
        print(f"Current Game Year: {current_year}")
        print(f"Game Started Year: {start_year}")
        if isinstance(current_year, int) and isinstance(start_year, int):
            years_playing = current_year - start_year
            print(f"Years Playing: {years_playing}")
        
        print(f"Game Ticks: {ticks_playing:,}" if isinstance(ticks_playing, int) else f"Game Ticks: {ticks_playing}")
        print(f"Calendar Date ID: {game_info.get('calendar_date', 'Unknown')}")
        
    def display_map_info(self):
        """Display map size and terrain information"""
        print("\n🗺️MAP INFORMATION")
        print("-" * 50)
        
        game_info = self.client.get_game_info()
        map_info = self.client.get_map_info()
        
        print(f"Map Size: {game_info.get('map_size', 'Unknown')}")
        
        if map_info:
            print(f"Map Width: {map_info.get('size_x', 'Unknown')}")
            print(f"Map Height: {map_info.get('size_y', 'Unknown')}")
            if 'landscape' in map_info:
                landscapes = {0: 'Temperate', 1: 'Arctic', 2: 'Tropical', 3: 'Toyland'}
                landscape_name = landscapes.get(map_info['landscape'], f"Unknown ({map_info['landscape']})")
                print(f"Landscape: {landscape_name}")
            if 'seed' in map_info:
                print(f"Map Seed: {map_info['seed']}")
                
    def display_company_info(self):
        """Display company information"""
        print("\nCOMPANY INFORMATION")
        print("-" * 50)
        
        game_info = self.client.get_game_info()
        companies = self.client.get_companies()
        
        # Summary
        companies_active = game_info.get('companies', len(companies))
        companies_max = game_info.get('companies_max', 'Unknown')
        print(f"Active Companies: {companies_active}/{companies_max}")
        
        # Our company
        our_company = self.client.get_our_company()
        our_company_id = self.client.game_state.company_id
        
        if our_company_id != 255:  # Not spectator
            print(f"Our Company ID: {our_company_id}")
            if our_company:
                print(f"Our Company Name: {getattr(our_company, 'name', 'Unknown')}")
        else:
            print("Status: Spectator")
            
        # Detailed company list
        if companies:
            print(f"\nDetailed Company List ({len(companies)} tracked):")
            for company_id, company_data in companies.items():
                name = company_data.get('name', f'Company {company_id}')
                manager = company_data.get('manager_name', 'Unknown')
                is_ai = company_data.get('is_ai', False)
                company_type = 'AI' if is_ai else 'Human'
                print(f"  {company_type} Company {company_id}: {name} (Manager: {manager})")
        else:
            print("No detailed company data available")
            
    def display_client_info(self):
        """Display client connection information"""
        print("\nCLIENT INFORMATION")
        print("-" * 50)
        
        game_info = self.client.get_game_info()
        clients = self.client.get_clients()
        
        # Summary
        clients_active = game_info.get('clients', len(clients))
        clients_max = game_info.get('clients_max', 'Unknown')
        spectators = game_info.get('spectators', 'Unknown')
        
        print(f"Connected Clients: {clients_active}/{clients_max}")
        print(f"Spectators: {spectators}")
        
        # Detailed client list
        if clients:
            print(f"\nDetailed Client List ({len(clients)} tracked):")
            for client_id, client_data in clients.items():
                name = client_data.get('name', f'Client {client_id}')
                company_id = client_data.get('company_id', 'Unknown')
                
                if company_id == 255:
                    status = "Spectator"
                elif company_id == 254:
                    status = "Creating Company"
                else:
                    status = f"Company {company_id}"
                    
                print(f"  Client {client_id}: {name} ({status})")
        else:
            print("No detailed client data available")
            
    def display_financial_info(self):
        """Display financial information and company finances"""
        print("\nFINANCIAL INFORMATION")
        print("-" * 50)
        
        # Our company finances
        finances = self.client.get_company_finances()
        if finances:
            print("Our Company Finances:")
            for key, value in finances.items():
                if isinstance(value, (int, float)):
                    if 'rate' in key.lower():
                        print(f"  {key.replace('_', ' ').title()}: {value}%")
                    else:
                        print(f"  {key.replace('_', ' ').title()}: £{value:,}")
                else:
                    print(f"  {key.replace('_', ' ').title()}: {value}")
        else:
            print("No personal financial data available (may be spectator)")
            
        # Performance data
        performance = self.client.get_company_performance()
        if performance:
            print("\nCompany Performance:")
            for key, value in performance.items():
                if isinstance(value, (int, float)):
                    if 'value' in key.lower() or 'money' in key.lower():
                        print(f"  {key.replace('_', ' ').title()}: £{value:,}")
                    elif 'rate' in key.lower():
                        print(f"  {key.replace('_', ' ').title()}: {value}%")
                    else:
                        print(f"  {key.replace('_', ' ').title()}: {value}")
                else:
                    print(f"  {key.replace('_', ' ').title()}: {value}")
                    
    def display_vehicle_info(self):
        """Display vehicle statistics and information"""
        print("\nVEHICLE INFORMATION")
        print("-" * 50)
        
        # Game-wide vehicle count
        game_info = self.client.get_game_info()
        total_vehicles = game_info.get('vehicles', 0)
        print(f"Total Vehicles in Game: {total_vehicles}")
        
        # Our vehicles
        our_vehicles = self.client.get_our_vehicles()
        print(f"Our Vehicles: {len(our_vehicles)}")
        
        if our_vehicles:
            print("Our Vehicle List:")
            for vehicle_id, vehicle_data in our_vehicles.items():
                vehicle_type = vehicle_data.get('type', 'Unknown')
                vehicle_name = vehicle_data.get('name', f'Vehicle {vehicle_id}')
                print(f"  {vehicle_type} {vehicle_id}: {vehicle_name}")
                
        # Vehicle statistics
        vehicle_stats = self.client.get_vehicle_statistics()
        if vehicle_stats:
            print("\nVehicle Statistics:")
            for key, value in vehicle_stats.items():
                if isinstance(value, dict):
                    print(f"  {key.replace('_', ' ').title()}:")
                    for sub_key, sub_value in value.items():
                        print(f"    {sub_key}: {sub_value}")
                else:
                    if isinstance(value, (int, float)) and 'profit' in key.lower():
                        print(f"  {key.replace('_', ' ').title()}: £{value:,}")
                    else:
                        print(f"  {key.replace('_', ' ').title()}: {value}")
                        
    def display_economic_info(self):
        """Display economic indicators and market information"""
        print("\nECONOMIC INFORMATION")
        print("-" * 50)
        
        economic_status = self.client.get_economic_status()
        if economic_status:
            print("Economic Indicators:")
            for key, value in economic_status.items():
                if isinstance(value, (int, float)):
                    if 'rate' in key.lower():
                        print(f"  {key.replace('_', ' ').title()}: {value}%")
                    elif 'loan' in key.lower() or 'money' in key.lower():
                        print(f"  {key.replace('_', ' ').title()}: £{value:,}")
                    else:
                        print(f"  {key.replace('_', ' ').title()}: {value}")
                else:
                    print(f"  {key.replace('_', ' ').title()}: {value}")
        else:
            print("No economic data available")
            
        # Loan interest calculation
        try:
            interest = self.client.calculate_loan_interest()
            print(f"Current Loan Interest (Annual): £{interest:,}")
        except:
            print("Loan interest calculation unavailable")
            
    def display_performance_info(self):
        """Display performance metrics and game statistics"""
        print("\nPERFORMANCE METRICS")
        print("-" * 50)
        
        # Check if we can afford various things
        test_amounts = [10000, 50000, 100000, 500000, 1000000]
        print("Affordability Analysis:")
        for amount in test_amounts:
            can_afford = self.client.can_afford(amount)
            status = "Affordable" if can_afford else "❌ Too expensive"
            print(f"  £{amount:,}: {status}")
            
        # Construction cost estimates
        print("\nConstruction Cost Estimates:")
        try:
            rail_cost = self.client.estimate_construction_cost((10, 10), (20, 20), "rail")
            print(f"  Rail (10,10) to (20,20): £{rail_cost:,}")
        except:
            print("  Rail cost estimation unavailable")
            
        # Auto-management recommendation
        try:
            auto_mgmt = self.client.auto_manage_company()
            if auto_mgmt and isinstance(auto_mgmt, dict):
                print(f"\nAI Recommendation: {auto_mgmt.get('recommendation', 'None')}")
                if 'actions_taken' in auto_mgmt:
                    actions = auto_mgmt['actions_taken']
                    if actions:
                        print("Suggested Actions:")
                        for action in actions:
                            print(f"  - {action}")
        except:
            print("\nAuto-management analysis unavailable")
            
    def broadcast_data_summary(self):
        """Send a summary of key data to game chat"""
        game_info = self.client.get_game_info()
        
        # Create concise summary
        year = game_info.get('current_year', '?')
        companies = game_info.get('companies', '?')
        clients = game_info.get('clients', '?')
        
        summary = f"Game Data: Year {year}, {companies} companies, {clients} clients connected"
        self.client.send_chat(summary)
        
    def run(self, duration=30):
        """Run the data monitor for specified duration"""
        try:
            if not self.connect_and_monitor():
                return
                
            logger.info(f"Monitoring for {duration} seconds...")
            
            # Keep connection alive
            start_time = time.time()
            while self.client.is_connected() and (time.time() - start_time) < duration:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("👋 Monitoring interrupted by user")
        finally:
            if self.client.is_connected():
                logger.info("Disconnecting...")
                self.client.disconnect()
            logger.info("Data monitoring completed!")


def main():
    """Main entry point"""
    print("OpenTTD Data Display")
    print("=" * 60)
    print("This script connects to an OpenTTD server and displays")
    print("all available real-time game state information.")
    print("=" * 60 + "\n")
    
    # Create and run monitor
    monitor = OpenTTDDataMonitor()
    monitor.run(duration=30)


if __name__ == "__main__":
    main()