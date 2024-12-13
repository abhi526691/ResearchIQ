from .utils import AdobeFunc, Preprocessing


class data_pipeline:

    def __init__(self):
        pass

    def text_extraction_pipeline(self, file):
        zip_file_path = AdobeFunc().adobe_process(file)
        json_data = AdobeFunc().extract_json_from_zip(zip_file_path)
        text_list = AdobeFunc().extract_information_from_json(json_data)
        return text_list

    def preprocess_pipeline(self, text):
        preprocessor = Preprocessing()
        methods = [method for method in dir(preprocessor) if callable(getattr(preprocessor, method))
                   and not method.startswith("__")]
        print(methods)

        # Apply each function to the text
        for method_name in methods:
            # Print the name of the current function being applied
            print(f"Applying function: {method_name}")
            text = getattr(preprocessor, method_name)(text)
        return text

    def preprocessed_data(self, file):
        text_list = self.text_extraction_pipeline(file)
        return [self.preprocess_pipeline(i) for i in text_list]
