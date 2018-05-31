from django.core.validators import MinValueValidator
from django.db import models


class Request(models.Model):
    id = models.PositiveIntegerField()
    timestamp = models.DateTimeField()
    item = models.CharField(max_length=75)
    cost = models.DecimalField(decimal_places=2, validators=[MinValueValidator(0.01)])
    quantity = models.PositiveSmallIntegerField()
    link = models.URLField(max_length=200)
    approved = models.NullBooleanField()
