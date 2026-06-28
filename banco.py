# ==========================================================
# Predictor Pro 3.0
# banco.py (CORRIGIDO)
# ==========================================================

import os
import streamlit as st
from supabase import create_client, Client
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")


# ==========================================================
# CONEXÃO COM O SUPABASE
# Usa st.secrets se estiver no Streamlit Cloud,
# caso contrário usa o .env local
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
        raise Exception("SUPABASE_URL ou SUPABASE_KEY não encontrados")

    return create_client(url, key)


# ==========================================================
# BUSCA TODOS OS TIMES
# ==========================================================

def carregar_times():
    try:
        supabase = conectar()

        resposta = (
            supabase
            .table("estatisticas_times")
            .select("*")
            .order("time")
            .execute()
        )

        if resposta.data:
            dados = {}
            for row in resposta.data:
                dados[row["time"]] = {
                    "g_casa":    float(row.get("g_casa") or 0),
                    "g_fora":    float(row.get("g_fora") or 0),
                    "c_casa":    float(row.get("c_casa") or 0),
                    "c_fora":    float(row.get("c_fora") or 0),
                    "cart_casa": float(row.get("cart_casa") or 0),
                    "cart_fora": float(row.get("cart_fora") or 0),
                }
            return True, dados

        return False, {}

    except Exception as erro:
        print(f"[ERRO] carregar_times: {erro}")
        return False, {}


# ==========================================================
# ÚLTIMA NOTÍCIA
# ==========================================================

def carregar_noticias():
    try:
        supabase = conectar()

        resposta = (
            supabase
            .table("noticias_bastidores")
            .select("*")
            .order("id", desc=True)
            .limit(1)
            .execute()
        )

        if resposta.data:
            return resposta.data[0]["texto"]

        return "Sem notícias cadastradas."

    except Exception as erro:
        print(f"[ERRO] carregar_noticias: {erro}")
        return "Erro ao consultar notícias."


# ==========================================================
# SALVAR NOTÍCIA
# ==========================================================

def salvar_noticia(texto: str, fonte: str = "manual"):
    try:
        supabase = conectar()

        supabase.table("noticias_bastidores").insert({
            "texto": texto,
            "fonte": fonte,                              # CORRIGIDO: campo fonte adicionado
            "data_atualizacao": datetime.now().isoformat()
        }).execute()

    except Exception as erro:
        print(f"[ERRO] salvar_noticia: {erro}")


# ==========================================================
# ATUALIZAR ESTATÍSTICAS
# ==========================================================

def atualizar_estatisticas(time, gols_casa, gols_fora,
                            cantos_casa, cantos_fora,
                            cartoes_casa, cartoes_fora):
    try:
        supabase = conectar()

        supabase.table("estatisticas_times").update({
            "g_casa":    gols_casa,
            "g_fora":    gols_fora,
            "c_casa":    cantos_casa,
            "c_fora":    cantos_fora,
            "cart_casa": cartoes_casa,
            "cart_fora": cartoes_fora,
        }).eq("time", time).execute()

    except Exception as erro:
        print(f"[ERRO] atualizar_estatisticas ({time}): {erro}")


# ==========================================================
# STATUS DO BANCO
# ==========================================================

def banco_online() -> bool:
    try:
        supabase = conectar()
        supabase.table("estatisticas_times").select("time").limit(1).execute()
        return True
    except Exception:
        return False