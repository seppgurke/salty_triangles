import hlt
import math
from collections import OrderedDict
import logging

# GAME START
game = hlt.Game("salty_triangles")
# Then we print our start message to the logs
logging.info("Das Salz probiert es!")


while True:
    # TURN START - Update markiert neuen Spielzug
    game_map = game.update_map()
    command_queue = []

    team_ships = game_map.get_me().all_ships()
    enemy_ships = [ship for ship in game_map._all_ships() if ship not in team_ships]


    for ship in team_ships:
        # If the ship is docked
        if ship.docking_status != ship.DockingStatus.UNDOCKED:
            # Skip this ship
            continue
        # Alle möglichen Zielobjekte erfassen
        Objekte = game_map.nearby_entities_by_distance(ship)
        # Dict sortieren
        Objekte = OrderedDict(sorted(Objekte.items(), key=lambda t: t[0]))
        # 15 wichtigsten Objekte aus Dict in eine Lsite übertragen
        Objekte_Liste = []
        i = 0
        for dis, entity in Objekte.items():
            logging.info(entity)
            for ent in entity:
                # eigene Schiffe sind keine Zielobjekte
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
                z = entity.radius * (1/ship.calculate_distance_between(entity))
                #ein unbesetzter
                if not entity.is_owned():
                    #z = entity.radius * (1/ship.calculate_distance_between(entity))
                    if z>z_alt:
                        wahl = entity
                        z_alt = z
                #ein eigener Planet
                elif entity.owner.id == game_map.get_me().id:
                    if len(entity._docked_ships) != entity.num_docking_spots:
                        #z = entity.radius * (1/ship.calculate_distance_between(entity)) 
                        if z>z_alt:
                            wahl = entity
                            z_alt = z
                #ein gegnerischer Planet
                else:
                    #z = entity.radius * (1/ship.calculate_distance_between(entity))
                    if z>z_alt:
                        wahl = entity
                        z_alt = z
            #ein gegnerisches Schiff
            else:
                z = 1/ship.calculate_distance_between(entity)
                if z>z_alt:
                    wahl = entity
                    z_alt = z

        #Handeln entscheiden je nach Entity-Art
        # Schiff ist noch zu weit entfernt
        if not ship.can_dock(wahl):
            navigate_command = ship.navigate(
            ship.closest_point_to(wahl),
            game_map,
            speed=int(hlt.constants.MAX_SPEED),
            ignore_ships=False)
            if navigate_command:
                command_queue.append(navigate_command)
        # Wahl ist ein ausreichend naher Planet
        elif wahl in game_map.all_planets() and ship.can_dock(wahl):
            # Docken falls kein gegnerischer Planet
            if wahl.owner == None or wahl.owner.id == game_map.get_me().id:
                command_queue.append(ship.dock(wahl))
            # Sudoku am Planeten begehen, falls gegnerisch
            else:
                navigate_command = ship.thrust(7,ship.calculate_angle_between(wahl))
                command_queue.append(navigate_command)


    # Send our set of commands to the Halite engine for this turn
    game.send_command_queue(command_queue)
    # TURN END
# GAME END
