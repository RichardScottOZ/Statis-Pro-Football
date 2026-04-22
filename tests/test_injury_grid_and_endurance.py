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

    def test_wr1_injury_with_3wrs_keeps_wr2_at_fl_puts_wr3_at_le(self):
        """Regression: WR1 (LE) injury should bring WR3 (backup) onto the field,
        NOT displace WR2 (FL) into the LE slot and pull WR3 into FL.

        Before fix: injuring WR1 promoted WR2 to WR1-slot, leaving WR3 to
        auto-fill FL — a bench player appeared on the field as the flanker.

        After fix: WR3 fills the vacated LE slot; WR2 stays at FL.
        """
        wr1 = _make_wr("Starter_LE", 80)  # depth-chart WR1 → LE
        wr2 = _make_wr("Starter_FL", 81)  # depth-chart WR2 → FL
        wr3 = _make_wr("Backup_WR", 82)   # bench player, must NOT auto-appear

        roster = _build_roster(wrs=[wr1, wr2, wr3])
        home = Team(abbreviation="HOM", city="Home", name="Tester",
                    conference="AFC", division="North", roster=roster)
        away_roster = _build_roster(
            rbs=[_make_rb("AwayRB1", 30), _make_rb("AwayRB2", 32)],
            qbs=[_make_qb("AwayQB", 12)],
            wrs=[_make_wr("AwayWR1", 83), _make_wr("AwayWR2", 84)],
            tes=[_make_te("AwayTE1", 86)],
        )
        away = Team(abbreviation="AWY", city="Away", name="Visitor",
                    conference="NFC", division="South", roster=away_roster)
        game = Game(home, away)
        game.state.possession = "home"

        # Injure WR1 (the LE starter) and trigger auto-sub
        game.state.injuries[wr1.player_name] = 4
        game._immediate_injury_swap(wr1.player_name)

        # Verify the roster swap used WR3 (true backup), not WR2 (the other starter)
        assert game.get_offense_team().roster.wrs[0].player_name == wr3.player_name, \
            "WR3 (backup) should now occupy the WR1 depth-chart slot"
        assert game.get_offense_team().roster.wrs[1].player_name == wr2.player_name, \
            "WR2 (Starter_FL) should remain unchanged in the depth chart"

        # Verify _get_all_receivers assigns the correct slots:
        # LE = WR3 (replaced WR1), FL = WR2 (unchanged)
        receivers = game._get_all_receivers()
        slots = {getattr(r, "_formation_slot", None): r.player_name for r in receivers}
        assert slots.get("LE") == wr3.player_name, \
            f"LE slot should be {wr3.player_name!r} (backup), got {slots.get('LE')!r}"
        assert slots.get("FL") == wr2.player_name, \
            f"FL slot should remain {wr2.player_name!r}, got {slots.get('FL')!r}"
        # The backup is already in LE; they must NOT also appear as FL
        fl_player = slots.get("FL")
        assert fl_player != wr3.player_name, \
            "Backup WR must not appear at both LE and FL"

    def test_rb1_injury_with_3rbs_keeps_rb2_at_bk2_puts_rb3_at_bk1(self):
        """Regression: RB1 (BK1) injury should bring RB3 (backup) onto the field,
        NOT displace RB2 (BK2) into the BK1 slot and pull RB3 into BK2.

        Mirrors the WR LE/FL fix: RB has two default starters (BK1 + BK2), so
        the same search_start = max(injured_idx+1, n_starters) protection applies.

        Before fix: injuring RB1 promoted RB2 to RB1-slot, leaving RB3 to
        auto-fill BK2 — a bench player appeared on the field as a second back.

        After fix: RB3 fills the vacated BK1 slot; RB2 stays at BK2.
        """
        rb1 = _make_rb("Starter_BK1", 20)  # depth-chart RB1 → BK1
        rb2 = _make_rb("Starter_BK2", 21)  # depth-chart RB2 → BK2
        rb3 = _make_rb("Backup_RB", 22)    # bench player, must NOT auto-appear

        roster = _build_roster(rbs=[rb1, rb2, rb3])
        home = Team(abbreviation="HOM", city="Home", name="Tester",
                    conference="AFC", division="North", roster=roster)
        away_roster = _build_roster(
            rbs=[_make_rb("AwayRB1", 30), _make_rb("AwayRB2", 32)],
            qbs=[_make_qb("AwayQB", 12)],
            wrs=[_make_wr("AwayWR1", 83), _make_wr("AwayWR2", 84)],
            tes=[_make_te("AwayTE1", 86)],
        )
        away = Team(abbreviation="AWY", city="Away", name="Visitor",
                    conference="NFC", division="South", roster=away_roster)
        game = Game(home, away)
        game.state.possession = "home"

        # Injure RB1 (the BK1 starter) and trigger auto-sub
        game.state.injuries[rb1.player_name] = 4
        game._immediate_injury_swap(rb1.player_name)

        # Verify the roster swap used RB3 (true backup), not RB2 (the other starter)
        assert game.get_offense_team().roster.rbs[0].player_name == rb3.player_name, \
            "RB3 (backup) should now occupy the RB1 depth-chart slot"
        assert game.get_offense_team().roster.rbs[1].player_name == rb2.player_name, \
            "RB2 (Starter_BK2) should remain unchanged in the depth chart"

        # Verify _get_all_receivers assigns the correct slots:
        # BK1 = RB3 (replaced RB1), BK2 = RB2 (unchanged)
        receivers = game._get_all_receivers()
        slots = {getattr(r, "_formation_slot", None): r.player_name for r in receivers}
        assert slots.get("BK1") == rb3.player_name, \
            f"BK1 slot should be {rb3.player_name!r} (backup), got {slots.get('BK1')!r}"
        assert slots.get("BK2") == rb2.player_name, \
            f"BK2 slot should remain {rb2.player_name!r}, got {slots.get('BK2')!r}"
        # The backup is already in BK1; they must NOT also appear as BK2
        assert slots.get("BK2") != rb3.player_name, \
            "Backup RB must not appear at both BK1 and BK2"

    def test_rb2_injury_with_3rbs_keeps_rb1_at_bk1_puts_rb3_at_bk2(self):
        """RB2 (BK2) injury should bring RB3 (backup) into BK2; RB1 stays at BK1."""
        rb1 = _make_rb("Starter_BK1", 20)
        rb2 = _make_rb("Starter_BK2", 21)
        rb3 = _make_rb("Backup_RB", 22)

        roster = _build_roster(rbs=[rb1, rb2, rb3])
        home = Team(abbreviation="HOM", city="Home", name="Tester",
                    conference="AFC", division="North", roster=roster)
        away_roster = _build_roster(
            rbs=[_make_rb("AwayRB1", 30), _make_rb("AwayRB2", 32)],
            qbs=[_make_qb("AwayQB", 12)],
            wrs=[_make_wr("AwayWR1", 83), _make_wr("AwayWR2", 84)],
            tes=[_make_te("AwayTE1", 86)],
        )
        away = Team(abbreviation="AWY", city="Away", name="Visitor",
                    conference="NFC", division="South", roster=away_roster)
        game = Game(home, away)
        game.state.possession = "home"

        game.state.injuries[rb2.player_name] = 4
        game._immediate_injury_swap(rb2.player_name)

        # RB1 must remain at index 0 (BK1 untouched); RB3 fills RB2's slot
        assert game.get_offense_team().roster.rbs[0].player_name == rb1.player_name, \
            "RB1 (Starter_BK1) should remain at index 0"
        assert game.get_offense_team().roster.rbs[1].player_name == rb3.player_name, \
            "RB3 (backup) should fill RB2's vacated slot"

        receivers = game._get_all_receivers()
        slots = {getattr(r, "_formation_slot", None): r.player_name for r in receivers}
        assert slots.get("BK1") == rb1.player_name, \
            f"BK1 should still be {rb1.player_name!r}"
        assert slots.get("BK2") == rb3.player_name, \
            f"BK2 should now be {rb3.player_name!r} (backup)"

    def test_qb_injury_swaps_to_backup_no_bench_player_on_field(self):
        """QB injury promotes QB2; no other position is displaced."""
        qb1 = _make_qb("Starter_QB", 1)
        qb2 = _make_qb("Backup_QB", 2)

        roster = _build_roster(qbs=[qb1, qb2])
        home = Team(abbreviation="HOM", city="Home", name="Tester",
                    conference="AFC", division="North", roster=roster)
        away_roster = _build_roster(
            rbs=[_make_rb("AwayRB1", 30), _make_rb("AwayRB2", 32)],
            qbs=[_make_qb("AwayQB", 12)],
            wrs=[_make_wr("AwayWR1", 83), _make_wr("AwayWR2", 84)],
            tes=[_make_te("AwayTE1", 86)],
        )
        away = Team(abbreviation="AWY", city="Away", name="Visitor",
                    conference="NFC", division="South", roster=away_roster)
        game = Game(home, away)
        game.state.possession = "home"

        game.state.injuries[qb1.player_name] = 4
        game._immediate_injury_swap(qb1.player_name)

        # QB2 should now be at index 0
        assert game.get_offense_team().roster.qbs[0].player_name == qb2.player_name, \
            "QB2 (backup) should now occupy the QB1 depth-chart slot"
        assert game.get_offense_team().roster.qbs[1].player_name == qb1.player_name, \
            "QB1 (injured) should be at index 1"

        # get_qb() should return QB2
        qb = game.get_qb()
        assert qb.player_name == qb2.player_name

    def test_te_injury_promotes_backup_te_to_re_slot(self):
        """TE1 injury promotes TE2 to the RE slot; LE/FL receivers unchanged."""
        te1 = _make_te("Starter_TE", 85)
        te2 = _make_te("Backup_TE", 86)
        wr1 = _make_wr("WR1", 80)
        wr2 = _make_wr("WR2", 81)

        roster = _build_roster(tes=[te1, te2], wrs=[wr1, wr2])
        home = Team(abbreviation="HOM", city="Home", name="Tester",
                    conference="AFC", division="North", roster=roster)
        away_roster = _build_roster(
            rbs=[_make_rb("AwayRB1", 30), _make_rb("AwayRB2", 32)],
            qbs=[_make_qb("AwayQB", 12)],
            wrs=[_make_wr("AwayWR1", 83), _make_wr("AwayWR2", 84)],
            tes=[_make_te("AwayTE1", 87)],
        )
        away = Team(abbreviation="AWY", city="Away", name="Visitor",
                    conference="NFC", division="South", roster=away_roster)
        game = Game(home, away)
        game.state.possession = "home"

        game.state.injuries[te1.player_name] = 4
        game._immediate_injury_swap(te1.player_name)

        # TE2 should now be at index 0 (RE slot)
        assert game.get_offense_team().roster.tes[0].player_name == te2.player_name, \
            "TE2 (backup) should now occupy the TE1 depth-chart slot"

        # WR slots (LE, FL) must be unaffected
        receivers = game._get_all_receivers()
        slots = {getattr(r, "_formation_slot", None): r.player_name for r in receivers}
        assert slots.get("LE") == wr1.player_name, "LE (WR1) should be unchanged"
        assert slots.get("FL") == wr2.player_name, "FL (WR2) should be unchanged"
        assert slots.get("RE") == te2.player_name, "RE should now be TE2 (backup)"



# ═════════════════════════════════════════════════════════════════════════════
#  Part 1b — 2TE / 3TE (JUMBO) Formation Injury Swap
# ═════════════════════════════════════════════════════════════════════════════

def _build_game_multi_te(wrs, tes, extra_te_backup=None):
    """Build a Game configured for multi-TE formation testing."""
    all_tes = list(tes)
    if extra_te_backup:
        all_tes.append(extra_te_backup)
    roster = _build_roster(wrs=wrs, tes=all_tes)
    home = Team(abbreviation="HOM", city="Home", name="Tester",
                conference="AFC", division="North", roster=roster)
    away_roster = _build_roster(
        rbs=[_make_rb("AwayRB1", 30), _make_rb("AwayRB2", 32)],
        qbs=[_make_qb("AwayQB", 12)],
        wrs=[_make_wr("AwayWR1", 83), _make_wr("AwayWR2", 84)],
        tes=[_make_te("AwayTE1", 90)],
    )
    away = Team(abbreviation="AWY", city="Away", name="Visitor",
                conference="NFC", division="South", roster=away_roster)
    game = Game(home, away)
    game.state.possession = "home"
    return game


class TestMultiTEFormationInjurySwap:
    """Verify _immediate_injury_swap is correct for 2TE and 3TE/JUMBO packages.

    Root cause of the bug: when a formation package puts N TEs on the field
    via explicit overrides and one of them is injured, the old code searched
    from injured_idx+1 — finding another on-field TE — and redirected the
    injured player's override slot to that on-field TE.  The on-field TE's own
    slot override was still in place, so _get_all_receivers assigned it to two
    slots simultaneously (double-assignment).

    Fix: when has_slot_override=True and multiple players of the same position
    are in on_field_offense, skip ALL of them and pull the first healthy bench
    player instead.
    """

    # ── 2TE_1WR package ──────────────────────────────────────────────

    def test_2te_package_te1_injury_keeps_te2_at_fl_puts_te3_at_re(self):
        """2TE_1WR: TE1 (RE) injury brings TE3 (backup) to RE; TE2 stays at FL."""
        wr1 = _make_wr("WR1", 80)
        te1 = _make_te("TE1_RE", 85)   # RE starter
        te2 = _make_te("TE2_FL", 86)   # FL starter (on field)
        te3 = _make_te("TE3_bench", 87)  # bench — should fill

        game = _build_game_multi_te([wr1], [te1, te2], extra_te_backup=te3)
        # Apply 2TE_1WR: WR1→LE, TE1→RE, TE2→FL
        game.apply_formation_package("home", "2TE_1WR")

        # Confirm package is set correctly
        overrides = game._on_field_offense["home"]
        assert overrides.get("LE") == wr1.player_name
        assert overrides.get("RE") == te1.player_name
        assert overrides.get("FL") == te2.player_name

        # Injure TE1 (RE)
        game.state.injuries[te1.player_name] = 4
        game._immediate_injury_swap(te1.player_name)

        # TE3 should be promoted into TE1's depth-chart slot
        tes_roster = game.get_offense_team().roster.tes
        assert tes_roster[0].player_name == te3.player_name, \
            "TE3 (backup) should be at index 0 after swap"
        assert tes_roster[1].player_name == te2.player_name, \
            "TE2 should remain at index 1 (unchanged)"

        # Override for RE should now point to TE3; FL stays TE2
        overrides = game._on_field_offense["home"]
        assert overrides.get("RE") == te3.player_name, \
            f"RE override should be TE3 (backup), got {overrides.get('RE')!r}"
        assert overrides.get("FL") == te2.player_name, \
            f"FL override must remain TE2 (on-field starter), got {overrides.get('FL')!r}"

        # _get_all_receivers must not double-assign TE2
        receivers = game._get_all_receivers()
        slots = {getattr(r, "_formation_slot", None): r.player_name for r in receivers}
        assert slots.get("RE") == te3.player_name, \
            f"RE slot should be TE3, got {slots.get('RE')!r}"
        assert slots.get("FL") == te2.player_name, \
            f"FL slot should still be TE2, got {slots.get('FL')!r}"
        # Exactly one slot per player — TE2 must NOT appear twice
        player_names = [n for n in slots.values()]
        assert player_names.count(te2.player_name) == 1, \
            "TE2 must not be assigned to two slots"

    def test_2te_package_te2_injury_keeps_te1_at_re_puts_te3_at_fl(self):
        """2TE_1WR: TE2 (FL) injury brings TE3 (backup) to FL; TE1 stays at RE."""
        wr1 = _make_wr("WR1", 80)
        te1 = _make_te("TE1_RE", 85)
        te2 = _make_te("TE2_FL", 86)
        te3 = _make_te("TE3_bench", 87)

        game = _build_game_multi_te([wr1], [te1, te2], extra_te_backup=te3)
        game.apply_formation_package("home", "2TE_1WR")

        game.state.injuries[te2.player_name] = 4
        game._immediate_injury_swap(te2.player_name)

        tes_roster = game.get_offense_team().roster.tes
        assert tes_roster[0].player_name == te1.player_name, \
            "TE1 should remain at index 0"
        assert tes_roster[1].player_name == te3.player_name, \
            "TE3 (backup) should fill TE2's vacated slot"

        overrides = game._on_field_offense["home"]
        assert overrides.get("RE") == te1.player_name, "RE stays TE1"
        assert overrides.get("FL") == te3.player_name, "FL updated to TE3"

        receivers = game._get_all_receivers()
        slots = {getattr(r, "_formation_slot", None): r.player_name for r in receivers}
        assert slots.get("RE") == te1.player_name
        assert slots.get("FL") == te3.player_name
        assert slots.get("LE") == wr1.player_name

    def test_2te_package_wr_injury_only_affects_le_slot(self):
        """2TE_1WR: WR1 (LE) injury should not disturb TE1/TE2 assignments."""
        wr1 = _make_wr("WR1_LE", 80)
        wr2 = _make_wr("WR2_bench", 81)   # backup WR for LE
        te1 = _make_te("TE1_RE", 85)
        te2 = _make_te("TE2_FL", 86)

        roster = _build_roster(wrs=[wr1, wr2], tes=[te1, te2])
        home = Team(abbreviation="HOM", city="Home", name="Tester",
                    conference="AFC", division="North", roster=roster)
        away_roster = _build_roster(
            rbs=[_make_rb("AwayRB1", 30), _make_rb("AwayRB2", 32)],
            qbs=[_make_qb("AwayQB", 12)],
            wrs=[_make_wr("AwayWR1", 83), _make_wr("AwayWR2", 84)],
            tes=[_make_te("AwayTE1", 90)],
        )
        away = Team(abbreviation="AWY", city="Away", name="Visitor",
                    conference="NFC", division="South", roster=away_roster)
        game = Game(home, away)
        game.state.possession = "home"
        game.apply_formation_package("home", "2TE_1WR")

        game.state.injuries[wr1.player_name] = 4
        game._immediate_injury_swap(wr1.player_name)

        overrides = game._on_field_offense["home"]
        # LE override redirected to WR2; TE slots unchanged
        assert overrides.get("LE") == wr2.player_name, "LE should now be WR2"
        assert overrides.get("RE") == te1.player_name, "RE unchanged"
        assert overrides.get("FL") == te2.player_name, "FL unchanged"

    # ── 3TE / JUMBO package ──────────────────────────────────────────

    def test_3te_te1_injury_keeps_te2_le_te3_fl_puts_te4_at_re(self):
        """3TE: TE1 (RE) injury brings TE4 (backup) to RE; TE2/TE3 stay at LE/FL.

        This is the core bug scenario — without the fix, TE2 would be moved
        into RE and double-assigned (both RE and LE overrides pointing to TE2).
        """
        te1 = _make_te("TE1_RE", 85)
        te2 = _make_te("TE2_LE", 86)
        te3 = _make_te("TE3_FL", 87)
        te4 = _make_te("TE4_bench", 88)   # true backup, must fill

        game = _build_game_multi_te([], [te1, te2, te3], extra_te_backup=te4)
        game.apply_formation_package("home", "3TE")

        overrides = game._on_field_offense["home"]
        assert overrides.get("RE") == te1.player_name
        assert overrides.get("LE") == te2.player_name
        assert overrides.get("FL") == te3.player_name

        game.state.injuries[te1.player_name] = 4
        game._immediate_injury_swap(te1.player_name)

        tes_roster = game.get_offense_team().roster.tes
        assert tes_roster[0].player_name == te4.player_name, \
            "TE4 (backup) should move to index 0"

        overrides = game._on_field_offense["home"]
        assert overrides.get("RE") == te4.player_name, \
            f"RE must point to TE4 (backup), got {overrides.get('RE')!r}"
        assert overrides.get("LE") == te2.player_name, "LE must remain TE2"
        assert overrides.get("FL") == te3.player_name, "FL must remain TE3"

        receivers = game._get_all_receivers()
        slots = {getattr(r, "_formation_slot", None): r.player_name for r in receivers}
        assert slots.get("RE") == te4.player_name
        assert slots.get("LE") == te2.player_name
        assert slots.get("FL") == te3.player_name
        # No player appears in two slots
        names = list(slots.values())
        assert len(names) == len(set(names)), \
            "Each player must appear in exactly one slot"

    def test_3te_te2_injury_keeps_te1_re_te3_fl_puts_te4_at_le(self):
        """3TE: TE2 (LE) injury brings TE4 (backup) to LE; TE1/TE3 stay."""
        te1 = _make_te("TE1_RE", 85)
        te2 = _make_te("TE2_LE", 86)
        te3 = _make_te("TE3_FL", 87)
        te4 = _make_te("TE4_bench", 88)

        game = _build_game_multi_te([], [te1, te2, te3], extra_te_backup=te4)
        game.apply_formation_package("home", "3TE")

        game.state.injuries[te2.player_name] = 4
        game._immediate_injury_swap(te2.player_name)

        overrides = game._on_field_offense["home"]
        assert overrides.get("RE") == te1.player_name, "RE must remain TE1"
        assert overrides.get("LE") == te4.player_name, \
            f"LE must be TE4 (backup), got {overrides.get('LE')!r}"
        assert overrides.get("FL") == te3.player_name, "FL must remain TE3"

        receivers = game._get_all_receivers()
        slots = {getattr(r, "_formation_slot", None): r.player_name for r in receivers}
        assert slots.get("RE") == te1.player_name
        assert slots.get("LE") == te4.player_name
        assert slots.get("FL") == te3.player_name
        names = list(slots.values())
        assert len(names) == len(set(names)), "No player double-assigned"

    def test_3te_te3_injury_keeps_te1_re_te2_le_puts_te4_at_fl(self):
        """3TE: TE3 (FL) injury brings TE4 (backup) to FL; TE1/TE2 stay."""
        te1 = _make_te("TE1_RE", 85)
        te2 = _make_te("TE2_LE", 86)
        te3 = _make_te("TE3_FL", 87)
        te4 = _make_te("TE4_bench", 88)

        game = _build_game_multi_te([], [te1, te2, te3], extra_te_backup=te4)
        game.apply_formation_package("home", "3TE")

        game.state.injuries[te3.player_name] = 4
        game._immediate_injury_swap(te3.player_name)

        overrides = game._on_field_offense["home"]
        assert overrides.get("RE") == te1.player_name, "RE must remain TE1"
        assert overrides.get("LE") == te2.player_name, "LE must remain TE2"
        assert overrides.get("FL") == te4.player_name, \
            f"FL must be TE4 (backup), got {overrides.get('FL')!r}"

        receivers = game._get_all_receivers()
        slots = {getattr(r, "_formation_slot", None): r.player_name for r in receivers}
        assert slots.get("FL") == te4.player_name
        names = list(slots.values())
        assert len(names) == len(set(names)), "No player double-assigned"

    def test_jumbo_te1_injury_is_equivalent_to_3te(self):
        """JUMBO package uses same slot logic as 3TE — same fix applies."""
        te1 = _make_te("TE1_RE", 85)
        te2 = _make_te("TE2_LE", 86)
        te3 = _make_te("TE3_FL", 87)
        te4 = _make_te("TE4_bench", 88)

        game = _build_game_multi_te([], [te1, te2, te3], extra_te_backup=te4)
        game.apply_formation_package("home", "JUMBO")

        game.state.injuries[te1.player_name] = 4
        game._immediate_injury_swap(te1.player_name)

        overrides = game._on_field_offense["home"]
        assert overrides.get("RE") == te4.player_name, \
            f"RE must be TE4 (backup) after JUMBO TE1 injury, got {overrides.get('RE')!r}"
        assert overrides.get("LE") == te2.player_name, "LE must remain TE2"
        assert overrides.get("FL") == te3.player_name, "FL must remain TE3"

        receivers = game._get_all_receivers()
        slots = {getattr(r, "_formation_slot", None): r.player_name for r in receivers}
        names = list(slots.values())
        assert len(names) == len(set(names)), "No player double-assigned in JUMBO"

    def test_3te_no_backup_falls_back_to_next_healthy_te(self):
        """3TE with only 3 TEs (no bench): emergency fallback when backup pool is empty.

        The fix skips all on-field TEs when searching for a replacement.  If
        there are no TEs beyond index 2, the existing fallback loop (which
        retries from injured_idx+1) picks the next healthy on-field TE as a
        last resort.  This means one TE will momentarily hold two override
        slots — which is unavoidable when the roster is exhausted.  The key
        guarantee is: (1) no crash, (2) the injured player is removed from
        the RE override so play logic doesn't try to call plays for them.
        """
        te1 = _make_te("TE1_RE", 85)
        te2 = _make_te("TE2_LE", 86)
        te3 = _make_te("TE3_FL", 87)  # no TE4; roster is exhausted

        game = _build_game_multi_te([], [te1, te2, te3])
        game.apply_formation_package("home", "3TE")

        game.state.injuries[te1.player_name] = 4
        # Should not raise; fallback picks te2 (next healthy TE)
        game._immediate_injury_swap(te1.player_name)

        # The injured player must be removed from the RE override
        overrides = game._on_field_offense["home"]
        assert overrides.get("RE") is not None, \
            "RE override must be set even when no true backup exists"
        assert overrides.get("RE") != te1.player_name, \
            "Injured TE1 must not remain in the RE override"
        # In the no-backup case the emergency fallback reuses an on-field TE,
        # so double-assignment is acceptable and intentional.
        assert overrides.get("RE") in (te2.player_name, te3.player_name), \
            "Emergency fill must be one of the remaining healthy on-field TEs"


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


# ═════════════════════════════════════════════════════════════════════════════
#  Part 3 — WR/TE Endurance on Pass Plays
# ═════════════════════════════════════════════════════════════════════════════

class TestPassEnduranceCheck:
    """Verify endurance check works for WR and TE as pass targets."""

    def test_wr_endurance_pass_violation(self):
        """WR with endurance_pass=1 targeted on consecutive play → violation."""
        game = _build_game()
        wr = _make_wr("SpeedWR", endurance=1)
        wr.endurance_pass = 1
        game.state.last_ball_carrier = "SpeedWR"
        assert game._check_endurance_violation(wr, for_pass=True) == "endurance_1"

    def test_wr_endurance_pass_ok(self):
        """WR with endurance_pass=1 rested one play → no violation."""
        game = _build_game()
        wr = _make_wr("SpeedWR", endurance=1)
        wr.endurance_pass = 1
        game.state.last_ball_carrier = "OtherPlayer"
        assert game._check_endurance_violation(wr, for_pass=True) is None

    def test_wr_endurance_0_unlimited(self):
        """WR with endurance_pass=0 can be targeted every play."""
        game = _build_game()
        wr = _make_wr("StarWR", endurance=0)
        wr.endurance_pass = 0
        game.state.last_ball_carrier = "StarWR"
        game.state.endurance_used_this_drive.add("StarWR")
        game.state.endurance_used_this_quarter.add("StarWR")
        assert game._check_endurance_violation(wr, for_pass=True) is None

    def test_te_endurance_3_drive_violation(self):
        """TE with endurance_pass=3 used already this drive → violation."""
        game = _build_game()
        te = _make_te("BlockTE", endurance=3)
        te.endurance_pass = 3
        game.state.endurance_used_this_drive.add("BlockTE")
        assert game._check_endurance_violation(te, for_pass=True) == "endurance_3"

    def test_te_endurance_3_new_drive_ok(self):
        """TE with endurance_pass=3 not yet used this drive → ok."""
        game = _build_game()
        te = _make_te("BlockTE", endurance=3)
        te.endurance_pass = 3
        assert game._check_endurance_violation(te, for_pass=True) is None

    def test_rushing_endurance_used_for_runs(self):
        """Run play should use endurance_rushing (not endurance_pass)."""
        game = _build_game()
        rb = _make_rb("DualRB", endurance=0)
        rb.endurance_pass = 2  # More restrictive for passes
        # RB used last play
        game.state.last_ball_carrier = "DualRB"
        # For runs: endurance_rushing=0 → unlimited
        assert game._check_endurance_violation(rb, for_pass=False) is None
        # For passes: endurance_pass=2 → violation (used 1 play ago)
        assert game._check_endurance_violation(rb, for_pass=True) == "endurance_2"


# ═════════════════════════════════════════════════════════════════════════════
#  Part 4 — Safety Scoring
# ═════════════════════════════════════════════════════════════════════════════

class TestSafety:
    """Verify safety scoring when ball carrier is in own end zone."""

    def test_safety_awards_2_points_to_defense(self):
        game = _build_game()
        game.state.possession = "home"
        game.state.yard_line = 2
        game.state.down = 1
        game.state.distance = 10

        # Advance -5 yards (loss), pushing below goal line
        game._advance_down(-5)

        # Defense (away team) should get 2 points
        assert game.state.score.away == 2
        assert game.state.score.home == 0

    def test_safety_changes_possession(self):
        """After safety, possession must switch: the scoring team receives."""
        game = _build_game()
        game.state.possession = "home"  # home gets tackled in own endzone
        game.state.yard_line = 2

        game._advance_down(-5)

        # Scoring team (away) now has the ball
        assert game.state.possession == "away"

    def test_safety_logged(self):
        game = _build_game()
        game.state.possession = "away"
        game.state.yard_line = 1

        game._advance_down(-3)

        # Home team (defense) gets 2 points
        assert game.state.score.home == 2
        assert any("SAFETY" in entry for entry in game.state.play_log)

    def test_no_safety_at_1(self):
        """Ball at 1, loss of 0 = no safety."""
        game = _build_game()
        game.state.possession = "home"
        game.state.yard_line = 1
        game.state.distance = 10
        game.state.down = 1

        result = game._advance_down(0)
        # No safety, normal play
        assert game.state.score.away == 0
        assert game.state.yard_line == 1


class TestSafetyKickoffYardLine:
    """Verify the yard-line helper for safety free kicks."""

    def test_plain_touchback_at_15(self):
        """Safety kickoff plain touchback (no modifier) → 15."""
        from engine.play_resolver import PlayResult
        game = _build_game()
        tb = PlayResult("KICKOFF", 0, "TOUCHBACK", description="Touchback")
        assert game._safety_kickoff_yard_line(tb) == 15

    def test_touchback_with_modifier(self):
        """Safety kickoff TB already at 17 (20-3 modifier) → 17-5=12."""
        from engine.play_resolver import PlayResult
        game = _build_game()
        tb = PlayResult("KICKOFF", 17, "TOUCHBACK",
                        description="Kickoff — touchback, ball at the 17-yard line")
        assert game._safety_kickoff_yard_line(tb) == 12

    def test_oob_safety_kickoff(self):
        """OOB safety kickoff → 40-15 = 25."""
        from engine.play_resolver import PlayResult
        game = _build_game()
        oob = PlayResult("KICKOFF", 0, "OOB", description="Kickoff OOB")
        assert game._safety_kickoff_yard_line(oob) == 25

    def test_return_uses_yards_gained(self):
        """Returned kick uses yards_gained as-is (field position from return)."""
        from engine.play_resolver import PlayResult
        game = _build_game()
        ret = PlayResult("KICKOFF", 33, "RETURN", description="Return to 33")
        assert game._safety_kickoff_yard_line(ret) == 33


# ═════════════════════════════════════════════════════════════════════════════
#  Part 5 — Touchback Yard Line Fix
# ═════════════════════════════════════════════════════════════════════════════

class TestTouchbackYardLine:
    """Verify touchbacks use 20-yard line per 5E rules."""

    def test_kickoff_touchback_at_20(self):
        game = _build_game()
        from engine.play_resolver import PlayResult
        touchback = PlayResult("KICKOFF", 0, "TOUCHBACK",
                               description="Touchback")
        yl = game._kickoff_yard_line(touchback)
        assert yl == 20
