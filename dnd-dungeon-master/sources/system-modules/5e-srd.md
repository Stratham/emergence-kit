# System Module: D&D 5e (SRD)

A ready-to-use module for fifth-edition-style d20 fantasy, based on mechanics from
the **System Reference Document (SRD)**, which Wizards of the Coast publishes under
the **Creative Commons Attribution 4.0 (CC-BY-4.0)** license. This file
paraphrases the core resolution rules; it is not a full rulebook. For complete
rules, monsters, and spells, consult the SRD itself (see Attribution).

---

## Adapter

```
SYSTEM NAME: D&D 5e (SRD)

RESOLUTION DIE: 1d20
CHECK FORMULA: 1d20 + ability modifier (+ proficiency if proficient) vs DC
  → roll_check(modifier=<abilmod + prof?>, dc=<target>, die="1d20")

DIFFICULTY LADDER (typical DCs):
  very easy 5  easy 10  medium 15  hard 20  very hard 25  nearly impossible 30

SUCCESS RULE: total >= DC succeeds
DEGREES OF SUCCESS: pass/fail; use margin for narration (DM discretion)
CRITICALS (attacks): natural 20 = automatic hit + double damage dice;
                     natural 1 = automatic miss
ADVANTAGE/DISADVANTAGE: yes — roll 2d20, keep higher/lower (advantage = 1 / -1)

ABILITY/STAT KEYS: str, dex, con, int, wis, cha   (store ability MODIFIERS in stats)
SKILLS: acrobatics, animal_handling, arcana, athletics, deception, history,
        insight, intimidation, investigation, medicine, nature, perception,
        performance, persuasion, religion, sleight_of_hand, stealth, survival

HIT POINTS: per class & Constitution; track current/max
0 HP MEANS: a player character falls unconscious and makes death saving throws
            (roll_check die="1d20", dc=10; 3 successes stabilize, 3 failures = death;
            nat 20 = regain 1 HP, nat 1 = two failures). Most monsters simply die.
DEFENSE VALUE (attack DC): Armor Class (AC) — an attack roll must meet or beat it
DAMAGE: by weapon/spell, e.g. shortsword 1d6 + Str/Dex mod; longbow 1d8 + Dex;
        roll via roll_dice("1d6+3"); crit doubles the dice (roll_dice("2d6+3"))
HEALING / REST: short rest spends Hit Dice; a long rest restores all HP

INITIATIVE: 1d20 + Dex modifier  → combatant_add ... --init-mod <Dex mod>
TURN STRUCTURE: move up to speed + one action (Attack, Cast a Spell, Dash, Dodge,
                Disengage, Help, Hide, Ready, Search, Use an Object) + possible
                bonus action + one reaction per round

CONDITIONS: blinded, charmed, deafened, exhaustion, frightened, grappled,
            incapacitated, invisible, paralyzed, petrified, poisoned, prone,
            restrained, stunned, unconscious

ADVANCEMENT: XP or milestone leveling (DM choice); higher level = more HP,
             proficiency bonus, and class features

NOTABLE SUBSYSTEMS: spellcasting (spell slots, save DC = 8 + prof + casting mod;
            spell attacks use roll_check vs target AC), resting, exhaustion track
```

## Saving throws
A save is `roll_check(modifier=<ability mod + prof if proficient>, dc=<effect DC>,
die="1d20")` against the effect's DC (often a spell save DC = 8 + proficiency +
caster's spellcasting modifier).

## Ability modifier reference
A score's modifier = (score − 10) ÷ 2, rounded down. Store the **modifier** in a
character's `stats` for direct use with `roll_check`.
| score | 8 | 10 | 12 | 14 | 16 | 18 | 20 |
|------|----|----|----|----|----|----|----|
| mod  | −1 | 0  | +1 | +2 | +3 | +4 | +5 |

## Proficiency bonus by level
Levels 1–4: +2 · 5–8: +3 · 9–12: +4 · 13–16: +5 · 17–20: +6.
Add it to checks/attacks/saves the character is proficient in.

## Quick play notes
- Default DC for an everyday adventuring task is **15 (medium)**.
- Attacks: `roll_check(modifier=attack_bonus, dc=target_AC)`; on a hit,
  `roll_dice("<weapon damage>")` then `apply_damage`.
- Apply status effects with the condition names listed above.

## Attribution
This module paraphrases mechanics from the *System Reference Document* by Wizards
of the Coast LLC, licensed under **Creative Commons Attribution 4.0 International
(CC-BY-4.0)**. "Dungeons & Dragons" and "D&D" are trademarks of Wizards of the
Coast; this kit is unofficial and not affiliated with or endorsed by them. Get the
SRD at https://www.dndbeyond.com/srd.
