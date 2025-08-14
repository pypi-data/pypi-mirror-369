from enum import Enum

class ScalePrefix(Enum):
    giga = 0
    mega = 1
    kilo = 2
    one = 3
    milli = 4
    micro = 5
    nano = 6
    angstrom = 7
    pico = 8
    femto = 9

class ScaleUnit(Enum):
    Volt = 0
    Amper = 1
    Hertz = 2
    Meter = 3
    Gram = 4
    Gauss = 5
    Degrees = 6
    Newton = 7
    Farad = 8
    Ohm = 9
    VoltRms = 10