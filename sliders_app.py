import streamlit as st
import ollama
import sqlite3, uuid, datetime

st.set_page_config(page_title="Hormone Lab v3.3", layout="wide")
st.title("Synthetic Cognition Lab — 10-Step")

# --- 10-step sliders (0.0 to 0.9) ---
N = st.slider("Neuroticism", 0.0, 0.9, 0.3, 0.1)
E = st.slider("Extraversion", 0.0, 0.9, 0.7, 0.1)
O = st.slider("Openness", 0.0, 0.9, 0.9, 0.1)
A = st.slider("Agreeableness", 0.0, 0.9, 0.7, 0.1)
C = st.slider("Conscientiousness", 0.0, 0.9, 0.7, 0.1)

zodiac_names = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
zodiac = st.selectbox("Zodiac Archetype", zodiac_names, index=10)

trauma = st.select_slider("Trauma / Vigilance", options=[0.0,0.25,0.5,0.75,1.0], value=0.25)

# --- hormone math (same as your v3) ---
Cort = 0.6*N + 0.4*(1-C) + 0.2*trauma
Dopa = 0.5*O + 0.3*E + 0.2*(1-trauma)
Oxy  = 0.6*A + 0.3*(1-N) - 0.2*trauma
Adr  = 0.5*(1-A) + 0.4*N + 0.3*trauma

st.markdown(f"**Live Hormones:** Cortisol `{Cort:.2f}` | Dopamine `{Dopa:.2f}` | Oxytocin `{Oxy:.2f}` | Adrenaline `{Adr:.2f}`")

# --- prompt builder ---
base_prompt = f"""You are an author with Big Five N{N:.1f} E{E:.1f} O{O:.1f} A{A:.1f} C{C:.1f}, zodiac {zodiac}, trauma {trauma}.
Internal state: Cortisol {Cort:.2f}, Dopamine {Dopa:.2f}, Oxytocin {Oxy:.2f}, Adrenaline {Adr:.2f}.
Write in a consistent voice that reflects this profile. Do not mention hormones or scores.
Story prompt: An Earth expedition lands on Mars but unexpectedly encounters a civilization.
Write 300-500 words."""

if st.button("Show Prompt"):
    st.code(base_prompt)

if st.button("Generate Story"):
    with st.spinner("Generating with Ollama gemma3:27b..."):
        resp = ollama.chat(
            model="gemma3:27b-it-qat",
            messages=[{"role":"user","content":base_prompt}],
            options={"temperature":0.9,"top_p":0.95,"num_predict":600}
        )
        story = resp["message"]["content"]
    
    st.subheader("Story Output")
    st.write(story)

    # --- save to DB ---
    conn = sqlite3.connect("random_author.db")
    conn.execute("""CREATE TABLE IF NOT EXISTS Limbic_State
        (id TEXT, N REAL, E REAL, O REAL, A REAL, C REAL, zodiac TEXT, trauma REAL, ts TEXT)""")
    aid = f"N{int(N*10)}_E{int(E*10)}_O{int(O*10)}_A{int(A*10)}_C{int(C*10)}_{zodiac[:3].upper()}_T{int(trauma*4)}"
    conn.execute("INSERT INTO Limbic_State VALUES (?,?,?,?,?,?,?,?,?)",
        (aid,N,E,O,A,C,zodiac,trauma,datetime.datetime.now().isoformat()))
    conn.commit()
    st.success(f"Saved as {aid}")