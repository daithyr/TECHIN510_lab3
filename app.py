import os
from dataclasses import dataclass, field

import streamlit as st
import psycopg2
from dotenv import load_dotenv

load_dotenv()

con = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = con.cursor()

cur.execute(
    """
    CREATE TABLE IF NOT EXISTS prompts (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        prompt TEXT NOT NULL,
        favorite BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
)

@dataclass
class Prompt:
    title: str = field(default="")
    prompt: str = field(default="")
    id: int = field(default=None)

def prompt_form(prompt=Prompt()):
    with st.form(key="prompt_form", clear_on_submit=True):
        title = st.text_input("Title", value=prompt.title, help="Title is required.")
        prompt_text = st.text_area("Prompt", height=200, value=prompt.prompt, help="Prompt text is required.")
        submitted = st.form_submit_button("Submit")
        if submitted and title and prompt_text:
            return Prompt(title=title, prompt=prompt_text, id=prompt.id)
        elif submitted:
            st.warning("Both title and prompt are required.")

st.title("Promptbase")
st.subheader("A simple app to store and retrieve prompts")

# Form for creating or updating prompts
prompt = prompt_form()
if prompt and prompt.id is None:
    cur.execute("INSERT INTO prompts (title, prompt) VALUES (%s, %s) RETURNING id", (prompt.title, prompt.prompt,))
    prompt_id = cur.fetchone()[0]
    con.commit()
    st.success(f"Prompt {prompt_id} added successfully!")

# Search functionality
search_query = st.text_input("Search for prompts")
sort_order = st.selectbox("Sort by", ["Newest", "Oldest"])

# Displaying prompts based on search and sort order
sort_order_sql = "DESC" if sort_order == "Newest" else "ASC"
cur.execute(f"SELECT id, title, prompt, favorite FROM prompts WHERE title ILIKE %s OR prompt ILIKE %s ORDER BY created_at {sort_order_sql}", (f"%{search_query}%", f"%{search_query}%"))
prompts = cur.fetchall()

# Handling prompt updates or deletions
for p in prompts:
    with st.expander(f"{p[1]}"):
        st.code(p[2])
        if st.checkbox("Favorite", value=p[3], key=f"fav_{p[0]}"):
            cur.execute("UPDATE prompts SET favorite = %s WHERE id = %s", (not p[3], p[0]))
            con.commit()
            st.success(f"Prompt {p[0]} favorite status updated!")
        edit = st.button("Edit", key=f"edit_{p[0]}")
        delete = st.button("Delete", key=f"delete_{p[0]}")
        if delete:
            cur.execute("DELETE FROM prompts WHERE id = %s", (p[0],))
            con.commit()
            st.experimental_rerun()
        if edit:
            prompt_to_edit = Prompt(title=p[1], prompt=p[2], id=p[0])
            prompt_form(prompt_to_edit)
            if prompt and prompt.id is not None:
                cur.execute("UPDATE prompts SET title = %s, prompt = %s WHERE id = %s", (prompt.title, prompt.prompt, prompt.id))
                con.commit()
                st.success(f"Prompt {prompt.id} updated successfully!")
                st.experimental_rerun()
