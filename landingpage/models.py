import uuid
from django.db import models
from django.forms import ModelForm

# Create your models here.
class Employee(models.Model):
    id = models.UUIDField(primary_key= True, default = uuid.uuid4)
    name = models.CharField(max_length=150)
    start_date_time = models.IntegerField()
    end_date_time = models.IntegerField()


class EmployeeAdd(ModelForm):
    class Meta:
        model = Employee
        fields = ['name', 'start_date_time', 'end_date_time']

    def my_save(self, user):
        lv = self.save(commit=False)
        lv.created_by = user
        lv.save()
        return lv
