import hashlib
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

class VectorEmbeddings:
    
    def __init__(self):
        self.client = chromadb.Client(
            Settings(
                chroma_db_impl = "duckdb+parquet",
                persist_directory="./backend/database"
            )
        )

        # Load Embedding Model i.e SentenceTransformer
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    def generate_uid_for_document(self, content):
        """
        Generate Unique Identifier for each document
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def embedding_creation(self, content, collection_name="researchIQ"):
        """
        Create Embedding for the input text.
        Checks for duplicacy of the file and act based on that
        """

        ## Generate UID
        uid = self.generate_uid_for_document(content)

        ## Load if exist or create the collection
        collection = self.client.get_or_create_collection(name=collection_name)

        ## Check if the UID exists
        existing = collection.query(ids=[uid], n_results=1)
        if existing['ids']:
            print(f"Document Already Exists")
            return existing['metadata'][0] ## # Return metadata of existing document
        
        ## If doesn't exist create the embedding
        embedding = self.embedding_model.encode(content, convert_to_tensor=False).tolist()

        # Add the document to the collection
        metadata = {"uid" : uid, "description" : "process document"}
        collection.add(
            documents=[content],
            metadatas=[metadata],
            ids=[uid],
            embeddings=[embedding]   
        )

        return metadata