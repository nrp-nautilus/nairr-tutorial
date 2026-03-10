# Milvus RAG with Qualcomm vLLM as the LLM backend.
# Run from a pod that can reach Milvus and the QAIC vLLM service (e.g. the Milvus RAG pod).
# Set OPENAI_API_BASE to the QAIC server, e.g. http://qaic-vllm-server:8000/v1
# Milvus connection uses MILVUS_HOST, MILVUS_PORT, MILVUS_USER, MILVUS_PASSWORD, MILVUS_DB_NAME, MILVUS_SECURE from env.
import os
from langchain_community.vectorstores import Milvus
from langchain_community.embeddings import SentenceTransformerEmbeddings
from openai import OpenAI

MILVUS_HOST = os.getenv("MILVUS_HOST", "milvus.nrp-nautilus.io")
MILVUS_PORT = os.getenv("MILVUS_PORT", "50051")
MILVUS_USER = os.getenv("MILVUS_USER", "")
MILVUS_PASSWORD = os.getenv("MILVUS_PASSWORD", "")
MILVUS_SECURE = os.getenv("MILVUS_SECURE", "true").lower() == "true"
MILVUS_DB_NAME = os.getenv("MILVUS_DB_NAME", "nrp_training_k8s")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "http://qaic-vllm-server:8000/v1")
COLLECTION_NAME = "simple_rag_example"

sample_documents = [
    "Pigeons are fed a diet of grains including wheat, corn, and peas. Never feed pigeons a full ration during the settling period.",
    "Tame pigeons typically have better plumage than wild pigeons because they receive better nutrition and care.",
    "Pigeon plumage is affected by diet, genetics, age, and environmental conditions. Proper nutrition is essential for healthy feathers.",
    "Pigeons are intelligent birds that can recognize themselves in mirrors and navigate using the Earth's magnetic field.",
    "The common pigeon, also known as the rock dove, is found in cities worldwide and has adapted well to urban environments.",
]

print("Step 1: Loading embedding model...")
embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
print("✓ Embedding model loaded\n")

print("Step 2: Connecting to Milvus and storing documents...")
connection_args = {
    "host": MILVUS_HOST,
    "port": MILVUS_PORT,
    "user": MILVUS_USER,
    "password": MILVUS_PASSWORD,
    "secure": MILVUS_SECURE,
    "db_name": MILVUS_DB_NAME,
}
try:
    db = Milvus.from_texts(
        texts=sample_documents,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        connection_args=connection_args,
    )
    print(f"✓ Stored {len(sample_documents)} documents in Milvus\n")
except Exception as e:
    if "already exists" in str(e).lower():
        print(f"✓ Collection already exists, connecting...")
        db = Milvus(
            embedding_function=embeddings,
            collection_name=COLLECTION_NAME,
            connection_args=connection_args,
        )
        print("✓ Connected to existing collection\n")
    else:
        raise

print("Step 3: Testing document retrieval...")
query = "What do you feed pigeons?"
retriever = db.as_retriever(search_kwargs={"k": 2})
relevant_docs = retriever.invoke(query)
print(f"✓ Retrieved {len(relevant_docs)} relevant documents")
for i, doc in enumerate(relevant_docs, 1):
    print(f"  Doc {i}: {doc.page_content[:80]}...")
print()

print("Step 4: Setting up LLM (Qualcomm vLLM)...")
client = OpenAI(base_url=OPENAI_API_BASE, api_key="dummy")
print("✓ LLM ready\n")

print("Step 5: RAG Query - Generating answer from retrieved context...")
print(f"Query: {query}")
print("-" * 60)
context = "\n\n".join([doc.page_content for doc in relevant_docs])
prompt = f"""Based on the following context, answer the question briefly and concisely.

Context:
{context}

Question: {query}

Answer:"""

try:
    resp = client.chat.completions.create(
        model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=80,
    )
    answer = resp.choices[0].message.content
    print(f"\nAnswer: {answer}\n")
except Exception as e:
    print(f"\n✗ Failed: {type(e).__name__}: {e}\n")
    print("Ensure the QAIC vLLM server pod is running and reachable at", OPENAI_API_BASE)
