__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')

from utils import get_first_spawn
from utils import get_controller_spawn
from utils import search_room
from utils import P
from utils import around_range
from utils import part_count
from utils import distance_from_controller

from room_manager.abstract import AbstractRoomManager
from room_manager.links import Links
from room_manager.abstract import g_links
from room_manager.rcl1 import RoomManagerRCL1


room_sizes = {}  # TODO: global memory


class RoomManagerRCL2(AbstractRoomManager):
    def spawn_creeps(self):
        room = self.room
        controller = room.controller
        controller_flag = Game.flags[room.name]
        #controller_flag = None
        #for s in room.lookForAt(LOOK_FLAGS, controller.pos.x, controller.pos.y):
        #    controller_flag = s
        #    break
        spawn = get_first_spawn(room)
        print('///////////////// spawn_creeps() in', room.name)
        #if spawn is None or spawn == undefined or not spawn:  # TODO: check which one this really is
        if not spawn:  # TODO: check which one this really is
            return  # no spawn yet
        if spawn.spawning:
            return
        if spawn.progress != undefined:
            return
        if room.energyCapacityAvailable < 1300: # and len(Game.rooms) >= 2:
            print('skipping spawning in', room.name, 'because we are bootstrapped by other rooms')
            return  # we are being bootstrapped by someone else, we hope
        if room.energyCapacityAvailable < 550:  # extensions were not built yet
            return self.spawn_creeps_in_transition_period()

        # XXX XXX XXX // big temp section \\

        claim_target = None
        fortify_hp = 1000000
        if controller_flag != undefined:
            print('we have a controller flag!')

            new_fortify_hp = controller_flag.memory['fortify_hp']
            if new_fortify_hp != undefined:
                fortify_hp = int(new_fortify_hp)

            for type_ in ['claim', 'reserve']:
                target = controller_flag.memory[type_]
                #if target_time <= Game.time and Game.time <= (target_time + 600):
                if not target:
                    continue
                print('and a', type_, 'target!')
                target_room = Game.rooms[target]
                if not target_room or not target_room.controller.my or (type_ == 'reserve' and target_room.controller.reservation and target_room.controller.reservation.ticksToEnd < 600):
                    cls = type_ + 'er'
                    name = target + '_' + cls
                    if Game.creeps[name] == undefined and room.energyCapacityAvailable > 1450:
                        print('and we spawn a', cls, 'whoooo!!')
                    spawn.spawnCreep([CLAIM, CLAIM, MOVE, MOVE, MOVE, MOVE, MOVE], name, {"memory": {"cls": cls, "room": claim_target}})
                if type_ == 'claim':
                    claim_target = target

            if claim_target:
                target_room = Game.rooms[claim_target]
                if target_room and target_room.energyCapacityAvailable < 1300:
                    # build and boost mode
                    if target_room.energyCapacityAvailable >= 1300:
                        controller_flag.remove()  # ok we are done
                    elif Game.map.getRoomLinearDistance(room.name, target_room.name) >= 2:
                        # long distance higher cost but move fast
                        miner_spec = [WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, CARRY, MOVE, MOVE, MOVE, MOVE]
                        upgrader_spec = [WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, CARRY, CARRY, MOVE, MOVE, MOVE, MOVE, MOVE]
                    else:
                        # short distance low cost but move slow
                        miner_spec = [WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, CARRY, CARRY, MOVE, MOVE]
                        upgrader_spec = [WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, CARRY, CARRY, MOVE, MOVE]

                    if room.energyAvailable < room.energyCapacityAvailable:  # only help other room if our room doesn't need much
                        pass
                    elif Game.creeps[claim_target + '_bminer1'] == undefined:  # or Game.creeps[claim_target + '_bminer1'].ticksToLive:
                        spawn.spawnCreep(miner_spec, claim_target + "_bminer1", {"memory": {"cls": "miner", "room": claim_target}})
                    elif Game.creeps[claim_target + '_bminer2'] == undefined:
                        spawn.spawnCreep(miner_spec, claim_target + "_bminer2", {"memory": {"cls": "miner", "room": claim_target}})

                    elif Game.creeps[claim_target + '_bbuilder1'] == undefined:
                        spawn.spawnCreep([WORK, WORK, WORK, WORK, WORK, CARRY, CARRY, CARRY, CARRY, CARRY, MOVE, MOVE, MOVE, MOVE, MOVE], claim_target + "_bbuilder1", {"memory": {"cls": "builder", "room": claim_target}})
                    #elif Game.creeps[claim_target + '_bbuilder2'] == undefined:
                    #    spawn.spawnCreep([WORK, WORK, WORK, WORK, WORK, CARRY, CARRY, CARRY, CARRY, CARRY, MOVE, MOVE, MOVE, MOVE, MOVE], claim_target + "_bbuilder2", {"memory": {"cls": "builder", "room": claim_target}})

                    elif Game.creeps[claim_target + '_bhauler1'] == undefined:
                        spawn.spawnCreep([WORK, WORK, CARRY, CARRY, CARRY, CARRY, CARRY, CARRY, CARRY, CARRY, MOVE, MOVE, MOVE, MOVE, MOVE], claim_target + "_bhauler1", {"memory": {"cls": "hauler", "room": claim_target}})
                    elif Game.creeps[claim_target + '_bhauler2'] == undefined:
                        spawn.spawnCreep([WORK, WORK, CARRY, CARRY, CARRY, CARRY, CARRY, CARRY, CARRY, CARRY, MOVE, MOVE, MOVE, MOVE, MOVE], claim_target + "_bhauler2", {"memory": {"cls": "hauler", "room": claim_target}})
                    elif Game.creeps[claim_target + '_bhauler3'] == undefined:
                        spawn.spawnCreep([WORK, WORK, CARRY, CARRY, CARRY, CARRY, CARRY, CARRY, CARRY, CARRY, MOVE, MOVE, MOVE, MOVE, MOVE], claim_target + "_bhauler3", {"memory": {"cls": "hauler", "room": claim_target}})
                    #elif Game.creeps[claim_target + '_bhauler4'] == undefined:
                    #    spawn.spawnCreep([WORK, WORK, CARRY, CARRY, CARRY, CARRY, CARRY, CARRY, CARRY, CARRY, MOVE, MOVE, MOVE, MOVE, MOVE], claim_target + "_bhauler4", {"memory": {"cls": "hauler", "room": claim_target}})

                    elif Game.creeps[claim_target + '_bupgrader1'] == undefined:
                        spawn.spawnCreep(upgrader_spec, claim_target + "_bupgrader1", {"memory": {"cls": "upgrader", "room": claim_target}})
                    elif Game.creeps[claim_target + '_bupgrader2'] == undefined:
                        spawn.spawnCreep(upgrader_spec, claim_target + "_bupgrader2", {"memory": {"cls": "upgrader", "room": claim_target}})
                    elif Game.creeps[claim_target + '_bupgrader3'] == undefined:
                        spawn.spawnCreep(upgrader_spec, claim_target + "_bupgrader3", {"memory": {"cls": "upgrader", "room": claim_target}})
                    #elif Game.creeps[claim_target + '_bupgrader4'] == undefined:
                    #    spawn.spawnCreep(upgrader_spec, claim_target + "_bupgrader4", {"memory": {"cls": "upgrader", "room": claim_target}})
                    #elif Game.creeps[claim_target + '_bupgrader5'] == undefined:
                    #    spawn.spawnCreep(upgrader_spec, claim_target + "_bupgrader5", {"memory": {"cls": "upgrader", "room": claim_target}})

        # XXX XXX XXX \\ big temp section //

        to_construct = [s.progressTotal - s.progress for s in room.find(FIND_CONSTRUCTION_SITES)]

        to_fortify = 0
        if len(to_construct) == 0:
            #rampart_filter = lambda s: (
            #    s.structureType == STRUCTURE_RAMPART and s.hits < fortify_hp
            #)
            #ramparts_to_fortify = [max(0, fortify_hp - s.hits) for s in room.find(FIND_MY_STRUCTURES, {'filter': rampart_filter})]

            wall_filter = lambda s: (
                (s.structureType == STRUCTURE_WALL or s.structureType == STRUCTURE_RAMPART) and s.hits < fortify_hp
            )
            walls_to_fortify = [max(0, fortify_hp - s.hits) for s in room.find(FIND_STRUCTURES, {'filter': wall_filter})]

            #to_fortify = _.sum(ramparts_to_fortify) + _.sum(walls_to_fortify)
            to_fortify = _.sum(walls_to_fortify)
            if to_fortify > (fortify_hp/10):
                to_construct.append(5002)  # fortify slowly
            #print('RAMPARTS_TO_FORTIFY', _.sum(ramparts_to_fortify), len(ramparts_to_fortify))
            #print('WALLS_TO_FORTIFY', _.sum(walls_to_fortify), len(walls_to_fortify))
        to_construct_sum = _.sum(to_construct)
        #print('TO_CONSTRUCT_SUM', room.name, to_construct_sum, to_construct)
        builders = self.creep_registry.count_of_type(room, 'builder')
        extractors = self.creep_registry.count_of_type(room, 'extractor')
        miners = self.creep_registry.count_of_type(room, 'miner')
        haulers = self.creep_registry.count_of_type(room, 'hauler')
        operators = self.creep_registry.count_of_type(room, 'operator')
        dropped_sum = sum([r.amount for r in room.find(FIND_DROPPED_RESOURCES)])
        size = room_sizes[room]
        if size == undefined:             # TODO: fill it aggresively, don't wait
            size = 20
        #print('room size', room, size)
        sources = search_room(room, FIND_SOURCES)
        desired_haulers = max(1, int(size / 7))  # TODO: can use less larger ones

        desired_operators = 0
        #if room.name == 'W28N4':
        #    desired_operators = 1
        desired_extractors = 0
        if room.controller.level == 4 and room.energyCapacityAvailable >= 1300:
            desired_haulers = desired_haulers / 2
        elif room.controller.level == 5:    # TODO: actually we should see if links are up and if we have miners with CARRY
            if len(sources) == 2:
                desired_haulers = max(2, desired_haulers/2)
            elif len(sources) == 1:
                desired_haulers = 1
            else:
                print('WARING: weird number of sources in a plannable room?')
        elif room.controller.level >= 6:
            if room.terminal != undefined:
                mineral = room.terminal.pos.findClosestByRange(FIND_MINERALS)
                if mineral.mineralAmount > 0:
                    desired_extractors = 1
            desired_haulers = 1  # with creeps fully optimized for CPU a single filler is not enough
            #if room.energyCapacityAvailable - room.energyAvailable >= 2401:
            #    desired_haulers = 2  # with creeps fully optimized for CPU just one filler is not enough
            #    Game.notify(
            #        'Room ' + room.name + ' was low on energy (' + str(room.energyCapacityAvailable) + ') and needed extra haulers',
            #        #1,  # group these notifications for X min
            #        60,  # group these notifications for X min
            #    )
        source_near_controller = room.controller.pos.findInRange(FIND_SOURCES, 2)  # TODO: can be made smarter
        if to_construct_sum > 12000 and builders < 5 and miners >= 1 and len(sources) >= 2 or \
           to_construct_sum > 9000 and builders < 4 and miners >= 1 and len(sources) >= 2 or \
           to_construct_sum > 6000 and builders < 3 and miners >= 1 and len(sources) >= 2 or \
           to_construct_sum > 3000 and builders < 2 or \
           to_construct_sum > 0 and builders < 1:
            # builders first to make containers for mining
            to_construct_max = _.max(to_construct)
            to_construct_avg = sum(to_construct) / len(to_construct)
            if room.energyAvailable >= 1000:
                if to_construct_max >= 5001: # terminal and storage
                    parts = [WORK, WORK, WORK, WORK, WORK, CARRY, CARRY, CARRY, CARRY, CARRY, MOVE, MOVE, MOVE, MOVE, MOVE]
                elif to_construct_avg >= 5001: # like a tower or spawn
                    parts = [WORK, CARRY, CARRY, CARRY, CARRY, MOVE, MOVE, MOVE, MOVE, MOVE]
                else:  # roads, extensions, containers
                    parts = [WORK, WORK, CARRY, CARRY, MOVE, MOVE, MOVE, MOVE]
                spawn.createCreep(parts, "", {'cls': 'builder'})
            elif room.energyAvailable >= 550:
                if to_construct_max >= 5001: # terminal and storage
                    parts = [WORK, WORK, WORK, CARRY, MOVE, MOVE, MOVE, MOVE]
                elif to_construct_avg >= 5001: # like a tower or spawn
                    parts = [WORK, CARRY, CARRY, CARRY, CARRY, MOVE, MOVE, MOVE, MOVE, MOVE]
                else:  # roads, extensions, containers
                    parts = [WORK, WORK, CARRY, CARRY, MOVE, MOVE, MOVE, MOVE]
                spawn.createCreep(parts, "", {'cls': 'builder'})
        elif miners < len(sources):
            if room.controller.level <= 4:
                parts = []
                alt_cost = 0
                if room.energyAvailable >= 2200:
                    parts = [WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, MOVE, MOVE, MOVE, MOVE]
                    alt_cost = 2250
                elif room.energyAvailable >= 1650:
                    parts = [WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, MOVE, MOVE, MOVE]
                    alt_cost = 1700
                elif room.energyAvailable >= 1100:
                    parts = [WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, MOVE, MOVE]
                    alt_cost = 1150
                elif room.energyAvailable >= 550:
                    parts = [WORK, WORK, WORK, WORK, WORK, MOVE]
                    alt_cost = 600
                if len(parts) and source_near_controller:
                    if room.energyAvailable >= alt_cost:
                        parts.append(CARRY)
                if parts:
                    spawn.createCreep(parts, "", {'cls': 'miner'})
            else:  # link miners
                if room.energyAvailable >= 3700 and False:  # this one is overoptimized for CPU, consumes a lot of energy
                    spawn.createCreep([
                        WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK,
                        WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK,
                        WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK,
                        CARRY, CARRY, CARRY, CARRY, CARRY,
                        CARRY, CARRY, CARRY,
                        MOVE, MOVE, MOVE, MOVE, MOVE, MOVE,  # TODO: they should spawn on the position and never move
                    ], "", {'cls': 'miner'})
                elif room.energyAvailable >= 3600 and False:  # this too
                    spawn.createCreep([  # TODO: those should be calculated by math from energyAvailable, not templated
                        WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK,
                        WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK,
                        WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK,
                        CARRY, CARRY, CARRY, CARRY, CARRY, CARRY,
                        MOVE, MOVE, MOVE, MOVE, MOVE, MOVE,
                    ], "", {'cls': 'miner'})
                elif room.energyAvailable >= 2400:
                    spawn.createCreep([
                        WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK,
                        WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK,
                        CARRY, CARRY, CARRY, CARRY,
                        MOVE, MOVE, MOVE, MOVE,  # TODO: could save 200*2/1500, 400 per creep life, if it didn't move
                    ], "", {'cls': 'miner'})
                elif room.energyAvailable >= 1800:
                    spawn.createCreep([
                        WORK, WORK, WORK, WORK, WORK,
                        WORK, WORK, WORK, WORK, WORK,
                        WORK, WORK, WORK, WORK, WORK,
                        CARRY, CARRY, CARRY,
                        MOVE, MOVE, MOVE
                    ], "", {'cls': 'miner'})
                elif room.energyAvailable >= 1200:
                    spawn.createCreep([WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, CARRY, CARRY, MOVE, MOVE], "", {'cls': 'miner'})
                elif room.energyAvailable >= 600:
                    spawn.createCreep([WORK, WORK, WORK, WORK, WORK, CARRY, MOVE], "", {'cls': 'miner'})
                elif room.energyAvailable >= 550 and room.controller.level <= 4:  # non-link miners only for non-link rooms
                    spawn.createCreep([WORK, WORK, WORK, WORK, WORK, MOVE], "", {'cls': 'miner'})
        #elif self.creep_registry.count_of_type(room, 'hauler') < 2: #TODO len(room.sources):  # TODO: ? 2
        #    if room.energyAvailable >= 550:
        #        spawn.createCreep([WORK, CARRY, CARRY, CARRY, CARRY, MOVE, MOVE, MOVE, MOVE, MOVE], "", {'cls': 'hauler'})
        #elif dropped_sum > 5000 and haulers < 5 or \
        #     dropped_sum > 1000 and haulers < 4 or \
        #     dropped_sum > 50 and haulers < 3 or \
        #     haulers < 2:
        elif haulers < desired_haulers:
            if room.energyAvailable >= 1100:
                parts = [WORK, WORK, CARRY, CARRY, CARRY, CARRY, CARRY, CARRY, CARRY, CARRY, MOVE, MOVE, MOVE, MOVE, MOVE]
                spawn.createCreep(parts, "", {'cls': 'hauler'})
                return
            if self.creep_registry.count_of_type(room, 'harvester') + self.creep_registry.count_of_type(room, 'hauler') >= 1 and room.energyCapacityAvailable >= 1100:
                return  # wait for refill
            if room.energyAvailable >= 550:
                # TODO: scale it to the room size
                #parts = [CARRY, CARRY, CARRY, CARRY, CARRY, CARRY, CARRY, MOVE, MOVE, MOVE, MOVE]
                parts = [WORK, CARRY, CARRY, CARRY, CARRY, CARRY, MOVE, MOVE, MOVE]
                spawn.createCreep(parts, "", {'cls': 'hauler'})
                return

        elif extractors < desired_extractors:
            if room.energyAvailable >= 2400:
                spawn.createCreep([
                    WORK, WORK, WORK, WORK, WORK,
                    WORK, WORK, WORK, WORK, WORK,
                    WORK, WORK, WORK, WORK, WORK,
                    WORK, WORK, WORK, WORK, WORK,
                    CARRY, CARRY, CARRY, CARRY,
                    MOVE, MOVE, MOVE, MOVE,  # TODO: could save 200*2/1500, 400 per creep life, if it didn't move
                ], "", {'cls': 'extractor'})
            elif room.energyAvailable >= 1800:
                spawn.createCreep([
                    WORK, WORK, WORK, WORK, WORK,
                    WORK, WORK, WORK, WORK, WORK,
                    WORK, WORK, WORK, WORK, WORK,
                    CARRY, CARRY, CARRY,
                    MOVE, MOVE, MOVE
                ], "", {'cls': 'extractor'})
            #elif room.energyAvailable >= 1200:
            #    spawn.createCreep([
            #        WORK, WORK, WORK, WORK, WORK,
            #        WORK, WORK, WORK, WORK, WORK,
            #        CARRY, CARRY,
            #        MOVE, MOVE,
            #    ], "", {'cls': 'extractor'})
            #elif room.energyAvailable >= 600:
            #    spawn.createCreep([
            #        WORK, WORK, WORK, WORK, WORK,
            #        CARRY,
            #        MOVE,
            #    ], "", {'cls': 'extractor'})

        elif operators < desired_operators:
            if room.energyAvailable >= 750:
                spawn.createCreep([
                    CARRY, CARRY,
                    CARRY, CARRY,
                    CARRY, CARRY,
                    CARRY, CARRY,
                    CARRY, CARRY,
                    MOVE, MOVE, MOVE, MOVE, MOVE,
                ], "", {'cls': 'operator'})

        if to_construct > 300:
            return

        # upgraders

        #  eee
        # 12fe
        # 1M2e
        # E11
        #
        # E: source
        # M: miner
        # f: filler
        # e: extension
        # 1: accessible only to Miner: tower, terminal
        # 2: accessible to both Miner and Filler: spawn, storage
        # please note that it would be best for terminal and storage to be accessible. Also Spawn(2) must be accessible.
        if source_near_controller:
            if miners >= 1:
                pass
            miners = self.creep_registry.list_of_type(room, 'miner')
            for miner in miners:
                if miner.pos.inRangeTo(room.controller, 3):
                    carries = part_count(miner, 'carry')
                    if carries >= 1:
                        print('do not spawn an upgrader in', room.name, 'as we expect the miner to take care of it')
                        return
        spawn = get_controller_spawn(room)
        if spawn.spawning:
            return  # spawn is busy

        if room.controller.ticksToDowngrade < 1000:
            pass  # we really need an upgrader
        elif to_construct_sum > 2000:
            return  # we have stuff to build, lets not use energy for upgrades right now
        elif claim_target:  #and room.energyCapacityAvailable != room.energyAvailable:
            return  # we are claiming another room, that needs a lot of the energy

        #if room.controller.ticksToDowngrade > 1000:
        #    # XXX: temporarily disable spawning upgraders so that we can build new rooms
        #    return

        #if room.controller.level == 8:
        #    print('not spawning an upgrader because it was disabled')
        #    return
        if room.energyCapacityAvailable >= 100*15 +50*3 +50*5:
            spawn_it = False
            if self.creep_registry.count_of_type(room, 'upgrader') < 1:
                spawn_it = True
            else:
                prespawn = 23 * CREEP_SPAWN_TIME
                for upgrader in self.creep_registry.list_of_type(room, 'upgrader'):  # this behaves funny, 'undefined', there is only one, lets go
                    if upgrader.ticksToLive <= prespawn:
                        spawn_it = True
                    break
            if spawn_it:
                newname = room.name + 'upg'
                while Game.creeps[newname] != undefined:
                    newname += '1'
                spawn.spawnCreep(  # TODO: use spawnCreep everywhere
                    [
                        WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK,
                        CARRY, CARRY, CARRY,  # TODO: get even more?
                        MOVE, MOVE, MOVE, MOVE, MOVE,  # TODO: could save 250 energy / 1500 tics here if we spawned the guy and immediately moved him where he belongs
                    ],
                    newname,  # TODO: uhhhh
                    {
                        'memory': {'cls': 'upgrader'},
                        # TODO: take energy from spawns first
                        # TODO: 'directions': [TOP_RIGHT],
                    }
                )
            if room.controller.level == 8:
                return
        elif room.energyCapacityAvailable >= 950:
            if self.creep_registry.count_of_type(room, 'upgrader') < len(sources):
                spawn.createCreep([WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, CARRY, MOVE, MOVE], "", {'cls': 'upgrader'})
            elif self.creep_registry.count_of_type(room, 'upgrader') < len(sources)+1 and dropped_sum >= 3000:
                spawn.createCreep([WORK, WORK, WORK, WORK, WORK, WORK, WORK, WORK, CARRY, MOVE, MOVE], "", {'cls': 'upgrader'})
                Game.notify('spawning additional upgrader in room ' + room.name + ' because ' + str(dropped_sum) + ' energy is laying on the ground', 60)
        elif room.energyCapacityAvailable >= 650:
            if self.creep_registry.count_of_type(room, 'upgrader') < (len(sources)+1):
                spawn.createCreep([WORK, WORK, WORK, WORK, WORK, CARRY, MOVE, MOVE], "", {'cls': 'upgrader'})
        elif room.energyCapacityAvailable >= 550:
            if self.creep_registry.count_of_type(room, 'upgrader') < 2*len(sources):
                spawn.createCreep([WORK, WORK, WORK, WORK, CARRY, MOVE, MOVE], "", {'cls': 'upgrader'})

    def spawn_creeps_in_transition_period(self):
        room = self.room
        spawn = get_first_spawn(room)
        sources = search_room(room, FIND_SOURCES)
        if room.energyCapacityAvailable >= 500:
            if self.creep_registry.count_of_type(room, 'harvester') < RoomManagerRCL1.MAX_HARVESTERS:  # keep spawning them, why not
                if room.energyAvailable >= 500:
                    spawn.createCreep([WORK, WORK, CARRY, CARRY, MOVE, MOVE, MOVE, MOVE], "", {'cls': 'harvester'})
        elif room.energyCapacityAvailable >= 450:
            if self.creep_registry.count_of_type(room, 'miner') < len(sources):
                if room.energyAvailable >= 450:
                    spawn.createCreep([WORK, WORK, WORK, WORK, MOVE], "", {'cls': 'miner'})
            if self.creep_registry.count_of_type(room, 'harvester') < RoomManagerRCL1.MAX_HARVESTERS:  # keep spawning them, why not
                if room.energyAvailable >= 450:
                    spawn.createCreep([WORK, CARRY, CARRY, CARRY, MOVE, MOVE, MOVE, MOVE], "", {'cls': 'harvester'})
        elif room.energyCapacityAvailable >= 350:
            if self.creep_registry.count_of_type(room, 'miner') < len(sources):
                if room.energyAvailable >= 350:
                    spawn.createCreep([WORK, WORK, WORK, MOVE], "", {'cls': 'miner'})
            if self.creep_registry.count_of_type(room, 'harvester') < RoomManagerRCL1.MAX_HARVESTERS:  # keep spawning them, why not
                if room.energyAvailable >= 350:
                    spawn.createCreep([WORK, CARRY, CARRY, MOVE, MOVE, MOVE], "", {'cls': 'harvester'})
        else:
            return RoomManagerRCL1(room, self.creep_registry).spawn_creeps()  # keep RCL1 layout until they build up the extensions

    AROUND_OFFSETS = (
        (
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, 1),
            (0, -1),
            (1, -1),
            (1, 0),
            (1, 1),
        ),
        (
            (1, -2),
            (0, -2),
            (-1, -2),
            (-2, -2),
            (-2, -1),
            (-2, 0),
            (-2, 1),
            (-2, 2),
            (-1, 2),
            (0, 2),
            (1, 2),
            (2, -2),
            (2, -1),
            (2, 0),
            (2, 1),
            (2, 2),
        ),
    )
    def run_build(self):
        # TODO: don't do it every tick
        room = self.room

        for s in room.find(FIND_HOSTILE_STRUCTURES):
            if not s.store or s.store.getUsedCapacity() == 0:
                print('destroying hostile structure at', room.name, ':', s.structureType, '@', s.pos, s.store, s.store.getUsedCapacity())
                s.destroy()
            else:
                print('keeping hostile structure at', room.name, ':', s.structureType, '@', s.pos, s.store, s.store.getUsedCapacity())

        # shaped farms first
        if room.energyCapacityAvailable < 550:  # all extensions were not built yet
            #eree
            # ere
            #   r
            #   S

            #self.build_extension(spawn_pos.x,   spawn_pos.y-2)
            #self.build_extension(spawn_pos.x,   spawn_pos.y-3)
            #self.build_extension(spawn_pos.x-1, spawn_pos.y-3)
            #self.build_extension(spawn_pos.x-2, spawn_pos.y-2)
            #self.build_extension(spawn_pos.x-3, spawn_pos.y-3)
            #if self.enable_building:
            #    return
            pass

        #self.build_roads(
        #    [
        #        P(spawn_pos.x,   spawn_pos.y-1),
        #        P(spawn_pos.x-1, spawn_pos.y-2),
        #        P(spawn_pos.x-2, spawn_pos.y-3),
        #    ]
        #)

        sources = search_room(room, FIND_SOURCES)

        miner_containers, source_to_controller_paths, map_size = self.get_miner_container_positions(sources)

        spawn = get_first_spawn(room)

        if not spawn or spawn == undefined:
            path = source_to_controller_paths[0]
            if len(source_to_controller_paths) >= 2:
                otherpath = source_to_controller_paths[1]
                if len(source_to_controller_paths[0]) > len(source_to_controller_paths[1]):
                    # actually source2 is closer to controller
                    path = source_to_controller_paths[1]
                    otherpath = source_to_controller_paths[0]
            if len(path) > 2:
                self.build_spawn(path[1].x, path[1].y)
            if room.controller.level >= 7:
                if len(otherpath) > 2:
                    self.build_spawn(otherpath[1].x, otherpath[1].y)

        if not spawn:
            return  # no spawn yet and no construction site.
        else:
            spawn_pos = spawn.pos

        if room.controller.level >= 6:
            self.build_extractor()

        if room.controller.level == 5 and len(sources) == 2:
            path = room.findPath(sources[0].pos, sources[1].pos, {'ignoreCreeps': True})
            map_size += len(path) - 2  # route to container, not source
        room_sizes[room] = map_size

        def costCallback(roomName, costMatrix):
            terrain = Game.rooms[roomName].getTerrain()
            around_coords = around_range(room, room.controller.pos.x, room.controller.pos.y, 1)
            around_coords.extend(
                around_range(room, room.controller.pos.x, room.controller.pos.y, 2)
            )
            walls = []
            for x, y in around_coords:
                if terrain.get(x, y) == 1:
                    walls.append((x, y))
            for wx, wy in walls:
                for x, y in around_range(room, wx, wy, 1):
                    costMatrix.set(x, y, 20)

            #    value = 70
            #        value = 255
            #    costMatrix.set(x, y, value)
            #for x, y in around_range(room, room.controller.pos.x, room.controller.pos.y, 2):
            #    value = 40
            #    if terrain.get(x, y) == 1:
            #        value = 255
            #    costMatrix.set(x, y, value)
            #costMatrix.set(18, 8, 50)

        #PathFinder.use(True)
        # build a container next to controller
        path = room.findPath(
            room.controller.pos,
            spawn_pos,
            {
                'ignoreCreeps': True,
                'costCallback': costCallback,
                'maxRooms': 1,
            },
        )
        controller_container = room.getPositionAt(path[1].x, path[1].y)

        if room.controller.level <= 4:
            self.build_container(path[1].x, path[1].y)

        roads = []
        #if 1:
        #    roads.append(path)
        #    #return

        ignoreRoads = True
        for miner_container in miner_containers:
            path = room.findPath(miner_container, controller_container, {'ignoreCreeps': True, 'ignoreRoads': ignoreRoads})
            roads.append(path[0:len(path)-1])
            path = room.findPath(miner_container, spawn_pos, {'ignoreCreeps': True})
            roads.append(path[0:len(path)-1])

        links = Links()
        link_filter = lambda s: (
            s.structureType == STRUCTURE_LINK
        )

        self.debug_log('REGISTERING LINKS IN ' + room.name)

        handled = set()
        for what, obj in [
                ('controller', room.controller),
                ('storage', room.storage),
                ('terminal', room.terminal),
                # TODO: mineral link
            ]:
            if obj == undefined:
                self.debug_log(what + ' does not exist in ' + room.name)
                continue
            structures = obj.pos.findInRange(FIND_STRUCTURES, 3, filter=link_filter)  # TODO: if faith source is close to energy source, this will mess up
            if len(structures) >= 1:
                setattr(links, what + '_id', structures[0].id)
                self.debug_log(what + '_link: ' + structures[0].id)
                handled.add(structures[0].id)
            else:
                self.debug_log(what + ' has no link, apparently')

        for miner_container in miner_containers:
            if not miner_container:
                continue
            #print(miner_container)
            if miner_container.pos != undefined:  # FIXME wtf
                miner_links = miner_container.pos.findInRange(FIND_STRUCTURES, 1, filter=link_filter)
            else:
                miner_links = miner_container.findInRange(FIND_STRUCTURES, 1, filter=link_filter)
            if len(miner_links):
                self.debug_log('miner_link ' + miner_links[0].id + ' ' + miner_container.id)
                links.source_ids.append(miner_links[0].id)
                handled.add(miner_links[0].id)
            else:
                self.debug_log('no miner_link for' + miner_container)

        for link in room.find(FIND_STRUCTURES, filter=link_filter):
            if link == undefined:
                continue
            #self.debug_log('handled', handled, 'link.id', link.id)
            #if link.id == links.controller_id:
            #    continue
            if handled.includes(link.id):
                #self.debug_log(link.id, 'was already handled')
                continue
            self.debug_log('other link: ' + link.id)
            links.other_ids.append(link.id)

        #print('setting links', links, 'in', room)
        g_links[room.name] = links

        #print('road', roads[0][1])
        #room.visual.poly(roads[0][1], {'color': 'ff0000'})
        #print(roads[0][1][0], roads[0][1][len(roads[0][1]-1)])
        #room.getPositionAt(roads[0][1][0].x, roads[0][1][0].y)
        roads.sort(key=lambda road: -1*len(road))
        #for road in roads:
        #    room.visual.poly([(point.x, point.y) for point in road], {'stroke': '#00ff00'})

        def has_road(room, point):
            for s in room.lookForAt(LOOK_STRUCTURES, point.x, point.y):
                if s.structureType == STRUCTURE_ROAD and s.hits >= 1:
                    has_road = True
                    return True
            return False

        build_something = False
        for road in roads:
            for point in road:
                if not has_road(room, point) or not self.enable_building:
                    build_something = True
            if build_something:
                self.build_roads(road)
                if self.enable_building:
                    break  # build roads one by one

        # basic extension planner
        terrain = room.getTerrain()
        positions = []
        for road in roads:
            for point in road:
                pos_o = self.room.getPositionAt(point.x, point.y)
                for pos in around_range(room, point.x, point.y, 1, vis='red'):
                    if terrain.get(pos[0], pos[1]) == 1:
                        continue
                    structures = room.lookForAt(LOOK_STRUCTURES, pos[0], pos[1])
                    if len(structures) >= 1 and structures[0].structureType != STRUCTURE_EXTENSION:
                        continue
                    if distance_from_controller(room, pos[0], pos[1]) <= 4:
                        continue
                    close_to_miner_container = False
                    for miner_container in miner_containers:
                        if miner_container.pos != undefined:  # FIXME wtf
                            miner_container = miner_container.pos
                        if miner_container.getRangeTo(pos[0], pos[1]) <= 2:
                            close_to_miner_container = True
                            break
                    if close_to_miner_container:
                        continue
                    #if has_road(room, pos):
                    #    continue

                    pos_o = self.room.getPositionAt(pos[0], pos[1])
                    room.visual.circle(pos_o, {'stroke': 'red'})
                    positions.append(pos)
                    #room.visual.circle(pos, {'stroke': 'yellow'})
                    #self.build_extension(spawn_pos.x,   spawn_pos.y-2)


#            break
#            candidate_spots = []
#            source_is_covered = False
#            print('room', room)
#            terrain = room.getTerrain()
#            print('terrain', terrain)
#            print('terrain.get', terrain.get)
#            return
#            terrain2 = Game.map.getRoomTerrain(room.name)
#            print('terrain2', terrain2)
#
#            print('terrain.get(1, 1)', terrain.get(15, 15))
#            #print('terrain2.get', terrain2.get)
#            #.get(1, 1)
#            for x_diff, y_diff in self.AROUND_OFFSETS:
#                print('offsets', x_diff, y_diff)
#                x = source.pos.x + x_diff
#                y = source.pos.y + y_diff
#                print('terrain', dict(terrain))
#                content = terrain.get(x, y)
#                print('content for x,y', x, y, content)
#                if content == 1:  # wall
#                    continue
#                thing = get_thing_at_coordinates(containers, x, y)
#                if thing:
#                    source_is_covered = True
#                    break
#                thing = get_thing_at_coordinates(container_sites, x, y)
#                if thing:
#                    source_is_covered = True
#                    break
#                candidate_spots.append((x, y))
#            if source_is_covered:
#                continue
#            print('uncovered source:', source, len(candidate_spots))
#            #if len(candidate_spots) == 1:
#            #    pass
#            # for each free space around source
#            # sort the list by distance to controller
#            # is container on that space already?
#            #     continue
#            # build a container
#
