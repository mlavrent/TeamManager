from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import User


class Request(models.Model):
    timestamp = models.DateTimeField()
    author = models.ForeignKey(User, null=True, related_name="+", on_delete=models.SET_NULL)
    item = models.CharField(max_length=75)
    cost = models.DecimalField(max_digits=6, decimal_places=2)
    quantity = models.PositiveSmallIntegerField()
    link = models.URLField(max_length=2000)
    notes = models.TextField(null=True, blank=True)

    approved = models.NullBooleanField()
    approved_timestamp = models.DateTimeField(null=True, blank=True)
    approver = models.ForeignKey(User, null=True, blank=True, related_name="+", on_delete=models.SET_NULL)

    ordered = models.BooleanField(default=False)
    order_timestamp  = models.DateTimeField(null=True, blank=True)
    orderer = models.ForeignKey(User, null=True, blank=True, related_name="+", on_delete=models.SET_NULL)
    shipping_cost = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    delivered = models.BooleanField(default=False)
    delivery_timestamp = models.DateTimeField(null=True, blank=True)
    delivery_person = models.ForeignKey(User, null=True, blank=True, related_name="+", on_delete=models.SET_NULL)

    def __str__(self):
        return self.item + ", x" + str(self.quantity)

    def line_total(self):
        return self.quantity * self.cost