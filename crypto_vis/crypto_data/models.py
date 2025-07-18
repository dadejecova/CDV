from django.db import models

class Portfolio(models.Model):
    coin_id = models.CharField(max_length=50)  # e.g., 'bitcoin'
    amount = models.DecimalField(max_digits=18, decimal_places=8)  # For fractional holdings
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Optional, for gains/losses
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.coin_id} holding: {self.amount}"
    
    def gain_loss(self):
        if self.purchase_price and hasattr(self, 'current_value') and self.current_value != 'N/A':
            return self.current_value - (self.amount * self.purchase_price)
        return None