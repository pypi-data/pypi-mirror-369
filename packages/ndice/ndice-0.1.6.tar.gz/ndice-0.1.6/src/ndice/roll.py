from .dice import Dice
from .rng import high, low, mid, RNG, rng


class Roll:
    def __init__(self, rng: RNG):
        self.rng = rng

    def __call__(self, *dice_expression: Dice) -> int:
        total = 0
        for dice_term in dice_expression:
            total = dice_term.op(total, sum(self.each_die(dice_term)))
        return total

    def each_die(self, dice: Dice) -> list[int]:
        if dice.is_mod:
            return [dice.number * dice.sides]
        else:
            return [self.rng(dice.sides) for _ in range(dice.number)]


min_roll = roll_low = Roll(low)
max_roll = roll_high = Roll(high)

roll = Roll(rng)
roll_mid = Roll(mid)
