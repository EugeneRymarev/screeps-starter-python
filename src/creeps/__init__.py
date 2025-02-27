from creeps.builder import Builder
from creeps.harvester import Harvester
from creeps.miner import Miner
from creeps.hauler import Hauler
from creeps.scout import Scout
from creeps.claimer import Claimer
from creeps.upgrader import Upgrader
from creeps.settler import Settler
from creeps.cleanser import Cleanser
from creeps.extractor import Extractor
from creeps.operator import Operator
from creeps.reserver import Reserver


CREEP_CLASSES = dict({
    'builder': Builder,
    'harvester': Harvester,
    'miner': Miner,
    'hauler': Hauler,
    'scout': Scout,
    'claimer': Claimer,
    'upgrader': Upgrader,
    'settler': Settler,
    'cleanser': Cleanser,
    'extractor': Extractor,
    'operator': Operator,
    'reserver': Reserver,
})
