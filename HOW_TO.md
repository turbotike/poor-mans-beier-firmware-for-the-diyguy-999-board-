# How to use RC LARGECARS — Step by Step

Complete guide from "I just downloaded this" to "my truck sounds awesome".

---

## 1. What you need

| Item | Notes |
|------|-------|
| TheDIYGuy999 RC_Engine_Sound_ESP32 board v1.2 | Unmodified. Stock board. |
| ESP32-WROOM-32 module | Already on the board above. |
| USB cable (data, not charge-only) | For flashing. |
| Windows / macOS / Linux PC | Windows has a one-click `.bat`. |
| Python 3.x | Free from python.org. **Add to PATH** during install. |
| RC receiver | Any PWM, iBUS, or SBUS receiver. |
| 2S or 3S LiPo + BEC | Powers the board in the truck. |
| 4Ω–8Ω speaker | Connected to the board's I2S amp output. |

---

## 2. Install Python (one time)

1. Go to <https://python.org/downloads/>.
2. Download Python 3.11 or newer.
3. **During install, check "Add Python to PATH"**. This is the most common
   thing people forget.
4. Open a new Command Prompt and type `python --version`. If you see a
   version number, you're good.

---

## 3. Get the firmware

Either:

- **Easy:** click the green **Code** button on the GitHub page → **Download
  ZIP** → extract anywhere.
- **Git:** `git clone https://github.com/turbotike/poor-mans-beier-firmware-for-the-diyguy-999-board-.git`

---

## 4. Flash the ESP32

### 4a. Plug it in

1. Take the ESP32 sound board out of the truck (or just disconnect the
   battery — USB only while flashing).
2. Plug it into your PC with a USB cable.
3. Windows usually auto-installs the CP210x or CH340 driver. If not:
   - **CP210x**: <https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers>
   - **CH340**: <https://sparks.gogo.co.nz/ch340.html>
4. Open Device Manager → Ports (COM & LPT) → note the COM number
   (e.g. `COM5`).

### 4b. Open the flasher

- **Windows**: double-click `flasher\Launch_Flasher.bat`.
  A Command window opens, then your default browser opens to
  <http://localhost:8765>.
  *(Use `Launch_Flasher_silent.vbs` if you don't want the console window.)*
- **macOS / Linux**: in a terminal,
  `python3 flasher/flasher_server.py`, then open
  <http://localhost:8765>.

### 4c. Pick your build

In the web UI:

1. **Engine sound**: pick **C15** (Caterpillar inline-6 turbo) or **8V92**
   (Detroit Diesel V8).
2. **Protocol**:
   - **PWM** — classic 5 servo wires from your receiver.
   - **iBUS** — FlySky one-wire bus (FS-iA6B, FS-iA10B).
   - **SBUS** — FrSky / Futaba one-wire inverted bus.
3. **Serial port**: pick the COM port from step 4a.
4. Click **Flash firmware**.

### 4d. If flashing fails

If you see `chip stopped responding` or it hangs at "Connecting…":

- Try a different USB cable (must be data-capable, not charge-only).
- Try a different USB port (rear ports on a desktop are most reliable;
  avoid hubs).
- Hold the **BOOT** button on the ESP32 while clicking Flash, release once
  it starts writing.
- Disconnect anything else powered from the board (servos, ESC, big LEDs)
  so the USB port can keep the board fed.

---

## 5. First boot

1. Unplug USB. Reconnect the truck battery.
2. The ESP32 starts up. If you have a speaker connected, you'll hear the
   start-up sample → idle.
3. The board creates a Wi-Fi access point:
   - **SSID**: `RC_SemiTruck`
   - **Password**: `truckin123`

---

## 6. Connect the web UI

1. On a phone or tablet, join Wi-Fi `RC_SemiTruck` (password `truckin123`).
2. Ignore the "no internet" warning — the truck *is* the network.
3. Open <http://192.168.4.1> in any browser.
4. You should see the **RC Semi Truck** dashboard with live channel values.

> **Tablet won't reconnect later?** Tell the tablet to *forget* the
> `RC_SemiTruck` network, then re-join. The firmware now resets the radio
> cleanly on every boot to prevent stale lease problems, but a once-only
> forget on the tablet helps if you ever flashed an older build.

---

## 7. RC channel map

| Channel | Function | Notes |
|--------:|----------|-------|
| CH1 | Steering | Proportional. Trim + invert in web UI. |
| CH2 | *(free)* | Not read. |
| CH3 | **Throttle** | Proportional. Centre = idle, forward = drive, back = brake. |
| CH4 | *(free)* | Not read. |
| CH5 | **Engine on/off** | 2-position switch. |
| CH6 | **Horn** | Momentary button. Tap = city horn, hold = air horn. |
| CH7 | **Gear** | **3-position switch** — Park / Forward / Reverse. |
| CH8 | **Lights** | Toggle or button. On/off at the level set in the web UI. |

PWM builds use a different set of pins — see `CHANNELS.md` for the full map.

*With iBUS or SBUS, all channels arrive on a single wire. With PWM, run one
servo wire per channel.*

---

## 8. Audio chain — what you'll hear

- **Throttle from idle**: `accel1` → `accel2` → `cruise` (loops).
- **Let off from cruise** or after reaching `accel2`: `decel1` → `decel2` → idle.
- **Let off mid-`accel1`** (never crossed over): `decel2` → idle.
- **Re-throttle from mid-decel**:
  - If decel started high (cruise/`accel2`) → resumes at `accel2`.
  - If decel started low (`accel1` only) → restarts at `accel1`.
- **Brake stick deep + release**: air-brake hiss (3 random samples,
  hysteresis + 2-second cooldown so it can't double-trigger).
- **Forward → Reverse**: gear-clunk one-shot.
- **In Reverse**: continuous reverse beep until back to Park or Forward.
- **Park + throttle**: free-rev.

---

## 9. Tuning in the web UI

Every value below is a slider you can move and hit **Save**:

- **Volumes**: idle, accel, cruise, decel, horn, air horn, air brake,
  shutdown, reverse beep, gear clunk.
- **Crossfade times** (ms): idle→accel, accel→cruise, accel→decel,
  cruise→decel, track→track, decel→idle, free-rev→idle, any→shutdown.
- **Throttle**: accel threshold (PWM µs above neutral that triggers accel),
  neutral zone width (deadband), full-brake PWM.
- **Steering**: trim, invert, rate limit.
- **Lights**: indicator blink rate, brake brightness, reverse brightness,
  combined-rear mode.

---

## 10. Updating later

When a new firmware drops on this repo:

1. Pull / re-download the repo.
2. Re-run the flasher exactly like the first time.
3. Saved settings *may* be wiped — re-tweak in the web UI.

---

## 11. Common problems

| Symptom | Fix |
|---------|-----|
| Browser shows "site can't be reached" at `localhost:8765` | Make sure `Launch_Flasher.bat` is still open. Check Python is on PATH. |
| `chip stopped responding` mid-flash | Different USB cable / port. Hold BOOT during flash. |
| Tablet connects but page won't load | On the tablet, forget the network and re-join. Browse to `http://192.168.4.1` directly (don't search). |
| Engine plays but no movement | Check ESC servo lead, throttle channel reversed, or RC battery dead. |
| No steering | Make sure you flashed the protocol that matches your receiver. iBUS firmware ≠ PWM firmware. |
| Air-brake hiss never plays | Throttle must go *deep* into brake (well below neutral) and then back up to neutral or above. Stick wiggle near neutral is intentionally ignored. |
| Air-brake hiss plays multiple times | Should not happen with current build — if it does, capture the throttle channel value and open an issue. |
| Sound drops / clicks under load | Lower master volume. The I2S amp can clip on big stick movements. |

---

## 12. Building your own

If you want to compile from source instead of flashing the included binaries:

1. Install [VS Code](https://code.visualstudio.com/) and the
   [PlatformIO IDE](https://platformio.org/install/ide?install=vscode)
   extension.
2. Open the project folder in VS Code.
3. Bottom toolbar: ✓ build, → upload, plug = serial monitor.
4. Or terminal:

   ```powershell
   pio run                 # build
   pio run -t upload       # build + flash
   pio device monitor      # serial @ 115200
   ```

5. To rebuild *all six* flasher variants:

   ```powershell
   ./tools/build_all_variants.ps1
   ```

---

## 13. Credits

Built on top of TheDIYGuy999's RC_Engine_Sound_ESP32 hardware and sound
heritage. Inspired by the Beier Sound Module. All hobbyist, all free,
all open source. PRs welcome.

Have fun. Drive smooth. Post videos.
