"""
Word-level forced alignment for a vocals-only audio stem, via WhisperX.

Run on the laptop's dedicated venv (~/.cache/whisperx-venv), NOT the Pi — needs a
real CPU/GPU budget. Input should be the isolated vocals stem from Demucs
(--two-stems vocals), not the full mix: much cleaner signal, much better alignment.

Usage:
    whisperx-venv/bin/python whisperx_align.py <vocals.mp3> <out.json> [language]

language defaults to "es". Output is raw Whisper-transcribed words with timestamps —
NOT the real lyrics (Whisper mishears things, especially sung/artistic phrasing).
Feed this output + the real lyrics text into reconcile_lyrics.py to get the final
per-line/per-word timing against the actual correct words.

Known environment gotchas (all handled below or required beforehand):
- pyannote's bundled VAD checkpoint predates torch 2.6's weights_only=True default
  and fails to load without a global torch.load patch (see below).
- `laptop-run`'s non-interactive SSH shell has a minimal PATH missing /opt/homebrew/bin
  (ffmpeg). Prefix the invocation with `export PATH="/opt/homebrew/bin:$PATH" &&`.
"""
import sys
import json
import torch
import whisperx

_orig_load = torch.load
def _patched_load(*a, **kw):
    kw["weights_only"] = False  # force override; caller (lightning_fabric) passes True explicitly
    return _orig_load(*a, **kw)
torch.load = _patched_load


def main():
    if len(sys.argv) < 3:
        print("usage: whisperx_align.py <vocals.mp3> <out.json> [language=es]", file=sys.stderr)
        sys.exit(2)
    audio_path, out_path = sys.argv[1], sys.argv[2]
    language = sys.argv[3] if len(sys.argv) > 3 else "es"

    device = "cpu"
    compute_type = "int8"

    print("loading model...", file=sys.stderr)
    model = whisperx.load_model("medium", device, compute_type=compute_type, language=language)

    print("transcribing...", file=sys.stderr)
    audio = whisperx.load_audio(audio_path)
    result = model.transcribe(audio, batch_size=8, language=language)

    print("raw transcription:", file=sys.stderr)
    for seg in result["segments"]:
        print(f"  [{seg['start']:.2f}-{seg['end']:.2f}] {seg['text']}", file=sys.stderr)

    print("aligning...", file=sys.stderr)
    align_model, align_metadata = whisperx.load_align_model(language_code=language, device=device)
    result_aligned = whisperx.align(result["segments"], align_model, align_metadata, audio, device, return_char_alignments=False)

    words = []
    for seg in result_aligned["segments"]:
        for w in seg.get("words", []):
            if "start" in w:
                words.append({"word": w["word"], "start": round(w["start"], 3), "end": round(w["end"], 3)})

    json.dump({
        "transcribed_text": " ".join(s["text"] for s in result["segments"]),
        "words": words,
    }, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    print(f"done, {len(words)} words aligned, written to {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
