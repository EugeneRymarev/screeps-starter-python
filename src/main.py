from room_manager import MANAGER_REGISTRY
from creeps import CREEP_CLASSES

# defs is a package which claims to export all constants and some JavaScript objects, but in reality does
#  nothing. This is useful mainly when using an editor like PyCharm, so that it 'knows' that things like Object, Creep,
#  Game, etc. do exist.
from defs import *

# These are currently required for Transcrypt in order to use the following names in JavaScript.
# Without the 'noalias' pragma, each of the following would be translated into something like 'py_Infinity' or
#  'py_keys' in the output file.
__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


class CreepRegistry:
    def __init__(self):
        self.by_room = {}
    def count(self, room):
        if room not in self.by_room:
            return 0
        return len(self.by_room[room])
    def count_of_type(self, room, creep_type):
        return len(self.list_of_type(room, creep_type))
    def list_of_type(self, room, creep_type):
        result = []
        if room in self.by_room:
            room_creeps = self.by_room[room]
            for creep in room_creeps:
                if creep.memory.cls == creep_type:
                    result.append(creep)
        return result
    def register(self, room, creep):
        if room not in self.by_room:
            self.by_room[room] = set()
        self.by_room[room].add(creep)


def main():
    """
    Main game logic loop.
    """
    if Game.cpu.bucket == 10000:
        Game.cpu.generatePixel()

    cpustats = {}
    global cpustats
    imports = Game.cpu.getUsed()
    creep_registry = CreepRegistry()

    all_actions = []
    # Register each creep
    creeps_to_do = []
    for name in Object.keys(Game.creeps):
        #if name == 'Stella':
        #    # Game.creeps['Stella'].moveTo(Game.creeps['Stella'].room.controller)
        #    # Game.creeps['Stella'].signController(Game.creeps['Stella'].room.controller, '')
        #    continue
        creep = Game.creeps[name]
        creep_registry.register(creep.room, creep)
        if creep.spawning:
            continue
        creeps_to_do.append(creep)

    my_rooms = set()  # TODO: cache my rooms in RAM like a pro
    for name in Object.keys(Game.rooms):
        my_rooms.add(Game.rooms[name])

    registry_time = Game.cpu.getUsed() - imports

    # Run each creep
    hostiles = {}
    for creep in creeps_to_do:
        if not creep.my:
            continue  # wtf
        creep_class = CREEP_CLASSES[creep.memory.cls]
        if not creep_class:
            #print('ERROR, NO CREEP CLASS FOR', creep.memory.cls)
            creep_class = CREEP_CLASSES['harvester']
        #print('running', creep_class.__name__, 'for', creep)
        actions = creep_class(creep, creep.name, creep_registry).run()
        #print('actions for', creep, 'are', actions)
        all_actions.append(actions)
        if creep.name == 'Jordyn':
            for action in actions:
                print('action', action)

    creeps_time = Game.cpu.getUsed() - registry_time - imports

    #print('creeps done')
    # Get the number of our creeps in the room.
    #num_creeps = _.sum(Game.creeps, lambda c: c.pos.roomName == spawn.pos.roomName)

    for room in my_rooms:
        #print('ROOM', room)
        if not room.controller or not room.controller.my:
            continue
        manager_class = MANAGER_REGISTRY[room.controller.level]
        manager = manager_class(room, creep_registry, True)
        #print("before", manager_class.__name__, room)
        all_actions.extend(manager.run())

        # TODO: cache tower list
        towers = []
        for s in room.find(FIND_MY_STRUCTURES):
            if s.structureType != STRUCTURE_TOWER:
                continue
            towers.append(s)

        busy_tower_ids = set()
        for creep in room.find(FIND_HOSTILE_CREEPS):
            print('hostile creep!', creep)
            for tower in towers:
                tower.attack(creep)  # TODO: action
                busy_tower_ids.add(tower.id)
            break

        for s in room.find(FIND_STRUCTURES):
            if s.structureType != STRUCTURE_ROAD:  # or room.name != 'W25N3':
                continue
            if s.hits <= s.hitsMax-1000:
                for tower in towers:
                    if tower.id in busy_tower_ids or tower.store[RESOURCE_ENERGY] < 10:
                        continue
                    if s.hits <= 500:
                        print('WARNING: tower performing emergency repairs', room.name, s, s.id, s.hits, s.hitsMax, tower)
                    tower.repair(s)  # TODO: action with priority
                    busy_tower_ids.add(tower.id)
                    break
            if len(towers) == len(busy_tower_ids):
                break

    #Game.rooms['W27N1'].visual.circle(10,20).line(0,0,10,20)
    #room = Game.rooms['W27N1']
    #MANAGER_REGISTRY[2](room, room.name, creep_registry, False).run()

    actions_cost = execute_actions(all_actions)
    used = Game.cpu.getUsed()
    print(
        '-------- total:', round(used, 3),
        'imp:', round(imports, 3),
        'reg:', round(registry_time, 3),
        'crp:', round(creeps_time, 3),
        'act:', round(actions_cost, 3),
        'code:', round(used-imports-actions_cost, 3),
    )
    if Game.time % 1500 == 0:
        for name in Object.keys(Memory.creeps):
            if not Game.creeps[name]:
                print('Clearing non-existing creep memory(powered by python™): ' + name)
                del Memory.creeps[name]

    #<font color="red"></font>

def execute_actions(all_actions):
    all_actions.sort(key=lambda action_set: max(action.priority for action in action_set), reversed=True)
    total = 0
    for action_set in all_actions:
        if Game.cpu.tickLimit < len(action_set)*0.2:  # TODO: this is actually not how the game works: the limit only affects the code exection. You can burn the entire bucket on actions in a single tick, if you want, just don't go over tickLimit with the code that schedules them
            print('=== WARNING === ran out of CPU before running', action_set, 'total actions', len(all_actions), 'executed', total / 0.2)
            break
        for action in action_set:
            action.run()
            total += 0.2
    return total


module.exports.loop = main
