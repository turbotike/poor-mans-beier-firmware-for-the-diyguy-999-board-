# Poor Man's Beier — Firmware for the DIYGuy999 ESP32 Sound Board

> ⚠️ **Public beta.** Most things work, but some features are still
> bench-tested only. Expect rough edges, please open issues when you find
> them.

> 🤖 **Vibe coded.** This entire project — firmware, flasher, web tools, and
> sound packs — was built by vibe coding with AI. Built for fun, tuned by ear.

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
  > Heads-up: PWM and iBUS have both been tested on real hardware. SBUS
  > is built and should work, but it hasn't been on a truck yet - if you
  > run it and hit issues, open an issue on GitHub and I'll help dial it in.
- **Realistic, time-based engine state machine** — accel and decel layers play
  out on real timers, not just throttle position. Punch the throttle and you
  hear a full `idle → accel1 → accel2 → cruise` climb; let off and the engine
  actually *coasts down* through `decel1 → decel2 → idle` over a couple
  seconds, just like a real diesel falling off boost. Re-accel mid-decel
  resumes at the correct layer (high-speed lift = high-speed re-engage,
  low-speed lift = low-speed re-engage). Plus park-gear free-rev, reverse
  beep, and air-brake hiss with arm/fire hysteresis + cooldown.
- **Every accel/decel timing is fully adjustable from the web UI** to match
  whatever sound pack you're running. Each layer (accel1, accel2, decel1,
  decel2) has its own duration slider, plus crossfade times between layers,
  so you can stretch a long lazy 8V92 lope or tighten up a snappy C15 spool
  until the timing lines up perfectly with the audio. Saved to NVS, no
  reflashing needed.
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
flasher_server.py             local web UI + flash backend (Python stdlib + esptool)
Launch_Flasher.bat            Windows launcher (opens browser automatically)
Launch_Flasher_silent.vbs     no-console launcher
firmware/
  manifest.json               variant + offset table
  bootloader.bin
  partitions.bin
  c15_pwm.bin    c15_ibus.bin    c15_sbus.bin
  8v92_pwm.bin   8v92_ibus.bin   8v92_sbus.bin
docs/                         GitHub Pages site (web flasher, builder)
tools/                        helper scripts (manifest generation)
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
3. Double-click **`Launch_Flasher.bat`** (Windows).
   On macOS/Linux, run `python3 flasher_server.py`.
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
  - **iBUS**: single signal wire to RX1 (GPIO16). FlySky FS-iA6B etc.
  - **SBUS**: single inverted signal wire to RX1. FrSky / Futaba. *(untested on real hardware)*
- **ESC + steering**: two servo outputs from the board.
- **Lights**: 13 LED channels via the on-board MOSFETs.

Detailed pin map and channel assignments are in [HOW_TO.md](HOW_TO.md).

---

## Building from source

You only need this if you want to add a new engine sound, add a new RC
protocol, or hack the firmware.

> **Note:** This repo is the *distribution* repo — prebuilt `.bin` files, the
> flasher, and the web tools. The PlatformIO firmware source (the `src/`,
> `platformio.ini`, the `tools/sound_packs/` audio headers, and the
> `build_all_variants.ps1` / `use_pack.ps1` build scripts referenced below)
> lives in the firmware source tree, not here. Grab that if you want to
> recompile.

1. Install [VS Code](https://code.visualstudio.com/) and the
   [PlatformIO IDE](https://platformio.org/install/ide?install=vscode) extension.
2. Open the firmware project folder.
3. Build a single variant: `pio run -e esp32dev`.
4. Build all six flasher variants: `./tools/build_all_variants.ps1`.
   This regenerates every `*.bin` in `firmware/` and refreshes `manifest.json`.

Adding a new engine sound: drop a new sound pack under
`tools/sound_packs/<name>/` matching the layout of `c15/` or `8v92/`, then
add it to `build_all_variants.ps1`.

---

## Making your own sound pack

You don't need PlatformIO, ffmpeg, or even Python for this — there's a
drag-and-drop builder right in the browser:

### 🎛 [Open the in-browser sound pack builder](https://turbotike.github.io/poor-mans-beier-firmware-for-the-diyguy-999-board-/builder.html)

**What you need**

A folder of WAV files (any sample rate, 8/16/24/32-bit PCM or float — the
builder normalizes everything for you). One file per slot:

| Slot          | What it is                                       | Typical length |
|---------------|--------------------------------------------------|----------------|
| `start`       | engine cranking → catch                          | 1–3 s          |
| `idle`        | clean, *seamlessly looping* idle                 | 1–2 s loop     |
| `accel1`      | low-rpm pull / spool                             | 4–8 s          |
| `accel2`      | mid-to-high rpm pull                             | 4–8 s          |
| `cruise`      | seamlessly looping mid-rpm                       | 1–2 s loop     |
| `decel1`      | high-rpm coast-down                              | 3–6 s          |
| `decel2`      | low-rpm coast-down                               | 3–6 s          |
| `lopeidle`    | (optional) rough/cammed idle                     | 2–6 s loop     |
| `knock`       | (optional) injector/diesel knock layer           | 1–2 s loop     |
| `horn`        | air horn one-shot                                | 1–3 s          |
| `airbrake`    | air-brake hiss one-shot                          | 0.5–2 s        |
| `reversebeep` | reverse beeper one-shot                          | 0.3–1 s        |

Missing slots are fine — just leave them out and the firmware falls back to
silence for that one.

### Step by step

1. **Open the builder** (link above) in Chrome or Edge.
2. **Drag your WAV files in.** Name each one to match the slot
   (`idle.wav`, `accel1.wav`, `horn.wav`, etc.) — the builder auto-detects
   the slot from the filename.
3. The flash-budget meter at the top tells you how much room you've got
   left. Aim to keep the whole pack under ~3.5 MB; trim long files in any
   audio editor (Audacity is free) before re-dropping if you blow past it.
4. Click **Build pack** → it spits out a `.zip` containing all the `.h`
   header files the firmware needs.
5. **Install it** — two options:
   - **Easy:** unzip into `tools/sound_packs/mypack/`, then run
     `./tools/build_all_variants.ps1` to bake it into a new firmware
     variant. Flash with the local flasher.
   - **Even easier (coming soon):** drop the zip directly on the live web
     flasher to build + flash in one step.

### Tips for sounds that don't suck

- **Idle and cruise must loop seamlessly.** Cut on a zero-crossing, fade
  the very last 5 ms into the very first 5 ms. Audacity's *Repeat* preview
  will tell you instantly if there's a click.
- **Match the rpm at the seams.** `idle` → `accel1` should land at the same
  rpm; `accel1` → `accel2` should hand off mid-pull, not jump.
- **Dial the timing in the web UI, not the audio.** After flashing, open
  the truck's web UI and tweak the **accel1/accel2/decel1/decel2 duration**
  sliders until the engine sound finishes right when the truck reaches
  cruise rpm. That's what those sliders are for.
- **Mono, please.** Stereo files just waste flash — the builder folds them
  to mono anyway.

---

## Credits

- **TheDIYGuy999** — the original RC_Engine_Sound_ESP32 board, sound assets,
  and the entire RC engine-sound community foundation this builds on.
- **Beier Sound Module** — the gold standard this firmware tries to chase.

---

## License

MIT. See [LICENSE](LICENSE) if present, otherwise treat as MIT.
