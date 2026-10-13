# Home server TODO (ASUS X556UQK laptop)

_Last updated: 2026-10-11 (late)_

## Power / uptime

Diagnosis: not a settings issue. Battery is worn out: 5.6 Wh of 38 Wh design (~15% health), 394 cycles.
On the Oct 9 08:52 outage the journal just stops — the battery didn't carry the load for even a second.

- [ ] Buy and install replacement battery **ASUS C21N1509** (7.6 V, 38 Wh, 2-cell, internal)
  - Chosen: SKOWER C21N1509 on AliExpress, ~₪62 (item 1005009244981431) — lists X556UQK, 7.6 V / 38 Wh
  - "Original" ones run ~€28–38 but are unverifiable; not worth it for an always-plugged server
  - After install: check real capacity with `upower -i $(upower -e | grep BAT)`
  - Not A41-X550A (that's the older 14.4 V external pack)
  - Bottom cover screws (some under the DVD drive) -> unplug battery connector first
- [ ] Put the router on a small UPS (server is useless during an outage if the router is down)
- [ ] Reserve 192.168.0.108 for the laptop in the router's DHCP settings
- [ ] Check BIOS (F2) for any "Power On By AC" / "Restore on AC Power Loss" option (unlikely on this model)
- [x] Charge limit at 80% — **not possible**: firmware does not expose `charge_control_end_threshold`
- [x] `loginctl enable-linger` — user services (bots) now start at boot without a login session

## ESP32 power-button pusher

Firmware: `esp32_power_button/esp32_power_button.ino` (Telegram-controlled, servo on GPIO 13).
Written but not yet compiled or tested on hardware.

- [ ] Create a dedicated bot in @BotFather for it; get chat ID from @userinfobot
- [ ] Fill in Wi-Fi / token / chat ID in the sketch
- [ ] Install libs: UniversalTelegramBot, ArduinoJson, ESP32Servo; board "ESP32 Dev Module"
- [ ] Compile + flash, wire servo (signal GPIO 13, 5V/VIN, GND)
- [ ] Mount servo over the power key (top-right of keyboard), tune angles with `/calibrate`
- [ ] Test: `/status`, `/on` with laptop off, and confirm the boot-up "online" message after unplugging the ESP32

## Telegram bots security

Tokens for all 3 bots (claude, pregnancy, fitness) were logged in plain text by httpx at INFO level.

- [x] Silenced httpx logging (`logging.getLogger("httpx").setLevel(logging.WARNING)`) in all 3 bots, restarted
- [x] Scrubbed token lines from `/tmp/telegram-*.log`
- [x] Verified tokens were never committed to git
- [x] Option C implemented (secrets in `~/.config/credstore`, systemd `LoadCredential=`, clean env for Claude, deny rules)
- [x] Revoked all 3 tokens in @BotFather
- [x] New tokens written to `~/.config/credstore/`, services restarted and verified
  - Note: after changing any token, run `systemctl --user restart telegram-claude telegram-pregnancy-bot fitness-bot`
- [x] Garmin password changed and stored in credstore
  - `garmin-tokens/` (cached OAuth login) survives password changes; sync verified working
- [x] Wiped the old system journal (contained the revoked tokens)
- [x] Committed `telegram_claude/` and pushed to GitHub (`d9e987d` on master)

### Secret storage (option C, done 2026-10-11)
- Secrets: `~/.config/credstore/` (dir 700, files 600) — outside the repo and outside every Claude working dir
  - `telegram-claude-token`, `telegram-pregnancy-token`, `telegram-fitness-token`, `garmin-password`, `garmin-tokens/`
- systemd units (`~/.config/systemd/user/*.service`) pass them with `LoadCredential=`; bots read them via `secret_store.get_secret()`
- `.env*` files hold only non-secret config
- Claude subprocesses run with `env=child_env()` (allowlist: HOME, PATH, LANG, ...) — no secrets inherited
- `~/.claude/settings.json` deny rules block Claude from reading credstore / `/run/user/*/credentials`
  (defense in depth only — Claude runs as the same Linux user)
