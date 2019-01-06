from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import User


class Request(models.Model):
    timestamp = models.DateTimeField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.CharField(max_length=75)
    cost = models.DecimalField(max_digits=6, decimal_places=2)
    quantity = models.PositiveSmallIntegerField()
    link = models.URLField(max_length=2000)
    notes = models.TextField(null=True, blank=True)

    approved = models.NullBooleanField()
    ordered = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)

    def __str__(self):
        return self.item + ", x" + str(self.quantity)

    def line_total(self):
        return self.quantity * self.cost