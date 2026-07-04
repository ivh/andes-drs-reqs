# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check: (1) RV/wavelength-cal requirements and where they flow;
(2) verification links on the 14 DRS WP requirements."""
import json
import pickle
import re

with open("model_index.pkl", "rb") as f:
    ix = pickle.load(f)
E, D, R, S = ix["elements"], ix["deps"], ix["requirements"], ix["stereo_of_dep"]

def doc_of(eid):
    parts = []
    while eid:
        e = E.get(eid)
        if not e:
            break
        parts.append(e["name"])
        eid = e["parent"]
    for i, p in enumerate(parts):
        if p == "0.Requirements" and i >= 1:
            return parts[i - 1]
    return parts[-2] if len(parts) >= 2 else ""

by_client, by_supplier = {}, {}
for did, d in D.items():
    for c in d["clients"]:
        by_client.setdefault(c, []).append(did)
    for s in d["suppliers"]:
        by_supplier.setdefault(s, []).append(did)

WP = "_2022x_1_ef20353_1686237423990_559313_159"

print("### RV / wavelength-calibration requirements in ANDES TRS:")
pat = re.compile(r"(radial velocity|\bRV\b|cm/s|m/s|wavelength calibration|wavelength accuracy)", re.I)
hits = []
for base, r in R.items():
    if not r["text"] or not pat.search(r["text"]):
        continue
    name = E.get(base, {}).get("name", "")
    doc = doc_of(base)
    if "ANDES Technical" not in doc:
        continue
    hits.append((name, base, r["text"]))
hits.sort()
for name, base, text in hits:
    # where does it flow (as supplier or client of DeriveReqt / plain deps)?
    targets = set()
    for did in by_client.get(base, []) + by_supplier.get(base, []):
        d = D[did]
        for o in d["clients"] + d["suppliers"]:
            if o != base:
                n = E.get(o, {}).get("name", "")
                if n:
                    targets.add(n)
    t = ", ".join(sorted(targets)[:8]) or "NO LINKS"
    print(f"  {name}: -> {t}")
    print(f"     {text[:150]}")

print("\n### Verification / satisfy links on the 14 WP requirements:")
with open("flowdown.json") as f:
    fd = json.load(f)
wp_reqs = fd["wp_reqs"]
for eid in wp_reqs:
    name = E.get(eid, {}).get("name", "")
    vlinks = []
    for did in by_client.get(eid, []) + by_supplier.get(eid, []):
        stereos = S.get(did, ["plain"])
        for st in stereos:
            if st in ("Verify", "Satisfy", "Refine", "Justify"):
                d = D[did]
                others = [E.get(o, {}).get("name", o) for o in d["clients"] + d["suppliers"] if o != eid]
                vlinks.append(f"{st} <-> {others}")
    print(f"  {name}: {vlinks if vlinks else 'none'}")

print("\n### 'Reduction Pipeline RV Error' element:")
for eid, e in E.items():
    if "RV Error" in (e["name"] or ""):
        parts = []
        p = eid
        while p:
            parts.append(E[p]["name"])
            p = E[p]["parent"]
        print(f"  {e['name']} ({e['type']})  path: {' < '.join(parts[1:5])}")
