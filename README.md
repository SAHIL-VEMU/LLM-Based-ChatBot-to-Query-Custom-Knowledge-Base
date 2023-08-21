# ChatDoc

## What is ChatDoc?
ChatDoc is an interactive application that helps users upload various types of documents, extract relevant information, and retrieve answers to their queries. The application supports a range of document formats, including PDF, TXT, JSON, and DOCX.

## Features
* Upload multiple files (upto 10 documents) at once.
* Supports various document formats: PDF, TXT, JSON, and DOCX.
* Extracts the uploaded documents and divides it into smaller, more digestible chunks.
* Embeds the uploaded documents into searchable knowledge base.
* User can enter a question/query and receive a relevant answer from the knowledge base.
* Provides the source document and context for each answer.

## Running
Streamlit should be installed along with dependent python modules. After installing Streamlit, run the following command:
```bash
python -m streamlit run chat_doc.py --server.maxUploadSize 2
```
The application should now be running at http://localhost:8501.

## Usage
* Open the application in the web browser.
* Select the `ChatDoc` tab.
* Upload upto 10 documents in the supported formats.
* The progress bar shows the extraction and processing progress.
* Once the documents are processed, enter a question in the text box and click "Submit".
* The relevant answer will be displayed along with the source document and context.
* Enjoy using ChatDoc to search and retrieve information from your uploaded documents.

## Limitations
* Max File size: 2MB.
* Requires Internet Connectivity.