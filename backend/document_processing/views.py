from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .pipeline import data_pipeline
from .embeddings import VectorEmbeddings, QnaHelper, summmarizerHelper
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST


class InformationExtractor(APIView):
    def post(self, request):
        file = request.FILES.get('uploaded_file')
        if file and file.name.endswith('.pdf'):
            output = data_pipeline().text_extraction_pipeline(file)
            return Response({
                'output': output,
                'document_uid': output['document_uid'],
                'status': HTTP_200_OK
            })
        else:
            return Response({
                'status': HTTP_204_NO_CONTENT,
                'error': 'Uploaded file is not a PDF.'
            })

class QnAView(APIView):
    def post(self, request):
        document_uid = request.POST['document_uid']
        question = request.POST['question']

        output = QnaHelper().generate_response(
            question=question, file_hash=document_uid)

        return Response({
            'output': output
        })

class SummarizerHeadingView(APIView):
    def post(self, request):
        document_uid = request.POST['document_uid']
        key_value_pair = summmarizerHelper(document_uid).retrieve_all_heading()
        return Response({
            "output" : key_value_pair
        })

class TitleWiseSummary(APIView):
    def post(self, request):
        content = request.POST['content']
        title_summary = summmarizerHelper().generate_response(content)
        return Response({
            "output" : title_summary
        })
    
class SummarizerView(APIView):
    def post(self, request):
        document_uid = request.POST['document_uid']
        output = summmarizerHelper(document_uid).document_summary()
        return Response({
            'output': output
        })
