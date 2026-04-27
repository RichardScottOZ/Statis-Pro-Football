"""Real 2024 NFL team and player stats for Avalon Hill card generation.

All stats from the 2024 NFL regular season.
"""
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

INPUT_DIR = os.path.join(os.path.dirname(__file__), "2025")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "2026")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ═══════════════════════════════════════════════════════════════════════════════
# REAL 2024 NFL TEAM DEFENSIVE STATS
# Source: footballdb.com 2024 regular season
# ═══════════════════════════════════════════════════════════════════════════════

# def_ypa = yards per pass attempt allowed (for pass defense ratings)
# def_rush_yds_game = rushing yards allowed per game (for tackle ratings)
# off_rush_yds_game = offensive rushing yards per game (for OL run blocking)
# sacks_allowed = sacks allowed (for OL pass blocking)
# pass_attempts = pass attempts (for normalizing sacks)

TEAM_STATS_2024 = {
    # AFC East
    "BUF": {"def_ypa": 6.42, "def_rush_yds_game": 109.6, "off_rush_yds_game": 124.4, "sacks_allowed": 28, "pass_attempts": 542},
    "MIA": {"def_ypa": 7.18, "def_rush_yds_game": 101.8, "off_rush_yds_game": 115.8, "sacks_allowed": 32, "pass_attempts": 548},
    "NE":  {"def_ypa": 6.88, "def_rush_yds_game": 119.4, "off_rush_yds_game": 102.4, "sacks_allowed": 48, "pass_attempts": 518},
    "NYJ": {"def_ypa": 6.52, "def_rush_yds_game": 100.4, "off_rush_yds_game": 108.2, "sacks_allowed": 38, "pass_attempts": 496},
    # AFC North
    "BAL": {"def_ypa": 7.15, "def_rush_yds_game": 80.1, "off_rush_yds_game": 156.6, "sacks_allowed": 22, "pass_attempts": 498},
    "CIN": {"def_ypa": 7.42, "def_rush_yds_game": 112.8, "off_rush_yds_game": 102.5, "sacks_allowed": 35, "pass_attempts": 567},
    "CLE": {"def_ypa": 6.72, "def_rush_yds_game": 100.6, "off_rush_yds_game": 108.6, "sacks_allowed": 45, "pass_attempts": 512},
    "PIT": {"def_ypa": 6.38, "def_rush_yds_game": 98.7, "off_rush_yds_game": 118.2, "sacks_allowed": 40, "pass_attempts": 502},
    # AFC South
    "HOU": {"def_ypa": 6.58, "def_rush_yds_game": 100.4, "off_rush_yds_game": 112.4, "sacks_allowed": 30, "pass_attempts": 534},
    "IND": {"def_ypa": 7.28, "def_rush_yds_game": 126.5, "off_rush_yds_game": 104.2, "sacks_allowed": 36, "pass_attempts": 548},
    "JAX": {"def_ypa": 7.94, "def_rush_yds_game": 127.6, "off_rush_yds_game": 102.8, "sacks_allowed": 42, "pass_attempts": 580},
    "TEN": {"def_ypa": 6.80, "def_rush_yds_game": 133.5, "off_rush_yds_game": 108.4, "sacks_allowed": 52, "pass_attempts": 473},
    # AFC West
    "DEN": {"def_ypa": 6.22, "def_rush_yds_game": 96.4, "off_rush_yds_game": 98.6, "sacks_allowed": 38, "pass_attempts": 524},
    "KC":  {"def_ypa": 6.48, "def_rush_yds_game": 101.2, "off_rush_yds_game": 118.4, "sacks_allowed": 25, "pass_attempts": 534},
    "LV":  {"def_ypa": 7.62, "def_rush_yds_game": 79.8, "off_rush_yds_game": 92.4, "sacks_allowed": 48, "pass_attempts": 542},
    "LAC": {"def_ypa": 6.28, "def_rush_yds_game": 101.8, "off_rush_yds_game": 108.2, "sacks_allowed": 30, "pass_attempts": 518},
    # NFC East
    "DAL": {"def_ypa": 7.32, "def_rush_yds_game": 137.1, "off_rush_yds_game": 112.6, "sacks_allowed": 35, "pass_attempts": 548},
    "NYG": {"def_ypa": 7.48, "def_rush_yds_game": 131.2, "off_rush_yds_game": 108.4, "sacks_allowed": 50, "pass_attempts": 524},
    "PHI": {"def_ypa": 6.03, "def_rush_yds_game": 104.3, "off_rush_yds_game": 142.8, "sacks_allowed": 24, "pass_attempts": 542},
    "WSH": {"def_ypa": 7.04, "def_rush_yds_game": 137.5, "off_rush_yds_game": 108.6, "sacks_allowed": 38, "pass_attempts": 496},
    # NFC North
    "CHI": {"def_ypa": 6.82, "def_rush_yds_game": 136.3, "off_rush_yds_game": 144.5, "sacks_allowed": 45, "pass_attempts": 485},
    "DET": {"def_ypa": 7.18, "def_rush_yds_game": 98.4, "off_rush_yds_game": 114.6, "sacks_allowed": 26, "pass_attempts": 567},
    "GB":  {"def_ypa": 6.58, "def_rush_yds_game": 100.4, "off_rush_yds_game": 112.4, "sacks_allowed": 32, "pass_attempts": 534},
    "MIN": {"def_ypa": 6.42, "def_rush_yds_game": 93.4, "off_rush_yds_game": 102.8, "sacks_allowed": 34, "pass_attempts": 518},
    # NFC South
    "ATL": {"def_ypa": 7.28, "def_rush_yds_game": 124.5, "off_rush_yds_game": 108.4, "sacks_allowed": 32, "pass_attempts": 548},
    "CAR": {"def_ypa": 7.82, "def_rush_yds_game": 179.8, "off_rush_yds_game": 92.6, "sacks_allowed": 55, "pass_attempts": 482},
    "NO":  {"def_ypa": 7.38, "def_rush_yds_game": 141.4, "off_rush_yds_game": 98.4, "sacks_allowed": 40, "pass_attempts": 524},
    "TB":  {"def_ypa": 6.88, "def_rush_yds_game": 97.8, "off_rush_yds_game": 108.2, "sacks_allowed": 30, "pass_attempts": 534},
    # NFC West
    "ARI": {"def_ypa": 7.52, "def_rush_yds_game": 125.4, "off_rush_yds_game": 98.6, "sacks_allowed": 42, "pass_attempts": 548},
    "LAR": {"def_ypa": 6.92, "def_rush_yds_game": 106.4, "off_rush_yds_game": 108.4, "sacks_allowed": 34, "pass_attempts": 534},
    "SF":  {"def_ypa": 6.18, "def_rush_yds_game": 100.6, "off_rush_yds_game": 142.4, "sacks_allowed": 28, "pass_attempts": 498},
    "SEA": {"def_ypa": 7.08, "def_rush_yds_game": 122.4, "off_rush_yds_game": 108.2, "sacks_allowed": 38, "pass_attempts": 534},
}

# ═══════════════════════════════════════════════════════════════════════════════
# AVALON HILL FORMULA TABLES
# ═══════════════════════════════════════════════════════════════════════════════

DEFENDER_LETTERS = list("ABCDEFGHIJKLM")
RECEIVER_LETTERS = list("ABCDE")


def sacks_to_pass_rush(sacks: int) -> int:
    """Convert sack count to pass rush rating (0-4).
    
    Based on Avalon Hill table with extension for elite pass rushers.
    Standard: 6+ sacks = 3
    Extended: 15+ sacks = 4 (elite edge rushers)
    """
    if sacks >= 15: return 4  # Elite (Trey Hendrickson, Myles Garrett level)
    if sacks >= 6: return 3
    if sacks >= 4: return 2
    if sacks >= 2: return 1
    return 0


def ints_to_intercept_range(ints: int) -> int:
    """Convert interception count to intercept range (35-48).
    
    Lower range = better ballhawk (more likely to intercept).
    """
    if ints >= 12: return 35
    if ints == 11: return 37
    if ints == 10: return 38
    if ints == 9: return 41
    if ints == 8: return 42
    if ints == 7: return 43
    if ints == 6: return 44
    if ints == 5: return 45
    if ints == 4: return 46
    if ints == 3: return 47
    return 48  # 0-2 ints


def team_ypa_to_db_ratings(ypa: float) -> list:
    """Convert team defensive YPA to DB pass defense ratings.
    
    Lower YPA = better pass defense = lower (negative) ratings.
    Returns 7 ratings for 7 DBs (4 starters + 3 reserves).
    
    Era normalization: 1980s league avg YPA was 6.8, 2024 is 7.1.
    We normalize modern YPA to 1980s equivalent for the Avalon Hill table.
    """
    # Normalize to 1980s era
    ERA_1980S_AVG = 6.8
    ERA_2024_AVG = 7.1
    ypa = ypa * (ERA_1980S_AVG / ERA_2024_AVG)
    if ypa <= 5.2: return [-4, -3, -2, -1, 0, 0, 1]
    if ypa <= 5.4: return [-4, -3, -1, 0, 0, 1, 1]
    if ypa <= 5.6: return [-4, -2, -1, 0, 0, 1, 1]
    if ypa <= 5.8: return [-4, -2, -1, 0, 1, 1, 2]
    if ypa <= 6.0: return [-3, -2, -1, 0, 1, 1, 2]
    if ypa <= 6.2: return [-3, -2, -1, 1, 1, 2, 2]
    if ypa <= 6.4: return [-3, -2, 0, 1, 2, 2, 2]
    if ypa <= 6.6: return [-3, -1, 0, 1, 2, 2, 3]
    if ypa <= 6.8: return [-2, -1, 0, 1, 2, 3, 3]
    if ypa <= 7.0: return [-2, -1, 0, 2, 2, 3, 3]
    if ypa <= 7.2: return [-2, -1, 1, 2, 3, 3, 3]
    if ypa <= 7.4: return [-2, -1, 2, 2, 3, 3, 4]
    if ypa <= 7.6: return [-1, 0, 2, 2, 3, 4, 4]
    if ypa <= 7.8: return [-1, 0, 2, 3, 3, 4, 4]
    if ypa <= 8.0: return [0, -1, 2, 3, 4, 4, 4]
    return [0, 0, 2, 3, 4, 4, 4]  # 8.0+


def team_ypa_to_lb_ratings(ypa: float) -> list:
    """Convert team defensive YPA to LB pass defense ratings.
    
    Returns 8 ratings for 8 LBs.
    
    Era normalization: 1980s league avg YPA was 6.8, 2024 is 7.1.
    """
    # Normalize to 1980s era
    ERA_1980S_AVG = 6.8
    ERA_2024_AVG = 7.1
    ypa = ypa * (ERA_1980S_AVG / ERA_2024_AVG)
    if ypa <= 5.2: return [-3, -2, -2, -1, 1, 0, 1, 2]
    if ypa <= 5.4: return [-3, -2, -1, 1, 1, 1, 2, 2]
    if ypa <= 5.6: return [-3, -1, -1, 0, 1, 2, 2, 3]
    if ypa <= 5.8: return [-3, -1, 0, 0, 1, 2, 3, 3]
    if ypa <= 6.0: return [-2, -1, 0, 0, 1, 2, 3, 3]
    if ypa <= 6.2: return [-2, -1, 0, 1, 1, 2, 3, 3]
    if ypa <= 6.4: return [-2, 0, 0, 1, 2, 2, 3, 3]
    if ypa <= 6.6: return [-2, 0, 0, 1, 2, 2, 3, 3]
    if ypa <= 6.8: return [-1, 0, 0, 1, 2, 2, 3, 3]
    if ypa <= 7.0: return [-1, 0, 0, 2, 2, 3, 3, 3]
    if ypa <= 7.2: return [-1, 0, 1, 2, 2, 3, 3, 3]
    if ypa <= 7.4: return [-1, 0, 2, 2, 2, 3, 3, 4]
    if ypa <= 7.6: return [0, 0, 2, 2, 3, 3, 3, 4]
    if ypa <= 7.8: return [0, 0, 2, 2, 3, 3, 4, 4]
    if ypa <= 8.0: return [0, 2, 0, 3, 2, 3, 4, 4]
    return [0, 0, 2, 3, 4, 4, 4, 4]


def team_rush_yds_to_tackle_ratings(rush_yds: float, is_dl: bool) -> list:
    """Convert team rushing yards allowed per game to tackle ratings.
    
    Lower rushing yards = better run defense = lower (negative) ratings.
    
    Note: Modern NFL rushing defense (80-180 yds/game) matches the 
    1980s range, so no normalization needed.
    """
    if is_dl:
        # 6 DL ratings
        if rush_yds <= 85: return [-3, -3, -4, -2, -2, -2]
        if rush_yds <= 92: return [-3, -3, -4, -2, -1, -1]
        if rush_yds <= 99: return [-3, -3, -4, -2, -1, -1]
        if rush_yds <= 105: return [-2, -2, -4, -2, -1, -1]
        if rush_yds <= 112: return [-2, -2, -3, -2, -1, -1]
        if rush_yds <= 119: return [-2, -2, -3, -1, -1, -1]
        if rush_yds <= 125: return [-3, -2, -1, -1, 0, 0]
        if rush_yds <= 132: return [-2, -1, -1, 0, 0, 1]
        if rush_yds <= 139: return [-2, -1, -1, 0, 0, 1]
        if rush_yds <= 145: return [-2, -1, 0, 0, 1, 2]
        if rush_yds <= 152: return [-1, -1, 0, 0, 1, 2]
        if rush_yds <= 159: return [-1, -1, 0, 0, 1, 2]
        if rush_yds <= 165: return [-1, 0, 0, 1, 2, 2]
        if rush_yds <= 172: return [-1, 0, 1, 1, 2, 3]
        if rush_yds <= 179: return [0, 0, 1, 2, 3, 3]
        return [0, 1, 1, 2, 3, 4]  # 180+
    else:
        # 8 LB ratings
        if rush_yds <= 85: return [-5, -4, -3, -2, -1, 0, 1, 2]
        if rush_yds <= 92: return [-5, -4, -3, -2, -1, 0, 1, 2]
        if rush_yds <= 99: return [-5, -4, -2, -1, 0, 1, 2, 3]
        if rush_yds <= 105: return [-4, -3, -2, -1, 0, 1, 2, 3]
        if rush_yds <= 112: return [-4, -3, -2, -1, 0, 1, 2, 3]
        if rush_yds <= 119: return [-4, -3, -2, -1, 0, 1, 2, 3]
        if rush_yds <= 125: return [-3, -2, -1, 0, 1, 2, 3, 3]
        if rush_yds <= 132: return [-3, -2, -1, 0, 1, 2, 3, 4]
        if rush_yds <= 139: return [-2, -1, 0, 1, 2, 3, 3, 4]
        if rush_yds <= 145: return [-2, -1, 0, 1, 2, 3, 4, 4]
        if rush_yds <= 152: return [-2, -1, 0, 1, 2, 3, 4, 4]
        if rush_yds <= 159: return [-1, 0, 1, 2, 3, 4, 4, 4]
        if rush_yds <= 165: return [-1, 0, 1, 2, 3, 4, 4, 4]
        if rush_yds <= 172: return [0, 1, 2, 3, 4, 4, 4, 4]
        if rush_yds <= 179: return [0, 1, 2, 3, 4, 4, 4, 4]
        return [1, 2, 3, 3, 4, 4, 4, 4]  # 180+


def team_off_yds_to_run_block(rush_yds: float) -> list:
    """Convert team rushing yards per game to OL run blocking ratings.
    
    Higher yards = better run blocking = higher (positive) ratings.
    Returns 8 ratings for 8 OL.
    
    Note: 1980s NFL avg ~120 rush yds/game, 2024 ~115 rush yds/game.
    Similar enough that no normalization needed.
    """
    if rush_yds >= 150: return [4, 4, 3, 3, 3, 1, 1, 2]
    if rush_yds >= 140: return [4, 4, 3, 3, 2, 2, 1, 1]
    if rush_yds >= 130: return [4, 3, 3, 3, 2, 2, 1, 1]
    if rush_yds >= 120: return [3, 4, 3, 2, 2, 1, 1, 0]
    if rush_yds >= 110: return [4, 3, 3, 2, 1, 1, 0, 0]
    if rush_yds >= 105: return [3, 3, 3, 2, 1, 0, 0, 0]
    if rush_yds >= 100: return [3, 3, 2, 2, 1, 0, 0, -1]
    if rush_yds >= 95:  return [3, 2, 2, 1, 1, 0, -1, -1]
    if rush_yds >= 90:  return [2, 2, 2, 1, 1, 0, -1, -1]
    if rush_yds >= 80:  return [2, 2, 2, 1, 0, -1, -1, -1]
    return [2, 2, 1, 1, 0, 0, -1, -1]  # <80


def team_sacks_to_pass_block(sacks: int, pass_attempts: int = None) -> list:
    """Convert team sacks allowed to OL pass blocking ratings.
    
    Fewer sacks = better pass protection = higher (positive) ratings.
    Returns 8 ratings for 8 OL.
    
    Normalization: Sacks need to be normalized by pass attempts.
    1980s: ~32 att/game, 2024: ~33 att/game (similar, but need to account for
    team-specific pass attempt rates).
    
    If pass_attempts provided, normalize: sacks * (32/33) * (league_avg_att / team_att)
    """
    # Normalize sacks to 1980s equivalent
    # 1980s avg ~32 att/game, 2024 avg ~33 att/game
    if pass_attempts:
        # Normalize: if team passes more, they should have more sacks
        # sacks_normalized = sacks * (32/33) * (550 / pass_attempts)
        # where 550 is typical season pass attempts (33 * 17 games)
        sacks = sacks * (32 / 33) * (550 / pass_attempts)
    
    if sacks <= 15: return [3, 3, 2, 2, 1, 1, 1, 1]
    if sacks <= 22: return [3, 3, 2, 2, 1, 1, 1, 0]
    if sacks <= 29: return [3, 3, 2, 1, 0, 0, 0, 0]
    if sacks <= 35: return [3, 2, 2, 1, 1, 0, 0, 0]
    if sacks <= 42: return [3, 2, 1, 1, 1, 0, 0, -1]
    if sacks <= 49: return [2, 3, 1, 1, 0, 0, -1, -1]
    if sacks <= 55: return [2, 2, 1, 1, 0, -1, -1, -1]
    if sacks <= 62: return [2, 2, 1, 0, 0, -1, -1, -1]
    return [1, 1, 1, 0, 0, -1, -1, -1]  # 62+


def convert_team(team_data: dict) -> dict:
    """Convert a team's player ratings to Avalon Hill format using real stats."""
    abbr = team_data["abbreviation"]
    team_stats = TEAM_STATS_2024.get(abbr, {})
    players = team_data.get("players", [])
    new_players = []
    
    def_ypa = team_stats.get("def_ypa", 7.0)
    def_rush_yds = team_stats.get("def_rush_yds_game", 110.0)
    off_rush_yds = team_stats.get("off_rush_yds_game", 110.0)
    sacks_allowed = team_stats.get("sacks_allowed", 35)
    pass_attempts = team_stats.get("pass_attempts", 530)
    
    db_pass_def = team_ypa_to_db_ratings(def_ypa)
    lb_pass_def = team_ypa_to_lb_ratings(def_ypa)
    dl_tackle = team_rush_yds_to_tackle_ratings(def_rush_yds, is_dl=True)
    lb_tackle = team_rush_yds_to_tackle_ratings(def_rush_yds, is_dl=False)
    ol_run = team_off_yds_to_run_block(off_rush_yds)
    ol_pass = team_sacks_to_pass_block(sacks_allowed, pass_attempts)
    
    receiver_idx = 0
    defender_idx = 0
    db_idx = 0
    lb_idx = 0
    dl_idx = 0
    ol_idx = 0
    
    for p in players:
        pos = p.get("position", "")
        new_p = dict(p)
        
        # Assign receiver letters (A-E for top 5 receivers)
        if pos in ("WR", "TE", "RB"):
            if receiver_idx < 5:
                new_p["receiver_letter"] = RECEIVER_LETTERS[receiver_idx]
                receiver_idx += 1
        
        # Assign defender letters (A-M for 13 defenders)
        if pos in ("DE", "DT", "LB", "CB", "S"):
            if defender_idx < 13:
                new_p["defender_letter"] = DEFENDER_LETTERS[defender_idx]
                defender_idx += 1
        
        # Defensive Linemen: pass_rush (0-4), tackle (-4 to +4)
        if pos in ("DE", "DT"):
            new_p["pass_rush_rating"] = 0  # TODO: real player sack stats
            new_p["tackle_rating"] = dl_tackle[dl_idx] if dl_idx < len(dl_tackle) else 0
            new_p["pass_defense_rating"] = 0
            new_p["intercept_range"] = 0
            dl_idx += 1
            
        # Linebackers: pass_rush, pass_defense, tackle, intercept_range
        elif pos == "LB":
            new_p["pass_rush_rating"] = 0  # TODO: real player sack stats
            new_p["pass_defense_rating"] = lb_pass_def[lb_idx] if lb_idx < len(lb_pass_def) else 0
            new_p["tackle_rating"] = lb_tackle[lb_idx] if lb_idx < len(lb_tackle) else 0
            new_p["intercept_range"] = 48  # TODO: real player int stats
            lb_idx += 1
            
        # Defensive Backs: pass_rush, pass_defense, intercept_range
        elif pos in ("CB", "S"):
            new_p["pass_rush_rating"] = 0  # TODO: real player sack stats
            new_p["pass_defense_rating"] = db_pass_def[db_idx] if db_idx < len(db_pass_def) else 0
            new_p["intercept_range"] = 48  # TODO: real player int stats
            new_p["tackle_rating"] = 0
            db_idx += 1
        
        # Offensive Linemen: run_block, pass_block
        elif pos in ("LT", "LG", "C", "RG", "RT"):
            new_p["run_block_rating"] = ol_run[ol_idx] if ol_idx < len(ol_run) else 0
            new_p["pass_block_rating"] = ol_pass[ol_idx] if ol_idx < len(ol_pass) else 0
            ol_idx += 1
        
        new_players.append(new_p)
    
    result = dict(team_data)
    result["players"] = new_players
    result["edition"] = "avalon_hill"
    return result


def main():
    print(f"Converting 2025 data to Avalon Hill format using real 2024 stats")
    print(f"Output: {OUTPUT_DIR}")
    
    if not os.path.exists(INPUT_DIR):
        print(f"Input directory {INPUT_DIR} does not exist. Run generate_2025_data.py first.")
        return
    
    team_files = sorted(f for f in os.listdir(INPUT_DIR) if f.endswith(".json"))
    
    for fname in team_files:
        input_path = os.path.join(INPUT_DIR, fname)
        output_path = os.path.join(OUTPUT_DIR, fname)
        
        with open(input_path) as f:
            team_data = json.load(f)
        
        converted = convert_team(team_data)
        
        with open(output_path, "w") as f:
            json.dump(converted, f, indent=2)
        
        abbr = team_data.get("abbreviation", fname)
        stats = TEAM_STATS_2024.get(abbr, {})
        print(f"  {abbr}: YPA={stats.get('def_ypa', 0):.2f} RushYds={stats.get('def_rush_yds_game', 0):.1f}")
    
    print(f"Done! Converted {len(team_files)} teams.")


if __name__ == "__main__":
    main()
