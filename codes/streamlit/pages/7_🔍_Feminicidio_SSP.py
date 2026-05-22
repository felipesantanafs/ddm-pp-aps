"""
🔍 Página 7 — Painel Feminicídio SSP
Análise dedicada aos dados de feminicídio da SSP.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.data_loader import load_ssp_feminicidio
from utils.charts import apply_theme, COLORS, PALETTE, PALETTE_WARM, metric_card_css, render_metric, section_header

st.set_page_config(page_title="Feminicídio SSP | DDM", page_icon="🔍", layout="wide")
st.markdown(metric_card_css(), unsafe_allow_html=True)

st.markdown("# 🔍 Painel Feminicídio — SSP/SP")
st.markdown("*Análise dedicada dos registros de feminicídio da Secretaria de Segurança Pública (2015–2022)*")
st.markdown("---")

# ─── Dados ────────────────────────────────────────────────────────────
df = load_ssp_feminicidio()

# ─── KPIs ─────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(render_metric("Total Feminicídios", str(len(df)), "2015–2022"), unsafe_allow_html=True)
with c2:
    idade_med = df['IDADE_PESSOA'].dropna().median()
    st.markdown(render_metric("Idade Mediana", f"{idade_med:.0f} anos"), unsafe_allow_html=True)
with c3:
    if 'DESC_TIPOLOCAL' in df.columns:
        pct_res = (df['DESC_TIPOLOCAL'].str.contains('Resid', case=False, na=False).sum() / len(df) * 100)
    else:
        pct_res = 0
    st.markdown(render_metric("Em Residência", f"{pct_res:.0f}%", "Local mais frequente"), unsafe_allow_html=True)
with c4:
    geo_disp = df['LATITUDE'].notna().sum()
    st.markdown(render_metric("Geolocalizado", f"{geo_disp}/{len(df)}", f"{geo_disp/len(df)*100:.0f}%"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Tabs ─────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📈 Evolução", "🏢 Delegacias", "👤 Perfil"])

# ─── Tab 1: Evolução ─────────────────────────────────────────────────
with tab1:
    st.markdown(section_header("📈 Evolução Anual dos Feminicídios (SSP)"), unsafe_allow_html=True)

    ano_counts = df.groupby('ano').size().reset_index(name='total')
    ano_counts = ano_counts.sort_values('ano')

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=ano_counts['ano'], y=ano_counts['total'],
        mode='lines+markers+text',
        text=ano_counts['total'].astype(str),
        textposition='top center',
        textfont=dict(color=COLORS['text'], size=14, family='Inter'),
        line=dict(color=COLORS['danger'], width=3),
        marker=dict(size=12, color=COLORS['danger'], line=dict(width=2, color=COLORS['text'])),
        hovertemplate='<b>%{x}</b><br>Feminicídios: %{y}<extra></extra>',
        name='Feminicídios',
    ))

    # Adicionar linha de tendência
    if len(ano_counts) > 2:
        z = np.polyfit(ano_counts['ano'], ano_counts['total'], 1)
        p = np.poly1d(z)
        fig1.add_trace(go.Scatter(
            x=ano_counts['ano'], y=p(ano_counts['ano']),
            mode='lines',
            line=dict(color=COLORS['text_dim'], width=1.5, dash='dash'),
            name='Tendência Linear',
            hoverinfo='skip',
        ))

    fig1.update_layout(
        title="Feminicídios por Ano — Município de São Paulo (SSP)",
        xaxis_title="Ano", yaxis_title="Nº de Vítimas",
    )
    apply_theme(fig1, height=450)
    st.plotly_chart(fig1, use_container_width=True)

    # Local do fato
    st.markdown(section_header("📍 Local do Fato"), unsafe_allow_html=True)

    if 'DESC_TIPOLOCAL' in df.columns:
        local_counts = df['DESC_TIPOLOCAL'].value_counts().reset_index()
        local_counts.columns = ['Local', 'Total']
        local_counts = local_counts[local_counts['Local'].notna()]

        fig_local = go.Figure(data=[go.Pie(
            labels=local_counts['Local'], values=local_counts['Total'],
            hole=0.5,
            marker=dict(colors=PALETTE_WARM, line=dict(color=COLORS['bg_dark'], width=2)),
            textfont=dict(color=COLORS['text'], size=12),
            hovertemplate='<b>%{label}</b><br>Total: %{value}<br>%{percent}<extra></extra>',
        )])
        fig_local.update_layout(title="Feminicídios por Local do Fato")
        apply_theme(fig_local, height=400)
        st.plotly_chart(fig_local, use_container_width=True)

# ─── Tab 2: Delegacias ───────────────────────────────────────────────
with tab2:
    st.markdown(section_header("🚔 Ranking de DPs — Feminicídios"), unsafe_allow_html=True)

    col_l, col_r = st.columns([3, 2])

    with col_l:
        if 'DP_CIRCUNSCRICAO' in df.columns:
            dp_counts = df['DP_CIRCUNSCRICAO'].value_counts().head(20).reset_index()
            dp_counts.columns = ['DP', 'Feminicídios']
            dp_counts = dp_counts.sort_values('Feminicídios')

            fig_dp = go.Figure()
            fig_dp.add_trace(go.Bar(
                y=dp_counts['DP'],
                x=dp_counts['Feminicídios'],
                orientation='h',
                marker=dict(
                    color=dp_counts['Feminicídios'],
                    colorscale=[[0, COLORS['warning']], [1, COLORS['danger']]],
                ),
                hovertemplate='<b>%{y}</b><br>Feminicídios: %{x}<extra></extra>',
            ))
            fig_dp.update_layout(title="Top 20 DPs (Circunscrição)", xaxis_title="Nº de Casos")
            apply_theme(fig_dp, height=520, show_legend=False)
            st.plotly_chart(fig_dp, use_container_width=True)

    with col_r:
        if 'SECCIONAL_CIRCUNSCRICAO' in df.columns:
            sec_counts = df['SECCIONAL_CIRCUNSCRICAO'].value_counts().reset_index()
            sec_counts.columns = ['Seccional', 'Feminicídios']
            sec_counts = sec_counts.sort_values('Feminicídios')

            fig_sec = go.Figure()
            fig_sec.add_trace(go.Bar(
                y=sec_counts['Seccional'],
                x=sec_counts['Feminicídios'],
                orientation='h',
                marker_color=COLORS['danger'],
                opacity=0.85,
                hovertemplate='<b>%{y}</b><br>Feminicídios: %{x}<extra></extra>',
            ))
            fig_sec.update_layout(title="Por Seccional", xaxis_title="Nº de Casos")
            apply_theme(fig_sec, height=520, show_legend=False)
            st.plotly_chart(fig_sec, use_container_width=True)

    # Evolução por seccional
    st.markdown(section_header("📊 Evolução por Seccional (Top 5)"), unsafe_allow_html=True)

    if 'SECCIONAL_CIRCUNSCRICAO' in df.columns:
        top5_sec = df['SECCIONAL_CIRCUNSCRICAO'].value_counts().head(5).index.tolist()
        df_top5 = df[df['SECCIONAL_CIRCUNSCRICAO'].isin(top5_sec)]
        evol = df_top5.groupby(['ano', 'SECCIONAL_CIRCUNSCRICAO']).size().reset_index(name='total')

        fig_evol = go.Figure()
        for i, sec in enumerate(top5_sec):
            subset = evol[evol['SECCIONAL_CIRCUNSCRICAO'] == sec]
            fig_evol.add_trace(go.Scatter(
                x=subset['ano'], y=subset['total'],
                name=sec,
                mode='lines+markers',
                line=dict(width=2, color=PALETTE[i]),
                marker=dict(size=8),
                hovertemplate=f'<b>{sec}</b><br>Ano: %{{x}}<br>Feminicídios: %{{y}}<extra></extra>',
            ))
        fig_evol.update_layout(
            title="Evolução Anual — Top 5 Seccionais",
            xaxis_title="Ano", yaxis_title="Feminicídios",
        )
        apply_theme(fig_evol, height=420)
        st.plotly_chart(fig_evol, use_container_width=True)

# ─── Tab 3: Perfil ───────────────────────────────────────────────────
with tab3:
    col_p1, col_p2 = st.columns(2)

    with col_p1:
        st.markdown(section_header("📊 Distribuição Etária"), unsafe_allow_html=True)

        idades = df['IDADE_PESSOA'].dropna()
        fig_idade = go.Figure()
        fig_idade.add_trace(go.Histogram(
            x=idades,
            nbinsx=25,
            marker_color=COLORS['danger'],
            opacity=0.8,
            hovertemplate='Idade: %{x}<br>Casos: %{y}<extra></extra>',
        ))
        media_idade = idades.mean()
        fig_idade.add_vline(x=media_idade, line_dash="dash", line_color=COLORS['warning'],
                           annotation_text=f"Média: {media_idade:.1f}", annotation_position="top")
        fig_idade.update_layout(title="Idade das Vítimas de Feminicídio", xaxis_title="Idade", yaxis_title="Frequência")
        apply_theme(fig_idade, height=380, show_legend=False)
        st.plotly_chart(fig_idade, use_container_width=True)

    with col_p2:
        st.markdown(section_header("🎨 Cor/Raça"), unsafe_allow_html=True)

        if 'COR_PELE' in df.columns:
            cor_counts = df['COR_PELE'].value_counts().reset_index()
            cor_counts.columns = ['Cor/Raça', 'Total']
            cor_counts = cor_counts[cor_counts['Cor/Raça'].notna()]

            raca_colors = {
                'Branca': COLORS['accent'],
                'Parda': COLORS['warning'],
                'Preta': COLORS['danger'],
                'Amarela': '#F1C40F',
            }
            colors = [raca_colors.get(r, COLORS['text_dim']) for r in cor_counts['Cor/Raça']]

            fig_cor = go.Figure(data=[go.Pie(
                labels=cor_counts['Cor/Raça'], values=cor_counts['Total'],
                hole=0.5,
                marker=dict(colors=colors, line=dict(color=COLORS['bg_dark'], width=2)),
                textfont=dict(color=COLORS['text']),
                hovertemplate='<b>%{label}</b><br>Total: %{value}<br>%{percent}<extra></extra>',
            )])
            fig_cor.update_layout(title="Distribuição por Cor/Raça")
            apply_theme(fig_cor, height=380)
            st.plotly_chart(fig_cor, use_container_width=True)

    # Profissão
    st.markdown(section_header("💼 Profissão das Vítimas"), unsafe_allow_html=True)

    if 'PROFISSAO' in df.columns:
        prof_counts = df['PROFISSAO'].value_counts().head(15).reset_index()
        prof_counts.columns = ['Profissão', 'Total']
        prof_counts = prof_counts.sort_values('Total')

        fig_prof = go.Figure()
        fig_prof.add_trace(go.Bar(
            y=prof_counts['Profissão'],
            x=prof_counts['Total'],
            orientation='h',
            marker=dict(
                color=prof_counts['Total'],
                colorscale=[[0, COLORS['primary']], [1, COLORS['secondary']]],
            ),
            hovertemplate='<b>%{y}</b><br>Casos: %{x}<extra></extra>',
        ))
        fig_prof.update_layout(title="Top 15 Profissões", xaxis_title="Nº de Casos")
        apply_theme(fig_prof, height=450, show_legend=False)
        st.plotly_chart(fig_prof, use_container_width=True)

st.markdown("---")
st.markdown("""
<div class="insight-box">
    💡 <strong>Resumo SSP</strong>: Os dados de feminicídio da SSP complementam os do SIM/DataSUS
    com variáveis institucionais (delegacia de circunscrição, local exato do fato, hora).
    A predominância de casos em residência e a concentração em seccionais específicas
    indicam territorialidade marcada — informação crucial para o pareamento no modelo DiD.
</div>
""", unsafe_allow_html=True)
