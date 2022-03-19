__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')

from creeps.scheduled_action import ScheduledAction
from creeps.abstract import AbstractCreep
from creeps.parts.carry import Carry
from utils import get_close_structure
from utils import get_thing_at_coordinates
from utils import search_room
from utils import part_count, make_transfer_action


# TODO: if the source is empty and there is another non-reserved source in that room that can be reached before our current source resets, then switch designated source to that new one and go to it
# TODO: if all sources are empty and we can reach spawn before sources reset + our spawning time, go to the spawn
# TODO: if you are at the spawn, decide whether to recycle itself or renew itself


class Miner(AbstractCreep, Carry):
    ICON = '⛏️'
    @classmethod
    def _get_transfer_to_link_actions(cls, creep, source):
        link = cls._get_neighboring_nonfull_link(creep)
        if link and part_count(creep, 'carry') >= 1:
            #print(creep.name, part_count(creep, 'carry'), creep.store.getFreeCapacity(RESOURCE_ENERGY), link.store.getFreeCapacity(RESOURCE_ENERGY))
            if creep.store.getFreeCapacity(RESOURCE_ENERGY) == 0:
                return [ScheduledAction.transfer(
                    creep,
                    link,
                    RESOURCE_ENERGY,
                    min(
                        link.store.getFreeCapacity(RESOURCE_ENERGY),
                        creep.store[RESOURCE_ENERGY],
                    )
                )]
        return []

    def _should_mine(self, source):
        works = part_count(self.creep, 'work')
        if source.ticksToRegeneration == undefined:
            return True  # new source
        if source.energy >= source.ticksToRegeneration * works * HARVEST_POWER:
            print('WARNING:', self.creep, 'in', self.creep.room.name, "must mine at full speed because we won't mine fast enough to get it all even if we ran 100%")
            return True

        should_have_mined = source.energyCapacity * ((ENERGY_REGEN_TIME-source.ticksToRegeneration)/ENERGY_REGEN_TIME)
        actually_mined = source.energyCapacity - source.energy
        if actually_mined <= should_have_mined:
            #print(self.creep.name, 'actually mining', should_have_mined, actually_mined)
            return True
        return False
        #if creep.name == 'Mia':
        #    print('kkkkkkkkkk', source.energy, (ENERGY_REGEN_TIME-source.ticksToRegeneration) * works * HARVEST_POWER)

    def _run(self):
        super()._run()
        creep = self.creep
        room = creep.room
        sources = search_room(room, FIND_SOURCES)
        containers = search_room(room, FIND_STRUCTURES, lambda x: x.structureType == STRUCTURE_CONTAINER)
        thing = get_thing_at_coordinates(containers, creep.pos.x, creep.pos.y)  # TODO save CPU via lookAt
        flag = room.lookForAt(LOOK_FLAGS, creep.pos.x, creep.pos.y)
        if thing or flag != undefined:
            for source in sources:
                if creep.pos.isNearTo(source):
                    #print(creep, source.ticksToRegeneration, source.ticksToRegeneration % (works/5) == 0)
                    actions = []
                    #if creep.store.getCapacity(RESOURCE_ENERGY) > 0 and creep.store[RESOURCE_ENERGY] > 0:
                    #    actions.append(ScheduledAction.drop(creep, RESOURCE_ENERGY))
                    #if creep.store.getCapacity(RESOURCE_ENERGY) > 0 and creep.store.getFreeCapacity(RESOURCE_ENERGY) == 0:
                    #    for s in creep.pos.findInRange(FIND_MY_STRUCTURES, 1):
                    #        if s.structureType != STRUCTURE_LINK:
                    #            continue
                    #        if s.store.getFreeCapacity(RESOURCE_ENERGY) > 0:
                    #            actions.append(
                    #                ScheduledAction.transfer(creep, s, RESOURCE_ENERGY, priority=80)
                    #            )
                    #        break  # only handle one link
                    dropped = self._get_nearby_dropped_resource(creep)
                    if dropped:
                        dropped = [s for s in dropped if s.pos != creep.pos]
                        if dropped is not None and dropped != undefined:
                            actions.append(
                                ScheduledAction.pickup(creep, dropped[0], lambda: 0)
                            )
                    if self._should_mine(source):
                        miner_container = None
                        structures = room.lookForAt(LOOK_STRUCTURES, creep.pos.x, creep.pos.y)
                        if structures:
                            for structure in structures:
                                if structure.structureType == STRUCTURE_CONTAINER:
                                    miner_container = structure
                        if source.energy != 0 and (creep.store.getFreeCapacity(RESOURCE_ENERGY) >= 1 or creep.store.getCapacity(RESOURCE_ENERGY) == 0 or (miner_container and miner_container.store.getFreeCapacity(RESOURCE_ENERGY) >= 1)):
                            actions.append(
                                ScheduledAction.harvest(creep, source)
                            )
                        # NOTE: this requires EasyCreep
                        if creep.store[RESOURCE_ENERGY] > 32:  # TODO appropriate value
                            repair = self._get_nearby_repair_action()
                            if len(repair) and Game.time % 10 == 0:
                                a = ScheduledAction.repair(creep, repair)
                                a.priority = 20
                                actions.append(a)
                            else:
                                build = self._get_nearby_build_action()
                                if build:
                                    actions.append(ScheduledAction.build(creep, build, priority=20))
                            if creep.room.controller.pos.inRangeTo(creep.pos.x, creep.pos.y, 3):
                                to_construct = [s.progressTotal - s.progress for s in room.find(FIND_CONSTRUCTION_SITES)]
                                if to_construct == 0:
                                    actions.append(ScheduledAction.upgradeController(creep, creep.room.controller))
                    transfer_to_link = self._get_transfer_to_link_actions(creep, source)
                    if len(transfer_to_link) >= 1:
                        actions.extend(transfer_to_link)
                    else:
                        util = self._get_neighboring_nonfull_util(creep)
                        if util:
                            a = make_transfer_action(creep, util)
                            if a:
                                return [a]
                    return actions
        else:  # we are not on a container
            pass

        for source in sources:
            path = creep.room.findPath(source.pos, creep.room.controller.pos, {'ignoreCreeps': True})
            if len(path) >= 2:
                where = path[0]
                if creep.pos.isEqualTo(where.x, where.y):
                    # mine regardless of whether there is a container or not
                    # other creeps will come and pick it up, use it to build the container
                    actions = []
                    if self._should_mine(source):
                        actions.append(ScheduledAction.harvest(creep, source))
                    transfer_to_link = self._get_transfer_to_link_actions(creep, source)
                    if len(transfer_to_link) >= 1:
                        actions.extend(transfer_to_link)
                    return actions
            else:
                container = get_close_structure(source.pos, 1, STRUCTURE_CONTAINER)
                if container != undefined:
                    where = container.pos
                else:
                    where = path[0]  # XXX ?

            who = room.lookForAt(LOOK_CREEPS, where.x, where.y)
            actions = []
            if len(who) >= 1:
                # some other creep is currently there
                if not who[0].my:
                    continue
                if who[0].memory.cls == 'miner':  # and it's a miner!
                    continue  # lets try another source
                elif who[0].pos.isNearTo(creep.pos):
                    actions.append(
                        ScheduledAction.moveTo(
                            who[0],
                            creep.pos,
                        )
                    )
                    #Game.notify(
                    print(
                        'swapping creeps at a mining station in ' + creep.room.name + ', ' + str(who[0]) + ' for ' + creep.name,
                        30,
                    )
            actions.append(
                ScheduledAction.moveTo(creep, room.getPositionAt(where.x, where.y))
            )
            return actions
        Game.notify('WARNING: ' + creep.name + ' is a miner with no source to mine', 30)
        return []
