# TODO: special mode to build containers for mining
# when building a container, check if it's next to a source. If it is, try to reserve it and stand on it, then mine and build alternating ticks
# of we can't stand on it, try to find some other non-wall place next to the source that is close enough to the container to be able to build it and do the same
# otherwise do the regular thing harvesters do

# have virtual construction sites

# build roads from controller to the sources from farthest to closest (starting at source side), then to spawn

from ..defs import *

from creeps.harvester import Harvester

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


class Settler(Harvester):
    ICON = '🌾'
    FILL_UP_BEFORE_LEAVING = False  # doesn't reset source :/
    #DEBUG = True
