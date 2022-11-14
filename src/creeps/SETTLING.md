put settler1 flag on the first waypoint and move it manually as the creep goes over it, unless one is enough

Game.spawns["W24N2-2"].spawnCreep([CLAIM, MOVE, MOVE, MOVE, MOVE, MOVE], "settler1", {"memory": {"room": "W25N3", "cls": "claimer"}})
Game.spawns["W24N2-2"].spawnCreep([ATTACK, ATTACK, ATTACK, ATTACK, ATTACK, ATTACK, ATTACK, ATTACK, ATTACK, ATTACK, MOVE, MOVE, MOVE, MOVE, MOVE], "cleanser1", {"memory": {"room": "W25N3", "cls": "cleanser"}})

Game.spawns["W24N2-2"].spawnCreep([CLAIM, WORK, CARRY, CARRY, CARRY, CARRY, MOVE, MOVE, MOVE, MOVE, MOVE, MOVE], "settler1", {"memory": {"room": "W27N3", "cls": "settler"}})
Game.spawns["W24N2-2"].spawnCreep([WORK, CARRY, CARRY, CARRY, CARRY, MOVE, MOVE, MOVE, MOVE, MOVE], "settler3", {"memory": {"room": "W26N2", "cls": "settler"}})
Game.spawns["W24N2-2"].spawnCreep([WORK, WORK, WORK, WORK, CARRY, CARRY, CARRY, CARRY, MOVE, MOVE, MOVE, MOVE, MOVE, MOVE, MOVE, MOVE], "settler4", {"memory": {"room": "W26N2", "cls": "settler"}})

tag other creeps with the target room and give them flags if necessary or 
Game.spawns["Spawn1"].spawnCreep([WORK, WORK, WORK, WORK, WORK, CARRY, CARRY, CARRY, CARRY, CARRY, MOVE, MOVE, MOVE, MOVE, MOVE], "settler2", {"memory": {"room": "TARGET_ROOM", "cls": "harvester"}})
Game.spawns["W24N2-3"].spawnCreep([WORK, WORK, WORK, WORK, WORK, CARRY, CARRY, CARRY, CARRY, CARRY, MOVE, MOVE, MOVE, MOVE, MOVE], "BOB2", {"memory": {"room": "W23N2", "cls": "builder"}})
Game.spawns["W24N2-3"].spawnCreep([WORK, WORK, WORK, WORK, WORK, CARRY, CARRY, CARRY, CARRY, CARRY, MOVE, MOVE, MOVE, MOVE, MOVE], "BOB-W25N2", {"memory": {"room": "W25N2", "cls": "settler"}})
Game.spawns["Spawn1"].spawnCreep([WORK, WORK, WORK, WORK, WORK, CARRY, CARRY, CARRY, CARRY, CARRY, MOVE, MOVE, MOVE, MOVE, MOVE, MOVE, MOVE, MOVE, MOVE, MOVE, MOVE, MOVE, MOVE, MOVE, MOVE], "settler17", {"memory": {"room": "W25S1", "cls": "builder"}})

Game.spawns["W27N1-2"].spawnCreep([WORK, WORK, WORK, WORK, WORK, MOVE, MOVE, MOVE, MOVE, MOVE], "settler2", {"memory": {"room": "W25N3", "cls": "miner"}, "directions": [BOTTOM]})

Game.spawns["W26N2-1"].spawnCreep([WORK, WORK, CARRY, MOVE], "super2", {"memory": {"cls": "harvester"}, "directions": [TOP]})

Game.spawns["Spawn3"].spawnCreep([ATTACK, ATTACK, ATTACK, ATTACK, ATTACK, ATTACK, ATTACK, ATTACK, ATTACK, ATTACK, ATTACK, ATTACK, MOVE, MOVE, MOVE, MOVE], "cleanser1", {"memory": {"cls": "cleanser", "room": "W23N3"}})





Game.spawns["W26N2-1"].spawnCreep([WORK, WORK, WORK, WORK, WORK, CARRY, CARRY, CARRY, CARRY, CARRY, MOVE, MOVE, MOVE, MOVE, MOVE], "BOB-W27N2a", {"memory": {"room": "W27N2", "cls": "settler"}})

Game.spawns["W25N3-2"].spawnCreep([WORK, WORK, WORK, WORK, WORK, CARRY, CARRY, CARRY, CARRY, CARRY, MOVE, MOVE, MOVE, MOVE, MOVE], "BOB-W26N3b", {"memory": {"room": "W26N3", "cls": "settler"}})

Game.spawns["W28N4-1"].spawnCreep([WORK, WORK, WORK, WORK, WORK, CARRY, CARRY, CARRY, CARRY, CARRY, MOVE, MOVE, MOVE, MOVE, MOVE], "BOB-W27N3b", {"memory": {"room": "W27N3", "cls": "settler"}})

