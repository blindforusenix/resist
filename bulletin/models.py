from django.db import models, transaction

import json
from django.conf import settings
from django.core.mail import send_mail
import datetime, logging, uuid, random, io
from django.contrib.postgres.fields import JSONField, ArrayField
from django.db.models.fields import BigIntegerField
#import bleach

"""
Stuff below this line is referencing python scripts taken from helios
Masood
26 Dec, 2018
"""
#from supervisor.crypto import electionalgs, algs, utils
#import utils as resistutils


class Election(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    short_name = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=250)
    organization = models.CharField(max_length=250)
    description = models.TextField()
    public_key = models.CharField(max_length=250)
    private_key = models.CharField(max_length=250)
    #List of accepted credentials
    cred_set = JSONField(null = True)
    cast_votes = JSONField(null = True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now_add=True)
    frozen_at = models.DateTimeField(auto_now_add=False, default=None, null=True)
    archived_at = models.DateTimeField(auto_now_add=False, default=None, null=True)
    # dates for the election steps, as scheduled
    # these are always UTC
    registration_starts_at = models.DateTimeField(auto_now_add=False, default=None, null=True)
    voting_starts_at = models.DateTimeField(auto_now_add=False, default=None, null=True)
    voting_ends_at = models.DateTimeField(auto_now_add=False, default=None, null=True)
    complaint_period_ends_at = models.DateTimeField(auto_now_add=False, default=None, null=True)

    tallying_starts_at = models.DateTimeField(auto_now_add=False, default=None, null=True)

    # dates when things were forced to be performed
    voting_started_at = models.DateTimeField(auto_now_add=False, default=None, null=True)
    voting_extended_until = models.DateTimeField(auto_now_add=False, default=None, null=True)
    voting_ended_at = models.DateTimeField(auto_now_add=False, default=None, null=True)
    tallying_started_at = models.DateTimeField(auto_now_add=False, default=None, null=True)
    tallying_finished_at = models.DateTimeField(auto_now_add=False, default=None, null=True)
    tallies_combined_at = models.DateTimeField(auto_now_add=False, default=None, null=True)

    # we want to explicitly release results
    result_released_at = models.DateTimeField(auto_now_add=False, default=None, null=True)

    # the hash of all voters (stored for large numbers)
    voters_hash = models.CharField(max_length=100, null=True)
    encrypted_tally = JSONField()
    result = JSONField()
    # help email
    help_email = models.EmailField(null=True)

    # downloadable election info
    election_info_url = models.CharField(max_length=300, null=True)

class Question(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=200)
    question_description = models.TextField()
    def __str__(self):
        return self.question_text

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    def __str__(self):
        self.choice_text

class CastVote(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    vote = JSONField()
    vote_hash = models.CharField(max_length = 100)
    cast_at = models.DateTimeField(auto_now_add=True)
    cast_ip = models.GenericIPAddressField(null=True)
"""
    AuditedBallot was taken directly from Helios\
"""
class AuditedBallot(models.Model):
  """
  ballots for auditing
  """
  election = models.ForeignKey(Election, on_delete=models.CASCADE)
  raw_vote = models.TextField()
  vote_hash = models.CharField(max_length=100)
  added_at = models.DateTimeField(auto_now_add=True)

  @classmethod
  def get(cls, election, vote_hash):
    return cls.objects.get(election = election, vote_hash = vote_hash)

  @classmethod
  def get_by_election(cls, election, after=None, limit=None):
    query = cls.objects.filter(election = election).order_by('vote_hash')

    # if we want the list after a certain UUID, add the inequality here
    if after:
      query = query.filter(vote_hash__gt = after)

    if limit:
      query = query[:limit]

    return query

class Trustee(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE)

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    secret = models.CharField(max_length = 100)

    public_key = models.CharField(max_length=250)
    private_key_hash = models.CharField(max_length=250)

    # secret key
    # if the secret key is present, this means
    # Resist is playing the role of the trustee.
    secret_key = models.CharField(max_length = 250)
    pok = models.CharField(max_length=250)

    #decryption_factors = ArrayField(models.BigIntegerField, null=True)
    #decryption_proofs = ArrayField(models.CharField(max_length=250), null=True)

    class Meta:
      unique_together = (('election', 'email'))

class Voter(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    voter_name = models.CharField(max_length=200, null=False)
    voter_email = models.CharField(max_length=250, null=False)
    alias = models.CharField(max_length=100, null=True)
    is_registered = models.BooleanField(default=False)
    auth_key_hash = models.CharField(max_length=250, null=True)
    auth_for = JSONField(null=True)
