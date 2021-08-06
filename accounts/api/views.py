from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib import auth
from django.core.exceptions import ObjectDoesNotExist
from json import loads
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt
from accounts.models import CustomUser, Transaction, CustomApplication, CustomUserFields
from . serializers import CustomUserSerializer, CustomUserFieldsSerializer, TransactionSerializer
from . responses import errorResponse, successResponse

# Create your views here.

@csrf_exempt
def authenticate(request):
    if request.method == 'POST':
        data = loads(request.body)
        username = data['email']
        password = data['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            if user.is_active == True:
                try:
                    token = Token.objects.get(user = user)
                except ObjectDoesNotExist:
                    token = Token.objects.create(user=user)
                return successResponse(token.key)
            else:
                return errorResponse("User is not active")
        else:
            return errorResponse("Wrong login or password")
    return errorResponse("This need `username`,`password`")



@api_view(['GET'])
def getMyBalance(request):
    if request.method == 'GET':
        user = CustomUser.objects.get(id=request.user.id)
        serialized_user = CustomUserSerializer(user)
        response = {"balance": serialized_user.data['balance']}
        return successResponse(response)
    return errorResponse("Method is not allowed")


@csrf_exempt
def getField(request):
    if request.method == 'POST':
        data = loads(request.body)
        key = data['key']
        field = data['field']
        response = {}
        try:
            user = Token.objects.get(key=key).user
            try:
                custom_field = user.customuserfields_set.get(name=field)
                ser_custom_field = CustomUserFieldsSerializer(custom_field)
                field_name = ser_custom_field.data["name"]
                field_value = ser_custom_field.data["value"]
                response = {field_name: field_value}
                return successResponse(response)
            except:
                message = "Requested field does not exist"
                return errorResponse(message)
        except:
            message = "This key is invalid"
            return errorResponse(message)
    return errorResponse("Metod is not allowed")


@csrf_exempt
def setField(request):
    if request.method == 'POST':
        data = loads(request.body)
        field = data['field']
        value = data['value']
        key = data['key']
        response = {}
        try:
            user = Token.objects.get(key=key).user
            try:
                custom_user_field = user.customuserfields_set.get(name=field)
                custom_user_field.value = value
                custom_user_field.save()
                ser_custom_field = CustomUserFieldsSerializer(custom_user_field)
                response = {ser_custom_field.data['name']: ser_custom_field.data['value']}
                return successResponse(response)
            except:
                message = "Requested field does not exist"
                return errorResponse(message)
        except:
            message = "This key is invalid"
            return errorResponse(message)
    return errorResponse("Metod is not allowed")


@csrf_exempt
def getTransactions(request):
    if request.method == 'POST':
        data = loads(request.body)
        key = data['key']
        response = {}
        try:
            user = Token.objects.get(key=key).user
            transactions = user.user_transaction.all()
            ser_transaction = TransactionSerializer(transactions, many=True).data
            response = {"transactions": ser_transaction}
            return successResponse(response)
        except:
            message = "This key is invalid"
            return errorResponse(message)
    return errorResponse("Metod is not allowed")


@csrf_exempt
def setTransaction(request):
    if request.method == 'POST':
        data = loads(request.body)
        key = data['key']
        response = {}
        try:
            transaction = data['transaction']
            user = Token.objects.get(key=key).user
            value = transaction['value']
            new_transaction = Transaction.objects.create(user=user, value=value)
            if "application" in transaction:
                app = CustomApplication.objects.get(name=transaction['application'])
                new_transaction.application = app
            if "custom_field" in transaction:
                cus = CustomUserFields.objects.get(name=transaction['custom_field'])
                new_transaction.custom_field = cus
            if "parentTransaction" in transaction:
                try:
                    parent = Transaction.objects.get(id=transaction['parentTransaction'])
                    new_transaction.parentTransaction = parent
                except:
                    message = "Parent transaction not found"
                    return errorResponse(message)
            if "comment" in transaction:
                new_transaction.comment = transaction['comment']
            if "archival" in transaction:
                new_transaction.archival = loads(transaction['archival'].lower())
            if "type" in transaction:
                new_transaction.type = int(transaction['type'])
            if "paymentType" in transaction:
                new_transaction.paymentType = int(transaction['paymentType'])
            new_transaction.save()

            balance = float(user.balance) + float(new_transaction.value)
            user.balance = balance
            user.save()
            serialized_user = CustomUserSerializer(user).data
            response = {serialized_user['email']: serialized_user['balance']}
            return successResponse(response)
        except:
            message = "This key is invalid"
            return errorResponse(message)

    return errorResponse("Metod is not allowed")
