# employees/models.py
from django.db import models
from django.contrib import settings


class Employee(models.Model):
    TITLE_CHOICES = [
        ("대표이사",                  "대표이사"),
        ("Vice President, Sales",     "Vice President, Sales"),
        ("Sales Manager",             "Sales Manager"),
        ("Inside Sales Coordinator",  "Inside Sales Coordinator"),
        ("Sales Representative",      "Sales Representative"),
    ]

    employeeid = models.AutoField(primary_key=True)
    lastname = models.CharField(max_length=40)
    firstname = models.CharField(max_length=40)
    title = models.CharField(max_length=60, choices=TITLE_CHOICES, blank=True, null=True)
    titleofcourtesy = models.CharField(max_length=20, blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    hiredate = models.DateField(blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=60,  blank=True, null=True)
    region = models.CharField(max_length=60,  blank=True, null=True)
    postalcode = models.CharField(max_length=20,  blank=True, null=True)
    country = models.CharField(max_length=60,  blank=True, null=True)
    homephone = models.CharField(max_length=40,  blank=True, null=True)
    extension = models.CharField(max_length=10,  blank=True, null=True)
    photo = models.BinaryField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    reportsto = models.ForeignKey("self", on_delete=models.SET_NULL,
                blank=True, null=True, db_column="reportsto", related_name="reports") 
    photopath = models.CharField(max_length=200, blank=True, null=True)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='employee',
    )

    class Meta:
        db_table = "employee"

    def __str__(self):
        return f"{self.lastname}{self.firstname}"


class EmployeeTerritory(models.Model):
    employeeid = models.ForeignKey(Employee, on_delete=models.CASCADE,
                                    db_column="employeeid", related_name="territories")
    territoryid = models.ForeignKey("ssafy_international.Territory", on_delete=models.CASCADE,
                                    db_column="territoryid", related_name="employees")

    class Meta:
        db_table = "employeeterritory"
        unique_together = ("employeeid", "territoryid")