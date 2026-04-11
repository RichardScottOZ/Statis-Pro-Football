import { useState } from 'react';
import type { PersonnelData, PlayerBrief } from '../types/game';

interface SubstitutionPanelProps {
  personnel: PersonnelData | null;
  loading: boolean;
  onSubstitute: (position: string, playerOut: string, playerIn: string) => void;
}

const POSITIONS = ['QB', 'RB', 'WR', 'TE', 'K', 'P'];

export function SubstitutionPanel({ personnel, loading, onSubstitute }: SubstitutionPanelProps) {
  const [selectedPos, setSelectedPos] = useState<string>('QB');
  const [isOpen, setIsOpen] = useState(false);

  if (!personnel) return null;

  const allPlayers = personnel.offense_all;
  const posPlayers = allPlayers.filter(
    (p) => p.position.toUpperCase() === selectedPos,
  );

  const starter = personnel.offense_starters[selectedPos];

  const handleSub = (benchPlayer: PlayerBrief) => {
    if (!starter) return;
    onSubstitute(selectedPos, starter.name, benchPlayer.name);
  };

  return (
    <div className="substitution-panel">
      <button
        className="sub-toggle-btn"
        onClick={() => setIsOpen(!isOpen)}
      >
        🔄 {isOpen ? 'Hide' : 'Show'} Substitutions
      </button>

      {isOpen && (
        <div className="sub-content">
          <div className="sub-pos-tabs">
            {POSITIONS.map((pos) => (
              <button
                key={pos}
                className={`sub-pos-tab ${selectedPos === pos ? 'active' : ''}`}
                onClick={() => setSelectedPos(pos)}
              >
                {pos}
              </button>
            ))}
          </div>

          <div className="sub-starter">
            <span className="sub-label">Starter:</span>
            {starter ? (
              <span className="sub-player-name">
                #{starter.number} {starter.name} ({starter.overall_grade})
              </span>
            ) : (
              <span className="sub-empty">None</span>
            )}
          </div>

          <div className="sub-bench">
            <span className="sub-label">Available:</span>
            <div className="sub-bench-list">
              {posPlayers
                .filter((p) => p.name !== starter?.name)
                .map((p, i) => (
                  <button
                    key={i}
                    className="sub-bench-btn"
                    onClick={() => handleSub(p)}
                    disabled={loading}
                    title={`Sub in ${p.name}`}
                  >
                    <span className="sub-num">#{p.number}</span>
                    <span className="sub-name">{p.name}</span>
                    <span className="sub-grade">{p.overall_grade}</span>
                    <span className="sub-arrow">↑</span>
                  </button>
                ))}
              {posPlayers.filter((p) => p.name !== starter?.name).length === 0 && (
                <span className="sub-empty">No backup at {selectedPos}</span>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
