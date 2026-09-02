# RC LARGECARS — User Manual

*RC LARGECARS firmware for the DIYGuy999 RC_Engine_Sound_ESP32 board (v1.2)*

Everything you need to drive, tune, and enjoy your truck. For first-time
flashing/setup, see **[HOW_TO.md](HOW_TO.md)**; this manual is about *using* it.

---

## Contents
1. [Quick start](#1-quick-start)
2. [Flashing the firmware](#2-flashing-the-firmware)
3. [Connecting to the web UI](#3-connecting-to-the-web-ui)
4. [Wiring your receiver](#4-wiring-your-receiver)
5. [Driving & engine sounds](#5-driving--engine-sounds)
6. [Turn signals](#6-turn-signals)
7. [Lights](#7-lights)
8. [Horn, brakes & other sounds](#8-horn-brakes--other-sounds)
9. [Wireless trailer](#9-wireless-trailer)
10. [The web UI in detail](#10-the-web-ui-in-detail)
11. [Making your own sound pack](#11-making-your-own-sound-pack)
12. [Troubleshooting](#12-troubleshooting)

---

## 1. Quick start

1. **Flash** the firmware (browser flasher or USB — see §2). Pick your **engine**
   (Caterpillar C15 / Detroit 8V92 / Cummins N14) and **protocol** (PWM / iBUS / SBUS).
2. **Wire** your receiver to the board (see §4) and plug in a **4Ω speaker** and a
   **2S–3S LiPo**.
3. **Power on.** The board makes its own Wi-Fi network.
4. On a phone/tablet, join Wi-Fi **`RC_SemiTruck`** (password **`truckin123`**) and
   open **`http://192.168.4.1`** to tune everything.
5. Flip your engine switch (or tap **ENGINE** in the web UI) and drive.

---

## 2. Flashing the firmware

**Browser (easiest):** open the flasher page in **Chrome or Edge on a desktop**,
plug the board in via USB (battery disconnected), pick engine + protocol, click
**Install**.
> If a flash finishes but nothing changed, **hard-refresh the page once**
> (Ctrl+Shift+R) and flash again — that clears any cached file.

**Local app:** run the included flasher (`Launch_Flasher.bat` on Windows, or
`python3 flasher_server.py`), pick engine/protocol/COM port, click **Flash**.

When it says *"Hard resetting…"*, power-cycle the board.

---

## 3. Connecting to the web UI

1. On any phone/tablet/PC, join Wi-Fi **`RC_SemiTruck`** / password **`truckin123`**.
2. Open **`http://192.168.4.1`** in a browser.
3. You'll see the **RC LARGECARS** dashboard. Tune anything, then tap **💾 Save to
   NVS** to keep your changes after a power-cycle.

The Wi-Fi has no internet — that's normal; your phone may warn "no internet,"
just stay connected.

---

## 4. Wiring your receiver

Pick the build that matches your radio when you flash.

### PWM (separate wire per channel)
Wire each receiver channel to the matching board header. Each header has two
slots wired together (pass-through), which is how steering works: the receiver
feeds the ESP32 *and* the servo at the same time.

| Function | Board channel | Notes |
|---|---|---|
| **Throttle** | **CH1** | |
| **Steering** | **CH2** | RX steering → one slot; steering **servo → the other CH2 slot** (pass-through). The ESP32 reads it for turn signals; the servo follows your radio directly. |
| **Gear (3-position)** | **CH3** | Park / Forward / Reverse |
| **Lights** | **CH4** | Switch/knob to cycle light modes |
| **Engine on/off** | **CH5** | 2-position switch |
| **Horn** | **CH6** | Momentary button/switch |

> In PWM, the ESP32 doesn't generate the steering signal, so steering **trim/
> reverse** is done on your transmitter (the turn-signal hold still works).

### iBUS (FlySky) / SBUS (FrSky-Futaba)
A **single signal wire** to the board's **RX1** input carries all channels.
- iBUS: standard FlySky (e.g. FS-iA6B).
- SBUS: inverted serial (FrSky/Futaba).
- Set which channel is **steering** in the web UI → **Steering → iBUS Channel**.
  Watch the live channel values to find each one.

> Tip: the dashboard shows live **Throttle**, **Gear**, **Motor %** etc. — use it
> to confirm your channels are mapped right.

---

## 5. Driving & engine sounds

The engine is a **time-based sound machine**. Punch the throttle and it climbs
**idle → accel → cruise**; ease off and the **jake brake** takes over until you
are back at idle, like a real diesel.

- **Start the engine:** flip the engine switch (CH5) or tap **🔑 ENGINE** in the web UI.
- **Gear (3-position switch):**
  - **Park** — engine idles; hold throttle to **free-rev** (no movement).
  - **Forward** — drive; throttle pulls through the accel/cruise/decel sounds.
  - **Reverse** — backs up with the **reverse beeper**.
- **Lifting off — the jake:** the engine brake holds for as long as you are off
  the throttle rather than playing once, and it grabs over about a third of a
  second instead of snapping on. Its chop follows **engine rpm**, so it steps
  back *up* every time the box drops a gear — the same sawtooth you hear from a
  real truck jaking down through the gears — and falls away as you slow.
- **Free-rev in Park:** hold the throttle with the gear switch in Park. On FH12
  this raises the pitch of the idle rather than playing a separate clip, so how
  far you push the stick is how far it revs.
- **Lope idle:** tap **🏎 LOPE IDLE** in the web UI for a lumpy/cammed idle.

All the timing (how long each accel/decel layer lasts, crossfades) is adjustable
in the web UI — see §10.

---

## 6. Turn signals

Turn signals work by **holding the steering at full lock**:
- Hold the wheel hard **left or right** for a moment → that indicator **latches on
  and flashes**.
- **Recenter** the wheel to cancel.

**Steering-tap gestures** (no extra channels needed):
- **Tap full-right 3× quickly → 4-way hazards** on/off.
- **Tap full-left 3× quickly → cycle the light modes.**

(Taps are quick jabs to full lock and back — a normal held turn won't trigger
them. Requires signals enabled.)

Tune it in the web UI → **Steering-Hold Turn Signals**:
- **Activation Threshold** — how far you must turn before it arms.
- **Hold Time** — how long to hold the lock before it latches.
- **Enable** toggle.

> PWM trucks: this needs the steering signal on **CH2** (see §4). iBUS/SBUS: set
> the steering channel in the UI.

---

## 7. Lights

13 light channels with 5 modes. Cycle modes with your **lights switch (CH4)** or
the **💡 LIGHTS** button in the web UI:

| Mode | Lights on |
|---|---|
| 0 | Off |
| 1 | Side markers + tail |
| 2 | + Roof |
| 3 | + Headlights |
| 4 | Full (fog, cabin, beacon, etc.) |

**Automatic overlays** (any mode): brake lights when braking, reverse lights in
reverse, turn signals, and hazards. Set every light's brightness in the web UI →
**Light Brightness**.

- **American combined rear** option: indicator outputs double as red tail/brake
  bulbs (US-style 3-wire trailer look).

---

## 8. Horn, brakes & other sounds

- **🔊 Air horn** — horn switch (or the web **HORN** button); hold for as long as
  you want.
- **Air brake hiss** — plays when you release the brakes to pull away.
- **Gear-change clunk** — on Forward↔Reverse shifts.
- **Park brake** — air release when entering/leaving Park.
- **Reverse beeper** — beeps while in Reverse (can be disabled in the UI).
- **Air dryer purge** — a random "pssst" every 40–70s while running (interval +
  volume adjustable; set volume to 0 to disable).

Every sound has its own **volume slider** in the web UI → **Sound Volumes**.

---

## 9. Wireless trailer

The truck broadcasts trailer lights/functions over **ESP-NOW** to a
**TheDIYGuy999 wireless trailer board**. Turn it on in the web UI →
**Air Dryer & Auto-Shutdown → Wireless Trailer**.

- **Lights** (tail/brake, markers, reverse, L/R indicators) mirror the truck
  automatically — no extra wiring on the truck side.
- **Legs / Ramps** — hold the **LEGS UP/DOWN** and **RAMPS UP/DOWN** buttons in the
  web UI's **Wireless Trailer** card.
- **Beacons** — the **BEACONS** toggle.

### Trailer hitch switch (optional)
Wire a small switch on your 5th wheel to **GPIO32 (the 3rd-brake-light header)
and GND**, then enable **Trailer Hitch Switch** in the web UI:
- Hitch a trailer → **coupling sound** (air + clunk).
- Unhitch → **uncoupling sound**, and the **trailer lights switch off
  automatically** until you hook up again.

> Switch logic: closed-to-ground = hitched. If it reads backwards, swap the
> switch's NO/NC wiring. The trailer board must be on the same Wi-Fi channel as
> the truck.

---

## 10. The web UI in detail

Open **`http://192.168.4.1`**. Everything is live; tap **💾 Save to NVS** to keep it.

- **Master Volume** — overall loudness.
- **Live Truck Status** — engine state, gear, throttle %, **motor %**, lights, uptime.
- **Remote Control** — HORN, LIGHTS, ENGINE, LOPE IDLE.
- **Wireless Trailer** — LEGS, RAMPS, BEACONS.
- **Settings sections** (tap to expand):
  - **Sound Volumes** — per-sound levels (incl. trailer coupling).
  - **Crossfade Times** — how smoothly sounds blend (idle→accel, etc.).
  - **Motor & ESC** — accel/brake ramps, kick-start, thresholds, neutral dead-zone.
  - **Steering** — channel (iBUS), center trim, invert.
  - **Gear & Channel PWM** — gear/horn/lights switch thresholds.
  - **Light Brightness** — per-channel brightness.
  - **Steering-Hold Turn Signals** — signal threshold/hold/enable.
  - **Air Dryer & Auto-Shutdown** — purge timing, auto-off, **Wireless Trailer**,
    **Trailer Hitch Switch**.
- **Light Test** — manually drive each light channel to check wiring.
- Buttons: **🔄 Reload**, **↩ Defaults**, **💾 Save to NVS**.

---

## 11. Making your own sound pack

Use the browser **sound-pack builder** (linked from the flasher page). Drag in
WAV files named for each slot (`idle`, `start`, `accel1`, `accel2`, `cruise`,
`decel1`, `decel2`, `horn`, `shutdown`, …), pick a **Loudness** level, and click
**Build pack** to get a `.zip` of headers. Tips:
- **Idle and cruise must loop seamlessly** (cut on a zero-crossing).
- **`decel1` is the jake.** It loops while you are off the throttle, so cut it
  to a **whole number of chop cycles** from the steadiest part of the take.
  Otherwise the rhythm slips a fraction of a beat at every loop wrap and you
  hear a stumble about once a second.
- Keep the whole pack under ~3.5 MB.
- Dial *timing* in the web UI, not the audio.

---

## 12. Troubleshooting

| Problem | Fix |
|---|---|
| **Flash "complete" but nothing changed** | Hard-refresh the flasher page (Ctrl+Shift+R) and flash again, or flash over USB. |
| **No sound** | Engine started? Master volume up? Speaker connected (4Ω)? |
| **Too quiet** | Use a **4Ω** speaker, make sure the amp gets a solid **5V**, and raise Master Volume. The audio is already mastered loud; the small onboard amp is the ceiling. |
| **Turn signals don't work (PWM)** | Steering signal must be on **CH2**. Check "Steering-Hold Turn Signals" is enabled and the threshold isn't too high. |
| **Signals flash backwards** | Steering → **Invert** in the web UI. |
| **Can't find the Wi-Fi** | Network is **RC_SemiTruck** / **truckin123**; page is **192.168.4.1**. Power-cycle the board. |
| **Web page won't load** | Re-join the Wi-Fi; ignore the "no internet" warning; try `http://192.168.4.1` (not https). |
| **Gear stuck / wrong** | Check the gear switch is on **CH3** (PWM) and set the gear PWM thresholds in **Gear & Channel PWM**. |
| **Trailer lights don't respond** | Enable **Wireless Trailer**; the trailer board must be powered and on the same Wi-Fi channel. |
| **Reverse beep annoying** | Turn off **Reverse Beep** in Motor & ESC, or set its volume to 0. |

---

## Specs

- **Board:** DIYGuy999 RC_Engine_Sound_ESP32 v1.2 (unmodified)
- **Engines:** Caterpillar C15, Detroit 8V92, Cummins N14, Volvo FH12
- **Protocols:** PWM (6-ch), FlySky iBUS, FrSky/Futaba SBUS
- **Audio:** 8-bit @ 22050 Hz, internal DAC → onboard amp (4Ω speaker recommended)
- **Power:** 2S–3S LiPo via the board's BEC
- **Wi-Fi:** `RC_SemiTruck` / `truckin123` → `http://192.168.4.1`

🤖 *This firmware was vibe-coded. Built for fun, tuned by ear. Enjoy the truck!* 🚛
