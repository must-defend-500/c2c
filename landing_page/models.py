from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.

class UserInfo(models.Model):
    #change this to settings.AUTH_USER_MODEL.id
    #user = models.ForeignKey(settings.AUTH_USER_MODEL, primary_key=True, on_delete=models.CASCADE)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True, on_delete=models.CASCADE)
    user_email = models.EmailField(max_length=100)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    user_timestamp = models.DateField(auto_now_add=True)
    wallet = models.CharField(max_length=100, default = '000000')

    def __str__(self):
        return self.user.username


class Fund(models.Model):
    fund_categories = (
    ('0', 'REIT'),
    ('1', 'BioTech'),
    ('2', 'Tech'),
    ('3', 'Crypto')
    )
    category = models.CharField(max_length =1, primary_key = True,  choices = fund_categories)
    net_asset_value = models.DecimalField(max_digits = 12, decimal_places= 3)
    cash_amount = models.DecimalField(max_digits = 12, decimal_places= 3)
    BTC_amount = models.DecimalField(max_digits = 12, decimal_places= 6)
    ETH_amount = models.DecimalField(max_digits = 12, decimal_places= 3)
    LTC_amount = models.DecimalField(max_digits = 12, decimal_places= 3)
    investment_value = models.DecimalField(max_digits = 12, decimal_places= 3)

    def __str__(self):
        return self.category

class UserInvestment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    currencies = (
    ('0', 'BTC'),
    ('1', 'ETH'),
    ('2', 'LTC')
    )
    currency = models.CharField(max_length =1, choices = currencies)
    amount = models.DecimalField(max_digits = 10, decimal_places= 3)
    fund_category = models.ForeignKey(Fund, on_delete=models.CASCADE)
    date = models.DateTimeField()

class FundInvestment(models.Model):
    business_name = models.CharField(max_length = 75)
    amount_invested = models.DecimalField(max_digits = 12, decimal_places= 3)
    fund_category = models.ForeignKey(Fund, on_delete=models.CASCADE)
    investment_date = models.DateTimeField()

    def __str__(self):
        return self.business_name

class FundDividend(models.Model):
    dividend_date = models.DateTimeField()
    currencies = (
    ('0', 'BTC'),
    ('1', 'ETH'),
    ('2', 'LTC')
    )
    currency = models.CharField(max_length =1, choices = currencies)
    dividend_amount = models.DecimalField(max_digits = 12, decimal_places= 3)
    payer = models.ForeignKey(FundInvestment, on_delete=models.CASCADE, related_name='Business')
    payee = models.ForeignKey(Fund, on_delete=models.CASCADE, related_name = 'Fund', default='default fund')

    def __str__(self):
        name = str(self.dividend_date)+ "- "+ str(self.payer) + " "+ str(self.payee)
        return name

class UserDividend(models.Model):
    payee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    currencies = (
    ('0', 'BTC'),
    ('1', 'ETH'),
    ('2', 'LTC')
    )
    currency = models.CharField(max_length =1, choices = currencies)
    dividend_amount = models.DecimalField(max_digits = 12, decimal_places= 3)
    payer = models.ForeignKey( Fund, on_delete=models.CASCADE)
    dividend_date = models.DateTimeField()

class UserPreference(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True, on_delete=models.CASCADE)
    inspector_tup = (
    ('0', 'BPG Home Inspectors'),
    ('1', 'inspect_B'),
    ('2', 'inspect_C'),
    ('3', 'inspect_D'),
    ('4', 'inspect_E'),
    )

    inspector1 = models.CharField(max_length=1, choices = inspector_tup)
    inspector2 = models.CharField(max_length=1, choices = inspector_tup)
    inspector3 = models.CharField(max_length=1, choices = inspector_tup)

    lender_tup = (
    ('0', 'USA Mortgage'),
    ('1', 'lender_B'),
    ('2', 'lender_C'),
    ('3', 'lender_D'),
    ('4', 'lender_E'),
    )

    lender1 = models.CharField(max_length=1, choices = lender_tup)
    lender2 = models.CharField(max_length=1, choices = lender_tup)
    lender3 = models.CharField(max_length=1, choices = lender_tup)

    closingco_tup = (
    ('0', 'Investors Title'),
    ('1', 'closingco_B'),
    ('2', 'closingco_C'),
    ('3', 'closingco_D'),
    ('4', 'closingco_E'),
    )

    closingco1 = models.CharField(max_length=1, choices = closingco_tup)
    closingco2 = models.CharField(max_length=1, choices = closingco_tup)
    closingco3 = models.CharField(max_length=1, choices = closingco_tup)

    def __str__(self):
        return str(self.user)
