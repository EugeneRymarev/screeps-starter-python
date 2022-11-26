__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')


from creeps.scheduled_action import ScheduledAction
from creeps.abstract import AbstractCreep
from creeps.parts.carry import Carry


def storage_stash_filter(s):
    if not s.structureType == STRUCTURE_STORAGE:
        return False  # not that type of a structure
    if not s.store:
        return False  # construction site
    if s.store.getFreeCapacity(RESOURCE_KEANIUM) == 0:
        return False
    return True  # we don't care if it belongs to a miner or upgrader or whatever, just get it.
def terminal_stash_filter(s):
    if not s.structureType == STRUCTURE_TERMINAL:
        return False  # not that type of a structure
    if not s.store:
        return False  # construction site
    if s.store.getFreeCapacity(RESOURCE_KEANIUM) == 0:
        return False
    return True  # we don't care if it belongs to a miner or upgrader or whatever, just get it.


class Extractor(AbstractCreep, Carry):
    DEBUG = True
    ICON = '🛢️'

    def _should_mine(self, mineral):
        if mineral.mineralAmount == 0:
            return False
        found = mineral.pos.lookFor(LOOK_STRUCTURES)
        for s in found:
            if s.structureType == STRUCTURE_EXTRACTOR:
                return s.cooldown == 0
        print('WARNING: no extractor found in', self.creep.room.name)
        return False

    def _run(self):
        super()._run()
        creep = self.creep
        room = creep.room
        mineral = self._get_mineral(creep)
        actions = []
        if creep.store.getFreeCapacity(mineral.mineralType) == 0:
            # time to stash it
            for f in [storage_stash_filter, terminal_stash_filter]:
                target = creep.pos.findClosestByRange(FIND_MY_STRUCTURES, filter=f)
                if not target:
                    continue
                if not creep.pos.isNearTo(target):
                    return [ScheduledAction.moveTo(creep, target)]
                actions.append(ScheduledAction.transfer(creep, target, mineral.mineralType))
                break
            else:
                print('ERROR! no suitable stash for extractor', creep)
                return []
        if not creep.pos.isNearTo(mineral):
            actions.append(ScheduledAction.moveTo(creep, mineral))
        elif self._should_mine(mineral):
            actions.append(ScheduledAction.harvest(creep, mineral))
        # TODO: go recycle yourself
        return actions
