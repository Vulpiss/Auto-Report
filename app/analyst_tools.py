"""Small deterministic helpers for analyst navigation and visible report scope."""
def compact_label(value, limit=42):
    text=str(value)
    return text if len(text)<=limit else text[:limit-1]+"…"

def driver_page(rows, query="", direction="Wszystkie", page=1, size=20):
    selected=[r for r in rows if query.casefold() in str(r["entity"] if r["entity"] is not None else "(brak identyfikatora)").casefold()]
    if direction=="Spadki": selected=[r for r in selected if r["difference"] is not None and r["difference"]<0]
    elif direction=="Wzrosty": selected=[r for r in selected if r["difference"] is not None and r["difference"]>0]
    selected=sorted(selected,key=lambda r:(-abs(r["difference"] if r["difference"] is not None else r["current"]),str(r["entity"])))
    pages=max(1,(len(selected)+size-1)//size)
    page=min(max(1,page),pages)
    return selected[(page-1)*size:page*size],len(selected),pages,page

def scope_text(result):
    parts=[]
    for key,label in (("selected_categories","Kategorie"),("selected_products","Produkty"),("selected_customers","Klienci")):
        values=result.get(key)
        if values:
            text=", ".join(str(x) for x in values[:2])
            if len(values)>2:text+=f" (+{len(values)-2})"
            parts.append(label+": "+compact_label(text,48))
    return " / ".join(parts) if parts else "Wszystkie kategorie, produkty i klienci"
