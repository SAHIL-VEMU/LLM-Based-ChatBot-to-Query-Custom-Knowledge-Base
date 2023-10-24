import os
import json
from uuid import uuid4
from io import StringIO
from dotenv import load_dotenv
import docx2txt
import pinecone
from PyPDF2 import PdfReader
from langchain.llms import OpenAI
from langchain.vectorstores import Pinecone
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains.question_answering import load_qa_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()

pinecone.init(
    api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENVIRONMENT")
)

model_name = "sentence-transformers/all-mpnet-base-v2"
model_kwargs = {"device": "cpu"}
encode_kwargs = {"normalize_embeddings": False}


embeddings = HuggingFaceEmbeddings(
    model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs
)
llm = OpenAI(model_name="gpt-3.5-turbo")


def get_index():
    index_name = "chat-doc-kb"
    if index_name not in pinecone.list_indexes():
        pinecone.create_index(
            name=index_name,
            metric="cosine",
            dimension=768,  # 768 dimension of text-embedding-ada-002
        )
    index = pinecone.Index(index_name)
    return index


def check_duplicate(File):
    if os.path.exists('Pinecone/Metadata.json'):
        with open('Pinecone/Metadata.json', "r") as contents:
            dictionary = json.load(contents)
        return File.name in dictionary
    else:
        with open('Pinecone/Metadata.json', "w+") as contents:
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
    embeds = embeddings.embed_documents(chunks)
    for index, content in enumerate(chunks):
        metadata.append({"File_Name": f_name, "Chunk_No": index + 1, "Text": content})

    index = get_index()
    ids = [str(uuid4()) for _ in chunks]
    index.upsert(vectors=zip(ids, embeds, metadata))
    with open('Pinecone/Metadata.json', "r") as contents:
        dictionary = json.load(contents)
    dictionary[f_name] = ids
    with open('Pinecone/Metadata.json', "w") as contents:
        json.dump(dictionary, contents)


def get_relevant_docs(question):
    text_field = "Text"
    index = get_index()
    knowledge_base = Pinecone(index, embeddings.embed_query, text_field)
    docs_and_score = knowledge_base.similarity_search_with_score(question, k=3)
    return docs_and_score


def get_answer(ques):
    docs_and_score = get_relevant_docs(question=ques)
    docs = [x[0] for x in docs_and_score]
    chain = load_qa_chain(llm, chain_type="stuff")
    ques = f"{ques} Answer only from the given context."
    response = chain.run(input_documents=docs, question=ques)
    return response


def delete_file(f_name):
    index = get_index()
    with open('Pinecone/Metadata.json', "r") as f:
        dictionary = json.load(f)
    ids = dictionary[f_name.replace("\n", "")]
    index.delete(ids=ids)
    dictionary.pop(f_name.replace("\n", ""))
    with open('Pinecone/Metadata.json', "w") as contents:
        json.dump(dictionary, contents)
