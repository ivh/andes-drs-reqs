# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Generate the flow-down diagram grid cells from flowdown.json."""
import html
import json

with open("flowdown.json") as f:
    data = json.load(f)
N = {n["name"]: n for n in data["nodes"]}

NOTES = {"[R-AND-112]": "also linked to SCAO work packages"}

def card(name, doc_cls, span=0):
    n = N[name]
    txt = html.escape(n["text"]).replace("\n", " ")
    note = f'<span class="note">{NOTES[name]}</span>' if name in NOTES else ""
    cls = f"card {doc_cls}" + (f" span{span}" if span else "")
    return (f'<div class="{cls}"><span class="rid">{html.escape(name)}</span>'
            f'<p>{txt}</p>{note}</div>')

EDGE_CLS = {"derive": "solid", "naming": "dashed"}

def conn(kind):
    lbl = '<em>implied</em>' if kind == "naming" else ""
    return f'<div class="conn {EDGE_CLS[kind]}">{lbl}</div>'

trs_chains = [
    ("[R-AND-65]", "derive", "[R-AND-65].3", "derive", "[R-AND-65].3.SW2"),
    ("[R-AND-70]", "derive", "[R-AND-70].1", "derive", "[R-AND-70].1.SW1"),
    ("[R-AND-88]", "derive", "[R-AND-88].1", "naming", "[R-AND-88].1.SW1"),
    ("[R-AND-112]", "derive", "[R-AND-112].1", "derive", "[R-AND-112].1.SW1"),
    ("[R-AND-114]", "derive", "[R-AND-114].1", "derive", "[R-AND-114].1.SW1"),
    ("[R-AND-115]", "derive", "[R-AND-115].1", "derive", "[R-AND-115].1.SW1"),
    ("[R-AND-119]", "derive", "[R-AND-119].1", "derive", "[R-AND-119].1.SW1"),
]

rows = []
rows.append('<div class="lvl c1">Document requirement</div>'
            '<div class="lvl c3">SW-level flow-down</div>'
            '<div class="lvl c5">DRS-level requirement</div>'
            '<div class="lvl c7">Work package</div>')

rows.append('<div class="ghead">ANDES Technical Requirements Specification'
            ' &mdash; ESO-published, architect flow-down</div>')
for l0, e1, l1, e2, l2 in trs_chains:
    rows.append(card(l0, "trs") + conn(e1) + card(l1, "trs") + conn(e2)
                + card(l2, "trs") + '<div class="conn solid stub"></div>')
rows.append(card("[R-AND-120]", "trs")
            + '<div class="conn solid direct"><em>applies directly</em></div>')

rows.append('<div class="ghead">Common Requirements for ELT Instruments'
            ' &mdash; ESO standard, local flow-down</div>')
tree = (card("[R-INS-896]", "ins", 3) + '<div class="conn solid span3"></div>'
        + card("[R-INS-896].1", "ins", 3))
for i, leaf in enumerate(["[R-INS-896].1.SW1", "[R-INS-896].1.SW2", "[R-INS-896].1.SW3"]):
    pos = ["btop", "bmid", "bbot"][i]
    tree += (f'<div class="conn dotted branch {pos}"><i class="v"></i><i class="ah"></i></div>'
             + card(leaf, "ins") + '<div class="conn solid stub"></div>')
rows.append(tree)
for name in ("[R-INS-928]", "[R-INS-1049]", "[R-INS-1050]"):
    rows.append(card(name, "ins")
                + '<div class="conn solid direct"><em>applies directly</em></div>')

with open("rows_fragment.html", "w") as f:
    f.write("\n".join(rows))
print("rows written")
