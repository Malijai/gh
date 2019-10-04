# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect
from gh.models import Questionnaire, Personne, Interview, Resultatrepet, Question, Resultat, User
from accueil.models import Projet
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
import datetime
import csv
import os
from django.template import loader
from django.http import HttpResponse
from dataentry.encrypter import Encrypter


def extraction_requete(intid, qid):
    phase = 1 if intid == '1' else 2
    q = (~Q(typequestion__id=7) & ~Q(typequestion__id=100) & (Q(phase=phase) | Q(phase=3)) & Q(questionnaire__id=qid))
    questions = Question.objects.filter(q).order_by('questionno')
    usersgh = [{'id': p.user.id, 'username': p.user.username} for p in Projet.objects.filter(projet=Projet.GH)]
    return questions, usersgh


@login_required(login_url=settings.LOGIN_URI)
def gh_resultats_tous(request, qid, intid):
    # Create the HttpResponse object with the appropriate CSV header.
    now = datetime.datetime.now().strftime('%Y_%m_%d')
    entrevue = "Baseline" if intid == '1' else "FU"
    filename = 'Datas_{}{}_{}.csv'.format(qid, entrevue, now)
    questionnaire = Questionnaire.objects.filter(pk=qid)
    if intid == '1':
        entrevues = Interview.objects.filter(pk=1)
    else:
        entrevues = Interview.objects.filter(Q(pk=200) | Q(pk=300))

    questions, usersgh = extraction_requete(intid, qid)

    csv_data = ([])
    debut = []
    debut.append('personne_ID')
    debut.append('Assistant_ID')
    debut.append('Entrevue_ID')
    debut.append('Questionnaire')
    for question in questions:
        debut.append(question.varname)

    csv_data.append(debut)

    for assistant in usersgh:
        for entrevue in entrevues:
            personnes = [p['personne'] for p in \
                Resultat.objects.values('personne').filter(
                    assistant__id=assistant['id'], interview=entrevue
                ).annotate(pc=Count('personne', distinct=True)) ]
            for personne_id in personnes:
                if Resultat.objects.filter(personne__id=personne_id, assistant__id=assistant['id'], interview=entrevue).exists():
                    # print(personne.id, ' - ', assistant.id, ' - ', entrevue.id)
                    ligne = []
                    ligne.append(personne_id)
                    ligne.append(assistant['id'])
                    ligne.append(entrevue.id)
                    ligne.append(qid)
                    for question in questions:
                        try:
                            donnee = Resultat.objects.get(personne__id=personne_id, assistant__id=assistant['id'], interview=entrevue, question=question)
                        except Resultat.DoesNotExist:
                            donnee = None
                        if donnee:
                            ligne.append(donnee.reponse_texte)
                            # ligne.append(donnee.reponse_texte.encode('utf-8'))
                        else:
                            ligne.append('')
                    csv_data.append(ligne)
    # MEDIA_DATAURL
    with open(os.path.join(settings.MEDIA_DATA, filename), 'w', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
        for row in csv_data:
            writer.writerow(row)

    return render(request,'donnee.html',{'filename': filename, 'MEDIA_DATAURL': settings.MEDIA_DATAURL})


def gh_res_repet_tous(request, qid):
    # Create the HttpResponse object with the appropriate CSV header.
    now = datetime.datetime.now().strftime('%Y_%m_%d')
    filename = 'Datas_{}FU_{}.csv'.format(qid, now)
    questionnaire = Questionnaire.objects.filter(pk=qid)
    entrevues = Interview.objects.filter(Q(pk=200) | Q(pk=300))

    questions, usersgh = extraction_requete(2, qid)

    csv_data = ([])
    debut = []
    debut.append('personne_ID')
    debut.append('Assistant_ID')
    debut.append('Entrevue_ID')
    debut.append('Questionnaire')
    debut.append('Fiche_ID')
    for question in questions:
        debut.append(question.varname)

    csv_data.append(debut)

    for assistant in usersgh:
        for entrevue in entrevues:
            personnes = {p['personne'] for p in \
                Resultatrepet.objects.values('personne').filter(
                    assistant__id=assistant['id'], interview=entrevue, questionnaire__id=qid)}
            for personne_id in personnes:
                if Resultat.objects.filter(personne__id=personne_id, assistant__id=assistant['id'], interview=entrevue).exists():
                    fiches = Resultatrepet.objects.filter(personne__id=personne_id, assistant__id=assistant['id'],
                                                                      interview=entrevue, questionnaire__id=qid).values_list(
                                                                        'fiche', flat=True).distinct().order_by()

                    for fiche in fiches:
                        ligne = []
                        ligne.append(personne_id)
                        ligne.append(assistant['id'])
                        ligne.append(entrevue.id)
                        ligne.append(qid)
                        ligne.append(fiche)
                        for question in questions:
                            try:
                                donnee =  Resultatrepet.objects.get(personne__id=personne_id, assistant__id=assistant['id'], interview=entrevue, question=question, fiche=fiche)
                            except Resultatrepet.DoesNotExist:
                                donnee = None
                            if donnee:
                                ligne.append(donnee.reponsetexte)
                                # ligne.append(donnee.reponse_texte.encode('utf-8'))
                            else:
                                ligne.append('')
                        csv_data.append(ligne)
    # MEDIA_DATAURL
    with open(os.path.join(settings.MEDIA_DATA, filename), 'w', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
        for row in csv_data:
            writer.writerow(row)

    return render(request,'donnee.html',{'filename': filename, 'MEDIA_DATAURL': settings.MEDIA_DATAURL})


def fait_entete_spss(request, qid, intid):
    entrevue = "Baseline" if intid == '1' else "FU"
    response = HttpResponse(content_type='text/csv')
    filename1 = '"enteteSPSS_' + str(qid) + entrevue + '.sps"'
    response['Content-Disposition'] = 'attachment; filename={}'.format(filename1)
    questions, usersgh = extraction_requete(intid, qid)

    t = loader.get_template('spss_syntaxe.txt')
    response.write(t.render({'questions': questions, 'users': usersgh}))
    return response


def fait_entete_stata(request, qid, intid):
    entrevue = "Baseline" if intid == '1' else "FU"
    response = HttpResponse(content_type='text/csv')
    filename1 = '"enteteSTATA_' + str(qid) + entrevue + '.txt"'
    response['Content-Disposition'] = 'attachment; filename={}'.format(filename1)
    questions, usersgh = extraction_requete(intid, qid)
    phase = 1 if intid == '1' else 2
    q = (~Q(typequestion__id=7) & ~Q(typequestion__id=100) & (Q(phase=phase) | Q(phase=3)) & Q(questionnaire__id=qid))
    typepresents = Question.objects.values('typequestion__nom').order_by().filter(q).annotate(tqcount=Count('typequestion__nom'))

    t = loader.get_template('stata_syntaxe.txt')
    response.write(t.render({'questions': questions, 'typequestions': typepresents, 'users': usersgh}))
    return response


def gh_decrypte_personne(request):
    personnes = Personne.objects.filter(id__lte=176)
    # Create the HttpResponse object with the appropriate CSV header.
    now = datetime.datetime.now().strftime('%Y_%m_%d')
    filename = 'Protected_{}.csv'.format(now)
    questions = Question.objects.filter(questionnaire_id=500)

    csv_data = ([])
    debut = []
    debut.append('personne_ID')
    debut.append('Assistant_ID')

    for question in questions:
        debut.append(question.varname)
    csv_data.append(debut)

    for personne in personnes:

        PK_path = settings.PRIVATE_KEY_PATH
        PK_name = settings.PRIVATE_KEY_GH
        e = Encrypter()
        priv_Key = e.read_key(PK_path + PK_name)
        DDN_dc = e.decrypt(personne.DDN, priv_Key)
        Verdict_dc =  e.decrypt(personne.VerdictDate, priv_Key)
        print(personne.id)
        ligne = []
        ligne.append(personne.id)
        ligne.append(personne.assistant.id)
        ligne.append(personne.province)
        ligne.append(DDN_dc)
        ligne.append(Verdict_dc)

        csv_data.append(ligne)

    # MEDIA_DATAURL
    with open(os.path.join(settings.MEDIA_DATA, filename), 'w', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
        for row in csv_data:
            writer.writerow(row)

    return render(request,'donnee.html',{'filename': filename, 'MEDIA_DATAURL': settings.MEDIA_DATAURL})

