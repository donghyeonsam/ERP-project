from rest_framework import serializers
from .models import (Category, Supplier, Customer,
                     Shipper, Region, Territory,
                     Product, Order, Orderdetail)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class ShipperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipper
        fields = '__all__'


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = '__all__'


class TerritorySerializer(serializers.ModelSerializer):

    region_name = serializers.CharField(
        source="regionid.regiondescription", read_only=True
    )

    class Meta:
        model = Territory
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):

    category_name = serializers.CharField(
        source="categoryid.categoryname", read_only=True
    )

    supplier_name = serializers.CharField(
        source="supplierid.companyname", read_only=True
    )

    class Meta:
        model = Product
        fields = '__all__'


class OrderdetailSerializer(serializers.ModelSerialzier):

    product_name = serializers.CharField(
        source="productid.productname", read_only=True
    )

    class Meta:
        model = Orderdetail
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):

    details = OrderdetailSerializer(many=True, read_only=True)

    customer_name = serializers.CharField(
        source="customerid.companyname", read_only=True
    )

    employee_name = serializers.SerializerMethodField()

    shipper_name = serializers.CharField(
        source="shipvia.companyname", read_only=True
    )

    class Meta:
        model = Order
        fields = '__all__'

    def get_employee_name(self, obj):

        emp = obj.employeeid
        if emp:
            return f"{emp.lastname}{emp.firstname}"
        return None