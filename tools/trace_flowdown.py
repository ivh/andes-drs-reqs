# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Trace requirement flow-down upward from the SW DRS work-package requirements.
Upward edges: DeriveReqt deps, containment nesting, and naming convention
([X].1.SW1 -> [X].1 -> [X]). Dumps DAG as JSON."""
import json
import pickle
import re

with open("model_index.pkl", "rb") as f:
    ix = pickle.load(f)
E, D, R, S = ix["elements"], ix["deps"], ix["requirements"], ix["stereo_of_dep"]

def chain_list(eid):
    parts = []
    while eid:
        e = E.get(eid)
        if not e:
            break
        parts.append(e["name"] or "")
        eid = e["parent"]
    return parts

def doc_of(eid):
    parts = chain_list(eid)
    for i, p in enumerate(parts):
        if p == "0.Requirements" and i >= 1:
            return parts[i - 1]
    return parts[-2] if len(parts) >= 2 else ""

req_ids = set(R)
name_to_ids = {}
for eid, e in E.items():
    if e["name"]:
        name_to_ids.setdefault(e["name"], []).append(eid)

# --- upward edge collection ---
up = {}  # derived id -> list of (source id, kind)

for did, stereos in S.items():
    if "DeriveReqt" not in stereos:
        continue
    d = D.get(did)
    if not d:
        continue
    for c in d["clients"]:
        for s in d["suppliers"]:
            up.setdefault(c, []).append((s, "derive"))

def is_real_req(eid):
    # section headings are requirement-stereotyped too; real reqs have [R-...] names
    return eid in req_ids and E.get(eid, {}).get("name", "").startswith("[")

def nesting_parent(eid):
    p = E.get(eid, {}).get("parent")
    return p if p and is_real_req(p) else None

def naming_parent(eid):
    name = E.get(eid, {}).get("name", "")
    m = re.match(r"^(.*)\.[A-Za-z0-9]+$", name)
    if not m:
        return None
    parent_name = m.group(1)
    cands = [i for i in name_to_ids.get(parent_name, []) if is_real_req(i)]
    return cands[0] if cands else None

WP = "_2022x_1_ef20353_1686237423990_559313_159"  # SW DRS
wp_reqs = []
for did, d in D.items():
    if WP in d["clients"]:
        wp_reqs.extend(d["suppliers"])

nodes, edges = {}, []
edge_seen = set()

def add_node(eid):
    if eid in nodes:
        return
    e = E.get(eid, {})
    r = R.get(eid, {})
    nodes[eid] = {
        "id": eid,
        "name": e.get("name", "?"),
        "text": r.get("text", ""),
        "stereo": r.get("stereo", ""),
        "doc": doc_of(eid),
    }

def add_edge(src, dst, kind):
    if (src, dst) in edge_seen:
        return False
    edge_seen.add((src, dst))
    edges.append({"from": src, "to": dst, "kind": kind})
    return True

def walk_up(eid, depth=0):
    add_node(eid)
    if depth > 12:
        return
    ups = list(up.get(eid, []))
    if not ups:
        np_ = nesting_parent(eid)
        if np_:
            ups = [(np_, "nested")]
        else:
            nm = naming_parent(eid)
            if nm:
                ups = [(nm, "naming")]
    for src, kind in ups:
        if add_edge(src, eid, kind):
            walk_up(src, depth + 1)

for rid in wp_reqs:
    walk_up(rid)

# edges go source -> derived; a top-level source never appears as a derived end
derived_ends = {e["to"] for e in edges}
sources = {e["from"] for e in edges}
top = [eid for eid in nodes if eid in sources and eid not in derived_ends]
isolated = [eid for eid in wp_reqs if eid not in derived_ends and eid not in sources]

print(f"WP reqs: {len(wp_reqs)}, nodes: {len(nodes)}, edges: {len(edges)}")
print("\nTop-level sources:")
for eid in top:
    n = nodes[eid]
    print(f"  {n['name']}  [{n['doc']}]")
    # any other deps from these roots?
    for did, d in D.items():
        if eid in d["clients"]:
            st = ",".join(S.get(did, ["plain"]))
            for s in d["suppliers"]:
                print(f"     root as client --{st}--> {E.get(s, {}).get('name', s)} [{doc_of(s)}]")
print("\nIsolated WP reqs (no upward link found):")
for eid in isolated:
    print(f"  {nodes[eid]['name']}")

with open("flowdown.json", "w") as f:
    json.dump({"wp_reqs": wp_reqs, "nodes": list(nodes.values()), "edges": edges}, f, indent=1)
