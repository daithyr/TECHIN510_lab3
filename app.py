import os
from dataclasses import dataclass, field
import streamlit as st
import psycopg2

# Retrieve the Supabase connection URL from Streamlit secrets
supabase_url = st.secrets["DATABASE_URL"]

con = psycopg2.connect(supabase_url)
cur = con.cursor()

# Function to execute SQL queries
def execute_query(query, params=None):
    with con:
        with con.cursor() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Check if the query is a SELECT query
            if query.strip().lower().startswith("select"):
                result = cursor.fetchall()
                return result
            else:
                # For non-SELECT queries, return None
                return None


# Function to create new task
def create_task(title, prompt):
    query = "INSERT INTO tasks (title, prompt, favorite) VALUES (%s, %s, %s)"
    execute_query(query, (title, prompt, False))

# Function to list all tasks
def list_tasks(show_favorite=False):
    if show_favorite:
        query = "SELECT * FROM tasks WHERE favorite = TRUE"
    else:
        query = "SELECT * FROM tasks"
    return execute_query(query)

# Function to list favorite tasks
def list_favorite_tasks():
    query = "SELECT * FROM tasks WHERE favorite = TRUE"
    return execute_query(query)

# Function to search tasks
def search_tasks(keyword):
    query = "SELECT * FROM tasks WHERE title LIKE %s OR prompt LIKE %s"
    return execute_query(query, ('%' + keyword + '%', '%' + keyword + '%'))

# Function to mark a task as favorite
def mark_as_favorite(task_id):
    query = "UPDATE tasks SET favorite = TRUE WHERE id = %s"
    execute_query(query, (task_id,))

# Function to remove a task from favorites
def remove_from_favorites(task_id):
    query = "UPDATE tasks SET favorite = FALSE WHERE id = %s"
    execute_query(query, (task_id,))
    
# Function to update a task
def update_task(task_id, title, prompt):
    query = "UPDATE tasks SET title = %s, prompt = %s WHERE id = %s"
    execute_query(query, (title, prompt, task_id))
    
# Function to delete a task
def delete_task(task_id):
    query = "DELETE FROM tasks WHERE id = %s"
    execute_query(query, (task_id,))
    
    
def main():
    st.title("Prompt Manager")

    # Add new task
    st.header("Create New Prompt ✏️")
    new_title = st.text_input("Title")
    new_prompt = st.text_area("Prompt")
    if st.button("Create"):
        create_task(new_title, new_prompt)
        st.success("Task created successfully!")
        
    # Section for updating a prompt
    st.header("Update Prompt 🔄")
    task_id_update = st.text_input("Enter Task ID to Update")
    update_title = st.text_input("New Title")
    update_prompt = st.text_area("New Prompt")
    if st.button("Update"):
        update_task(task_id_update, update_title, update_prompt)
        st.success("Task updated successfully!")


    # Layout for listing all tasks
    st.header("All Prompts 📝")
    show_favorite = st.checkbox("Show only favorite prompts")
    tasks = list_tasks(show_favorite)
    if not tasks:
        st.info("No prompts found.")
    else:
        cols = st.columns(5)
        cols[0].write("ID")
        cols[1].write("Title")
        cols[2].write("Prompt")
        cols[3].write("Favorite")
        cols[4].write("Delete")
        for row in tasks:
            cols = st.columns(5)
            cols[0].write(row[0])
            cols[1].write(row[1])
            cols[2].write(row[2])
            favorite = cols[3].checkbox("", value=row[3], key=f"favorite_checkbox_{row[0]}")

            if favorite:
                mark_as_favorite(row[0])
            else:
                remove_from_favorites(row[0])

            if cols[4].button(f"Delete {row[0]}", key=f"delete_button_{row[0]}"):
                delete_task(row[0])


    # Search tasks
    st.header("Search Prompts 🔍")
    search_term = st.text_input("Search by keyword in title")
    if st.button("Search"):
        search_results = search_tasks(search_term)
        for result in search_results:
            st.write(result)
            
    

if __name__ == "__main__":
    main()
# cur.execute('''
#     CREATE TABLE IF NOT EXISTS prompts (
#         id SERIAL PRIMARY KEY,
#         title TEXT NOT NULL,
#         prompt TEXT NOT NULL,
#         favorite BOOLEAN DEFAULT FALSE,
#         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#         updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#     )
# ''')
# con.commit()

# @dataclass
# class Prompt:
#     title: str = field(default="")
#     prompt: str = field(default="")
#     id: int = field(default=None)

# def prompt_form(prompt=Prompt()):
#     with st.form(key="create_prompt_form", clear_on_submit=True):
#         title = st.text_input("Title", value=prompt.title, help="Title is required.")
#         prompt_text = st.text_area("Prompt", height=200, value=prompt.prompt, help="Prompt text is required.")
#         submitted = st.form_submit_button("Submit")
#         if submitted and title and prompt_text:
#             return Prompt(title=title, prompt=prompt_text, id=prompt.id)
#         elif submitted:
#             st.warning("Both title and prompt are required.")

# def edit_prompt_form(prompt):
#     with st.form(key=f"edit_prompt_form_{prompt.id}", clear_on_submit=True):
#         title = st.text_input("Title", value=prompt.title, help="Title is required.")
#         prompt_text = st.text_area("Prompt", height=200, value=prompt.prompt, help="Prompt text is required.")
#         submitted = st.form_submit_button("Save")
#         if submitted and title and prompt_text:
#             return Prompt(title=title, prompt=prompt_text, id=prompt.id)
#         elif submitted:
#             st.warning("Both title and prompt are required.")

# st.title("Promptbase")
# st.subheader("A simple app to store and retrieve prompts")

# # Form for creating prompts
# new_prompt = prompt_form()

# if new_prompt and new_prompt.id is None:
#     cur.execute("INSERT INTO prompts (title, prompt) VALUES (%s, %s) RETURNING id", (new_prompt.title, new_prompt.prompt,))
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
#             edited_prompt = edit_prompt_form(prompt_to_edit)
#             if edited_prompt:
#                 cur.execute("UPDATE prompts SET title = %s, prompt = %s WHERE id = %s", (edited_prompt.title, edited_prompt.prompt, edited_prompt.id))
#                 con.commit()
#                 st.success(f"Prompt {edited_prompt.id} updated successfully!")
#                 st.experimental_rerun()
