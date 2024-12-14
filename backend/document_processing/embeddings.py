import hashlib
import chromadb
from chromadb.config import Settings
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

    # def fetch_document_data_by_content(self, document_content, collection_name="researchIQ"):
    #     """
    #     Fetch all data associated with a document UID if the same file is uploaded.
    #     """
    #     try:
    #         # Generate UID for the given document content
    #         document_uid = self.generate_document_uid(document_content)
    #         print(f"Generated UID for the document: {document_uid}")

    #         # Load the collection
    #         collection = self.client.get_collection(name=collection_name)

    #         # Query data using the document UID
    #         results = collection.query(
    #             # Filter by document UID in metadata
    #             where={"document_uid": document_uid}
    #         )

    #         if results["ids"]:
    #             print(f"Found {len(results['ids'])} entries for document UID: {
    #                   document_uid}")
    #             for idx, doc_id in enumerate(results["ids"]):
    #                 print(f"UID: {doc_id}")
    #                 print(f"Content: {results['documents'][idx]}")
    #                 print(f"Metadata: {results['metadatas'][idx]}")
    #                 print("-" * 40)
    #             return results
    #         else:
    #             print(f"No data found for document UID: {document_uid}")
    #             return None

    #     except Exception as e:
    #         print(f"Error fetching data: {e}")
    #         return None
        


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
            return results  # Return all associated entries
        
        else:
            return False

        # If document does not exist, process and create embeddings
        print(f"No existing entries found for UID: {
              file_hash}. Creating embeddings...")
