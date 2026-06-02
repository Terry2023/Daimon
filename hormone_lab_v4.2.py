import streamlit as st
import sqlite3
import datetime
import os
import ollama

DB_PATH = "hormone_lab.db"
STORIES_DIR = "stories"
os.makedirs(STORIES_DIR, exist_ok=True)

# --- DB setup ---
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.execute("""CREATE TABLE IF NOT EXISTS Presets (
    name TEXT PRIMARY KEY,
    N REAL, E REAL, O REAL, A REAL, C REAL,
    zodiac TEXT,
    trauma REAL
)""")
conn.commit()

# --- defaults ---
defaults = {"N":0.25,"E":0.45,"O":0.65,"A":0.50,"C":0.75,"trauma":0.35,"zodiac":"Capricorn","premise":"A widow takes over her late husband's outlaw gang, seeking to prove she is more ruthless than any man."}
for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k]=v

# --- sidebar presets ---
st.sidebar.title("Presets")
preset_names = [r[0] for r in conn.execute("SELECT name FROM Presets ORDER BY name").fetchall()]
load_name = st.sidebar.selectbox("Load preset", [""]+preset_names)
if st.sidebar.button("Load") and load_name:
    r = conn.execute("SELECT N,E,O,A,C,zodiac,trauma FROM Presets WHERE name=?", (load_name,)).fetchone()
    if r:
        st.session_state.update(
            N=float(min(1.0,max(0.0,r[0]))),
            E=float(min(1.0,max(0.0,r[1]))),
            O=float(min(1.0,max(0.0,r[2]))),
            A=float(min(1.0,max(0.0,r[3]))),
            C=float(min(1.0,max(0.0,r[4]))),
            zodiac=r[5],
            trauma=float(min(1.0,max(0.0,r[6])))
        )
        st.rerun()

save_name = st.sidebar.text_input("Save current as")
if st.sidebar.button("Save Preset") and save_name:
    conn.execute("REPLACE INTO Presets VALUES (?,?,?,?,?,?,?,?)",
        (save_name, st.session_state.N, st.session_state.E, st.session_state.O,
         st.session_state.A, st.session_state.C, st.session_state.zodiac, st.session_state.trauma))
    conn.commit()
    st.sidebar.success(f"Saved {save_name}")

# pre-seed western presets once
for name, vals in {
    "western_capricorn": (0.20,0.40,0.60,0.40,0.80,"Capricorn",0.35),
    "western_scorpio": (0.30,0.40,0.75,0.35,0.70,"Scorpio",0.45),
    "western_taurus": (0.25,0.45,0.50,0.60,0.80,"Taurus",0.30),
    "western_base": (0.25,0.45,0.65,0.50,0.75,"Capricorn",0.35)
}.items():
    if not conn.execute("SELECT 1 FROM Presets WHERE name=?", (name,)).fetchone():
        conn.execute("REPLACE INTO Presets VALUES (?,?,?,?,?,?,?,?)", (name,*vals))
        conn.commit()

st.title("Hormone Lab v4.2")

# --- sliders ---
st.subheader("Big Five + Trauma")
N = st.slider("Neuroticism", 0.0, 1.0, st.session_state.N, 0.05, key="N")
E = st.slider("Extraversion", 0.0, 1.0, st.session_state.E, 0.05, key="E")
O = st.slider("Openness", 0.0, 1.0, st.session_state.O, 0.05, key="O")
A = st.slider("Agreeableness", 0.0, 1.0, st.session_state.A, 0.05, key="A")
C = st.slider("Conscientiousness", 0.0, 1.0, st.session_state.C, 0.05, key="C")
trauma = st.slider("Trauma / Vigilance", 0.0, 1.0, st.session_state.trauma, 0.05, key="trauma")

zodiac = st.selectbox("Zodiac", ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"],
                      index=["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"].index(st.session_state.zodiac),
                      key="zodiac")

# --- premise ---
st.subheader("Story Premise")
premise = st.text_area("Paste your premise here:", value=st.session_state.premise, height=120, key="premise_input")
st.session_state.premise = premise

# --- generate ---
model_name = "gemma3:27b-it-qat"
if st.button("Generate", type="primary"):
    tone_words = f"N={N:.2f} E={E:.2f} O={O:.2f} A={A:.2f} C={C:.2f} trauma={trauma:.2f}"
    system_prompt = (
        f"You are a gritty western fiction author. Voice parameters: {tone_words}. "
        f"Zodiac influence: {zodiac}. Write in tight, visual prose. No exposition dumps. "
        f"Show don't tell. Keep sentences short."
    )
    user_prompt = f"Premise: {premise}\n\nWrite the opening 300-400 words."

    with st.spinner(f"Generating with {model_name}..."):
        try:
            resp = ollama.generate(model=model_name, system=system_prompt, prompt=user_prompt, options={"num_predict": 4096, "temperature": 0.8})
            text = resp["response"]
            st.session_state.last_output = text
            # auto-save
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            fname = os.path.join(STORIES_DIR, f"story_{ts}.txt")
            with open(fname,"w",encoding="utf-8") as f:
                f.write(f"Model: {model_name}\nPremise: {premise}\nVoice: {tone_words} {zodiac}\n\n{text}")
            st.success(f"Saved to {fname}")
        except Exception as e:
            st.error(f"Generation failed: {e}")
            text = ""

if "last_output" in st.session_state:
    st.subheader("Output")
    st.write(st.session_state.last_output)
