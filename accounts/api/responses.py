from django.http import JsonResponse

def errorResponse(message = "Неизвестная ошибка"):
    return JsonResponse({"success":False,"message":message,"result":{}})

def successResponse(result = {}):
    return JsonResponse({"success":True,"message":"","result":result})
