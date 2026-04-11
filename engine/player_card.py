"""Player card data model for Statis Pro Football (5th Edition).

5th-edition card structure:
  * QB cards: 48 rows (Pass Numbers 1-48) × columns (short_pass, long_pass,
    quick_pass).  Each cell is a receiver letter (A-E), "INC", or "INT".
  * RB cards: 12 rows (Run Numbers 1-12) × columns (inside_run, outside_run,
    sweep).  Each cell is yardage, "FUMBLE", "BREAKAWAY", or "TD".
  * WR/TE (receiver) cards: 48 rows × columns (short_reception,
    long_reception).  Each cell is yardage or "INC".
  * K cards: fg_chart + xp_rate  (unchanged from earlier editions).
  * P cards: avg_distance + inside_20_rate  (unchanged).
  * DEF cards: pass_rush_rating, coverage_rating, run_stop_rating,
    plus a defender_letter for FAC blocking-matchup resolution.

The old 64-slot (11-88) columns are preserved in legacy_* fields for
backward-compatible loading of pre-5th-edition team data.
"""
from dataclasses import dataclass, field
from typing import Dict, Optional, Any, List
from enum import Enum


class Position(str, Enum):
    QB = "QB"
    RB = "RB"
    WR = "WR"
    TE = "TE"
    K = "K"
    P = "P"
    DEF = "DEF"
    OL = "OL"
    DL = "DL"
    LB = "LB"
    CB = "CB"
    S = "S"


class Grade(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


# 5th-edition pass-number slots (strings "1" through "48")
PASS_SLOTS = [str(n) for n in range(1, 49)]
PASS_SLOT_COUNT = 48

# 5th-edition run-number slots (strings "1" through "12")
RUN_SLOTS = [str(n) for n in range(1, 13)]
RUN_SLOT_COUNT = 12

# Legacy 64-slot keys (for backward compatibility)
ALL_SLOTS = [f"{t}{o}" for t in range(1, 9) for o in range(1, 9)]
LEGACY_SLOT_COUNT = 64

# Receiver letters used on QB cards
RECEIVER_LETTERS = ["A", "B", "C", "D", "E"]

ResultDict = Dict[str, Any]
CardColumn = Dict[str, ResultDict]


@dataclass
class PlayerCard:
    player_name: str
    team: str
    position: str
    number: int
    overall_grade: str = "C"

    # Receiver letter (A-E) — used to link QB card results to receiver cards
    receiver_letter: str = ""

    # ── QB passing columns (5th ed: 48 rows, result = receiver letter / INC / INT)
    short_pass: CardColumn = field(default_factory=dict)
    long_pass: CardColumn = field(default_factory=dict)
    quick_pass: CardColumn = field(default_factory=dict)

    # ── RB / QB rushing columns (5th ed: 12 rows, result = yards / FUMBLE / etc.)
    inside_run: CardColumn = field(default_factory=dict)
    outside_run: CardColumn = field(default_factory=dict)
    sweep: CardColumn = field(default_factory=dict)  # new: sweep column

    # ── WR / TE reception columns (5th ed: 48 rows)
    short_reception: CardColumn = field(default_factory=dict)
    long_reception: CardColumn = field(default_factory=dict)

    # ── Kicker
    fg_chart: Dict[str, float] = field(default_factory=dict)
    xp_rate: float = 0.95

    # ── Punter
    avg_distance: float = 44.0
    inside_20_rate: float = 0.35

    # ── Defense
    pass_rush_rating: int = 50
    coverage_rating: int = 50
    run_stop_rating: int = 50
    defender_letter: str = ""  # A-M defensive player letter for FAC matchups

    stats_summary: Dict[str, Any] = field(default_factory=dict)

    # ── Legacy columns (for backward compatibility with old 64-slot data)
    screen_pass: CardColumn = field(default_factory=dict)
    qb_rush: CardColumn = field(default_factory=dict)
    punt_column: CardColumn = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "name": self.player_name,
            "position": self.position,
            "number": self.number,
            "team": self.team,
            "overall_grade": self.overall_grade,
            "receiver_letter": self.receiver_letter,
            "short_pass": self.short_pass,
            "long_pass": self.long_pass,
            "quick_pass": self.quick_pass,
            "screen_pass": self.screen_pass,
            "qb_rush": self.qb_rush,
            "inside_run": self.inside_run,
            "outside_run": self.outside_run,
            "sweep": self.sweep,
            "short_reception": self.short_reception,
            "long_reception": self.long_reception,
            "fg_chart": self.fg_chart,
            "xp_rate": self.xp_rate,
            "punt_column": self.punt_column,
            "avg_distance": self.avg_distance,
            "inside_20_rate": self.inside_20_rate,
            "pass_rush_rating": self.pass_rush_rating,
            "coverage_rating": self.coverage_rating,
            "run_stop_rating": self.run_stop_rating,
            "defender_letter": self.defender_letter,
            "stats_summary": self.stats_summary,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PlayerCard":
        card = cls(
            player_name=data.get("name", "Unknown"),
            team=data.get("team", ""),
            position=data.get("position", ""),
            number=data.get("number", 0),
            overall_grade=data.get("overall_grade", "C"),
        )
        card.receiver_letter = data.get("receiver_letter", "")
        card.short_pass = data.get("short_pass", {})
        card.long_pass = data.get("long_pass", {})
        card.quick_pass = data.get("quick_pass", {})
        card.screen_pass = data.get("screen_pass", {})
        card.qb_rush = data.get("qb_rush", {})
        card.inside_run = data.get("inside_run", {})
        card.outside_run = data.get("outside_run", {})
        card.sweep = data.get("sweep", {})
        card.short_reception = data.get("short_reception", {})
        card.long_reception = data.get("long_reception", {})
        card.fg_chart = data.get("fg_chart", {})
        card.xp_rate = data.get("xp_rate", 0.95)
        card.punt_column = data.get("punt_column", {})
        card.avg_distance = data.get("avg_distance", 44.0)
        card.inside_20_rate = data.get("inside_20_rate", 0.35)
        card.pass_rush_rating = data.get("pass_rush_rating", 50)
        card.coverage_rating = data.get("coverage_rating", 50)
        card.run_stop_rating = data.get("run_stop_rating", 50)
        card.defender_letter = data.get("defender_letter", "")
        card.stats_summary = data.get("stats_summary", {})
        return card
