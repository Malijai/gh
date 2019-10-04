from __future__ import unicode_literals
from django import template
import re
from django.apps import apps
from gh.models import Reponse, Question, Resultatrepet, Typequestion, Listevaleur
from django import forms
from .formulairesgh import gh_select_date, gh_liste_tables, enlevelisttag
from gh.gh_constants import CHOIX_ONUK, CHOIX_ON

register = template.Library()


@register.simple_tag
def ghrep_reponse(qid,b, *args, **kwargs):
    #Pour listes de valeurs specifiques a chaque question
    personneid = kwargs['persid']
    relation = kwargs['relation']
    cible = kwargs['cible']
    assistant = kwargs['uid']
    ordre = kwargs['ordre']
    intid = kwargs['interview']

    defaultvalue = ghrep_default(personneid, qid, intid, assistant=assistant, ordre=ordre)
    IDCondition = ghrep_id(qid,cible,relation=relation)

    listevaleurs = Reponse.objects.filter(question__id=qid, )
    name = 'q{}Z_Z{}'.format(qid, ordre)
    liste = gh_liste_tables(listevaleurs, 'reponse')

    question = forms.Select(choices = liste, attrs={'id': IDCondition,'name': name, })

    return question.render(name, defaultvalue)


@register.simple_tag
def ghrep_dichou(qid,type, *args, **kwargs):
    personneid = kwargs['persid']
    relation = kwargs['relation']
    cible = kwargs['cible']
    assistant = kwargs['uid']
    ordre = kwargs['ordre']
    intid = kwargs['interview']

    defaultvalue = ghrep_default(personneid, qid, intid, assistant=assistant, ordre=ordre)
    IDCondition = ghrep_id(qid,cible,relation=relation)
    name = 'q{}Z_Z{}'.format(qid, ordre)

    if type == "DICHO":
        liste = CHOIX_ON.items()
        question = forms.RadioSelect(choices = liste, attrs={'id': IDCondition,'name': name, })
    else:
        liste = CHOIX_ONUK.items()
        question = forms.RadioSelect(choices=liste, attrs={'id': IDCondition, 'name': name, })

    return enlevelisttag(question.render(name, defaultvalue))



@register.simple_tag
def ghrep_textechar(qid,type, *args, **kwargs):
    personneid = kwargs['persid']
    relation = kwargs['relation']
    cible = kwargs['cible']
    assistant = kwargs['uid']
    ordre = kwargs['ordre']
    intid = kwargs['interview']

    defaultvalue = ghrep_default(personneid, qid, intid, assistant=assistant, ordre=ordre)
    IDCondition = ghrep_id(qid,cible,relation=relation)
    name = 'q{}Z_Z{}'.format(qid, ordre)
    if type == 'STRING' or type == 'CODESTRING':
        question = forms.TextInput(attrs={'size': 30, 'id': IDCondition,'name': name,})
    else:
        question = forms.NumberInput(attrs={'size': 30, 'id': IDCondition,'name': name,})

    return question.render(name, defaultvalue)


@register.simple_tag
def ghrep_date(qid,b, *args, **kwargs):
    personneid = kwargs['persid']
    relation = kwargs['relation']
    cible = kwargs['cible']
    assistant = kwargs['uid']
    ordre = kwargs['ordre']
    intid = kwargs['interview']

    an = ''
    mois = ''
    jour = ''
    if Resultatrepet.objects.filter(personne__id=personneid, assistant__id=assistant, question__id=qid, fiche=ordre, interview__id=intid).exists():
        ancienne = Resultatrepet.objects.get(personne__id=personneid, assistant__id=assistant,
                                                 question__id=qid, fiche=ordre, interview__id=intid).__str__()
        if ancienne:
            an, mois, jour = ancienne.split('-')

    IDCondition = ghrep_id(qid, cible, relation=relation)
    name = 'q{}Z_Z{}'.format(qid, ordre)
    day, month, year = gh_select_date(IDCondition, name)
# #name=q69_year, id=row...
    return year.render(name + '_year' , an) + month.render(name + '_month', mois) + day.render(name + '_day', jour)


#Utlitaires generaux
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


def ghrep_default(personneid, qid, intid, *args, **kwargs):
    ##fail la valeur par deffaut
    assistant = kwargs['assistant']
    ordre = kwargs['ordre']
    ancienne = ''

    if Resultatrepet.objects.filter(personne__id=personneid, assistant__id=assistant, question__id=qid, fiche=ordre, interview__id=intid).exists():
        ancienne = Resultatrepet.objects.get(personne__id=personneid, assistant__id=assistant,
                                                 question__id=qid, fiche=ordre, interview__id=intid).__str__()

    return ancienne


def ghrep_id(qid, cible, *args, **kwargs):
    ##fail l'ID pour javascripts ou autre
    relation = kwargs['relation']

    IDCondition = ''
    if relation != '' and cible != '':
        IDCondition = 'row-{}X{}X{}'.format(qid, relation, cible)
    return IDCondition


@register.simple_tag
def fait_dateghrep(persid,province,*args, ** kwargs):
    ordre = kwargs['ordre']
    assistant = kwargs['uid']
    interview = kwargs['interview']
    qid = kwargs['qid']
    datehosp = ''
    texte = {
        3: 'Moved on: ',
        4: 'Job started on: '
    }
    question = Question.objects.get(typequestion_id=60, questionnaire_id=qid).pk
    if Resultatrepet.objects.filter(personne__id=persid, assistant__id=assistant, question_id=question, province__id=province, interview__id=interview, fiche=ordre).exists():
        datehosp = Resultatrepet.objects.get(personne__id=persid, assistant__id=assistant, province__id=province, interview__id=interview,
                                                 question__id=question, fiche=ordre).__str__()
    else:
        datehosp = ordre
    return '<h3>{}</h3><b>{} {}</b>'.format(datehosp, texte[int(qid)],datehosp)

