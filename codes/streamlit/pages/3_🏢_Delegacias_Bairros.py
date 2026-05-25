"""
🏢 Página 3 — Delegacias e Bairros
Rankings e concentrações territoriais.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.data_loader import load_sinan_cnes, load_sim, LOCAL_OCORRENCIA_MAP
from utils.charts import apply_theme, COLORS, PALETTE, metric_card_css, render_metric, section_header

st.set_page_config(page_title="Delegacias & Bairros | DDM", page_icon="🏢", layout="wide")
st.markdown(metric_card_css(), unsafe_allow_html=True)

st.markdown("# 🏢 Análise por Delegacias e Bairros")
st.markdown("*Identificando concentrações territoriais da violência — base para o DiD*")
st.markdown("---")

# ─── Dados ────────────────────────────────────────────────────────────
df_sinan = load_sinan_cnes()
df_sim = load_sim()

# ─── Filtros ──────────────────────────────────────────────────────────
ano_range = st.slider("Período", 2015, 2019, (2015, 2019), key="db_ano")
df_filt = df_sinan[(df_sinan['ano'] >= ano_range[0]) & (df_sinan['ano'] <= ano_range[1])]

# ─── KPIs ─────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
bairros_unicos = df_filt['bairro'].dropna().nunique()
with c1:
    st.markdown(render_metric("Bairros Ativos", str(bairros_unicos), "Com notificações"), unsafe_allow_html=True)
with c2:
    top_bairro = df_filt['bairro'].value_counts().index[0] if len(df_filt) > 0 else "N/A"
    top_count = df_filt['bairro'].value_counts().iloc[0] if len(df_filt) > 0 else 0
    st.markdown(render_metric("Bairro Líder", top_bairro, f"{top_count:,.0f} notif."), unsafe_allow_html=True)
with c3:
    encam_ddm = df_filt['encaminhamento_delegacia_mulher'].sum()
    st.markdown(render_metric("Encam. DDM", f"{int(encam_ddm):,.0f}".replace(",", "."),
                              f"{encam_ddm/len(df_filt)*100:.1f}% do total"), unsafe_allow_html=True)
with c4:
    df_sim_filt = df_sim[(df_sim['ano'] >= ano_range[0]) & (df_sim['ano'] <= ano_range[1])]
    fem_count = len(df_sim_filt)
    st.markdown(render_metric("Feminicídios (SIM)", str(fem_count), f"Total SP {ano_range[0]}–{ano_range[1]}", "down"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Tab Layout ───────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["🏘️ Ranking de Bairros", "📋 Cruzamento"])

# ─── Tab 1: Bairros ──────────────────────────────────────────────────
with tab1:
    st.markdown(section_header("Top 25 Bairros por Volume de Notificações (SINAN)"), unsafe_allow_html=True)

    n_bairros = st.slider("Nº de bairros a exibir", 10, 50, 25, key="n_bairros")
    
    bairro_counts = df_filt['bairro'].value_counts().head(n_bairros).reset_index()
    bairro_counts.columns = ['Bairro', 'Notificações']
    bairro_counts = bairro_counts.sort_values('Notificações')

    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        y=bairro_counts['Bairro'],
        x=bairro_counts['Notificações'],
        orientation='h',
        marker=dict(
            color=bairro_counts['Notificações'],
            colorscale=[[0, COLORS['primary']], [0.5, COLORS['secondary']], [1, COLORS['accent']]],
            line=dict(width=0),
        ),
        hovertemplate='<b>%{y}</b><br>Notificações: %{x:,.0f}<extra></extra>',
    ))
    fig1.update_layout(
        title=f"Top {n_bairros} Bairros — Notificações de Violência (SINAN)",
        xaxis_title="Nº de Notificações",
        yaxis_title="",
    )
    apply_theme(fig1, height=max(400, n_bairros * 22), show_legend=False)
    st.plotly_chart(fig1, use_container_width=True)

    # Encaminhamento a DDM por bairro
    st.markdown(section_header("📬 Taxa de Encaminhamento à DDM por Bairro"), unsafe_allow_html=True)

    bairro_ddm = df_filt.groupby('bairro').agg(
        total=('ano', 'count'),
        encam_ddm=('encaminhamento_delegacia_mulher', 'sum'),
    ).reset_index()
    bairro_ddm['taxa_encam'] = (bairro_ddm['encam_ddm'] / bairro_ddm['total'] * 100).round(1)
    bairro_ddm = bairro_ddm[bairro_ddm['total'] >= 50].sort_values('taxa_encam', ascending=False).head(20)

    fig_ddm = go.Figure()
    fig_ddm.add_trace(go.Bar(
        x=bairro_ddm['bairro'],
        y=bairro_ddm['taxa_encam'],
        marker_color=COLORS['secondary'],
        hovertemplate='<b>%{x}</b><br>Taxa: %{y:.1f}%<br>Total notif.: ' + 
                      bairro_ddm['total'].astype(str) + '<extra></extra>',
    ))
    fig_ddm.update_layout(
        title="Taxa de Encaminhamento à Delegacia da Mulher (%) — Bairros com ≥50 notif.",
        xaxis_title="Bairro", yaxis_title="% Encaminhados à DDM",
    )
    apply_theme(fig_ddm, height=420, show_legend=False)
    st.plotly_chart(fig_ddm, use_container_width=True)

# ─── Tab 2: Cruzamento ───────────────────────────────────────────────
with tab2:
    st.markdown(section_header("📋 Bairros × Tipo de Violência"), unsafe_allow_html=True)

    top_bairros = df_filt['bairro'].value_counts().head(15).index.tolist()
    df_cross = df_filt[df_filt['bairro'].isin(top_bairros)].copy()

    cross_table = df_cross.groupby('bairro').agg(
        total=('ano', 'count'),
        v_fisica=('ocorreu_violencia_fisica', 'sum'),
        ameaca=('meio_ameaca', 'sum'),
        v_sexual=('ocorreu_violencia_sexual', 'sum'),
        v_psicol=('ocorreu_violencia_psicologica', 'sum'),
        encam_ddm=('encaminhamento_delegacia_mulher', 'sum'),
    ).reset_index()
    cross_table.columns = ['Bairro', 'Total', 'V. Física', 'Ameaça', 'V. Sexual', 'V. Psicológica', 'Encam. DDM']
    cross_table = cross_table.sort_values('Total', ascending=False)

    st.dataframe(cross_table, hide_index=True, use_container_width=True)

    # Heatmap
    heat_data = cross_table.set_index('Bairro')[['V. Física', 'Ameaça', 'V. Sexual', 'V. Psicológica']].astype(float)
    
    fig_heat = go.Figure(data=go.Heatmap(
        z=heat_data.values,
        x=heat_data.columns.tolist(),
        y=heat_data.index.tolist(),
        colorscale=[[0, COLORS['bg_dark']], [0.3, COLORS['primary']], [0.7, COLORS['secondary']], [1, COLORS['accent']]],
        hovertemplate='<b>%{y}</b><br>%{x}: %{z:,.0f}<extra></extra>',
    ))
    fig_heat.update_layout(title="Heatmap — Bairro × Tipo de Violência")
    apply_theme(fig_heat, height=450, show_legend=False)
    st.plotly_chart(fig_heat, use_container_width=True)

