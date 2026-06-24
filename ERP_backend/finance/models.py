from django.db import models


class Budget(models.Model):
    id         = models.AutoField(primary_key=True)
    period     = models.CharField(max_length=7)          # 'YYYY-MM', Expense와 동일 기준
    costcenter = models.CharField(max_length=40)         # 부서 (Expense.costcenter와 매칭)
    category   = models.CharField(max_length=40)         # 비용 항목 (Expense.category와 매칭)
    amount     = models.DecimalField(max_digits=14, decimal_places=2)  # 편성 예산액
    currency   = models.CharField(max_length=8, default="KRW")

    class Meta:
        db_table = "budget"
        verbose_name = '예산'
        verbose_name_plural = '예산 목록'


class Expense(models.Model):
    id         = models.AutoField(primary_key=True)
    period     = models.CharField(max_length=7)          # 'YYYY-MM'
    category   = models.CharField(max_length=40)         # 급여/인건비, 임대료
    amount     = models.DecimalField(max_digits=14, decimal_places=2)
    currency   = models.CharField(max_length=8, default="KRW")
    costcenter = models.CharField(max_length=40)         # 本社 / 営業本部 

    class Meta:
        db_table = "expense"
        verbose_name = '일반 경비'
        verbose_name_plural = '일반 경비 목록'


class AccountsReceivable(models.Model):
    id = models.AutoField(primary_key=True)
    # 안전성을 위해 PROTECT로 전환 (매출채권이 존재하면 원본 주문 삭제 불가)
    orderid      = models.ForeignKey("ssafy_international.Order", on_delete=models.PROTECT, db_column="orderid", related_name="receivables")
    customerid   = models.ForeignKey("ssafy_international.Customer", on_delete=models.PROTECT, db_column="customerid", related_name="receivables")
    invoicedate  = models.DateField()
    duedate      = models.DateField()
    amount       = models.DecimalField(max_digits=14, decimal_places=2)
    currency     = models.CharField(max_length=8, default="KRW")
    paymentterms = models.CharField(max_length=20)       # NET15 / NET30 ... (버퍼 확장)
    status       = models.CharField(max_length=20)       # paid / open / overdue (버퍼 확장)

    class Meta:
        db_table = "accountsreceivable"
        verbose_name = '매출채권'
        verbose_name_plural = '매출채권 목록'

    def __str__(self):
        return f"AR-{self.id} ({self.customerid_id} - {self.amount})"


class AccountsPayable(models.Model):
    id = models.AutoField(primary_key=True)
    purchaseorderid = models.ForeignKey("procurement.PurchaseOrder", on_delete=models.PROTECT, db_column="purchaseorderid", related_name="payables")
    supplierid      = models.ForeignKey("ssafy_international.Supplier", on_delete=models.PROTECT, db_column="supplierid", related_name="payables")
    invoicedate     = models.DateField()
    duedate         = models.DateField()
    amount          = models.DecimalField(max_digits=14, decimal_places=2)
    currency        = models.CharField(max_length=8, default="KRW")
    paymentterms    = models.CharField(max_length=20)       # 버퍼 확장
    status          = models.CharField(max_length=20)       # b버퍼 확장
     
    class Meta:
        db_table = "accountspayable"
        verbose_name = '매입채무'
        verbose_name_plural = '매입채무 목록'

    def __str__(self):
        return f"AP-{self.id} ({self.supplierid_id} - {self.amount})"