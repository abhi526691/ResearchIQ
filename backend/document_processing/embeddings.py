import time
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
        self.client = chromadb.PersistentClient(path="database")
        # Load Embedding Model i.e SentenceTransformer
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    def flatten_values_to_string(self, data):
        """
        Convert all values in a dictionary (including nested structures) into a single flattened string.

        Parameters:
        - data (dict): The input dictionary with possibly nested or multiple items.

        Returns:
        - dict: A dictionary where values are flattened into strings.
        """
        result = {}

        def process_value(value):
            if isinstance(value, dict):
                # Convert dictionary to a single string by joining key-value pairs
                return "; ".join(f"{k}: {process_value(v)}" for k, v in value.items())
            elif isinstance(value, list):
                # Convert list to a single string by joining items
                return ", ".join(process_value(v) for v in value)
            else:
                # Return the value as a string
                return str(value)

        for key, value in data.items():
            result[key] = process_value(value)

        return result

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
        flat_data = self.flatten_values_to_string(contents)
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
                {"key": key, "value": value, "embedding": embedding}
            ]

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
            for idx, doc_id in enumerate(results["ids"]):
                print(f"UID: {doc_id}")
                # print(f"Content: {results['documents'][idx]}")
                # print(f"Metadata: {results['metadatas'][idx]}")
                # print("-" * 40)
            results["document_uid"] = file_hash
            return results  # Return all associated entries
        else:
            return False


class QnaHelper(VectorEmbeddings):
    def __init__(self):
        super().__init__()
        os.environ["GROQ_API_KEY"] = os.environ.get("GROQ_API_KEY")
        self.llm = Groq()
        self.LLAMA3_70B_INSTRUCT = "llama-3.1-70b-versatile"
        self.LLAMA3_8B_INSTRUCT = "llama3.1-8b-instant"
        self.DEFAULT_MODEL = self.LLAMA3_70B_INSTRUCT
        self.max_token = 5000

    def truncate_to_fit(self, content):
        """
        Limit for llama 70b is 6000 token 
        1 token = 4 word
        """
        if len(content) > 20000:
            return content[:20000]
        return content

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

        prompt = self.truncate_to_fit(data["prompt"])
        scored_result = data["scored_results"]
        top_document = data["top_document"]

        # Combine prompt and question into a single role
        combined_prompt = f"""
            You are an AI assistant that answers questions based only on the following documents.
            Do not use any external information and do not return Irrelevant Information.
            {prompt}
        Q: {question}
        A:"""

        # Generate response
        try:
            response = self.llm.chat.completions.create(
                messages=[{"role": "user", "content": combined_prompt}],
                model=self.DEFAULT_MODEL,
                temperature=0.6,
                top_p=0.9,
                max_tokens=4096
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


class summmarizerHelper(QnaHelper):

    def __init__(self, document_uid=""):
        super().__init__()
        self.document_uid = document_uid

    def retrieve_data(self, collection_name="researchIQ"):
        """Retrieve top_k relevant data based on the file_hash and return query and prompt as a dictionary."""
        # Load or create collection
        collection = self.client.get_or_create_collection(name=collection_name)

        # Fetch all entries matching the document UID
        results = collection.get(
            where={"document_uid": self.document_uid},
            include=["documents", "metadatas", "embeddings"]
        )
        return results["metadatas"]

    def retrieve_all_heading(self, collection_name="researchIQ"):
        """Retrieve top_k relevant data based on the file_hash and return query and prompt as a dictionary."""
        # Load or create collection
        collection = self.client.get_or_create_collection(name=collection_name)

        # Fetch all entries matching the document UID
        results = collection.get(
            where={"document_uid": self.document_uid},
            include=["documents", "metadatas", "embeddings"]
        )
        return results["metadatas"]

    def check_token_size(self, next_output):
        if len(next_output) > 15000:
            return True
        return False

    def token_wise_summary(self):
        summary_prompt = ""
        prompt = self.retrieve_data()
        output, next_output = "", ""
        cnt = 0
        for i in prompt:
            output = next_output
            next_output += i['key'] + " " + i['value'] + " "
            if self.check_token_size(next_output):
                summary_prompt += self.generate_response(output)[
                    "output"] + " "
                print("summary_prompt", summary_prompt)
                output = ""
                cnt += 1

        summary_prompt += self.generate_response(output)["output"] + " "
        return cnt, summary_prompt

    def llm_response(self, combined_prompt):
        if len(combined_prompt) > 20000:
            combined_prompt = combined_prompt[:20000]
        response = self.llm.chat.completions.create(
            messages=[{"role": "user", "content": combined_prompt}],
            model=self.DEFAULT_MODEL,
            temperature=0.8,
            top_p=0.9,
        )

        return {
            'output': response.choices[0].message.content,
            'prompt': combined_prompt,
        }

    def generate_response(self, prompt=""):
        if prompt == "":
            prompt = self.retrieve_data()

        combined_prompt = f"""
        You are an AI assistant specialized in creating concise and accurate summaries based exclusively on
        the provided documents. Do not use any external information or personal knowledge beyond what is given below.
        {prompt}
        ### Task:
        Please provide a comprehensive summary of the above documents.
        Ensure that the summary captures all key points, main ideas, and essential details without introducing any information not present in the documents.
        Strictly limit the summary under 150 words and a single paragraph.

        ### Summary:
        """
        try:
            return self.llm_response(combined_prompt)
        except Exception as e:
            print("sleeping for 60 seconds")
            time.sleep(60)
            return self.llm_response(combined_prompt)

    def document_summary(self):
        cnt, summary_prompt = self.token_wise_summary()
        if cnt > 0:
            combined_prompt = f"""
            You are an AI assistant specialized in creating concise and accurate summaries based exclusively on
            the provided documents. Do not use any external information or personal knowledge beyond what is given below.
            {summary_prompt}
            ### Task:
            Please provide a comprehensive summary of the above documents.
            Ensure that the summary captures all key points, main ideas, and essential details without introducing any information not present in the documents.
            Strictly limit the summary to 2-3 paragraph depending on the prompt.

            ### Summary:
            """
            try:
                return self.llm_response(combined_prompt)
            except Exception as e:
                return self.llm_response(combined_prompt)
        return {
            'output': summary_prompt
        }
