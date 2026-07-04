# /// script
# requires-python = ">=3.11"
# dependencies = ["lxml"]
# ///
"""Index a MagicDraw/Cameo XMI model: elements, requirements, and
dependency-type relationships. Writes a pickle for downstream queries."""
import pickle
import sys
from lxml import etree

path = sys.argv[1]
out = sys.argv[2]

XMI = "{http://www.omg.org/spec/XMI/20131001}"

elements = {}        # id -> dict(name, type, parent)
deps = {}            # dep_id -> dict(clients=[], suppliers=[])
requirements = {}    # base_Class id -> dict(id_attr, text, stereo)
stereo_of_dep = {}   # dep/abstraction id -> stereotype name (DeriveReqt, Allocate, ...)
other_stereos = {}   # base element id -> [stereotype names]

DEP_TYPES = {"uml:Dependency", "uml:Abstraction", "uml:Realization", "uml:Usage"}
REQ_STEREOS = {
    "Requirement", "AstroMBSE_Requirement", "AstroMBSE_Interface_Requirement",
    "Test_Requirement", "AstroMBSE_Requirement_Local", "System_Requirement",
    "Justification",
}

stack = []  # element ids (or None) for parent tracking
cur_dep = []

for event, elem in etree.iterparse(path, events=("start", "end"), huge_tree=True):
    tag = elem.tag
    if event == "start":
        eid = elem.get(XMI + "id")
        etype = elem.get(XMI + "type", "")
        if eid and (etype or elem.get("name")):
            elements[eid] = {
                "name": elem.get("name", ""),
                "type": etype or tag,
                "parent": next((s for s in reversed(stack) if s), None),
            }
        stack.append(eid)
        if etype in DEP_TYPES and eid:
            deps[eid] = {"clients": [], "suppliers": [], "type": etype}
            # client/supplier may be space-separated attrs
            for attr, key in (("client", "clients"), ("supplier", "suppliers")):
                v = elem.get(attr)
                if v:
                    deps[eid][key].extend(v.split())
            cur_dep.append(eid)
        elif cur_dep and tag in ("client", "supplier"):
            ref = elem.get(XMI + "idref") or elem.get("href", "").split("#")[-1]
            if ref:
                deps[cur_dep[-1]][tag + "s"].append(ref)
    else:
        eid = stack.pop()
        etype = elem.get(XMI + "type", "")
        if etype in DEP_TYPES and cur_dep and cur_dep[-1] == eid:
            cur_dep.pop()
        # stereotype applications live at root level, tags namespaced by profile
        if tag.startswith("{http://www.omg.org/spec/SysML") or "magicdraw.com" in tag or "spec/Customization" in tag:
            local = tag.split("}")[1]
            base = None
            for k, v in elem.attrib.items():
                if k.startswith("base_"):
                    base = v
                    break
            if base:
                if local in REQ_STEREOS:
                    requirements[base] = {
                        "rid": elem.get("Id", ""),
                        "text": elem.get("Text", ""),
                        "stereo": local,
                    }
                elif base in deps or local in ("DeriveReqt", "Allocate", "Refine",
                                               "Satisfy", "Verify", "associatedElmnt",
                                               "Defines", "Trace"):
                    stereo_of_dep.setdefault(base, []).append(local)
                else:
                    other_stereos.setdefault(base, []).append(local)
        if tag == "packagedElement":
            elem.clear()

with open(out, "wb") as f:
    pickle.dump({"elements": elements, "deps": deps, "requirements": requirements,
                 "stereo_of_dep": stereo_of_dep, "other_stereos": other_stereos}, f)

print(f"elements: {len(elements)}")
print(f"deps: {len(deps)}")
print(f"requirements: {len(requirements)}")
print(f"stereotyped deps: {len(stereo_of_dep)}")
from collections import Counter
print(Counter(s for v in stereo_of_dep.values() for s in v).most_common(15))
