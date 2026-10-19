from app.validation import currency_label
"""Native, interactive Streamlit charts using the shared dashboard model."""
import streamlit as st
import pandas as pd
import altair as alt
from app.dashboard_model import COLORS, table_page
from app.pdf_report import money, percent
from app.analyst_tools import compact_label,driver_page

def render_view(result, model, view):
    unit=currency_label(result["profile"])
    colors=list(COLORS)
    def panel(title):
        st.subheader(title)
    def draw(chart,height=380):
        st.altair_chart(chart.properties(height=560 if st.session_state.get("presentation_mode") else height).configure_view(strokeWidth=0).configure_axis(labelFontSize=12,titleFontSize=13).configure_legend(labelFontSize=12,titleFontSize=12),width="stretch")
    def bars(rows,label,value):
        if not rows or all(r[value] is None for r in rows):
            st.info(result["comparison"]["reason"]);return
        data=[{label:r[label],"Kwota":float(r[value]) if r[value] is not None else None,"Dokładna kwota":money(r[value])} for r in rows]
        draw(alt.Chart(pd.DataFrame(data)).mark_bar(color=colors[0],cornerRadiusEnd=3).encode(
            x=alt.X("Kwota:Q",title=f"{unit}",scale=alt.Scale(zero=True)),
            y=alt.Y(label+":N",sort=None,title=None,axis=alt.Axis(labelLimit=200)),
            tooltip=[label,"Dokładna kwota"]))
    def trend(count=False):
        rows=[]
        for n,t in enumerate(model["trend"]):
            for key,name in ([("rows_cnt","Liczba pozycji")] if count else [("current","Bieżący"),("previous","Poprzedni")]):
                if key=="previous" and not result["comparison"]["baseline_available"]:continue
                v=t[key]
                rows.append({"Dzień okresu":n+1,"Okres":t["label"] if key!="previous" else t["previous_label"],
                             "Seria":name,"Wartość":float(v) if v is not None else None,
                             "Dokładna wartość":str(v) if count else money(v),"Status":t["state"]})
        draw(alt.Chart(pd.DataFrame(rows)).mark_line(point=True,invalid="break-paths-filter-domains").encode(
            x=alt.X("Dzień okresu:Q",title="Kolejna jednostka okresu",axis=alt.Axis(tickMinStep=1)),
            y=alt.Y("Wartość:Q",title="Pozycje" if count else f"{unit}",scale=alt.Scale(zero=True)),
            color=alt.Color("Seria:N",scale=alt.Scale(domain=["Liczba pozycji"] if count else ["Bieżący","Poprzedni"] if result["comparison"]["baseline_available"] else ["Bieżący"],range=[colors[0]] if count else [colors[0],"#aabed3"]),legend=alt.Legend(orient="bottom")),
            tooltip=["Okres","Seria","Dokładna wartość","Status"]))
    def structure():
        rows=[dict(Okres=x["label"],Kategoria=x["category"],Kwota=float(x["value"]) if x["value"] is not None else None,
                   Dokładnie=money(x["value"]),Znak=x["sign"]) for x in model["structure"]]
        draw(alt.Chart(pd.DataFrame(rows)).mark_bar().encode(
            x=alt.X("Okres:O",title=None,axis=alt.Axis(labelLimit=100,labelAngle=-30,values=[x["label"] for x in model["trend"]][::max(1,(len(model["trend"])+11)//12)])),
            y=alt.Y("Kwota:Q",stack="zero",title=f"{unit}",scale=alt.Scale(zero=True)),
            color=alt.Color("Kategoria:N",scale=alt.Scale(domain=model["category_labels"],range=colors[:len(model["category_labels"])]),legend=alt.Legend(orient="bottom",labelLimit=260,columns=3)),
            detail="Znak:N",tooltip=["Okres","Kategoria","Dokładnie","Znak"]))
    def table():
        pages=max(1,(len(model["table"])+99)//100)
        key=f"category_page_{view}"
        st.session_state[key]=min(max(1,st.session_state.get(key,1)),pages)
        page=st.number_input("Strona kategorii (100 pozycji)",1,pages,key=key)
        st.caption(f"Kategorie: {len(model['table'])}. Kolejność: wartość bieżąca malejąco. Wybór strony nie zmienia filtrów ani eksportu.")
        rows=[{"Kategoria":c["category"],f"Wartość {unit}":money(c["value"]),f"Poprzednio {unit}":money(c["previous"]),
               f"Różnica {unit}":money(c["difference"]),"Zmiana":percent(c["change"]),"Pozycje":c["rows_cnt"],f"Średnia {unit}":money(c["avg"]),"Trend":c["spark"]}
              for c in table_page(result,model,(page-1)*100)]
        st.dataframe(rows,hide_index=True,width="stretch",height=350,
                     column_config={"Trend":st.column_config.LineChartColumn("Trend",width="small")})
    for box,(label,value,previous,change) in zip(st.columns(3),model["cards"][view]):
        box.metric(label,value,change if change else None,delta_color="off")
        box.caption(previous)
    if view==0:render_business(result,view)
    with st.container(border=True,key=f"panel_{view}_0"):
        panel(["Bieżący i poprzedni okres","Wkład kategorii w zmianę","Obecność pozycji"][view])
        if view==0:trend()
        elif view==1:
            bars(model["changes"],"category","value")
            st.caption("Do 5 kategorii i suma pozostałych. Różnice nie wyjaśniają przyczyn.")
        else:
            data=[dict(Data=x["event_date"],Pozycje=x["rows_cnt"],Status=x["state"]) for x in result["daily"]]
            draw(alt.Chart(pd.DataFrame(data)).mark_rect().encode(
                x=alt.X("Data:O",title=None,axis=alt.Axis(labelAngle=-30)),
                color=alt.Color("Status:N",scale=alt.Scale(domain=["Brak danych o kompletności","Brak pozycji","Pozycje"],range=["#e6edf4","#72afd0","#123c72"]),legend=alt.Legend(orient="bottom")),
                tooltip=["Data","Pozycje","Status"]),180)
            st.caption("Obecność rekordów nie dowodzi kompletności eksportu.")
    with st.container(border=True,key=f"panel_{view}_1"):
        panel(["Największe wartości","Struktura wartości w czasie","Rozliczenie filtrów"][view])
        if view==0:bars([dict(category=r["category"],value=r["total_value"]) for r in model["rank"]],"category","value")
        elif view==1:structure()
        else:
            q=result["quality"]
            rows=[{"Zakres":name,"Rekordy":q[key]} for name,key in [("W widoku","rows_in_period"),("Poza datami","rows_outside_period"),("Wykluczone filtrami","rows_excluded_category")]]
            draw(alt.Chart(pd.DataFrame(rows)).mark_bar(color=colors[0]).encode(x="Rekordy:Q",y=alt.Y("Zakres:N",title=None),tooltip=["Zakres","Rekordy"]))
    with st.container(border=True,key=f"panel_{view}_2"):
        panel(["Struktura wartości w czasie","Porównanie kategorii","Liczba pozycji w czasie"][view])
        if view==0:structure()
        elif view==1:
            rows=[{"Kategoria":x["category"],"Okres":name,"Kwota":float(value),"Dokładnie":money(value)}
                  for x in model["table"][:8] for name,value in [("Bieżący",x["value"]),("Poprzedni",x["previous"])] if value is not None]
            draw(alt.Chart(pd.DataFrame(rows)).mark_bar().encode(x=alt.X("Kwota:Q",title=f"{unit}"),y=alt.Y("Kategoria:N",title=None,sort=None,axis=alt.Axis(labelLimit=150)),
                 yOffset="Okres:N",color=alt.Color("Okres:N",scale=alt.Scale(domain=["Bieżący","Poprzedni"],range=[colors[0],"#aabed3"]),legend=alt.Legend(orient="bottom")),tooltip=["Kategoria","Okres","Dokładnie"]))
            st.caption("Do 8 kategorii; pełna tabela poniżej.")
        else:trend(count=True)
    with st.container(border=True,key=f"panel_{view}_3"):
        panel("Reguły interpretacji" if view==2 else "Kategorie w liczbach")
        if view!=2:table()
        else:
            q=result["quality"]
            st.write("Pełny eksport: "+str(result["coverage_start"] or "nie podano")+" / "+str(result["coverage_end"] or "nie podano"))
            st.write(f"Kwota: {unit} / "+result["profile"]["amount_basis"])
            st.write(f"Identyczne pełne wiersze: {q.get('exact_duplicate_rows', 0)}. Puste linie: {q.get('blank_lines', 0)}.")
            st.write(f"Powtórzenia daty, kwoty i kategorii: {q['duplicate_rows']} — zachowane.")
            st.write(f"Kwoty ujemne w widoku: {q['view_negative_count']}.")
            if q.get("rounded_rows",0):
                st.caption(f"Zaokrąglono w źródle: {q['rounded_rows']}; wpływ {q['rounding_delta']} {unit}.")
            st.caption(result["comparison"]["reason"])
            st.caption("Brak danych i zero mają odrębne znaczenie. Liczba pozycji nie jest liczbą zamówień.")

def render_business(result,view):
    from app.business import business_notes
    b=result.get("business",{})
    unit=currency_label(result["profile"])
    if view==0 and any(v is not None for v in b.values()):
        st.subheader("Dokumenty, ilość i rentowność")
        labels={"orders":"Unikalne dokumenty w zakresie","quantity":"Ilość · "+result["profile"].get("quantity_unit",""),"average_order":"Wartość / dokument · "+unit,
                "profit":"Zysk pozycji · "+unit,"cost":"Koszt pozycji · "+unit,"margin_pct":"Marża %"}
        boxes=st.columns(3)
        for i,(key,label) in enumerate(labels.items()):
            value=b.get(key)
            boxes[i%3].metric(label,str(value) if key=="orders" and value is not None else money(value))
        st.caption("Wartość na dokument dotyczy wyłącznie pozycji po filtrach. Marża = zysk / wartość sprzedaży; tylko dodatni mianownik i potwierdzona semantyka. Ilości muszą mieć wspólną jednostkę.")
    if view==1:
        for field,rows in result.get("dimensions",{}).items():
            st.subheader("Wkład produktów w zmianę" if field=="product" else "Wkład klientów w zmianę")
            if not result["comparison"]["baseline_available"]:
                st.info(result["comparison"]["reason"])
            search=st.text_input("Szukaj "+("produktu" if field=="product" else "klienta"),key="driver_search_"+field)
            direction=st.selectbox("Kierunek zmiany",["Wszystkie","Spadki","Wzrosty"],key="driver_direction_"+field)
            _,count,pages,_=driver_page(rows,search,direction)
            page_key="driver_page_"+field
            st.session_state[page_key]=min(st.session_state.get(page_key,1),pages)
            page=st.number_input("Strona listy (20 pozycji)",1,pages,key=page_key)
            shown,_,_,_=driver_page(rows,search,direction,page)
            signature=(result["source_sha256"],result["kpis"]["start_date"],result["kpis"]["end_date"],search,direction,page,repr(shown))
            signature_key="driver_signature_"+field
            if st.session_state.get(signature_key)!=signature:
                st.session_state.pop("drivers_"+field,None)
                st.session_state[signature_key]=signature
            st.caption(f"Znaleziono {count} grup. Strona {page} / {pages}. Wyszukiwanie i kierunek zmieniają tylko tę listę.")
            if not shown:
                st.info("Brak pozycji spełniających warunki listy.")
                continue
            frame=[{"Identyfikator":r["entity"] if r["entity"] is not None else "(brak identyfikatora)",
                    "Bieżąca wartość":money(r["current"]),"Poprzednia wartość":money(r["previous"]),
                    "Wkład w zmianę":money(r["difference"]),"Pozycje":r["rows"]} for r in shown]
            if result["comparison"]["baseline_available"] and shown:
                chart=alt.Chart(pd.DataFrame([{"Pozycja":str((page-1)*20+i+1)+". "+compact_label(r["entity"] if r["entity"] is not None else "(brak)",52),"Pełna nazwa":str(r["entity"]),"Dokładna zmiana":money(r["difference"]),"Zmiana":float(r["difference"])} for i,r in enumerate(shown)])).mark_bar(color=COLORS[0]).encode(
                    x=alt.X("Zmiana:Q",title=unit),y=alt.Y("Pozycja:N",sort=None,title=None,axis=alt.Axis(labelLimit=340)),tooltip=["Pełna nazwa","Dokładna zmiana"]).properties(height=max(300,len(shown)*28))
                st.altair_chart(chart,width="stretch")
                st.caption("Widoczna strona według bezwzględnego wkładu. Suma wkładów wszystkich grup: "+money(sum(r["difference"] for r in rows))+" "+unit+". To rozkład zmiany, nie dowód przyczyn biznesowych.")
            event=st.dataframe(frame,on_select="rerun",selection_mode="single-row",key="drivers_"+field,hide_index=True,width="stretch")
            def focus(field=field,shown=shown,event=event):
                if event.selection.rows:
                    value=shown[event.selection.rows[0]]["entity"]
                    if value is not None:
                        st.session_state[field+"_filter"]=[value]
                        st.session_state["details_open"]=True
            st.button("Pokaż pozycje wybranego "+("produktu" if field=="product" else "klienta"),on_click=focus,key="drill_"+field,disabled=not bool(event.selection.rows) or shown[event.selection.rows[0]]["entity"] is None)
            st.caption("Brak identyfikatora nie pozwala wskazać konkretnego produktu lub klienta. Zaznacz wiersz i zastosuj filtr; pozycje CSV znajdziesz w sekcji szczegółów.")
    if view==2:
        st.subheader("Kompletność dodatkowych kolumn")
        names={"quantity":"Ilość","order_id":"Dokument","product":"Produkt","customer":"Klient","cost_minor":"Koszt pozycji","profit_minor":"Zysk pozycji"}
        missing=result["quality"].get("optional_missing",{})
        if missing:st.dataframe([{"Pole":names[k],"Brakujące wartości":v} for k,v in missing.items()],hide_index=True)
        else:st.caption("W mapowanych dodatkowych kolumnach nie wykryto braków.")
        st.caption("Liczby dotyczą całego pliku. Brak wartości w mapowanej kolumnie wyłącza zależną metrykę w danym zakresie.")
        adjustments=result["quality"].get("optional_rounding",{})
        if adjustments:
            st.dataframe([{"Pole":names[k],"Zmienione pozycje":v["rows"],"Wpływ na sumę · "+unit:v["delta"]} for k,v in adjustments.items()],hide_index=True)
