# RC LARGECARS — Firmware for the DIYGuy999 ESP32 Sound Board

> 🤖 **Vibe coded.** This entire project — firmware, flasher, web tools, and
> sound packs — was built by vibe coding with AI. Built for fun, tuned by ear.

> ⚠️ **Public beta.** Most things work, but some features are still
> bench-tested only. Expect rough edges — please open an issue when you hit one.

### ⚡ [Flash it now in your browser — no downloads](https://turbotike.github.io/poor-mans-beier-firmware-for-the-diyguy-999-board-/)

A free, one-click ESP32 firmware + web flasher that turns
**TheDIYGuy999's RC_Engine_Sound_ESP32 board (v1.2, unmodified)** into a
full-feature RC semi-truck controller — realistic engine sounds, lights, ESC,
steering, horns, gear change, reverse beep, air-brake hiss, air-dryer purge, and
a phone/tablet web UI for tuning, all running on a single ESP32.

> Inspired by the Beier Sound Module experience — built for everyone who
> doesn't want to spend $300 on one.

---

## Highlights

- **Four engines included**: Caterpillar **C15**, Detroit **8V92**,
  Cummins **N14**, and Volvo **FH12** — twelve ready-to-flash builds in total.
- **FH12 does two things differently.** Its decel voice is the jake brake,
  looped for as long as you are off the throttle and pitched by engine rpm, so
  it steps back up at every downshift instead of sliding down one long glide.
  And it carries no free-rev recording at all — blipping in neutral raises the
  pitch of the idle loop and lets it settle back, which also makes the blip
  proportional to how far you move the stick.
- **Three RC protocols**: standard **PWM** (up to **6 channels** off the board's
  header strip), **FlySky iBUS**, and **FrSky/Futaba SBUS**.
  > PWM and iBUS are tested on real hardware. SBUS is built and should work but
  > hasn't been on a truck yet — open an issue if you run it and hit snags.
- **Realistic, time-based engine state machine** — accel layers play out on
  real timers, not just throttle position. Punch the throttle and you climb
  `idle → accel1 → accel2 → cruise`. Plus park free-rev, reverse beep,
  gear-change clunk, park-brake air release, air-brake hiss, and a random
  air-dryer purge.
- **The jake brake is the decel voice.** Every pack ships this way, because it
  is what you actually hear from a truck lifting off. It is not a one-shot: the
  braap **loops** while you are off the throttle, engages like a clutch rather
  than a switch, and its chop follows **engine rpm, not road speed** — so it
  steps back up at every downshift instead of sliding down one long glide. Each
  pack carries its own native rpm (C15 1950, 8V92 1800, N14 and FH12 to suit),
  because a Cat inline-six and a two-stroke Detroit chop at completely
  different rates for the same road speed.
- **FH12 has no free-rev recording and does not need one** — blipping in
  neutral raises the pitch of the idle loop and lets it settle back, which is
  the same sound going faster, and makes the blip proportional to the stick
  instead of on/off.
- **Reassign what each channel does** (FH12 builds) — throttle, steering,
  engine, horn, gear and lights each take a channel number instead of being
  fixed. iBUS/SBUS only; PWM wires each role to its own pin. See
  [CHANNELS.md](CHANNELS.md).
- **Loud and clean** — every sound pack is mastered for a consistent, punchy
  level, and the firmware runs a master soft-saturation stage so you can crank
  it to cut through a closed truck body without harsh clipping.
- **Fully tunable from the web UI** — every volume, crossfade time, throttle
  threshold, ESC/brake curve, light brightness, and steering trim is a live
  slider. Saved to NVS, no reflashing needed.
- **90s neon web UI** over the ESP32's own Wi-Fi AP — connect from any
  phone/tablet, no app required.
- **One-click flashing** — flash straight from the browser, or run the included
  pure-Python local flasher. **Twelve** pre-built variants ship in this repo
  (four engines x three protocols) so non-developers never touch a compiler.
- **In-browser sound-pack builder** — drag in WAVs, get a ready-to-use pack.

---

## What's in this repo

```
flasher_server.py             local web UI + flash backend (Python stdlib + esptool)
Launch_Flasher.bat            Windows launcher (opens browser automatically)
Launch_Flasher_silent.vbs     no-console launcher
firmware/
  manifest.json               variant + offset table
  bootloader.bin
  partitions.bin
  c15_pwm.bin   c15_ibus.bin   c15_sbus.bin
  8v92_pwm.bin  8v92_ibus.bin  8v92_sbus.bin
  n14_pwm.bin   n14_ibus.bin   n14_sbus.bin
  fh12_pwm.bin  fh12_ibus.bin  fh12_sbus.bin
docs/                         GitHub Pages site (web flasher + sound-pack builder)
tools/                        helper scripts (web manifest generation)
HOW_TO.md                     flashing + first-time setup, step by step
USER_MANUAL.md                full operating manual (driving, wiring, web UI, trailer)
CHANNELS.md                   what each RC channel does, and how to reassign it
README.md                     this file
```

---

## Quick start (flash an ESP32)

**Easiest — web flasher, no downloads:**
Open the [web flasher](https://turbotike.github.io/poor-mans-beier-firmware-for-the-diyguy-999-board-/)
in **Chrome or Edge on a desktop**, plug in the ESP32, pick engine + protocol,
click **Install**.

> If a flash finishes but nothing changed, hard-refresh the page once
> (**Ctrl+Shift+R**) and try again — that clears any stale cached file.

**Or run the local flasher app:**

1. Download or `git clone` this repo.
2. Plug the ESP32 sound board into your PC over USB **with the truck battery
   disconnected** (USB power only while flashing).
3. Double-click **`Launch_Flasher.bat`** (Windows).
   On macOS/Linux: `python3 flasher_server.py`.
4. Your browser opens to <http://localhost:8765>.
5. Pick **engine** (C15 / 8V92 / N14 / FH12), **protocol** (PWM / iBUS / SBUS), and the
   **COM port** the ESP32 enumerated as.
6. Click **Flash firmware** and watch the progress bar.
7. When it says "Hard resetting via RTS pin", you're done.
8. Power-cycle the board. The ESP32 boots, brings up Wi-Fi AP **`RC_SemiTruck`**
   (password **`truckin123`**), and starts driving.

For wiring, RC binding, and tuning, see **[HOW_TO.md](HOW_TO.md)** (setup) and the
**[USER_MANUAL.md](USER_MANUAL.md)** (driving, controls, web UI, wireless trailer).

---

## Connecting to the truck's web UI

After first boot:

1. On a phone/tablet, join Wi-Fi network **`RC_SemiTruck`**, password
   **`truckin123`**.
2. Open <http://192.168.4.1> in any browser.
3. The **RC LARGECARS** dashboard shows live RC channel values and engine
   state, with sliders for every volume, crossfade time, throttle threshold,
   ESC/brake curve, light, and steering trim. Hit **Save** to persist to NVS.

---

## Hardware

- **Board**: TheDIYGuy999 *RC_Engine_Sound_ESP32* v1.2 (standard, unmodified).
- **Audio out**: the ESP32's built-in DAC into the board's PAM8403 amp. It's an
  8-bit DAC, so loudness is mastered in software; for max volume, run a 4Ω
  speaker and feed the amp a solid 5V.
- **Power**: 2S–3S LiPo into the board's BEC, or USB while flashing.
- **Receiver**:
  - **PWM**: up to **6 servo wires** from RX to CH1–CH6 (throttle, steering,
    gear/3-pos, horn, lights, aux).
  - **iBUS**: single signal wire to RX1 (GPIO16). FlySky FS-iA6B etc.
  - **SBUS**: single inverted signal wire to RX1. FrSky / Futaba. *(untested on
    real hardware)*
- **ESC + steering**: two servo outputs from the board.
- **Lights**: 13 LED channels via the on-board MOSFETs.

Detailed pin map and channel assignments are in [HOW_TO.md](HOW_TO.md).

---

## Making your own sound pack

No PlatformIO, ffmpeg, or Python needed — there's a drag-and-drop builder right
in the browser:

### 🎛 [Open the in-browser sound-pack builder](https://turbotike.github.io/poor-mans-beier-firmware-for-the-diyguy-999-board-/builder.html)

1. **Drop your WAV files in** (any sample rate, mono/stereo, 8/16/24/32-bit PCM
   or float — the builder normalizes everything).
2. **Name each one to match a slot** so the firmware finds it: `idle`, `start`,
   `shutdown`, `accel1`, `accel2`, `cruise`, `decel1`, `decel2`, `lope`, `horn`,
   `airbrake`, `airdry`, `gearchg`, `revbeep`, `pbrakeon`, `pbrakeoff`,
   `freerev`, `highrev`, `blinker`. Missing slots just fall back to silence.
3. Pick a **Loudness** level (built-in limiter + dither, so packs come out loud
   and clean) and keep an eye on the flash-budget meter (~3.5 MB ceiling).
4. Click **Build pack** → you get a `.zip` of `.h` header files.
5. Drop it into `tools/sound_packs/<name>/` of the firmware source and rebuild
   (see below).

**Tips for sounds that don't suck**
- **Idle and cruise must loop seamlessly** — cut on a zero-crossing.
- **Match the RPM at the seams** so `idle → accel1 → accel2` hand off cleanly.
- **Dial timing in the web UI**, not the audio — tweak the crossfade sliders
  until the engine sound lines up with the truck's motion.
- **Mono is fine** — stereo just wastes flash; the builder folds it to mono.

---

## Building from source

You only need this to add a new engine, add an RC protocol, or hack the firmware.

> **Note:** this repo is the *distribution* repo — prebuilt `.bin` files, the
> flasher, and the web tools. The PlatformIO firmware source (`src/`,
> `platformio.ini`, the `tools/sound_packs/` audio headers, and the
> `build_all_variants.ps1` / `use_pack.ps1` build scripts) lives in the firmware
> source tree, not here.

1. Install [VS Code](https://code.visualstudio.com/) and the
   [PlatformIO IDE](https://platformio.org/install/ide?install=vscode) extension.
2. Open the firmware project folder.
3. Build one variant: `pio run -e esp32dev`.
4. Build all variants: `./tools/build_all_variants.ps1` — regenerates every
   `*.bin` and refreshes `manifest.json`. Recorded-engine packs are built with
   `-DDRIVELINE_SIM`; the script handles that for you.

Adding a new engine: drop a sound pack under `tools/sound_packs/<name>/` matching
the layout of `c15/`, add it to `build_all_variants.ps1` and `use_pack.ps1`, then
rebuild.

---

## Credits

- **TheDIYGuy999** — the original RC_Engine_Sound_ESP32 board, sound assets, and
  the RC engine-sound community foundation this builds on.
- **Beier Sound Module** — the gold standard this firmware chases.

---

## License

MIT. See [LICENSE](LICENSE) if present, otherwise treat as MIT.
