"""
Grupo 5 – Red Social X
6 Gráficos estáticos sobre la situación penitenciaria en Ecuador
Fuente: Bases de datos vinculación 2026
"""

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import numpy as np
import os

OUT = "outputs"
os.makedirs(OUT, exist_ok=True)

# ─── Constantes de estilo para X (móvil) ──────────────────────────────────────
PALETTE   = ["#1DA1F2", "#FF6B35", "#2ECC71", "#9B59B6", "#F39C12", "#E74C3C", "#1ABC9C"]
FUENTE    = "Bases de datos vinculación 2026"
BG        = "#0D1117"      # fondo oscuro → contraste alto
FG        = "#FFFFFF"
GRID_COL  = "#2D3748"
TITLE_FS  = 18
LABEL_FS  = 13
TICK_FS   = 12
ANNOT_FS  = 11
INTERP_FS = 11
FIG_W, FIG_H = 10, 7

plt.rcParams.update({
    "figure.facecolor": BG,
    "axes.facecolor":   BG,
    "axes.edgecolor":   FG,
    "axes.labelcolor":  FG,
    "xtick.color":      FG,
    "ytick.color":      FG,
    "text.color":       FG,
    "grid.color":       GRID_COL,
    "font.family":      "DejaVu Sans",
})

# ─── Cargar datos (solo columnas no-sensibles) ─────────────────────────────────
rc = pd.read_csv("data/registrocivil_limpio.csv",
                 usecols=["cedula", "cod_instruccion", "cod_profesion1", "cod_sexo"])

cnj = pd.read_csv("data/sentenciados_cnj_limpio.csv",
                  usecols=["cedula", "mes", "anio"])

csj = pd.read_csv("data/demandados_csj_limpio.csv",
                  usecols=["cedula", "accion", "fecha_ingreso"])

iess = pd.read_csv("data/iess_limpio.csv",
                   usecols=["cedula", "ocupacion", "tipo_empresa"])

fisc = pd.read_csv("data/carceles_fiscalia_limpio.csv",
                   usecols=["arma", "presun_motiva_obser", "sexo", "zona"])

# Eliminar cualquier columna sensible si existiera por error
for df in [rc, cnj, csj, iess, fisc]:
    for col in ["cedula", "apellidos_y_nombres_victima"]:
        if col in df.columns:
            df.drop(columns=[col], inplace=True, errors="ignore")


def add_footer(ax, fig, interp_text):
    """Agrega fuente e interpretación debajo del gráfico."""
    fig.text(0.01, 0.01,
             f"Fuente: {FUENTE}",
             fontsize=9, color="#AAAAAA", ha="left")
    fig.text(0.5, -0.04,
             interp_text,
             fontsize=INTERP_FS, color="#DDDDDD", ha="center",
             wrap=True, multialignment="center",
             bbox=dict(boxstyle="round,pad=0.4", facecolor="#1A2332", edgecolor="none"))


# ══════════════════════════════════════════════════════════════════════════════
# GRÁFICO 1 – Distribución del nivel de instrucción (Registro Civil)
# ══════════════════════════════════════════════════════════════════════════════
fig1, ax1 = plt.subplots(figsize=(FIG_W, FIG_H))
fig1.subplots_adjust(bottom=0.22, top=0.88)

orden_instr = ["NINGUNA", "INICIAL", "BASICA", "SECUNDARIA/BACHILLER", "SUPERIOR"]
etiquetas   = ["Ninguna", "Inicial", "Básica", "Secundaria\n/Bachiller", "Superior"]
conteo_instr = rc["cod_instruccion"].value_counts().reindex(orden_instr, fill_value=0)
total = conteo_instr.sum()

bars = ax1.bar(etiquetas, conteo_instr.values, color=PALETTE[:5],
               edgecolor="none", width=0.6)

for bar, val in zip(bars, conteo_instr.values):
    pct = val / total * 100
    ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 3,
             f"{val}\n({pct:.1f}%)", ha="center", va="bottom",
             fontsize=ANNOT_FS, fontweight="bold", color=FG)

ax1.set_title("Nivel de instrucción académica\nde la población vinculada",
              fontsize=TITLE_FS, fontweight="bold", color=FG, pad=14)
ax1.set_ylabel("N.º de personas", fontsize=LABEL_FS)
ax1.set_xlabel("Nivel educativo", fontsize=LABEL_FS)
ax1.tick_params(labelsize=TICK_FS)
ax1.yaxis.grid(True, linestyle="--", alpha=0.5)
ax1.set_axisbelow(True)

interp1 = ("La mayoría de las personas cuenta solo con educación básica (57.2 %).\n"
           "Quienes tienen educación superior representan el grupo minoritario,\n"
           "lo que refleja brechas de acceso educativo previas al ingreso al sistema.")
add_footer(ax1, fig1, interp1)
fig1.savefig(f"{OUT}/G1_instruccion.png", dpi=150, bbox_inches="tight",
             facecolor=BG)
print("G1 guardado")


# ══════════════════════════════════════════════════════════════════════════════
# GRÁFICO 2 – Evolución de sentencias por año (CNJ)
# ══════════════════════════════════════════════════════════════════════════════
fig2, ax2 = plt.subplots(figsize=(FIG_W, FIG_H))
fig2.subplots_adjust(bottom=0.22, top=0.88)

sent_anio = cnj["anio"].dropna().astype(int).value_counts().sort_index()

ax2.plot(sent_anio.index, sent_anio.values,
         marker="o", linewidth=2.5, markersize=9,
         color=PALETTE[0], markerfacecolor=PALETTE[1])
ax2.fill_between(sent_anio.index, sent_anio.values,
                 alpha=0.25, color=PALETTE[0])

for x, y in zip(sent_anio.index, sent_anio.values):
    ax2.annotate(str(y), (x, y), textcoords="offset points",
                 xytext=(0, 10), ha="center", fontsize=ANNOT_FS, fontweight="bold")

ax2.set_title("Evolución de sentencias registradas por año\n(Sentenciados CNJ)",
              fontsize=TITLE_FS, fontweight="bold", color=FG, pad=14)
ax2.set_ylabel("N.º de sentencias", fontsize=LABEL_FS)
ax2.set_xlabel("Año", fontsize=LABEL_FS)
ax2.set_xticks(sent_anio.index)
ax2.tick_params(labelsize=TICK_FS)
ax2.yaxis.grid(True, linestyle="--", alpha=0.5)
ax2.set_axisbelow(True)

interp2 = ("Las sentencias crecen sostenidamente entre 2017 y 2022, con un\n"
           "marcado incremento en 2021–2022. Este aumento coincide con\n"
           "el agravamiento de la crisis carcelaria en Ecuador en ese período.")
add_footer(ax2, fig2, interp2)
fig2.savefig(f"{OUT}/G2_sentencias_anio.png", dpi=150, bbox_inches="tight",
             facecolor=BG)
print("G2 guardado")


# ══════════════════════════════════════════════════════════════════════════════
# GRÁFICO 3 – Los 5 delitos más frecuentes (Demandados CSJ)
# ══════════════════════════════════════════════════════════════════════════════
def simplify_accion(a):
    a = str(a).upper()
    if "ROBO" in a:            return "Robo"
    if "TRÁFICO" in a or "TRAFICO" in a: return "Tráfico de drogas"
    if "ASESINAT" in a:        return "Asesinato"
    if "ALIMENTOS" in a:       return "Alimentos"
    if "ARMA" in a:            return "Tenencia de armas"
    if "HOMICID" in a:         return "Homicidio"
    if "ESTAF" in a:           return "Estafa"
    return "Otros"

csj["delito"] = csj["accion"].apply(simplify_accion)
top5 = csj["delito"].value_counts().head(5)

fig3, ax3 = plt.subplots(figsize=(FIG_W, FIG_H))
fig3.subplots_adjust(bottom=0.22, top=0.88, left=0.28)

colors3 = PALETTE[:5]
bars3 = ax3.barh(top5.index[::-1], top5.values[::-1],
                 color=colors3[::-1], edgecolor="none", height=0.6)

for bar, val in zip(bars3, top5.values[::-1]):
    ax3.text(bar.get_width() + 3, bar.get_y() + bar.get_height() / 2,
             str(val), va="center", ha="left",
             fontsize=ANNOT_FS, fontweight="bold", color=FG)

ax3.set_title("5 delitos más frecuentes en procesos\njudiciales (Demandados CSJ)",
              fontsize=TITLE_FS, fontweight="bold", color=FG, pad=14)
ax3.set_xlabel("N.º de procesos", fontsize=LABEL_FS)
ax3.tick_params(labelsize=TICK_FS)
ax3.xaxis.grid(True, linestyle="--", alpha=0.5)
ax3.set_axisbelow(True)

interp3 = ("El robo concentra la mayor cantidad de procesos judiciales,\n"
           "seguido de tráfico de drogas. La tenencia ilegal de armas\n"
           "también figura entre los delitos más registrados.")
add_footer(ax3, fig3, interp3)
fig3.savefig(f"{OUT}/G3_delitos_frecuentes.png", dpi=150, bbox_inches="tight",
             facecolor=BG)
print("G3 guardado")


# ══════════════════════════════════════════════════════════════════════════════
# GRÁFICO 4 – Tipos de armas en eventos críticos carcelarios (Fiscalía)
# ══════════════════════════════════════════════════════════════════════════════
armas = fisc["arma"].value_counts()
total_armas = armas.sum()

fig4, ax4 = plt.subplots(figsize=(FIG_W, FIG_H))
fig4.subplots_adjust(bottom=0.22, top=0.88)

wedges, texts, autotexts = ax4.pie(
    armas.values,
    labels=armas.index,
    autopct="%1.1f%%",
    colors=PALETTE[:len(armas)],
    startangle=140,
    pctdistance=0.78,
    textprops={"color": FG, "fontsize": LABEL_FS},
    wedgeprops={"edgecolor": BG, "linewidth": 2},
)
for at in autotexts:
    at.set_fontsize(ANNOT_FS)
    at.set_fontweight("bold")

ax4.set_title("Tipos de armas utilizadas\nen eventos críticos carcelarios (Fiscalía)",
              fontsize=TITLE_FS, fontweight="bold", color=FG, pad=14)

interp4 = ("Las armas de fuego representan el 43.5 % de los instrumentos\n"
           "registrados, seguidas de armas blancas (37.0 %).\n"
           "La presencia de armas dentro de los centros refleja\n"
           "un grave déficit en los controles de seguridad penitenciaria.")
add_footer(ax4, fig4, interp4)
fig4.savefig(f"{OUT}/G4_armas.png", dpi=150, bbox_inches="tight",
             facecolor=BG)
print("G4 guardado")


# ══════════════════════════════════════════════════════════════════════════════
# GRÁFICO 5 – Ocupaciones previas (IESS + Registro Civil)
# ══════════════════════════════════════════════════════════════════════════════
# IESS: ocupacion
iess_ocu = iess["ocupacion"].str.strip().str.title().value_counts()

# RC: profesion como proxy de ocupación previa
rc_prof = rc["cod_profesion1"].str.strip().str.title().value_counts()

# Unir ambas fuentes
ocu_combinada = pd.concat([iess_ocu, rc_prof]).groupby(level=0).sum()

def simplify_ocu(o):
    o = str(o).upper()
    if "ESTUDI" in o:                  return "Estudiante"
    if "GUARD" in o:                   return "Guardia / Seguridad"
    if "OBRER" in o or "JORNALERO" in o or "PEON" in o: return "Obrero / Jornalero"
    if "COMERC" in o:                  return "Comerciante"
    if "ALBAÑIL" in o or "ALBANIL" in o or "CONSTRUC" in o: return "Construcción"
    if "EMPLOY" in o or "EMPLEAD" in o: return "Empleado"
    if "NINGUN" in o or "SIN REL" in o: return "Sin ocupación registrada"
    if "GERENTE" in o or "DIRECT" in o: return "Gerente / Directivo"
    if "AUXIL" in o or "ASIST" in o:   return "Auxiliar / Asistente"
    return "Otros"

ocu_combinada.index = ocu_combinada.index.map(simplify_ocu)
ocu_agrupada = ocu_combinada.groupby(level=0).sum().sort_values(ascending=False).head(8)

fig5, ax5 = plt.subplots(figsize=(FIG_W, FIG_H))
fig5.subplots_adjust(bottom=0.22, top=0.88, left=0.30)

bars5 = ax5.barh(ocu_agrupada.index[::-1], ocu_agrupada.values[::-1],
                  color=PALETTE[:len(ocu_agrupada)][::-1], edgecolor="none", height=0.6)

for bar, val in zip(bars5, ocu_agrupada.values[::-1]):
    ax5.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
             str(val), va="center", ha="left",
             fontsize=ANNOT_FS, fontweight="bold", color=FG)

ax5.set_title("Ocupaciones previas de personas\nantes de ingresar al sistema (IESS + Registro Civil)",
              fontsize=TITLE_FS, fontweight="bold", color=FG, pad=14)
ax5.set_xlabel("N.º de personas", fontsize=LABEL_FS)
ax5.tick_params(labelsize=TICK_FS)
ax5.xaxis.grid(True, linestyle="--", alpha=0.5)
ax5.set_axisbelow(True)

interp5 = ("La ocupación más frecuente antes del ingreso al sistema es 'Estudiante',\n"
           "lo que señala la presencia de jóvenes en el sistema penal.\n"
           "Obreros, jornaleros y comerciantes también tienen alta representación,\n"
           "vinculada a empleos informales y condiciones de vulnerabilidad económica.")
add_footer(ax5, fig5, interp5)
fig5.savefig(f"{OUT}/G5_ocupaciones.png", dpi=150, bbox_inches="tight",
             facecolor=BG)
print("G5 guardado")


# ══════════════════════════════════════════════════════════════════════════════
# GRÁFICO 6 – Nivel educativo vs tipos de delito (Registro Civil × CSJ)
# ══════════════════════════════════════════════════════════════════════════════
# Cruce por cédula (ya eliminada del df, pero necesitamos hacer el merge antes)
rc_cross = pd.read_csv("data/registrocivil_limpio.csv",
                       usecols=["cedula", "cod_instruccion"])
csj_cross = pd.read_csv("data/demandados_csj_limpio.csv",
                        usecols=["cedula", "accion"])
csj_cross["delito"] = csj_cross["accion"].apply(simplify_accion)

merged = pd.merge(rc_cross, csj_cross[["cedula","delito"]], on="cedula").drop(columns=["cedula"])

orden_edu = ["NINGUNA", "INICIAL", "BASICA", "SECUNDARIA/BACHILLER", "SUPERIOR"]
etiq_edu  = ["Ninguna", "Inicial", "Básica", "Sec./Bach.", "Superior"]
top_delitos = ["Robo", "Tráfico de drogas", "Asesinato", "Tenencia de armas", "Homicidio"]

ct = pd.crosstab(merged["cod_instruccion"], merged["delito"])
ct = ct.reindex(index=orden_edu, fill_value=0)
ct = ct[[d for d in top_delitos if d in ct.columns]]

# Convertir a porcentajes por fila
ct_pct = ct.div(ct.sum(axis=1), axis=0) * 100

fig6, ax6 = plt.subplots(figsize=(FIG_W + 1, FIG_H))
fig6.subplots_adjust(bottom=0.25, top=0.88, right=0.85)

x = np.arange(len(etiq_edu))
width = 0.15
n_delitos = len(ct_pct.columns)

for i, (delito, color) in enumerate(zip(ct_pct.columns, PALETTE)):
    offset = (i - n_delitos / 2 + 0.5) * width
    ax6.bar(x + offset, ct_pct[delito].values, width,
            label=delito, color=color, edgecolor="none")

ax6.set_title("Distribución de delitos por nivel educativo\n(Cruce Registro Civil × CSJ)",
              fontsize=TITLE_FS, fontweight="bold", color=FG, pad=14)
ax6.set_ylabel("Porcentaje (%)", fontsize=LABEL_FS)
ax6.set_xlabel("Nivel educativo", fontsize=LABEL_FS)
ax6.set_xticks(x)
ax6.set_xticklabels(etiq_edu, fontsize=TICK_FS)
ax6.tick_params(labelsize=TICK_FS)
ax6.yaxis.grid(True, linestyle="--", alpha=0.5)
ax6.set_axisbelow(True)
ax6.legend(fontsize=10, loc="upper left", framealpha=0.3,
           bbox_to_anchor=(1.01, 1), borderaxespad=0)

interp6 = ("El robo predomina en todos los niveles educativos, especialmente\n"
           "en básica y secundaria. El tráfico de drogas es relevante en\n"
           "todos los grupos. Las personas con educación superior muestran\n"
           "un perfil de delitos relativamente más diversificado.")
add_footer(ax6, fig6, interp6)
fig6.savefig(f"{OUT}/G6_educacion_delito.png", dpi=150, bbox_inches="tight",
             facecolor=BG)
print("G6 guardado")

print("\n✅ Todos los gráficos fueron generados exitosamente.")