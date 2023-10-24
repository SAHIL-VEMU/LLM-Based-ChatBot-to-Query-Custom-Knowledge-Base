import os
import json
import docx2txt
from io import StringIO
from PyPDF2 import PdfReader
from langchain.llms import OpenAI
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains.question_answering import load_qa_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter


model_name = "sentence-transformers/all-mpnet-base-v2"
model_kwargs = {"device": "cpu"}
encode_kwargs = {"normalize_embeddings": False}


embeddings = HuggingFaceEmbeddings(
    model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs
)
llm = OpenAI(model_name="gpt-3.5-turbo")


def check_duplicate(File):
    if os.path.exists('FAISS/Metadata.json'):
        with open('FAISS/Metadata.json', "r") as contents:
            dictionary = json.load(contents)
        return File.name in dictionary
    else:
        with open('FAISS/Metadata.json', "w+") as contents:
            json.dump({}, contents)
        return False


def get_text(File):
    text = ""
    match File.type:
        case "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            abs_path = os.path.abspath(File.name)
            # saves the uploaded file in the local system
            with open(abs_path, "wb+") as f:
                f.write(File.getbuffer())
            text = docx2txt.process(abs_path)
            # deletes the uploaded file from the local system
            os.remove(abs_path)

        case "application/pdf":
            pdf_reader = PdfReader(File)
            for page in pdf_reader.pages:
                text += page.extract_text()

        case _:  # for json and txt files
            # to convert to a string based IO
            stringio = StringIO(File.getvalue().decode("utf-8"))
            # to read file as string
            text = stringio.read()

    return text


def get_chunks(text):
    # text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        separators=[" ", "\n\n", "\n"],
        chunk_size=3000,
        chunk_overlap=150,
        length_function=len,
    )
    # list of strings known as chunks
    chunks = text_splitter.split_text(text=text)
    return chunks


def add_to_database(chunks, f_name):
    metadata = []
    for i in range(len(chunks)):
        metadata.append({"File_Name": f_name})

    if os.path.exists('FAISS/kb'):
        exsisting_db = FAISS.load_local('FAISS/kb', embeddings)
        knowledge_base = FAISS.from_texts(
            chunks, embedding=embeddings, metadatas=metadata
        )
        knowledge_base.merge_from(exsisting_db)
        knowledge_base.save_local('FAISS/kb')
    else:
        knowledge_base = FAISS.from_texts(
            chunks, embedding=embeddings, metadatas=metadata
        )
        knowledge_base.save_local('FAISS/kb')

    if os.path.exists('FAISS/Metadata.json'):
        with open('FAISS/Metadata.json', "r") as contents:
            dictionary = json.load(contents)
        dictionary[f_name] = len(chunks)
        with open('FAISS/Metadata.json', "w") as contents:
            json.dump(dictionary, contents)


def get_relevant_docs(question):
    knowledge_base = FAISS.load_local('FAISS/kb', embeddings=embeddings)
    docs_and_score = knowledge_base.similarity_search_with_score(question)
    return docs_and_score


def get_answer(ques):
    docs_and_score = get_relevant_docs(question=ques)
    docs = [x[0] for x in docs_and_score]
    chain = load_qa_chain(llm, chain_type="stuff")
    ques = f"{ques} Answer only from the given context."
    response = chain.run(input_documents=docs, question=ques)
    return response
