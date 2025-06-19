from django.db import models
from django.conf import settings

class InteriorColor(models.Model):
    color = models.CharField(max_length=200, null=True)
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    
    def __str__(self):
        return self.color
    
class Color(models.Model):
    color = models.CharField(max_length=200, null=True)
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    
    def __str__(self):
        return self.color
    
class Body(models.Model):
    body = models.CharField(max_length=200, null=True)
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    
    def __str__(self):
        return self.body
    
class Brand(models.Model):
    name = models.CharField(max_length=200, null=True)
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    country_origin = models.CharField(max_length=200, null=True)
    founded_year = models.IntegerField(null=True)

    def __str__(self):
        return self.name
    
class Car(models.Model):
    name = models.CharField(max_length=200, null=True)
    brand = models.ForeignKey(Brand, on_delete= models.SET_NULL, null=True)
    color = models.ForeignKey(Color, on_delete= models.SET_NULL, null=True)
    interiorColor = models.ForeignKey(InteriorColor, on_delete= models.SET_NULL, null=True)
    transmission = models.CharField(max_length=200, null=True)
    model = models.CharField(max_length=200, null=True)
    trim = models.CharField(max_length=200, null=True)
    body = models.ForeignKey(Body, on_delete= models.SET_NULL, null=True)
    condition = models.CharField(max_length=200, null=True)
    odometer = models.FloatField(max_length=1000, null=True)
    image = models.ImageField(upload_to='cars_image/', null=True, blank=True)
    price = models.FloatField(max_length=1000, null=True)
    status = models.CharField(max_length=200, null=True, default='Available')

    
    def __str__(self):
        return self.name
    
class Request(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, null=True)
    car = models.ForeignKey(Car, on_delete= models.SET_NULL, null=True)
    status = models.CharField(max_length=200, null=True)
    date = models.DateField(null=True)
    time = models.TimeField(null=True)
    
class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, null=True)
    car = models.ForeignKey(Car, on_delete= models.SET_NULL, null=True)
    
    class Meta:
        unique_together = ('user', 'car')
    
    def __str__(self):
        return f'{self.car.name} ada di wishlist {self.user}'
    
class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, null=True)
    car = models.ForeignKey(Car, on_delete= models.SET_NULL, null=True)
    status = models.CharField(max_length=200, null=True)
    payment_date = models.CharField(max_length=100, null=True)

