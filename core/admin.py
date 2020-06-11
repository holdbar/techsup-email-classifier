from django.contrib import admin
from core.models import (
    Source,
    Email,
    ConstituencyTemplate,
    EmailSentence,
    OntologyVariableType,
    OntologyVariable,
    OntologyVariableValue
)

class OntologyVariableValueAdmin(admin.ModelAdmin):
    search_fields = ('text',)

class EmailAdmin(admin.ModelAdmin):
    search_fields = ('text',)

# Register your models here.

admin.site.register(Source)
admin.site.register(Email, EmailAdmin)
admin.site.register(ConstituencyTemplate)
admin.site.register(EmailSentence)
admin.site.register(OntologyVariableType)
admin.site.register(OntologyVariable)
admin.site.register(OntologyVariableValue, OntologyVariableValueAdmin)