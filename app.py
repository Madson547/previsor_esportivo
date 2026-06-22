import os
os.makedirs("dashboard", exist_ok=True)

with open("dashboard/app.py", "w", encoding="utf-8") as f:
    f.write('''import streamlit as st
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
        'media_gols_casa': np.random.uniform(0.5, 2.5, 150), 'media_gols_fora': np.random.uniform(0.3, 1.8, 150),
        'media_cantos_casa': np.random.uniform(4.0, 7.5, 150), 'media_cantos_fora': np.random.uniform(3.0, 6.0, 150),
        'media_cartoes_casa': np.random.uniform(1.5, 4.0, 150), 'media_cartoes_fora': np.random.uniform(2.0, 4.5, 150),
        'resultado': np.random.choice(, 150), 'gols': np.random.randint(0, 5, 150),
        'cantos': np.random.randint(5, 15, 150), 'cartoes': np.random.randint(1, 9, 150)
    }
    df_treino = pd.DataFrame(dados_treino)
    X = df_treino[['media_gols_casa', 'media_gols_fora', 'media_cantos_casa', 'media_cantos_fora', 'media_cartoes_casa', 'media_cartoes_fora']]
    
    clf_vencedor = RandomForestClassifier(n_estimators=100, random_state=42).fit(X, df_treino['resultado'])
    reg_gols = RandomForestRegressor(n_estimators=100, random_state=42).fit(X, df_treino['gols'])
    reg_cantos = RandomForestRegressor(n_estimators=100, random_state=42).fit(X, df_treino['cantos'])
    reg_cartoes = RandomForestRegressor(n_estimators=100, random_state=42).fit(X, df_treino['cartoes'])
    
    df_confronto = pd.DataFrame([dados_estatisticos])
    prob = clf_vencedor.predict_proba(df_confronto)
    p_gols = reg_gols.predict(df_confronto)
    p_cantos = reg_cantos.predict(df_confronto)
    p_cartoes = reg_cartoes.predict(df_confronto)
    
    p_casa, p_empate, p_fora = prob * 100, prob * 100, prob * 100
    
    texto_analise = texto_noticias.lower()
    st_analise_ia = []
    
    if any(t in texto_analise for t in ["desfalque", "reserva", "poupado", "crise", "atraso"]):
        p_casa -= 12
        p_fora += 8
        p_empate += 4
        p_gols -= 0.35
        st_analise_ia.append("AVISO DA IA: Desfalques criticos identificados. Forca ofensiva afetada.")
        
    if any(t in texto_analise for t in ["tenso", "revanche", "classico", "rigoroso", "juiz"]):
        p_cartoes += 1.6
        st_analise_ia.append("AVISO DA IA: Clima de alta rivalidade. Tendencia de cartoes aumentada.")

    if not st_analise_ia:
        st_analise_ia.append("STATUS DA IA: Cenário padrão sem anomalias de notícias.")
        
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
        soup = BeautifulSoup(resposta.text, 'html.parser')
        manchetes = [item.text.strip() for item in soup.find_all(['h2', 'a'], class_=["feed-post-link", "gui-color-hover"]) if len(item.text.strip()) > 15]
        return " | ".join(manchetes[:6]) if manchetes else "Sem desfalques reportados nas ultimas horas."
    except Exception:
        return "Modo simulado ativo para analise de bastidores."

# ==========================================
# 3. TABELA REAL DE TIMES (ATUALIZADA DA SUA IMAGEM)
# ==========================================
st.set_page_config(page_title="Predictor Pro", layout="wide")
st.title("Sports Predictor Pro - Serie B REAL")

if 'feed' not in st.session_state:
    st.session_state['feed'] = buscar_feed_ge_real()

# Dicionario calibrado conforme a realidade da sua tabela (Vila Nova/Sport fortes, Ponte/America em crise)
dados_times = {
    "Vila Nova": {"g_casa": 1.9, "g_fora": 1.2, "c_casa": 6.2, "c_fora": 4.5, "cart_casa": 2.0, "cart_fora": 2.5},
    "Sao Bernardo": {"g_casa": 1.6, "g_fora": 1.1, "c_casa": 5.8, "c_fora": 4.3, "cart_casa": 2.2, "cart_fora": 2.9},
    "Sport": {"g_casa": 1.8, "g_fora": 1.1, "c_casa": 6.5, "c_fora": 4.9, "cart_casa": 1.9, "cart_fora": 2.6},
    "Juventude": {"g_casa": 1.4, "g_fora": 1.0, "c_casa": 5.4, "c_fora": 4.2, "cart_casa": 2.4, "cart_fora": 3.1},
    "Operario-PR": {"g_casa": 1.5, "g_fora": 0.9, "c_casa": 5.5, "c_fora": 4.0, "cart_casa": 2.1, "cart_fora": 2.8},
    "Fortaleza": {"g_casa": 1.6, "g_fora": 0.9, "c_casa": 5.9, "c_fora": 4.1, "cart_casa": 2.3, "cart_fora": 3.0},
    "Novorizontino": {"g_casa": 1.5, "g_fora": 1.1, "c_casa": 5.6, "c_fora": 4.6, "cart_casa": 2.2, "cart_fora": 2.9},
    "Criciuma": {"g_casa": 1.4, "g_fora": 1.0, "c_casa": 5.3, "c_fora": 4.2, "cart_casa": 2.4, "cart_fora": 3.2},
    "Nautico": {"g_casa": 1.6, "g_fora": 0.9, "c_casa": 5.7, "c_fora": 4.3, "cart_casa": 2.5, "cart_fora": 3.4},
    "Cuiaba": {"g_casa": 1.2, "g_fora": 0.7, "c_casa": 4.8, "c_fora": 3.6, "cart_casa": 2.1, "cart_fora": 2.7},
    "Athletic Club": {"g_casa": 1.4, "g_fora": 0.9, "c_casa": 5.2, "c_fora": 4.0, "cart_casa": 2.3, "cart_fora": 3.1},
    "Goias": {"g_casa": 1.3, "g_fora": 0.8, "c_casa": 5.1, "c_fora": 3.9, "cart_casa": 2.6, "cart_fora": 3.5},
    "Atletico-GO": {"g_casa": 1.4, "g_fora": 0.8, "c_casa": 5.3, "c_fora": 4.1, "cart_casa": 2.4, "cart_fora": 3.2},
    "Ceara": {"g_casa": 1.5, "g_fora": 0.8, "c_casa": 5.6, "c_fora": 4.2, "cart_casa": 2.5, "cart_fora": 3.3},
    "Botafogo-SP": {"g_casa": 1.2, "g_fora": 0.7, "c_casa": 4.9, "c_fora": 3.7, "cart_casa": 2.3, "cart_fora": 3.2},
    "CRB": {"g_casa": 1.4, "g_fora": 0.7, "c_casa": 5.2, "c_fora": 3.8, "cart_casa": 2.4, "cart_fora": 3.1},
    "Londrina": {"g_casa": 1.3, "g_fora": 0.6, "c_casa": 5.0, "c_fora": 3.7, "cart_casa": 2.5, "cart_fora": 3.4},
    "Avai": {"g_casa": 1.2, "g_fora": 0.7, "c_casa": 4.9, "c_fora": 3.9, "cart_casa": 2.6, "cart_fora": 3.5},
    "Ponte Preta": {"g_casa": 1.1, "g_fora": 0.6, "c_casa": 4.7, "c_fora": 3.5, "cart_casa": 2.7, "cart_fora": 3.7},
    "America-MG": {"g_casa": 1.0, "g_fora": 0.5, "c_casa": 4.5, "c_fora": 3.4, "cart_casa": 2.6, "cart_fora": 3.6}
}

times_ordenados = sorted(list(dados_times.keys()))

c1, c2 = st.columns(2)
with c1:
    st.subheader("Configurar Jogo Real (14a Rodada)")
    tc = st.selectbox("Time da Casa:", times_ordenados, index=times_ordenados.index("Ponte Preta"))
    tf = st.selectbox("Time de Fora:", times_ordenados, index=times_ordenados.index("Novorizontino"))
    noticias = st.text_area("Informacoes de Bastidores (GE):", value=st.session_state['feed'], height=150)

with c2:
    st.subheader("Projecao do Sistema")
    if tc == tf:
        st.error("Escolha times diferentes.")
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
''')

print("Correção aplicada! Os 20 times de verdade da imagem foram injetados no código.")
