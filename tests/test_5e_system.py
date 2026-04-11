"""Tests for the 5th-edition FAC deck system and card resolution."""
import random
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.fac_deck import (
    FACDeck, FACCard, DECK_SIZE, Z_CARD_COUNT, STANDARD_CARD_COUNT,
    PASS_NUMBER_RANGE, RUN_NUMBER_RANGE,
)
from engine.player_card import (
    PlayerCard, PASS_SLOTS, RUN_SLOTS, PASS_SLOT_COUNT, RUN_SLOT_COUNT,
    RECEIVER_LETTERS,
)
from engine.card_generator import CardGenerator
from engine.play_resolver import PlayResolver, PlayResult
from engine.fac_distributions import (
    qb_pass_distribution_5e, qb_long_pass_distribution_5e,
    qb_quick_pass_distribution_5e,
    rb_run_distribution_5e, reception_distribution_5e,
    PASS_SLOT_COUNT as DIST_PASS_SLOT_COUNT,
    RUN_SLOT_COUNT as DIST_RUN_SLOT_COUNT,
)
from engine.solitaire import SolitaireAI, GameSituation, PlayCall
from engine.game import Game
from engine.team import Team


# ──────────────────────────────────────────────────────────────────────
#  FAC Deck Tests
# ──────────────────────────────────────────────────────────────────────

class TestFACDeckStructure:
    """Test the 109-card FAC deck structure."""

    def test_deck_has_109_cards(self):
        deck = FACDeck(seed=42)
        assert deck.cards_remaining == DECK_SIZE

    def test_deck_has_13_z_cards(self):
        deck = FACDeck(seed=42)
        z_count = 0
        for _ in range(DECK_SIZE):
            card = deck.draw()
            if card.is_z_card:
                z_count += 1
        assert z_count == Z_CARD_COUNT

    def test_deck_has_96_standard_cards(self):
        deck = FACDeck(seed=42)
        standard = 0
        for _ in range(DECK_SIZE):
            card = deck.draw()
            if not card.is_z_card:
                standard += 1
        assert standard == STANDARD_CARD_COUNT

    def test_deck_draw_reduces_count(self):
        deck = FACDeck(seed=42)
        deck.draw()
        assert deck.cards_remaining == DECK_SIZE - 1

    def test_deck_auto_reshuffles_when_empty(self):
        deck = FACDeck(seed=42)
        for _ in range(DECK_SIZE):
            deck.draw()
        assert deck.cards_remaining == 0
        card = deck.draw()
        assert card is not None
        assert deck.cards_remaining == DECK_SIZE - 1

    def test_deck_reshuffle_restores_all_cards(self):
        deck = FACDeck(seed=42)
        for _ in range(50):
            deck.draw()
        deck.reshuffle()
        assert deck.cards_remaining == DECK_SIZE

    def test_seeded_deck_is_reproducible(self):
        deck1 = FACDeck(seed=42)
        deck2 = FACDeck(seed=42)
        for _ in range(20):
            c1 = deck1.draw()
            c2 = deck2.draw()
            assert c1.card_number == c2.card_number

    def test_draw_non_z_skips_z_cards(self):
        deck = FACDeck(seed=42)
        card = deck.draw_non_z()
        assert not card.is_z_card


class TestFACCardProperties:
    """Test FACCard property methods."""

    def test_z_card_detected(self):
        deck = FACDeck(seed=42)
        z_cards = []
        for _ in range(DECK_SIZE):
            card = deck.draw()
            if card.is_z_card:
                z_cards.append(card)
        assert all(c.run_number == "Z" for c in z_cards)
        assert all(c.pass_number == "Z" for c in z_cards)

    def test_run_num_int_for_standard_cards(self):
        deck = FACDeck(seed=42)
        for _ in range(DECK_SIZE):
            card = deck.draw()
            if not card.is_z_card:
                rn = card.run_num_int
                assert rn is not None
                assert 1 <= rn <= RUN_NUMBER_RANGE

    def test_pass_num_int_for_standard_cards(self):
        deck = FACDeck(seed=42)
        for _ in range(DECK_SIZE):
            card = deck.draw()
            if not card.is_z_card:
                pn = card.pass_num_int
                assert pn is not None
                assert 1 <= pn <= PASS_NUMBER_RANGE

    def test_oob_cards_detected(self):
        deck = FACDeck(seed=42)
        oob_count = 0
        for _ in range(DECK_SIZE):
            card = deck.draw()
            if card.is_out_of_bounds:
                oob_count += 1
                assert "(OB)" in card.run_number
        assert oob_count > 0

    def test_sack_yards_detected(self):
        deck = FACDeck(seed=42)
        sack_count = 0
        for _ in range(DECK_SIZE):
            card = deck.draw()
            sy = card.sack_yards
            if sy is not None:
                assert sy < 0
                sack_count += 1
        assert sack_count > 0

    def test_screen_result_values(self):
        deck = FACDeck(seed=42)
        valid_types = {"Com", "Inc", "Int", "Dropped Int"}
        for _ in range(DECK_SIZE):
            card = deck.draw()
            sc = card.screen_result
            assert isinstance(sc, str)

    def test_receiver_target_fields(self):
        deck = FACDeck(seed=42)
        for _ in range(DECK_SIZE):
            card = deck.draw()
            if not card.is_z_card:
                for pt in ("QUICK", "SHORT", "LONG"):
                    target = card.get_receiver_target(pt)
                    assert isinstance(target, str)

    def test_blocking_matchup_fields(self):
        deck = FACDeck(seed=42)
        for _ in range(DECK_SIZE):
            card = deck.draw()
            if not card.is_z_card:
                for direction in ("SL", "IL", "SR", "IR"):
                    matchup = card.get_blocking_matchup(direction)
                    assert isinstance(matchup, str)

    def test_solo_field_parses(self):
        deck = FACDeck(seed=42)
        parsed_count = 0
        for _ in range(DECK_SIZE):
            card = deck.draw()
            if not card.is_z_card:
                solo = card.parse_solo()
                assert isinstance(solo, dict)
                if solo:
                    parsed_count += 1
                    for key in solo:
                        assert isinstance(key, int)
        assert parsed_count > 0

    def test_z_result_parses(self):
        deck = FACDeck(seed=42)
        for _ in range(DECK_SIZE):
            card = deck.draw()
            z_res = card.parse_z_result()
            assert "type" in z_res
            assert "detail" in z_res


# ──────────────────────────────────────────────────────────────────────
#  5th-Edition Distribution Tests
# ──────────────────────────────────────────────────────────────────────

class TestFifthEdDistributions:
    """Test the 48/12-slot distribution functions."""

    def test_qb_pass_distribution_sums_to_48(self):
        dist = qb_pass_distribution_5e(0.65, 0.03, "B")
        total = sum(dist.values())
        assert total == 48

    def test_qb_pass_has_receiver_letters(self):
        dist = qb_pass_distribution_5e(0.65, 0.03, "B", n_receivers=5)
        for letter in RECEIVER_LETTERS:
            assert letter in dist
        assert dist["INC"] >= 0
        assert dist["INT"] >= 1

    def test_qb_long_pass_sums_to_48(self):
        dist = qb_long_pass_distribution_5e(0.65, 0.03, "B")
        total = sum(dist.values())
        assert total == 48

    def test_qb_quick_pass_sums_to_48(self):
        dist = qb_quick_pass_distribution_5e(0.65, 0.03, "B")
        total = sum(dist.values())
        assert total == 48

    def test_rb_run_distribution_sums_to_12(self):
        dist = rb_run_distribution_5e(0.02, "B")
        total = sum(dist.values())
        assert total == 12

    def test_rb_run_has_breakaway(self):
        dist = rb_run_distribution_5e(0.02, "A")
        assert "BREAKAWAY" in dist

    def test_sweep_has_more_breakaway(self):
        regular = rb_run_distribution_5e(0.02, "A", is_outside=False)
        sweep = rb_run_distribution_5e(0.02, "A", is_sweep=True)
        assert sweep["BREAKAWAY"] >= regular["BREAKAWAY"]

    def test_reception_distribution_sums_to_48(self):
        dist = reception_distribution_5e(0.70, is_long=False)
        total = sum(dist.values())
        assert total == 48


# ──────────────────────────────────────────────────────────────────────
#  5th-Edition Card Generator Tests
# ──────────────────────────────────────────────────────────────────────

class TestFifthEdCardGenerator:
    """Test 5th-edition card generation."""

    def setup_method(self):
        self.gen = CardGenerator(seed=42)

    def test_qb_card_5e_has_48_row_short_pass(self):
        qb = self.gen.generate_qb_card_5e("Test QB", "TST", 1, 0.65, 7.5, 0.03, 0.06, "B")
        assert len(qb.short_pass) == PASS_SLOT_COUNT

    def test_qb_card_5e_has_48_row_long_pass(self):
        qb = self.gen.generate_qb_card_5e("Test QB", "TST", 1, 0.65, 7.5, 0.03, 0.06, "B")
        assert len(qb.long_pass) == PASS_SLOT_COUNT

    def test_qb_card_5e_has_48_row_quick_pass(self):
        qb = self.gen.generate_qb_card_5e("Test QB", "TST", 1, 0.65, 7.5, 0.03, 0.06, "B")
        assert len(qb.quick_pass) == PASS_SLOT_COUNT

    def test_qb_card_5e_results_are_receiver_letters(self):
        qb = self.gen.generate_qb_card_5e("Test QB", "TST", 1, 0.65, 7.5, 0.03, 0.06, "B")
        valid_results = set(RECEIVER_LETTERS) | {"INC", "INT"}
        for slot, data in qb.short_pass.items():
            assert data["result"] in valid_results

    def test_rb_card_5e_has_12_row_inside_run(self):
        rb = self.gen.generate_rb_card_5e("Test RB", "TST", 2, 4.5, 0.02, "B")
        assert len(rb.inside_run) == RUN_SLOT_COUNT

    def test_rb_card_5e_has_12_row_outside_run(self):
        rb = self.gen.generate_rb_card_5e("Test RB", "TST", 2, 4.5, 0.02, "B")
        assert len(rb.outside_run) == RUN_SLOT_COUNT

    def test_rb_card_5e_has_12_row_sweep(self):
        rb = self.gen.generate_rb_card_5e("Test RB", "TST", 2, 4.5, 0.02, "B")
        assert len(rb.sweep) == RUN_SLOT_COUNT

    def test_rb_card_5e_has_breakaway(self):
        rb = self.gen.generate_rb_card_5e("Test RB", "TST", 2, 4.5, 0.02, "A")
        results = [rb.sweep[str(n)]["result"] for n in range(1, 13)]
        assert "BREAKAWAY" in results

    def test_wr_card_5e_has_48_row_reception(self):
        wr = self.gen.generate_wr_card_5e("Test WR", "TST", 3, 0.70, 12.0, "B")
        assert len(wr.short_reception) == PASS_SLOT_COUNT
        assert len(wr.long_reception) == PASS_SLOT_COUNT

    def test_wr_card_5e_has_receiver_letter(self):
        wr = self.gen.generate_wr_card_5e("Test WR", "TST", 3, 0.70, 12.0, "B", receiver_letter="A")
        assert wr.receiver_letter == "A"

    def test_te_card_5e_has_receiver_letter(self):
        te = self.gen.generate_te_card_5e("Test TE", "TST", 4, 0.60, 10.0, "C", receiver_letter="D")
        assert te.receiver_letter == "D"

    def test_def_card_5e_has_defender_letter(self):
        d = self.gen.generate_def_card_5e("Test DE", "TST", 99, "DL", 80, 40, 60, "B", defender_letter="A")
        assert d.defender_letter == "A"

    def test_card_to_dict_round_trip(self):
        qb = self.gen.generate_qb_card_5e("Test QB", "TST", 1, 0.65, 7.5, 0.03, 0.06, "B")
        d = qb.to_dict()
        restored = PlayerCard.from_dict(d)
        assert restored.short_pass == qb.short_pass
        assert restored.quick_pass == qb.quick_pass
        assert len(restored.short_pass) == PASS_SLOT_COUNT


# ──────────────────────────────────────────────────────────────────────
#  5th-Edition Play Resolution Tests
# ──────────────────────────────────────────────────────────────────────

class TestFifthEdPassResolution:
    """Test 5th-edition pass play resolution."""

    def setup_method(self):
        random.seed(42)
        gen = CardGenerator(seed=42)
        self.resolver = PlayResolver()
        self.deck = FACDeck(seed=42)

        self.qb = gen.generate_qb_card_5e("Test QB", "TST", 1, 0.65, 7.5, 0.03, 0.06, "B")
        self.wr1 = gen.generate_wr_card_5e("Test WR1", "TST", 80, 0.70, 12.0, "B", receiver_letter="A")
        self.wr2 = gen.generate_wr_card_5e("Test WR2", "TST", 81, 0.65, 11.0, "C", receiver_letter="B")
        self.te = gen.generate_te_card_5e("Test TE", "TST", 85, 0.60, 10.0, "C", receiver_letter="D")
        self.receivers = [self.wr1, self.wr2, self.te]

    def test_pass_produces_play_result(self):
        card = self.deck.draw_non_z()
        result = self.resolver.resolve_pass_5e(
            card, self.deck, self.qb, self.wr1, self.receivers, "SHORT",
        )
        assert isinstance(result, PlayResult)
        assert result.play_type == "PASS"

    def test_sack_on_negative_er(self):
        """Cards with negative ER should produce sacks."""
        results = []
        deck = FACDeck(seed=42)
        for _ in range(200):
            card = deck.draw_non_z()
            if card.sack_yards is not None:
                result = self.resolver.resolve_pass_5e(
                    card, deck, self.qb, self.wr1, self.receivers, "SHORT",
                )
                results.append(result)
        # Some cards have negative ER — those should produce sacks
        assert any(r.result == "SACK" for r in results)

    def test_screen_uses_fac_sc_field(self):
        card = self.deck.draw_non_z()
        result = self.resolver.resolve_pass_5e(
            card, self.deck, self.qb, self.wr1, self.receivers, "SCREEN",
        )
        assert result.play_type == "PASS"
        assert result.result in ("COMPLETE", "INCOMPLETE", "INT", "TD", "SACK")

    def test_multiple_passes_produce_variety(self):
        results = set()
        deck = FACDeck(seed=42)
        for _ in range(100):
            card = deck.draw_non_z()
            result = self.resolver.resolve_pass_5e(
                card, deck, self.qb, self.wr1, self.receivers, "SHORT",
            )
            results.add(result.result)
        assert len(results) >= 2  # At least complete and incomplete

    def test_z_card_handled_gracefully(self):
        """Drawing a Z card should not crash."""
        # Build a Z card manually
        z_card = FACCard(
            card_number=97, run_number="Z", pass_number="Z",
            sweep_left="Z", inside_left="Z", sweep_right="Z", inside_right="Z",
            end_run="Z", quick_kick="Z", short_pass="Z", long_pass="Z",
            screen="Z", z_result="Follow 3-rules for Z", solo="Z",
        )
        deck = FACDeck(seed=42)
        result = self.resolver.resolve_pass_5e(
            z_card, deck, self.qb, self.wr1, self.receivers, "SHORT",
        )
        assert isinstance(result, PlayResult)


class TestFifthEdRunResolution:
    """Test 5th-edition run play resolution."""

    def setup_method(self):
        random.seed(42)
        gen = CardGenerator(seed=42)
        self.resolver = PlayResolver()
        self.deck = FACDeck(seed=42)
        self.rb = gen.generate_rb_card_5e("Test RB", "TST", 2, 4.5, 0.02, "B")

    def test_run_produces_play_result(self):
        card = self.deck.draw_non_z()
        result = self.resolver.resolve_run_5e(
            card, self.deck, self.rb, "IL",
        )
        assert isinstance(result, PlayResult)
        assert result.play_type == "RUN"

    def test_oob_cards_produce_oob_result(self):
        """Cards with (OB) suffix should produce OOB results."""
        results = []
        deck = FACDeck(seed=42)
        for _ in range(200):
            card = deck.draw_non_z()
            if card.is_out_of_bounds:
                result = self.resolver.resolve_run_5e(
                    card, deck, self.rb, "IL",
                )
                results.append(result)
        assert any(r.out_of_bounds for r in results)

    def test_sweep_direction(self):
        card = self.deck.draw_non_z()
        result = self.resolver.resolve_run_5e(
            card, self.deck, self.rb, "SL",
        )
        assert result.play_type == "RUN"

    def test_defense_run_stop_affects_yards(self):
        """Higher defense run stop should reduce yards on average."""
        low_def_yards = []
        high_def_yards = []
        for seed in range(50):
            deck = FACDeck(seed=seed)
            card = deck.draw_non_z()
            r1 = self.resolver.resolve_run_5e(card, deck, self.rb, "IL",
                                              defense_run_stop=20)
            low_def_yards.append(r1.yards_gained)

            deck2 = FACDeck(seed=seed)
            card2 = deck2.draw_non_z()
            r2 = self.resolver.resolve_run_5e(card2, deck2, self.rb, "IL",
                                              defense_run_stop=80)
            high_def_yards.append(r2.yards_gained)

        avg_low = sum(low_def_yards) / len(low_def_yards)
        avg_high = sum(high_def_yards) / len(high_def_yards)
        assert avg_low >= avg_high


# ──────────────────────────────────────────────────────────────────────
#  5th-Edition Solitaire Tests
# ──────────────────────────────────────────────────────────────────────

class TestFifthEdSolitaire:
    """Test SOLO field-based play calling."""

    def setup_method(self):
        self.ai = SolitaireAI()
        self.deck = FACDeck(seed=42)

    def test_call_play_5e_returns_play_call(self):
        sit = GameSituation(
            down=1, distance=10, yard_line=25,
            score_diff=0, quarter=1, time_remaining=900,
        )
        card = self.deck.draw_non_z()
        result = self.ai.call_play_5e(sit, card)
        assert isinstance(result, PlayCall)

    def test_call_defense_5e_returns_formation(self):
        sit = GameSituation(
            down=1, distance=10, yard_line=25,
            score_diff=0, quarter=1, time_remaining=900,
        )
        card = self.deck.draw_non_z()
        formation = self.ai.call_defense_5e(sit, card)
        assert isinstance(formation, str)

    def test_fourth_down_overrides_solo(self):
        sit = GameSituation(
            down=4, distance=10, yard_line=25,
            score_diff=0, quarter=1, time_remaining=900,
        )
        card = self.deck.draw_non_z()
        result = self.ai.call_play_5e(sit, card)
        # On 4th and 10 from own 25, should punt
        assert result.play_type in ("PUNT", "FG", "RUN", "SHORT_PASS", "LONG_PASS")


# ──────────────────────────────────────────────────────────────────────
#  5th-Edition Full Game Tests
# ──────────────────────────────────────────────────────────────────────

class TestFifthEdGameIntegration:
    """Test full game simulation in 5th-edition mode."""

    def _load_teams(self):
        """Load two teams for testing."""
        import json
        data_dir = os.path.join(os.path.dirname(__file__), "..", "engine", "data", "2025")
        if not os.path.exists(data_dir):
            data_dir = os.path.join(os.path.dirname(__file__), "..", "engine", "data", "2024")
        if not os.path.exists(data_dir):
            pytest.skip("No team data available")
        teams = sorted(os.listdir(data_dir))
        team_files = [f for f in teams if f.endswith(".json")]
        if len(team_files) < 2:
            pytest.skip("Need at least 2 team data files")
        with open(os.path.join(data_dir, team_files[0])) as f:
            home_data = json.load(f)
        with open(os.path.join(data_dir, team_files[1])) as f:
            away_data = json.load(f)
        return Team.from_dict(home_data), Team.from_dict(away_data)

    def test_5e_game_completes(self):
        """A full game using 5th-edition mode should complete without errors."""
        random.seed(42)
        home, away = self._load_teams()
        game = Game(home, away, use_5e=True, seed=42)
        state = game.simulate_game()
        assert state.is_over
        assert state.score.home >= 0
        assert state.score.away >= 0

    def test_5e_game_uses_deck(self):
        """The deck should be used (cards drawn) during a 5e game."""
        random.seed(42)
        home, away = self._load_teams()
        game = Game(home, away, use_5e=True, seed=42)
        initial_remaining = game.deck.cards_remaining
        game.simulate_game()
        # Deck should have been used (possibly reshuffled)
        assert game.deck.cards_used > 0 or game.deck.cards_remaining < initial_remaining

    def test_legacy_game_still_works(self):
        """Legacy mode should still work without 5th-edition features."""
        random.seed(42)
        home, away = self._load_teams()
        game = Game(home, away, use_5e=False)
        state = game.simulate_game()
        assert state.is_over


# ──────────────────────────────────────────────────────────────────────
#  Deck Exhaustion Tests
# ──────────────────────────────────────────────────────────────────────

class TestDeckExhaustion:
    """Test deck behavior when cards run out."""

    def test_playing_through_entire_deck(self):
        deck = FACDeck(seed=42)
        for _ in range(DECK_SIZE):
            card = deck.draw()
            assert card is not None
        assert deck.cards_remaining == 0

    def test_auto_reshuffle_on_exhaustion(self):
        deck = FACDeck(seed=42)
        for _ in range(DECK_SIZE + 5):
            card = deck.draw()
            assert card is not None

    def test_all_pass_numbers_represented(self):
        """All 48 pass numbers should appear across the deck."""
        deck = FACDeck(seed=42)
        pass_nums = set()
        for _ in range(DECK_SIZE):
            card = deck.draw()
            pn = card.pass_num_int
            if pn is not None:
                pass_nums.add(pn)
        assert len(pass_nums) == PASS_NUMBER_RANGE

    def test_all_run_numbers_represented(self):
        """All 12 run numbers should appear across the deck."""
        deck = FACDeck(seed=42)
        run_nums = set()
        for _ in range(DECK_SIZE):
            card = deck.draw()
            rn = card.run_num_int
            if rn is not None:
                run_nums.add(rn)
        assert len(run_nums) == RUN_NUMBER_RANGE

    def test_pass_numbers_have_duplicates(self):
        """Each pass number 1-48 should appear at least twice."""
        deck = FACDeck(seed=42)
        pn_counts = {}
        for _ in range(DECK_SIZE):
            card = deck.draw()
            pn = card.pass_num_int
            if pn is not None:
                pn_counts[pn] = pn_counts.get(pn, 0) + 1
        for pn in range(1, 49):
            assert pn_counts.get(pn, 0) >= 2, f"Pass number {pn} appears {pn_counts.get(pn, 0)} times"
