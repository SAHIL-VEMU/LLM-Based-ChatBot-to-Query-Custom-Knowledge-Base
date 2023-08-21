from PIL import Image
from dotenv import load_dotenv
import streamlit as st

# python -m streamlit run app.py --server.maxUploadSize 2

load_dotenv()

from FAISS import faiss
from Pinecone import pine_cone

# image = Image.open(r"ChatDoc_Final\Optum_logo_2021.png")

st.set_page_config(page_title="APP")

# st.image(image=image, width=72, use_column_width=False)

st.header("ChatDoc")

faiss_tab, pinecone_tab, about_tab, contact_tab = st.tabs(
    ["FAISS", "Pinecone", "About", "Contact"]
)

with faiss_tab:
    faiss()

with pinecone_tab:
    pine_cone()

with about_tab:
    st.header("About")
    ABOUT = """ 

ChatDoc is an interactive application that helps users upload various types of documents, extract relevant information, and retrieve answers to their queries. The application supports a range of document formats, including PDF, TXT, JSON, and DOCX.

## Features
* Upload multiple files (upto 10 documents) at once.
* Supports various document formats: PDF, TXT, JSON, and DOCX.
* Extracts the uploaded documents and divides it into smaller, more digestible chunks.
* Embeds the uploaded documents into searchable knowledge base.
* User can enter a question/query and receive a relevant answer from the knowledge base.
* Provides the source document and context for each answer. 

## Limitations
* Max File size: 2MB.
* Requires Internet Connectivity.

## Your Feedback Matters
We value your feedback as it helps drive improvements in our chatbot's performance. If our AI ChatDoc could not answer your question, or if you have any suggestions for improvement, please don't hesitate to let me know (from the Contact Page). Your insights will aid in the ongoiung development and refinement of my virtual asistant. Thank you for your trust in our AI ChatDoc.

Developed by Sahil Vemu.
     """
    st.write(ABOUT)

with contact_tab:
    st.header("Contact")
    CONTACT = """
    Do you need assistance or have questions about our question-answering chatbot? I am ready to help you!

    I understand the importance of providing you with excellent service and right solutions. Please do not hesitate to reach out to us for any inquiries, or general feedback. I am always eager to help you make the most of my AI-powered ChatDoc.

    ## Email
    For any technical or inquiries, please email me:
    Krishna Sahil Vemu : sahilvemu@gmail.com

    Thank you for using my ChatDoc application. I look forward to hearing from you!
    """
    st.write(CONTACT)


# I am a 10 year old. Am I eligible to online services?
