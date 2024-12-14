import hashlib
from io import BytesIO
from .utils import AdobeFunc
from .embeddings import VectorEmbeddings


class data_pipeline:

    def __init__(self):
        pass

    def generate_hash_for_file(self, file):
        """
        Generate a unique hash for the file content.
        """
        file.seek(0)  # Reset file pointer to the beginning
        file_content = file.read()  # Read the file content as bytes
        # Generate hash from bytes
        file_uid = hashlib.sha256(file_content).hexdigest()
        print(f"Generated file UID: {file_uid}")
        file.seek(0)  # Reset the original file pointer again
        return file_uid

    def text_extraction_pipeline(self, file):
        embeddings = VectorEmbeddings()
        adobe = AdobeFunc()

        file_hash = self.generate_hash_for_file(file)

        results = embeddings.retrieve_data(file_hash)
        if results:
            print("Already Exists")
            return results

        zip_file_path = adobe.adobe_process(file)
        json_data = adobe.extract_json_from_zip(zip_file_path)
        text_list = adobe.extract_information_from_json(json_data)
        # return VectorEmbeddings().fetch_document_data_by_content(file)

        return embeddings.embedding_creation(text_list, file_hash)
    


