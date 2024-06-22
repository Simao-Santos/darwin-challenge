from django.db import models

class CurrencyRate(models.Model):
    rate_value = models.DecimalField(max_digits=11, decimal_places=6)
    rate_date = models.DateField(unique=True, db_index=True)
    
    class Meta:
        db_table = "currency_rate"
        indexes = [
            models.Index(fields=['rate_date']),
        ]