# Master task list

One place for every open task. Claude reads this before task-related requests and
updates it (plus a git commit) whenever a task is added, progressed or closed.

Format: `- [ ] [ID] Title — waiting: Ofir|Claude|external · added YYYY-MM-DD`
IDs: section letter + number (S=Home server, H=Home Assistant, B=Bots, P=Projects).
A new task gets the next unused number in its section; IDs are never reused or
renumbered. Closed tasks move to **Done** (keeping their ID) with their close date. Detailed HA history stays in
`~/ha-backups/HA-TODO.md` (its open `- [ ]` items are counted by `/tasks`).

## Home server
- [ ] [S1] Install replacement battery (C21N1509, in shipment) and check real capacity — waiting: external · added 2026-10-11
- [ ] [S2] ESP32 power-button servo: BotFather bot, fill in sketch, flash, mount, calibrate — waiting: Ofir · added 2026-10-11
- [ ] [S3] Put the router on a small UPS — waiting: Ofir · added 2026-10-11
- [ ] [S4] Router DHCP reservations: laptop → 192.168.0.108, CoolMaster MAC 28:3B:96:03:0A:E3 → 10.0.0.17 — waiting: Ofir · added 2026-10-11
- [ ] [S5] Second home computer as server/worker: Ofir sends specs (desktop/laptop, CPU, RAM, GPU, OS), Claude writes the plan — waiting: Ofir · added 2026-10-13

## Home Assistant
- [ ] [H1] Shabbat "who's home" flow: check the first live run (Fri 2026-10-16, ask 13:51, decide 17:06) — waiting: Claude · added 2026-10-12
- [ ] [H2] Ack-button test: report who confirmed, then delete `test_notify_ack` — waiting: Ofir · added 2026-10-12
- [ ] [H3] Find which Samsung Yossi uses; drop the other from shabbat_ask / shabbat_vacation_end — waiting: Ofir · added 2026-10-12
- [ ] [H4] Find the iPhone failing /auth/token (caused the router-IP ban); log out/in, set internal URL; confirm Yossi connects — waiting: Ofir · added 2026-10-12
- [ ] [H5] Remote-access restrictions after family trial (reminder fires 2026-11-08), then delete the reminder — waiting: Ofir · added 2026-10-12
- [ ] [H6] Clean AC filters 101, 102, 105, 106, 108, 109, then press reset_filter — waiting: Ofir · added 2026-10-12
- [ ] [H7] Test Welcome flow and AC control — waiting: Ofir · added 2026-10-12
- [ ] [H8] Name the phones in the network list — waiting: Ofir · added 2026-10-12
- [ ] [H9] Optional: revoke Ofir's old HA token (`~/.ha_token.ofir_old`) — waiting: Ofir · added 2026-10-12

## Bots
- [ ] [B1] Voice messages in the Claude bot (Groq Whisper) — waiting: Ofir (decision + API key) · added 2026-10-13
- [ ] [B2] Confirm bot formatting and session rollover work well — waiting: Ofir · added 2026-10-12

## Projects
- [ ] [P1] snnio: review local diffs (`.gitignore`, `openvins/`, `run_euroc_serial.cpp` in external repo) — waiting: Ofir · added 2026-10-13
- [ ] [P2] VIO accelerator: find an ML/SNN/VIO algorithms co-founder — waiting: Ofir · added 2026-10-13

## Done
- [x] Directory cleanup: duplicates in `~/ofir` removed, sandbox merged and pushed, 4 skills installed — 2026-10-13
- [x] Master task list + /tasks + weekly review — 2026-10-13
