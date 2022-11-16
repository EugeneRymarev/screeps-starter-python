from ..defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


from utils import around_range


non_empty_util_building_filter = lambda s: (
    (
        s.structureType == STRUCTURE_SPAWN or
        s.structureType == STRUCTURE_EXTENSION or
        s.structureType == STRUCTURE_TOWER  # somehow ;)
    )
    and s.energy < s.energyCapacity
)

spawn_filter = lambda s: (
    s.structureType == STRUCTURE_SPAWN
)

link_filter = lambda s: (
    s.structureType == STRUCTURE_LINK
)

non_full_link_filter = lambda s: (
    s.structureType == STRUCTURE_LINK and s.energy < s.energyCapacity
)


class WorkTarget:
    @classmethod
    def _get_spawn_construction_site(cls, creep):
        return _(creep.room.find(FIND_CONSTRUCTION_SITES)).filter(spawn_filter).sample()

    @classmethod
    def _get_closest_fortification(cls, creep):
        # TODO: refactor - it's also in rcl2
        fortify_hp = 1000000
        controller_flag = Game.flags[creep.room.name]
        new_fortify_hp = controller_flag.memory['fortify_hp']
        if new_fortify_hp != undefined:
            fortify_hp = int(new_fortify_hp)

        rampart_filter = lambda s: (
            s.structureType == STRUCTURE_RAMPART and s.hits < fortify_hp
        )

        wall_filter = lambda s: (
            s.structureType == STRUCTURE_WALL and s.hits < fortify_hp
        )

        rampart = creep.pos.findClosestByRange(FIND_MY_STRUCTURES, {'filter': rampart_filter})
        if rampart != undefined and rampart:
            return rampart
        wall = creep.pos.findClosestByRange(FIND_STRUCTURES, {'filter': wall_filter})
        if wall != undefined and wall:
            return wall
        return None

    @classmethod
    def _get_closest_construction_site(cls, creep):
        link = creep.pos.findClosestByRange(FIND_CONSTRUCTION_SITES, {'filter': link_filter})
        if link != undefined and link:
            return link
        return creep.pos.findClosestByRange(FIND_CONSTRUCTION_SITES)

    @classmethod
    def _get_neighboring_construction_site(cls, creep):
        links = creep.pos.findInRange(FIND_CONSTRUCTION_SITES, 2, {'filter': link_filter})
        if links != undefined and links:
            return links[0]
        sites = creep.pos.findInRange(FIND_CONSTRUCTION_SITES, 2)
        if sites != undefined and sites:
            return sites[0]
        return None

    @classmethod
    def _get_rcl1_controller(cls, creep):
        if creep.room.controller.level == 1:
            # in RCL1 we don't want to fill the spawn, it will fill by itself in 300t and there is nothing else to fill, really
            return creep.room.controller

    @classmethod
    def _get_random_nonempty_util_building(cls, creep):
        return _(creep.room.find(FIND_MY_STRUCTURES)).filter(non_empty_util_building_filter).sample()  # TODO: reserve it so that everyone doesn't run to the same thing

    @classmethod
    def _get_closest_nonempty_util_building(cls, creep):
        return creep.pos.findClosestByPath(FIND_MY_STRUCTURES, {'filter': non_empty_util_building_filter})

    @classmethod
    def _get_closest_link(cls, creep):
        return creep.pos.findClosestByPath(FIND_MY_STRUCTURES, {'filter': link_filter})

    @classmethod
    def _get_closest_nonfull_link(cls, creep):
        p = creep.pos.findClosestByPath(FIND_MY_STRUCTURES, {'filter': non_full_link_filter})
        print(creep.room.name, 'closest_nonfull_links', p)
        return p

    @classmethod
    def _get_room_controller_if_low(cls, creep):
        if creep.room.controller.ticksToDowngrade < 4000:
            return creep.room.controller

    @classmethod
    def _get_best_free_church(cls, creep):
        # TODO: this calculates all the time, should remember or flag or something
        faith_source = None
        def _get_close_structure(creep, structure_types):
            for s in creep.room.controller.pos.findInRange(FIND_STRUCTURES, 3):
                if s.structureType != structure_types:
                    continue
                return s
        if creep.room.controller.level >= 5:
            link = _get_close_structure(creep, STRUCTURE_LINK)
            if link:
                faith_source = link
            else:
                faith_source = _get_close_structure(creep, STRUCTURE_CONTAINER)
        if not faith_source:
            return None
        terrain = creep.room.getTerrain()
        positions = []
        for pos in around_range(creep.room, faith_source.pos.x, faith_source.pos.y, 1):
            if terrain.get(pos[0], pos[1]) == 1:
                continue
            positions.append(pos)

        def distance_from_controller(position):
            c = creep.room.controller.pos.getRangeTo(position[0], position[1])
            return c
        positions.sort(key=distance_from_controller)
        #if creep.room != '':
        #print(creep.room, creep.name)
        for i, pos in enumerate(positions):
            creep.room.visual.text(str(i), pos[0], pos[1]) #, {'color': 'green', 'font': 0.8})
            #print(i, pos[0], pos[1])
        for i, pos in enumerate(positions):
            if creep.pos.isEqualTo(pos[0], pos[1]):
                return None  # we are where we should be already
            who = creep.room.lookForAt(LOOK_CREEPS, pos[0], pos[1])
            if len(who) >= 1:
                continue  # busy spot
            return creep.room.getPositionAt(pos[0], pos[1])
            #creep.room.visual.circle(pos[0], pos[1], {'stroke': 'red'})
        return None  # XXX

    @classmethod
    def _get_room_controller(cls, creep):
        return creep.room.controller

    @classmethod
    def _get_nearby_construction_site(cls, creep):
        builds = creep.pos.findInRange(FIND_CONSTRUCTION_SITES, 3)
        if builds != undefined:
            return builds[0]

    @classmethod
    def _get_random_non_miner_container(cls, creep):
        containers = []
        for s in creep.room.find(FIND_STRUCTURES):
            if s.structureType != STRUCTURE_CONTAINER:
                continue
            # TODO: if store is not full
            # s.store[RESOURCE_ENERGY]
            #    continue
            #print('container found', s)
            nearby_sources = s.pos.findInRange(FIND_SOURCES, 1)
            #print('len', len(nearby_sources))
            if len(nearby_sources) >= 1:
                continue  # that's for a miner
            if s.store.getFreeCapacity(RESOURCE_ENERGY) <= min(creep.store[RESOURCE_ENERGY], 1000):
                continue  # it's full or we'd overfill it. We'll come by later when it's more empty
            containers.append(s)
        if len(containers) >= 1:
            return containers[0]  # TODO: get a "random" one ha ha, maybe Creep.id + Game.time

    @classmethod
    def _get_storage(cls, creep):
        storage = creep.room.storage
        if storage != undefined:
            return storage

    @classmethod
    def _get_terminal(cls, creep):
        terminal = creep.room.terminal
        if terminal != undefined:
            return terminal

    @classmethod
    def _get_nonfull_storage(cls, creep):
        storage = creep.room.storage
        if storage != undefined:
            if storage.store.getFreeCapacity(RESOURCE_ENERGY) > 150:
                return storage

    @classmethod
    def _get_nonfull_terminal(cls, creep):
        terminal = creep.room.terminal
        if terminal != undefined:
            if terminal.store.getFreeCapacity(RESOURCE_ENERGY) > 150:
                return terminal
