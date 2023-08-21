import time
import os
import json
import streamlit as st
from FAISS.utils_FAISS import (
    check_duplicate,
    get_text,
    get_chunks,
    add_to_database,
    get_relevant_docs,
    get_answer,
)


def faiss():
    MAX_FILES = 10
    count = 1

    uploaded_files = st.file_uploader(
        label=f"Choose Atmost {MAX_FILES} Files ",
        accept_multiple_files=True,
        type=["pdf", "txt", "json", "docx"],
        key="faiss_file_uploader",
    )

    if len(uploaded_files) > MAX_FILES:
        st.warning(
            f"Maximum number of files reached. Only the first {MAX_FILES} will be processed."
        )
        uploaded_files = uploaded_files[:MAX_FILES]

    if len(uploaded_files) > 0:
        progress_text = "Upload in progress. Please Wait."
        my_bar = st.progress(0, text=progress_text)
        tot_steps_before_completion = len(uploaded_files) * 4

    for uploaded_file in uploaded_files:
        if check_duplicate(File=uploaded_file):
            my_bar.progress(
                (count / tot_steps_before_completion),
                text=f"File  {uploaded_file.name}  already Present in the Knowledge Base!",
            )
            time.sleep(1)
            count += 4
            if count == tot_steps_before_completion + 1:
                my_bar.progress(100, text="Upload Complete")
            continue

        my_bar.progress(
            (count / tot_steps_before_completion),
            text=f"Extracting the Text from  {uploaded_file.name}  .",
        )
        count += 1
        time.sleep(1)
        text = get_text(File=uploaded_file)

        my_bar.progress(
            (count / tot_steps_before_completion),
            text=f"Converting  {uploaded_file.name}  to smaller modules.",
        )
        count += 1
        time.sleep(1)
        chunks = get_chunks(text=text)

        my_bar.progress(
            (count / tot_steps_before_completion),
            text=f"Embedding the File  {uploaded_file.name}  .",
        )
        count += 1
        add_to_database(chunks=chunks, f_name=uploaded_file.name)

        my_bar.progress(
            (count / tot_steps_before_completion),
            text=f" {uploaded_file.name}  is Uploaded !.",
        )
        count += 1

        if count == tot_steps_before_completion + 1:
            my_bar.progress(100, text="Upload Complete.")

    with st.expander("View / Delete Files"):
        if not os.path.exists("FAISS\Metadata.json"):
            st.error("knowledge Base does not Exists!!")
        else:
            with open("FAISS\Metadata.json", "r") as f:
                dictionary = json.load(f)
            exsisting_files = list(dictionary)
            if len(exsisting_files) == 0:
                st.error("No Files Exists in the knowledge Base!!")
            for file_name in exsisting_files:
                st.write(file_name)

    user_question = st.text_input("Please enter the question: ", key="faiss_text_input")

    if st.button("Submit", key="faiss_button"):
        response = get_answer(ques=user_question)
        st.write(response)
        st.divider()
        st.write("The Documents, ChatDoc reffered :")
        docs_and_score = get_relevant_docs(question=user_question)
        for doc in docs_and_score:
            fn = doc[0].metadata["File_Name"]  # File Name
            fc = doc[0].page_content  # File Content
            st.markdown(f"Answered from the File :  :blue[{fn}]")
            st.write(f"Answered from the context :  \n{fc}")
            st.write("Similarity Score = " + str(doc[1]))
            st.divider()
