from django.db import models

class Race(models.Model):
    race_name=models.CharField(max_length=200)
    city=models.CharField(max_length=200, blank=True)
    race_date=models.DateField('date of race', blank=True, null=True)    
    def __str__(self):
        return self.race_name

class Runner(models.Model):
    first_name=models.CharField(max_length=200)
    last_name=models.CharField(max_length=200)
 
# Create your models here.
class Result(models.Model):
    first_name=models.CharField(max_length=200)
    last_name=models.CharField(max_length=200)
    gender=models.CharField(max_length=1, default='f', null=True)
    city=models.CharField(max_length=200, blank=True, null=True)
    time=models.DurationField(default=0, null=True);
    member=models.CharField(max_length=2, default='n', null=True);
    category_10=models.CharField(max_length=100, default='unknown', null=True);
    race=models.ForeignKey(Race, on_delete=models.CASCADE)
    runner=models.ForeignKey(Runner,  on_delete=models.CASCADE, null=True)

   

