from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .pipeline import data_pipeline
from .embeddings import VectorEmbeddings, QnaHelper, summmarizerHelper
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST


class InformationExtractor(APIView):

    def __init__(self):
        pass

    def post(self, request):
        # try:
        file = request.FILES['uploaded_file']
        if file:
            output = data_pipeline().text_extraction_pipeline(file)
            # print(output['document_uid'])
            return Response({
                'output': output,
                'document_uid': output['document_uid'],
                'status': HTTP_200_OK
            })
        else:
            return Response({
                'status': HTTP_204_NO_CONTENT
            })
        # except:
        #     return Response({
        #         'status': HTTP_400_BAD_REQUEST
        #     })


class QnAView(APIView):
    def post(self, request):
        document_uid = request.POST['document_uid']
        question = request.POST['question']

        output = QnaHelper().generate_response(
            question=question, file_hash=document_uid)

        return Response({
            'output': output
        })


class SummarizerView(APIView):
    def post(self, request):
        document_uid = request.POST['document_uid']
        output = summmarizerHelper(document_uid).generate_response()
        return Response({
            'output': output
        })
