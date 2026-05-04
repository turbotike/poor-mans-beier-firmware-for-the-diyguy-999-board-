"""
Regenerate playable .wav previews from the PROGMEM .h sound pack files.

Reads every .h in tools/sound_packs/<pack>/ and writes matching .wav files
to flasher/previews/<pack>/  (8-bit unsigned PCM mono @ <sample_rate> Hz).

Resolves alias headers (e.g. airbrake1.h -> #include "airbrake2.h") so that
preview shows the actual played sound.

Usage:  python tools\headers_to_wavs.py
"""

import os
import re
import struct
import sys

ROOT      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKS_DIR = os.path.join(ROOT, "tools", "sound_packs")
OUT_DIR   = os.path.join(ROOT, "flasher", "previews")

HEX_RE  = re.compile(r"0x([0-9A-Fa-f]{2})")
SR_RE   = re.compile(r"sample_rate\s*=\s*(\d+)")
INC_RE  = re.compile(r'#include\s+"([^"]+\.h)"')


def parse_header(path):
    """Return (rate, bytes, is_alias).
       is_alias=True if header has no own data array (it just #include's another).
    """
    with open(path, "r", encoding="ascii", errors="ignore") as f:
        text = f.read()
    sr_match = SR_RE.search(text)
    rate = int(sr_match.group(1)) if sr_match else 22050
    # strip block + line comments to avoid hex-looking comment text
    stripped = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    stripped = re.sub(r"//.*", "", stripped)
    # only take bytes inside the array braces
    m = re.search(r"_data\s*\[\s*\]\s*PROGMEM\s*=\s*\{(.*?)\}\s*;", stripped, re.S)
    if not m:
        return rate, None, True  # alias / empty
    body = m.group(1)
    data = bytes(int(h, 16) for h in HEX_RE.findall(body))
    return rate, (data if data else None), False


def resolve_alias(path, depth=0):
    """If header has no data array but #include's another header in same dir,
    follow that include (one level, max 3 hops)."""
    if depth > 3:
        return None
    rate, data, _ = parse_header(path)
    if data:
        return rate, data
    # try alias via #include
    with open(path, "r", encoding="ascii", errors="ignore") as f:
        text = f.read()
    for inc in INC_RE.findall(text):
        cand = os.path.join(os.path.dirname(path), os.path.basename(inc))
        if os.path.isfile(cand):
            r = resolve_alias(cand, depth + 1)
            if r:
                return r
    return None


def write_wav(out_path, rate, data):
    n = len(data)
    with open(out_path, "wb") as f:
        # RIFF header (8-bit unsigned PCM mono)
        f.write(b"RIFF")
        f.write(struct.pack("<I", 36 + n))
        f.write(b"WAVE")
        f.write(b"fmt ")
        f.write(struct.pack("<IHHIIHH", 16, 1, 1, rate, rate, 1, 8))
        f.write(b"data")
        f.write(struct.pack("<I", n))
        f.write(data)


def main():
    if not os.path.isdir(PACKS_DIR):
        sys.exit("sound_packs/ not found")
    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for pack in sorted(os.listdir(PACKS_DIR)):
        pack_dir = os.path.join(PACKS_DIR, pack)
        if not os.path.isdir(pack_dir):
            continue
        out_pack = os.path.join(OUT_DIR, pack)
        os.makedirs(out_pack, exist_ok=True)
        # wipe stale previews
        for old in os.listdir(out_pack):
            if old.endswith(".wav"):
                os.remove(os.path.join(out_pack, old))
        print(f"[{pack}]")
        SKIP = {"sounds"}  # master include, not a clip
        for h in sorted(os.listdir(pack_dir)):
            if not h.endswith(".h"):
                continue
            name = os.path.splitext(h)[0]
            if name in SKIP:
                continue
            # skip alias headers (they just #include another) - dedupes airbrake1/2/3 etc.
            _, _, is_alias = parse_header(os.path.join(pack_dir, h))
            if is_alias:
                print(f"  ~ {name:<14} (alias, skipped)")
                continue
            r = resolve_alias(os.path.join(pack_dir, h))
            if not r:
                print(f"  - {name:<14} (no data)")
                continue
            rate, data = r
            out = os.path.join(out_pack, name + ".wav")
            write_wav(out, rate, data)
            secs = len(data) / rate
            print(f"  + {name:<14} {secs:5.2f}s  {len(data)/1024:6.1f} KB")
            total += 1
    print(f"Done. {total} preview WAVs in {OUT_DIR}")


if __name__ == "__main__":
    main()
