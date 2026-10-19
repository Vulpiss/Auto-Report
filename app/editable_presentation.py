"""Native PowerPoint charts filled from an Artifact Tool-authored template."""
from io import BytesIO
from pathlib import Path
from decimal import Decimal
import json,zipfile,textwrap,copy
import xml.etree.ElementTree as E
from app.presentation import A,P,R,CT,_xml,_resolve,_rels,_replace
from app.dashboard_model import make_model,VIEW_NAMES
from app.validation import currency_label
from app.analyst_tools import compact_label,scope_text
from app.pdf_report import money
C="http://schemas.openxmlformats.org/drawingml/2006/chart"
S="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
TEMPLATE=Path(__file__).resolve().parents[1]/"assets/editable-template.pptx"

def chart_data(result,view,grouping,dimension="category"):
    model=make_model(result,grouping)
    if view==0:
        labels=[x["label"] for x in model["trend"]]
        series=[("Bieżący",[x["current"] for x in model["trend"]])]
        if result["comparison"]["baseline_available"]:series.append(("Poprzedni",[x["previous"] for x in model["trend"]]))
        return labels,series,"Wartość w czasie"
    if view==1:
        if dimension not in ("category","product","customer"):raise ValueError("Nieobsługiwany wymiar.")
        if dimension!="category":
            if dimension not in result.get("dimensions",{}):raise ValueError("Brak mapowania wybranego wymiaru.")
            source=result["dimensions"][dimension]
            top=source[:8]
            labels=[(str(i+1)+". "+str(r["entity"] if r["entity"] is not None else "(brak identyfikatora)")) for i,r in enumerate(top)]
            values=[r["difference"] for r in top]
            if len(source)>8:
                labels.append("Pozostałe ("+str(len(source)-8)+")")
                values.append(sum((r["difference"] for r in source[8:]),Decimal(0)) if result["comparison"]["baseline_available"] else None)
            title="Wkład "+("produktów" if dimension=="product" else "klientów")+" w zmianę"
        else:
            labels=[r["category"] for r in model["changes"]];values=[r["value"] for r in model["changes"]];title="Wkład kategorii w zmianę"
        return labels,[("Zmiana",values)],title
    q=result["quality"]
    return ["W widoku","Poza datami","Wykluczone filtrami"],[("Pozycje",[q["rows_in_period"],q["rows_outside_period"],q["rows_excluded_category"]])],"Rozliczenie filtrów"

def workbook(data,labels,series):
    with zipfile.ZipFile(BytesIO(data)) as z:parts={n:z.read(n) for n in z.namelist()}
    sheet=next(n for n in parts if n.startswith("xl/worksheets/") and n.endswith(".xml"))
    root=E.fromstring(parts[sheet]);body=root.find("{"+S+"}sheetData")
    body.clear()
    rows=[sum(([ "Kategoria",name] for name,_ in series),[])]
    for index,label in enumerate(labels):
        rows.append(sum(([label,values[index]] for _,values in series),[]))
    for ri,values in enumerate(rows,1):
        row=E.SubElement(body,"{"+S+"}row",r=str(ri))
        for ci,value in enumerate(values):
            if value is None:continue
            cell=E.SubElement(row,"{"+S+"}c",r=chr(65+ci)+str(ri))
            if isinstance(value,str):
                cell.set("t","inlineStr");E.SubElement(E.SubElement(cell,"{"+S+"}is"),"{"+S+"}t").text=value
            else:E.SubElement(cell,"{"+S+"}v").text=str(value)
    dimension=root.find("{"+S+"}dimension")
    if dimension is not None:dimension.set("ref","A1:"+chr(64+len(rows[0]))+str(len(rows)))
    parts[sheet]=_xml(root)
    out=BytesIO()
    with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as z:
        for n,v in parts.items():z.writestr(n,v)
    return out.getvalue()

def fill_chart(data,labels,series,view,omitted=0):
    root=E.fromstring(data)
    plot=root.find(".//{"+C+"}plotArea")
    kind=next(n for n in plot if n.tag in ("{"+C+"}lineChart","{"+C+"}barChart"))
    if view==0 and omitted:
        kind.tag="{"+C+"}barChart"
        kind.insert(0,E.Element("{"+C+"}barDir",val="col"))
        kind.find("{"+C+"}grouping").set("val","clustered")
    old=kind.findall("{"+C+"}ser")
    if view==1:
        prototype=copy.deepcopy(old[0])
        for index in range(len(old),len(series)):
            clone=copy.deepcopy(prototype)
            clone.find("{"+C+"}idx").set("val",str(index))
            clone.find("{"+C+"}order").set("val",str(index))
            palette=("2786E2","21A4A4","DBA752","8A79C7","8498AD","AA5566","559955","7755AA","555555")
            for color in clone.iter("{"+A+"}srgbClr"):color.set("val",palette[index%len(palette)])
            kind.insert(list(kind).index(old[-1])+index,clone)
        old=kind.findall("{"+C+"}ser")
        chart=root.find("{"+C+"}chart")
        legend=E.SubElement(chart,"{"+C+"}legend")
        E.SubElement(legend,"{"+C+"}legendPos",val="b")
        E.SubElement(legend,"{"+C+"}overlay",val="0")
        props=E.SubElement(legend,"{"+C+"}txPr")
        E.SubElement(props,"{"+A+"}bodyPr");E.SubElement(props,"{"+A+"}lstStyle")
        run=E.SubElement(E.SubElement(E.SubElement(props,"{"+A+"}p"),"{"+A+"}pPr"),"{"+A+"}defRPr",sz="1200")
        E.SubElement(run,"{"+A+"}latin",typeface="Arial")
        chart.remove(legend);chart.insert(list(chart).index(plot)+1,legend)
        plot.find("{"+C+"}catAx/{"+C+"}delete").set("val","1")

    for i,ser in enumerate(old):
        if i>=len(series):kind.remove(ser);continue
        if view==0:
            marker=ser.find("{"+C+"}marker")
            if omitted:
                if marker is not None:ser.remove(marker)
            elif marker is not None:
                marker.find("{"+C+"}symbol").set("val","circle")
                E.SubElement(marker,"{"+C+"}size",val="5")
                E.SubElement(ser,"{"+C+"}smooth",val="0")
        if kind.tag=="{"+C+"}barChart":
            inverse=ser.find("{"+C+"}invertIfNegative")
            if inverse is None:
                inverse=E.Element("{"+C+"}invertIfNegative",val="0")
                position=next((j for j,n in enumerate(ser) if n.tag in ("{"+C+"}cat","{"+C+"}val")),len(ser))
                ser.insert(position,inverse)
            inverse.set("val","0")
        name,values=series[i]
        tx=ser.find("{"+C+"}tx");tx.clear();E.SubElement(tx,"{"+C+"}v").text=name
        for typ,cachetype,col,items in (("cat","str",chr(65+2*i),labels),("val","num",chr(66+2*i),values)):
            node=ser.find("{"+C+"}"+typ);node.clear()
            ref=E.SubElement(node,"{"+C+"}"+cachetype+"Ref")
            E.SubElement(ref,"{"+C+"}f").text=f"'Chart Data'!${col}$2:${col}${len(labels)+1}"
            cache=E.SubElement(ref,"{"+C+"}"+cachetype+"Cache")
            if cachetype=="num":E.SubElement(cache,"{"+C+"}formatCode").text="0" if view==2 else "#,##0.00"
            E.SubElement(cache,"{"+C+"}ptCount",val=str(len(items)))
            for j,value in enumerate(items):
                if value is not None:E.SubElement(E.SubElement(cache,"{"+C+"}pt",idx=str(j)),"{"+C+"}v").text=str(value)
    if view==0:
        plot.find("{"+C+"}catAx/{"+C+"}axPos").set("val","b")
        plot.find("{"+C+"}valAx/{"+C+"}axPos").set("val","l")
    if view==1:
        labels_node=kind.find("{"+C+"}dLbls")
        if labels_node is not None:
            labels_node.find("{"+C+"}showVal").set("val","1")
            labels_node.insert(0,E.Element("{"+C+"}dLblPos",val="outEnd"))
            for run in labels_node.iter("{"+A+"}defRPr"):run.set("sz","1200")
        numbers=[v for _,values in series for v in values]
        span=max(numbers)-min(min(numbers),0)
        step=Decimal(10)**(span.adjusted() if span else 0)
        from decimal import ROUND_CEILING,ROUND_FLOOR
        maximum=(max(max(numbers),0)*Decimal("1.5")/step).to_integral_value(rounding=ROUND_CEILING)*step or step
        minimum=(min(min(numbers),0)*Decimal("1.3")/step).to_integral_value(rounding=ROUND_FLOOR)*step
        axis=plot.find("{"+C+"}valAx")
        scale=axis.find("{"+C+"}scaling")
        E.SubElement(scale,"{"+C+"}max",val=str(maximum))
        E.SubElement(scale,"{"+C+"}min",val=str(minimum))
        cross=axis.find("{"+C+"}crossAx")
        axis.insert(list(axis).index(cross)+1,E.Element("{"+C+"}crosses",val="min"))
        E.SubElement(axis,"{"+C+"}majorUnit",val=str(step))
    if view==2:
        from math import ceil
        largest=max(float(v) for _,values in series for v in values)
        E.SubElement(plot.find("{"+C+"}valAx"),"{"+C+"}majorUnit",val=str(max(1,ceil(largest/6))))
        for fmt in root.iter("{"+C+"}numFmt"):fmt.set("formatCode","0")
    if view!=2:
        maximum=max(abs(float(v)) for _,values in series for v in values)
        code='#,##0.0,,," mld"' if maximum>=1e9 else '#,##0.0,," mln"' if maximum>=1e6 else '#,##0.0," tys."' if maximum>=1e4 else '#,##0.00'
        axis=plot.find("{"+C+"}valAx")
        fmt=axis.find("{"+C+"}numFmt")
        if fmt is not None:
            fmt.set("formatCode",code);fmt.set("sourceLinked","0")
        labels_node=kind.find("{"+C+"}dLbls")
        if labels_node is not None:
            fmt=labels_node.find("{"+C+"}numFmt")
            if fmt is None:fmt=E.SubElement(labels_node,"{"+C+"}numFmt")
            fmt.set("formatCode",code);fmt.set("sourceLinked","0")
    if len(series)==1 and view!=1:
        chart=root.find("{"+C+"}chart")
        legend=chart.find("{"+C+"}legend")
        if legend is not None:chart.remove(legend)
    # Bound dense date-axis labels, retaining every data point in the workbook.
    cat_axis=plot.find("{"+C+"}catAx")
    E.SubElement(cat_axis,"{"+C+"}tickLblSkip",val=str((len(labels)+11)//12) if view==0 and len(labels)>16 else "1")
    position=E.Element("{"+C+"}tickLblPos",val="low")
    before=next((i for i,n in enumerate(cat_axis) if n.tag in ("{"+C+"}spPr","{"+C+"}txPr","{"+C+"}crossAx")),len(cat_axis))
    cat_axis.insert(before,position)
    return _xml(root)

def export_editable(result,views=(0,1,2),*,grouping="Dzień",title="",comment="",dimension="category"):
    views=tuple(views)
    if result["status"]!="complete" or not views or len(set(views))!=len(views) or any(type(v)!=int or v not in range(3) for v in views):raise ValueError("Wybierz od jednego do trzech widoków z danymi.")
    if len(title)>45 or len(comment)>160:raise ValueError("Tytuł do 45 znaków, komentarz do 160.")
    with zipfile.ZipFile(TEMPLATE) as z:parts={n:z.read(n) for n in z.namelist()}
    presentation=E.fromstring(parts["ppt/presentation.xml"]);ids=presentation.find("{"+P+"}sldIdLst");original=list(ids)
    rels=E.fromstring(parts["ppt/_rels/presentation.xml.rels"]);links={r.get("Id"):r for r in rels}
    removed=set()
    unit=currency_label(result["profile"])
    for view,item in enumerate(original):
        link=links[item.get("{"+R+"}id")];part=_resolve("ppt/presentation.xml",link.get("Target"))
        slide_rels=E.fromstring(parts[_rels(part)])
        selected=view in views
        if not selected:rels.remove(link);removed.update((part,_rels(part)))
        labels,series,heading=chart_data(result,view,grouping,dimension if view==1 else "category")
        valid=[i for i in range(len(labels)) if all(values[i] is not None for _,values in series)]
        omitted=len(labels)-len(valid)
        labels=[labels[i] for i in valid]
        series=[(name,[values[i] for i in valid]) for name,values in series]
        if view==0 and omitted:heading="Wartość dostępnych okresów"
        if view==1 and labels:
            series=[(compact_label(label,40),[value]) for label,value in zip(labels,series[0][1])]
            labels=["Zmiana"]

        for rel in list(slide_rels):
            target=_resolve(part,rel.get("Target"));kind=rel.get("Type","").split("/")[-1]
            if kind=="chart":
                chart_rels=E.fromstring(parts[_rels(target)])
                embedded=next(_resolve(target,x.get("Target")) for x in chart_rels if x.get("Type","").endswith("/package"))
                if selected and labels:
                    parts[target]=fill_chart(parts[target],labels,series,view,omitted)
                    parts[embedded]=workbook(parts[embedded],labels,series)
                else:
                    removed.update((target,_rels(target),embedded))
                    slide_rels.remove(rel)
            if kind=="notesSlide":
                if selected:
                    metadata={k:v for k,v in result.items() if k not in ("rows","category_daily")}
                    metadata.update(comment=comment,grouping=grouping,dimension=dimension,template_version="editable-1")
                    parts[target]=_replace(parts[target],{"{{NOTES}}":json.dumps(metadata,ensure_ascii=False,default=str)})
                else:removed.update((target,_rels(target)))
        if selected:
            parts[_rels(part)]=_xml(slide_rels)
            k=result["kpis"];b=result.get("business",{})
            metrics=f"Wartość: {money(k['total_value'])} {unit}  |  Pozycje: {k['rows_cnt']}"
            if b.get("orders") is not None:metrics+=f"  |  Dokumenty: {b['orders']}"
            if b.get("profit") is not None:metrics+=f"  |  Zysk: {money(b['profit'])} {unit}"
            scope="Wszystkie kategorie" if result["selected_categories"] is None else "Wybrane kategorie"
            if result.get("selected_products"):scope+="; filtr produktów"
            if result.get("selected_customers"):scope+="; filtr klientów"
            scope=compact_label(scope_text(result),105)
            subtitle=f"{k['start_date']} – {k['end_date']} | {unit} / {result['profile']['amount_basis']} | {grouping}\n{scope}; pełny wybór w notatkach"
            cmp=result["comparison"];prev=cmp["previous"]
            footer=f"{cmp.get('mode','Poprzedni okres')}: {prev['start_date']} – {prev['end_date']}." if cmp["baseline_available"] else "Porównanie N/A: niepełne dane lub niepotwierdzone pokrycie."
            if not result["coverage_current"]:footer+=" Bieżący zakres niepotwierdzony."
            if result["profile"]["amount_precision"]=="half_up":footer+=" Kwoty HALF_UP do 2 miejsc."
            if omitted and view==0:footer+=f" Pominięto {omitted} okresów bez potwierdzonej kompletności; brak nie oznacza zera."
            if comment:footer+="\n"+textwrap.shorten(comment,width=110,placeholder="… (pełny komentarz w notatkach)")
            heading=(title+" — " if title else "")+heading
            parts[part]=_replace(parts[part],{"{{TITLE}}":heading,"{{SUBTITLE}}":subtitle,"{{METRICS}}":metrics,"{{FOOTER}}":footer})
            if not labels:
                node=E.fromstring(parts[part]);tree=node.find("{"+P+"}cSld/{"+P+"}spTree")
                for frame in list(tree):
                    if frame.tag=="{"+P+"}graphicFrame":tree.remove(frame)
                shape=next(shape for shape in tree.findall("{"+P+"}sp") if metrics in [x.text for x in shape.iter("{"+A+"}t")])
                message=copy.deepcopy(shape)
                message.find("{"+P+"}nvSpPr/{"+P+"}cNvPr").set("id","999")
                transform=message.find("{"+P+"}spPr/{"+A+"}xfrm")
                transform.find("{"+A+"}off").set("y",str(290*9525))
                transform.find("{"+A+"}ext").set("cy",str(150*9525))
                for i,text in enumerate(message.iter("{"+A+"}t")):text.text="Brak podstaw do wykresu. Sprawdź kompletność danych i zakres porównania." if i==0 else ""
                tree.append(message);parts[part]=_xml(node)
            if len(heading)>60:
                node=E.fromstring(parts[part])
                for shape in node.findall(".//{"+P+"}sp"):
                    if heading in [t.text for t in shape.iter("{"+A+"}t")]:
                        for run in shape.iter("{"+A+"}rPr"):run.set("sz","2000")
                parts[part]=_xml(node)
    ids.clear()
    for view in views:ids.append(original[view])
    parts["ppt/presentation.xml"]=_xml(presentation);parts["ppt/_rels/presentation.xml.rels"]=_xml(rels)
    content=E.fromstring(parts["[Content_Types].xml"])
    for node in list(content):
        if node.get("PartName","").lstrip("/") in removed:content.remove(node)
    parts["[Content_Types].xml"]=_xml(content)
    app=E.fromstring(parts["docProps/app.xml"])
    for node in app.iter():
        if node.tag.endswith("}Slides"):node.text=str(len(views))
    parts["docProps/app.xml"]=_xml(app)
    out=BytesIO()
    with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as z:
        for n,v in parts.items():
            if n not in removed:z.writestr(n,v)
    return out.getvalue()
