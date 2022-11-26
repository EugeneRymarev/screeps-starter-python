from creeps.parts.carry import Carry
from creeps.parts.work import Work
from creeps.scheduled_action import ScheduledAction
from utils import points_to_path

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


class AbstractCreep:
    DEBUG = False
    REMOVE_FLAG_ON_ARRIVAL = True
    FILL_UP_BEFORE_LEAVING = False
    ICON = '?'
    def __init__(self, creep, namee, creep_registry):
        self.creep = creep
        self.creep_registry = creep_registry

    def __str__(self):
        return self.creep + '@' + self.creep.room.name

    @classmethod
    def energy(cls, creep):  # TODO other res
        return _.sum(creep.carry)

    def get_debug(self):
        return self.DEBUG or self.creep.memory.debug
    debug = property(get_debug)

    def get_smart_move_actions(self, where_pos):
        creep = self.creep
        if creep.pos.roomName == where_pos.roomName:  # just a regular single-room move
            return [ScheduledAction.moveTo(creep, where_pos)]

        limit = 10000
        if Game.cpu.tickLimit < limit/1000:
            print('WARNING:', creep.name, 'cannot pathfind, not enough cpu')
            return []
        result = PathFinder.search(
            creep.pos,
            where_pos,
            {
                'plainCost': 2,
                'swampCost': 10,
                'maxOps': limit,  # 1000 ops = 1 CPU
                #'maxRooms': 16,  # max 64
                #'maxCost': 123456,
            }
        )
        # result structure
        # path	An array of RoomPosition objects.
        # ops	Total number of operations performed before this path was calculated.
        # cost	The total cost of the path as derived from plainCost, swampCost and any given CostMatrix instances.
        # incomplete (flag)
        if result['ops'] >= 0.1*limit:
            print('WARNING: get_smart_move_actions() for', creep.name, 'used', result['ops'], 'mCPU to find path to', where_pos, 'in', where_pos.roomName)
        creep.memory.path = result['path']
        return [ScheduledAction.moveByPath(creep, creep.memory.path)]

    def pre_run(self):
        creep = self.creep
        if self.debug:
            creep.say(creep.name[:8] + self.ICON)

        if creep.memory.path != undefined:
            return [ScheduledAction.moveByPath(creep, points_to_path(creep.memory.path))]

        if creep.memory.target_flag != undefined:
            target_flag_name = creep.memory.target_flag
        else:
            target_flag_name = creep.name

        target_flag = Game.flags[target_flag_name]
        if target_flag:
            if creep.pos.isEqualTo(target_flag):
                if self.REMOVE_FLAG_ON_ARRIVAL:
                    target_flag.remove()
                else:
                    return []
            elif creep.pos.isNearTo(target_flag):
                structures = target_flag.pos.lookFor(LOOK_STRUCTURES)
                if len(structures) and structures[0].my:  # TODO: what if it's covered by a rampart?
                    if structures[0].structureType == STRUCTURE_SPAWN:
                        structures[0].recycleCreep(creep)
                        target_flag.remove()
                        return []
                    elif structures[0].structureType == STRUCTURE_TERMINAL or structures[0].structureType == STRUCTURE_STORAGE:
                        target_flag.remove()
                        return [ScheduledAction.transfer(creep, structures[0], RESOURCE_ENERGY)]  # TODO: dump all
            return self.get_smart_move_actions(target_flag.pos)

        if creep.memory.room != undefined and creep.memory.room != creep.room.name:
            target_room = Game.rooms[creep.memory.room]
            if self.FILL_UP_BEFORE_LEAVING and self.energy(creep) < creep.carryCapacity:
                pass  # don't go anywhere, fill up first
            elif target_room == undefined or True:  # TODO XXX smart actions inhibitor
                if creep.memory.wp_room != undefined:
                    if creep.room.name == creep.memory.wp_room:
                        del creep.memory.wp_room
                        return [] # just skip a tick
                    else:
                        target_room_name = creep.memory.wp_room
                elif creep.memory.wp_room2 != undefined:
                    if creep.room.name == creep.memory.wp_room2:
                        del creep.memory.wp_room2
                        return [] # just skip a tick
                    else:
                        target_room_name = creep.memory.wp_room2
                else:
                    target_room_name = creep.memory.room
                if target_room == undefined:
                    rp = __new__(RoomPosition(23, 23, target_room_name))
                else:
                    rp = target_room.controller.pos
                print(creep, 'is in', creep.room, 'but should be in', target_room_name, 'which we have no eyes on', rp)
                del creep.memory.source  # so that we don't end up getting back to hatchery after using current energy
                #return self.get_smart_move_actions(rp)
                return [ScheduledAction.moveTo(creep, rp)]  # TODO XXX smart actions inhibitor
            else:
                return self.get_smart_move_actions(target_room.controller.pos)

            #roompos = RoomPosition(24, 24, creep.memory.room)
            #print('roompos', roompos, creep.memory.room)
            #pos = {
            #    'range': 22,
            #    'pos': roompos,
            #}
            #return [ScheduledAction.moveTo(self.creep, pos)]

            #route = Game.map.findRoute(creep.room, target);
            #if len(route) > 0:
            #    exit = creep.pos.findClosestByPath(route[0].exit);
            #    return [ScheduledAction.moveTo(self.creep, exit]

    def run(self):
        override_actions = self.pre_run()
        if override_actions:
            return override_actions
        return self._run()

    def _run(self):
        pass  #raise NotImplementedError

    def class_exists(self, klass):
        return self.creep_registry.count_of_type(self.creep.room, klass) >= 1

    def total_creeps_in_room(self):
        return self.creep_registry.count(self.creep.room)

    def _get_nearby_repair_action(self, including_walls=False):
        creep = self.creep
        repairs = []
        for s in creep.pos.findInRange(FIND_STRUCTURES, 3):
            if not including_walls and s.structureType == STRUCTURE_WALL:
                continue
            if (s.hitsMax-s.hits) > 500:  # if it's lower, we might get two repair dudes to overburn it
                repairs.append(s)
        if len(repairs) >= 1:
            tgt = _.min(repairs, lambda s: s.hits)
            return tgt

    def _get_nearby_build_action(self, including_walls=False):
        creep = self.creep
        builds = creep.pos.findInRange(FIND_CONSTRUCTION_SITES, 3)
        if not including_walls:
            builds = [b for b in builds if b.structureType != STRUCTURE_WALL]
        for str_type in [STRUCTURE_LINK, STRUCTURE_CONTAINER, STRUCTURE_SPAWN]:
            high_priority = [b for b in builds if b.structureType == str_type]
            if len(high_priority) >= 1:
                print('HIGH PRIORITY BUILD DETECTED', creep, high_priority[0])
                builds = high_priority
                break
        if len(builds) >= 1:
            tgt = _.min(builds, lambda s: s.progressTotal - s.progress)
            return tgt
