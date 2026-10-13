# Master task list

One place for every open task. Claude reads this before task-related requests and
updates it (plus a git commit) whenever a task is added, progressed or closed.

Format: `- [ ] [ID] Short title — waiting: Ofir|Claude|external · added YYYY-MM-DD`
Keep titles short (~6 words); details go on indented `  - ` lines below the task.
IDs: section letter + number (S=Home server, H=Home Assistant, B=Bots, P=Projects).
A new task gets the next unused number in its section; IDs are never reused or
renumbered. Closed tasks move to **Done** (keeping their ID) with their close date. Detailed HA history stays in
`~/ha-backups/HA-TODO.md` (its open `- [ ]` items are counted by `/tasks`).

## Home server
- [ ] [S1] Install replacement battery — waiting: external · added 2026-10-11
  - C21N1509, in shipment; after install check real capacity with upower
- [ ] [S2] ESP32 power-button servo — waiting: Ofir · added 2026-10-11
  - BotFather bot, fill in sketch, flash, mount, calibrate (see HOME_SERVER_TODO.md)
- [ ] [S3] Router on a small UPS — waiting: Ofir · added 2026-10-11
- [ ] [S4] Router DHCP reservations — waiting: Ofir · added 2026-10-11
  - laptop → 192.168.0.108; CoolMaster MAC 28:3B:96:03:0A:E3 → 10.0.0.17
- [ ] [S5] Second computer as server — waiting: Ofir · added 2026-10-13
  - Ofir sends specs (desktop/laptop, CPU, RAM, GPU, OS), then Claude writes the plan

## Home Assistant
- [ ] [H1] Check Shabbat flow first live run — waiting: Claude · added 2026-10-12
  - Fri 2026-10-16: ask 13:51, decide 17:06
- [ ] [H2] Ack-button test results — waiting: external · added 2026-10-12
  - resent 10-13 to Yossi, Orly, Elior; you get a ✅ per press; then delete `test_notify_ack`
- [ ] [H4] Find the iPhone causing HA bans — waiting: Ofir · added 2026-10-12
  - still failing 10-13 20:55 from cellular; likely Shaked or Idan (phones silent since 10-12)
  - fix: log out/in in the HA app; Yossi now connects OK
- [ ] [H5] Remote-access restrictions — waiting: Ofir · added 2026-10-12
  - after family trial; reminder fires 2026-11-08, then delete the reminder
- [ ] [H6] Clean AC filters — waiting: Ofir · added 2026-10-12
  - units 101, 102, 105, 106, 108, 109, then press reset_filter
- [ ] [H7] Test Welcome flow + AC control — waiting: Ofir · added 2026-10-12
- [ ] [H8] Name phones in network list — waiting: Ofir · added 2026-10-12
- [ ] [H9] Optional: revoke old HA token — waiting: Ofir · added 2026-10-12
  - `~/.ha_token.ofir_old`

## Bots
- [ ] [B1] Voice messages in Claude bot — waiting: Ofir · added 2026-10-13
  - Groq Whisper; needs decision + API key

## Projects
- [ ] [P1] Review snnio local changes — waiting: Ofir · added 2026-10-13
  - `.gitignore`, `openvins/`, `run_euroc_serial.cpp` in the external repo
- [ ] [P2] Find VIO co-founder — waiting: Ofir · added 2026-10-13
  - ML/SNN/VIO algorithms person for the VIO accelerator

## Done
- [x] [H10] Deleted old phone registrations (S901E, F936B, old S928B) — 2026-10-13
- [x] [H3] Yossi uses SM-S928B; dead SM-F936B dropped from Shabbat + person — 2026-10-13
- [x] [B2] Bot formatting and session rollover confirmed OK — 2026-10-13
- [x] Directory cleanup: duplicates in `~/ofir` removed, sandbox merged and pushed, 4 skills installed — 2026-10-13
- [x] Master task list + /tasks + weekly review — 2026-10-13
