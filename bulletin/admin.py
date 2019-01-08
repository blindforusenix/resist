from django.contrib import admin
#The Nested Admin is used because Choice>Questions>Election inline will not work for multiple levels of inline with basic javascript.
from nested_admin import NestedModelAdmin, NestedStackedInline, NestedTabularInline
# Register your models here.
from .models import Election, Voter, Trustee, Question, Choice, Registrar


class ChoiceInline(NestedTabularInline):
    model = Choice
    extra = 1

class QuestionInline(NestedTabularInline):
    model = Question
    extra = 1
    inlines = [ChoiceInline, ]

class TrusteeInline(NestedTabularInline):
    fieldsets = [
        ('Trustee Name', {'fields':['name']}),
        ('Trustee Email', {'fields':['email']}),
    ]
    model = Trustee
    extra = 1

class ElectionAdmin(NestedModelAdmin):
    fieldsets = [
        ('Name', {'fields':['name']}),
        ('Organization', {'fields':['organization']}),
        ('Description', {'fields':['description']}),
        ('Registration Start', {'fields':['registration_starts_at']}),
        ('Voting Start', {'fields':['voting_starts_at']}),
        ('Voting End', {'fields':['voting_ends_at']}),
        ('Tallying Start', {'fields':['tallying_starts_at']}),
        ('Result Release', {'fields':['result_released_at']}),
        ('Help Email', {'fields':['help_email']}),
    ]
    inlines = [QuestionInline, TrusteeInline]
    list_display = ('name','registration_starts_at', 'voting_starts_at', 'voting_ends_at', 'tallying_starts_at', 'result_released_at')
    list_filter = ['created_at']

admin.site.register(Election, ElectionAdmin)

class VoterAdmin(NestedModelAdmin):
    fieldsets = [
        ('Name', {'fields':['voter_name']}),
        ('Email', {'fields':['voter_email']}),
        ('Registered?', {'fields':['is_registered']}),
    ]
    list_display = ('voter_name', 'voter_email', 'is_registered')
    list_filter = ['voter_name']
    search_fields = ['voter_name']

admin.site.register(Voter, VoterAdmin)

class RegistrarAdmin(NestedModelAdmin):
    fieldsets = [
        ('Name', {'fields':['name']}),
        ('Email', {'fields':['email']}),
    ]
admin.site.register(Registrar, RegistrarAdmin)
