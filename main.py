import streamlit as st
from datetime import datetime
import google as genai
import json
import os

@st.cache_data(ttl=3600)
def analyze_with_gemini(text: str) -> str:
    """
    Usa a biblioteca google.genai com o modelo "gemini-2.0-flash" para analisar
    a frase em italiano, com cache para melhor performance.
    """

    gemini_key = st.secrets["google"]["gemini_key"]
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
    """
    Salva o histórico de análises em um arquivo JSON.
    """
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
        page_icon="🇮🇹",
        layout="wide"
    )

    st.markdown("""
        <style>
        .stTextArea textarea {
            font-size: 16px;
        }
        .main .block-container {
            padding-top: 2rem;
        }
        .stAlert {
            padding: 1rem;
            margin: 1rem 0;
        }
        .resource-card {
            padding: 1rem;
            border-radius: 0.5rem;
            background-color: #f0f2f6;
            margin-bottom: 0.5rem;
        }
        /* Estilo fixo para o footer independente do tema */
        .footer {
            position: fixed;
            bottom: 0;
            right: 0;
            padding: 10px;
            background-color: #1B1B1B !important;  /* Cor de fundo do Claude */
            border-top-left-radius: 10px;
            text-align: right;
            font-size: 0.8em;
            color: #FFFFFF !important;  /* Texto branco */
            z-index: 1000;
        }
        /* Garante que o link no footer também seja branco */
        .footer a {
            color: #FFFFFF !important;
            text-decoration: none;
        }
        .footer a:hover {
            text-decoration: underline;
        }
        /* Força o tema escuro para estes elementos mesmo em modo claro */
        [data-testid="stSidebar"] {
            background-color: #1B1B1B !important;
            color: #FFFFFF !important;
        }
        </style>
    """, unsafe_allow_html=True)

    if 'history' not in st.session_state:
        st.session_state.history = []

    # Sidebar com recursos úteis e histórico
    with st.sidebar:
        st.title("📚 Risorse Utili")

        # Dicionários
        st.subheader("📖 Dizionari")
        with st.expander("Dizionari Online", expanded=True):
            st.markdown("""
            - [Treccani](https://www.treccani.it/vocabolario/) - Dizionario ufficiale
            - [WordReference](https://www.wordreference.com/it/) - Dizionario multilingue
            - [Grande Dizionario Hoepli](https://dizionari.repubblica.it/italiano.html) - Dizionario completo
            """)

        # Conjugação
        st.subheader("🔄 Coniugazione")
        with st.expander("Strumenti di Coniugazione", expanded=True):
            st.markdown("""
            - [Coniugazione.it](https://www.coniugazione.it/) - Tutti i verbi italiani
            - [Reverso Coniugazione](https://conjugator.reverso.net/conjugation-italian.html) - Coniugatore con esempi
            """)

        # Recursos de aprendizado
        st.subheader("📝 Risorse di Apprendimento")
        with st.expander("Strumenti di Studio", expanded=True):
            st.markdown("""
            - [TV-Series & Film](https://www.raiplay.it/) - RaiPlay
            - [Podcast in Italiano](https://www.almaedizioni.it/it/almatv/) - AlmaTV
            - [Giornali Italiani](https://www.quotidiano.net/) - Notizie in italiano
            - [Esercizi Online](https://www.italienisch-lernen-online.de/) - Grammatica ed esercizi
            """)

        st.markdown("---")

        # Histórico de análises
        st.subheader("📚 Cronologia")
        if st.session_state.history:
            for i, item in enumerate(st.session_state.history):
                with st.expander(f"Analisi {i+1}: {item['phrase'][:30]}..."):
                    st.write(f"Data: {item['timestamp']}")
                    st.write(f"Frase: {item['phrase']}")
                    if st.button(f"Ricarica analisi {i+1}"):
                        st.session_state.phrase = item['phrase']
                        st.experimental_rerun()

    # Interface principal
    col1, col2 = st.columns([2, 3])

    with col1:
        st.title("🇮🇹 Impara l'Italiano")
        st.markdown("### Analisi e Note")

        phrase = st.text_area(
            "Scrivi una frase in italiano:",
            placeholder="Inserisci la tua frase qui...",
            height=100,
            key="phrase" if "phrase" in st.session_state else None
        )
        st.caption(f"Caratteri: {len(phrase)}/500")

        col1_1, col1_2 = st.columns(2)
        with col1_1:
            analyze_button = st.button("Analizza 🔍", use_container_width=True)
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
            else:
                with st.spinner("Analizzando..."):
                    analysis = analyze_with_gemini(phrase)
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
            notes = st.text_area(
                "Scrivi le tue note:",
                placeholder="Inserisci le tue note qui...",
                height=150
            )
            st.caption(f"Caratteri: {len(notes)}/1000")

            col2_1, col2_2 = st.columns(2)
            with col2_1:
                if st.button("Scarica Nota 📥", use_container_width=True):
                    content = (
                        f"🇮🇹 NOTA DI STUDIO ITALIANO\n"
                        f"=========================\n\n"
                        f"FRASE ANALIZZATA:\n{st.session_state.phrase}\n\n"
                        f"ANALISI DETTAGLIATA:\n{st.session_state.analysis_result}\n\n"
                        f"NOTE PERSONALI:\n{notes}\n\n"
                        f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
                    )

                    save_history(st.session_state.phrase, st.session_state.analysis_result, notes)

                    st.download_button(
                        label="Conferma Download 📄",
                        data=content,
                        file_name=f"nota_italiano_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )

            with col2_2:
                if st.button("Salva nelle note 💾", use_container_width=True):
                    save_history(st.session_state.phrase, st.session_state.analysis_result, notes)
                    st.success("✅ Nota salvata con successo!")

    # Footer com créditos
    st.markdown("""
        <div class="footer">
            Sviluppato da Paulo Augusto Giavoni
            <br/>
            <a href="https://www.linkedin.com/in/paulogiavoni/" target="_blank">LinkedIn</a>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
