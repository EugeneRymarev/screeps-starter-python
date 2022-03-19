__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')


from creeps.scheduled_action import ScheduledAction
from creeps.abstract import AbstractCreep


class Cleanser(AbstractCreep):
    DEBUG = False
    ICON = '!'
    TARGET_ROSTER = [
        (
            # creeps
            FIND_HOSTILE_CREEPS,
            lambda x: x.hits >= 1,  # probably not needed
        ),
        (
            # tower
            FIND_HOSTILE_STRUCTURES,
            lambda x: x.structureType == STRUCTURE_TOWER,
        ),
        (
            # invader core
            FIND_HOSTILE_STRUCTURES,
            lambda x: x.structureType == STRUCTURE_INVADER_CORE,
        ),
    ]

    def _run(self):
        super()._run()
        creep = self.creep
        room = creep.room
        controller = room.controller

        actions = []

        heals = part_count(creep, 'heal')
        if heals >= 1 and creep.hitsMax > creep.hits:
            actions.append(
                ScheduledAction.heal(creep, creep, priority=1001)
            )

        actions.extend(self._handle_target_roster())
        return actions

    def _handle_target_roster(self):
        for type_, filter in self.TARGET_ROSTER:
            target = creep.pos.findClosestByRange(type_, filter=filter)
            if target != undefined:
                if not creep.pos.isNearTo(target):
                    return [ScheduledAction.moveTo(creep, target, priority=20)]
                return [ScheduledAction.attack(creep, target, priority=19)]
        return []
