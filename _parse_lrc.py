import json, re, sys

def parse_lrc(lrc_text):
    lines = []
    pattern = re.compile(r'\[(\d{2}):(\d{2}\.\d{2})\]\s*(.*)')
    for raw in lrc_text.split('\n'):
        m = pattern.match(raw)
        if not m:
            continue
        mm, ss, text = m.groups()
        t = int(mm) * 60 + float(ss)
        text = text.strip()
        if text:
            lines.append({"time": round(t, 2), "text": text})
    return lines

def convert(raw_path, entry_index, out_path, slug, artist, title, audio_file):
    data = json.load(open(raw_path))
    entry = data[entry_index]
    lines = parse_lrc(entry.get("syncedLyrics") or "")
    out = {
        "slug": slug,
        "artist": artist,
        "title": title,
        "audio": audio_file,
        "duration": entry.get("duration"),
        "sync": "line",
        "source": "lrclib.net",
        "lines": lines,
    }
    json.dump(out, open(out_path, "w"), ensure_ascii=False, indent=2)
    print(f"{slug}: {len(lines)} synced lines")

convert(f"{sys.argv[1]}/data/_raw_stop_this_train.json", 0, f"{sys.argv[1]}/data/john-mayer-stop-this-train.json",
        "john-mayer-stop-this-train", "John Mayer", "Stop This Train", "audio/john-mayer-stop-this-train.mp3")
convert(f"{sys.argv[1]}/data/_raw_best_part.json", 0, f"{sys.argv[1]}/data/jordan-rakei-best-part.json",
        "jordan-rakei-best-part", "Jordan Rakei", "Best Part (Maida Vale Session)", "audio/jordan-rakei-best-part.mp3")
