from django.contrib import admin

# Register your models here.
from .models import Election, Voter, Trustee, Question, Choice


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 1

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    inlines = [ChoiceInline]

class TrusteeInline(admin.TabularInline):
    model = Trustee
    extra = 1

class ElectionAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Short Name', {'fields':['short_name']}),
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
    list_display = ('short_name', 'registration_starts_at', 'voting_starts_at', 'voting_ends_at', 'tallying_starts_at', 'result_released_at')
    list_filter = ['created_at']

admin.site.register(Election, ElectionAdmin)

class VoterAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Name', {'fields':['voter_name']}),
        ('Email', {'fields':['voter_email']}),
        ('Registered?', {'fields':['is_registered']}),
    ]
    list_display = ('voter_name', 'voter_email', 'is_registered')
    list_filter = ['voter_name']
    search_fields = ['voter_name']

admin.site.register(Voter, VoterAdmin)
