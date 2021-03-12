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
    city=models.CharField(max_length=200, blank=True, null=True)
    time=models.DurationField(default=0, null=True);
    race=models.ForeignKey(Race, on_delete=models.CASCADE)
    runner=models.ForeignKey(Runner,  on_delete=models.CASCADE, null=True)

   

