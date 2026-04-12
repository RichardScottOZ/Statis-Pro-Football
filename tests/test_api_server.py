"""API coverage for play metadata exposed to the GUI."""

import os
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.api_server import app, _active_games


client = TestClient(app)


def setup_function():
    _active_games.clear()


def _new_game() -> str:
    response = client.post(
        "/games/new",
        json={
            "home_team": "CHI",
            "away_team": "GB",
            "season": "2025_5e",
            "solitaire_home": False,
            "solitaire_away": False,
        },
    )
    assert response.status_code == 200
    return response.json()["game_id"]


def test_run_play_response_includes_resolution_numbers():
    game_id = _new_game()

    response = client.post(
        f"/games/{game_id}/human-play",
        json={
            "play_type": "RUN",
            "direction": "MIDDLE",
            "formation": "UNDER_CENTER",
        },
    )

    assert response.status_code == 200
    play_result = response.json()["play_result"]
    assert 1 <= play_result["run_number"] <= 12
    assert play_result["pass_number"] is None
    assert play_result["defense_formation"] in {
        "4_3", "3_4", "4_3_BLITZ", "3_4_ZONE", "4_3_COVER2",
        "NICKEL_BLITZ", "NICKEL_ZONE", "NICKEL_COVER2", "GOAL_LINE",
    }


def test_pass_play_response_includes_pass_number_and_optional_run_number():
    game_id = _new_game()

    response = client.post(
        f"/games/{game_id}/human-play",
        json={
            "play_type": "SHORT_PASS",
            "direction": "MIDDLE",
            "formation": "UNDER_CENTER",
        },
    )

    assert response.status_code == 200
    play_result = response.json()["play_result"]
    assert 1 <= play_result["pass_number"] <= 48
    if play_result["run_number"] is not None:
        assert 1 <= play_result["run_number"] <= 12
    assert play_result["defense_formation"] in {
        "4_3", "3_4", "4_3_BLITZ", "3_4_ZONE", "4_3_COVER2",
        "NICKEL_BLITZ", "NICKEL_ZONE", "NICKEL_COVER2", "GOAL_LINE",
    }


def test_human_defense_response_keeps_called_formation():
    game_id = _new_game()

    response = client.post(
        f"/games/{game_id}/human-defense",
        json={"formation": "NICKEL_BLITZ"},
    )

    assert response.status_code == 200
    play_result = response.json()["play_result"]
    assert play_result["defense_formation"] == "NICKEL_BLITZ"
