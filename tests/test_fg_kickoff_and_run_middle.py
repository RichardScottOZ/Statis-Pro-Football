"""Tests for:
1. Kickoff after successful field goal (bug fix)
2. No 'MIDDLE' direction for RUN plays in solitaire (invalid play removal)
"""

import random
from unittest.mock import patch, MagicMock

import pytest
from engine.team import Team
from engine.game import Game
from engine.play_resolver import PlayResult
from engine.solitaire import PlayCall, SolitaireAI, GameSituation, _solo_code_to_play


class TestKickoffAfterFieldGoal:
    """After a successful FG the scoring team must kick off to the opponent."""

    def setup_method(self):
        self.home = Team.load("KC")
        self.away = Team.load("BUF")
        self.game = Game(self.home, self.away, use_5e=True, seed=42)

    def test_fg_good_triggers_kickoff(self):
        """A made FG should trigger a kickoff, evidenced by a kickoff log entry."""
        # Set up: place ball in FG range
        self.game.state.yard_line = 70  # ~47-yard attempt
        self.game.state.down = 4
        self.game.state.distance = 8
        initial_possession = self.game.state.possession

        fg_result = PlayResult("FG", 0, "FG_GOOD",
                               description="Makes 47-yard field goal")

        with patch.object(self.game, '_execute_field_goal', return_value=fg_result):
            kickoff_result = PlayResult("KICKOFF", 25, "KICKOFF_RETURN",
                                        description="Kickoff returned to the 25")
            with patch.object(self.game, '_do_kickoff', return_value=kickoff_result) as mock_ko:
                play_call = PlayCall("FG", "SHOTGUN", "MIDDLE", "FG attempt")
                result = self.game.execute_play(play_call=play_call)

                # Kickoff must be called after a made FG
                mock_ko.assert_called_once()
                # Possession should have changed
                assert self.game.state.possession != initial_possession

    def test_fg_no_good_does_not_trigger_kickoff(self):
        """A missed FG should NOT trigger a kickoff — just change possession."""
        self.game.state.yard_line = 60
        self.game.state.down = 4
        self.game.state.distance = 12
        initial_possession = self.game.state.possession

        fg_result = PlayResult("FG", 0, "FG_NO_GOOD",
                               description="Misses 57-yard field goal")

        with patch.object(self.game, '_execute_field_goal', return_value=fg_result):
            with patch.object(self.game, '_do_kickoff') as mock_ko:
                play_call = PlayCall("FG", "SHOTGUN", "MIDDLE", "FG attempt")
                result = self.game.execute_play(play_call=play_call)

                # No kickoff on a miss
                mock_ko.assert_not_called()
                # Possession should still change
                assert self.game.state.possession != initial_possession

    def test_fg_good_adds_3_points(self):
        """Scoring after a FG should add 3 points to the kicking team."""
        self.game.state.yard_line = 75
        self.game.state.down = 4
        self.game.state.distance = 5
        possession = self.game.state.possession
        score_before = (self.game.state.score.home if possession == "home"
                        else self.game.state.score.away)

        fg_result = PlayResult("FG", 0, "FG_GOOD",
                               description="Makes 42-yard field goal")

        with patch.object(self.game, '_execute_field_goal', return_value=fg_result):
            with patch.object(self.game, '_do_kickoff',
                              return_value=PlayResult("KICKOFF", 25, "KICKOFF_RETURN",
                                                      description="Kickoff")):
                play_call = PlayCall("FG", "SHOTGUN", "MIDDLE", "FG attempt")
                self.game.execute_play(play_call=play_call)

        score_after = (self.game.state.score.home if possession == "home"
                       else self.game.state.score.away)
        assert score_after == score_before + 3

    def test_fg_good_logs_score_and_kickoff(self):
        """Play log should contain both the score and the kickoff description."""
        self.game.state.yard_line = 75
        self.game.state.down = 4
        self.game.state.distance = 5

        fg_result = PlayResult("FG", 0, "FG_GOOD",
                               description="Makes 42-yard field goal")
        ko_result = PlayResult("KICKOFF", 25, "KICKOFF_RETURN",
                               description="Kickoff returned to the 25")

        with patch.object(self.game, '_execute_field_goal', return_value=fg_result):
            with patch.object(self.game, '_do_kickoff', return_value=ko_result):
                play_call = PlayCall("FG", "SHOTGUN", "MIDDLE", "FG attempt")
                self.game.execute_play(play_call=play_call)

        log_text = "\n".join(self.game.state.play_log)
        assert "Score:" in log_text
        assert "Kickoff" in log_text


class TestNoRunMiddleDirection:
    """'MIDDLE' is not a valid 5E run direction. Runs must use IL/IR/SL/SR."""

    VALID_RUN_DIRECTIONS = {"IL", "IR", "SL", "SR"}

    def test_solo_code_unknown_uses_valid_direction(self):
        """Fallback for unknown solo codes should use IL or IR, not MIDDLE."""
        for _ in range(50):
            pc = _solo_code_to_play("UNKNOWN_CODE_XYZ")
            assert pc.play_type == "RUN"
            assert pc.direction in self.VALID_RUN_DIRECTIONS, (
                f"Expected valid run direction, got '{pc.direction}'"
            )

    def test_fourth_down_short_yardage_run_uses_valid_direction(self):
        """4th-and-short run in opponent territory should use valid direction."""
        ai = SolitaireAI()
        situation = GameSituation(
            down=4, distance=1, yard_line=65,
            score_diff=0, quarter=2, time_remaining=600,
        )
        for _ in range(50):
            pc = ai._call_fourth_down(situation)
            if pc.play_type == "RUN":
                assert pc.direction in self.VALID_RUN_DIRECTIONS, (
                    f"Expected valid run direction, got '{pc.direction}'"
                )

    def test_default_run_play_uses_valid_direction(self):
        """Default fallback run play should use valid 5E direction."""
        ai = SolitaireAI()
        # Situation where no SOLO card data is available — triggers fallback
        situation = GameSituation(
            down=1, distance=10, yard_line=30,
            score_diff=0, quarter=1, time_remaining=900,
        )
        for _ in range(100):
            pc = ai.call_play_5e(situation, fac_card=None)
            if pc.play_type == "RUN":
                assert pc.direction in self.VALID_RUN_DIRECTIONS, (
                    f"Expected valid run direction, got '{pc.direction}'"
                )
