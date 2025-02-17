import streamlit as st
from datetime import datetime
from google import genai
import json
import os

@st.cache_data(ttl=3600)
def analyze_with_gemini(text: str, gemini_key: str) -> str:
    client = genai.Client(api_key=gemini_key)

    prompt = (
        f"Analizza la seguente frase in italiano: \"{text}\"\n\n"
        "Fornisci un'analisi dettagliata della frase, includendo:\n"
        "1. Analisi grammaticale (verbi, soggetto, complementi)\n"
        "2. Tre frasi simili per esercitarsi\n"
        "3. Suggerimenti per migliorare la frase\n\n"
        "Infine, identifica il verbo principale della frase e fornisci una tabella in formato Markdown "
        "con due colonne: 'Tempo' e 'Coniugazione', contenente le coniugazioni del verbo per i tempi: "
        "Presente, Passato e Futuro."
    )
    try:
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        return response.text
    except Exception as e:
        st.error(f"Errore durante l'analisi: {str(e)}")
        return None

def save_history(phrase: str, analysis: str, notes: str):
    history_file = "analysis_history.json"
    history = []

    if os.path.exists(history_file):
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)

    history.append({
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "phrase": phrase,
        "analysis": analysis,
        "notes": notes
    })

    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def main():
    st.set_page_config(
        page_title="Impara l'Italiano",
        page_icon="\U0001F1EE\U0001F1F9",
        layout="wide"
    )

    st.sidebar.title("Configurações")
    gemini_key = st.sidebar.text_input("Insira sua chave do Gemini:", value="", type="password")

    if "phrase" not in st.session_state:
        st.session_state.phrase = ""
    if "history" not in st.session_state:
        st.session_state.history = []

    col1, col2 = st.columns([2, 3])

    with col1:
        st.title("\U0001F1EE\U0001F1F9 Impara l'Italiano")
        st.markdown("### Analisi e Note")

        phrase = st.text_area(
            "Scrivi una frase in italiano:",
            placeholder="Inserisci la tua frase qui...",
            height=100,
            key="phrase"
        )
        st.caption(f"Caratteri: {len(phrase)}/500")

        col1_1, col1_2 = st.columns(2)
        with col1_1:
            analyze_button = st.button("Analizza \U0001F50D", use_container_width=True)
        with col1_2:
            clear_button = st.button("Pulisci ❌", use_container_width=True)

        if clear_button:
            st.session_state.phrase = ""
            st.session_state.pop('analysis_result', None)
            st.experimental_rerun()

    with col2:
        if analyze_button:
            if len(phrase.strip()) == 0:
                st.error("⚠️ Per favore, inserisci una frase.")
            elif len(phrase) > 500:
                st.error("⚠️ La frase è troppo lunga. Massimo 500 caratteri.")
            elif not gemini_key.strip():
                st.error("⚠️ Per favore, insira a chave do Gemini na barra laterale.")
            else:
                with st.spinner("Analizzando..."):
                    analysis = analyze_with_gemini(phrase, gemini_key)
                    if analysis:
                        st.session_state.analysis_result = analysis
                        st.session_state.phrase = phrase

                        if phrase not in [h['phrase'] for h in st.session_state.history]:
                            st.session_state.history.append({
                                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'phrase': phrase
                            })

                        st.success("✅ Analisi completata!")

        if "analysis_result" in st.session_state:
            st.markdown("### 📝 Risultati dell'analisi")
            st.markdown(st.session_state.analysis_result)

            st.markdown("### 📒 Le tue note")
            notes = st.text_area("Scrivi le tue note:", placeholder="Inserisci le tue note qui...", height=150)
            st.caption(f"Caratteri: {len(notes)}/1000")

            col2_1, col2_2 = st.columns(2)
            with col2_1:
                if st.button("Scarica Nota 📥", use_container_width=True):
                    content = (
                        f"\U0001F1EE\U0001F1F9 NOTA DI STUDIO ITALIANO\n"
                        f"=========================\n\n"
                        f"FRASE ANALIZZATA:\n{st.session_state.phrase}\n\n"
                        f"ANALISI DETTAGLIATA:\n{st.session_state.analysis_result}\n\n"
                        f"NOTE PERSONALI:\n{notes}\n\n"
                        f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
                    )
                    save_history(st.session_state.phrase, st.session_state.analysis_result, notes)
                    st.download_button("Conferma Download 📄", data=content, file_name=f"nota_italiano_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", mime="text/plain", use_container_width=True)

            with col2_2:
                if st.button("Salva nelle note 💾", use_container_width=True):
                    save_history(st.session_state.phrase, st.session_state.analysis_result, notes)
                    st.success("✅ Nota salvata con successo!")

if __name__ == "__main__":
    main()
