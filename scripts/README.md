# Pipeline scripts for songs without LRCLIB coverage

When `https://lrclib.net/api/search?...` has no match for a song (common for
lesser-known/regional artists), use forced alignment instead of leaving it unsynced:

1. Get the isolated vocals stem from Demucs (`--two-stems vocals`, keep `vocals.mp3`
   this time instead of discarding it — cleaner signal than the full mix, much better
   alignment).
2. Fetch the real lyrics text from a public lyrics site (plain text, one line per lyric
   line). Don't rely on an AI summarizer tool for this — copyrighted lyrics reproduction
   gets refused at that layer; fetch the raw page HTML directly and parse out the lyrics
   block yourself.
3. Run `whisperx_align.py <vocals.mp3> <align.json> <lang>` on the laptop
   (`~/.cache/whisperx-venv`, MPS-capable, don't run this on the Pi — untested there and
   likely slow). This gives WhisperX's own (imperfect) transcription with word timestamps.
4. Run `reconcile_lyrics.py <lyrics.txt> <align.json> <out.json> <slug> <artist> <title>
   <audio-path>` to map the REAL lyrics words onto WhisperX's timestamps via sequence
   alignment (handles Whisper's mishearings/insertions via interpolation). Output is
   `data/<slug>.json` with `sync: "word"`, ready to drop in.

Measured on a 4-minute Spanish indie track: ~84% of real words matched a WhisperX word
directly; the rest interpolated between neighboring matches. Line-level timing came out
sane and usable; word-level highlighting works but individual word boundaries in the
interpolated stretches are approximate, not exact.
