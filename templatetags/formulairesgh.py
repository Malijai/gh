from __future__ import unicode_literals
from django import template
import re
from django.apps import apps
from gh.models import Reponse, Resultat, Personne, Listevaleur, Typequestion, Victime
from django import forms
from gh.gh_constants import CHOIX_ONUK, CHOIX_ON, LISTE_HCR, LISTE_START

register = template.Library()


@register.simple_tag
def gh_check(a,b, *args, **kwargs):
    qid = a
    type = b
    personneid = kwargs['persid']
    relation = kwargs['relation']
    cible = kwargs['cible']
    assistant = kwargs['uid']
    intid = kwargs['intid']

    defaultvalue = gh_default(personneid, qid, intid, assistant=assistant)
    IDCondition = gh_id(qid,cible,relation=relation)
    name = "q" + str(qid)
    if type=='LISTEHCR':
        liste =  sorted(LISTE_HCR.items())
    else:
        liste = sorted(LISTE_START.items())

    question = forms.CheckboxSelectMultiple(choices=liste, attrs={'id': IDCondition, 'name': name, })

    return enlevelisttag(question.render(name, defaultvalue))


@register.simple_tag
def gh_dichou(a,b, *args, **kwargs):
    qid = a
    type = b
    personneid = kwargs['persid']
    relation = kwargs['relation']
    cible = kwargs['cible']
    assistant = kwargs['uid']
    intid = kwargs['intid']

    defaultvalue = gh_default(personneid, qid, intid, assistant=assistant)
    IDCondition = gh_id(qid,cible,relation=relation)
    name = "q" + str(qid)
    if type == "DICHO":
        liste = CHOIX_ON.items()
        question = forms.RadioSelect(choices = liste, attrs={'id': IDCondition,'name': name, })
    else:
        liste = CHOIX_ONUK.items()
        question = forms.RadioSelect(choices=liste, attrs={'id': IDCondition, 'name': name, })

    return enlevelisttag(question.render(name, defaultvalue))


@register.simple_tag
def gh_date(qid,b, *args, **kwargs):
    personneid = kwargs['persid']
    relation = kwargs['relation']
    cible = kwargs['cible']
    assistant = kwargs['uid']
    intid = kwargs['intid']
    an = ''
    mois = ''
    jour = ''
    if Resultat.objects.filter(personne__id = personneid, question__id = qid, interview__id=intid, assistant__id = assistant).exists():
        ancienne = Resultat.objects.get(personne__id = personneid, question__id = qid, interview__id=intid,
                                            assistant__id = assistant).__str__()
        an, mois, jour = ancienne.split('-')

    IDCondition = gh_id(qid,cible,relation=relation)
    name = "q" + str(qid)
    day, month, year = gh_select_date(IDCondition, name)
    #name=q69_year, id=row...

    return year.render(name + '_year', an) + month.render(name + '_month', mois) + day.render(name + '_day', jour)


@register.simple_tag
def gh_datecode(qid, type, *args, **kwargs):
    personneid = kwargs['persid']
    relation = kwargs['relation']
    cible = kwargs['cible']
    assistant = kwargs['uid']
    varname = kwargs['varname']
    intid = kwargs['intid']
    an = ''
    mois = ''
    jour = ''
    ancienne = ''

    personne = Personne.objects.get(pk=personneid)
    if personne.__dict__[varname] is not None:
        ancienne = 1

    IDCondition = gh_id(qid, cible, relation=relation)
    name = "q" + str(qid)
    day, month, year = gh_select_date(IDCondition, name)
    # name=q69_year, id=row...
    if ancienne:
        return 'Already Encrypted data'
    else:
        return year.render(name + '_year', an) + month.render(name + '_month',mois) + day.render(name + '_day',jour)


@register.simple_tag
def gh_textechar(qid,type, *args, **kwargs):
    personneid = kwargs['persid']
    relation = kwargs['relation']
    cible = kwargs['cible']
    assistant = kwargs['uid']
    intid = kwargs['intid']

    defaultvalue = gh_default(personneid, qid, intid, assistant=assistant)
    IDCondition = gh_id(qid,cible,relation=relation)
    name = "q" + str(qid)

    if type == 'STRING':
        question = forms.Textarea(attrs={'rows':1, 'size': 30, 'id': IDCondition,'name': name,})
    else:
        question = forms.NumberInput(attrs={'size': 30, 'id': IDCondition,'name': name,})

    return question.render(name, defaultvalue)


@register.simple_tag
def gh_codetexte(qid,type, *args, **kwargs):
    personneid = kwargs['persid']
    relation = kwargs['relation']
    cible = kwargs['cible']
    assistant = kwargs['uid']
    varname = kwargs['varname']
    ancienne = ''
    personne = Personne.objects.get(pk=personneid)
    if personne.__dict__[varname] is not None:
        ancienne = 1

    IDCondition = gh_id(qid,cible,relation=relation)
    name = "q" + str(qid)
    if ancienne:
        return 'Already Encrypted data'
    else:
        question = forms.TextInput(attrs={'size': 30, 'id': IDCondition,'name': name,})
        return question.render(name, '')


####Pour les listes de valeurs qui etaient dans des tables
@register.simple_tag
def gh_table(qid,type, *args, **kwargs):
    #questid type
    personneid = kwargs['persid']
    relation = kwargs['relation']
    cible = kwargs['cible']
    assistant = kwargs['uid']
    intid = kwargs['intid']

    defaultvalue = gh_default(personneid, qid, intid, assistant=assistant)
    IDCondition = gh_id(qid,cible,relation=relation)
    typeq = Typequestion.objects.get(nom=type)
    listevaleurs = Listevaleur.objects.filter(typequestion=typeq)
    name = "q" + str(qid)
    if type == "VIOLATION":
        liste = gh_liste_tables(listevaleurs, 'violation')
    else:
        liste = gh_liste_tables(listevaleurs, 'reponse')

    question = forms.Select(choices = liste, attrs={'id': IDCondition,'name': name, })
    return question.render(name, defaultvalue)


@register.simple_tag
def gh_reponse(qid,b, *args, **kwargs):
    #Pour listes de valeurs specifiques a chaque question
    personneid = kwargs['persid']
    relation = kwargs['relation']
    cible = kwargs['cible']
    assistant = kwargs['uid']
    intid = kwargs['intid']

    defaultvalue = gh_default(personneid, qid, intid, assistant=assistant)
    IDCondition = gh_id(qid,cible,relation=relation)

    listevaleurs = Reponse.objects.filter(question_id=qid, )
    name = "q" + str(qid)
    liste = gh_liste_tables(listevaleurs, 'reponse')

    question = forms.Select(choices = liste, attrs={'id': IDCondition,'name': name, })
#   return question.render(name, defaultvalue)
    return enlevelisttag(question.render(name, defaultvalue))


@register.simple_tag
def gh_table_victime(qid,type, *args, **kwargs):
    #pour les tables dont la valeur a enregistrer n'est pas l'id mais la reponse_valeur (independant de la province)
    personneid = kwargs['persid']
    relation = kwargs['relation']
    cible = kwargs['cible']

    assistant = kwargs['uid']
    intid = kwargs['intid']

    defaultvalue = gh_default(personneid, qid, intid, assistant=assistant)
    IDCondition = gh_id(qid,cible,relation=relation)

    listevaleurs = Victime.objects.all()
    name = "q" + str(qid)
    liste = gh_liste_tables(listevaleurs, 'reponse')

    question = forms.Select(choices = liste, attrs={'id': IDCondition,'name': name, })

    return question.render(name, defaultvalue)


@register.simple_tag
def gh_table_valeurs_prov(qid,type, *args, **kwargs):
    #pour les tables dont la valeur a enregistrer n'est pas l'id mais la reponse_valeur
    #et dont la liste depend de la province
    province =  kwargs['province']
    personneid = kwargs['persid']
    relation = kwargs['relation']
    cible = kwargs['cible']
    typetable = {"ETABLISSEMENT": "etablissement", "MUNICIPALITE": "municipalite",}
    tableext = typetable[type]
    assistant = kwargs['uid']
    intid = kwargs['intid']

    defaultvalue = gh_default(personneid, qid, intid, assistant=assistant)
    IDCondition = gh_id(qid,cible,relation=relation)

    Klass = apps.get_model('gh', tableext)
    # Klass = apps.get_model('dataentry', typetable[b])
    listevaleurs = Klass.objects.filter(province__id = province)
    name = "q" + str(qid)
    liste = gh_liste_tables(listevaleurs, 'reponse')

    question = forms.Select(choices = liste, attrs={'id': IDCondition,'name': name, })

    return question.render(name, defaultvalue)


#Utlitaires generaux
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


def enlevelisttag(texte):
    ## pour mettre les radiobutton sur une seule ligne
    texte = re.sub(r"(<ul[^>]*>)",r"", texte)
    texte = re.sub(r"(<li[^>]*>)",r"", texte)
    texte = re.sub(r"(</li>)",r"", texte)
    return re.sub(r"(</ul>)",r" ", texte)


def gh_default(personneid, qid, intid, *args, **kwargs):
    ##fail la valeur par deffaut
    assistant = kwargs['assistant']
    ancienne = ''
    if Resultat.objects.filter(personne__id=personneid, question__id=qid, interview__id= intid, assistant__id=assistant).exists():
        ancienne = Resultat.objects.get(personne__id=personneid, question__id=qid, interview__id= intid, assistant__id=assistant).__str__()
    return ancienne


def gh_id(qid, cible, *args, **kwargs):
    ##fail l'ID pour javascripts ou autre
    relation = kwargs['relation']
    IDCondition = "q" + str(qid)
    if relation != '' and cible != '':
        IDCondition = 'row-{}X{}X{}'.format(qid, relation, cible)
    return IDCondition


def gh_liste_tables(listevaleurs,type):
    liste = [('', '')]
    for valeur in listevaleurs:
        if type == 'reponse':
            val = valeur.reponse_valeur
            nen = valeur.reponse_en
            liste.append((val, nen))
        elif type == 'violation':
            val = str(valeur.reponse_valeur)
            nen = val + ' - ' + valeur.reponse_en
            liste.append((val, nen))
    return liste


def gh_select_date(IDCondition, name):
    years = {x: x for x in range(1910, 2020)}
    years[''] = ''
    days = {x: x for x in range(1, 32)}
    days[''] = ''
    months = (('', ''), (1, 'Jan'), (2, 'Feb'), (3, 'Mar'), (4, 'Apr'), (5, 'May'), (6, 'Jun'), (7, 'Jul'), (8, 'Aug'),
              (9, 'Sept'), (10, 'Oct'), (11, 'Nov'), (12, 'Dec'))
    year = forms.Select(choices=years.items(), attrs={'id': IDCondition, 'name': name + '_year', })
    month = forms.Select(choices=months, attrs={'name': name + '_month'})
    day = forms.Select(choices=days.items(), attrs={'name': name + '_day'})
    return day, month, year


##### pour les questions de Personne
@register.simple_tag
def gh_creetextechar(qid, type, *args, **kwargs):

    name = "q" + str(qid)

    if type == 'STRING' or type == 'CODESTRING':
        question = forms.Textarea(attrs={'rows':1, 'size': 30, 'id': name,'name': name,})
    else:
        question = forms.NumberInput(attrs={'size': 30, 'id': name,'name': name,})

    return question.render(name, '')


@register.simple_tag
def gh_creedichou(qid, type, *args, **kwargs):

    name = "q" + str(qid)
    if type == "DICHO":
        liste = CHOIX_ON.items()
        question = forms.RadioSelect(choices = liste, attrs={'id': name,'name': name, })
    else:
        liste = CHOIX_ONUK.items()
        question = forms.RadioSelect(choices=liste, attrs={'id': name, 'name': name, })

    return enlevelisttag(question.render(name, ''))


@register.simple_tag
def gh_creedate(qid, *args, **kwargs):
    an = ''
    mois = ''
    jour = ''

    name = "q" + str(qid)
    day, month, year = gh_select_date(name, name)
    # name=q69_year, id=row...
    return year.render(name + '_year', an) + month.render(name + '_month',mois) + day.render(name + '_day',jour)


##############################
##Pour l'affichage des reponses aux questions dans les intruments
@register.simple_tag
def gh_lieedichou(a,b, *args, **kwargs):
    qid = a
    type = b
    personneid = kwargs['persid']
    assistant = kwargs['uid']
    intid = kwargs['intid']

    defaultvalue = gh_default(personneid, qid, intid, assistant=assistant)
    if defaultvalue:
        liste = CHOIX_ONUK
        reponse = liste[int(defaultvalue)]
    else:
        reponse = '---'
    return reponse


@register.simple_tag
def gh_lieetxt(qid,b, *args, **kwargs):
    personneid = kwargs['persid']
    assistant = kwargs['uid']
    intid = kwargs['intid']
    if Resultat.objects.filter(personne__id = personneid, question__id = qid, interview__id=intid, assistant__id = assistant).exists():
        reponse = Resultat.objects.get(personne__id = personneid, question__id = qid, interview__id=intid,
                                            assistant__id = assistant).__str__()
    else:
        reponse = '---'

    return reponse


@register.simple_tag
def gh_lieereponse(qid,b, *args, **kwargs):
    #Pour listes de valeurs specifiques a chaque question
    personneid = kwargs['persid']
    assistant = kwargs['uid']
    intid = kwargs['intid']

    defaultvalue = gh_default(personneid, qid, intid, assistant=assistant)
    if defaultvalue:
        reponse = Reponse.objects.get(question_id=qid,reponse_valeur=defaultvalue ).__str__()
    else:
        reponse = '---'

    return reponse


@register.simple_tag
def gh_liee_prov(qid,type, *args, **kwargs):
    #pour les tables dont la valeur a enregistrer n'est pas l'id mais la reponse_valeur
    #et dont la liste depend de la province
    province =  kwargs['province']
    personneid = kwargs['persid']
    typetable = {"ETABLISSEMENT": "etablissement", "MUNICIPALITE": "municipalite",}
    tableext = typetable[type]
    assistant = kwargs['uid']
    intid = kwargs['intid']

    defaultvalue = gh_default(personneid, qid, intid, assistant=assistant)

    if defaultvalue:
        Klass = apps.get_model('gh', tableext)
        reponse = Klass.objects.get(province__id=province, reponse_valeur=defaultvalue).__str__()
    else:
        reponse = '---'

    return reponse
##############################


@register.simple_tag
def refaitliste(texte):
    ## pour mettre les radiobutton sur une seule ligne
    texte = re.sub(r"(\])",r"", texte)
    texte = re.sub(r"(\[)",r"", texte)
    texte = re.sub(r"(,)",r"</br>", texte)
