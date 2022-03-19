__pragma__('noalias', 'undefined')

from room_manager.abstract import AbstractRoomManager
from utils import get_first_spawn
from utils import search_room


class RoomManagerRCL1(AbstractRoomManager):
    MAX_HARVESTERS = {
        0: 1,
        1: 3, # 6?
        2: 8,
    }  # map from source count to number of harvesters
    ROOM_HARVESTERS = {
        'W26N2': 6,
        'W26N3': 6,
        'W25N2': 4,
    }
    def spawn_creeps(self):
        room = self.room
        spawn = get_first_spawn(room)
        if not spawn:
            return
        if room.energyCapacityAvailable < 1300 and len(Game.rooms) >= 2:
            return  # we are being bootstrapped by someone else, we hope
        if not spawn.spawning:
            sources = search_room(room, FIND_SOURCES)
            desired_miners = len(sources)
            if room.name == 'W26N3':
                desired_miners =  2*len(sources)
            if len(sources) == 1 and self.creep_registry.count_of_type(room, 'miner') < desired_miners:
                miner_containers, source_to_controller_paths, map_size = self.get_miner_container_positions(sources)
                point = miner_containers[0]
                for s in room.lookForAt(LOOK_STRUCTURES, point.x, point.y):
                    if s.structureType == STRUCTURE_CONTAINER and s.hits >= 1:
                        if room.energyAvailable >= 300:  # wait until source is full (there are no extensions)
                            spawn.createCreep([WORK, WORK, MOVE, MOVE], "", {'cls': 'miner'})
                        return
            max_harvesters = self.ROOM_HARVESTERS[room.name]
            if max_harvesters == undefined:
                max_harvesters = self.MAX_HARVESTERS[len(sources)]
            if (self.creep_registry.count_of_type(room, 'harvester') + 8*self.creep_registry.count_of_type(room, 'upgrader')) < max_harvesters:  # keep spawning them, why not
                if room.energyAvailable >= 250:  # wait until source is full (there are no extensions)
                    spawn.createCreep([WORK, CARRY, MOVE, MOVE], "", {'cls': 'harvester'})

    def run_build(self):
        pass  # do literally nothing
