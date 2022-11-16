__pragma__('noalias', 'undefined')
__pragma__('noalias', 'name')

from creeps.scheduled_action import ScheduledAction


extension_filter = lambda s: s.structureType == STRUCTURE_EXTENSION


class CarrySource:
    @classmethod
    def _get_cached_source(cls, creep):
        if creep.memory.source:  # TODO: don't ever use memory, unless we've just reset RAM
            return Game.getObjectById(creep.memory.source)

    @classmethod
    def _get_dropped_resource(cls, creep):
        # when a creep dies and leaves some energy, go pick it up
        source_filter = lambda s: (
            s.resourceType == RESOURCE_ENERGY and s.amount >= 50
        )
        source = creep.pos.findClosestByRange(FIND_DROPPED_RESOURCES, filter=source_filter)  # TODO: reserve it for the creep that is closest to the thing
        return source

    @classmethod
    def print_debug(cls, creep, *args):
        #if creep.room.name == 'W27N1':
        #if creep.room.name == 'W24N2':  # that explodes for some reason
        #print(*args)
        return

    @classmethod
    def _get_refill_source(self, creep):
        def source_filter(s):
            if not (
                s.structureType == STRUCTURE_CONTAINER or
                s.structureType == STRUCTURE_STORAGE or
                s.structureType == STRUCTURE_TERMINAL or
                s.structureType == STRUCTURE_LINK
            ):
                return False  # not that type of a structure
            if not s.store:
                return False  # construction site
            if s.store[RESOURCE_ENERGY] < 50:
                return False  # not enough energy

            if s.structureType == STRUCTURE_LINK:
                if len(s.pos.findInRange(FIND_MY_STRUCTURES, 2, filter=extension_filter)) == 0:
                    # when refilling don't take from a link if it's not near an extensions
                    return False
            return True
        result = creep.pos.findClosestByRange(FIND_STRUCTURES, filter=source_filter)
        return result


    @classmethod
    def _get_closest_energetic_container(cls, creep):
        #free_capacity = creep.store.getFreeCapacity(RESOURCE_ENERGY)
        cls.print_debug(creep, '_get_closest_energetic_container() by', creep.name)
        # TODO: should not take from miner links!
        def source_filter(s):
            #if creep.room.name == 'W27N1': #and s.id == '5fc61ef4fd39edb21752082a':
            #   cls.print_debug(creep, '=== CONSIDERING', s.id)
            if not (s.structureType == STRUCTURE_CONTAINER or s.structureType == STRUCTURE_LINK):
            #if not (s.structureType == STRUCTURE_CONTAINER or s.structureType == STRUCTURE_STORAGE or s.structureType == STRUCTURE_TERMINAL or s.structureType == STRUCTURE_LINK):
                if s.id == '5fc61ef4fd39edb21752082a':
                    cls.print_debug(creep, '=== TYPE', s.id)
                return False  # not that type of a structure
            if not s.store:
                cls.print_debug(creep, '=== CONSTRUCTION SITE', s.id)
                return False
            if s.store[RESOURCE_ENERGY] < 50:
                #if creep.room.name == 'W27N1':# and s.id == '5fc61ef4fd39edb21752082a':
                #    cls.print_debug(creep, '=== POOR', s.id)
                return False  # not enough energy
            sources = s.pos.findInRange(FIND_SOURCES, 2)
            if sources != undefined and len(sources) >= 1:
                cls.print_debug(creep, '=== BELONGS TO A MINER', s.id, sources)
                return False
            creeps = s.pos.lookFor(LOOK_CREEPS)
            if creeps != undefined:
                for c2 in creeps:
                    if c2.memory.cls == 'miner':
                        cls.print_debug(creep, '=== MINER', s.id)
                        return False
            cls.print_debug('=== GOOD', s.id)
            #creep.room.visual.circle(s.pos.x, s.pos.y, {'stroke': 'red'})
            return True
        result = creep.pos.findClosestByRange(FIND_STRUCTURES, filter=source_filter)
        #cls.print_debug(creep, 'closest energetic container for', creep, 'is', result)
        return result

    @classmethod
    def _get_nearby_dropped_resource(cls, creep):
        sources = creep.pos.findInRange(FIND_DROPPED_RESOURCES, 1)
        if len(sources) >= 1:
            return sources[0]

    @classmethod
    def _get_nearby_energetic_tombstones(cls, creep):
        for s in creep.pos.findInRange(FIND_TOMBSTONES, 1):
            if s.store[RESOURCE_ENERGY] >= 1:
                return s

    @classmethod
    def _get_nearby_energetic_ruin(cls, creep):
        for s in creep.pos.findInRange(FIND_RUINS, 1):
            if s.store[RESOURCE_ENERGY] >= 1:
                return s

    @classmethod
    def _get_random_energetic_ruin(cls, creep):
        source_filter = lambda s: (
            s.store[RESOURCE_ENERGY] >= 1
        )
        return _(creep.room.find(FIND_RUINS)).filter(source_filter).sample()  # TODO: reserve it so that everyone doesn't run to the same thing

    @classmethod
    def _get_random_enemy_building(cls, creep):
        source_filter = lambda s: (
            s.structureType != STRUCTURE_CONTAINER and s.store and s.store[RESOURCE_ENERGY] >= 1
        )
        return _(creep.room.find(FIND_HOSTILE_STRUCTURES)).filter(source_filter).sample()  # TODO: reserve it so that everyone doesn't run to the same thing

    @classmethod
    def _get_closest_enemy_spawn(cls, creep):
        source_filter = lambda s: (
            s.structureType == STRUCTURE_SPAWN and s.store[RESOURCE_ENERGY] >= 1
        )
        return creep.pos.findClosestByRange(FIND_HOSTILE_STRUCTURES, filter=source_filter)

    @classmethod
    def _get_closest_enemy_building(cls, creep):
        source_filter = lambda s: (
            s.structureType != STRUCTURE_CONTAINER and s.store and s.store[RESOURCE_ENERGY] >= 1
        )
        return creep.pos.findClosestByRange(FIND_HOSTILE_STRUCTURES, filter=source_filter)

    @classmethod
    def _get_mineral(cls, creep):
        return creep.pos.findClosestByRange(FIND_MINERALS)

    def get_source(self):
        source = self._get_cached_source(self.creep)
        if source:
            return source
        for source_getter_id, source_getter in enumerate(self._get_source_getters()):
            #print('considering source_getter', source_getter_id)
            source = source_getter(self.creep)
            if source and (source.pos != None or source.x and source.y):
                self.creep.memory.source = source.id
                return source
        if self.creep.memory.cls != 'upgrader':  # XXX
            print(self, 'no source!')

    @classmethod
    def _get_neighboring_nonempty_link(cls, creep):
        source_filter = lambda s: (
            s.structureType == STRUCTURE_LINK and s.store[RESOURCE_ENERGY] >= 50
        )
        container = creep.pos.findInRange(FIND_STRUCTURES, 1, filter=source_filter)
        if len(container) >= 1:
            return container[0]

    @classmethod
    def _get_neighboring_nonfull_util(cls, creep):
        source_filter = lambda s: (
            (
                s.structureType == STRUCTURE_SPAWN or
                s.structureType == STRUCTURE_EXTENSION or
                s.structureType == STRUCTURE_TOWER
            )
            and s.energy < s.energyCapacity
            and s.store != undefined
        )
        util = creep.pos.findInRange(FIND_MY_STRUCTURES, 1, filter=source_filter)
        if len(util) >= 1:
            return util[0]

    @classmethod
    def _get_neighboring_nonfull_link(cls, creep):
        source_filter = lambda s: (
            s.structureType == STRUCTURE_LINK and s.store.getFreeCapacity(RESOURCE_ENERGY) > 0
        )
        container = creep.pos.findInRange(FIND_STRUCTURES, 3, filter=source_filter)  # TODO
        if len(container) >= 1:
            return container[0]

    @classmethod
    def _get_neighboring_miner_container(cls, creep):
        source_filter = lambda s: (  # TODO: deduplicate those lambdas
            s.structureType == STRUCTURE_CONTAINER and s.store[RESOURCE_ENERGY] >= 50
        )
        container = creep.pos.findInRange(FIND_STRUCTURES, 1, filter=source_filter)
        if len(container) >= 1:
            nearby_sources = container[0].pos.findInRange(FIND_SOURCES, 1)
            if len(nearby_sources) >= 1:
                return container[0]

    @classmethod
    def _get_neighboring_source(cls, creep):
        return creep.pos.findInRange(FIND_SOURCES, 1)

    @classmethod
    def _get_random_source(cls, creep):
        source = _.sample(creep.room.find(FIND_SOURCES))  # TODO: balance instead of randomizing
        if creep.room.name == 'sim':
            while source.pos.x == 6 and source.pos.y == 44:  # TODO: do not just walk up to a Source Keeper
                source = _.sample(creep.room.find(FIND_SOURCES))
        return source

    @classmethod
    def _get_fullest_miner_container(cls, creep):
        containers = []
        for s in creep.room.find(FIND_STRUCTURES):
            if s.structureType != STRUCTURE_CONTAINER:
                continue
            if s.store[RESOURCE_ENERGY] <= 0:
                continue
            nearby_sources = s.pos.findInRange(FIND_SOURCES, 1)
            if len(nearby_sources) == 0:
                continue  # that's not for a miner
            containers.append(s)
        #def distanceFromCreep(site):
        #    return max(abs(site.pos.x-creep.pos.x), abs(site.pos.y-creep.pos.y))
        containers.sort(key=lambda container: -1*container.store[RESOURCE_ENERGY])
        return containers[0]  # TODO: get a "random" one ha ha, maybe Creep.id + Game.time

    @classmethod
    def _get_source_of_faith(cls, creep):
        #containers = []
        #for s in creep.room.controller.pos.findInRange(FIND_STRUCTURES, 3):
        #    if s.structureType != STRUCTURE_CONTAINER and s.structureType != STRUCTURE_LINK:
        #        continue
        #    if s.store[RESOURCE_ENERGY] > 0:
        #        if s.structureType == STRUCTURE_LINK:
        #            containers.insert(0, s)
        #        else:
        #            containers.append(s)
        #if len(containers) >= 1:
        #    return containers[0]
        source_filter = lambda s: (
            (
                s.structureType == STRUCTURE_CONTAINER or
                s.structureType == STRUCTURE_LINK
            )
            and s.store != undefined
            and s.store[RESOURCE_ENERGY] > 50
        )
        u = creep.room.controller.pos.findInRange(FIND_STRUCTURES, 3, filter=source_filter)
        if len(u) >= 1:
            return u[0]
        return None

    @classmethod
    def _get_nonempty_storage(cls, creep):
        storage = creep.room.storage
        if storage != undefined:
            if storage.store[RESOURCE_ENERGY] > 50:
                return storage

    @classmethod
    def _get_nonempty_terminal(cls, creep):
        terminal = creep.room.terminal
        if terminal != undefined:
            if terminal.store[RESOURCE_ENERGY] > 50:
                return terminal

    def do_fill(self):
        creep = self.creep
        source = self.get_source(creep)

        def reset_source():
            if creep.store.getFreeCapacity(RESOURCE_ENERGY) < creep.store.getCapacity(RESOURCE_ENERGY) * 0.6:
                creep.memory.filling = False  # XXX HACKS
            del creep.memory.source

        if not creep.pos.isNearTo(source):
            return [ScheduledAction.moveTo(creep, source, reset_source)]

        if source.amount != None:  # dropped resource
            return [ScheduledAction.pickup(creep, source, reset_source)]
        elif source.destroyTime != None:  # ruin
            del creep.memory.source  # we'll drain it to our capacity all in one tick, lets not try taking it again next tick
            return [ScheduledAction.withdraw(creep, source, RESOURCE_ENERGY)]
        elif source.store != undefined and (source.my == undefined or source.my == True):  # container/storage/link/terminal
            if creep.store.getFreeCapacity(RESOURCE_ENERGY) >= source.store[RESOURCE_ENERGY]:
                who = creep.room.lookForAt(LOOK_CREEPS, source.pos)
                if len(who) >= 1:
                    # some creep is currently there
                    if who[0].memory.cls == 'miner':  # and it's a miner!
                        # save CPU: don't just stand there and siphon it as it is being filled
                        if Game.time % 10 != 0:  # TODO: save even more cpu
                            # but if the room is drained completely, don't wait for the entire pilgrimage
                            # try to unstuck
                            return []
            return [ScheduledAction.withdraw(creep, source, RESOURCE_ENERGY)]  # TODO: reset_source doesn't work
        elif source.my == False and source.store != undefined:  # enemy building
            return [ScheduledAction.withdraw(creep, source, RESOURCE_ENERGY)]
        else:  # a source
            return [ScheduledAction.harvest(creep, source)]
