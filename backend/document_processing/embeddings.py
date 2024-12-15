import hashlib
import os
import chromadb
from groq import Groq
from chromadb.config import Settings
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer


class VectorEmbeddings:

    def __init__(self):
        self.client = chromadb.PersistentClient(path="./backend/database")
        # Load Embedding Model i.e SentenceTransformer
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    def flatten_json(self, json_obj, parent_key='', sep='_'):
        """
        Flatten nested JSON into a single-level dictionary.
        """
        items = []
        for k, v in json_obj.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self.flatten_json(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    if isinstance(item, dict):
                        items.extend(self.flatten_json(
                            item, f"{new_key}_{i}", sep=sep).items())
                    else:
                        items.append((f"{new_key}_{i}", item))
            else:
                items.append((new_key, v))
        return dict(items)

    def generate_uid_for_document(self, content):
        """
        Generate Unique Identifier for each document
        """
        return hashlib.sha256(str(content).encode('utf-8')).hexdigest()

    def embedding_creation(self, contents, file_hash, collection_name="researchIQ"):
        """
        Process JSON data to generate embeddings and store in ChromaDB.
        If the document UID exists, return the existing data; otherwise, create embeddings and store.
        """
        # # Generate a unique UID for the entire document
        # document_uid = self.generate_uid_for_document(contents)
        # print(f"Processing document with UID: {document_uid}")

        # Load or create collection
        collection = self.client.get_or_create_collection(name=collection_name)

        # Flatten the JSON structure
        flat_data = self.flatten_json(contents)
        output_data = {}
        output_data['document_uid'] = file_hash

        for idx, (key, value) in enumerate(flat_data.items()):
            # Generate unique ID for each key-value pair within the document
            content_uid = f"{file_hash}_content{idx + 1}"

            # Combine key and value as input for embedding
            content = f"{key}: {value}"

            # Generate embedding
            embedding = self.embedding_model.encode(
                content, convert_to_tensor=False).tolist()

            # Store in ChromaDB
            collection.upsert(
                documents=[content],  # Document text (key-value pair)
                metadatas=[{
                    "document_uid": file_hash,  # Link key-value pair to document UID
                    "key": key,
                    "value": value
                }],  # Metadata for the pair
                ids=[content_uid],  # Unique ID for key-value pair
                embeddings=[embedding]  # Vector embedding
            )

            output_data[content_uid] = [
                {"content": content, "embedding": embedding}
            ]
            print(f"Stored {content_uid} with content: {content}")

        print(f"Embeddings created and stored for document UID: {
              file_hash}")
        return output_data

    def retrieve_data(self, file_hash, collection_name="researchIQ"):
        # Load or create collection
        collection = self.client.get_or_create_collection(name=collection_name)

        # Check if entries with the same document UID already exist
        results = collection.get(
            where={"document_uid": file_hash},
            include=["documents", "metadatas", "embeddings"]
        )

        if results and results["ids"]:  # If data exists, return it
            print(f"Document with UID: {
                  file_hash} already exists. Returning existing data...")
            for idx, doc_id in enumerate(results["ids"]):
                print(f"UID: {doc_id}")
                print(f"Content: {results['documents'][idx]}")
                print(f"Metadata: {results['metadatas'][idx]}")
                print("-" * 40)
            results["document_uid"] = file_hash
            return results  # Return all associated entries
        else:
            return False


class QnaHelper(VectorEmbeddings):
    def __init__(self):
        super().__init__()
        os.environ["GROQ_API_KEY"] = "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"
        self.llm = Groq()
        self.LLAMA3_70B_INSTRUCT = "llama-3.1-70b-versatile"
        self.LLAMA3_8B_INSTRUCT = "llama3.1-8b-instant"
        self.DEFAULT_MODEL = self.LLAMA3_70B_INSTRUCT

    def question_embedding(self, question):
        """Generate embedding for the given question."""
        return self.embedding_model.encode(
            question, convert_to_tensor=False
        ).tolist()

    def retrieve_data(self, question, file_hash, collection_name="researchIQ", top_k=5):
        """Retrieve top_k relevant data based on the file_hash and return query and prompt as a dictionary."""
        # Load or create collection
        collection = self.client.get_or_create_collection(name=collection_name)

        # Fetch all entries matching the document UID
        results = collection.get(
            where={"document_uid": file_hash},
            include=["documents", "metadatas", "embeddings"]
        )

        if results and results["ids"]:  # If data exists, rank and return top_k
            print(f"Document with UID: {file_hash} found. Returning top {
                  top_k} associated data...")

            # Combine embeddings and documents to calculate relevance scores
            question_emb = self.question_embedding(question)
            scored_results = []

            for idx, embedding in enumerate(results["embeddings"]):
                score = self.calculate_similarity(question_emb, embedding)
                scored_results.append((score, results['documents'][idx]))

            # Sort by scores in descending order and retrieve top_k
            scored_results = sorted(
                scored_results, key=lambda x: x[0], reverse=True)[:top_k]
            top_documents = [doc for _, doc in scored_results]

            # Combine top_k document data into a single string
            prompt = " ".join(top_documents)

            # Create and return the dictionary
            return {"prompt": prompt, 'scored_results': scored_results, 'top_document': top_documents}
        else:
            print(f"No data found for UID: {file_hash}")
            return None

    def generate_response(self, question, file_hash, collection_name="researchIQ", top_k=5):
        """Generate a response for the given question using the top_k relevant content from file_hash."""
        # Retrieve data
        data = self.retrieve_data(question, file_hash, collection_name, top_k)

        if not data:
            return None

        prompt = data["prompt"]
        scored_result = data["scored_results"]
        top_document = data["top_document"]

        # Combine prompt and question into a single role
        combined_prompt = f"""{prompt}
        Q: {question}
        A:"""

        # Generate response
        try:
            response = self.llm.chat.completions.create(
                messages=[{"role": "user", "content": combined_prompt}],
                model=self.DEFAULT_MODEL,
                temperature=0.6,
                top_p=0.9,
            )

            return {
                'output': response.choices[0].message.content,
                'prompt': prompt,
                'scored_result': scored_result,
                'top_document': top_document
            }
        except Exception as e:
            print(f"Error generating response: {e}")
            return None

    def calculate_similarity(self, query_emb, doc_emb):
        """Calculate cosine similarity between query and document embeddings."""
        # Ensure inputs are NumPy arrays
        query_emb = np.array(query_emb)
        doc_emb = np.array(doc_emb)

        # Reshape to 2D arrays if needed
        query_emb = query_emb.reshape(
            1, -1) if query_emb.ndim == 1 else query_emb
        doc_emb = doc_emb.reshape(1, -1) if doc_emb.ndim == 1 else doc_emb

        # Compute cosine similarity
        # Extract scalar similarity value
        return cosine_similarity(query_emb, doc_emb)[0][0]
