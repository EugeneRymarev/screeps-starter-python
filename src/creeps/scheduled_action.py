from ..defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


from creeps.action_execution import ActionExecution


class ScheduledAction:
    @classmethod
    def moveTo(cls, creep, target, on_error=None, priority=100):
        return ActionExecution(creep, 'moveTo', target, on_error=on_error, priority=priority)

    @classmethod
    def moveByPath(cls, creep, path, on_error=None, priority=100):
        return ActionExecution(creep, 'moveByPath', path, on_error=on_error, priority=priority)

    @classmethod
    def upgradeController(cls, creep, target, priority=100):
        return ActionExecution(creep, 'upgradeController', target, priority=priority)

    @classmethod
    def attackController(cls, creep, target, priority=100):
        return ActionExecution(creep, 'attackController', target, priority=priority)

    @classmethod
    def claimController(cls, creep, target, priority=100):
        return ActionExecution(creep, 'claimController', target, priority=priority)

    @classmethod
    def signController(cls, creep, target, text, priority=100):
        return ActionExecution(creep, 'signController', target, text, priority=priority)

    @classmethod
    def build(cls, creep, target, priority=100):
        return ActionExecution(creep, 'build', target, priority=priority)

    @classmethod
    def repair(cls, creep, target, priority=100):
        return ActionExecution(creep, 'repair', target, priority=priority)

    @classmethod
    def attack(cls, creep, target, priority=200):
        return ActionExecution(creep, 'attack', target, priority=priority)

    @classmethod
    def dismantle(cls, creep, target, priority=100):
        return ActionExecution(creep, 'dismantle', target, priority=priority)

    @classmethod
    def harvest(cls, creep, target, priority=100):
        return ActionExecution(creep, 'harvest', target, priority=priority)

    @classmethod
    def transfer(cls, creep, target, what, on_error=None, priority=100):
        return ActionExecution(creep, 'transfer', target, what, on_error, priority=priority)

    @classmethod
    def drop(cls, creep, what, on_error=None, priority=100):
        return ActionExecution(creep, 'drop', what, on_error, priority=priority)

    @classmethod
    def pickup(cls, creep, target, on_error=None, priority=100):
        return ActionExecution(creep, 'pickup', target, on_error, priority=priority)

    @classmethod
    def withdraw(cls, creep, target, what, on_error=None, priority=100):
        return ActionExecution(creep, 'withdraw', target, what, on_error, priority=priority)
