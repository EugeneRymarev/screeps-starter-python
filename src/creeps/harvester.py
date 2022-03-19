from ..defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')

from creeps.easy import EasyCreep


class Harvester(EasyCreep):
    ICON = '☭'
    def _get_source_getters(self):
        result = []
        #if not self.class_exists('hauler'):  # TODO: this gets weird in transition from RCL 4 to 5
        #else:
        result.append(self._get_nearby_dropped_resource)
        result.append(self._get_nearby_energetic_ruin)
        result.append(self._get_nearby_energetic_tombstones)
        result.append(self._get_dropped_resource)
        if self.creep.room.energyCapacityAvailable - self.creep.room.energyAvailable >= 1 or self.creep.memory.cls == 'builder':
            result.append(self._get_refill_source)
        result.append(self._get_random_energetic_ruin)
        if not self.class_exists('hauler'):
            if self.creep.room.controller.level <= 2:
                result.append(self._get_closest_enemy_spawn)
                result.append(self._get_random_enemy_building)
        result.append(self._get_fullest_miner_container)
        if self.creep.room.controller.level >= 6 and self.class_exists('miner'):
            result.append(
                self._get_closest_link,
            )
        if not self.class_exists('miner'):  # TODO: scale with number of sources in the room
            result.append(self._get_neighboring_source)
        result.append(self._get_nonempty_storage)
        result.append(self._get_random_source)
        return result

    def _get_target_getters(self):
        result = [
            self._get_rcl1_controller,
            self._get_room_controller_if_low,
            self._get_spawn_construction_site,
        ]
        if not self.class_exists('hauler'):
            #if self.total_creeps_in_room() == 1:
            result.append(self._get_closest_nonempty_util_building)
            #else:
            #    result.append(self._get_random_nonempty_util_building)
        # TODO XXX: critical repairs?
        if not self.class_exists('builder') or self.creep.memory.cls == 'builder':
            result.append(self._get_closest_construction_site)
        #else:
        #    result.append(self._get_neighboring_construction_site)
        result.append(self._get_best_free_church)
        if self.creep.room.controller.level != 8 or not self.class_exists('upgrader'):
            result.append(self._get_room_controller)
        return result

