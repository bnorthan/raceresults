from django.db import models

class Race(models.Model):
    race_name=models.CharField(max_length=200)
    city=models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return self.race_name


# Create your models here.
class Result(models.Model):
    first_name=models.CharField(max_length=200)
    last_name=models.CharField(max_length=200)
    city=models.CharField(max_length=200, blank=True, null=True)
    time=models.DurationField();
    race=models.ForeignKey(Race, on_delete=models.CASCADE)



