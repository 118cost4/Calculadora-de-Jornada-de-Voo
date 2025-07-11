import streamlit as st
from datetime import datetime, timedelta, time
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

st.set_page_config(page_title="Calculadora de Jornada de Voo", page_icon="✈️")
st.title("✈️ Calculadora de Limite de Jornada de Voo")

# 🚀 1. Seleção do tipo de aeronave
aeronave = st.selectbox("✈️ Tipo de Aeronave", ["C-105 Amazonas", "C-98 Caravan"])

# 2. Entradas principais
data_inicio = st.date_input("📅 Data de Início")
hora_inicio = st.time_input("⏰ Hora de Início")
tipo_jornada = st.radio("📋 Tipo de Jornada", ["Jornada Contínua", "Jornada Máxima"])

# 3. Define tipos de tripulação por aeronave
if aeronave == "C-105 Amazonas":
    opcoes_tripulacao = ["Simples", "Composta", "Revezamento"]
else:  # C-98 Caravan
    opcoes_tripulacao = ["Simples", "Composta"]

tipo_tripulacao = st.selectbox("👨‍✈️ Tipo de Tripulação", opcoes_tripulacao)

# 4. Limites de jornada por aeronave
limites_jornada = {
    "C-105 Amazonas": {
        "Jornada Contínua": {
            "Simples": 14,
            "Composta": 16,
            "Revezamento": 19
        },
        "Jornada Máxima": {
            "Simples": 16,
            "Composta": 18,
            "Revezamento": 22
        }
    },
    "C-98 Caravan": {
        "Jornada Contínua": {
            "Simples": 12,
            "Composta": 14
        },
        "Jornada Máxima": {
            "Simples": 14,
            "Composta": 14
        }
    }
}

# 🔁 Penalidade entre 02:00 e 10:00 de múltiplos dias
def calcular_penalidade(inicio: datetime, duracao: timedelta) -> timedelta:
    fim = inicio + duracao
    penalidade_total = timedelta(0)

    # Começa no dia anterior ao início, termina no dia do fim da jornada
    data_atual = (inicio - timedelta(days=1)).date()
    data_final = fim.date()

    while data_atual <= data_final:
        penal_inicio = datetime.combine(data_atual, time(2, 0))
        penal_fim = datetime.combine(data_atual, time(10, 0))

        # Interseção com jornada
        inter_inicio = max(inicio, penal_inicio)
        inter_fim = min(fim, penal_fim)

        if inter_inicio < inter_fim:
            tempo_penalizado = inter_fim - inter_inicio
            horas_completas = int(tempo_penalizado.total_seconds() // 3600)
            penalidade_total += timedelta(minutes=30 * horas_completas)

        data_atual += timedelta(days=1)

    return penalidade_total


# 🔁 Versão otimizada: convergência ou máximo de 10 iterações
def calcular_jornada_com_penalidade(inicio: datetime, jornada_base: timedelta) -> (timedelta, timedelta):
    jornada_final = jornada_base
    for _ in range(10):
        penalidade = calcular_penalidade(inicio, jornada_final)
        nova_jornada = jornada_base - penalidade
        if abs((nova_jornada - jornada_final).total_seconds()) < 60:  # diferença menor que 1 min
            break
        jornada_final = nova_jornada
    return jornada_final, penalidade

# ▶️ Botão de cálculo
if st.button("Calcular Limite de Jornada"):
    inicio = datetime.combine(data_inicio, hora_inicio)

    try:
        jornada_base_horas = limites_jornada[aeronave][tipo_jornada][tipo_tripulacao]
    except KeyError:
        st.error("⚠️ Parâmetro inválido para essa aeronave. Verifique a tripulação.")
        st.stop()

    jornada_base = timedelta(hours=jornada_base_horas)
    jornada_final, penalidade = calcular_jornada_com_penalidade(inicio, jornada_base)
    fim_base = inicio + jornada_base
    fim_final = inicio + jornada_final

    # 📋 Resultados
    st.success(f"🕒 Início da jornada: {inicio.strftime('%d/%m/%Y %H:%M')}")
    st.success(f"⏳ Limite da jornada (com penalidade): {fim_final.strftime('%d/%m/%Y %H:%M')}")
    st.info(f"Tempo base permitido: {jornada_base_horas}h")
    st.warning(f"Penalidade aplicada: -{penalidade}")
    st.info(f"Tempo final permitido: {jornada_final}")

    # 📊 Linha do tempo
    fig, ax = plt.subplots(figsize=(10, 1.5))
    ax.hlines(1, inicio, fim_base, colors="lightgray", linewidth=10, label="Jornada Base")
    ax.hlines(1, inicio, fim_final, colors="tab:red", linewidth=10, label="Jornada Final")

    data_plot = (inicio - timedelta(days=1)).date()
    while data_plot <= fim_base.date():
        penal_start = datetime.combine(data_plot, time(2, 0))
        penal_end = datetime.combine(data_plot, time(10, 0))
        ax.axvspan(penal_start, penal_end, color='orange', alpha=0.3)
        data_plot += timedelta(days=1)

    ax.plot(inicio, 1, "go", label="Início")
    ax.plot(fim_base, 1, "bo", label="Fim Base")
    ax.plot(fim_final, 1, "ro", label="Fim Ajustado")

    ax.set_yticks([])
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m %H:%M'))
    ax.set_xlim(inicio - timedelta(hours=2), fim_base + timedelta(hours=2))
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.5), ncol=4)
    ax.set_title("🧭 Linha do Tempo da Jornada de Voo", fontsize=12)
    st.pyplot(fig)

st.caption("🧪 Esta é uma versão de testes - Cap Av José Roberto Pedraza da Costa - 1°/15° GAv")
