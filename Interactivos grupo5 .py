"""
Grupo 5 – Red Social X
4 Visualizaciones Interactivas – Situación Penitenciaria Ecuador
Fuente: Bases de datos vinculación 2026
Salida: 4 archivos .html independientes listos para publicar en X
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os, json

OUT = "outputs2"
os.makedirs(OUT, exist_ok=True)

# ── Paleta corporativa oscura, apta para X ─────────────────────────────────────
C = {
    "bg":       "#0D1117",
    "paper":    "#161B22",
    "panel":    "#1C2333",
    "accent1":  "#1DA1F2",   # azul X
    "accent2":  "#FF6B35",
    "accent3":  "#2ECC71",
    "accent4":  "#9B59B6",
    "accent5":  "#F39C12",
    "accent6":  "#E74C3C",
    "text":     "#E6EDF3",
    "subtext":  "#8B949E",
    "grid":     "#21262D",
}

FUENTE = "Fuente: Bases de datos vinculación 2026"

LAYOUT_BASE = dict(
    paper_bgcolor=C["bg"],
    plot_bgcolor=C["paper"],
    font=dict(color=C["text"], family="Inter, Arial, sans-serif", size=13),
    margin=dict(t=110, b=120, l=60, r=60),
    hoverlabel=dict(bgcolor=C["panel"], font_color=C["text"], font_size=13),
)

# Coordenadas de centroides de provincias/subzonas de Ecuador
COORDS = {
    "AZUAY":         (-2.9001, -78.9997),
    "CAÑAR":         (-2.5583, -78.9389),
    "CHIMBORAZO":    (-1.6636, -78.6543),
    "COTOPAXI":      (-0.9338, -78.6140),
    "DMG":           (-0.2295, -78.5243),  # Distrito Metropolitano Guayas / Guayaquil
    "EL ORO":        (-3.2592, -79.9554),
    "ESMERALDAS":    ( 0.9592, -79.6519),
    "LOJA":          (-3.9931, -79.2042),
    "LOS RÍOS":      (-1.7864, -79.4883),
    "MANABÍ":        (-1.0539, -80.4518),
    "SANTO DOMINGO": (-0.2543, -79.1719),
}

# ══════════════════════════════════════════════════════════════════════════════
#  INTERACTIVO 1 – Mapa de Incidentes Críticos por Provincia
#  Datos: Fiscalía | Filtros: Año · Sexo
# ══════════════════════════════════════════════════════════════════════════════
print("Generando Interactivo 1 – Mapa de Incidentes...")

fisc = pd.read_csv(
    "data/carceles_fiscalia_limpio.csv",
    usecols=["edad", "sexo", "subzona", "fecha_infraccion", "arma", "presun_motiva_obser"]
)
fisc["anio"] = pd.to_datetime(fisc["fecha_infraccion"], errors="coerce").dt.year.dropna()
fisc.dropna(subset=["anio", "subzona"], inplace=True)
fisc["anio"] = fisc["anio"].astype(int)
fisc["lat"]  = fisc["subzona"].map(lambda x: COORDS.get(x, (None, None))[0])
fisc["lon"]  = fisc["subzona"].map(lambda x: COORDS.get(x, (None, None))[1])

anios_fisc = sorted(fisc["anio"].unique())
sexos_fisc = ["TODOS"] + sorted(fisc["sexo"].dropna().unique().tolist())

# Construir trazas para cada combinación año × sexo
traces_map = []
visibility_map = []

for anio in anios_fisc:
    for sexo in sexos_fisc:
        df_f = fisc[fisc["anio"] == anio].copy()
        if sexo != "TODOS":
            df_f = df_f[df_f["sexo"] == sexo]

        agg = (df_f.groupby(["subzona", "lat", "lon"])
                   .size()
                   .reset_index(name="incidentes"))
        agg["arma_top"] = (df_f.groupby("subzona")["arma"]
                               .agg(lambda s: s.value_counts().index[0] if len(s) > 0 else "N/D")
                               .reindex(agg["subzona"]).values)

        traces_map.append(go.Scattergeo(
            lat=agg["lat"],
            lon=agg["lon"],
            mode="markers",
            marker=dict(
                size=np.sqrt(agg["incidentes"]) * 8,
                color=agg["incidentes"],
                colorscale=[
                    [0.0, "#1a3a5c"], [0.3, "#1DA1F2"],
                    [0.6, "#FF6B35"], [1.0, "#E74C3C"]
                ],
                cmin=0,
                cmax=fisc.groupby(["subzona"]).size().max(),
                colorbar=dict(
                    title=dict(text="N° incidentes", font=dict(color=C["text"])),
                    tickfont=dict(color=C["text"]),
                    bgcolor=C["paper"],
                    bordercolor=C["grid"],
                ),
                opacity=0.85,
                line=dict(width=1.5, color=C["bg"]),
            ),
            text=agg["subzona"],
            customdata=np.stack([agg["incidentes"], agg["arma_top"]], axis=-1),
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Incidentes: <b>%{customdata[0]}</b><br>"
                "Arma predominante: %{customdata[1]}<br>"
                "<extra></extra>"
            ),
            visible=False,
        ))
        visibility_map.append((anio, sexo))

# Activar primera combinación
traces_map[0].visible = True

# Botones de Año
btn_anio = []
for a in anios_fisc:
    vis = [v[0] == a and v[1] == sexos_fisc[0] for v in visibility_map]
    btn_anio.append(dict(
        label=str(a),
        method="update",
        args=[{"visible": vis},
              {"title.text": f"Incidentes críticos carcelarios · {a} · {sexos_fisc[0]}"}]
    ))

# Botones de Sexo (activan según año activo — JS limitado en static HTML,
# usamos updatemenus encadenados: Año activa su grupo; Sexo activa sobre ese año)
btn_sexo = []
for s in sexos_fisc:
    vis = [v[0] == anios_fisc[0] and v[1] == s for v in visibility_map]
    btn_sexo.append(dict(
        label=s.title() if s != "TODOS" else "Todos",
        method="update",
        args=[{"visible": vis},
              {"title.text": f"Incidentes críticos carcelarios · {anios_fisc[0]} · {s}"}]
    ))

fig1 = go.Figure(data=traces_map)
fig1.update_layout(
    **LAYOUT_BASE,
    title=dict(
        text="Incidentes críticos carcelarios · 2020 · TODOS",
        font=dict(size=20, color=C["text"]),
        x=0.5, xanchor="center",
    ),
    geo=dict(
        scope="south america",
        projection_type="mercator",
        center=dict(lat=-1.8, lon=-78.2),
        lataxis_range=[-5.5, 1.5],
        lonaxis_range=[-81.5, -74.5],
        bgcolor=C["bg"],
        landcolor="#1a2332",
        oceancolor="#0a1520",
        lakecolor="#0a1520",
        countrycolor=C["grid"],
        showland=True, showocean=True, showlakes=True,
        showcoastlines=True, coastlinecolor=C["subtext"],
        showcountries=True,
    ),
    updatemenus=[
        dict(
            buttons=btn_anio,
            direction="right",
            pad=dict(r=10, t=10),
            showactive=True,
            x=0.01, xanchor="left",
            y=1.12, yanchor="top",
            bgcolor=C["panel"],
            bordercolor=C["accent1"],
            font=dict(color=C["text"], size=13),
            active=0,
            type="buttons",
        ),
        dict(
            buttons=btn_sexo,
            direction="right",
            pad=dict(r=10, t=10),
            showactive=True,
            x=0.01, xanchor="left",
            y=1.04, yanchor="top",
            bgcolor=C["panel"],
            bordercolor=C["accent2"],
            font=dict(color=C["text"], size=13),
            active=0,
            type="buttons",
        ),
    ],
    annotations=[
        dict(text="<b>Año:</b>", x=0.0, xref="paper", y=1.115, yref="paper",
             showarrow=False, font=dict(color=C["subtext"], size=12)),
        dict(text="<b>Sexo:</b>", x=0.0, xref="paper", y=1.045, yref="paper",
             showarrow=False, font=dict(color=C["subtext"], size=12)),
        dict(
            text=(
                f"{FUENTE}  |  Variables: subzona, arma, fecha de infracción, sexo<br>"
                "<i>El tamaño de cada burbuja representa el número de incidentes registrados en ese territorio.<br>"
                "La concentración en DMG refleja la alta densidad poblacional penitenciaria de esa provincia.<br>"
                "Los filtros permiten analizar la evolución temporal y las diferencias por sexo de los eventos.</i>"
            ),
            x=0.5, xref="paper", y=-0.18, yref="paper",
            align="center", showarrow=False,
            font=dict(color=C["subtext"], size=11),
            bordercolor=C["grid"], borderwidth=1,
            bgcolor=C["panel"], borderpad=8,
        ),
    ],
)

fig1.write_html(
    f"{OUT}/I1_mapa_incidentes.html",
    full_html=True, include_plotlyjs="cdn",
    config={"responsive": True, "displayModeBar": True},
)
print("  → I1 guardado")


# ══════════════════════════════════════════════════════════════════════════════
#  INTERACTIVO 2 – Dashboard: Tipos de Armas y Motivaciones por Centro
#  Datos: Fiscalía | Filtros: Provincia · Año
# ══════════════════════════════════════════════════════════════════════════════
print("Generando Interactivo 2 – Burbujas Armas × Motivaciones...")

fisc2 = fisc.copy()
fisc2["motiva_corta"] = fisc2["presun_motiva_obser"].apply(
    lambda x: str(x)[:30] if pd.notna(x) else "No especificado"
)

provincias = ["TODAS"] + sorted(fisc2["subzona"].dropna().unique().tolist())
anios_f2   = ["TODOS"] + [str(a) for a in anios_fisc]

# Datos base para el gráfico (se filtran vía JS con Plotly updatemenus)
def build_bubble(df):
    agg = (df.groupby(["arma", "motiva_corta"])
              .size()
              .reset_index(name="n"))
    # x = arma, y = motivación, size = frecuencia
    armas_cat = agg["arma"].astype("category").cat.codes
    motiv_cat = agg["motiva_corta"].astype("category").cat.codes
    return agg, armas_cat, motiv_cat

traces2, vis2 = [], []

for anio in (["TODOS"] + [str(a) for a in anios_fisc]):
    for prov in provincias:
        df_f = fisc2.copy()
        if anio != "TODOS":
            df_f = df_f[df_f["anio"] == int(anio)]
        if prov != "TODAS":
            df_f = df_f[df_f["subzona"] == prov]

        agg, ax, ay = build_bubble(df_f)
        arma_labels  = agg["arma"].tolist()
        motiv_labels = agg["motiva_corta"].tolist()

        traces2.append(go.Scatter(
            x=ax,
            y=ay,
            mode="markers",
            marker=dict(
                size=np.sqrt(agg["n"].values) * 12,
                color=ax,
                colorscale="Viridis",
                opacity=0.82,
                line=dict(width=1.5, color=C["bg"]),
                showscale=False,
            ),
            text=agg["arma"],
            customdata=np.stack([agg["n"], agg["motiva_corta"]], axis=-1),
            hovertemplate=(
                "<b>Arma:</b> %{text}<br>"
                "<b>Motivación:</b> %{customdata[1]}<br>"
                "<b>Casos:</b> %{customdata[0]}<br><extra></extra>"
            ),
            visible=False,
        ))
        vis2.append((anio, prov))

traces2[0].visible = True

# Construir botones
def make_buttons2(dim, values, other_default, other_list, dim2):
    btns = []
    for v in values:
        vis = []
        for entry in vis2:
            match_self  = (entry[dim] == v)
            match_other = (entry[dim2] == other_default)
            vis.append(match_self and match_other)
        btns.append(dict(
            label=v.title() if v not in ("TODOS","TODAS") else ("Todos" if dim == 0 else "Todas"),
            method="update",
            args=[{"visible": vis}],
        ))
    return btns

btn_anio2 = make_buttons2(0, anios_f2,  "TODAS", provincias, 1)
btn_prov2 = make_buttons2(1, provincias, "TODOS", anios_f2,   0)

# Etiquetas de ejes (se actualizan en hover, no dinámicamente en static)
arma_tick_vals = list(range(fisc2["arma"].dropna().nunique()))
arma_tick_text = sorted(fisc2["arma"].dropna().unique().tolist())
motiv_tick_vals = list(range(fisc2["motiva_corta"].nunique()))
motiv_tick_text = sorted(fisc2["motiva_corta"].unique().tolist())

fig2 = go.Figure(data=traces2)
fig2.update_layout(
    **LAYOUT_BASE,
    title=dict(
        text="Tipo de arma × Motivación del evento – Centros carcelarios",
        font=dict(size=20, color=C["text"]),
        x=0.5, xanchor="center",
    ),
    xaxis=dict(
        title="Tipo de arma",
        tickvals=arma_tick_vals,
        ticktext=arma_tick_text,
        tickfont=dict(color=C["text"]),
        gridcolor=C["grid"],
        showgrid=True,
        zeroline=False,
    ),
    yaxis=dict(
        title="Motivación declarada",
        tickvals=motiv_tick_vals,
        ticktext=[t[:28] + "…" if len(t) > 28 else t for t in motiv_tick_text],
        tickfont=dict(color=C["text"], size=11),
        gridcolor=C["grid"],
        showgrid=True,
        zeroline=False,
    ),
    updatemenus=[
        dict(
            buttons=btn_anio2,
            direction="right",
            pad=dict(r=10, t=10),
            showactive=True,
            x=0.01, xanchor="left",
            y=1.14, yanchor="top",
            bgcolor=C["panel"], bordercolor=C["accent1"],
            font=dict(color=C["text"], size=13), active=0, type="buttons",
        ),
        dict(
            buttons=btn_prov2,
            direction="right",
            pad=dict(r=10, t=10),
            showactive=True,
            x=0.01, xanchor="left",
            y=1.06, yanchor="top",
            bgcolor=C["panel"], bordercolor=C["accent2"],
            font=dict(color=C["text"], size=13), active=0, type="buttons",
        ),
    ],
    annotations=[
        dict(text="<b>Año:</b>", x=0.0, xref="paper", y=1.145, yref="paper",
             showarrow=False, font=dict(color=C["subtext"], size=12)),
        dict(text="<b>Provincia:</b>", x=0.0, xref="paper", y=1.065, yref="paper",
             showarrow=False, font=dict(color=C["subtext"], size=12)),
        dict(
            text=(
                f"{FUENTE}  |  Variables: arma, motivación, provincia, año<br>"
                "<i>El tamaño de cada burbuja indica la frecuencia de esa combinación arma–motivación.<br>"
                "Las riñas son la motivación predominante en casi todas las provincias y tipos de arma.<br>"
                "Al filtrar por provincia se pueden identificar patrones locales específicos.</i>"
            ),
            x=0.5, xref="paper", y=-0.22, yref="paper",
            align="center", showarrow=False,
            font=dict(color=C["subtext"], size=11),
            bordercolor=C["grid"], borderwidth=1,
            bgcolor=C["panel"], borderpad=8,
        ),
    ],
)

fig2.write_html(
    f"{OUT}/I2_burbujas_armas.html",
    full_html=True, include_plotlyjs="cdn",
    config={"responsive": True},
)
print("  → I2 guardado")


# ══════════════════════════════════════════════════════════════════════════════
#  INTERACTIVO 3 – Sentencias × Nivel Educativo
#  Datos: Sentenciados CNJ + Registro Civil | Filtros: Instrucción · Año
# ══════════════════════════════════════════════════════════════════════════════
print("Generando Interactivo 3 – Sentencias × Educación...")

cnj = pd.read_csv(
    "data/sentenciados_cnj_limpio.csv",
    usecols=["cedula", "mes", "anio"]
)
rc = pd.read_csv(
    "data/registrocivil_limpio.csv",
    usecols=["cedula", "cod_instruccion", "cod_sexo"]
)

# Cruce
merged = pd.merge(cnj, rc, on="cedula").drop(columns=["cedula"])
merged.dropna(subset=["anio", "cod_instruccion"], inplace=True)
merged["anio"] = merged["anio"].astype(int)

INSTR_ORDER = ["NINGUNA", "INICIAL", "BASICA", "SECUNDARIA/BACHILLER", "SUPERIOR"]
INSTR_LABEL = {
    "NINGUNA": "Ninguna",
    "INICIAL": "Inicial",
    "BASICA": "Básica",
    "SECUNDARIA/BACHILLER": "Sec./Bach.",
    "SUPERIOR": "Superior",
}
COLOR_INSTR = {
    "NINGUNA": C["accent6"],
    "INICIAL": C["accent5"],
    "BASICA": C["accent1"],
    "SECUNDARIA/BACHILLER": C["accent3"],
    "SUPERIOR": C["accent4"],
}

anios_cnj = sorted(merged["anio"].unique())

# Panel superior: barras apiladas por año × instrucción
# Panel inferior: línea de evolución total
fig3 = make_subplots(
    rows=2, cols=1,
    row_heights=[0.65, 0.35],
    subplot_titles=[
        "Distribución de sentencias por nivel educativo (barras apiladas)",
        "Evolución total de sentencias por año",
    ],
    vertical_spacing=0.14,
)

# ── Barras apiladas (una traza por nivel de instrucción, filtrada) ─────────
instr_filtros = ["TODAS"] + INSTR_ORDER
traces3, vis3 = [], []

for instruccion in instr_filtros:
    df_f = merged.copy()
    if instruccion != "TODAS":
        df_f = df_f[df_f["cod_instruccion"] == instruccion]

    # Barra apilada: una sub-traza por nivel de instrucción presente
    subtrazas = []
    for instr in INSTR_ORDER:
        df_i = df_f[df_f["cod_instruccion"] == instr]
        cnt  = df_i.groupby("anio").size().reindex(anios_cnj, fill_value=0)
        subtrazas.append(go.Bar(
            name=INSTR_LABEL[instr],
            x=anios_cnj,
            y=cnt.values,
            marker_color=COLOR_INSTR[instr],
            hovertemplate=f"<b>{INSTR_LABEL[instr]}</b><br>Año: %{{x}}<br>Sentencias: %{{y}}<extra></extra>",
            visible=instruccion == "TODAS",
            legendgroup=instr,
            showlegend=(instruccion == "TODAS"),
        ))
    traces3.append((instruccion, subtrazas))

# Línea de evolución total
total_anio = merged.groupby("anio").size().reindex(anios_cnj, fill_value=0)
trace_linea = go.Scatter(
    x=anios_cnj, y=total_anio.values,
    mode="lines+markers+text",
    line=dict(color=C["accent1"], width=2.5),
    marker=dict(size=9, color=C["accent2"]),
    text=total_anio.values,
    textposition="top center",
    textfont=dict(color=C["text"], size=11),
    hovertemplate="<b>%{x}</b><br>Total sentencias: %{y}<extra></extra>",
    name="Total",
    showlegend=True,
)

# Agregar todas las subtrazas al panel 1 y la línea al panel 2
all_bar_traces = []
for instruccion, subs in traces3:
    for t in subs:
        fig3.add_trace(t, row=1, col=1)
        all_bar_traces.append((instruccion, t.name))

fig3.add_trace(trace_linea, row=2, col=1)

# Construir botones de filtro de instrucción
def make_btn3(instr_target):
    vis = []
    for (instr, _) in all_bar_traces:
        vis.append(instr == instr_target)
    vis.append(True)  # línea siempre visible
    return dict(
        label=INSTR_LABEL.get(instr_target, "Todas"),
        method="update",
        args=[{"visible": vis}, {"barmode": "stack"}],
    )

btns3 = [make_btn3("TODAS")] + [make_btn3(i) for i in INSTR_ORDER]

fig3.update_layout(
    **LAYOUT_BASE,
    barmode="stack",
    title=dict(
        text="Distribución de Sentencias por Nivel Educativo – CNJ × Registro Civil",
        font=dict(size=20, color=C["text"]),
        x=0.5, xanchor="center",
    ),
    legend=dict(
        orientation="h", y=-0.06, x=0.5, xanchor="center",
        font=dict(color=C["text"], size=12),
        bgcolor=C["panel"], bordercolor=C["grid"],
    ),
    updatemenus=[dict(
        buttons=btns3,
        direction="right",
        pad=dict(r=10, t=10),
        showactive=True,
        x=0.01, xanchor="left",
        y=1.10, yanchor="top",
        bgcolor=C["panel"], bordercolor=C["accent3"],
        font=dict(color=C["text"], size=13), active=0, type="buttons",
    )],
    annotations=[
        dict(text="<b>Instrucción:</b>", x=0.0, xref="paper", y=1.105, yref="paper",
             showarrow=False, font=dict(color=C["subtext"], size=12)),
        # Subtítulos de subplots ya los agrega make_subplots
        dict(
            text=(
                f"{FUENTE}  |  Variables: nivel de instrucción, año de sentencia, sexo<br>"
                "<i>Las sentencias se incrementaron sostenidamente entre 2017 y 2022.<br>"
                "La mayoría de las personas sentenciadas tiene educación básica o secundaria,<br>"
                "lo que evidencia la correlación entre brechas educativas y vulnerabilidad penal.</i>"
            ),
            x=0.5, xref="paper", y=-0.20, yref="paper",
            align="center", showarrow=False,
            font=dict(color=C["subtext"], size=11),
            bordercolor=C["grid"], borderwidth=1,
            bgcolor=C["panel"], borderpad=8,
        ),
    ],
)
fig3.update_xaxes(tickfont=dict(color=C["text"]), gridcolor=C["grid"], zeroline=False)
fig3.update_yaxes(tickfont=dict(color=C["text"]), gridcolor=C["grid"], zeroline=False)

fig3.write_html(
    f"{OUT}/I3_sentencias_educacion.html",
    full_html=True, include_plotlyjs="cdn",
    config={"responsive": True},
)
print("  → I3 guardado")


# ══════════════════════════════════════════════════════════════════════════════
#  INTERACTIVO 4 – Ocupaciones y Vulnerabilidad Económica (IESS)
#  Filtros: Rango salarial · Tipo de empresa
# ══════════════════════════════════════════════════════════════════════════════
print("Generando Interactivo 4 – Ocupaciones y Vulnerabilidad Económica...")

iess = pd.read_csv(
    "data/iess_limpio.csv",
    usecols=["salario", "tipo_empresa", "fecha_ingreso", "ocupacion", "anio", "mes"]
)
iess.dropna(subset=["salario", "ocupacion"], inplace=True)

# Simplificar ocupación
def simplify_ocu(o):
    o = str(o).upper()
    if "ESTUDI"   in o: return "Estudiante"
    if "GUARD"    in o: return "Guardia/Seguridad"
    if "OBRERO"   in o or "JORNALERO" in o or "PEON" in o: return "Obrero/Jornalero"
    if "COMERC"   in o: return "Comerciante"
    if "ALBAÑIL"  in o or "ALBANIL" in o or "CONSTRUC" in o: return "Construcción"
    if "EMPLEAD"  in o: return "Empleado"
    if "NINGUN"   in o or "SIN REL" in o: return "Sin registro"
    if "GERENTE"  in o or "DIRECT"  in o: return "Gerente/Directivo"
    if "AUXIL"    in o or "ASIST"   in o: return "Auxiliar/Asistente"
    if "TRABAJ"   in o: return "Trabajador general"
    return "Otro"

iess["ocu_simple"] = iess["ocupacion"].apply(simplify_ocu)

# Simplificar tipo empresa
def simplify_emp(e):
    e = str(e).upper()
    if "PRIVAD" in e: return "Empresa Privada"
    if "UNIPER" in e or "PEQUEÑA" in e: return "Pequeña Empresa"
    if "CAMPESI" in e: return "Org. Campesina"
    if "ESTADO" in e or "EJECUT" in e: return "Estado"
    if "VOLUNT" in e: return "Afiliación Voluntaria"
    if "AUTONO" in e: return "Entidad Autónoma"
    if "CONSTRUC" in e: return "Construcción"
    if "DOMEST" in e: return "Empleo Doméstico"
    return "Otro"

iess["empresa_simple"] = iess["tipo_empresa"].apply(simplify_emp)

# Rangos salariales
bins  = [0, 100, 200, 400, 800, 99999]
labels = ["$0–100", "$101–200", "$201–400", "$401–800", "$800+"]
iess["rango_sal"] = pd.cut(iess["salario"], bins=bins, labels=labels, right=True)

rangos  = ["TODOS"] + labels
empresas = ["TODAS"] + sorted(iess["empresa_simple"].unique().tolist())

# Construir trazas: para cada combinación rango × empresa, una traza de barras h
traces4, vis4 = [], []

COLOR_OCU = {
    "Estudiante":       C["accent1"],
    "Guardia/Seguridad":C["accent2"],
    "Obrero/Jornalero": C["accent3"],
    "Comerciante":      C["accent4"],
    "Construcción":     C["accent5"],
    "Empleado":         C["accent6"],
    "Sin registro":     "#7F8C8D",
    "Gerente/Directivo":"#27AE60",
    "Auxiliar/Asistente":"#8E44AD",
    "Trabajador general":"#D35400",
    "Otro":             "#BDC3C7",
}

for rango in rangos:
    for emp in empresas:
        df_f = iess.copy()
        if rango != "TODOS":
            df_f = df_f[df_f["rango_sal"] == rango]
        if emp != "TODAS":
            df_f = df_f[df_f["empresa_simple"] == emp]

        cnt = df_f["ocu_simple"].value_counts().sort_values()
        colors_bar = [COLOR_OCU.get(o, "#BDC3C7") for o in cnt.index]

        traces4.append(go.Bar(
            x=cnt.values,
            y=cnt.index.tolist(),
            orientation="h",
            marker=dict(color=colors_bar, line=dict(width=0)),
            text=cnt.values,
            textposition="outside",
            textfont=dict(color=C["text"], size=12),
            hovertemplate="<b>%{y}</b><br>Personas: %{x}<extra></extra>",
            visible=False,
        ))
        vis4.append((rango, emp))

traces4[0].visible = True

def make_buttons4(dim, values, other_default, dim2):
    btns = []
    for v in values:
        vis = [entry[dim] == v and entry[dim2] == other_default for entry in vis4]
        lbl = v if v not in ("TODOS","TODAS") else ("Todos" if dim == 0 else "Todas")
        btns.append(dict(
            label=lbl,
            method="update",
            args=[{"visible": vis}],
        ))
    return btns

btn_rango4  = make_buttons4(0, rangos,   "TODAS", 1)
btn_emp4    = make_buttons4(1, empresas, "TODOS",  0)

fig4 = go.Figure(data=traces4)
fig4.update_layout(
    **LAYOUT_BASE,
    title=dict(
        text="Ocupaciones previas y Vulnerabilidad Económica – IESS",
        font=dict(size=20, color=C["text"]),
        x=0.5, xanchor="center",
    ),
    xaxis=dict(
        title="N° de personas",
        tickfont=dict(color=C["text"]),
        gridcolor=C["grid"], zeroline=False,
    ),
    yaxis=dict(
        title="Ocupación previa",
        tickfont=dict(color=C["text"], size=12),
        gridcolor=C["grid"], zeroline=False,
    ),
    updatemenus=[
        dict(
            buttons=btn_rango4,
            direction="right",
            pad=dict(r=10, t=10),
            showactive=True,
            x=0.01, xanchor="left",
            y=1.16, yanchor="top",
            bgcolor=C["panel"], bordercolor=C["accent1"],
            font=dict(color=C["text"], size=13), active=0, type="buttons",
        ),
        dict(
            buttons=btn_emp4,
            direction="right",
            pad=dict(r=10, t=10),
            showactive=True,
            x=0.01, xanchor="left",
            y=1.07, yanchor="top",
            bgcolor=C["panel"], bordercolor=C["accent3"],
            font=dict(color=C["text"], size=12), active=0, type="buttons",
        ),
    ],
    annotations=[
        dict(text="<b>Rango salarial:</b>", x=0.0, xref="paper", y=1.165, yref="paper",
             showarrow=False, font=dict(color=C["subtext"], size=12)),
        dict(text="<b>Tipo empresa:</b>", x=0.0, xref="paper", y=1.075, yref="paper",
             showarrow=False, font=dict(color=C["subtext"], size=12)),
        dict(
            text=(
                f"{FUENTE}  |  Variables: ocupación, salario, tipo de empresa, período de afiliación<br>"
                "<i>La mayoría de las personas afiliadas al IESS antes de su ingreso al sistema\n"
                "percibía salarios inferiores a $400, lo que evidencia condiciones de vulnerabilidad económica.<br>"
                "Los empleos de baja cualificación y el sector privado son los más representados.\n"
                "El filtro por rango salarial permite identificar perfiles socioeconómicos diferenciados.</i>"
            ),
            x=0.5, xref="paper", y=-0.18, yref="paper",
            align="center", showarrow=False,
            font=dict(color=C["subtext"], size=11),
            bordercolor=C["grid"], borderwidth=1,
            bgcolor=C["panel"], borderpad=8,
        ),
    ],
)

fig4.write_html(
    f"{OUT}/I4_ocupaciones_vulnerabilidad.html",
    full_html=True, include_plotlyjs="cdn",
    config={"responsive": True},
)
print("  → I4 guardado")

print("\n✅ Los 4 interactivos fueron generados exitosamente.")
print(f"   Archivos en: {OUT}")
for fn in ["I1_mapa_incidentes.html","I2_burbujas_armas.html",
           "I3_sentencias_educacion.html","I4_ocupaciones_vulnerabilidad.html"]:
    size = os.path.getsize(f"{OUT}/{fn}") // 1024
    print(f"   {fn}  →  {size} KB")