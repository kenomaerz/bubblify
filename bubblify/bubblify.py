from xml.etree import ElementTree as ET
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF, renderPM


def bubblify_preset(source: str, target: str, preset="cami"):
    preset = presets[preset]
    bubblify(source, preset[0], preset[1], target)


def bubblify(source: str, primary_color, bg_color, target: str):
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    tree = ET.parse(source)
    root = tree.getroot()

    coordinates = fix_viewbox(root.attrib["viewBox"])
    root.attrib["viewBox"] = coordinates["viewBox"]

    to_delete = []
    g = None
    for child in root:
        if child.tag == "{http://www.w3.org/2000/svg}g":
            g = child
        if child.tag == "{http://www.w3.org/2000/svg}text":
            to_delete.append(child)

    colorize(g, primary_color)
    insert_circle(root, coordinates, bg_color)

    for candidate in to_delete:
        root.remove(candidate)

    export(tree, target)


def colorize(g, color: str):
    for child in g:
        child.attrib["fill"] = color


def insert_circle(target, coords, color):
    c = ET.Element("circle")
    c.set("cx", str(((coords["x1"] - coords["x0"]) / 2) + coords["x0"]))
    c.set("cy", str(((coords["y1"] - coords["y0"]) / 2) + coords["y0"]))
    c.set("r", str((coords["x1"] - coords["x0"]) / 2))  # assume rect... dangerous
    c.set("fill", color)
    target.insert(0, c)


def fix_viewbox(viewbox: str):
    boxparts = viewbox.split(" ")
    for i in range(len(boxparts)):
        boxparts[i] = int(boxparts[i])
    result = {}
    result["x0"] = boxparts[0]
    result["y0"] = boxparts[1]
    result["x1"] = boxparts[2]
    result["y1"] = boxparts[3]

    # Make viewBbox square, this works on all nounproject icons images i have encountered yet
    result["y1"] = result["x1"]
    # build viewBox string
    result["viewBox"] = (
        str(result["x0"])
        + " "
        + str(result["y0"])
        + " "
        + str(result["x1"])
        + " "
        + str(result["y1"])
    )
    return result


def export(tree, target):
    tree.write(target)

    # currently throws exception, see https://github.com/deeplook/svglib/issues/205
    # drawing = svg2rlg("test2.svg")
    # renderPDF.drawToFile(drawing, "file.pdf")
    # renderPM.drawToFile(drawing, "file.png", fmt="PNG")


presets = {"cami": ["#FFFFFF", "#122B54"]}

