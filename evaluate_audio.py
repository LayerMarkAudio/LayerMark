"""Evaluate distributed mono PCM16 WAV files without external dependencies."""

from __future__ import annotations

import argparse
import array
import json
import math
import sys
import wave
from pathlib import Path


def read_wav(path: Path) -> tuple[int, list[float]]:
    with wave.open(str(path), "rb") as audio:
        if audio.getnchannels() != 1 or audio.getsampwidth() != 2:
            raise ValueError(f"{path.name}: expected mono, 16-bit PCM WAV")
        rate = audio.getframerate()
        raw = audio.readframes(audio.getnframes())
    samples = array.array("h", raw)
    if sys.byteorder != "little":
        samples.byteswap()
    if not samples:
        raise ValueError(f"{path.name}: audio is empty")
    return rate, [value / 32768.0 for value in samples]


def compare(reference: Path, candidate: Path) -> dict:
    ref_rate, ref = read_wav(reference)
    rate, audio = read_wav(candidate)
    if rate != ref_rate or len(audio) != len(ref):
        raise ValueError(f"{candidate.name}: sample rate and length must match reference")
    power = math.fsum(value * value for value in ref) / len(ref)
    error = math.fsum((a - b) ** 2 for a, b in zip(ref, audio)) / len(ref)
    snr = 10 * math.log10(power / error) if power > 0 and error > 0 else None
    return {
        "file": candidate.name,
        "sample_rate": rate,
        "duration_seconds": round(len(audio) / rate, 6),
        "snr_db": round(snr, 4) if snr is not None else None,
        "snr_status": "finite" if snr is not None else (
            "undefined_silent_reference" if power == 0 else "identical_infinite_snr"
        ),
        "mean_absolute_error": math.fsum(abs(a - b) for a, b in zip(ref, audio)) / len(ref),
        "peak_magnitude": max(abs(value) for value in audio),
        "full_scale_fraction": sum(abs(value) >= 32767 / 32768 for value in audio) / len(audio),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", type=Path)
    parser.add_argument("candidates", type=Path, nargs="+")
    args = parser.parse_args()
    try:
        results = [compare(args.reference, path) for path in args.candidates]
    except (OSError, ValueError, wave.Error) as error:
        parser.exit(1, f"Error: {error}\n")
    print(json.dumps(results, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
