from django.db import models, transaction

#Sepecifically for ElGamal Key generation
from Crypto import Random
from Crypto.Random import random
from Crypto.PublicKey import ElGamal
from Crypto.Util.number import GCD
from Crypto.Hash import SHA

#Specifically for RSA Key generation
from Crypto.PublicKey import RSA

#for sending emails
from django.core.mail import send_mail

import json
from django.conf import settings
from django.core.mail import send_mail
import datetime, logging, uuid, random, io
from django.contrib.postgres.fields import JSONField, ArrayField
from django.db.models.fields import BigIntegerField
import bleach


class Election(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    #short_name = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=250, unique=True)
    organization = models.CharField(max_length=250)
    description = models.TextField(null = True)
    public_key = JSONField(null=True)
    private_key = JSONField(null=True)
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
    encrypted_tally = JSONField(null=True)
    result = JSONField(null=True)
    # help email
    help_email = models.EmailField(null=True)

    # downloadable election info
    election_info_url = models.CharField(max_length=300, null=True)

class Question(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=200)
    question_description = models.TextField()


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)


class CastVote(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    vote = JSONField()
    vote_hash = models.CharField(max_length = 100)
    cast_at = models.DateTimeField(auto_now_add=True)
    cast_ip = models.GenericIPAddressField(null=True)
"""
    AuditedBallot was taken directly from Helios
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

    trustee_public_key = JSONField(null=True)
    trustee_private_key_hash = models.CharField(max_length=250)
    trustee_private_key = JSONField(null=True)
    # secret key
    # if the secret key is present, this means
    # Resist is playing the role of the trustee.
    secret_key = models.CharField(max_length = 250)
    pok = models.CharField(max_length=250)

    class Meta:
      unique_together = (('election', 'email'))
    #decryption_factors = ArrayField(models.BigIntegerField, null=True)
    #decryption_proofs = ArrayField(models.CharField(max_length=250), null=True)
    def save(self, *args, **kwargs):
        key = ElGamal.generate(512, Random.new().read)
        publicparams = json.dumps({'p' : key.p, 'g' : key.g, 'y' : key.y})
        privateparams = {'x' : key.x}
        message = "Hi " + self.name + ", You are a trustee. Your private key is " + json.dumps(privateparams)
        send_mail(
            'Test Trustee Key',
            message,
            'themasoodali@gmail.com',
            [self.email, ],
            fail_silently=False,
        )
        self.trustee_public_key = publicparams
        super(Trustee, self).save(*args, **kwargs)



class RegistrationTeller(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    secret = models.CharField(max_length = 100)

    registration_public_key = JSONField(null=True)
    registration_private_key_hash = models.CharField(max_length=250)

    # secret key
    # if the secret key is present, this means
    # Resist is playing the role of the registrar.
    secret_key = models.CharField(max_length = 250)
    #pok = models.CharField(max_length=250)

    def save(self, *args, **kwargs):
        key = RSA.generate(2048)
        publicparams = json.dumps({'n' : key.n, 'e' : key.e})
        privateparams = json.dumps({'d' : key.d, 'p' : key.p, 'q' : key.q, 'u' : key.u})
        message = "Hi " + self.name + ", You are a Registration Teller. Your private key is " + privateparams
        send_mail(
            'Test Registration Key',
            message,
            'themasoodali@gmail.com',
            [self.email, ],
            fail_silently=False,
        )
        self.registration_public_key = publicparams
        super(RegistrationTeller, self).save(*args, **kwargs)


class Voter(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    voter_name = models.CharField(max_length=200, null=False)
    voter_email = models.CharField(max_length=250, null=False)
    alias = models.CharField(max_length=100, null=True)
    is_registered = models.BooleanField(default=False)
    public_auth_key = JSONField(null=True)
    public_desig_key = JSONField(null=True)
    auth_key_hash = models.CharField(max_length=250, null=True)
    desig_key_hash = models.CharField(max_length=250, null=True)
    #auth_for was initially intended to include the UUID's of the elections that the voter is registered for
    auth_for = JSONField(null=True)
    def save(self, *args, **kwargs):
        auth_key = RSA.generate(2048)
        auth_publicparams = json.dumps({'n' : auth_key.n, 'e' : auth_key.e})
        auth_privateparams = json.dumps({'d' : auth_key.d, 'p' : auth_key.p, 'q' : auth_key.q, 'u' : auth_key.u})
        desig_key = RSA.generate(2048)
        desig_publicparams = json.dumps({'n' : desig_key.n, 'e' : desig_key.e})
        desig_privateparams = json.dumps({'d' : desig_key.d, 'p' : desig_key.p, 'q' : desig_key.q, 'u' : desig_key.u})
        message = "Hi " + self.voter_name + ",\n You are a registered voter. \nYour authorization key is " + auth_privateparams + "\n Your designation key is " + desig_privateparams
        send_mail(
            'Test Registration Key',
            message,
            'themasoodali@gmail.com',
            [self.voter_email, ],
            fail_silently=False,
        )
        self.is_registered = True
        self.public_auth_key = auth_publicparams
        self.public_desig_key = desig_publicparams
        super(Voter, self).save(*args, **kwargs)
