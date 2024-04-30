import os
from dataclasses import dataclass
import datetime
import sys
import streamlit as st
import psycopg2
from dotenv import load_dotenv

load_dotenv()
print(os.getenv('DATABASE_URL'))
con = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = con.cursor()

cur.execute('''
Create TABLE IF NOT EXISTS prompts (
    id SERIAL PRIMARY KEY,
    title TEXT,
    prompt TEXT,
    is_favorite BOOLEAN,
    created_at TIMESTAMP NOT NULL
) 
''')

@dataclass
class Prompt:
    id: int = None
    title: str = ''
    prompt: str = ''
    is_favorite: bool = False
    created_at: datetime.datetime = None

def callback():
    st.session_state.first_form = True

def prompt_form(prompt=Prompt()):
    with st.form(key=f'prompt_form', clear_on_submit=True):
        title = st.text_input('Title', value=prompt.title)
        prompt_text = st.text_area('Prompt', value=prompt.prompt)
        is_favorite = st.checkbox('Favorite', value=prompt.is_favorite)
        ret = st.form_submit_button('Submit')
        if ret:
            return Prompt(prompt.id, title, prompt_text, is_favorite, datetime.datetime.now() if prompt.created_at is None else prompt.created_at)
        

def display_prompts(prompts):
    for p in prompts:
        with st.expander(f'{p[1]} {":star-struck:" if p[3] else ""}'):
            st.code(p[2])
            st.text(f'created at {p[4]}')
            if st.button("Delete", key=f"delete_{p[0]}"):
                cur.execute("DELETE FROM prompts WHERE id = %s", (p[0],))
                con.commit()
                st.rerun()
            if st.button("Toggle Favorite", key=f"fav_{p[0]}"):
                cur.execute("UPDATE prompts SET is_favorite = NOT is_favorite WHERE id = %s", (p[0],))
                con.commit()
                st.rerun()
            if st.button("Edit", key=f"edit_{p[0]}", on_click=callback) or st.session_state.first_form:
                with st.form(key=f'prompt_{p[0]}', clear_on_submit=True):
                    title = st.text_input('Title', value=p[1])
                    prompt_text = st.text_area('Prompt', value=p[2])
                    is_favorite = st.checkbox('Favorite', value=p[3])
                    ret = st.form_submit_button('Submit')
                    if ret:
                        print('in ret')
                        cur.execute("UPDATE prompts SET title = %s, prompt = %s, is_favorite = %s WHERE id = %s", (title, prompt_text, is_favorite, p[0]))
                        con.commit()
                        st.success("Prompt updated successfully!")
                        st.rerun()

    

st.title('Prompt Storage')
st.subheader('A simple app to store and retrieve prompts')

if 'first_form' not in st.session_state:
    st.session_state.first_form = False




prompt = prompt_form()
if prompt:
    if prompt.id:  # This means we are updating an existing prompt
        cur.execute("UPDATE prompts SET title = %s, prompt = %s, is_favorite = %s WHERE id = %s", 
                    (prompt.title, prompt.prompt, prompt.is_favorite, prompt.id))
    else:  # This means we are creating a new prompt
        cur.execute("INSERT INTO prompts (title, prompt, is_favorite, created_at) VALUES (%s, %s, %s, %s)",(prompt.title, prompt.prompt, prompt.is_favorite, prompt.created_at))
con.commit()
st.success("Prompt added/updated successfully!")

st.markdown('---')

# Search, sort, and filter bar
search_query = st.text_input("Search prompts")
sort_order = st.selectbox("Sort by", ["title", "prompt", "created_at"], index=0)
filter_favorites = st.checkbox("Show favorites only")
search_button = st.button("Search")

query = "SELECT * FROM prompts"
if filter_favorites:
    query += " WHERE is_favorite = true"
if search_query:
    if filter_favorites:
        query += " AND "
    else:
        query += " WHERE "
    query += "title LIKE %s OR prompt LIKE %s"
    query += f" ORDER BY {sort_order} DESC"
    cur.execute(query, ('%' + search_query + '%', '%' + search_query + '%'))
else:
    query += f" ORDER BY {sort_order} DESC"
    cur.execute(query)

prompts = cur.fetchall()



display_prompts(prompts)

# sys.exit()
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
