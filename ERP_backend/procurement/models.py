from django.db import models

# Create your models here.
class ProductCost(models.Model):
    # PK 이자 FK: 제품 1종당 1행 (OneToOne)
    productid = models.OneToOneField("ssafy_international.Product",on_delete=models.CASCADE,primary_key=True, db_column="productid",related_name="cost")
    unitcost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=8, default="KRW")
    leadtimedays = models.IntegerField(default=0)
    moq = models.IntegerField(default=0)
    safetystock = models.IntegerField(default=0)
    preferredsupplierid = models.ForeignKey("ssafy_international.Supplier",on_delete=models.PROTECT,db_column="preferredsupplierid",related_name="preferred_products")

    class Meta:
        db_table = "productcost"


class PurchaseOrder(models.Model):
    id = models.AutoField(primary_key=True)
    supplierid   = models.ForeignKey("ssafy_international.Supplier", on_delete=models.PROTECT, db_column="supplierid", related_name="purchaseorders")
    employeeid   = models.ForeignKey("employees.Employee", on_delete=models.SET_NULL, db_column="employeeid", related_name="purchaseorders", null=True, blank=True)
    orderdate    = models.DateField()
    expecteddate = models.DateField(blank=True, null=True)
    receiveddate = models.DateField(blank=True, null=True)         # 미입고 시 null
    status       = models.CharField(max_length=20)                # ordered / partial / received
    currency     = models.CharField(max_length=10, default="KRW")
    freight      = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    totalamount  = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    warehouse    = models.CharField(max_length=40, blank=True, null=True)

    class Meta:
        db_table = "purchaseorder"

    def __str__(self):
        return f"PO-{self.id} ({self.orderdate})"

class PurchaseOrderDetail(models.Model):
    id = models.AutoField(primary_key=True)
    purchaseorderid = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, db_column="purchaseorderid", related_name="details")
    productid       = models.ForeignKey("ssafy_international.Product", on_delete=models.PROTECT, db_column="productid", related_name="po_details")
    quantity        = models.IntegerField()
    unitcost        = models.DecimalField(max_digits=12, decimal_places=2)
    discount        = models.FloatField(default=0.00)
    linetotal       = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        db_table = "purchaseorderdetail"


class GoodsReceipt(models.Model):
    id               = models.AutoField(primary_key=True)
    purchaseorderid  = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, db_column="purchaseorderid", related_name="receipts")
    productid        = models.ForeignKey("ssafy_international.Product", on_delete=models.PROTECT, db_column="productid", related_name="receipts")
    receiptdate      = models.DateField()
    quantityordered  = models.IntegerField()
    quantityreceived = models.IntegerField()
    qcstatus         = models.CharField(max_length=20)             # pass / hold / reject
    warehouse        = models.CharField(max_length=40, blank=True, null=True)

    class Meta:
        db_table = "goodsreceipt"


class Material(models.Model):
    materialid   = models.CharField(primary_key=True, max_length=20)  
    materialname = models.CharField(max_length=120)
    materialtype = models.CharField(max_length=20)                     # 원재료 / 부자재
    unit         = models.CharField(max_length=10)
    unitcost     = models.DecimalField(max_digits=12, decimal_places=2)
    currency     = models.CharField(max_length=8, default="KRW")
    allergen     = models.CharField(max_length=60, blank=True, null=True)
    supplierid   = models.ForeignKey("ssafy_international.Supplier", on_delete=models.PROTECT, db_column="supplierid", related_name="materials")

    class Meta:
        db_table = "material"


class Bom(models.Model):
    bomid         = models.AutoField(primary_key=True)
    bomcode       = models.CharField(max_length=30)
    productname   = models.CharField(max_length=120)
    bomtype       = models.CharField(max_length=20)                   # 완제품 / 반제품
    basisquantity = models.DecimalField(max_digits=12, decimal_places=2)
    basisunit     = models.CharField(max_length=10)
    revision      = models.CharField(max_length=10)
    status        = models.CharField(max_length=20)                   # 활성 / 검토중 / 폐기
    allergen      = models.CharField(max_length=120, blank=True, null=True)
    batchcost     = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    currency      = models.CharField(max_length=8, default="KRW")

    class Meta:
        db_table = "bom"
    def __str__(self):
        return f"{self.productname} 레시피 ({self.bomid})"

class BomComponent(models.Model):
    id         = models.AutoField(primary_key=True)
    bomid      = models.ForeignKey(Bom, on_delete=models.CASCADE, db_column="bomid", related_name="components")
    materialid = models.ForeignKey(Material, on_delete=models.PROTECT, db_column="materialid", related_name="used_in")
    quantity   = models.DecimalField(max_digits=12, decimal_places=4)
    ratio      = models.FloatField(blank=True, null=True)             # 부자재는 배합비 null
    linecost   = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        db_table = "bomcomponent"
    