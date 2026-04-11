import { useState, useEffect } from 'react';
import axios from 'axios';
import type { GameMode } from '../types/game';

const API_BASE = '/api';

const ALL_TEAMS = [
  'ARI','ATL','BAL','BUF','CAR','CHI','CIN','CLE',
  'DAL','DEN','DET','GB','HOU','IND','JAX','KC',
  'LAC','LAR','LV','MIA','MIN','NE','NO','NYG',
  'NYJ','PHI','PIT','SF','SEA','TB','TEN','WAS',
];

const GAME_MODES: { value: GameMode; label: string; desc: string }[] = [
  { value: 'human_home', label: '🏠 Play as Home', desc: 'You control the home team offense vs AI' },
  { value: 'human_away', label: '✈️ Play as Away', desc: 'You control the away team offense vs AI' },
  { value: 'solitaire', label: '🤖 Solitaire', desc: 'AI controls both teams (simulation mode)' },
];

interface TeamSelectorProps {
  onStartGame: (homeTeam: string, awayTeam: string, mode: GameMode) => void;
  loading: boolean;
}

export function TeamSelector({ onStartGame, loading }: TeamSelectorProps) {
  const [homeTeam, setHomeTeam] = useState('KC');
  const [awayTeam, setAwayTeam] = useState('BUF');
  const [gameMode, setGameMode] = useState<GameMode>('human_home');
  const [availableTeams, setAvailableTeams] = useState<string[]>(ALL_TEAMS);

  useEffect(() => {
    axios
      .get(`${API_BASE}/teams`)
      .then((res) => {
        if (res.data.teams && res.data.teams.length > 0) {
          setAvailableTeams(res.data.teams);
        }
      })
      .catch(() => {
        // Use fallback list if API unavailable
      });
  }, []);

  const handleStart = () => {
    if (homeTeam && awayTeam && homeTeam !== awayTeam) {
      onStartGame(homeTeam, awayTeam, gameMode);
    }
  };

  return (
    <div className="team-selector">
      <h2 className="selector-title">🏈 Statis Pro Football</h2>
      <p className="selector-subtitle">Select teams and game mode</p>

      <div className="team-pickers">
        <div className="team-pick">
          <label htmlFor="away-team">Away Team</label>
          <select
            id="away-team"
            value={awayTeam}
            onChange={(e) => setAwayTeam(e.target.value)}
          >
            {availableTeams.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>

        <span className="at-symbol">@</span>

        <div className="team-pick">
          <label htmlFor="home-team">Home Team</label>
          <select
            id="home-team"
            value={homeTeam}
            onChange={(e) => setHomeTeam(e.target.value)}
          >
            {availableTeams.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>
      </div>

      {homeTeam === awayTeam && (
        <p className="selector-error">Home and away teams must be different.</p>
      )}

      {/* Game Mode Selection */}
      <div className="mode-selector">
        {GAME_MODES.map((m) => (
          <button
            key={m.value}
            className={`mode-btn ${gameMode === m.value ? 'active' : ''}`}
            onClick={() => setGameMode(m.value)}
          >
            <span className="mode-label">{m.label}</span>
            <span className="mode-desc">{m.desc}</span>
          </button>
        ))}
      </div>

      <button
        className="btn btn-start"
        onClick={handleStart}
        disabled={loading || homeTeam === awayTeam}
      >
        {loading ? '⏳ Starting...' : '🏈 Start Game'}
      </button>
    </div>
  );
}
