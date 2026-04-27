"""Generate complete 2025 NFL player data for all 32 teams.
Each team has 45+ players: 3 QB, 6 RB, 5 WR, 3 TE, 8 OL, 6 DL, 8 LB, 7 DB, 1 K, 1 P
"""
# This file is auto-generated - see generate_2026_data_avalon_hill.py

TEAM_PLAYERS_FULL = {
    "BUF": {
        "qb": [
            {"name": "Josh Allen", "number": 17, "comp_pct": 0.639, "ypa": 7.5, "int_rate": 0.018, "sack_rate": 0.058, "rush_ypc": 4.5},
            {"name": "Mitchell Trubisky", "number": 10, "comp_pct": 0.58, "ypa": 6.2, "int_rate": 0.030, "sack_rate": 0.080, "rush_ypc": 3.5},
            {"name": "Mike White", "number": 14, "comp_pct": 0.55, "ypa": 5.8, "int_rate": 0.035, "sack_rate": 0.090, "rush_ypc": 2.5},
        ],
        "rb": [
            {"name": "James Cook", "number": 4, "ypc": 4.8, "fumble_rate": 0.009, "catch_rate": 0.70, "avg_rec_yards": 8.5},
            {"name": "Ray Davis", "number": 22, "ypc": 4.0, "fumble_rate": 0.013, "catch_rate": 0.55, "avg_rec_yards": 6.5},
            {"name": "Ty Johnson", "number": 25, "ypc": 3.8, "fumble_rate": 0.015, "catch_rate": 0.50, "avg_rec_yards": 6.0},
            {"name": "Reginald Brown", "number": 35, "ypc": 3.5, "fumble_rate": 0.018, "catch_rate": 0.45, "avg_rec_yards": 5.5},
            {"name": "Frank Gore Jr.", "number": 38, "ypc": 3.2, "fumble_rate": 0.020, "catch_rate": 0.40, "avg_rec_yards": 5.0},
            {"name": "Zack Moss", "number": 20, "ypc": 3.6, "fumble_rate": 0.016, "catch_rate": 0.48, "avg_rec_yards": 5.8},
        ],
        "wr": [
            {"name": "Keon Coleman", "number": 0, "catch_rate": 0.64, "avg_yards": 12.5},
            {"name": "Khalil Shakir", "number": 10, "catch_rate": 0.67, "avg_yards": 11.8},
            {"name": "Curtis Samuel", "number": 4, "catch_rate": 0.61, "avg_yards": 10.5},
            {"name": "Jalen Virgil", "number": 83, "catch_rate": 0.55, "avg_yards": 12.0},
            {"name": "Andy Isabella", "number": 88, "catch_rate": 0.52, "avg_yards": 11.0},
        ],
        "te": [
            {"name": "Dalton Kincaid", "number": 86, "catch_rate": 0.67, "avg_yards": 9.8},
            {"name": "Dawson Knox", "number": 88, "catch_rate": 0.62, "avg_yards": 10.5},
            {"name": "Quintin Morris", "number": 85, "catch_rate": 0.55, "avg_yards": 8.0},
        ],
        "k": [{"name": "Tyler Bass", "number": 2, "fg_pct": 0.845, "xp_pct": 0.980, "longest_fg": 55}],
        "p": [{"name": "Sam Martin", "number": 8, "avg_punt": 46.0, "inside_20_pct": 0.41}],
        "dl": [
            {"name": "Greg Rousseau", "number": 50, "pos": "DE", "sacks": 8},
            {"name": "Ed Oliver", "number": 91, "pos": "DT", "sacks": 5},
            {"name": "DaQuan Jones", "number": 92, "pos": "DT", "sacks": 3},
            {"name": "AJ Epenesa", "number": 57, "pos": "DE", "sacks": 4},
            {"name": "Von Miller", "number": 40, "pos": "DE", "sacks": 5},
            {"name": "Tim Settle", "number": 99, "pos": "DT", "sacks": 2},
        ],
        "lb": [
            {"name": "Matt Milano", "number": 58, "sacks": 2, "interceptions": 1},
            {"name": "Terrel Bernard", "number": 43, "sacks": 3, "interceptions": 2},
            {"name": "Dorian Williams", "number": 6, "sacks": 1, "interceptions": 0},
            {"name": "Baylon Spector", "number": 54, "sacks": 0, "interceptions": 0},
            {"name": "Joe Andreessen", "number": 48, "sacks": 0, "interceptions": 0},
            {"name": "Nicholas Morrow", "number": 50, "sacks": 1, "interceptions": 0},
            {"name": "Edefuan Ulofoshio", "number": 52, "sacks": 0, "interceptions": 0},
            {"name": "Shaq Lawson", "number": 90, "sacks": 2, "interceptions": 0},
        ],
        "db": [
            {"name": "Rasul Douglas", "number": 31, "pos": "CB", "sacks": 0, "interceptions": 4},
            {"name": "Christian Benford", "number": 47, "pos": "CB", "sacks": 0, "interceptions": 2},
            {"name": "Taron Johnson", "number": 24, "pos": "CB", "sacks": 1, "interceptions": 1},
            {"name": "Taylor Rapp", "number": 20, "pos": "S", "sacks": 0, "interceptions": 2},
            {"name": "Damar Hamlin", "number": 3, "pos": "S", "sacks": 0, "interceptions": 1},
            {"name": "Kaiir Elam", "number": 24, "pos": "CB", "sacks": 0, "interceptions": 1},
            {"name": "Cam Lewis", "number": 39, "pos": "CB", "sacks": 0, "interceptions": 0},
        ],
    },
    # Additional teams will be added in subsequent chunks
}
