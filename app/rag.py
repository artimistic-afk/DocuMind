import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

VECTORSTORE_DIR = "vectorstore"
os.makedirs(VECTORSTORE_DIR, exist_ok=True)

# Load HuggingFace embeddings (free, no API key needed)
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
)

PROMPT_TEMPLATE = """You are DocuMind, an expert AI assistant for analyzing documents.
Use the following context from the document to answer the question accurately and concisely.
If the answer is not in the context, say "I couldn't find that information in the document."

Context:
{context}

Question: {question}

Answer:"""

prompt = PromptTemplate(
    template=PROMPT_TEMPLATE,
    input_variables=["context", "question"],
)


def ingest_pdf(file_path: str, session_id: str) -> str:
    """
    Load a PDF, split into chunks, embed, and store in FAISS.
    Returns the path to the saved vectorstore.
    """
    # Load PDF
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    chunks = splitter.split_documents(documents)

    if not chunks:
        raise ValueError("No text could be extracted from the PDF.")

    # Embed and store
    vectorstore = FAISS.from_documents(chunks, embeddings)
    save_path = os.path.join(VECTORSTORE_DIR, session_id)
    vectorstore.save_local(save_path)

    return save_path


def query_document(vectorstore_path: str, question: str) -> dict:
    """
    Load a FAISS vectorstore and answer a question using RAG.
    Returns answer and source page references.
    """
    # Load vectorstore
    vectorstore = FAISS.load_local(
        vectorstore_path,
        embeddings,
        allow_dangerous_deserialization=True,
    )

    # Set up retriever
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4},
    )

    # Load LLM (Groq — free and fast)
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.2,
        api_key=os.getenv("GROQ_API_KEY"),
    )

    # Build RAG chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt},
    )

    result = qa_chain.invoke({"query": question})

    # Extract source page numbers
    sources = []
    for doc in result.get("source_documents", []):
        page = doc.metadata.get("page", "unknown")
        source = f"Page {page + 1}"
        if source not in sources:
            sources.append(source)

    return {
        "answer": result["result"],
        "sources": sources,
    }
