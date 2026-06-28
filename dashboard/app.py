# ==========================================================
# Predictor Pro 3.0
# dashboard/app.py (VERSÃO COM API DADOS FUTEBOL)
# ==========================================================

import os
import requests
import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv(dotenv_path="../.env")

# ==========================================================
# CONEXÃO SUPABASE
# ==========================================================

@st.cache_resource
def conectar() -> Client:
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    except Exception:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise Exception("Credenciais Supabase não encontradas")
    return create_client(url, key)

# ==========================================================
# CARREGAR DADOS DO BANCO
# ==========================================================

def carregar_times():
    try:
        supabase = conectar()
        resp = supabase.table("estatisticas_times").select("*").execute()
        if not resp.data:
            raise Exception("Tabela vazia.")
        dados = {}
        for row in resp.data:
            dados[row["time"]] = {
                "g_casa":    float(row.get("g_casa") or 0),
                "g_fora":    float(row.get("g_fora") or 0),
                "c_casa":    float(row.get("c_casa") or 0),
                "c_fora":    float(row.get("c_fora") or 0),
                "cart_casa": float(row.get("cart_casa") or 0),
                "cart_fora": float(row.get("cart_fora") or 0),
            }
        return dados, True
    except Exception:
        return DADOS_FALLBACK, False

def carregar_tabela():
    try:
        supabase = conectar()
        resp = supabase.table("tabela_serie_b").select("*").order("posicao").execute()
        if resp.data:
            return resp.data
        return []
    except Exception:
        return []

def carregar_rodada():
    try:
        supabase = conectar()
        resp = supabase.table("rodada_atual").select("*").order("data").execute()
        if resp.data:
            return resp.data
        return []
    except Exception:
        return []

# ==========================================================
# DADOS FALLBACK
# ==========================================================

DADOS_FALLBACK = {
    "America-MG":    {"g_casa": 1.0, "g_fora": 0.5, "c_casa": 4.5, "c_fora": 3.4, "cart_casa": 2.6, "cart_fora": 3.6},
    "Athletic Club": {"g_casa": 1.4, "g_fora": 0.9, "c_casa": 5.2, "c_fora": 4.0, "cart_casa": 2.3, "cart_fora": 3.1},
    "Atletico-GO":   {"g_casa": 1.4, "g_fora": 0.8, "c_casa": 5.3, "c_fora": 4.1, "cart_casa": 2.4, "cart_fora": 3.2},
    "Avai":          {"g_casa": 1.2, "g_fora": 0.7, "c_casa": 4.9, "c_fora": 3.9, "cart_casa": 2.6, "cart_fora": 3.5},
    "Botafogo-SP":   {"g_casa": 1.2, "g_fora": 0.7, "c_casa": 4.9, "c_fora": 3.7, "cart_casa": 2.3, "cart_fora": 3.2},
    "Ceara":         {"g_casa": 1.5, "g_fora": 0.8, "c_casa": 5.6, "c_fora": 4.2, "cart_casa": 2.5, "cart_fora": 3.3},
    "CRB":           {"g_casa": 1.4, "g_fora": 0.7, "c_casa": 5.2, "c_fora": 3.8, "cart_casa": 2.4, "cart_fora": 3.1},
    "Criciuma":      {"g_casa": 1.4, "g_fora": 1.0, "c_casa": 5.3, "c_fora": 4.2, "cart_casa": 2.4, "cart_fora": 3.2},
    "Cuiaba":        {"g_casa": 1.2, "g_fora": 0.7, "c_casa": 4.8, "c_fora": 3.6, "cart_casa": 2.1, "cart_fora": 2.7},
    "Fortaleza":     {"g_casa": 1.6, "g_fora": 0.9, "c_casa": 5.9, "c_fora": 4.1, "cart_casa": 2.3, "cart_fora": 3.0},
    "Goias":         {"g_casa": 1.3, "g_fora": 0.8, "c_casa": 5.1, "c_fora": 3.9, "cart_casa": 2.6, "cart_fora": 3.5},
    "Juventude":     {"g_casa": 1.4, "g_fora": 1.0, "c_casa": 5.4, "c_fora": 4.2, "cart_casa": 2.4, "cart_fora": 3.1},
    "Londrina":      {"g_casa": 1.3, "g_fora": 0.6, "c_casa": 5.0, "c_fora": 3.7, "cart_casa": 2.5, "cart_fora": 3.4},
    "Nautico":       {"g_casa": 1.6, "g_fora": 0.9, "c_casa": 5.7, "c_fora": 4.3, "cart_casa": 2.5, "cart_fora": 3.4},
    "Novorizontino": {"g_casa": 1.5, "g_fora": 1.1, "c_casa": 5.6, "c_fora": 4.6, "cart_casa": 2.2, "cart_fora": 2.9},
    "Operario-PR":   {"g_casa": 1.5, "g_fora": 0.9, "c_casa": 5.5, "c_fora": 4.0, "cart_casa": 2.1, "cart_fora": 2.8},
    "Ponte Preta":   {"g_casa": 1.1, "g_fora": 0.6, "c_casa": 4.7, "c_fora": 3.5, "cart_casa": 2.7, "cart_fora": 3.7},
    "Sao Bernardo":  {"g_casa": 1.6, "g_fora": 1.1, "c_casa": 5.8, "c_fora": 4.3, "cart_casa": 2.2, "cart_fora": 2.9},
    "Sport":         {"g_casa": 1.8, "g_fora": 1.1, "c_casa": 6.5, "c_fora": 4.9, "cart_casa": 1.9, "cart_fora": 2.6},
    "Vila Nova":     {"g_casa": 1.9, "g_fora": 1.2, "c_casa": 6.2, "c_fora": 4.5, "cart_casa": 2.0, "cart_fora": 2.5},
}

# ==========================================================
# NOTÍCIAS
# ==========================================================

def buscar_noticias():
    try:
        url = "https://ge.globo.com/futebol/"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            titulos = soup.select("a.feed-post-link, h2 a, .post__title a")
            textos = [t.get_text(strip=True) for t in titulos if len(t.get_text(strip=True)) > 15]
            if textos:
                return textos[:8]
        return ["Sem noticias no momento."]
    except Exception:
        return ["Modo local - noticias indisponiveis."]

# ==========================================================
# PALPITE DE LINHA
# ==========================================================

def palpite_linha(media: float) -> str:
    linhas = [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5]
    linha = 0.5
    for l in linhas:
        if media > l:
            linha = l
        else:
            break
    return f"Over {linha}"

# ==========================================================
# MOTOR DE PREVISÃO
# ==========================================================

def calcular_previsao(tc, tf, dados):
    d_casa = dados[tc]
    d_fora = dados[tf]

    g_casa = d_casa["g_casa"]
    g_fora = d_fora["g_fora"]
    total  = g_casa + g_fora or 1.0

    p_casa   = (g_casa / total) * 75.0
    p_fora   = (g_fora / total) * 75.0
    p_empate = 25.0
    soma = p_casa + p_empate + p_fora or 1.0
    p_casa   = round((p_casa   / soma) * 100, 1)
    p_empate = round((p_empate / soma) * 100, 1)
    p_fora   = round((p_fora   / soma) * 100, 1)

    gols_jogo       = round(g_casa + g_fora, 2)
    gols_1t         = round(gols_jogo / 2, 2)
    escanteios_jogo = round(d_casa["c_casa"] + d_fora["c_fora"], 1)
    escanteios_1t   = round(escanteios_jogo / 2, 1)
    cartoes_jogo    = round(d_casa["cart_casa"] + d_fora["cart_fora"], 1)

    return {
        "p_casa": p_casa, "p_empate": p_empate, "p_fora": p_fora,
        "gols_jogo": gols_jogo, "gols_1t": gols_1t,
        "esc_jogo": escanteios_jogo, "esc_1t": escanteios_1t,
        "cartoes_jogo": cartoes_jogo,
        "linha_gols_jogo": palpite_linha(gols_jogo),
        "linha_gols_1t":   palpite_linha(gols_1t),
        "linha_esc_jogo":  palpite_linha(escanteios_jogo),
        "linha_esc_1t":    palpite_linha(escanteios_1t),
        "linha_cart_jogo": palpite_linha(cartoes_jogo),
    }

# ==========================================================
# CSS
# ==========================================================

st.markdown("""
<style>
    .stApp { background-color: #0e1117; }

    .card-result {
        background: #1a1f2e; border-radius: 12px;
        padding: 18px 10px; text-align: center;
        border: 1px solid #2a3040;
    }
    .card-result .label { color: #8892a4; font-size: 13px; margin-bottom: 4px; }
    .card-result .time  { color: #ffffff; font-size: 15px; font-weight: 700; margin-bottom: 8px; }
    .card-result .pct   { font-size: 28px; font-weight: 900; }
    .pct-casa   { color: #3b82f6; }
    .pct-empate { color: #f59e0b; }
    .pct-fora   { color: #ef4444; }

    .palpite-card {
        background: #1a1f2e; border-radius: 10px;
        padding: 14px 16px; border: 1px solid #2a3040; margin-bottom: 10px;
    }
    .palpite-card .titulo { color: #8892a4; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; }
    .palpite-card .valor  { color: #ffffff; font-size: 22px; font-weight: 800; margin: 4px 0; }
    .palpite-card .linha  { color: #10b981; font-size: 14px; font-weight: 600; }
    .palpite-card .media  { color: #6b7280; font-size: 12px; }

    .jogo-card {
        background: #1a1f2e; border-radius: 10px;
        padding: 14px 18px; border: 1px solid #2a3040; margin-bottom: 10px;
    }
    .jogo-card .times { color: #ffffff; font-size: 16px; font-weight: 700; text-align: center; }
    .jogo-card .info  { color: #8892a4; font-size: 12px; text-align: center; margin-top: 4px; }
    .jogo-card .placar { color: #10b981; font-size: 20px; font-weight: 900; text-align: center; margin-top: 6px; }
    .status-agendada  { color: #f59e0b; font-size: 11px; font-weight: 600; }
    .status-encerrada { color: #6b7280; font-size: 11px; }
    .status-andamento { color: #10b981; font-size: 11px; font-weight: 700; }

    .noticia-item { padding: 8px 0; border-bottom: 1px solid #1e2433; color: #cbd5e1; font-size: 14px; }

    .barra-wrap { margin: 6px 0 14px 0; }
    .barra-label { display: flex; justify-content: space-between; color: #8892a4; font-size: 12px; margin-bottom: 4px; }
    .barra-bg { background: #1e2433; border-radius: 6px; height: 10px; width: 100%; }
    .barra-fill-casa   { background: #3b82f6; border-radius: 6px; height: 10px; }
    .barra-fill-empate { background: #f59e0b; border-radius: 6px; height: 10px; }
    .barra-fill-fora   { background: #ef4444; border-radius: 6px; height: 10px; }
</style>
""", unsafe_allow_html=True)

# ==========================================================
# LAYOUT
# ==========================================================

st.markdown("## Predictor Pro 3.0")

dados_times, banco_ok = carregar_times()
if banco_ok:
    st.success("Supabase conectado")
else:
    st.warning("Banco indisponivel - usando dados locais")

times_ordenados = sorted(dados_times.keys())

aba_preditor, aba_rodada, aba_tabela = st.tabs([
    "Preditor", "Jogos da Rodada", "Tabela Serie B"
])

# ======================================================
# ABA 1 — PREDITOR
# ======================================================
with aba_preditor:

    col1, col2 = st.columns(2)
    with col1:
        default_casa = "America-MG" if "America-MG" in times_ordenados else times_ordenados[0]
        tc = st.selectbox("Time da Casa", times_ordenados, index=times_ordenados.index(default_casa))
    with col2:
        default_fora = "Operario-PR" if "Operario-PR" in times_ordenados else times_ordenados[-1]
        tf = st.selectbox("Time de Fora", times_ordenados, index=times_ordenados.index(default_fora))

    if tc == tf:
        st.error("Selecione times diferentes.")
        st.stop()

    res = calcular_previsao(tc, tf, dados_times)

    st.markdown("---")
    st.markdown("#### Probabilidades 1X2")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class="card-result">
            <div class="label">Casa</div><div class="time">{tc}</div>
            <div class="pct pct-casa">{res['p_casa']}%</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="card-result">
            <div class="label">Empate</div><div class="time">—</div>
            <div class="pct pct-empate">{res['p_empate']}%</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="card-result">
            <div class="label">Fora</div><div class="time">{tf}</div>
            <div class="pct pct-fora">{res['p_fora']}%</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    for label, pct, cor in [(tc, res['p_casa'], "casa"), ("Empate", res['p_empate'], "empate"), (tf, res['p_fora'], "fora")]:
        st.markdown(f"""<div class="barra-wrap">
            <div class="barra-label"><span>{label}</span><span>{pct}%</span></div>
            <div class="barra-bg"><div class="barra-fill-{cor}" style="width:{pct}%"></div></div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Palpites")

    cg, ce, cc = st.columns(3)
    with cg:
        st.markdown("**Gols**")
        st.markdown(f"""
        <div class="palpite-card">
            <div class="titulo">1 Tempo</div>
            <div class="valor">{res['gols_1t']}</div>
            <div class="linha">Sugestao: {res['linha_gols_1t']}</div>
            <div class="media">media esperada</div>
        </div>
        <div class="palpite-card">
            <div class="titulo">Jogo Todo</div>
            <div class="valor">{res['gols_jogo']}</div>
            <div class="linha">Sugestao: {res['linha_gols_jogo']}</div>
            <div class="media">media esperada</div>
        </div>""", unsafe_allow_html=True)
    with ce:
        st.markdown("**Escanteios**")
        st.markdown(f"""
        <div class="palpite-card">
            <div class="titulo">1 Tempo</div>
            <div class="valor">{res['esc_1t']}</div>
            <div class="linha">Sugestao: {res['linha_esc_1t']}</div>
            <div class="media">media esperada</div>
        </div>
        <div class="palpite-card">
            <div class="titulo">Jogo Todo</div>
            <div class="valor">{res['esc_jogo']}</div>
            <div class="linha">Sugestao: {res['linha_esc_jogo']}</div>
            <div class="media">media esperada</div>
        </div>""", unsafe_allow_html=True)
    with cc:
        st.markdown("**Cartoes Amarelos**")
        st.markdown(f"""
        <div class="palpite-card">
            <div class="titulo">Jogo Todo</div>
            <div class="valor">{res['cartoes_jogo']}</div>
            <div class="linha">Sugestao: {res['linha_cart_jogo']}</div>
            <div class="media">media esperada</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Ultimas Noticias")
    if "noticias" not in st.session_state:
        with st.spinner("Buscando noticias..."):
            st.session_state["noticias"] = buscar_noticias()
    for n in st.session_state["noticias"]:
        st.markdown(f'<div class="noticia-item">- {n}</div>', unsafe_allow_html=True)
    if st.button("Atualizar Noticias"):
        del st.session_state["noticias"]
        st.rerun()

# ======================================================
# ABA 2 — JOGOS DA RODADA
# ======================================================
with aba_rodada:
    st.markdown("#### Jogos da Rodada Atual — Serie B 2026")

    partidas = carregar_rodada()

    if not partidas:
        st.info("Nenhum jogo encontrado. Clique em Atualizar para buscar via API.")
    else:
        rodada_num = partidas[0].get("rodada", "?")
        st.markdown(f"**Rodada {rodada_num}**")
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        for p in partidas:
            status = p.get("status", "agendada").lower()
            mandante  = p.get("mandante", "")
            visitante = p.get("visitante", "")
            data  = p.get("data", "")
            hora  = p.get("hora", "")
            gm = p.get("gols_mandante")
            gv = p.get("gols_visitante")

            if status == "encerrada":
                css_status = "status-encerrada"
                label_status = "Encerrada"
                placar_html = f'<div class="placar">{gm} x {gv}</div>'
            elif status in ("andamento", "ao_vivo"):
                css_status = "status-andamento"
                label_status = "AO VIVO"
                placar_html = f'<div class="placar">{gm} x {gv}</div>'
            else:
                css_status = "status-agendada"
                label_status = f"{data} {hora}"
                placar_html = ""

            st.markdown(f"""
            <div class="jogo-card">
                <div class="times">{mandante} x {visitante}</div>
                {placar_html}
                <div class="info">
                    <span class="{css_status}">{label_status}</span>
                    {"&nbsp;|&nbsp;" + p.get("estadio","") if p.get("estadio") else ""}
                </div>
            </div>""", unsafe_allow_html=True)

    if st.button("Atualizar Jogos via API"):
        with st.spinner("Buscando dados..."):
            try:
                import subprocess
                subprocess.run(["python", "-c",
                    "from raspador import atualizar_dados_api; atualizar_dados_api()"],
                    cwd="..", timeout=30)
                st.success("Dados atualizados! Recarregue a pagina.")
            except Exception as e:
                st.error(f"Erro: {e}")

# ======================================================
# ABA 3 — TABELA SÉRIE B
# ======================================================
with aba_tabela:
    st.markdown("#### Classificacao — Serie B 2026")

    tabela = carregar_tabela()

    if not tabela:
        st.info("Tabela ainda nao carregada. Clique em Atualizar para buscar via API.")
    else:
        df = pd.DataFrame(tabela)
        colunas = ["posicao","time","pontos","jogos","vitorias","empates","derrotas","gols_pro","gols_contra","saldo"]
        colunas_existentes = [c for c in colunas if c in df.columns]
        df = df[colunas_existentes].rename(columns={
            "posicao": "Pos", "time": "Time", "pontos": "PTS",
            "jogos": "PJ", "vitorias": "V", "empates": "E",
            "derrotas": "D", "gols_pro": "GP", "gols_contra": "GC", "saldo": "SG"
        })

        def colorir(row):
            pos = row["Pos"]
            if pos <= 4:
                return ["background-color: #14532d; color: white"] * len(row)
            elif pos >= 17:
                return ["background-color: #7f1d1d; color: white"] * len(row)
            return [""] * len(row)

        st.dataframe(df.style.apply(colorir, axis=1), use_container_width=True, hide_index=True)
        st.markdown("""
        <div style='margin-top:8px; font-size:13px; color:#6b7280'>
            Verde = Acesso a Serie A | Vermelho = Rebaixamento a Serie C
        </div>""", unsafe_allow_html=True)

    if st.button("Atualizar Tabela via API"):
        with st.spinner("Buscando dados..."):
            try:
                import subprocess
                subprocess.run(["python", "-c",
                    "from raspador import atualizar_dados_api; atualizar_dados_api()"],
                    cwd="..", timeout=30)
                st.success("Dados atualizados! Recarregue a pagina.")
            except Exception as e:
                st.error(f"Erro: {e}")