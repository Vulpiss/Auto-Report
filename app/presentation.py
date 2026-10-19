from app.analyst_tools import compact_label,scope_text
from app.validation import currency_label
"""Offline PPTX export using a validated Artifact Tool template.
Only the standard library and existing chart dependencies are required at runtime.
"""
from io import BytesIO
import json
from pathlib import Path
import posixpath
import textwrap
import zipfile
import xml.etree.ElementTree as ET
from app.dashboard_model import VIEW_NAMES
from app.dashboard_render import board_png

A="http://schemas.openxmlformats.org/drawingml/2006/main"
P="http://schemas.openxmlformats.org/presentationml/2006/main"
R="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL="http://schemas.openxmlformats.org/package/2006/relationships"
CT="http://schemas.openxmlformats.org/package/2006/content-types"
for prefix,uri in (("a",A),("p",P),("r",R),("",CT)):
    ET.register_namespace(prefix,uri)
TEMPLATE=Path(__file__).resolve().parents[1]/"assets/dashboard-template.pptx"

def _xml(root):
    return ET.tostring(root,encoding="utf-8",xml_declaration=True)

def _resolve(part,target):
    return target.lstrip("/") if target.startswith("/") else posixpath.normpath(posixpath.join(posixpath.dirname(part),target))

def _rels(part):
    folder,name=posixpath.split(part)
    return folder+"/_rels/"+name+".rels"

def _replace(data,mapping):
    root=ET.fromstring(data)
    for node in root.iter("{"+A+"}t"):
        if node.text in mapping:node.text=mapping[node.text]
    return _xml(root)

def export_pptx(result, views=(0,1,2), *, grouping="Dzień", title="", comment=""):
    unit=currency_label(result["profile"])
    views=tuple(views)
    if result["status"]!="complete":raise ValueError("Brak pozycji do eksportu.")
    if not views or len(set(views))!=len(views) or any(type(v) is not int or v not in range(3) for v in views):
        raise ValueError("Wybierz od jednego do trzech różnych widoków.")
    if grouping not in ("Dzień","Tydzień","Miesiąc"):raise ValueError("Nieobsługiwane grupowanie.")
    if len(title)>45 or len(comment)>160:raise ValueError("Tytuł: do 45 znaków. Komentarz: do 160 znaków.")
    with zipfile.ZipFile(TEMPLATE) as z:
        files={name:z.read(name) for name in z.namelist()}
    presentation=ET.fromstring(files["ppt/presentation.xml"])
    pr=ET.fromstring(files["ppt/_rels/presentation.xml.rels"])
    ids=presentation.find("{"+P+"}sldIdLst")
    original=list(ids)
    links={x.get("Id"):x for x in pr}
    selected=set(views)
    removed=set()
    for i,item in enumerate(original):
        rid=item.get("{"+R+"}id")
        link=links[rid]
        part=_resolve("ppt/presentation.xml",link.get("Target"))
        relpart=_rels(part)
        relationships=ET.fromstring(files[relpart])
        if i not in selected:
            ids.remove(item);pr.remove(link);removed.update((part,relpart))
        for rel in relationships:
            target=_resolve(part,rel.get("Target"))
            kind=rel.get("Type","").split("/")[-1]
            if kind=="image":
                if i in selected:files[target]=board_png(result,i,grouping)
                else:removed.add(target)
            elif kind=="notesSlide":
                if i in selected:
                    metadata={key:result[key] for key in ("source_sha256","source_range","profile","selected_categories","coverage_start","coverage_end","kpis","comparison","quality","categories","business","dimensions","selected_products","selected_customers","comparison_mode")}
                    metadata.update(view=VIEW_NAMES[i],grouping=grouping,comment=comment,template_version="analyst-1")
                    files[target]=_replace(files[target],{"{{NOTES}}":json.dumps(metadata,ensure_ascii=False,default=str)})
                else:
                    removed.add(target)
                    removed.add(_rels(target))
        if i in selected:
            chosen="Wszystkie kategorie" if result["selected_categories"] is None else ", ".join(result["selected_categories"])
            label=textwrap.shorten(chosen,width=44,placeholder="… (pełny wybór w notatkach)")
            label=compact_label(scope_text(result),65)+" (pełny zakres w notatkach)"
            k=result["kpis"]
            subtitle=f"{k['start_date']} / {k['end_date']} | {unit} {result['profile']['amount_basis']} | {grouping} | {label}"
            prev=result["comparison"]["previous"]
            warning=f"Porównanie: {prev['start_date']} / {prev['end_date']}." if result["comparison"]["baseline_available"] else result["comparison"]["reason"]
            if result["profile"]["amount_basis"]=="nieokreślona":warning+=" Podstawa kwoty nieokreślona."
            if result["profile"].get("currency")=="XXX":warning+=" Waluta nieokreślona."
            if result["quality"].get("rounded_rows",0):warning+=" Kwoty: HALF_UP do 2 miejsc (szczegóły w notatkach)."
            footer=warning+(" | "+textwrap.shorten(comment,width=90,placeholder="…") if comment else "")
            heading=(title+" — " if title else "")+VIEW_NAMES[i]
            files[part]=_replace(files[part],{"{{TITLE}}":heading,"{{SUBTITLE}}":subtitle,"{{FOOTER}}":footer})
            root=ET.fromstring(files[part])
            for pic in root.findall(".//{"+P+"}pic"):
                transform=pic.find("{"+P+"}spPr/{"+A+"}xfrm")
                transform.find("{"+A+"}off").attrib.update(x=str(24*9525),y=str(100*9525))
                transform.find("{"+A+"}ext").attrib.update(cx=str(1232*9525),cy=str(554*9525))
            files[part]=_xml(root)
            if len(heading)>55:
                root=ET.fromstring(files[part])
                for shape in root.findall(".//{"+P+"}sp"):
                    if heading in [x.text for x in shape.iter("{"+A+"}t")]:
                        for run in shape.iter("{"+A+"}rPr"):run.set("sz","1800")
                files[part]=_xml(root)
    # Respect selection order without renumbering stable OOXML part names.
    for item in list(ids):ids.remove(item)
    for i in views:ids.append(original[i])
    files["ppt/presentation.xml"]=_xml(presentation)
    files["ppt/_rels/presentation.xml.rels"]=_xml(pr)
    content=ET.fromstring(files["[Content_Types].xml"])
    for node in list(content):
        if node.get("PartName","").lstrip("/") in removed:content.remove(node)
    files["[Content_Types].xml"]=_xml(content)
    # Keep package metadata consistent with the selected slide count.
    if "docProps/app.xml" in files:
        app=ET.fromstring(files["docProps/app.xml"])
        for node in app.iter():
            if node.tag.endswith("}Slides"):node.text=str(len(views))
        files["docProps/app.xml"]=_xml(app)
    output=BytesIO()
    with zipfile.ZipFile(output,"w",zipfile.ZIP_DEFLATED) as z:
        for name,data in files.items():
            if name not in removed:z.writestr(name,data)
    return output.getvalue()
