# ruff: noqa: D102, ANN401

from dataclasses import dataclass
from typing import Any

from aiwolf_nlp_common.packet.role import Species


@dataclass
class Judge:
    """占い結果や霊能結果などの判定結果を示す情報の構造体.

    Attributes:
        day (int): 判定が出た日数.
        agent (str): 判定を出したエージェントの名前.
        target (str): 判定の対象となったエージェントの名前.
        result (Species): 判定結果.
    """

    day: int
    agent: str
    target: str
    result: Species

    @staticmethod
    def from_dict(obj: Any) -> "Judge":
        _day = int(obj.get("day"))
        _agent = str(obj.get("agent"))
        _target = str(obj.get("target"))
        _result = Species(obj.get("result"))
        return Judge(_day, _agent, _target, _result)
