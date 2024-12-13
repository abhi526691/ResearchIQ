import os
import json
import re
import emoji
import zipfile
from datetime import datetime
from collections import defaultdict
import logging

from supporting_docs.slang_dict import abbreviations

import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet, stopwords

from adobe.pdfservices.operation.auth.service_principal_credentials import ServicePrincipalCredentials
from adobe.pdfservices.operation.pdf_services_media_type import PDFServicesMediaType
from adobe.pdfservices.operation.io.cloud_asset import CloudAsset
from adobe.pdfservices.operation.io.stream_asset import StreamAsset
from adobe.pdfservices.operation.pdf_services import PDFServices
from adobe.pdfservices.operation.pdfjobs.jobs.extract_pdf_job import ExtractPDFJob
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_element_type import ExtractElementType
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_pdf_params import ExtractPDFParams
from adobe.pdfservices.operation.pdfjobs.result.extract_pdf_result import ExtractPDFResult


class AdobeFunc:
    """
    A class to interact with Adobe PDF Services for extracting text from PDFs and returning structured data.
    """

    def __init__(self):
        """
        Initialize AdobeFunc with Service Principal Credentials.
        """
        self.credentials = ServicePrincipalCredentials(
            client_id="b2d53a9ebdf3457c9935331406ea1dea",
            client_secret="p8e--ujIBIaRR663vvekvOGUYxUp2-f0zeKn"
        )


    def adobe_process(self, file):
        """
        Process the PDF file using Adobe PDF Services and return the path of the resulting ZIP file.

        Args:
            file (file-like object): The PDF file to be processed.

        Returns:
            str: Path to the ZIP file containing the extracted data.
        """
        try:
            input_stream = file.read()
            file.close()

            pdf_services = PDFServices(credentials=self.credentials)

            # Upload the input PDF
            input_asset = pdf_services.upload(
                input_stream=input_stream, mime_type=PDFServicesMediaType.PDF
            )

            # Define parameters for extracting text
            extract_pdf_params = ExtractPDFParams(
                elements_to_extract=[ExtractElementType.TEXT]
            )

            # Create and submit the job
            extract_pdf_job = ExtractPDFJob(
                input_asset=input_asset, extract_pdf_params=extract_pdf_params
            )

            location = pdf_services.submit(extract_pdf_job)
            pdf_services_response = pdf_services.get_job_result(
                location, ExtractPDFResult
            )

            # Get the content from the resulting asset
            result_asset: CloudAsset = pdf_services_response.get_result().get_resource()
            stream_asset: StreamAsset = pdf_services.get_content(result_asset)

            # Save the ZIP file
            output_file_path = self.create_output_file_path()
            with open(output_file_path, "wb") as output_file:
                output_file.write(stream_asset.get_input_stream())

            return output_file_path

        except Exception as e:
            logging.exception(f"Error during Adobe PDF processing: {e}")
            raise

    def create_output_file_path(self):
        """
        Generate a unique file path for the output ZIP file.

        Returns:
            str: The generated file path.
        """
        now = datetime.now()
        time_stamp = now.strftime("%Y-%m-%dT%H-%M-%S")
        os.makedirs("output/ExtractTextInfoFromPDF", exist_ok=True)
        return f"output/ExtractTextInfoFromPDF/extract{time_stamp}.zip"

    def extract_json_from_zip(self, zip_file_path):
        """
        Extract JSON data from the ZIP file.

        Args:
            zip_file_path (str): Path to the ZIP file.

        Returns:
            dict: The extracted JSON data.
        """
        with zipfile.ZipFile(zip_file_path, 'r') as archive:
            with archive.open('structuredData.json') as json_entry:
                return json.load(json_entry)

    def extract_information_from_json(self, json_data):
        """
        Process JSON data to extract structured text information.

        Args:
            json_data (dict): The JSON data extracted from the ZIP file.

        Returns:
            dict: Structured data grouped by sections.
        """
        structured_data = []

        for element in json_data.get("elements", []):
            section = (
                element.get("Path", "").split("/")[2]
                if "Path" in element and len(element.get("Path", "").split("/")) > 2
                else "General"
            )
            text = element.get("Text", "").strip()

            if text:
                structured_data.append(text)

        return structured_data


class Preprocessing:
    """
    Pre-Processing
    - There are lots of things which we have to do to preprocess the text data
    - Handle Emojis, Slangs, Punctuations, ShortForm
    - Spelling Corrections
    - POS Tagging
    - Handling Pronouns and Special Characters
    - Tokenize
    - Lowercase and En-grams
    """
    def __init__(self):
        pass

    def convert_abbrev(self, word):
        final_word = []
        for i in word.split(" "):
            final_word.append(
                abbreviations[i.lower()] if i.lower() in abbreviations.keys() else i)
        return " ".join(final_word)

    def remove_urls(self, text):
        url_pattern = re.compile(r'https?://\S+|www\.\S+')
        return url_pattern.sub(r'', text)

    def remove_html(self, text):
        html_pattern = re.compile('<.*?>')
        return html_pattern.sub(r'', text)

    def remove_unnecessary_digits(self, text):
        pattern = r'\b\d+\b|(\d{4}-\d{2}-\d{2})|\b\d+\s*(?=\w)'

        # Remove matched patterns
        cleaned_text = re.sub(pattern, '', text)

        # Remove extra whitespace
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()

        return cleaned_text

    def lemmatize_text_nltk(self, text):
        lemmatizer = WordNetLemmatizer()
        words = nltk.word_tokenize(text)  # Tokenize the text
        lemmatized_words = [lemmatizer.lemmatize(word) for word in words]
        return ' '.join(lemmatized_words)

    def remove_stopwords(self, text):
        # Get the set of English stopwords
        stop_words = set(stopwords.words('english'))
        words = word_tokenize(text)  # Tokenize the text
        filtered_words = [
            word for word in words if word.lower() not in stop_words]
        return ' '.join(filtered_words)

    def cleaning_repeating_char(self, text):
        return re.sub(r'(.)\1+', r'\1', text)

    def cleaning_username(self, text):
        return re.sub('@[^\s]+', ' ', text)

    def handle_emoji(self, text):
        # Handling Emoji's
        return emoji.demojize(text)
