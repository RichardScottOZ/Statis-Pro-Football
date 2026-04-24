# FAC Field Distributions Reference

This document provides the exact probability distributions for every field on the
109-card Fast Action Card (FAC) deck used in Statis Pro Football 5th Edition.
All counts and percentages are derived directly from the canonical BJY deck data in
`engine/fac_deck.py`.

---

## Deck Structure

| Subset | Count | Notes |
|--------|-------|-------|
| Standard cards | 96 | Numbers 1–48, each appearing twice (once normal, once OB) |
| Z cards | 13 | Special-event cards — all fields are "Z" |
| **Total** | **109** | |

> **Z-card rule:** When a Z card is drawn, it is resolved via the "3 Z-rules" and a
> second card is drawn for the play. Z cards carry no RN, PASS#, SL/IL/SR/IR, ER,
> QK/SH/LG, SC, or SOLO values. Only the Z_RES field on *non-Z cards* is used
> during normal play.
>
> In solitaire mode, one Z card is removed before play, leaving 108 cards.

Probabilities below are quoted for **non-Z draws** (96 cards) unless stated otherwise.
Use the **109-card** base when computing the chance of drawing a Z card at all (~11.9%).

---

## 1. RN — Run Number

RN drives all rushing play lookups on RB/QB cards. The RN is either a plain number
(1–12), a number with `(OB)` suffix (runner goes out of bounds, clock stops), or `Z`
(Z card — no RN used).

### Overall breakdown (109 cards)

| Category | Count | Probability |
|----------|-------|-------------|
| Z card (no RN) | 13 | 11.9% |
| OB variant (runner goes OOB) | 24 | 22.0% |
| Normal (in-bounds) | 72 | 66.1% |

> Among non-Z cards: **25.0%** of plays result in an out-of-bounds run; **75.0%** are in-bounds.

### RN per value (non-Z cards, base = 96)

| RN | Normal | OB | Total | Normal % | OB % | Total % |
|----|--------|----|-------|----------|------|---------|
|  1 |   7    |  1 |   8   |  7.3%    | 1.0% |  8.3%   |
|  2 |   3    |  2 |   5   |  3.1%    | 2.1% |  5.2%   |
|  3 |   3    |  2 |   5   |  3.1%    | 2.1% |  5.2%   |
|  4 |   4    |  2 |   6   |  4.2%    | 2.1% |  6.2%   |
|  5 |   9    |  3 |  12   |  9.4%    | 3.1% | 12.5%   |
|  6 |   9    |  2 |  11   |  9.4%    | 2.1% | 11.5%   |
|  7 |   8    |  2 |  10   |  8.3%    | 2.1% | 10.4%   |
|  8 |   5    |  2 |   7   |  5.2%    | 2.1% |  7.3%   |
|  9 |   6    |  2 |   8   |  6.2%    | 2.1% |  8.3%   |
| 10 |   6    |  2 |   8   |  6.2%    | 2.1% |  8.3%   |
| 11 |   5    |  3 |   8   |  5.2%    | 3.1% |  8.3%   |
| 12 |   7    |  1 |   8   |  7.3%    | 1.0% |  8.3%   |
| **Total** | **72** | **24** | **96** | | | |

**Key observations for tackle-table work:**
- RN 5 and 6 are by far the most common values (~12.5% and 11.5% of non-Z draws).
- RN 2 and 3 are the rarest (~5.2% each).
- RN 1, 8–12 are each ~7–8.3%.
- About 1-in-4 non-Z draws has an OB suffix, which stops the clock on runs.

---

## 2. PASS# — Pass Number

PASS# drives all passing play lookups on QB and receiver cards.

| Feature | Detail |
|---------|--------|
| Range | 1–48 |
| Occurrences per value | Exactly **2** on every non-Z card |
| Z card PASS# | "Z" (13 cards) |

Every pass number from 1 to 48 appears exactly twice across the 96 non-Z cards,
giving a perfectly flat distribution: each PASS# has a **2/96 = 2.08%** chance of
appearing on any non-Z draw.

---

## 3. SL / IL / SR / IR — Blocking Matchup Fields

These four fields identify which offensive blocker(s) face which defensive box(es) for
each run direction. The engine compares Blocker Value (BV) versus Tackle Value (TV) to
determine whether the offense, defense, or both win the blocking battle.

The values fall into several pattern families:

| Pattern | Example | Meaning |
|---------|---------|---------|
| Single OL position | `LT`, `LG`, `LE`, `RT`, `RG`, `RE`, `CN` | One lineman blocks |
| OL + OL pair | `LG + LT`, `LG + LE` | Two linemen block together |
| OL vs box | `LT vs A`, `LG vs B` | OL matched to a specific defensive box |
| Box letter only | `A`, `B`, `C`, `D`, `E` | Blocker is the player in that box |
| Box pair | `A + F`, `B + G` | Two boxes are both matched |
| Back | `BK`, `BK vs F`, `BK vs G` | Running back is the blocker |
| Break | `Break` | Breakaway — no meaningful matchup |

### SL (Sweep Left) — 96 non-Z cards

| Value | Count | % |
|-------|-------|---|
| `LG + LT` | 8 | 8.3% |
| `LE vs F` | 8 | 8.3% |
| `LT vs A` | 8 | 8.3% |
| `A` | 8 | 8.3% |
| `B` | 8 | 8.3% |
| `A + F` | 8 | 8.3% |
| `B + G` | 8 | 8.3% |
| `LT` | 6 | 6.2% |
| `LG + LE` | 5 | 5.2% |
| `LG vs F` | 4 | 4.2% |
| `LT vs B` | 4 | 4.2% |
| `LE` | 4 | 4.2% |
| `LG` | 4 | 4.2% |
| `Break` | 3 | 3.1% |
| `BK vs F` | 2 | 2.1% |
| `BK vs G` | 2 | 2.1% |
| `BK` | 2 | 2.1% |
| `LT vs G` | 2 | 2.1% |
| `LE vs H` | 2 | 2.1% |

### IL (Inside Left) — 96 non-Z cards

| Value | Count | % |
|-------|-------|---|
| `LG` | 10 | 10.4% |
| `LG vs B` | 9 | 9.4% |
| `CN vs C` | 8 | 8.3% |
| `B` | 8 | 8.3% |
| `C` | 8 | 8.3% |
| `B + G` | 8 | 8.3% |
| `C + H` | 8 | 8.3% |
| `CN` | 6 | 6.2% |
| `BK` | 5 | 5.2% |
| `CN + LG` | 4 | 4.2% |
| `CN vs H` | 4 | 4.2% |
| `LT` | 4 | 4.2% |
| `LG vs G` | 3 | 3.1% |
| `Break` | 3 | 3.1% |
| `BK vs G` | 2 | 2.1% |
| `BK vs H` | 2 | 2.1% |
| `BK vs I` | 2 | 2.1% |
| `LT vs G` | 2 | 2.1% |

### SR (Sweep Right) — 96 non-Z cards

| Value | Count | % |
|-------|-------|---|
| `RG + RT` | 8 | 8.3% |
| `RE vs J` | 8 | 8.3% |
| `RT vs E` | 8 | 8.3% |
| `D` | 8 | 8.3% |
| `E` | 8 | 8.3% |
| `D + I` | 8 | 8.3% |
| `E + J` | 8 | 8.3% |
| `RT` | 6 | 6.2% |
| `RG + RE` | 5 | 5.2% |
| `RG vs J` | 4 | 4.2% |
| `RT vs D` | 4 | 4.2% |
| `RE` | 4 | 4.2% |
| `Break` | 3 | 3.1% |
| `RG` | 3 | 3.1% |
| `BK vs J` | 2 | 2.1% |
| `BK vs I` | 2 | 2.1% |
| `BK` | 2 | 2.1% |
| `RT vs I` | 2 | 2.1% |
| `RE vs H` | 2 | 2.1% |
| `CN + RG` | 1 | 1.0% |

### IR (Inside Right) — 96 non-Z cards

| Value | Count | % |
|-------|-------|---|
| `RG` | 11 | 11.5% |
| `CN vs C` | 8 | 8.3% |
| `RG vs D` | 8 | 8.3% |
| `C` | 8 | 8.3% |
| `D` | 8 | 8.3% |
| `C + H` | 8 | 8.3% |
| `D + I` | 8 | 8.3% |
| `CN` | 6 | 6.2% |
| `BK` | 5 | 5.2% |
| `CN vs H` | 4 | 4.2% |
| `RG vs I` | 4 | 4.2% |
| `RT` | 4 | 4.2% |
| `CN + RG` | 3 | 3.1% |
| `Break` | 3 | 3.1% |
| `BK vs H` | 2 | 2.1% |
| `BK vs G` | 2 | 2.1% |
| `RT vs I` | 2 | 2.1% |
| `BK vs I` | 1 | 1.0% |
| `BK vs J` | 1 | 1.0% |

**Symmetry note:** SL and SR mirror each other (left-side blockers on SL, right-side on
SR). IL and IR likewise mirror each other. `Break` (~3%) appears equally on all four
fields and triggers a breakaway run result independent of BV/TV.

---

## 4. ER — End Run / Pass Rush

The ER field is used in two contexts:
- **End-around plays:** Look up ER on the ball-carrier's rush column.
- **Pass rush:** When QK/SH/LG shows `P.Rush`, the ER value determines whether the
  rusher gets a sack (negative yards) or the QB escapes (`OK`).

| Value | Count | % | Meaning |
|-------|-------|---|---------|
| `OK` | 48 | 50.0% | No sack — QB/runner escapes |
| `-1` |  8 |  8.3% | 1-yard sack |
| `-2` |  8 |  8.3% | 2-yard sack |
| `-3` |  8 |  8.3% | 3-yard sack |
| `-4` |  8 |  8.3% | 4-yard sack |
| `-5` |  8 |  8.3% | 5-yard sack |
| `-6` |  8 |  8.3% | 6-yard sack |

**Summary:** Exactly **50%** of non-Z cards give `OK` (no sack). The other 50% are
evenly split across sack values of −1 through −6 (8 cards each, ~8.3% each). When a
`P.Rush` fires, there is therefore a **50% chance of a sack** and, given a sack,
equal probability of each depth (−1 through −6).

---

## 5. QK / SH / LG — Receiver Target Override

These three fields redirect which receiver is targeted (or trigger a pass rush) for
quick, short, and long passes respectively. When the field reads `Orig`, the called
receiver from the play call is used. All other values override or modify the target.

| Code | Meaning |
|------|---------|
| `Orig` | Use the originally called receiver |
| `FL` | Target the Flanker (WR in FL position) |
| `LE` | Target the Left End (TE or WR on left) |
| `RE` | Target the Right End (TE or WR on right) |
| `BK1` | Target Running Back 1 |
| `BK2` | Target Running Back 2 |
| `P.Rush` | Defensive pass rush fires — use ER to resolve |

### QK (Quick Pass target) — 96 non-Z cards

| Value | Count | % |
|-------|-------|---|
| `Orig` | 40 | 41.7% |
| `FL`   | 13 | 13.5% |
| `RE`   | 13 | 13.5% |
| `LE`   | 13 | 13.5% |
| `BK1`  |  8 |  8.3% |
| `BK2`  |  7 |  7.3% |
| `P.Rush` | 2 |  2.1% |

### SH (Short Pass target) — 96 non-Z cards

| Value | Count | % |
|-------|-------|---|
| `Orig`   | 40 | 41.7% |
| `FL`     | 12 | 12.5% |
| `LE`     | 11 | 11.5% |
| `RE`     | 10 | 10.4% |
| `BK1`    |  8 |  8.3% |
| `P.Rush` |  8 |  8.3% |
| `BK2`    |  7 |  7.3% |

### LG (Long Pass target) — 96 non-Z cards

| Value | Count | % |
|-------|-------|---|
| `Orig`   | 40 | 41.7% |
| `P.Rush` | 14 | 14.6% |
| `FL`     |  9 |  9.4% |
| `RE`     |  9 |  9.4% |
| `LE`     |  9 |  9.4% |
| `BK1`    |  8 |  8.3% |
| `BK2`    |  7 |  7.3% |

**Key observations:**
- `Orig` (no override) is the most common result at ~42% for all three pass types.
- `P.Rush` escalates sharply from QK (2.1%) → SH (8.3%) → LG (14.6%), reflecting
  the greater pass-rush opportunity on longer-developing routes.
- `FL`, `LE`, and `RE` receiver redirects each appear ~9–14% across pass types.
- `BK1` and `BK2` (checkdown backs) together account for ~15–16% of non-Orig
  non-P.Rush results on all three pass types.

---

## 6. SC — Screen Pass Result

The SC field is used only on screen pass plays.

| Value | Count | % | Meaning |
|-------|-------|---|---------|
| `Com` | 49 | 51.0% | Standard completion — look up yardage on receiver card |
| `Inc` | 21 | 21.9% | Incomplete pass |
| `Com x 2` | 20 | 20.8% | Completion — yardage doubled |
| `Com x 3` |  4 |  4.2% | Completion — yardage tripled |
| `Dropped Int` | 1 | 1.0% | Defensive drop — treated as incomplete |
| `Int` | 1 | 1.0% | Interception |

**Summary:**
- Screen pass completion rate: **~76%** (Com + Com x 2 + Com x 3)
- "Big play" multiplied completions (×2 or ×3): **~25%** of all draws
- Negative outcomes (Int + Dropped Int): **~2%**

---

## 7. Z_RES — Z Result (Injury, Penalty, Fumble)

The Z_RES field appears on every card but is **only consulted on non-Z cards when
the specific game situation calls for it** (e.g., some play outcomes require a Z_RES
check). On Z cards themselves, Z_RES reads "Follow 3-rules for Z" and the Z resolution
rules apply instead.

### Type summary (96 non-Z cards)

| Type | Count | % |
|------|-------|---|
| INJURY | 43 | 44.8% |
| PENALTY | 37 | 38.5% |
| FUMBLE | 10 | 10.4% |
| DOWN_BY_CONTACT | 5 | 5.2% |
| NO_INJURY | 1 | 1.0% |

### Injury targets (INJURY + NO_INJURY events = 44)

| Target Code | Count | Position |
|-------------|-------|---------|
| BC | 9 | Ball Carrier |
| A–E | 2 each | Defensive Box (DL) |
| F–J | various | Defensive Box (LB) |
| K–O | various | Defensive Box (DB) |
| LT, LG, LE, RT, RG, RE, CN | 2 each | Offensive linemen |
| QB | 1 | Quarterback |
| N, O | 1 each | Defensive DB boxes |

Full breakdown:

| Code | Count | Code | Count |
|------|-------|------|-------|
| BC (Ball Carrier) | 9 | RT | 2 |
| LT | 2 | RE | 2 |
| LG | 2 | CN | 2 |
| LE | 2 | RG | 2 |
| A | 2 | B | 2 |
| C | 2 | D | 2 |
| E | 2 | G | 1 |
| F | 1 | H | 1 |
| I | 1 | J | 1 |
| K | 1 | L | 1 |
| M | 1 | N | 1 |
| O | 1 | QB | 1 |
| No Inj: BC | 1 | | |

### Fumble events (10 total)

Six cards show `Fumble`; four show `Fumble(s)` (a fumble where recovery is still
decided by chart). Both trigger the fumble-recovery procedure.

### Down By Contact (5 total)

The runner is down by contact — no fumble, no injury. Play ends normally.

### Penalties (37 total)

Each penalty entry encodes four situation-dependent outcomes in the format:
`1.<code> /2.<code> /3.<code> /4.<code>`

where situations correspond to specific game scenarios (down, field position, etc.).

**Penalty code key:**
- `D<n>` — Defensive penalty, n yards
- `O<n>` — Offensive penalty, n yards
- `R<n>` — Replay (re-run the down) at a specific run-number lookup
- `K<n>` — Kicking situation result (down/distance code)

#### Situation 1 penalty codes (37 penalty cards)

| Code | Count | Code | Count |
|------|-------|------|-------|
| O1 | 9 | D1 | 8 |
| D2 | 3 | O2 | 3 |
| D5 | 2 | O5 | 2 |
| O3 | 2 | O7 | 2 |
| D7 | 2 | D9 | 1 |
| O14 | 1 | O4 | 1 |
| O6 | 1 | | |

#### Situation 2 penalty codes

| Code | Count | Code | Count |
|------|-------|------|-------|
| O1 | 7 | O7 | 7 |
| D1 | 6 | D8 | 3 |
| D2 | 2 | O2 | 2 |
| D7 | 2 | O3 | 1 |
| O8 | 1 | D5 | 1 |
| O5 | 1 | D9 | 1 |
| O14 | 1 | O4 | 1 |
| O10 | 1 | | |

#### Situation 3 penalty codes

| Code | Count | Code | Count |
|------|-------|------|-------|
| R11 | 13 | R1 | 5 |
| K1 | 5 | R13 | 4 |
| K9 | 4 | R5 | 2 |
| K5 | 2 | R12 | 1 |
| K14 | 1 | | |

#### Situation 4 penalty codes

| Code | Count | Code | Count |
|------|-------|------|-------|
| R11 | 22 | K9 | 5 |
| K15 | 3 | K1 | 2 |
| R5 | 2 | K5 | 2 |
| R1 | 1 | | |

---

## 8. SOLO — Solitaire Play Calling

The SOLO field provides a 5-situation defensive play sequence used when playing
solitaire (one player controls one team; the AI controls the other). Each card encodes
5 numbered situations, e.g. `1.R(NK)/2.P/3.BLZ/4.PR(x2)/5.R(BC)`.

### Play code key

| Code | Meaning |
|------|---------|
| `R(NK)` | Run — No Key |
| `R(BC)` | Run — Key Ball Carrier |
| `P` | Pass Defense |
| `P(x2)` | Pass Defense × 2 (double coverage) |
| `PR` | Pass Rush |
| `PR(x2)` | Pass Rush × 2 (extra rushers) |
| `BLZ` | Blitz |

### Distribution across all 5 situations (96 non-Z cards × 5 situations = 480 entries)

| Code | Count | % |
|------|-------|---|
| `R(NK)` | 200 | 41.7% |
| `P` | 75 | 15.6% |
| `PR` | 66 | 13.8% |
| `R(BC)` | 54 | 11.3% |
| `PR(x2)` | 30 | 6.2% |
| `BLZ` | 30 | 6.2% |
| `P(x2)` | 25 | 5.2% |

**Observations:** The solitaire AI runs a No-Key run defense most often (~42%), with
pass defense second (~21% combining P and P×2). Aggressive calls (Blitz + Press Rush
variants) account for ~25% combined.

---

## Summary Table

| Field | Non-Z base | Most common value | Notes |
|-------|-----------|-------------------|-------|
| RN | 96 | 5 (12.5%) | 25% of non-Z cards have OB suffix |
| PASS# | 96 | Flat — each 1–48 appears exactly twice | 2.08% each |
| SL | 96 | 7 values tied at 8 (8.3%) | Mirrors SR |
| IL | 96 | LG (10.4%) | Mirrors IR |
| SR | 96 | 7 values tied at 8 (8.3%) | Mirrors SL |
| IR | 96 | RG (11.5%) | Mirrors IL |
| ER | 96 | OK (50%) | 8 cards each for −1 through −6 |
| QK | 96 | Orig (41.7%) | P.Rush only 2.1% |
| SH | 96 | Orig (41.7%) | P.Rush 8.3% |
| LG | 96 | Orig (41.7%) | P.Rush 14.6% |
| SC | 96 | Com (51.0%) | ~76% completion rate |
| Z_RES type | 96 | INJURY (44.8%) | 38.5% penalty, 10.4% fumble |
| SOLO | 480 slots | R(NK) (41.7%) | AI defensive play calls |

---

*Data source: `engine/fac_deck.py` — BJY FAC flipper canonical 5th-edition deck.*
