# Poor Man's Beier — Firmware for the DIYGuy999 ESP32 Sound Board

> ⚠️ **Public beta.** Most things work, but some features are still
> bench-tested only. Expect rough edges, please open issues when you find
> them.

### ⚡ [Flash it now in your browser - no downloads](https://turbotike.github.io/poor-mans-beier-firmware-for-the-diyguy-999-board-/)

A free, one-click ESP32 firmware + web flasher that turns
**TheDIYGuy999's RC_Engine_Sound_ESP32 board (v1.2, unmodified)** into a
full-feature RC semi-truck controller — engine sounds, lights, ESC, steering,
horns, gear change, reverse beep, air-brake hiss, and a phone/tablet web UI
for tuning, all running on a single ESP32.

> Inspired by the Beier Sound Module experience, built for everyone who
> doesn't want to spend $300 on one.

---

## Highlights

- **Two engines included**: Caterpillar **C15** and Detroit **8V92**.
- **Three RC protocols**: standard **PWM** (uses up to **6 channels** from the
  board's header strip), **FlySky iBUS**, **FrSky SBUS**.
  > Heads-up: only PWM has been bench-tested so far. iBUS and SBUS variants
  > are built and should work, but if you hit issues open an issue on GitHub
  > and I'll help dial them in.
- **Realistic, time-based engine state machine** — accel and decel layers play
  out on real timers, not just throttle position. Punch the throttle and you
  hear a full `idle → accel1 → accel2 → cruise` climb; let off and the engine
  actually *coasts down* through `decel1 → decel2 → idle` over a couple
  seconds, just like a real diesel falling off boost. Re-accel mid-decel
  resumes at the correct layer (high-speed lift = high-speed re-engage,
  low-speed lift = low-speed re-engage). Plus park-gear free-rev, reverse
  beep, and air-brake hiss with arm/fire hysteresis + cooldown.
- **Web UI** over the ESP32's own Wi-Fi AP — connect from any phone/tablet,
  no app needed. Tune volumes, crossfades, throttle thresholds, lights, and
  steering trim live.
- **One-click flasher** — pick engine + protocol, click **Flash**, done.
  Pure Python stdlib, no extra installs beyond Python and esptool.
- **Six pre-built variants** ship in this repo so non-developers never have
  to touch a compiler.

---

## What's in this repo

```
flasher/
  flasher_server.py           web UI + flash backend (Python stdlib + esptool)
  Launch_Flasher.bat          Windows launcher (opens browser automatically)
  Launch_Flasher_silent.vbs   no-console launcher
  firmware/
    manifest.json             variant + offset table
    bootloader.bin
    partitions.bin
    c15_pwm.bin    c15_ibus.bin    c15_sbus.bin
    8v92_pwm.bin   8v92_ibus.bin   8v92_sbus.bin
HOW_TO.md                     full step-by-step guide (start here if new)
README.md                     this file
```

---

## Quick start (flash an ESP32)

**Easiest — web flasher, no downloads:**
Open <https://turbotike.github.io/poor-mans-beier-firmware-for-the-diyguy-999-board-/>
in Chrome or Edge on a desktop, plug in the ESP32, click **Install**. Done.

**Or run the local flasher app:**

1. Download or `git clone` this repo.
2. Plug the ESP32 sound board into your PC over USB **with the truck battery
   disconnected** (USB power only while flashing).
3. Double-click **`flasher/Launch_Flasher.bat`** (Windows).
   On macOS/Linux, run `python3 flasher/flasher_server.py`.
4. Your browser opens to <http://localhost:8765>.
5. Pick **engine** (C15 or 8V92), **protocol** (PWM / iBUS / SBUS), and the
   **COM port** the ESP32 enumerated as.
6. Click **Flash firmware**. Watch the progress bar.
7. When it says "Hard resetting via RTS pin", you're done.
8. Power-cycle the board. The ESP32 boots, brings up Wi-Fi AP
   **`RC_SemiTruck`** (password **`truckin123`**), and starts driving.

For full wiring, RC binding, and tuning instructions, see **[HOW_TO.md](HOW_TO.md)**.

---

## Connecting to the truck's web UI

After first boot:

1. On a phone/tablet, join Wi-Fi network **`RC_SemiTruck`**, password
   **`truckin123`**.
2. Open <http://192.168.4.1> in any browser.
3. The dashboard shows live RC channel values, engine state, and gives you
   sliders for every volume, crossfade time, throttle threshold, and light
   timing. Hit **Save** to persist to NVS.

---

## Hardware

- **Board**: TheDIYGuy999 *RC_Engine_Sound_ESP32* v1.2 (standard, unmodified).
- **Power**: 2S–3S LiPo into the board's BEC, or USB while flashing.
- **Receiver**:
  - **PWM**: up to **6 servo wires** from RX to CH1–CH6 headers on the board
    (throttle, steering, gear/3-pos, horn, lights, aux).
  - **iBUS**: single signal wire to RX1 (GPIO16). FlySky FS-iA6B etc. *(untested)*
  - **SBUS**: single inverted signal wire to RX1. FrSky / Futaba. *(untested)*
- **ESC + steering**: two servo outputs from the board.
- **Lights**: 13 LED channels via the on-board MOSFETs.

Detailed pin map and channel assignments are in [HOW_TO.md](HOW_TO.md).

---

## Building from source

You only need this if you want to add a new engine sound, add a new RC
protocol, or hack the firmware.

1. Install [VS Code](https://code.visualstudio.com/) and the
   [PlatformIO IDE](https://platformio.org/install/ide?install=vscode) extension.
2. Open the firmware project folder (the parent of `flasher/`).
3. Build a single variant: `pio run -e esp32dev`.
4. Build all six flasher variants: `./tools/build_all_variants.ps1`.
   This regenerates every `*.bin` in `flasher/firmware/` and refreshes
   `manifest.json`.

Adding a new engine sound: drop a new sound pack under
`tools/sound_packs/<name>/` matching the layout of `c15/` or `8v92/`, then
add it to `build_all_variants.ps1`.

---

## Credits

- **TheDIYGuy999** — the original RC_Engine_Sound_ESP32 board, sound assets,
  and the entire RC engine-sound community foundation this builds on.
- **Beier Sound Module** — the gold standard this firmware tries to chase.

---

## License

MIT. See [LICENSE](LICENSE) if present, otherwise treat as MIT.
