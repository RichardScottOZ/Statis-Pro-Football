"""Tests for the injury replacement grid fix and endurance enforcement."""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.player_card import PlayerCard
from engine.team import Team, Roster
from engine.game import Game, GameState
from engine.play_resolver import PlayResolver


# ── Helpers ──────────────────────────────────────────────────────────────────

def _make_rb(name, number=20, endurance=0):
    return PlayerCard(
        player_name=name, team="TST", position="RB", number=number,
        overall_grade="C", endurance_rushing=endurance,
    )


def _make_wr(name, number=80, endurance=0):
    return PlayerCard(
        player_name=name, team="TST", position="WR", number=number,
        overall_grade="C", endurance_rushing=endurance,
    )


def _make_qb(name="TestQB", number=7):
    return PlayerCard(
        player_name=name, team="TST", position="QB", number=number,
        overall_grade="B",
    )


def _make_te(name="TestTE", number=85, endurance=0):
    return PlayerCard(
        player_name=name, team="TST", position="TE", number=number,
        overall_grade="C", endurance_rushing=endurance,
    )


def _make_ol(name, position, number):
    return PlayerCard(
        player_name=name, team="TST", position=position, number=number,
        overall_grade="C",
    )


def _make_def(name, position, number):
    return PlayerCard(
        player_name=name, team="TST", position=position, number=number,
        overall_grade="C",
    )


def _build_roster(rbs=None, qbs=None, wrs=None, tes=None):
    """Build a minimal roster for testing."""
    rbs = rbs or [_make_rb("RB1", 20), _make_rb("RB2", 22)]
    qbs = qbs or [_make_qb()]
    wrs = wrs or [_make_wr("WR1", 80), _make_wr("WR2", 81)]
    tes = tes or [_make_te("TE1", 85)]
    ol = [
        _make_ol("LT", "LT", 70),
        _make_ol("LG", "LG", 71),
        _make_ol("C", "C", 72),
        _make_ol("RG", "RG", 73),
        _make_ol("RT", "RT", 74),
    ]
    defenders = [_make_def(f"DEF{i}", pos, 50 + i)
                 for i, pos in enumerate(["DE", "DT", "DT", "DE",
                                          "LB", "LB", "LB",
                                          "CB", "CB", "SS", "FS"])]
    return Roster(
        qbs=qbs, rbs=rbs, wrs=wrs, tes=tes,
        kickers=[], punters=[],
        offensive_line=ol, defenders=defenders,
    )


def _build_game():
    """Build a minimal Game with two teams."""
    home_roster = _build_roster()
    away_roster = _build_roster(
        rbs=[_make_rb("AwayRB1", 30), _make_rb("AwayRB2", 32)],
        qbs=[_make_qb("AwayQB", 12)],
        wrs=[_make_wr("AwayWR1", 83), _make_wr("AwayWR2", 84)],
        tes=[_make_te("AwayTE1", 86)],
    )
    home = Team(abbreviation="HOM", city="Home", name="Tester",
                conference="AFC", division="North", roster=home_roster)
    away = Team(abbreviation="AWY", city="Away", name="Visitor",
                conference="NFC", division="South", roster=away_roster)
    return Game(home, away)


# ═════════════════════════════════════════════════════════════════════════════
#  Part 1 — Injury Replacement Grid Fix
# ═════════════════════════════════════════════════════════════════════════════

class TestImmediateInjurySwap:
    """Verify _immediate_injury_swap promotes backup into starter slot."""

    def test_rb_injury_swaps_starter_slot(self):
        game = _build_game()
        team = game.get_offense_team()
        rb1_name = team.roster.rbs[0].player_name
        rb2_name = team.roster.rbs[1].player_name

        # Mark RB1 as injured
        game.state.injuries[rb1_name] = 4

        # Trigger the swap
        game._immediate_injury_swap(rb1_name)

        # After swap, rbs[0] should be the backup
        assert team.roster.rbs[0].player_name == rb2_name
        # The injured player should now be in rbs[1]
        assert team.roster.rbs[1].player_name == rb1_name

    def test_wr_injury_swaps_starter_slot(self):
        game = _build_game()
        team = game.get_offense_team()
        wr1_name = team.roster.wrs[0].player_name
        wr2_name = team.roster.wrs[1].player_name

        game.state.injuries[wr1_name] = 4
        game._immediate_injury_swap(wr1_name)

        assert team.roster.wrs[0].player_name == wr2_name

    def test_swap_only_happens_for_starter(self):
        """No swap if the injured player isn't in the starter slot."""
        game = _build_game()
        team = game.get_offense_team()
        rb1_name = team.roster.rbs[0].player_name
        rb2_name = team.roster.rbs[1].player_name

        # Injure the backup (rbs[1])
        game.state.injuries[rb2_name] = 4
        game._immediate_injury_swap(rb2_name)

        # Starter slot unchanged
        assert team.roster.rbs[0].player_name == rb1_name

    def test_swap_generates_personnel_note(self):
        game = _build_game()
        game._current_play_personnel_note = None
        team = game.get_offense_team()
        rb1_name = team.roster.rbs[0].player_name

        game.state.injuries[rb1_name] = 4
        game._immediate_injury_swap(rb1_name)

        # Personnel note should mention the auto-sub
        assert game._current_play_personnel_note is not None
        assert "Auto-sub" in game._current_play_personnel_note
        assert rb1_name in game._current_play_personnel_note

    def test_get_rb_returns_healthy_after_swap(self):
        """After immediate swap, get_rb() should return the backup."""
        game = _build_game()
        team = game.get_offense_team()
        rb1_name = team.roster.rbs[0].player_name
        rb2_name = team.roster.rbs[1].player_name

        game.state.injuries[rb1_name] = 4
        game._immediate_injury_swap(rb1_name)

        # get_rb() should now return the backup without further swapping
        rb = game.get_rb()
        assert rb.player_name == rb2_name


# ═════════════════════════════════════════════════════════════════════════════
#  Part 2 — Endurance Enforcement
# ═════════════════════════════════════════════════════════════════════════════

class TestGameEnduranceCheck:
    """Test the game-level _check_endurance_violation method."""

    def test_endurance_0_never_violates(self):
        game = _build_game()
        rb = _make_rb("Workhorse", endurance=0)
        # Even if used on last play
        game.state.last_ball_carrier = "Workhorse"
        game.state.prev_ball_carrier = "Workhorse"
        game.state.endurance_used_this_drive.add("Workhorse")
        game.state.endurance_used_this_quarter.add("Workhorse")
        assert game._check_endurance_violation(rb) is None

    def test_endurance_1_violation_consecutive(self):
        game = _build_game()
        rb = _make_rb("SpeedBack", endurance=1)
        game.state.last_ball_carrier = "SpeedBack"
        assert game._check_endurance_violation(rb) == "endurance_1"

    def test_endurance_1_ok_after_rest(self):
        game = _build_game()
        rb = _make_rb("SpeedBack", endurance=1)
        game.state.last_ball_carrier = "OtherPlayer"
        game.state.prev_ball_carrier = "SpeedBack"
        # Only last_ball_carrier matters for endurance 1
        assert game._check_endurance_violation(rb) is None

    def test_endurance_2_violation_one_play_ago(self):
        game = _build_game()
        rb = _make_rb("MediumBack", endurance=2)
        game.state.last_ball_carrier = "MediumBack"
        assert game._check_endurance_violation(rb) == "endurance_2"

    def test_endurance_2_violation_two_plays_ago(self):
        game = _build_game()
        rb = _make_rb("MediumBack", endurance=2)
        game.state.last_ball_carrier = "OtherPlayer"
        game.state.prev_ball_carrier = "MediumBack"
        assert game._check_endurance_violation(rb) == "endurance_2"

    def test_endurance_2_ok_after_two_rest(self):
        game = _build_game()
        rb = _make_rb("MediumBack", endurance=2)
        game.state.last_ball_carrier = "Other1"
        game.state.prev_ball_carrier = "Other2"
        assert game._check_endurance_violation(rb) is None

    def test_endurance_3_violation_same_drive(self):
        game = _build_game()
        rb = _make_rb("LimitedBack", endurance=3)
        game.state.endurance_used_this_drive.add("LimitedBack")
        assert game._check_endurance_violation(rb) == "endurance_3"

    def test_endurance_3_ok_new_drive(self):
        game = _build_game()
        rb = _make_rb("LimitedBack", endurance=3)
        # Not in the set → OK
        assert game._check_endurance_violation(rb) is None

    def test_endurance_4_violation_same_quarter(self):
        game = _build_game()
        rb = _make_rb("RareBack", endurance=4)
        game.state.endurance_used_this_quarter.add("RareBack")
        assert game._check_endurance_violation(rb) == "endurance_4"

    def test_endurance_4_ok_new_quarter(self):
        game = _build_game()
        rb = _make_rb("RareBack", endurance=4)
        assert game._check_endurance_violation(rb) is None


class TestEnduranceResets:
    """Verify endurance tracking resets on possession/quarter changes."""

    def test_drive_endurance_resets_on_possession_change(self):
        game = _build_game()
        game.state.endurance_used_this_drive.add("SomePlayer")
        game.state.last_ball_carrier = "SomePlayer"
        game.state.prev_ball_carrier = "SomePlayer"

        game._change_possession(25)

        assert len(game.state.endurance_used_this_drive) == 0
        assert game.state.last_ball_carrier is None
        assert game.state.prev_ball_carrier is None

    def test_quarter_endurance_resets_on_quarter_change(self):
        game = _build_game()
        game.state.endurance_used_this_quarter.add("SomePlayer")
        game.state.time_remaining = 0  # Force quarter change

        game._advance_time(0)  # Trigger the check

        assert len(game.state.endurance_used_this_quarter) == 0

    def test_endurance_usage_recorded(self):
        game = _build_game()
        game._record_endurance_usage("TestRB")

        assert "TestRB" in game.state.endurance_used_this_drive
        assert "TestRB" in game.state.endurance_used_this_quarter

    def test_endurance_usage_not_recorded_for_none(self):
        game = _build_game()
        game._record_endurance_usage(None)

        assert len(game.state.endurance_used_this_drive) == 0
        assert len(game.state.endurance_used_this_quarter) == 0


class TestEndurancePenaltyRun:
    """Verify +2 RN penalty is applied for run endurance violations."""

    def test_penalty_applied(self):
        game = _build_game()
        rb = _make_rb("TiredRB", endurance=1)
        game.state.last_ball_carrier = "TiredRB"

        rn, violation = game._apply_endurance_penalty_to_run(rb, 5)
        assert rn == 7
        assert violation == "endurance_1"

    def test_no_penalty_when_rested(self):
        game = _build_game()
        rb = _make_rb("FreshRB", endurance=1)
        game.state.last_ball_carrier = "OtherPlayer"

        rn, violation = game._apply_endurance_penalty_to_run(rb, 5)
        assert rn == 5
        assert violation is None

    def test_no_penalty_for_endurance_0(self):
        game = _build_game()
        rb = _make_rb("Workhorse", endurance=0)
        game.state.last_ball_carrier = "Workhorse"

        rn, violation = game._apply_endurance_penalty_to_run(rb, 5)
        assert rn == 5
        assert violation is None
