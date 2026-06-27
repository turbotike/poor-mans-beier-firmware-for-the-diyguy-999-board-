"""Generate ESP Web Tools manifests (one per variant) for GitHub Pages.

Reads docs/firmware/ and writes docs/manifest_<variant>.json files plus
a single docs/manifests.json index that the index.html uses to populate the
variant picker.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FW   = os.path.join(ROOT, "docs", "firmware")
OUT  = os.path.join(ROOT, "docs")

LABELS = {
    "c15_pwm":  ("CAT C15",  "PWM (standard RC PPM)"),
    "c15_ibus": ("CAT C15",  "iBUS (FlySky)"),
    "c15_sbus": ("CAT C15",  "SBUS (FrSky/Futaba)"),
    "8v92_pwm":  ("Detroit 8V92", "PWM (standard RC PPM)"),
    "8v92_ibus": ("Detroit 8V92", "iBUS (FlySky)"),
    "8v92_sbus": ("Detroit 8V92", "SBUS (FrSky/Futaba)"),
    "n14_pwm":   ("Cummins N14", "PWM (standard RC PPM)"),
    "n14_ibus":  ("Cummins N14", "iBUS (FlySky)"),
    "n14_sbus":  ("Cummins N14", "SBUS (FrSky/Futaba)"),
}

variants = sorted([
    os.path.splitext(f)[0]
    for f in os.listdir(FW)
    if f.endswith(".bin") and f not in ("bootloader.bin","partitions.bin")
])

index = []
for v in variants:
    pack, sub = LABELS.get(v, (v, ""))
    name = f"Poor Man's Beier - {pack} {sub}".strip()
    manifest = {
        "name": name,
        "version": "1.0",
        "new_install_prompt_erase": False,
        "builds": [{
            "chipFamily": "ESP32",
            "parts": [
                {"path": "firmware/bootloader.bin", "offset": 0x1000},
                {"path": "firmware/partitions.bin", "offset": 0x8000},
                {"path": f"firmware/{v}.bin",       "offset": 0x10000},
            ],
        }],
    }
    fname = f"manifest_{v}.json"
    with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    index.append({"id": v, "manifest": fname, "pack": pack, "sub": sub})
    print(f"  + {fname}  ({name})")

with open(os.path.join(OUT, "manifests.json"), "w", encoding="utf-8") as f:
    json.dump(index, f, indent=2)
print(f"Wrote {len(index)} manifests + manifests.json")
