from django.db import models

class UUser(models.Model):
    name = models.CharField(max_length=120, blank=False)
    second_name = models.CharField(max_length=120, blank=False)
    last_name = models.CharField(max_length=120, blank=False)

    def __str__(self):
        return f"{self.name} {self.second_name} {self.last_name}"

class PPatient(models.Model):
    name = models.CharField(max_length=120, blank=False)
    second_name = models.CharField(max_length=120, blank=False)
    last_name = models.CharField(max_length=120, blank=False)
    date_of_birth = models.CharField(max_length=120, blank=False)

    def __str__(self):
        return f"{self.name} {self.second_name} {self.last_name}"

class Diagnose(models.Model):
    user = models.ForeignKey(UUser, on_delete=models.CASCADE)
    patient = models.ForeignKey(PPatient, on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    note = models.CharField(max_length=1000)
    diagnose = models.CharField(max_length=100)
    photo_before = models.ImageField()
    photo_after = models.ImageField()
