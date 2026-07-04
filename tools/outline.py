# /// script
# requires-python = ">=3.11"
# dependencies = ["lxml"]
# ///
"""Outline the package tree and diagrams of a MagicDraw/Cameo XMI model."""
import sys
from lxml import etree

path = sys.argv[1]
max_depth = int(sys.argv[2]) if len(sys.argv) > 2 else 3

UML = "{http://www.omg.org/spec/UML/20131001}"
XMI = "{http://www.omg.org/spec/XMI/20131001}"

pkg_stack = []
diagrams = []

def emit(name, depth, kind):
    print("  " * depth + f"- {name}" + (f"  [{kind}]" if kind else ""))

for event, elem in etree.iterparse(path, events=("start", "end"), huge_tree=True):
    tag = elem.tag
    if event == "start" and tag == "packagedElement":
        t = elem.get(XMI + "type", "")
        if t == "uml:Package":
            name = elem.get("name", "(unnamed)")
            if len(pkg_stack) < max_depth:
                emit(name, len(pkg_stack), "")
            pkg_stack.append(name)
    elif event == "end":
        if tag == "packagedElement" and elem.get(XMI + "type") == "uml:Package":
            pkg_stack.pop()
        if elem.get(XMI + "type") == "uml:Diagram":
            diagrams.append(elem.get("name", "(unnamed)"))
        # free memory
        if tag == "packagedElement":
            elem.clear()

print(f"\n=== {len(diagrams)} diagrams (first 40) ===")
for d in diagrams[:40]:
    print("  ", d)
