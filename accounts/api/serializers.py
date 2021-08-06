from rest_framework import serializers
from accounts.models import CustomUser, CustomUserFields, Transaction


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'balance', 'rating', 'phone_number']


class CustomUserFieldsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUserFields
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
