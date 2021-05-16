"""
Welcome to your first Halite-II bot!

This bot's name is Settler. It's purpose is simple (don't expect it to win complex games :) ):
1. Initialize game
2. If a ship is not docked and there are unowned planets
2.a. Try to Dock in the planet if close enough
2.b If not, go towards the planet

Note: Please do not place print statements here as they are used to communicate with the Halite engine. If you need
to log anything use the logging module.
"""
# Let's start by importing the Halite Starter Kit so we can interface with the Halite engine
import hlt
import math
from collections import OrderedDict
import logging

# GAME START
# Here we define the bot's name as Settler and initialize the game, including communication with the Halite engine.
game = hlt.Game("Saltries")
# Then we print our start message to the logs
logging.info("Starting the winning bot!")


while True:
    # TURN START
    game_map = game.update_map()
    command_queue = []

    team_ships = game_map.get_me().all_ships()
    enemy_ships = [ship for ship in game_map._all_ships() if ship not in team_ships]


    for ship in team_ships:
        # If the ship is docked
        if ship.docking_status != ship.DockingStatus.UNDOCKED:
            # Skip this ship
            continue

        logging.info(game_map.get_me())
        Objekte = game_map.nearby_entities_by_distance(ship)
        Objekte = OrderedDict(sorted(Objekte.items(), key=lambda t: t[0]))
        Objekte_Liste = []
        i = 0
        for dis, entity in Objekte.items():
            logging.info(entity)
            for ent in entity:
                if ent in team_ships:
                    continue
                else:
                    Objekte_Liste.append(ent)
                    i = i+1
                logging.info(Objekte_Liste)
            if i>15:
                break

        #Objekt (wahl) höchster Wichtigkeit (z) erkennen
        z = 0
        z_alt = 0

        for entity in Objekte_Liste:
            #Wenn ent ein Planet ist
            if entity in game_map.all_planets():
                #ein unbesetzter
                if not entity.is_owned():
                    z = entity.radius * (1/ship.calculate_distance_between(entity))
                    if z>z_alt:
                        wahl = entity
                        z_alt = z
                #ein eigener Planet
                elif entity.owner.id == game_map.get_me().id:
                    if len(entity._docked_ships) != entity.num_docking_spots:
                        z = entity.radius * (1/ship.calculate_distance_between(entity)) * (1/entity.health)
                        if z>z_alt:
                            wahl = entity
                            z_alt = z
                #ein gegnerischer Planet
                else:
                    z = entity.radius * (1/ship.calculate_distance_between(entity))
                    if z>z_alt:
                        wahl = entity
                        z_alt = z
            #ein gegnerisches Schiff
            else:
                z = 1/ship.calculate_distance_between(entity)
                if z>z_alt:
                    wahl = entity
                    z_alt = z

        #Handeln entscheiden
        if not ship.can_dock(wahl):
            navigate_command = ship.navigate(
            ship.closest_point_to(wahl),
            game_map,
            speed=int(hlt.constants.MAX_SPEED),
            ignore_ships=False)
            if navigate_command:
                command_queue.append(navigate_command)
        elif wahl in game_map.all_planets() and ship.can_dock(wahl):
            if wahl.owner == None or wahl.owner.id == game_map.get_me().id:
                command_queue.append(ship.dock(wahl))
            else:
                navigate_command = ship.thrust(7,ship.calculate_angle_between(wahl))
                command_queue.append(navigate_command)


    # Send our set of commands to the Halite engine for this turn
    game.send_command_queue(command_queue)
    # TURN END
# GAME END
