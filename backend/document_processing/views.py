from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .processing_pipeline import data_pipeline
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST


class InformationExtractor(APIView):

    def __init__(self):
        pass

    def post(self, request):
        try:
            file = request.FILES['uploaded_file']
            if file:
                output = data_pipeline().preprocessed_data(file)
                return Response({
                    'output': output,
                    'status': HTTP_200_OK
                })
            else:
                return Response({
                    'status': HTTP_204_NO_CONTENT
                })
        except:
            return Response({
                'status': HTTP_400_BAD_REQUEST
            })

