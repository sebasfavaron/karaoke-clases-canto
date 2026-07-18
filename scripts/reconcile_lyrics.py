"""
Reconcile the REAL lyrics text against WhisperX's (imperfect) transcription+timestamps,
producing final per-line/per-word timing for the actual correct words.

Why: Whisper mishears sung/artistic lyrics fairly often (measured ~84% direct word-match
on a Spanish indie track), so its own transcript isn't safe to show as "the lyrics" —
but its timestamps are still usable. This does a word-level sequence alignment
(difflib) between the real lyrics and Whisper's output, borrows the timestamp from each
matched Whisper word, and linearly interpolates timestamps for real words that didn't
match anything (typos/mishearings/insertions).

Usage:
    python3 reconcile_lyrics.py <lyrics.txt> <whisperx_align_output.json> <out.json> \\
        <slug> <artist> <title> <audio-path-in-repo>

lyrics.txt: plain text, one line per lyric line (blank lines are skipped/ignored).
Output matches this repo's data/<slug>.json schema with sync="word".
"""
import json
import re
import sys
import difflib
import unicodedata


def norm(w):
    w = w.lower().strip()
    w = re.sub(r'[^\w]', '', w, flags=re.UNICODE)
    w = ''.join(c for c in unicodedata.normalize('NFD', w) if unicodedata.category(c) != 'Mn')
    return w


def reconcile(lyrics_text, whisper_words):
    lines = [ln.strip().split() for ln in lyrics_text.strip('\n').split('\n') if ln.strip()]

    real_words_flat, real_line_idx = [], []
    for li, words in enumerate(lines):
        for w in words:
            real_words_flat.append(w)
            real_line_idx.append(li)
    real_norm = [norm(w) for w in real_words_flat]
    whisper_norm = [norm(w['word']) for w in whisper_words]

    sm = difflib.SequenceMatcher(None, real_norm, whisper_norm, autojunk=False)
    real_time = [None] * len(real_words_flat)
    direct_matches = 0
    for block in sm.get_matching_blocks():
        for k in range(block.size):
            ri, wi = block.a + k, block.b + k
            real_time[ri] = (whisper_words[wi]['start'], whisper_words[wi]['end'])
            direct_matches += 1

    n = len(real_time)
    i = 0
    while i < n:
        if real_time[i] is None:
            j = i
            while j < n and real_time[j] is None:
                j += 1
            prev_end = real_time[i - 1][1] if i > 0 and real_time[i - 1] else (whisper_words[0]['start'] if whisper_words else 0.0)
            next_start = real_time[j][0] if j < n and real_time[j] else (whisper_words[-1]['end'] if whisper_words else prev_end + 1)
            gap = max(next_start - prev_end, 0.01)
            span = j - i
            for k in range(span):
                real_time[i + k] = (
                    prev_end + gap * k / (span + 1),
                    prev_end + gap * (k + 1) / (span + 1),
                )
            i = j
        else:
            i += 1

    words_out = [
        {"word": w, "start": round(t0, 2), "end": round(t1, 2), "line": li}
        for w, (t0, t1), li in zip(real_words_flat, real_time, real_line_idx)
    ]
    lines_out = []
    for li, words in enumerate(lines):
        entries = [w for w in words_out if w["line"] == li]
        lines_out.append({
            "time": entries[0]["start"] if entries else 0.0,
            "text": " ".join(words),
            "words": [{"time": w["start"], "text": w["word"]} for w in entries],
        })
    return lines_out, direct_matches, n


def main():
    if len(sys.argv) != 8:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    lyrics_path, align_path, out_path, slug, artist, title, audio_rel_path = sys.argv[1:]

    lyrics_text = open(lyrics_path, encoding="utf-8").read()
    align = json.load(open(align_path, encoding="utf-8"))
    lines_out, direct_matches, total = reconcile(lyrics_text, align["words"])

    json.dump({
        "slug": slug,
        "artist": artist,
        "title": title,
        "audio": audio_rel_path,
        "sync": "word",
        "source": "whisperx-forced-alignment+lyrics-reconciliation",
        "lines": lines_out,
    }, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    print(f"matched {direct_matches}/{total} real words directly to whisper timestamps ({100*direct_matches/total:.0f}%)", file=sys.stderr)
    for l in lines_out:
        print(f"[{l['time']:.2f}] {l['text']}")
    print(f"\nwritten to {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
