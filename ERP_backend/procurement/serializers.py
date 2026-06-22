from rest_framework import serializers
from .models import ProductCost, PurchaseOrder, PurchaseOrderDetail, GoodsReceipt, Material, Bom, BomComponent

# =====================================================================
# 1. ProductCost (제품 원가 / 매입가) Serializer
# =====================================================================
class ProductCostSerializer(serializers.ModelSerializer):
    # 주 공급업체명을 프론트엔드에서 바로 보여줄 수 있도록 읽기 전용 필드 추가
    preferred_supplier_name = serializers.CharField(source='preferredsupplierid.companyname', read_only=True)
    product_name = serializers.CharField(source='productid.productname', read_only=True)

    class Meta:
        model = ProductCost
        fields = '__all__'


# =====================================================================
# 2. PurchaseOrder & Detail (구매 주문 마스터 및 상세) Serializer
# =====================================================================
class PurchaseOrderDetailSerializer(serializers.ModelSerializer):
    # 제품 코드가 아닌 제품명을 프론트엔드 화면(Vue)에 보여주기 위한 필드
    product_name = serializers.CharField(source='productid.productname', read_only=True)
    
    class Meta:
        model = PurchaseOrderDetail
        fields = '__all__'


class PurchaseOrderSerializer(serializers.ModelSerializer):
    # 중요: 주문 마스터 조회 시 하위 상세 내역(details)을 리스트로 묶어서 함께 포함시킴
    # models.py에서 설정한 related_name="details"와 변수명이 일치해야 합니다.
    details = PurchaseOrderDetailSerializer(many=True, read_only=True)
    
    # 가독성을 위한 마스터 정보 추가 필드
    supplier_name = serializers.CharField(source='supplierid.companyname', read_only=True)
    employee_name = serializers.CharField(source='employeeid.lastname', read_only=True) # 혹은 firstname과 조합

    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'supplierid', 'supplier_name', 'employeeid', 'employee_name',
            'orderdate', 'expecteddate', 'receiveddate', 'status', 'currency',
            'freight', 'totalamount', 'warehouse', 'details'
        ]


# =====================================================================
# 3. GoodsReceipt (상품 입고 / 수령증) Serializer
# =====================================================================
class GoodsReceiptSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='productid.productname', read_only=True)
    
    class Meta:
        model = GoodsReceipt
        fields = '__all__'


# =====================================================================
# 4. Material (원자재 마스터) Serializer
# =====================================================================
class MaterialSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplierid.companyname', read_only=True)

    class Meta:
        model = Material
        fields = '__all__'


# =====================================================================
# 5. Bom & Component (자재 명세서 마스터 및 구성품) Serializer
# =====================================================================
class BomComponentSerializer(serializers.ModelSerializer):
    # 자재 ID뿐만 아니라 자재 이름, 단위, 단가까지 한눈에 보여주도록 세팅
    material_name = serializers.CharField(source='materialid.materialname', read_only=True)
    material_unit = serializers.CharField(source='materialid.unit', read_only=True)
    material_unitcost = serializers.DecimalField(source='materialid.unitcost', max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = BomComponent
        fields = '__all__'


class BomSerializer(serializers.ModelSerializer):
    # 중요: BOM 레시피 조회 시 들어가는 하위 원자재 목록(components)을 통째로 포함시킴
    # models.py에서 설정한 related_name="components"와 변수명이 일치해야 합니다.
    components = BomComponentSerializer(many=True, read_only=True)

    class Meta:
        model = Bom
        fields = [
            'bomid', 'bomcode', 'productname', 'bomtype', 'basisquantity',
            'basisunit', 'revision', 'status', 'allergen', 'batchcost',
            'currency', 'components'
        ]