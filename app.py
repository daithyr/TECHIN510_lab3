import streamlit as st
import pandas as pd
from datetime import datetime

# File path for the CSV data store
data_file = 'prompts.csv'

# Initialize or load prompts data
try:
    prompts_df = pd.read_csv(data_file, converters={'tags': eval})  # eval tags as list
except FileNotFoundError:
    prompts_df = pd.DataFrame(columns=['id', 'title', 'content', 'favorite', 'tags', 'creation_date', 'last_modified_date', 'usage_count'])
    prompts_df.to_csv(data_file, index=False)

# CRUD operations
def add_prompt(title, content, tags):
    global prompts_df
    new_id = prompts_df['id'].max() + 1 if not prompts_df.empty else 1
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prompts_df = prompts_df.append({
        'id': new_id, 'title': title, 'content': content, 'favorite': False,
        'tags': tags.split(','), 'creation_date': now, 'last_modified_date': now, 'usage_count': 0
    }, ignore_index=True)
    prompts_df.to_csv(data_file, index=False)

def delete_prompt(id):
    global prompts_df
    prompts_df = prompts_df[prompts_df['id'] != id]
    prompts_df.to_csv(data_file, index=False)

# App Title
st.title("ChatGPT Prompt Manager")

# Sidebar Navigation
page = st.sidebar.selectbox("Navigate", ["Create Prompt", "View Prompts", "Search Prompts"])

# Page: Create Prompt
if page == "Create Prompt":
    with st.form("Create Prompt"):
        st.write("## Create a new prompt")
        title = st.text_input("Title")
        content = st.text_area("Prompt Content")
        tags = st.text_input("Tags (comma-separated)")
        submitted = st.form_submit_button("Save Prompt")
        if submitted and title and content:
            add_prompt(title, content, tags)
            st.success("Prompt saved successfully!")

# Page: View Prompts
elif page == "View Prompts":
    st.write("## All Prompts")
    for index, row in prompts_df.iterrows():
        st.write(f"### {row['title']}")
        st.write(f"**Tags:** {', '.join(row['tags'])}")
        st.write(f"**Content:** {row['content']}")
        if st.button(f"Delete {row['id']}", key=f"delete_{row['id']}"):
            delete_prompt(row['id'])
            st.experimental_rerun()

# Page: Search Prompts
elif page == "Search Prompts":
    search_query = st.text_input("Search prompts by title, content, or tags")
    if search_query:
        # Simple filter for demonstration, could be expanded for full-text search or using tags
        filtered_prompts = prompts_df[prompts_df.apply(lambda row: search_query.lower() in row['title'].lower() 
                                                       or search_query.lower() in row['content'].lower() 
                                                       or any(search_query.lower() in tag for tag in row['tags']), axis=1)]
        for index, row in filtered_prompts.iterrows():
            st.write(f"### {row['title']}")
            st.write(f"**Tags:** {', '.join(row['tags'])}")
            st.write(f"**Content:** {row['content']}")
