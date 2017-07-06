from django.http import HttpResponse
from QnA_maker_connector import *
def query(request):
    q = request.GET.get('q','')
    res = process_question(q,request)
    return HttpResponse(res)