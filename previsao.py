# ==========================================================
# Predictor Pro 3.0
# previsao.py (CORRIGIDO)
# ==========================================================

# CORRIGIDO: reutiliza a conexão do raspador, sem duplicar cliente Supabase
from raspador import supabase


# ==========================================================
# BUSCAR DADOS
# ==========================================================

def buscar_jogos() -> list:
    """Retorna todos os jogos cadastrados no Supabase."""
    try:
        return supabase.table("estatisticas_jogos").select("*").execute().data
    except Exception as e:
        print(f"[ERRO] buscar_jogos: {e}")
        return []


# ==========================================================
# FORÇA DO TIME
# ==========================================================

def calcular_forca(time: str) -> float:
    """
    Calcula um índice de força do time com base nas estatísticas
    armazenadas: xG, finalizações e posse de bola.
    Retorna 0.0 se não houver dados.
    """
    try:
        jogos = supabase.table("estatisticas_jogos") \
            .select("*") \
            .eq("time", time) \
            .execute().data
    except Exception as e:
        print(f"[ERRO] calcular_forca ({time}): {e}")
        return 0.0

    if not jogos:
        return 0.0

    total_xg = 0.0
    total_finalizacoes = 0.0
    total_posse = 0.0
    count = 0

    for j in jogos:
        stats = j.get("estatisticas") or {}

        # CORRIGIDO: garante que None não causa erro de soma
        xg = stats.get("xg") or 0
        fin = stats.get("finalizacoes") or 0
        posse = stats.get("posse") or 0

        total_xg += float(xg)
        total_finalizacoes += float(fin)
        total_posse += float(posse)
        count += 1

    if count == 0:
        return 0.0

    forca = (
        (total_xg / count) * 0.5 +
        (total_finalizacoes / count) * 0.3 +
        (total_posse / count) * 0.2
    )

    return round(forca, 4)


# ==========================================================
# PREVISÃO
# ==========================================================

def prever_jogo(time_casa: str, time_fora: str) -> dict:
    """
    Compara a força dos dois times e retorna uma previsão.
    """
    forca_casa = calcular_forca(time_casa)
    forca_fora = calcular_forca(time_fora)
    diff = forca_casa - forca_fora

    # CORRIGIDO: confiança arredondada para exibição limpa
    if diff > 1.5:
        return {
            "vencedor": time_casa,
            "probabilidade": "alta",
            "confianca": round(min(95.0, 50 + diff * 10), 1),
            "forca_casa": forca_casa,
            "forca_fora": forca_fora
        }

    if diff < -1.5:
        return {
            "vencedor": time_fora,
            "probabilidade": "alta",
            "confianca": round(min(95.0, 50 + abs(diff) * 10), 1),
            "forca_casa": forca_casa,
            "forca_fora": forca_fora
        }

    return {
        "vencedor": "empate",
        "probabilidade": "media",
        "confianca": 55.0,
        "forca_casa": forca_casa,
        "forca_fora": forca_fora
    }


# ==========================================================
# TESTE LOCAL
# ==========================================================

if __name__ == "__main__":
    import json
    resultado = prever_jogo("Flamengo", "Palmeiras")
    print(json.dumps(resultado, indent=2, ensure_ascii=False))