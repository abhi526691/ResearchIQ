from .utils import AdobeFunc


class data_pipeline:

    def __init__(self):
        pass

    def text_extraction_pipeline(self, file):
        zip_file_path = AdobeFunc().adobe_process(file)
        json_data = AdobeFunc().extract_json_from_zip(zip_file_path)
        text_list = AdobeFunc().extract_information_from_json(json_data)
        return text_list

