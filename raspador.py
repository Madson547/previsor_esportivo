# ==========================================================
# Predictor Pro 3.0
# raspador.py (CORRIGIDO - endpoint rodada ajustado)
# ==========================================================

import os
import time
import requests
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client
from bs4 import BeautifulSoup

load_dotenv(dotenv_path=".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("ERRO: SUPABASE_URL ou SUPABASE_KEY não encontrados no .env")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

DADOS_FUTEBOL_KEY = os.getenv("DADOS_FUTEBOL_KEY")
DADOS_FUTEBOL_URL = "https://api.dadosfutebol.com.br/v1"

def _headers_api():
    return {
        "Authorization": f"Bearer {DADOS_FUTEBOL_KEY}",
        "Accept": "application/json"
    }

def _get(endpoint: str) -> dict:
    try:
        resp = requests.get(
            f"{DADOS_FUTEBOL_URL}{endpoint}",
            headers=_headers_api(),
            timeout=10
        )
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        print(f"[ERRO API] {endpoint}: {e}")
        return {}

def buscar_id_serie_b() -> int:
    data = _get("/campeonatos")
    for c in data.get("data", []):
        nome = c.get("nome", "").lower()
        if "série b" in nome or "serie b" in nome:
            print(f"[API] Série B encontrada: ID={c['id']} — {c['nome']}")
            return c["id"]
    return None

def buscar_tabela_serie_b(campeonato_id: int) -> list:
    data = _get(f"/campeonatos/{campeonato_id}/tabela")
    classificacao = data.get("data", {}).get("classificacao", [])
    tabela = []
    for entry in classificacao:
        time_info = entry.get("time", {})
        tabela.append({
            "posicao":     entry.get("posicao"),
            "time":        time_info.get("nome", ""),
            "sigla":       time_info.get("sigla", ""),
            "pontos":      entry.get("pontos", 0),
            "jogos":       entry.get("jogos", 0),
            "vitorias":    entry.get("vitorias", 0),
            "empates":     entry.get("empates", 0),
            "derrotas":    entry.get("derrotas", 0),
            "gols_pro":    entry.get("gols_pro", 0),
            "gols_contra": entry.get("gols_contra", 0),
            "saldo":       entry.get("saldo_gols", 0),
        })
    print(f"[API] Tabela obtida: {len(tabela)} times")
    return tabela

def buscar_rodada_atual(campeonato_id: int) -> dict:
    """
    Busca partidas do campeonato com status agendada/andamento/encerrada hoje.
    Tenta /partidas com filtro de data de hoje.
    """
    from datetime import date
    hoje = date.today().isoformat()

    # Tenta buscar partidas de hoje
    data = _get(f"/campeonatos/{campeonato_id}/partidas?data={hoje}")
    partidas_raw = data.get("data", [])

    # Se não vier nada hoje, busca as próximas partidas
    if not partidas_raw:
        print("[API] Sem jogos hoje, buscando proximas partidas...")
        data = _get(f"/campeonatos/{campeonato_id}/partidas?status=agendada")
        partidas_raw = data.get("data", [])[:10]

    numero = "?"
    partidas = []
    for p in partidas_raw:
        mandante  = p.get("mandante", {})
        visitante = p.get("visitante", {})
        placar    = p.get("placar", {})
        numero    = p.get("rodada", numero)

        partidas.append({
            "id":             p.get("id"),
            "rodada":         p.get("rodada", "?"),
            "status":         p.get("status", "agendada"),
            "data":           p.get("data_realizacao", ""),
            "hora":           p.get("hora_realizacao", ""),
            "estadio":        p.get("estadio", {}).get("nome", "") if isinstance(p.get("estadio"), dict) else "",
            "mandante":       mandante.get("nome", "") if isinstance(mandante, dict) else str(mandante),
            "visitante":      visitante.get("nome", "") if isinstance(visitante, dict) else str(visitante),
            "gols_mandante":  placar.get("mandante") if isinstance(placar, dict) else None,
            "gols_visitante": placar.get("visitante") if isinstance(placar, dict) else None,
        })

    print(f"[API] Rodada {numero}: {len(partidas)} partidas encontradas")
    return {"numero": numero, "partidas": partidas}

def salvar_tabela(tabela: list):
    if not tabela:
        return
    try:
        supabase.table("tabela_serie_b").delete().neq("posicao", 0).execute()
    except Exception:
        pass
    for row in tabela:
        row["data_atualizacao"] = datetime.now().isoformat()
        supabase.table("tabela_serie_b").insert(row).execute()
    print(f"[TABELA] {len(tabela)} times salvos.")

def salvar_rodada(rodada: dict):
    partidas = rodada.get("partidas", [])
    if not partidas:
        return
    try:
        supabase.table("rodada_atual").delete().neq("id", 0).execute()
    except Exception:
        pass
    for p in partidas:
        p["data_atualizacao"] = datetime.now().isoformat()
        supabase.table("rodada_atual").insert(p).execute()
    print(f"[RODADA] {len(partidas)} partidas salvas.")

def salvar_noticia(texto: str, fonte: str = "sistema"):
    try:
        supabase.table("noticias_bastidores").insert({
            "texto": texto,
            "fonte": fonte,
            "data_atualizacao": datetime.now().isoformat()
        }).execute()
    except Exception as e:
        print(f"[ERRO] salvar_noticia: {e}")

def coletar_ge() -> list:
    noticias = []
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        resp = requests.get("https://ge.globo.com/futebol/", headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup.select("a.feed-post-link, h2.post__title a, .bastian-feed-item a"):
            texto = tag.get_text(strip=True)
            if texto and len(texto) > 10:
                noticias.append(texto)
        print(f"[GE] {len(noticias)} notícias")
    except Exception as e:
        print(f"[ERRO] coletar_ge: {e}")
    return noticias

def coletar_uol() -> list:
    noticias = []
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        resp = requests.get("https://www.uol.com.br/esporte/futebol/", headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup.select("h3 a, h2 a, .title a"):
            texto = tag.get_text(strip=True)
            if texto and len(texto) > 10:
                noticias.append(texto)
        print(f"[UOL] {len(noticias)} notícias")
    except Exception as e:
        print(f"[ERRO] coletar_uol: {e}")
    return noticias

def atualizar_feed():
    print("[FEED] Iniciando noticias...")
    total = 0
    for nome, fn in [("GE", coletar_ge), ("UOL", coletar_uol)]:
        try:
            for texto in fn():
                salvar_noticia(texto, fonte=nome)
                total += 1
            time.sleep(1)
        except Exception as e:
            print(f"[ERRO] {nome}: {e}")
    print(f"[FEED] {total} noticias salvas.")

def atualizar_dados_api():
    if not DADOS_FUTEBOL_KEY:
        print("[API] DADOS_FUTEBOL_KEY não encontrada no .env")
        return

    print("[API] Iniciando atualização...")

    campeonato_id = buscar_id_serie_b()
    if not campeonato_id:
        print("[API] ID da Série B não encontrado.")
        return

    tabela = buscar_tabela_serie_b(campeonato_id)
    if tabela:
        salvar_tabela(tabela)

    time.sleep(1)

    rodada = buscar_rodada_atual(campeonato_id)
    if rodada.get("partidas"):
        salvar_rodada(rodada)

    print("[API] Concluído!")