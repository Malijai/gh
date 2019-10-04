from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models



#listes valeurs dependant de province
DEFAULT_PID = 1
class Province(models.Model):
    nom_en = models.CharField(max_length=200, )
    nom_fr = models.CharField(max_length=200, )
    reponse_en = models.CharField(max_length=200, )
    reponse_fr = models.CharField(max_length=200, )
    reponse_valeur = models.IntegerField()

    def __str__(self):
        return '%s' % self.reponse_en


class Etablissement(models.Model):
    reponse_valeur = models.CharField(max_length=200)
    reponse_en = models.CharField(max_length=200, )
    reponse_fr = models.CharField(max_length=200, )
    province = models.ForeignKey(Province, default=DEFAULT_PID, on_delete=models.DO_NOTHING)

    class Meta:
        ordering = ['reponse_valeur']

    def __str__(self):
        return '%s' % self.reponse_en


##############
#Indispensable au questionnaire
class Typequestion(models.Model):
    nom = models.CharField(max_length=200, )
    tatable = models.CharField(max_length=200, blank=True, null=True)
    taille = models.CharField(max_length=200, )

    def __str__(self):
        return '%s' % self.nom


class Victime(models.Model):
    # a part a cause du tri par id du a la hierarchie des reponses proposees
    reponse_valeur = models.CharField(max_length=200)
    reponse_en = models.CharField(max_length=200, )
    reponse_fr = models.CharField(max_length=200, )

    class Meta:
        ordering = ['id']

    def __str__(self):
        return '%s' % self.reponse_en


#listes valeurs SANS province
class Listevaleur(models.Model):
    reponse_valeur = models.CharField(max_length=200)
    reponse_en = models.CharField(max_length=200, )
    reponse_fr = models.CharField(max_length=200, )
    typequestion = models.ForeignKey(Typequestion, on_delete=models.DO_NOTHING)

    class Meta:
        ordering = ['typequestion', 'reponse_valeur']

    def __str__(self):
        return '%s' % self.reponse_en


class Questionnaire(models.Model):
    nom_en = models.CharField(max_length=200, )
    nom_fr = models.CharField(max_length=200, )
    description = models.CharField(max_length=200, )

    def __str__(self):
        return '%s' % self.nom_en


class Interview(models.Model):
    reponse_valeur = models.CharField(max_length=200, )
    reponse_en = models.CharField(max_length=200, )
    reponse_fr = models.CharField(max_length=200, )

    def __str__(self):
        return '%s' % self.reponse_en


##############
class Question(models.Model):
    questionno = models.IntegerField()
    questionen = models.CharField(max_length=255,)
    questionfr = models.CharField(max_length=255,)
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.DO_NOTHING)
    typequestion = models.ForeignKey(Typequestion, on_delete=models.DO_NOTHING)
    parent= models.ForeignKey("self",default=1, on_delete=models.DO_NOTHING)
    relation = models.CharField(blank=True, null=True, max_length=45,)
    cible = models.CharField(blank=True, null=True, max_length=45,)
    varname = models.CharField(blank=True, null=True, max_length=45,)
    aidefr = models.TextField(blank=True, null=True)
    aideen = models.TextField(blank=True, null=True)
    qstyle = models.CharField(blank=True, null=True, max_length=45,)
    phase = models.CharField(blank=True, null=True, max_length=45,)
    parentvarname = models.CharField(blank=True, null=True, max_length=45,)

    class Meta:
        ordering = ['questionnaire', 'questionno']

    def __str__(self):
        return '%s' % self.questionen


#########################
class Instrument(models.Model):
    #Pour identifier les instruments
    nom = models.ForeignKey(Question, related_name='questionsinstrument', on_delete=models.CASCADE)
    phase = models.CharField(blank=True, null=True, max_length=45, )


class ItemInstrument(models.Model):
    #Pour identifier les items des instruments
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)


class QuestionItem(models.Model):
    #Pour trouver les réponses aux questions reliees aux items des instruments
    item = models.ForeignKey(ItemInstrument, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)


###########
class Reponse(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    reponse_no = models.CharField(max_length=200)
    reponse_valeur = models.CharField(max_length=200)
    reponse_en = models.CharField(max_length=200,)
    reponse_fr = models.CharField(max_length=200,)
    questionnaire = models.CharField(blank=True, null=True, max_length=45, )

    class Meta:
        ordering = ['reponse_valeur']

    def __str__(self):
        return '%s' % self.reponse_en


class Personne(models.Model):
    personne_code = models.CharField(max_length=200,)
    province = models.ForeignKey(Province, on_delete=models.CASCADE)
    date_consentement = models.CharField(max_length=200,blank=True, null=True)
    PartN = models.TextField()                                              #encrypte
    PartP = models.CharField(max_length=200,)
    VerdictDate = models.TextField(blank=True, null=True)
    LibeDate = models.TextField(blank=True, null=True)
    DDN = models.TextField(blank=True, null=True)                           #encrypte
    Consent = models.IntegerField()
    ConsentAudio = models.IntegerField()
    ConsentFamille = models.IntegerField()
    ConsentSuivi = models.IntegerField()
    fpsyn = models.IntegerField(blank=True, null=True)
    fps = models.TextField(max_length=200,blank=True, null=True)            #encrypte
    Medicyn = models.IntegerField(blank=True, null=True)
    Medic = models.TextField(blank=True, null=True)                         #encrypte
    Hearingdate = models.CharField(max_length=200,blank=True, null=True)
    confid1 = models.TextField(blank=True, null=True)                       #encrypte
    confid2 = models.TextField(blank=True, null=True)                       #encrypte
    assistant = models.ForeignKey(User, related_name='assistant2gh', on_delete=models.DO_NOTHING)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s' % self.personne_code


class Resultat(models.Model):
    personne = models.ForeignKey(Personne, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    reponse_texte = models.TextField(blank=True, null=True)
    reponse_code = models.CharField(max_length=10, blank=True, null=True)
    assistant = models.ForeignKey(User, related_name='assistantgh', on_delete=models.DO_NOTHING)
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE)
    province = models.ForeignKey(Province, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('personne', 'question', 'interview', 'assistant'),)

    def __str__(self):
        return '%s' % self.reponse_texte


#Pour housing et jobs repetitive (questionnaire 4 Work TLBF et 3 Housing TLFB
class Resultatrepet(models.Model):
    personne = models.ForeignKey(Personne, on_delete=models.DO_NOTHING)
    question = models.ForeignKey(Question, db_index=True, on_delete=models.DO_NOTHING)
    questionnaire =  models.ForeignKey(Questionnaire,db_index=True, on_delete=models.DO_NOTHING)
    reponsetexte = models.CharField(max_length=200, blank=True, null=True)
    assistant = models.ForeignKey(User, related_name='arrepetgh', on_delete=models.DO_NOTHING)
    interview = models.ForeignKey(Interview, on_delete=models.DO_NOTHING)
    province = models.ForeignKey(Province, on_delete=models.DO_NOTHING)
    fiche = models.IntegerField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('personne','questionnaire', 'question', 'interview', 'fiche', 'assistant'))

        ordering = ['personne','questionnaire', 'question', 'interview', 'fiche', 'assistant']

    def __str__(self):
        return '%s' % self.reponsetexte
