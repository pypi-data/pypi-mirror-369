import enum


class UpgradeType(enum.Enum):
    BIGGER_SAIL = 0
    BETTER_DEFENCES = 1
    MAP_READING = 2
    IMPROVED_LOOKOUT = 3


class Upgrade:
    def __init__(
        self,
        type: UpgradeType,
        name: str,
        cost: int,
        effect: str,
    ):
        self.type = type
        self.name = name
        self.cost = cost
        self.effect = effect
