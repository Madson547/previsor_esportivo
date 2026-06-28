# ==========================================================
# Predictor Pro 3.0
# app.py (CORRIGIDO)
# ==========================================================

import os
from flask import Flask, jsonify, request

app = Flask(__name__)


# ==========================================================
# HOME
# ==========================================================
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "sistema": "Predictor Pro 3.0",
        "mensagem": "Servidor rodando corretamente"
    })


# ==========================================================
# NOTÍCIAS
# ==========================================================
@app.route("/noticias", methods=["GET"])
def noticias():
    try:
        from raspador import supabase

        data = supabase.table("noticias_bastidores") \
            .select("*") \
            .order("data_atualizacao", desc=True) \
            .execute()

        return jsonify(data.data)

    except Exception as e:
        return jsonify({
            "erro": "Falha ao buscar notícias",
            "detalhe": str(e)
        }), 500


# ==========================================================
# JOGOS
# ==========================================================
@app.route("/jogos", methods=["GET"])
def jogos():
    try:
        from raspador import supabase

        data = supabase.table("estatisticas_jogos") \
            .select("*") \
            .execute()

        return jsonify(data.data)

    except Exception as e:
        return jsonify({
            "erro": "Falha ao buscar jogos",
            "detalhe": str(e)
        }), 500


# ==========================================================
# RODAR RASPADOR MANUAL
# ==========================================================
@app.route("/rodar", methods=["GET"])
def rodar():
    try:
        from raspador import atualizar_feed
        atualizar_feed()

        return jsonify({"msg": "Raspador executado com sucesso"})

    except Exception as e:
        return jsonify({
            "erro": "Falha ao executar raspador",
            "detalhe": str(e)
        }), 500


# ==========================================================
# PREVISÃO
# ==========================================================
@app.route("/prever", methods=["GET"])
def prever():
    try:
        from previsao import prever_jogo

        casa = request.args.get("casa", "").strip()
        fora = request.args.get("fora", "").strip()

        if not casa or not fora:
            return jsonify({
                "erro": "Parâmetros obrigatórios",
                "uso": "/prever?casa=FLAMENGO&fora=PALMEIRAS"
            }), 400

        resultado = prever_jogo(casa, fora)

        return jsonify({
            "casa": casa,
            "fora": fora,
            "resultado": resultado
        })

    except Exception as e:
        return jsonify({
            "erro": "Falha na previsão",
            "detalhe": str(e)
        }), 500


# ==========================================================
# MAIN
# ==========================================================
if __name__ == "__main__":
    # Em produção, use: gunicorn app:app
    # Para liberar acesso externo, mude host para "0.0.0.0"
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    print("====================================")
    print(" Predictor Pro 3.0")
    print(f" Modo debug: {debug_mode}")
    print(" Servidor iniciando em http://127.0.0.1:5000")
    print("====================================")

    app.run(
        debug=debug_mode,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000))
    )