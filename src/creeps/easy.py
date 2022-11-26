from creeps.abstract import AbstractCreep
from creeps.parts.carry import Carry
from creeps.parts.work import Work
from creeps.scheduled_action import ScheduledAction
from utils import part_count

__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'name')
__pragma__('noalias', 'update')


class EasyCreep(AbstractCreep, Carry, Work):
    DEBUG = False
    ICON = '?'
    def __init__(self, creep, name, creep_registry):
        self.creep = creep
        #self.name = name  # proper no-alias
        self.creep_registry = creep_registry

    def _get_source_getters(self):
        raise NotImplementedError

    def _get_target_getters(self):
        raise NotImplementedError

    def _get_new_target(self):
        for target_getter in self._get_target_getters(self.creep):
            target = target_getter(self.creep)
            if target:
                return target
        if not (self.creep.memory.cls == 'hauler' and self.creep.room.controller.level >= 5):
            print('FATAL: no targets for', self.creep, '(', self.creep.memory.cls, ') and no default')

    def get_new_target(self):
        target = self._get_new_target()
        if target:
            print('new target for', self.creep, 'is', target)
            self.creep.memory.target = target.id
            return target

    def _run(self):
        super()._run()
        creep = self.creep
        # If we're full, stop filling up and remove the saved source
        if creep.memory.filling and creep.store.getFreeCapacity(RESOURCE_ENERGY) == 0:
            creep.memory.filling = False
            del creep.memory.source
        # If we're empty, start filling again and remove the saved target
        elif not creep.memory.filling and creep.store.getUsedCapacity(RESOURCE_ENERGY) <= 0:
            creep.memory.filling = True
            del creep.memory.target

        if creep.memory.filling:
            fill_actions = self.do_fill(creep)
            #if fill_actions[0].method == 'move':  # TODO: fill and go move to a new target, but no double transfer
            return fill_actions

        # If we have a saved target, use it
        if creep.memory.target:
            target = Game.getObjectById(creep.memory.target)
            if not target:
                target = self.get_new_target(creep)
            elif target.energy != undefined and target.energy == target.energyCapacity:
                # full container, probably someone else filled it last tick or helped filling it
                target = self.get_new_target(creep)
        else:
            target = self.get_new_target(creep)

        if not target:
            return []

        # If we are targeting a spawn or extension, we need to be directly next to it - otherwise, we can be 3 away.
        if target.energyCapacity or target.store:
            is_close = creep.pos.isNearTo(target)
        else:
            is_close = creep.pos.inRangeTo(target, 3)

        def reset_target():
            print('WARNING', creep, "reset_target() had to be called on", creep.memory.target)
            del creep.memory.target

        if not is_close:
            actions = []
            if target.structureType == STRUCTURE_STORAGE or target.structureType == STRUCTURE_CONTAINER or target.structureType == STRUCTURE_TERMINAL or target.structureType == STRUCTURE_LINK:
                if not target.store:
                    pass  # that's a construction site, not an actual thing
                    #print(creep, 'not gonna repair anything on the way because heading to c-site')
                #elif target.store[RESOURCE_ENERGY] >= 1000:
                else:
                    if creep.body[0].type == WORK:  # TODO: IN, not body[0]
                        #print(creep, 'gonna try to repair because target >= 1000 and WORK')
                        repair = self._get_nearby_repair_action()
                        if repair:
                            a = ScheduledAction.repair(creep, repair)
                            a.priority = 20
                            actions.append(a)
                        else:
                            build = self._get_nearby_build_action()
                            if build:
                                actions.append(ScheduledAction.build(creep, build, priority=20))
            actions.append(ScheduledAction.moveTo(creep, target, on_error=reset_target))
            return actions

        if target.creep != undefined:  # tombstone?
            print('NotImplementedError: tombstone target detectred but not implemented!', creep, target)
            pass

        # If we are targeting a spawn or extension, transfer energy. Otherwise, use upgradeController on it.
        if target.energyCapacity:
            actions = []
            actions.append(ScheduledAction.transfer(creep, target, RESOURCE_ENERGY, on_error=reset_target))
            if target.store.getFreeCapacity(RESOURCE_ENERGY) >= self.energy(creep):
                actions.extend(self.do_fill(creep))
                #print(creep, 'gooooo')  # TODO XXX: test it
            else:
                # we will fill it to the brim
                # maybe someone will pull from this container or spawn or something and in the next tick
                # it would need to be filled again - but in that case we will run self.get_new_target() with
                # next tick where we know what happened.
                # TODO: this didn't work, the creep got the same target and kept moving onto it over and over
                # the problem is with the simultaneous action sequence elimination or something, I guess?
                target = self.get_new_target(creep)  # TODO XXX: but this should be a different one!
                #actions.append(ScheduledAction.moveTo(creep, target))
            return actions

        # upgradeController
        if target.structureType == STRUCTURE_CONTROLLER:
            actions = [ScheduledAction.upgradeController(creep, target)]
            if creep.room.controller.ticksToDowngrade < 4000:
                actions[0].priority = 1000
            else:
                actions[0].priority = 20
            fill_actions = self.do_fill(creep)
            works = part_count(creep, 'work')
            if works * 1 >= creep.store[RESOURCE_ENERGY]: # TODO: multiply by upgrade cost per part per tick
                # there used to be: and fill_actions[0].method == 'withdraw':  
                # here but creeps can move and work in the same tick
                #actions.append(fill_actions[0])
                actions.extend(fill_actions)
            return actions

        # build
        if target.progressTotal:
            action = ScheduledAction.build(creep, target)
            action.priority = 200
            return [action]

        # store
        if target.store and (target.my or target.structureType == STRUCTURE_CONTAINER):
            if target.structureType == STRUCTURE_STORAGE or target.structureType == STRUCTURE_TERMINAL:
                for r in Object.keys(creep.store):
                    if r != RESOURCE_ENERGY:
                        return [ScheduledAction.transfer(creep, target, r, on_error=reset_target)]
            actions = [ScheduledAction.transfer(creep, target, RESOURCE_ENERGY, on_error=reset_target)]
            #if target.store.getFreeCapacity(RESOURCE_ENERGY) >= self.energy(creep):
            #    #print(creep, 'gooooo2')  # TODO XXX: flaps near storage if room really needs refill
            #    actions.extend(self.do_fill(creep))
            return actions

        # fortify
        if target.structureType == STRUCTURE_RAMPART or target.structureType == STRUCTURE_WALL:
            action = ScheduledAction.repair(creep, target, on_error=reset_target)
            action.priority = 5
            return [action]

        if is_close:
            print(creep, 'doing a fallback move towards', target, 'when it already arrived!')
            #return []

        actions = []
        actions.append(ScheduledAction.moveTo(creep, target))
        #print('ERROR: not sure what', creep, 'should do with', target)
        return actions
