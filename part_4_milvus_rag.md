# 4. Multi-Tenant Vector Databasing with Milvus for RAG and Fine-tuning with GPU/QAIC (Instructor: Mohammad Sada)

The tutorial focuses on NRP-managed Milvus as a multi-tenant vector database service.
Participants are guided through accessing Milvus with their credentials, defining collections, and inserting embeddings for semantic search. Using either GPU or QAIC resources, attendees will integrate Milvus into RAG or fine-tuning workflow, generating embeddings from large language models, storing them in Milvus, and performing fine-tuning with retrieval augmentation to enrich model outputs.

## RAG example using Milvus
### Credit: Mohammad Sada, SDSC

This example demonstrates RAG using Milvus as the vector database instead of ChromaDB. Milvus is a distributed vector database designed for scalable similarity search. In the milvus-rag.yaml file please change the username to a unique name for yourself.

Start up the pod:
```
kubectl apply -f milvus-rag.yaml
```
Watch the logs and make sure you wait till the installs are done:

```
kubectl logs vectordb-example-username
```
The pod automatically:
- Installs all Python dependencies
- Installs Ollama
- Starts Ollama server in the background
- Downloads the mistral model in the background

Download the simple example script into the pod once it is running:
```
kubectl exec -it vectordb-example-username -- /bin/bash
cd /scratch
wget https://raw.githubusercontent.com/groundsada/nrp-milvus-example/refs/heads/main/milvus-example.py
```

Once the installation is complete (check logs), you can run the example. \
**Note:** This example connects to the `sc25_milvus` database using credentials from the Kubernetes secret `sc25-milvus-credentials`. The collection name is `simple_rag_example`. You can change the name in the `milvus-example.py` file if you want to create a separate collection of your own. There are two places where the collection name is specified. Look for:

```
 collection_name="simple_rag_example"
```
For all other aspects, the script uses environment variables for Milvus connection, so no manual editing is needed.

```
kubectl exec -it vectordb-example-username -- /bin/bash
cd /scratch
python3 milvus-example.py
```

This simple example:
- Uses a small set of sample documents to demonstrate Milvus vector storage and retrieval
- Shows RAG with Ollama LLM


## End

**Please make sure you did not leave any running pods. Jobs and associated completed pods are OK.**
