import os
import glob
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import  OpenAIEmbeddings
from langchain_chroma import Chroma

CHROMA_PATH = "chroma_store"
DATA_PATH = "data"

def ingest_pdfs():
        pdf_files = glob.glob(os.path.join(DATA_PATH, "*.pdf"))
        if not pdf_files:
            print("No pdf files found in the data folder.")
            return
        
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

        db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)

        for pdf in pdf_files:
            print(f"Processing {pdf}...")
            loader = PyPDFLoader(pdf)
            docs = loader.load()

            for doc in docs:
                    doc.metadata["source"] = os.path.basename(pdf)
            
            chunks = splitter.split_documents(docs)
            db.add_documents(chunks)
        
        print(f"All PDFs are loaded with metadata stored in {CHROMA_PATH}")

            
if __name__ == "__main__":
    ingest_pdfs()