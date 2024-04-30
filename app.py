import os
from dataclasses import dataclass
import datetime

import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

con = psycopg2.connect(os.getenv("DATABASE_URL"), cursor_factory=RealDictCursor)
cur = con.cursor()

@dataclass
class Prompt:
    title: str
    prompt: str
    is_favorite: bool = False

def prompt_form(prompt=Prompt("", "", False)):
    with st.form(key="prompt_form", clear_on_submit=True):
        title = st.text_input("Title", value=prompt.title)
        prompt_text = st.text_area("Prompt", height=200, value=prompt.prompt)
        is_favorite = st.checkbox("Favorite", value=prompt.is_favorite)
        submitted = st.form_submit_button("Submit")
        if submitted and title and prompt_text:  
            return Prompt(title, prompt_text, is_favorite)
        elif submitted:
            st.error("Both title and prompt must be filled.")

st.title("Promptbase")
st.subheader("A simple app to store and retrieve prompts")

# Filtering and sorting options
date_filter = st.selectbox(
    'Filter by date',
    ('All Time', 'Today', 'This Week', 'This Month', 'This Year')
)

if date_filter == 'Today':
    start_date = datetime.date.today()
elif date_filter == 'This Week':
    start_date = datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday())
elif date_filter == 'This Month':
    start_date = datetime.date.today().replace(day=1)
elif date_filter == 'This Year':
    start_date = datetime.date.today().replace(month=1, day=1)
else:
    start_date = None

filter_favorite = st.checkbox('Show only favorites')

# Applying the filter and sort query
if start_date:
    cur.execute("""
        SELECT * FROM prompts 
        WHERE created_at >= %s
        AND (%s OR is_favorite = true)
        ORDER BY created_at DESC""", 
        (start_date, not filter_favorite))
else:
    cur.execute("""
        SELECT * FROM prompts 
        WHERE %s OR is_favorite = true
        ORDER BY created_at DESC""", 
        (not filter_favorite,))

prompts = cur.fetchall()

# Displaying prompts with improved favorite visibility
for p in prompts:
    favorite_status = "❤️" if p['is_favorite'] else "🖤"
    with st.expander(f"{favorite_status} {p['title']} (created on {p['created_at'].date()})"):
        st.code(p['prompt'])
        if st.button("Toggle Favorite", key=f"fav-{p['id']}"):
            cur.execute("UPDATE prompts SET is_favorite = NOT is_favorite WHERE id = %s", (p['id'],))
            con.commit()
            st.experimental_rerun()
        if st.button("Delete", key=f"del-{p['id']}"):
            cur.execute("DELETE FROM prompts WHERE id = %s", (p['id'],))
            con.commit()
            st.experimental_rerun()

prompt = prompt_form()
if prompt:
    cur.execute("INSERT INTO prompts (title, prompt, is_favorite) VALUES (%s, %s, %s)", 
                (prompt.title, prompt.prompt, prompt.is_favorite))
    con.commit()
    st.success("Prompt added successfully!")
    st.experimental_rerun()
# import os
# from dataclasses import dataclass, field
# import streamlit as st
# import psycopg2

# # Retrieve the DATABASE_URL from Streamlit secrets
# database_url = st.secrets["DATABASE_URL"]

# con = psycopg2.connect(database_url)
# cur = con.cursor()

# cur.execute(
#     """
#     SELECT EXISTS (
#         SELECT FROM information_schema.tables
#         WHERE table_name = 'prompts'
#     );
#     """
# )
# table_exists = cur.fetchone()[0]

# if not table_exists:
#     cur.execute(
#         """
#         CREATE TABLE prompts (
#             id SERIAL PRIMARY KEY,
#             title TEXT NOT NULL,
#             prompt TEXT NOT NULL,
#             favorite BOOLEAN DEFAULT FALSE,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#             updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         );
#         """
#     )
#     con.commit()

# @dataclass
# class Prompt:
#     title: str = field(default="")
#     prompt: str = field(default="")
#     id: int = field(default=None)

# def prompt_form(prompt=Prompt()):
#     with st.form(key="prompt_form", clear_on_submit=True):
#         title = st.text_input("Title", value=prompt.title, help="Title is required.")
#         prompt_text = st.text_area("Prompt", height=200, value=prompt.prompt, help="Prompt text is required.")
#         submitted = st.form_submit_button("Submit")
#         if submitted and title and prompt_text:
#             return Prompt(title=title, prompt=prompt_text, id=prompt.id)
#         elif submitted:
#             st.warning("Both title and prompt are required.")

# st.title("Promptbase")
# st.subheader("A simple app to store and retrieve prompts")

# # Form for creating or updating prompts
# prompt = prompt_form()

# if prompt and prompt.id is None:
#     cur.execute("INSERT INTO prompts (title, prompt) VALUES (%s, %s) RETURNING id", (prompt.title, prompt.prompt,))
#     prompt_id = cur.fetchone()[0]
#     con.commit()
#     st.success(f"Prompt {prompt_id} added successfully!")

# # Search functionality
# search_query = st.text_input("Search for prompts")
# sort_order = st.selectbox("Sort by", ["Newest", "Oldest"])

# # Displaying prompts based on search and sort order
# sort_order_sql = "DESC" if sort_order == "Newest" else "ASC"
# cur.execute(f"SELECT id, title, prompt, favorite FROM prompts WHERE title ILIKE %s OR prompt ILIKE %s ORDER BY created_at {sort_order_sql}", (f"%{search_query}%", f"%{search_query}%"))
# prompts = cur.fetchall()

# # Handling prompt updates or deletions
# for p in prompts:
#     with st.expander(f"{p[1]}"):
#         st.code(p[2])
#         if st.checkbox("Favorite", value=p[3], key=f"fav_{p[0]}"):
#             cur.execute("UPDATE prompts SET favorite = %s WHERE id = %s", (not p[3], p[0]))
#             con.commit()
#             st.success(f"Prompt {p[0]} favorite status updated!")
#         edit = st.button("Edit", key=f"edit_{p[0]}")
#         delete = st.button("Delete", key=f"delete_{p[0]}")
#         if delete:
#             cur.execute("DELETE FROM prompts WHERE id = %s", (p[0],))
#             con.commit()
#             st.experimental_rerun()
#         if edit:
#             prompt_to_edit = Prompt(title=p[1], prompt=p[2], id=p[0])
#             prompt_form(prompt_to_edit)
#             if prompt and prompt.id is not None:
#                 cur.execute("UPDATE prompts SET title = %s, prompt = %s WHERE id = %s", (prompt.title, prompt.prompt, prompt.id))
#                 con.commit()
#                 st.success(f"Prompt {prompt.id} updated successfully!")
#                 st.experimental_rerun()


# import os
# from dataclasses import dataclass, field

# import streamlit as st
# import psycopg2
# from dotenv import load_dotenv

# load_dotenv()

# con = psycopg2.connect(os.getenv("DATABASE_URL"))
# cur = con.cursor()

# import os
# from dataclasses import dataclass, field
# import streamlit as st
# import psycopg2

# # Retrieve the DATABASE_URL from Streamlit secrets
# database_url = st.secrets["DATABASE_URL"]

# con = psycopg2.connect(database_url)
# cur = con.cursor()

# cur.execute(
#     """
#     CREATE TABLE IF NOT EXISTS prompts (
#         id SERIAL PRIMARY KEY,
#         title TEXT NOT NULL,
#         prompt TEXT NOT NULL,
#         favorite BOOLEAN DEFAULT FALSE,
#         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#         updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#     )
#     """
# )


# @dataclass
# class Prompt:
#     title: str = field(default="")
#     prompt: str = field(default="")
#     id: int = field(default=None)

# def prompt_form(prompt=Prompt()):
#     with st.form(key="prompt_form", clear_on_submit=True):
#         title = st.text_input("Title", value=prompt.title, help="Title is required.")
#         prompt_text = st.text_area("Prompt", height=200, value=prompt.prompt, help="Prompt text is required.")
#         submitted = st.form_submit_button("Submit")
#         if submitted and title and prompt_text:
#             return Prompt(title=title, prompt=prompt_text, id=prompt.id)
#         elif submitted:
#             st.warning("Both title and prompt are required.")

# st.title("Promptbase")
# st.subheader("A simple app to store and retrieve prompts")

# # Form for creating or updating prompts
# prompt = prompt_form()
# if prompt and prompt.id is None:
#     cur.execute("INSERT INTO prompts (title, prompt) VALUES (%s, %s) RETURNING id", (prompt.title, prompt.prompt,))
#     prompt_id = cur.fetchone()[0]
#     con.commit()
#     st.success(f"Prompt {prompt_id} added successfully!")

# # Search functionality
# search_query = st.text_input("Search for prompts")
# sort_order = st.selectbox("Sort by", ["Newest", "Oldest"])

# # Displaying prompts based on search and sort order
# sort_order_sql = "DESC" if sort_order == "Newest" else "ASC"
# cur.execute(f"SELECT id, title, prompt, favorite FROM prompts WHERE title ILIKE %s OR prompt ILIKE %s ORDER BY created_at {sort_order_sql}", (f"%{search_query}%", f"%{search_query}%"))
# prompts = cur.fetchall()

# # Handling prompt updates or deletions
# for p in prompts:
#     with st.expander(f"{p[1]}"):
#         st.code(p[2])
#         if st.checkbox("Favorite", value=p[3], key=f"fav_{p[0]}"):
#             cur.execute("UPDATE prompts SET favorite = %s WHERE id = %s", (not p[3], p[0]))
#             con.commit()
#             st.success(f"Prompt {p[0]} favorite status updated!")
#         edit = st.button("Edit", key=f"edit_{p[0]}")
#         delete = st.button("Delete", key=f"delete_{p[0]}")
#         if delete:
#             cur.execute("DELETE FROM prompts WHERE id = %s", (p[0],))
#             con.commit()
#             st.experimental_rerun()
#         if edit:
#             prompt_to_edit = Prompt(title=p[1], prompt=p[2], id=p[0])
#             prompt_form(prompt_to_edit)
#             if prompt and prompt.id is not None:
#                 cur.execute("UPDATE prompts SET title = %s, prompt = %s WHERE id = %s", (prompt.title, prompt.prompt, prompt.id))
#                 con.commit()
#                 st.success(f"Prompt {prompt.id} updated successfully!")
#                 st.experimental_rerun()
