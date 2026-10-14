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
- [ ] [S6] Finish full-upgrade, reboot, verify — waiting: Ofir · added 2026-10-14
  - fixes stuck NVIDIA driver; after reboot Claude checks nvidia-smi, bots, Wi-Fi errors
- [ ] [S7] Upgrade Ubuntu to 26.04 LTS — waiting: Ofir · added 2026-10-14
  - backups ready: `~/pre-upgrade-2026-10-14` + Drive copy
  - run `sudo do-release-upgrade` at the laptop; then rebuild bot venvs

## Home Assistant
- [ ] [H1] Check Shabbat flow first live run — waiting: Claude · added 2026-10-12
  - Fri 2026-10-16: ask 13:51, decide 17:06
- [ ] [H2] Ack-button test results — waiting: external · added 2026-10-12
  - resent 10-13 to Yossi, Orly, Elior; you get a ✅ per press; then delete `test_notify_ack`
  - Yossi's app can't reach HA from outside (error on press); fix with his phone in hand
- [ ] [H4] Elior re-login to stop HA bans — waiting: external · added 2026-10-12
  - her app uses the deactivated user `elior`; log out, log in as `eliori`
  - then Claude deletes user `elior` (on Ofir's go)
- [ ] [H5] Remote-access restrictions — waiting: Ofir · added 2026-10-12
  - after family trial; reminder fires 2026-11-08, then delete the reminder
- [ ] [H6] Clean AC filters — waiting: Ofir · added 2026-10-12
  - units 101, 102, 105, 106, 108, 109, then press reset_filter
- [ ] [H7] Test Welcome flow + AC control — waiting: Ofir · added 2026-10-12
- [ ] [H8] Name phones in network list — waiting: Ofir · added 2026-10-12
- [ ] [H9] Optional: revoke old HA token — waiting: Ofir · added 2026-10-12
  - `~/.ha_token.ofir_old`
- [ ] [H11] Fix presence, then restore who's-home badges — waiting: Claude · added 2026-10-13
  - removed from dashboard 10-13; backup home-main-before-remove-whos-home-2026-10-13.json
- [ ] [H12] Integrate Dahua cameras (ONVIF) — waiting: Ofir · added 2026-10-13
  - NVR at 10.0.0.5; need username/password, camera count, who can see them

## Bots
- [ ] [B1] Voice messages in Claude bot — waiting: Ofir · added 2026-10-13
  - Groq Whisper; needs decision + API key

## Projects
- [ ] [P1] Review snnio local changes — waiting: Ofir · added 2026-10-13
  - `.gitignore`, `openvins/`, `run_euroc_serial.cpp` in the external repo
- [ ] [P2] Find VIO co-founder — waiting: Ofir · added 2026-10-13
  - ML/SNN/VIO algorithms person for the VIO accelerator

## Done
- [x] Dashboard icons fixed (areas, boilers/heaters, alert badge names) — 2026-10-13
- [x] [H10] Deleted old phone registrations (S901E, F936B, old S928B) — 2026-10-13
- [x] [H3] Yossi uses SM-S928B; dead SM-F936B dropped from Shabbat + person — 2026-10-13
- [x] [B2] Bot formatting and session rollover confirmed OK — 2026-10-13
- [x] Directory cleanup: duplicates in `~/ofir` removed, sandbox merged and pushed, 4 skills installed — 2026-10-13
- [x] Master task list + /tasks + weekly review — 2026-10-13
