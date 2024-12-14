from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .pipeline import data_pipeline
from .embeddings import VectorEmbeddings, QnaHelper
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


class QnA(APIView):
    def post(self, request):
        document_uid = request.POST['document_uid']
        question = request.POST['question']

        output = QnaHelper().generate_response(question=question, file_hash=document_uid)

        return Response({
            'output': output
        })
