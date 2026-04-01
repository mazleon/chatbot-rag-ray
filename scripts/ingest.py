#!/usr/bin/env python3
"""
RAG Ingestion Script

This script loads insurance knowledge documents, chunks them, and creates
a FAISS vector store for semantic retrieval.

Usage:
    python scripts/ingest.py           # Ingest default data
    python scripts/ingest.py --rebuild # Rebuild from scratch
    python scripts/ingest.py --stats  # Show vector store stats

Environment:
    Set OPENAI_API_KEY or OPENROUTER_API_KEY in .env for embeddings
"""

import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

# Load environment from .env file
load_dotenv()

DEFAULT_DATA_PATH = Path(__file__).parent.parent / "data" / "raw_docs"
DEFAULT_VECTORSTORE_PATH = Path(__file__).parent.parent / "vectorstore"


def load_json_documents(data_path: Path) -> list[str]:
    """Load and parse insurance knowledge JSON."""
    knowledge_file = data_path / "insurance_knowledge.json"
    
    if not knowledge_file.exists():
        raise FileNotFoundError(f"Knowledge file not found: {knowledge_file}")
    
    with open(knowledge_file, "r") as f:
        data = json.load(f)
    
    documents = []
    
    # Process policies
    for policy in data.get("policies", []):
        doc = f"Policy: {policy['name']}\n\n"
        doc += f"Description: {policy['description']}\n\n"
        doc += f"Benefits: {', '.join(policy['benefits'])}\n\n"
        doc += f"Eligibility: {', '.join(policy['eligibility'])}\n\n"
        doc += f"Premium Factors: {', '.join(policy['premium_factors'])}"
        documents.append(doc)
    
    # Process claims info
    claims = data.get("claims", {})
    claims_doc = "Claims Process:\n\n"
    claims_doc += "Process Steps:\n" + "\n".join(f"  {step}" for step in claims.get("process", []))
    claims_doc += "\n\nRequired Documents:\n" + "\n".join(f"  - {doc}" for doc in claims.get("required_documents", []))
    claims_doc += "\n\nCommon Reasons for Denial:\n" + "\n".join(f"  - {reason}" for reason in claims.get("common_reasons_for_denial", []))
    documents.append(claims_doc)
    
    # Process FAQ
    faq = data.get("faq", {})
    faq_doc = "Frequently Asked Questions:\n\n"
    for question, answer in faq.items():
        faq_doc += f"Q: {question.replace('_', ' ').title()}\n"
        faq_doc += f"A: {answer}\n\n"
    documents.append(faq_doc)
    
    return documents


def create_vectorstore(
    documents: list[str],
    vectorstore_path: Path,
    embedding_model: str = "text-embedding-3-small",
) -> FAISS:
    """Create FAISS vector store from documents."""
    from app.core.config import get_settings
    
    settings = get_settings()
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""],
    )
    
    chunks = text_splitter.create_documents(documents)
    
    print(f"Created {len(chunks)} chunks from {len(documents)} documents")
    
    # Use OpenRouter API key if available, otherwise OpenAI
    api_key = settings.openrouter_api_key or settings.openai_api_key
    base_url = settings.openrouter_base_url if settings.llm_provider == "openrouter" else None
    
    embeddings = OpenAIEmbeddings(
        model=embedding_model,
        api_key=api_key,
        base_url=base_url,
    )
    
    vectorstore = FAISS.from_documents(chunks, embeddings)
    
    os.makedirs(vectorstore_path, exist_ok=True)
    vectorstore.save_local(str(vectorstore_path))
    
    print(f"Saved vector store to: {vectorstore_path}")
    
    return vectorstore


def load_vectorstore(vectorstore_path: Path, embedding_model: str = "text-embedding-3-small") -> FAISS:
    """Load existing vector store."""
    from app.core.config import get_settings
    
    if not vectorstore_path.exists():
        raise FileNotFoundError(f"Vector store not found: {vectorstore_path}")
    
    settings = get_settings()
    api_key = settings.openrouter_api_key or settings.openai_api_key
    base_url = settings.openrouter_base_url if settings.llm_provider == "openrouter" else None
    
    embeddings = OpenAIEmbeddings(
        model=embedding_model,
        api_key=api_key,
        base_url=base_url,
    )
    return FAISS.load_local(
        str(vectorstore_path),
        embeddings,
        allow_dangerous_deserialization=True,
    )


def get_vectorstore_stats(vectorstore: FAISS) -> dict:
    """Get statistics about the vector store."""
    return {
        "total_documents": vectorstore.index.ntotal,
        "dimension": vectorstore.index.d,
    }


def main():
    parser = argparse.ArgumentParser(description="RAG Ingestion Script")
    parser.add_argument("--rebuild", action="store_true", help="Rebuild vector store from scratch")
    parser.add_argument("--stats", action="store_true", help="Show vector store statistics")
    parser.add_argument("--data-path", type=Path, default=DEFAULT_DATA_PATH, help="Path to raw data")
    parser.add_argument("--vectorstore-path", type=Path, default=DEFAULT_VECTORSTORE_PATH, help="Path to vector store")
    parser.add_argument("--embedding-model", type=str, default="text-embedding-3-small", help="Embedding model")
    
    args = parser.parse_args()
    
    # Stats mode
    if args.stats:
        try:
            vectorstore = load_vectorstore(args.vectorstore_path, args.embedding_model)
            stats = get_vectorstore_stats(vectorstore)
            print(f"Vector Store Statistics:")
            print(f"  Total documents: {stats['total_documents']}")
            print(f"  Embedding dimension: {stats['dimension']}")
        except FileNotFoundError as e:
            print(f"Error: {e}")
            print("Run ingestion first: python scripts/ingest.py")
        return
    
    # Check if vectorstore exists
    if args.vectorstore_path.exists() and not args.rebuild:
        response = input(f"Vector store exists at {args.vectorstore_path}. Rebuild? [y/N]: ")
        if response.lower() != "y":
            print("Aborted.")
            return
    
    # Load documents
    print(f"Loading documents from: {args.data_path}")
    documents = load_json_documents(args.data_path)
    print(f"Loaded {len(documents)} documents")
    
    # Create vectorstore
    print(f"Creating vector store with model: {args.embedding_model}")
    vectorstore = create_vectorstore(
        documents,
        args.vectorstore_path,
        args.embedding_model,
    )
    
    # Show stats
    stats = get_vectorstore_stats(vectorstore)
    print(f"\nVector store created successfully!")
    print(f"  Documents: {stats['total_documents']}")
    print(f"  Dimension: {stats['dimension']}")


if __name__ == "__main__":
    main()