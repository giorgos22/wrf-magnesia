from pathlib import Path
import re
import json

root = Path("/home/wrfuser/wrf-magnesia")
html = root / "index.html"

def entries(folder, pattern, kind):
    files = list((root / folder).glob("*.webp"))

    def hour(path):
        name = path.stem
        if kind == "dated":
            m = re.search(r"_(\d{4}-\d{2}-\d{2})_(\d{2})-00-00$", name)
            return m.group(1) + " " + m.group(2) + ":00" if m else name
        m = re.search(r"FH\+?(\d+)h?$", name)
        return int(m.group(1)) if m else 9999

    files.sort(key=hour)
    out = []
    for p in files:
        h = hour(p)
        if kind == "dated":
            label = h
            valid = h
            hour_value = len(out)
        else:
            hour_value = h if isinstance(h, int) else len(out)
            label = f"+{hour_value} ώρες"
            valid = f"Πρόγνωση +{hour_value} h"
        out.append({
            "hour": hour_value,
            "url": f"maps/{folder}/{p.name}",
            "label": label,
            "valid": valid
        })
    return out

maps = {
    "rain": [],
    "temp": entries("maps/temp/webp", "*.webp", "fh"),
    "wind": entries("maps/wind/webp", "*.webp", "fh"),
    "cloud": entries("maps/rain/webp", "*.webp", "dated")
}

replacement = "const maps=" + json.dumps(maps, ensure_ascii=False, separators=(",", ":")) + ";"
text = html.read_text(encoding="utf-8")
if not re.search(r"const maps=\{rain:\[\],temp:\[\],wind:\[\],cloud:\[\]\};", text):
    raise SystemExit("Δεν βρέθηκε η αναμενόμενη γραμμή maps. Δεν άλλαξε το index.html.")

backup = html.with_suffix(".html.bak")
backup.write_text(text, encoding="utf-8")
text = re.sub(r"const maps=\{rain:\[\],temp:\[\],wind:\[\],cloud:\[\]\};",
              lambda _: replacement, text, count=1)
html.write_text(text, encoding="utf-8")

print("Ενημερώθηκε το index.html.")
print("Νέφωση/βροχή:", len(maps["cloud"]))
print("Θερμοκρασία:", len(maps["temp"]))
print("Άνεμος:", len(maps["wind"]))
print("Συνολικός υετός:", len(maps["rain"]), "(δεν υπάρχουν ακόμη εικόνες)")
print("Αντίγραφο ασφαλείας:", backup.name)
