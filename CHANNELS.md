# RC LARGECARS — Channel Map & Wiring

What each channel does, and **what kind of control you need to assign to it**.
That second part matters: a 3-position switch on a channel that wants a button
will misbehave, and vice-versa.

The mapping is different between **iBUS/SBUS** and **PWM**, because PWM builds
read five separate signal wires while serial builds read one bus.

---

## iBUS / SBUS (one signal wire to the receiver)

Wire a single lead from the receiver's iBUS/SBUS output to **GPIO36 (VP)**.

| Ch | Function | Control type | Notes |
|----|----------|--------------|-------|
| **CH1** | Steering | Proportional stick/wheel | Passed to the servo on GPIO13. Trim + invert + rate limit in the web UI. Source channel is configurable (`steeringChannel`, 1–14). |
| **CH2** | *(free)* | — | Not read. Use it for anything. |
| **CH3** | **Throttle** | Proportional stick/trigger | Centre = idle, forward = drive, back = brake. Bottom ~92% of forward travel is the creep zone; full stick launches the truck. |
| **CH4** | *(free)* | — | Not read. |
| **CH5** | **Engine on/off** | 2-position switch | Low = off, high = running. Starts and stops the engine. |
| **CH6** | **Horn** | Momentary button | Short tap = city horn, hold = air horn. In PARK it also does free-rev. |
| **CH7** | **Gear** | **3-position switch** | Park ↔ Forward ↔ Reverse. Needs three distinct positions — a 2-pos switch can only ever reach two of them. |
| **CH8** | **Lights** | **Toggle or button** | Simple on/off. What "on" means is set by **Lights Switch Level** in the web UI. |

Anything above CH8 is ignored, so a 10-channel radio has spares.

---

## PWM (five separate signal wires)

Each channel is its own servo lead from the receiver to the board.

| Ch | Function | Control type | Board pin |
|----|----------|--------------|-----------|
| **CH1** | Throttle | Proportional | **GPIO13** |
| **CH2** | Steering | Proportional | **GPIO12** — passes through to the servo; the board does not generate steering in PWM mode |
| **CH3** | Gear | **3-position switch** | **GPIO14** |
| **CH4** | Lights | Toggle or button | **GPIO27** |
| **CH5** | Engine on/off | 2-position switch | **GPIO35** |
| **CH6** | Horn | Momentary button | **GPIO34** |

> **Note:** GPIO14 is the gear input in PWM builds, which is why PWM firmware
> drives the ESC from GPIO33 rather than the level-shifted GPIO14 pin.

---

## Light modes

The lights channel is a plain **on/off** — a 2-position toggle is fine. Which
mode it comes on at is set by **Lights Switch Level** in the web UI, because a
toggle cannot reach five modes on its own and the 3-position switch is already
used by the gear selector.

If you would rather step through from the transmitter, **double-tap** the switch
(off/on twice within 600 ms) and it advances one level and remembers it.

| Mode | What's on |
|------|-----------|
| 0 | All off |
| 1 | Side markers + tail running lights |
| 2 | + headlights |
| 3 | + roof / cab clearance |
| 4 | + fog, cabin, beacon (full) |

Brake, reverse and indicator lights are automatic and work in every mode.

**Turn signals** come from steering by default — hold a steering input past the
threshold and the indicator on that side blinks, then holds briefly after you
straighten up. Threshold and hold time are in the web UI, and it can be turned
off entirely.

**American mode** (`combinedRearLights`) makes the rear indicators glow at tail
brightness with the running lights, like a US 3-wire harness. The rear brake
still comes from the dedicated tail output.

---

## ESC and outputs

| Output | Pin | Notes |
|--------|-----|-------|
| ESC signal | **GPIO33** | 3.3V logic. Most brushless ESCs are fine with this; older brushed controllers can be fussy. |
| Steering servo | **GPIO13** | iBUS/SBUS builds only |
| Lights | 3, 15, 2, 4, 17, 5, 18, 21, 22, 16, 19, 32, 23 | All 13 assigned |
| Battery sense | **GPIO39** | |

**Brushed ESC Mode** in the web UI raises the minimum signal sent once the truck
should be rolling. Brushless setups pull away happily just off neutral; a
brushed ESC with a high-turn motor often will not, and just sits there. Turn it
on and raise **Kick Start** until it launches cleanly.

---

## Web UI

Power the truck, connect to the WiFi access point, then open the page.

- **SSID:** `RC_SemiTruck`
- **Password:** `truckin123`
- **Address:** `http://192.168.4.1`

Everything is live — sliders take effect as you drag them, and settings survive
a reflash because they live in a separate area of flash from the firmware.

---

## Reassigning channels (FH12 builds)

The map above is the default. On **FH12** firmware you can also change which
channel drives which role, from the truck's web UI or over `/set`:

| Key                | Role     | Default |
|--------------------|----------|---------|
| `throttleChannel`  | throttle | 3       |
| `engineChannel`    | engine   | 5       |
| `hornChannel`      | horn     | 6       |
| `gearChannel`      | gear     | 7       |
| `lightsChannel`    | lights   | 8       |
| `steeringChannel`  | steering | 1       |

Each takes a channel number 1–14. Anything outside that range is ignored and
the default is used instead, so a bad value cannot leave the truck without a
throttle.

**iBUS and SBUS only.** In PWM builds each role is wired to its own GPIO on the
board, so there is nothing to reassign in software — you move the servo lead.

The other engines still use the fixed map; they pick this up when they are next
rebuilt.
