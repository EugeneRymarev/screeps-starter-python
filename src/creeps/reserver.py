__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')


from creeps.scheduled_action import ScheduledAction
from creeps.claimer import Claimer


class Reserver(Claimer):
    DEBUG = True
    ICON = 'R'
    ACTION = ScheduledAction.claimController
