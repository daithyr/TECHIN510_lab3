import os
from dataclasses import dataclass, field
import streamlit as st
import psycopg2

# Retrieve the Supabase connection URL from Streamlit secrets
supabase_url = st.secrets["DATABASE_URL"]

con = psycopg2.connect(supabase_url)
cur = con.cursor()


cur.execute('''
    CREATE TABLE IF NOT EXISTS prompts (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        prompt TEXT NOT NULL,
        favorite BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
con.commit()

@dataclass
class Prompt:
    title: str = field(default="")
    prompt: str = field(default="")
    id: int = field(default=None)

def prompt_form(prompt=Prompt()):
    with st.form(key="create_prompt_form", clear_on_submit=True):
        title = st.text_input("Title", value=prompt.title, help="Title is required.")
        prompt_text = st.text_area("Prompt", height=200, value=prompt.prompt, help="Prompt text is required.")
        submitted = st.form_submit_button("Submit")
        if submitted and title and prompt_text:
            return Prompt(title=title, prompt=prompt_text, id=prompt.id)
        elif submitted:
            st.warning("Both title and prompt are required.")

def edit_prompt_form(prompt):
    with st.form(key=f"edit_prompt_form_{prompt.id}", clear_on_submit=True):
        title = st.text_input("Title", value=prompt.title, help="Title is required.")
        prompt_text = st.text_area("Prompt", height=200, value=prompt.prompt, help="Prompt text is required.")
        submitted = st.form_submit_button("Save")
        if submitted and title and prompt_text:
            return Prompt(title=title, prompt=prompt_text, id=prompt.id)
        elif submitted:
            st.warning("Both title and prompt are required.")

st.title("Promptbase")
st.subheader("A simple app to store and retrieve prompts")

# Form for creating prompts
new_prompt = prompt_form()

if new_prompt and new_prompt.id is None:
    cur.execute("INSERT INTO prompts (title, prompt) VALUES (%s, %s) RETURNING id", (new_prompt.title, new_prompt.prompt,))
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
            edited_prompt = edit_prompt_form(prompt_to_edit)
            if edited_prompt:
                cur.execute("UPDATE prompts SET title = %s, prompt = %s WHERE id = %s", (edited_prompt.title, edited_prompt.prompt, edited_prompt.id))
                con.commit()
                st.success(f"Prompt {edited_prompt.id} updated successfully!")
                st.experimental_rerun()
            else:
                st.empty()  # Clear the edit form if no changes were made
        else:
            st.empty()  # Clear the edit form if not in edit mode
