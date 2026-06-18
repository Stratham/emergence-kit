# Core procedures (system-neutral)

Reference the DM uses to adjudicate play consistently, independent of the chosen
ruleset. The specific numbers come from the system module; the *procedures* here
are universal. All randomness routes through the tools (`roll_dice`,
`roll_check`).

## When to call for a roll
Roll only when **all three** are true:
1. The outcome is **uncertain**.
2. **Both** success and failure are **interesting**.
3. There is a **meaningful stake**.

Otherwise narrate the result directly:
- Trivial task, competent character, no pressure → **success, no roll**.
- Impossible task → **failure, no roll** (offer a different approach).

## The adjudication loop
1. Player states a goal and an approach ("I want X by doing Y").
2. DM identifies the relevant ability/skill and sets a **DC** from the system's
   difficulty ladder based on fictional difficulty.
3. DM decides advantage/disadvantage from circumstances (good plan, right tools,
   help, leverage → advantage; bad position, distraction, poor tools →
   disadvantage).
4. `roll_check(modifier, dc, advantage)` → read success and margin.
5. Narrate, applying degrees of success.

## Setting a DC
Anchor to the ladder in the system module (e.g. easy / medium / hard / very
hard). Heuristics: most adventuring tasks are *medium*; raise for poor conditions,
haste, or strong opposition; lower for clever preparation or ideal conditions.
Set the DC **before** the roll and don't fudge it after.

## Degrees of success (fail forward)
Use the margin from `roll_check` to color the outcome:
- **Critical success** (natural max / beat by a wide margin): full success plus a
  bonus or extra information.
- **Success**: the goal is achieved.
- **Success at a cost / partial**: barely makes it — achieved with a complication,
  resource spent, or new danger.
- **Failure**: the goal isn't met *and the situation changes* — a clock advances,
  a new threat appears, an opportunity closes. Never a dead end; always a new
  branch.
- **Critical failure** (natural min / miss by a wide margin): failure plus a
  serious complication.

## The three pillars
Vary the spotlight across:
- **Exploration** — describe spaces, telegraph dangers and points of interest,
  reward curiosity and careful play; use checks for perception, navigation,
  survival.
- **Social** — NPCs have goals and attitudes; roleplay first, roll to resolve
  uncertain persuasion/deception/insight. A good argument can lower the DC or
  grant advantage.
- **Combat** — see below.

## Combat procedure
1. `encounter_start("...")`.
2. `combatant_add` every participant; pass `hp`, `ac`, and `init_mod` (omit
   `initiative` to auto-roll).
3. `turn_next` to advance through initiative order, round by round.
4. On a turn: describe the situation → ask the active character's action →
   resolve attacks with `roll_check(modifier=attack_bonus, dc=target_AC)` →
   on a hit, `roll_dice("<damage>")` then `apply_damage(target, amount)` →
   apply status via `condition_add`.
5. Track HP only through tools. At 0 HP, apply the module's down/dying rule.
6. `encounter_end` when resolved; award advancement per the module.

## Time, resources, and clocks
- Track meaningful time with `var_set` (`day`, `turns_until_X`). Advance "clocks"
  on failures and significant actions to create momentum.
- Track consumables in `inventory`; resource pressure makes choices matter.

## Rulings over rules
If the system module doesn't cover a situation: make the most fun, fair ruling
quickly, say it out loud, and apply it consistently for the rest of the campaign
(record lasting rulings with `var_set`).
