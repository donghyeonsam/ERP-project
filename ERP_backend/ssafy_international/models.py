from django.db import models
from employees.models import Employee

# Create your models here.
class Category(models.Model):

    categoryid = models.AutoField(primary_key=True)
    categoryname = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    picture = models.ImageField(blank=True, null=True)
    
    class Meta: db_table = "category"


class Supplier(models.Model):

    supplierid = models.AutoField(primary_key=True)
    companyname = models.CharField(max_length=100)
    contactname = models.CharField(max_length=100, blank=True, null=True)
    contacttitle = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    postalcode = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=60, blank=True, null=True)
    phone = models.CharField(max_length=40)
    fax = models.CharField(max_length=60, blank=True, null=True)
    homepage = models.TextField(max_length=100, blank=True, null=True)

    class Meta: db_table = "supplier"


class Customer(models.Model):

    customerid = models.CharField(primary_key=True, max_length=10)
    companyname = models.CharField(max_length=100)
    contactname = models.CharField(max_length=100, blank=True, null=True)
    contacttitle = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    postalcode = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=60, blank=True, null=True)
    phone = models.CharField(max_length=40)
    fax = models.CharField(max_length=60, blank=True, null=True)
    
    class Meta: db_table = "customer"


class Shipper(models.Model):
    
    shipperid = models.AutoField(primary_key=True)
    companyname = models.CharField(max_length=100)
    phone = models.CharField(max_length=40)

    class Meta: db_table = "shipper"


class Region(models.Model):
    
    regionid = models.AutoField(primary_key=True)
    regiondescription = models.CharField(max_length=200)

    class Meta: db_table = "region"


class Territory(models.Model):
    
    territoryid = models.CharField(primary_key=True, max_length=20)
    territorydescription = models.CharField(max_length=200)
    regionid = models.ForeignKey(Region, on_delete=models.PROTECT, db_column='regionid', related_name='territories')

    class Meta: db_table = "territory"


class Product(models.Model):
    
    productid = models.AutoField(primary_key=True)
    productname = models.CharField(max_length=100)
    supplierid = models.ForeignKey(Supplier, on_delete=models.PROTECT, db_column='supplierid', related_name='products')
    categoryid = models.ForeignKey(Category, on_delete=models.PROTECT, db_column='categoryid', related_name='products')
    quantityperunit = models.CharField(max_length=100, blank=True, null=True)
    unitprice = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unitsinstock = models.IntegerField(default=0)
    unitsonorder = models.IntegerField(default=0)
    reorderlevel = models.IntegerField(default=0)
    discontinued = models.CharField(max_length=1, default="0")

    class Meta: db_table = "product"


class Order(models.Model):
    
    orderid = models.AutoField(primary_key=True)
    customerid = models.ForeignKey(Customer, on_delete=models.PROTECT, db_column='customerid', related_name='orders')
    employeeid = models.ForeignKey(Employee, on_delete=models.PROTECT, db_column='employeeid', related_name='orders')
    orderdate = models.DateTimeField(null=True)
    requireddate = models.DateTimeField(null=True)
    shippeddate = models.DateTimeField(blank=True, null=True)
    shipvia = models.ForeignKey(Shipper, on_delete=models.SET_NULL, null=True, db_column='shipvia', related_name='orders')
    freight = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipname = models.CharField(max_length=120, blank=True, null=True)
    shipaddress = models.CharField(max_length=200, blank=True, null=True)
    shipcity = models.CharField(max_length=60,  blank=True, null=True)
    shipregion = models.CharField(max_length=60,  blank=True, null=True)
    shippostalcode = models.CharField(max_length=20,  blank=True, null=True)
    shipcountry = models.CharField(max_length=60,  blank=True, null=True)

    class Meta: db_table = "order"


class Orderdetail(models.Model):
    
    id = models.AutoField(primary_key=True)
    orderid = models.ForeignKey(Order, on_delete=models.CASCADE, db_column='orderid', related_name='orderdetails')
    productid = models.ForeignKey(Product, on_delete=models.PROTECT, db_column='productid', related_name='orderdetails')
    unitprice = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.IntegerField()
    discount = models.FloatField(default=0)

    class Meta: db_table = "orderdetail"