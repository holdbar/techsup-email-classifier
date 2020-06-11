from django.db import models
from django.utils import timezone

class Source(models.Model):
    name = models.CharField(max_length=200)
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):

        return f'[{self.pk}] {self.name}'

class Email(models.Model):
    text = models.TextField()
    annotated_text = models.TextField(blank=True, null=True)
    manual_annotation_info = models.CharField(max_length=1000, blank=True, null=True)
    rules_annotation_info = models.CharField(max_length=1000, blank=True, null=True)
    model_annotation_info = models.CharField(max_length=1000, blank=True, null=True)
    source = models.ForeignKey(Source, on_delete=models.SET_NULL, blank=True, null=True)
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):

        return f'[{self.pk}] {self.text[:50]}'

class ConstituencyTemplate(models.Model):
    template_text = models.TextField()
    examples = models.TextField(blank=True, null=True)
    source = models.ForeignKey(Source, on_delete=models.SET_NULL, blank=True, null=True)
    frequency = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):

        return f'[{self.pk}] {self.template_text}'

class EmailSentence(models.Model):
    text = models.TextField()
    annotated_text = models.TextField(blank=True, null=True)
    tree = models.TextField(blank=True, null=True)
    source = models.ForeignKey(Source, on_delete=models.SET_NULL, blank=True, null=True)
    template = models.ForeignKey(ConstituencyTemplate, on_delete=models.SET_NULL, blank=True, null=True)
    email = models.ForeignKey(Email, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.IntegerField()
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):

        return f'[{self.pk}] {self.text}'

class Ngrams(models.Model):
    text = models.TextField()
    frequency = models.IntegerField(default=0)
    type = models.IntegerField(default=1)

    def __str__(self):

        return f'[{self.pk}] {self.text}'

class OntologyVariableType(models.Model):
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)

    def __str__(self):

        return f'[{self.pk}] {self.name}'

class OntologyVariable(models.Model):
    name = models.CharField(max_length=200)
    type = models.ForeignKey(OntologyVariableType, on_delete=models.SET_NULL, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):

        return f'[{self.pk}] {self.name}'

class OntologyVariableValue(models.Model):
    text = models.TextField()
    variable = models.ForeignKey(OntologyVariable, on_delete=models.SET_NULL, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):

        return f'[{self.pk}] {self.text}'

