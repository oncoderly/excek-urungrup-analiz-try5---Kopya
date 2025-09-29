import pathlib
pairs = {}
items = ['ğŸ“', 'ğŸ”', 'âš ï¸', 'âŒ']
for s in items:
    for enc in ('cp1254', 'cp1252', 'latin1'):
        try:
            txt = s.encode(enc).decode('utf-8')
            pairs[s] = txt
            break
        except Exception:
            continue

path = pathlib.Path('decoded_pairs.txt')
with path.open('w', encoding='utf-8') as f:
    for k, v in pairs.items():
        f.write(f"{k.encode('unicode_escape').decode()} -> {v.encode('unicode_escape').decode()}\n")
