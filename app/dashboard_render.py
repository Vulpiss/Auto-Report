from app.validation import currency_label
"""Render compact slide visuals from the same model used by the interactive UI."""
from io import BytesIO
import textwrap
import numpy as np
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator, FuncFormatter
from app.dashboard_model import make_model, COLORS
from app.pdf_report import money, percent
from app.analyst_tools import compact_label

def board_png(result, view, grouping="Dzień"):
    unit=currency_label(result["profile"])
    model=make_model(result,grouping)
    fig=Figure(figsize=(12.8,5.75),dpi=170,facecolor="#eef3f8")
    def text(x,y,s,size=10,color="#172d44",weight="normal"):
        fig.text(x,y,str(s),fontsize=size,color=color,weight=weight,va="top",parse_math=False)
    def short(s,n=40):return compact_label(s,n)
    for i,(label,value,previous,change) in enumerate(model["cards"][view]):
        x=.025+i*.33
        ax=fig.add_axes([x,.79,.31,.19],facecolor="white")
        ax.set_xticks([]);ax.set_yticks([])
        for spine in ax.spines.values():spine.set_visible(False)
        text(x+.012,.963,label,9,color="#5d7387")
        text(x+.012,.912,short(value,28),20,weight="bold")
        text(x+.012,.839,short(previous,49),8,color="#5d7387")
        if change:text(x+.235,.963,change,9,color="#237be0")
    def panel(x,y,w,h,title):
        bg=fig.add_axes([x,y,w,h],facecolor="white")
        bg.set_xticks([]);bg.set_yticks([])
        for spine in bg.spines.values():spine.set_visible(False)
        text(x+.014,y+h-.016,title,11,weight="bold")
        ax=fig.add_axes([x+.065,y+.065,w-.095,h-.12],facecolor="white")
        ax.tick_params(labelsize=7,colors="#597184",length=0)
        for spine in ax.spines.values():spine.set_visible(False)
        ax.grid(axis="y",color="#e6edf4",linewidth=.6);ax.set_axisbelow(True)
        return ax
    axes=[panel(.025,.40,.54,.36,["Bieżący i poprzedni okres","Wkład kategorii w zmianę","Obecność pozycji"][view]),
          panel(.58,.40,.405,.36,["Największe wartości","Struktura w czasie","Rozliczenie filtrów"][view]),
          panel(.025,.025,.47,.35,["Struktura w czasie","Kategorie: bieżący / poprzedni","Liczba pozycji w czasie"][view]),
          panel(.51,.025,.475,.35,"Reguły i ograniczenia" if view==2 else "Kategorie w liczbach")]
    def number(v):
        return f"{v/1e9:.1f} mld" if abs(v)>=1e9 else f"{v/1e6:.1f} mln" if abs(v)>=1e6 else f"{v/1e3:.1f} tys." if abs(v)>=1e4 else f"{v:g}"
    def format_axis(ax,which):
        getattr(ax,which+"axis").set_major_formatter(FuncFormatter(lambda value,pos:number(value)))
        getattr(ax,which+"axis").set_major_locator(MaxNLocator(nbins=5))
    def series(ax,count=False):
        trend=model["trend"]; xs=np.arange(len(trend))
        ax.plot(xs,[t["rows_cnt"] if count else float(t["current"]) if t["current"] is not None else np.nan for t in trend],color=COLORS[0],linewidth=2,marker="o",markersize=3,label="Bieżący")
        if not count and result["comparison"]["baseline_available"]:
            ax.plot(xs,[float(t["previous"]) for t in trend],color="#aabed3",linewidth=2,marker="o",markersize=3,label="Poprzedni")
            ax.legend(fontsize=7,loc="upper left",frameon=False)
        ticks=list(range(0,len(trend),max(1,len(trend)//5)))
        ax.set_xticks(ticks,[trend[i]["label"][5:10] for i in ticks])
        ax.set_ylabel("Pozycje" if count else f"{unit}",fontsize=8,color="#597184")
        low,high=ax.get_ylim();ax.set_ylim(min(0,low),max(0,high))
        if count:ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        else:format_axis(ax,"y")
    def horizontal(ax,rows):
        if not rows or all(v is None for _,v in rows):
            ax.set_axis_off();ax.text(0,.6,"Porównanie niedostępne",fontsize=11,transform=ax.transAxes);return
        vals=[float(v or 0) for _,v in rows]
        yy=np.arange(len(rows))
        ax.barh(yy,vals,color=[COLORS[i%len(COLORS)] for i in range(len(rows))],height=.52)
        ax.set_yticks(yy,[short(n,15) for n,_ in rows]);ax.invert_yaxis()
        ax.axvline(0,color="#aabed3",linewidth=.6)
        ax.set_xlabel(f"{unit}",fontsize=7);ax.grid(axis="x",color="#e6edf4")
        for i,(_,v) in enumerate(rows):
            ax.text(vals[i],i," "+(number(float(v)) if abs(v)>=10000 else money(v)),fontsize=7,va="center",ha="left" if vals[i]>=0 else "right")
        l,h=ax.get_xlim();ax.set_xlim(l-(h-l)*.1,h+(h-l)*.27)
        format_axis(ax,"x")
    def stacked(ax):
        box=ax.get_position()
        ax.set_position([box.x0,box.y0,box.width,box.height-.055])
        xs=np.arange(len(model["trend"]));positive=np.zeros(len(xs));negative=np.zeros(len(xs))
        for ci,name in enumerate(model["category_labels"]):
            for neg in (False,True):
                vals=np.array([float(next(z["value"] for z in model["structure"] if z["label"]==t["label"] and z["category_id"]==ci and (z["sign"]=="Ujemne")==neg) or 0) if t["current"] is not None else np.nan for t in model["trend"]])
                bottom=negative if neg else positive
                ax.bar(xs,vals,bottom=bottom,color=COLORS[ci],label=short(name,18) if not neg else None)
                bottom+=np.nan_to_num(vals)
        ticks=list(range(0,len(xs),max(1,len(xs)//5)))
        ax.set_xticks(ticks,[model["trend"][i]["label"][5:10] for i in ticks])
        ax.axhline(0,color="#aabed3",linewidth=.6)
        ax.set_ylabel(f"{unit}",fontsize=8)
        format_axis(ax,"y")
        ax.legend(fontsize=6,loc="lower left",bbox_to_anchor=(0,1.02),ncol=2,frameon=False,borderaxespad=0)
    def tab(ax):
        ax.set_axis_off()
        rows=model["table"][:5]
        values=[[short(c["category"],23),money(c["value"]),money(c["difference"])] for c in rows]
        if len(model["table"])>5:
            rest=model["table"][5:]
            values.append(["Pozostałe ("+str(len(rest))+")",money(sum(c["value"] for c in rest)),
                           money(sum(c["difference"] for c in rest)) if result["comparison"]["baseline_available"] else "N/A"])
        table=ax.table(cellText=values,colLabels=["Kategoria",f"{unit}",f"Różnica {unit}"],cellLoc="left",colLoc="left",bbox=[0,0,1,1],colWidths=[.5,.25,.25])
        table.auto_set_font_size(False);table.set_fontsize(7)
        for (row,col),cell in table.get_celld().items():
            cell.set_edgecolor("#e6edf4");cell.set_linewidth(.4);cell.set_facecolor("#f1f5f9" if row==0 else "white")
    if view==0:
        series(axes[0]);horizontal(axes[1],[(x["category"],x["total_value"]) for x in model["rank"]]);stacked(axes[2]);tab(axes[3])
    elif view==1:
        horizontal(axes[0],[(x["category"],x["value"]) for x in model["changes"]]);stacked(axes[1])
        rows=model["table"][:5];ax=axes[2];y=np.arange(len(rows))
        ax.barh(y-.17,[float(c["value"]) for c in rows],height=.3,color=COLORS[0],label="Bieżący")
        if result["comparison"]["baseline_available"]:ax.barh(y+.17,[float(c["previous"]) for c in rows],height=.3,color="#aabed3",label="Poprzedni")
        ax.set_yticks(y,[short(c["category"],15) for c in rows]);ax.invert_yaxis();ax.legend(fontsize=7,frameon=False);format_axis(ax,"x");tab(axes[3])
    else:
        ax=axes[0]
        states=[0 if x["total_value"] is None else 1 if not x["rows_cnt"] else 2 for x in result["daily"]]
        ax.imshow([states],aspect="auto",cmap="Blues",vmin=0,vmax=2)
        ticks=list(range(0,len(states),max(1,len(states)//6)))
        ax.set_xticks(ticks,[result["daily"][i]["event_date"][5:] for i in ticks]);ax.set_yticks([])
        from matplotlib.patches import Patch
        from matplotlib import colormaps
        cmap=colormaps["Blues"]
        ax.legend(handles=[Patch(color=cmap(i/2),label=label) for i,label in enumerate(["Niepotwierdzone","Brak pozycji","Pozycje"])],loc="upper center",bbox_to_anchor=(.5,-.18),ncol=3,fontsize=6,frameon=False)
        q=result["quality"];ax=axes[1]
        ax.barh([0,1,2],[q["rows_in_period"],q["rows_outside_period"],q["rows_excluded_category"]],color=COLORS[:3])
        ax.set_yticks([0,1,2],["W widoku","Poza datami","Poza filtrami"]);ax.invert_yaxis();ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        series(axes[2],True);ax=axes[3];ax.set_axis_off()
        notes=["Pełny eksport: "+str(result["coverage_start"] or "nie podano")+" / "+str(result["coverage_end"] or "nie podano"),
               f"Kwota: {unit} / "+result["profile"]["amount_basis"],
               "Powtórzenia: "+str(q["duplicate_rows"])+"; zachowane.",
               "Ujemne w widoku: "+str(q["view_negative_count"])+".",
               "Brak danych nie oznacza zera."]
        ax.text(0,1,"\n\n".join(notes),fontsize=9,va="top",transform=ax.transAxes,parse_math=False)
    output=BytesIO();fig.savefig(output,format="png",dpi=170,facecolor=fig.get_facecolor());return output.getvalue()
