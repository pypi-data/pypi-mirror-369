from typing import Literal, TypeAlias


InterOperator: TypeAlias = Literal[
    "Swap<2, 0>",
    "Swap<2, 1>",
    "Swap<2, 2>",
    "Relocate",
    "SwapStar",
    "Cross",
    "SdSwapStar",
    "SdSwapOneOne",
    "SdSwapTwoOne",
]

IntraOperator: TypeAlias = Literal[
    "Exchange",
    "OrOpt<1>",
    "OrOpt<2>",
    "OrOpt<3>",
]

AcceptanceRuleType: TypeAlias = Literal["HC", "HCWE", "LAHC", "SA"]

RuinMethodType: TypeAlias = Literal["SISRs", "Random"]

Sorter: TypeAlias = Literal[
    "random",
    "demand",
    "far",
    "close",
]

InputFormat: TypeAlias = Literal["DENSE_MATRIX", "COORD_LIST"]
