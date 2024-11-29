import random
from backend.game_functions.tickets import Tickets
from backend.game_functions.database import Database


class Player:
    def __init__(self, name, player_type, location, is_computer=0):
        self.name = name  # Player's name
        self.type = player_type  # Player type: 0 for criminal, 1 for detective
        self.location = location  # Starting location
        self.is_computer = is_computer  # Whether the player is computer-controlled
        self.database = Database()  # Database instance
        self.id = None  # Player ID, to be set once the player is inserted into the database

    # Method to insert a new player into the database
    def insert_player(self):
        sql = f"""INSERT INTO player (screen_name, type, location, is_computer)
                  VALUES ('{self.name}', '{self.type}', '{self.location}', {self.is_computer})"""
        self.id = self.database.db_insert(sql)
        return self.id

    # Method to add a player to a game
    def add_player_to_game(self, game_id):
        sql = f"""INSERT INTO game_player (game_id, player_id) 
                  VALUES ('{game_id}', '{self.id}')"""
        self.database.db_insert(sql)

    # Method to get player information by screen name
    def get_player_info(self):
        sql = f"""
            SELECT player.id, player.screen_name, player.type, player.is_computer, player.location, airport.name, country.name, airport.latitude_deg, airport.longitude_deg 
            FROM player 
            LEFT JOIN airport ON player.location = airport.ident 
            LEFT JOIN country ON airport.iso_country = country.iso_country 
            WHERE screen_name = '{self.name}'
        """
        result = self.database.db_query(sql)
        if result:
            return {
                "id": result[0][0],
                "screen_name": result[0][1],
                "type": result[0][2],
                "is_computer": result[0][3],
                "location": result[0][4],
                "airport_name": result[0][5],
                "country_name": result[0][6],
                "latitude": result[0][7],
                "longitude": result[0][8]
            }
        return {}

    # Method to get all screen names of players
    def get_screen_names(self):
        sql = "SELECT screen_name FROM player"
        result = self.database.db_query(sql)
        return [row[0] for row in result]

    # Method to insert tickets for a player based on their type
    def insert_player_tickets(self):
        tickets = {
            0: [(1, 10), (2, 6), (3, 4)],  # Criminal
            1: [(1, 5), (2, 3), (3, 2)]  # Detective
        }

        for ticket_id, count in tickets.get(self.type, []):
            for _ in range(count):
                Tickets().insert_tickets(self.id, ticket_id)

    # Method for the criminal to choose a starting point
    def choose_criminal_starting_point(self, airports):
        if self.is_computer:
            selected_icao = random.choice(list(airports.keys()))
        else:
            selected_icao = list(airports.keys())[0]  # Placeholder for actual front-end selection logic

        self.location = selected_icao
        self.insert_player()  # Insert the player after determining the starting point
        self.insert_player_tickets()

        return self.id

    # Method to create a new player
    def create_new_player(self, player_type, name, location):
        max_char = 20
        existing_names = self.get_screen_names()

        if name not in existing_names and len(name) <= max_char:
            return Player(name, player_type, location, self.database)
        return None

    # Method to get the latest movement of a criminal
    def get_criminal_movements(self):
        sql = f"""
        SELECT player.screen_name, airport.name, country.name, past_movement.ticket_type
        FROM past_movement
        LEFT JOIN player ON past_movement.player_id = player.id
        LEFT JOIN airport ON past_movement.location = airport.ident
        LEFT JOIN country ON airport.iso_country = country.iso_country
        WHERE past_movement.player_id = '{self.id}'
        ORDER BY past_movement.id DESC
        LIMIT 1
        """
        result = self.database.db_query(sql)
        if result:
            return {
                "screen_name": result[0][0],
                "airport": result[0][1],
                "country": result[0][2],
                "ticket_type": result[0][3]
            }
        return {}

    # Method to show the locations of detectives
    def show_detective_locations(self, game_id):
        sql = f"""SELECT screen_name 
                  FROM player 
                  LEFT JOIN game_player ON player.id = game_player.player_id 
                  LEFT JOIN game on game_player.game_id = game.id 
                  WHERE game.id = '{game_id}'"""
        result = self.database.db_query(sql)
        if result:
            detective_names = [row[0] for row in result[-2:]]  # Get the last two detective names
            detective_infos = [Player(name, None, None, self.database).get_player_info() for name in detective_names]
            return detective_infos
        return []

    # Method to update the location of the player
    def update_location(self, location):
        sql = f"""
        UPDATE player
        SET location = '{location}'
        WHERE screen_name = '{self.name}'
        """
        self.database.db_update(sql)
        self.location = location

    def add_player_past_movement(self, location, ticket_id, player_id):

        # Add the ticket and player information to the database
        sql = f"""INSERT INTO past_movement (player_id, location, ticket_type) 
                  VALUES ('{player_id}', '{location}','{ticket_id}' )"""
        self.database.db_insert(sql)

        # After that delete the ticket from the tickets table
        result = Tickets().delete_ticket(ticket_id, player_id)
        if not result:
            return False

