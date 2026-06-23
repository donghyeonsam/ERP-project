from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from .models import Employee, EmployeeTerritory


class EmployeeSerializer(serializers.ModelSerializer):

    reports_to_name = serializers.SerializerMethodField()

    role_level = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = '__all__'

    def get_reports_to_name(self, obj):
        if obj.reportsto:
            return f"{obj.reportsto.lastname}{obj.reportsto.firstname}"
        return None
    
    def get_role_level(self, obj):
        ROLE_LEVEL = {
            "대표이사": 5,
            "Vice President, Sales": 4,
            "Sales Manager": 3,
            "Inside Sales Coordinator": 2,
            "Sales Representative": 1,
        }
        return ROLE_LEVEL.get(obj.title, 0)


class EmployeeTerritorySerializer(serializers.ModelSerializer):

    class Meta:
        model = EmployeeTerritory
        fields = '__all__'


class EmployeeRegisterSerializer(RegisterSerializer):
    # 기본 필드(username, password1, password2)에 더해 사원번호를 추가로 받음
    employeeid = serializers.IntegerField(write_only=True)
    email = serializers.EmailField(required=False, allow_blank=True)
 
    def validate_employeeid(self, value):
        """사원번호 검증: 실제 존재 + 아직 미가입이어야 함"""
        try:
            employee = Employee.objects.get(pk=value)
        except Employee.DoesNotExist:
            raise serializers.ValidationError('존재하지 않는 사원번호입니다.')
 
        if employee.user_id is not None:
            raise serializers.ValidationError('이미 가입된 사원번호입니다.')
        return value
 
    def get_cleaned_data(self):
        # 부모가 모으는 데이터(username 등)에 employeeid 추가
        data = super().get_cleaned_data()
        data['employeeid'] = self.validated_data.get('employeeid')
        return data
 
    def custom_signup(self, request, user):
        """RegisterSerializer.save() 내부에서 User 생성 직후 호출되는 훅"""
        employee = Employee.objects.get(pk=self.validated_data['employeeid'])
        employee.user = user
        employee.save()