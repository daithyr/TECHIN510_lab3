import os
from dataclasses import dataclass

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
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
)

@dataclass
class Prompt:
    title: str
    prompt: str

def prompt_form(prompt=Prompt("","")):
    """
    TODO: Add validation to the form, so that the title and prompt are required.
    """
    with st.form(key="prompt_form", clear_on_submit=True):
        title = st.text_input("Title", value=prompt.title)
        prompt = st.text_area("Prompt", height=200, value=prompt.prompt)
        submitted = st.form_submit_button("Submit")
        if submitted:
            return Prompt(title, prompt)

st.title("Promptbase")
st.subheader("A simple app to store and retrieve prompts")

prompt = prompt_form()
if prompt:
    cur.execute("INSERT INTO prompts (title, prompt) VALUES (%s, %s)", (prompt.title, prompt.prompt,))
    con.commit()
    st.success("Prompt added successfully!")

cur.execute("SELECT * FROM prompts")
prompts = cur.fetchall()

# TODO: Add a search bar
# TODO: Add a sort by date
# TODO: Add favorite button
for p in prompts:
    with st.expander(p[1]):
        st.code(p[2])
        # TODO: Add a edit function
        if st.button("Delete", key=p[0]):
            cur.execute("DELETE FROM prompts WHERE id = %s", (p[0],))
            con.commit()
            st.rerun()



# import streamlit as st
# import pandas as pd
# from datetime import datetime

# # Initialize data store
# data_file = 'prompts.csv'
# try:
#     prompts_df = pd.read_csv(data_file, converters={'tags': eval})
# except FileNotFoundError:
#     prompts_df = pd.DataFrame(columns=['id', 'title', 'content', 'favorite', 'tags', 'creation_date', 'last_modified_date', 'usage_count'])
#     prompts_df.to_csv(data_file, index=False)

# # Function to save changes to CSV
# def save_changes():
#     prompts_df.to_csv(data_file, index=False)

# # CRUD Operations
# def add_prompt(title, content, tags):
#     new_id = prompts_df['id'].max() + 1 if not prompts_df.empty else 1
#     now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     prompts_df.loc[len(prompts_df.index)] = [new_id, title, content, False, tags.split(','), now, now, 0]
#     save_changes()

# def update_prompt(id, title, content, tags):
#     row_index = prompts_df.index[prompts_df['id'] == id].tolist()[0]
#     prompts_df.at[row_index, 'title'] = title
#     prompts_df.at[row_index, 'content'] = content
#     prompts_df.at[row_index, 'tags'] = tags.split(',')
#     prompts_df.at[row_index, 'last_modified_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     save_changes()

# def delete_prompt(id):
#     global prompts_df
#     prompts_df = prompts_df[prompts_df['id'] != id]
#     save_changes()



# def toggle_favorite(id):
#     row_index = prompts_df.index[prompts_df['id'] == id].tolist()[0]
#     prompts_df.at[row_index, 'favorite'] = not prompts_df.at[row_index, 'favorite']
#     save_changes()

# # Streamlit UI
# st.title("ChatGPT Prompt Manager")

# # Navigation
# page = st.sidebar.selectbox("Navigate", ["Create Prompt", "View Prompts", "Search Prompts", "Favorites"])

# if page == "Create Prompt":
#     with st.form("Create Prompt"):
#         st.write("## Create a New Prompt")
#         title = st.text_input("Title")
#         content = st.text_area("Prompt Content")
#         tags = st.text_input("Tags (comma-separated)")
#         submitted = st.form_submit_button("Save Prompt")
#         if submitted and title and content:
#             add_prompt(title, content, tags)
#             st.success("Prompt saved successfully!")

# elif page == "View Prompts":
#     st.write("## View and Manage Prompts")
#     for index, row in prompts_df.iterrows():
#         with st.expander(f"{row['title']}"):
#             st.write(f"**ID:** {row['id']}")
#             st.write(f"**Content:** {row['content']}")
#             st.write(f"**Tags:** {', '.join(row['tags'])}")
#             st.write(f"**Favorite:** {'Yes' if row['favorite'] else 'No'}")
#             if st.button(f"Toggle Favorite", key=f"fav_{row['id']}"):
#                 toggle_favorite(row['id'])
#                 st.experimental_rerun()
#             if st.button(f"Delete {row['id']}", key=f"delete_{row['id']}"):
#                 prompts_df.drop(index, inplace=True)
#                 save_changes()
#                 st.experimental_rerun()
#             title, content, tags = st.text_input(f"Title {row['id']}", row['title']), st.text_area(f"Content {row['id']}", row['content']), st.text_input(f"Tags {row['id']}", ', '.join(row['tags']))
#             if st.button(f"Update {row['id']}", key=f"update_{row['id']}"):
#                 update_prompt(row['id'], title, content, tags)
#                 st.experimental_rerun()

# elif page == "Search Prompts":
#     search_query = st.text_input("Enter search query")
#     if search_query:
#         results = prompts_df[prompts_df.apply(lambda row: search_query.lower() in row['title'].lower() or search_query.lower() in row['content'].lower() or search_query.lower() in ','.join(row['tags']).lower(), axis=1)]
#         for _, row in results.iterrows():
#             st.subheader(row['title'])
#             st.write(row['content'])

# elif page == "Favorites":
#     st.write("## Favorite Prompts")
#     favorites = prompts_df[prompts_df['favorite'] == True]
#     for index, row in favorites.iterrows():
#         st.subheader(row['title'])
#         st.write(row['content'])
