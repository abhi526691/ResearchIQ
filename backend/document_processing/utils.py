import os
import json
import zipfile
from datetime import datetime
from collections import defaultdict
import logging
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

    def extract_text(self, file):
        """
        Public method to process a PDF file and extract structured text information.

        Args:
            file (file-like object): The PDF file to be processed.

        Returns:
            dict: Structured data extracted from the PDF.
        """
        zip_file_path = self._adobe_process(file)
        json_data = self._extract_json_from_zip(zip_file_path)
        return self._extract_information_from_json(json_data)

    # Private Methods
    def _adobe_process(self, file):
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
            output_file_path = self._create_output_file_path()
            with open(output_file_path, "wb") as output_file:
                output_file.write(stream_asset.get_input_stream())

            return output_file_path

        except Exception as e:
            logging.exception(f"Error during Adobe PDF processing: {e}")
            raise

    def _create_output_file_path(self):
        """
        Generate a unique file path for the output ZIP file.

        Returns:
            str: The generated file path.
        """
        now = datetime.now()
        time_stamp = now.strftime("%Y-%m-%dT%H-%M-%S")
        os.makedirs("output/ExtractTextInfoFromPDF", exist_ok=True)
        return f"output/ExtractTextInfoFromPDF/extract{time_stamp}.zip"

    def _extract_json_from_zip(self, zip_file_path):
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

    def _extract_information_from_json(self, json_data):
        """
        Process JSON data to extract structured text information.

        Args:
            json_data (dict): The JSON data extracted from the ZIP file.

        Returns:
            dict: Structured data grouped by sections.
        """
        structured_data = defaultdict(list)

        for element in json_data.get("elements", []):
            section = (
                element.get("Path", "").split("/")[2]
                if "Path" in element and len(element.get("Path", "").split("/")) > 2
                else "General"
            )
            text = element.get("Text", "").strip()
            if text:
                structured_data[section].append(text)

        return structured_data
