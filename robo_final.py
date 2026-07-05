# ==========================================================
# Predictor Pro 3.0 — Série A
# robo_final.py — job local para manter o Supabase atualizado
#
# Uso: rodar manualmente (python robo_final.py) ou agendar via
# Windows Task Scheduler pra manter tabela, rodada, estatísticas
# e notícias sempre frescas, sem depender de abrir o Streamlit.
# ==========================================================

import sys
import traceback
from datetime import datetime

from raspador import atualizar_dados_api, atualizar_feed


def log(msg: str):
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{agora}] {msg}")


def main():
    inicio = datetime.now()
    log("=== ROBÔ Predictor Pro 3.0 (Série A) — iniciando ===")

    # 1. Tabela + rodada + estatísticas (finalizações, cartões, escanteios)
    try:
        log("Atualizando tabela, rodada e estatísticas via API...")
        atualizar_dados_api()
        log("OK — dados da API atualizados.")
    except Exception as e:
        log(f"ERRO em atualizar_dados_api: {e}")
        traceback.print_exc()

    # 2. Notícias (ge.globo.com)
    try:
        log("Coletando notícias...")
        resultado_feed = atualizar_feed()
        log(f"OK — {resultado_feed['coletadas']} coletadas, "
            f"{resultado_feed['salvas']} salvas.")
    except Exception as e:
        log(f"ERRO em atualizar_feed: {e}")
        traceback.print_exc()

    duracao = (datetime.now() - inicio).total_seconds()
    log(f"=== ROBÔ finalizado em {duracao:.1f}s ===")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Garante saída não-zero pro Task Scheduler sinalizar falha
        traceback.print_exc()
        sys.exit(1)
