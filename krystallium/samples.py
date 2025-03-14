import enum

import pydantic


class Action(enum.StrEnum):
    Creating = "creating"
    Destroying = "destroying"
    Increasing = "increasing"
    Decreasing = "decreasing"
    Expanding = "expanding"
    Contracting = "contracting"
    Fortifying = "fortifying"
    Deteriorating = "deteriorating"
    Lightening = "lightening"
    Encumbering = "encumbering"
    Heating = "heating"
    Cooling = "cooling"
    Conducting = "conducting"
    Insulating = "insulating"
    Absorbing = "absorbing"
    Releasing = "releasing"
    Solidifying = "solidifying"

    @staticmethod
    def is_opposite(first, second):
        match first:
            case Action.Creating:
                return second == Action.Destroying
            case Action.Destroying:
                return second == Action.Creating
            case Action.Increasing:
                return second == Action.Decreasing
            case Action.Decreasing:
                return second == Action.Increasing
            case Action.Expanding:
                return second == Action.Contracting
            case Action.Contracting:
                return second == Action.Expanding
            case Action.Fortifying:
                return second == Action.Deteriorating
            case Action.Deteriorating:
                return second == Action.Fortifying
            case Action.Lightening:
                return second == Action.Encumbering
            case Action.Encumbering:
                return second == Action.Lightening
            case Action.Heating:
                return second == Action.Cooling
            case Action.Cooling:
                return second == Action.Heating
            case Action.Conducting:
                return second == Action.Insulating
            case Action.Insulating:
                return second == Action.Conducting
            case Action.Absorbing:
                return second == Action.Releasing
            case Action.Releasing:
                return second == Action.Absorbing
            case Action.Solidifying:
                return False


class Target(enum.StrEnum):
    Energy = "energy"
    Light = "light"
    Sound = "sound"
    Flesh = "flesh"
    Krystal = "krystal"
    Gas = "gas"
    Liquid = "liquid"
    Solid = "solid"
    Mind = "mind"
    Plant = "plant"

    def to_int(self):
        match self:
            case Target.Mind:
                return 1
            case Target.Sound:
                return 2
            case Target.Light:
                return 3
            case Target.Energy:
                return 4
            case Target.Gas:
                return 5
            case Target.Liquid:
                return 6
            case Target.Plant:
                return 7
            case Target.Flesh:
                return 8
            case Target.Solid:
                return 9
            case Target.Krystal:
                return 10


class Purity(enum.IntEnum):
    Unknown = 0
    Polluted = 2
    Tarnished = 3
    Dirty = 4
    Blemished = 5
    Impure = 6
    Unblemished = 7
    Lucid = 8
    Stainless = 9
    Pristine = 10
    Immaculate = 11
    Perfect = 12

    @classmethod
    def from_string(cls, name):
        for key, value in cls.__members__.items():
            if key.lower() == name.lower():
                return cls(value)
        return cls.Unknown


@pydantic.dataclasses.dataclass(kw_only = True, frozen = True)
class RefinedSample:
    id: str = ""
    rfid_id: str = ""

    primary_action: Action
    primary_target: Target
    secondary_action: Action
    secondary_target: Target
    purity: Purity

    @classmethod
    def from_traits(cls, rfid_id: str, traits: list[str]):
        return cls(
            rfid_id = rfid_id,
            primary_action = traits[1],
            primary_target = traits[2],
            secondary_action = traits[3],
            secondary_target = traits[4],
            purity = Purity.from_string(traits[6]),
        )
