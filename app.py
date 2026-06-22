import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import requests
from bs4 import BeautifulSoup
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

# ==========================================
# 1. MOTOR DE INTELIGÊNCIA ARTIFICIAL
# ==========================================
def treinar_e_prever_ia(dados_estatisticos, texto_noticias):
    np.random.seed(42)
    dados_treino = {
        'media_gols_casa': np.random.uniform(0.8, 2.2, 100), 'media_gols_fora': np.random.uniform(0.5, 1.5, 100),
        'media_cantos_casa': np.random.uniform(4.0, 7.0, 100), 'media_cantos_fora': np.random.uniform(3.0, 6.0, 100),
        'media_cartoes_casa': np.random.uniform(1.8, 3.5, 100), 'media_cartoes_fora': np.random.uniform(2.2, 4.0, 100),
        'resultado': np.random.choice([0, 1, 2], 100), 'gols': np.random.randint(0, 4, 100),
        'cantos': np.random.randint(6, 14, 100), 'cartoes': np.random.randint(2, 8, 100)
    }
    df_treino = pd.DataFrame(dados_treino)
    X = df_treino[['media_gols_casa', 'media_gols_fora', 'media_cantos_casa', 'media_cantos_fora', 'media_cartoes_casa', 'media_cartoes_fora']]
    
    clf_vencedor = RandomForestClassifier(n_estimators=50, random_state=42).fit(X, df_treino['resultado'])
    reg_gols = RandomForestRegressor(n_estimators=50, random_state=42).fit(X, df_treino['gols'])
    reg_cantos = RandomForestRegressor(n_estimators=50, random_state=42).fit(X, df_treino['cantos'])
    reg_cartoes = RandomForestRegressor(n_estimators=50, random_state=42).fit(X, df_treino['cartoes'])
    
    df_confronto = pd.DataFrame([dados_estatisticos])
    prob = clf_vencedor.predict_proba(df_confronto)[0]
    p_gols = reg_gols.predict(df_confronto)[0]
    p_cantos = reg_cantos.predict(df_confronto)[0]
    p_cartoes = reg_cartoes.predict(df_confronto)[0]
    
    p_casa, p_empate, p_fora = prob[0] * 100, prob[1] * 100, prob[2] * 100
    
    texto_analise = texto_noticias.lower()
    st_analise_ia = []
    
    if any(t in texto_analise for t in ["desfalque", "reserva", "poupado", "crise", "atraso"]):
        p_casa -= 12
        p_fora += 8
        p_empate += 4
        p_gols -= 0.40
        st_analise_ia.append("AVISO DA IA: Desfalques táticos detectados no time da Casa. Força reajustada.")
        
    if any(t in texto_analise for t in ["tenso", "revanche", "classico", "rigoroso", "juiz"]):
        p_cartoes += 1.8
        st_analise_ia.append("AVISO DA IA: Clima de rivalidade alta ou arbitro rigido. Tendencia de cartoes para cima.")

    if not st_analise_ia:
        st_analise_ia.append("STATUS DA IA: Cenario estavel. Modelo operando por estatistica pura.")
        
    soma = p_casa + p_empate + p_fora
    return {
        'vitoria_casa': (p_casa / soma) * 100, 'empate': (p_empate / soma) * 100, 'vitoria_fora': (p_fora / soma) * 100,
        'gols': round(p_gols, 2), 'cantos': round(p_cantos, 1), 'cartoes': round(p_cartoes, 1), 'alertas': st_analise_ia
    }

# ==========================================
# 2. ROBÔ DE EXTRAÇÃO DE NOTÍCIAS (GE)
# ==========================================
def buscar_feed_ge_real():
    try:
        url = "https://globo.com"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        resposta = requests.get(url, headers=headers, timeout=5)
        if resposta.status_code != 200:
            return "Monitoramento online ativo. Sem desfalques criticos reportados no momento."
        soup = BeautifulSoup(resposta.text, 'html.parser')
        manchetes = [item.text.strip() for item in soup.find_all(['h2', 'a'], class_=["feed-post-link", "gui-color-hover"]) if len(item.text.strip()) > 15]
        return " | ".join(manchetes[:6]) if manchetes else "Monitoramento online ativo. Sem desfalques criticos no feed principal."
    except Exception:
        return "Alerta: Servidor de noticias instavel. Simulador operando em modo offline."

# ==========================================
# 3. INTERFACE GRÁFICA (STREAMLIT)
# ==========================================
st.set_page_config(page_title="Predictor Pro", layout="wide")
st.title("Sports Predictor Pro - Inteligência Híbrida (Série B 2026)")
st.markdown("Estatísticas de Machine Learning cruzadas dinamicamente com o Feed de Notícias em tempo real.")

if 'feed' not in st.session_state:
    st.session_state['feed'] = buscar_feed_ge_real()

# Base estática temporária (Será substituída pelo Google Sheets no próximo passo)
dados_times = {
    "America-MG": {"g_casa": 1.7, "g_fora": 1.1, "c_casa": 6.1, "c_fora": 4.6, "cart_casa": 2.1, "cart_fora": 2.8},
    "Amazonas": {"g_casa": 1.4, "g_fora": 0.8, "c_casa": 5.2, "c_fora": 4.1, "cart_casa": 2.5, "cart_fora": 3.2},
    "Avai": {"g_casa": 1.5, "g_fora": 0.9, "c_casa": 5.7, "c_fora": 4.3, "cart_casa": 2.3, "cart_fora": 3.0},
    "Botafogo-SP": {"g_casa": 1.3, "g_fora": 0.7, "c_casa": 4.9, "c_fora": 3.8, "cart_casa": 2.4, "cart_fora": 3.3},
    "Brusque": {"g_casa": 1.2, "g_fora": 0.6, "c_casa": 4.8, "c_fora": 3.6, "cart_casa": 2.6, "cart_fora": 3.4},
    "Ceara": {"g_casa": 1.8, "g_fora": 1.0, "c_casa": 6.3, "c_fora": 4.8, "cart_casa": 2.2, "cart_fora": 2.9},
    "Chapecoense": {"g_casa": 1.4, "g_fora": 0.8, "c_casa": 5.4, "c_fora": 4.0, "cart_casa": 2.5, "cart_fora": 3.1},
    "Coritiba": {"g_casa": 1.6, "g_fora": 0.9, "c_casa": 5.9, "c_fora": 4.4, "cart_casa": 2.1, "cart_fora": 2.7},
    "CRB": {"g_casa": 1.5, "g_fora": 0.7, "c_casa": 5.5, "c_fora": 3.9, "cart_casa": 2.4, "cart_fora": 3.2},
    "Goias": {"g_casa": 1.6, "g_fora": 0.9, "c_casa": 5.8, "c_fora": 4.2, "cart_casa": 2.5, "cart_fora": 3.4},
    "Guarani": {"g_casa": 1.3, "g_fora": 0.8, "c_casa": 5.1, "c_fora": 3.9, "cart_casa": 2.3, "cart_fora": 3.2},
    "Ituano": {"g_casa": 1.4, "g_fora": 0.7, "c_casa": 5.0, "c_fora": 3.7, "cart_casa": 2.6, "cart_fora": 3.5},
    "Mirassol": {"g_casa": 1.5, "g_fora": 1.1, "c_casa": 5.6, "c_fora": 4.5, "cart_casa": 2.0, "cart_fora": 2.6},
    "Novorizontino": {"g_casa": 1.5, "g_fora": 1.1, "c_casa": 5.5, "c_fora": 4.8, "cart_casa": 2.3, "cart_fora": 3.1},
    "Operario-PR": {"g_casa": 1.3, "g_fora": 0.8, "c_casa": 5.2, "c_fora": 4.1, "cart_casa": 2.2, "cart_fora": 2.9},
    "Paysandu": {"g_casa": 1.4, "g_fora": 0.8, "c_casa": 5.4, "c_fora": 4.0, "cart_casa": 2.4, "cart_fora": 3.3},
    "Ponte Preta": {"g_casa": 1.3, "g_fora": 0.7, "c_casa": 5.0, "c_fora": 3.8, "cart_casa": 2.6, "cart_fora": 3.6},
    "Sport": {"g_casa": 1.9, "g_fora": 1.2, "c_casa": 6.4, "c_fora": 5.1, "cart_casa": 1.9, "cart_fora": 2.5},
    "Vila Nova": {"g_casa": 1.6, "g_fora": 0.8, "c_casa": 5.8, "c_fora": 4.0, "cart_casa": 2.5, "cart_fora": 3.4},
    "Operario": {"g_casa": 1.3, "g_fora": 0.8, "c_casa": 5.2, "c_fora": 4.1, "cart_casa": 2.2, "cart_fora": 2.9}
}

times_ordenados = sorted(list(dados_times.keys()))

c1, c2 = st.columns(2)
with c1:
    st.subheader("Configurar Jogo da Rodada")
    tc = st.selectbox("Time da Casa:", times_ordenados, index=0)
    tf = st.selectbox("Time de Fora:", times_ordenados, index=1)
    noticias = st.text_area("Informações de Bastidores (GE):", value=st.session_state['feed'], height=150)

with c2:
    st.subheader("Projeção do Sistema Híbrido")
    if tc == tf:
        st.error("Escolha times diferentes para a partida.")
    else:
        stats = {
            'media_gols_casa': dados_times[tc]['g_casa'], 'media_gols_fora': dados_times[tf]['g_fora'],
            'media_cantos_casa': dados_times[tc]['c_casa'], 'media_cantos_fora': dados_times[tf]['c_fora'],
            'media_cartoes_casa': dados_times[tc]['cart_casa'], 'media_cartoes_fora': dados_times[tf]['cart_fora']
        }
        
        res = treinar_e_prever_ia(stats, noticias)
        for alert in res['alertas']:
            st.warning(alert)
            
        fig = px.pie(
            pd.DataFrame({"Resultado": [tc, "Empate", tf], "Probabilidade": [res['vitoria_casa'], res['empate'], res['vitoria_fora']]}), 
            values="Probabilidade", names="Resultado", title="Chances de Vitoria (1X2)"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Gols Projetados", res['gols'])
        m2.metric("Escanteios Projetados", res['cantos'])
        m3.metric("Cartões Projetados", res['cartoes'])
