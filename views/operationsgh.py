# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect
#from django.http import HttpResponse
from gh.models import Questionnaire, Personne, Interview, Resultatrepet, Question, Resultat, \
                     Instrument, Province, Reponse, User, Listevaleur, Victime
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.db.models import Q
import datetime
from dataentry.encrypter import Encrypter
import csv
from django.template import loader, Context
from django.http import HttpResponse, StreamingHttpResponse
from gh.gh_constants import LISTE_PROVINCE, LISTE_START, LISTE_HCR, CHOIX_ONUK, CHOIX_ON


@login_required(login_url=settings.LOGIN_URI)
def SelectDossier(request):
    #Pour selectionner personne (en fonction de la province)
    province = request.user.profile.province
    if province == 10:
        personnes = Personne.objects.all()
    else:
        personnes = Personne.objects.filter(province_id=province)

    if request.method == 'POST':
        if request.POST.get('personneid') == '':
            messages.add_message(request, messages.ERROR, 'You have forgotten to chose at least one field')
            return render(
                request,
                'choixgh.html',
                    {
                    'personnes': personnes,
                    'interviews': Interview.objects.all(),
                    'provinces': Province.objects.all()
                    }
                )
        if 'Clinical File' in request.POST:
            return rendu_questionnaire(request, 200)
        elif 'Interview Guide 1' in request.POST:
            return rendu_questionnaire(request, 10)
        elif 'Interview Guide 2' in request.POST:
            return rendu_questionnaire(request, 15)
        elif 'Instruments' in request.POST:
            return redirect(saveinstrugh,
                            request.POST.get('interviewid'),
                            request.POST.get('personneid'),
                            )
        elif 'Scales' in request.POST:
            return rendu_questionnaire(request, 101)
        elif 'Sensible' in request.POST:
            return rendu_questionnaire(request, 300)
        elif 'WorkTLBF' in request.POST:
            return rendu_questionnairerep(request, 4)
        elif 'HousingTLFB' in request.POST:
            return rendu_questionnairerep(request, 3)
        elif 'Newfile' in request.POST:
            return redirect(creerdossier)
        elif 'Voirliste' in request.POST:
            return redirect(listedossiers, request.POST.get('provinceid'),)
        elif 'PrintFile' in request.POST:
            return redirect(gh_csv,request.POST.get('personneid'),)
    else:
        return render(
                    request,
                    'choixgh.html',
                    {
                        'personnes': personnes,
                        'interviews': Interview.objects.all(),
                        'provinces': Province.objects.all(),
                        'message':'welcome'
                    }
                )


def rendu_questionnairerep(request, questionnaireid):
    return redirect(saveghrepet,
                    questionnaireid,
                    request.POST.get('interviewid'),
                    request.POST.get('personneid'),
                    )


def rendu_questionnaire(request, questionnaireid):
    return redirect(savegh,
                    questionnaireid,
                    request.POST.get('interviewid'),
                    request.POST.get('personneid'),
                    )


@login_required(login_url=settings.LOGIN_URI)
def creerdossier(request):
    qid = 500
    questionstoutes = Question.objects.filter(questionnaire__id=qid)
    if request.method == 'POST':
        reponses = {}
        for question in questionstoutes:
            if question.typequestion.nom == 'DATE' or question.typequestion.nom == 'CODEDATE':
                an = request.POST.get('q{}_year'.format(question.id))
                if an != "":
                    mois = request.POST.get('q{}_month'.format(question.id))
                    jour = request.POST.get('q{}_day'.format(question.id))
                    reponseaquestion = "{}-{}-{}".format(an, mois, jour)
                else:
                    reponseaquestion = ''
            else:
                reponseaquestion = request.POST.get('q' + str(question.id))

            if reponseaquestion:
                if question.typequestion.nom == 'CODEDATE' or question.typequestion.nom == 'CODESTRING':
                    reponseaquestion = encode_donnee(reponseaquestion)
                reponses[question.varname] = reponseaquestion
        prov = LISTE_PROVINCE[request.user.profile.province]
        reponses['personne_code'] = "{}_{}{}_P".format(prov,reponses['PartP'][:3], reponses['date_consentement'])
        Personne.objects.create(
                                personne_code = reponses['personne_code'],
                                province_id = request.user.profile.province,
                                date_consentement = reponses['date_consentement'],
                                PartN = reponses['PartN'],
                                PartP = reponses['PartP'],
                                VerdictDate = reponses['VerdictDate'],
                                LibeDate = reponses['LibeDate'],
                                DDN = reponses['DDN'],
                                Consent = reponses['Consent'],
                                ConsentAudio = reponses['ConsentAudio'],
                                ConsentFamille = reponses['ConsentFamille'],
                                ConsentSuivi = reponses['ConsentSuivi'],
                                assistant_id = request.user.id
                                )
        textefin=  "{}  has been created".format(reponses['personne_code'])
        messages.add_message(request, messages.ERROR, textefin)
        return redirect('SelectDossier')
    else:
        return render(request, 'createghh.html',
                      {
                          'questions': questionstoutes,
                      }
                      )


@login_required(login_url=settings.LOGIN_URI)
def savegh(request, qid, intid, pid):
    # genere le questionnaire demande NON repetitif
    ascendancesF, ascendancesM, questionstoutes, questions = genere_questions(qid, intid)
    questionfin = Question.objects.get(questionno=qid, questionnaire__id=1000)
    nomcode = Personne.objects.get(id=pid).__str__()
    questionnaire = Questionnaire.objects.get(id=qid).__str__()
    interview = Interview.objects.get(pk=intid).__str__()
    if request.method == 'POST':
        for question in questionstoutes:
            if question.typequestion.nom == 'DATE' or question.typequestion.nom == 'CODEDATE' or \
                            question.typequestion.nom == 'DATEH':
                an = request.POST.get('q{}_year'.format(question.id))
                if an != "":
                    mois = request.POST.get('q{}_month'.format(question.id))
                    jour = request.POST.get('q{}_day'.format(question.id))
                    reponseaquestion = "{}-{}-{}".format(an, mois, jour)
                else:
                    reponseaquestion = ''
            else:
                reponseaquestion = request.POST.get('q' + str(question.id))
            if reponseaquestion:
                if question.typequestion.nom == 'CODEDATE' or question.typequestion.nom == 'CODESTRING':
                    reponseaquestion = encode_donnee(reponseaquestion)
                    personne = Personne.objects.get(pk=pid)
                    personne.__dict__[question.varname] = reponseaquestion
                    personne.save()
                else:
                    Resultat.objects.update_or_create(
                        personne_id=pid, question=question, interview_id=intid, assistant=request.user,
                        # (('personne', 'question', 'interview', 'assistant'),)
                        defaults={
                            'reponse_texte': reponseaquestion,
                            'province_id': request.user.profile.province,
                        }
                    )
        now = datetime.datetime.now().strftime('%H:%M:%S')
        messages.add_message(request, messages.WARNING, 'Data saved at ' + now)

    sectionterminee = cherchefin(questionfin, pid, intid, request.user.id, request.user.profile.province)
    if sectionterminee:
        textefin=  "{} : {} has been closed  for {}".format(nomcode, questionnaire, interview )
        messages.add_message(request, messages.WARNING, textefin)
        return redirect('SelectDossier')
    else:
        return render(request, 'savegh.html',
                      {
                          'qid': qid,
                          'intid': intid,
                          'pid': pid,
                          'questions': questions,
                          'ascendancesM': ascendancesM,
                          'ascendancesF': ascendancesF,
                          'code': nomcode,
                          'questionnaire': questionnaire,
                          'questionfin': questionfin,
                          'interview': interview
                      }
                      )


@login_required(login_url=settings.LOGIN_URI)
def saveinstrugh(request, intid, pid):
    # genere le questionnaire demande NON repetitif
    qid = 100
    interview = Interview.objects.get(pk=intid).__str__()
    nomcode = Personne.objects.get(id=pid).__str__()
    questionnaire = Questionnaire.objects.get(id=100).__str__()
    questionfin = Question.objects.get(questionno=100, questionnaire__id=1000)
    if request.method == 'POST':
        if intid == '1':
            questionstoutes = Question.objects.filter(
                Q(questionno=str(qid), questionnaire__id=1000) | Q((Q(phase=1) | Q(phase=3)), questionnaire__id=qid))
        else:
            questionstoutes = Question.objects.filter(
                Q(questionno=str(qid), questionnaire__id=1000) | Q((Q(phase=2) | Q(phase=3)), questionnaire__id=qid))
        for question in questionstoutes:
            reponseaquestion = request.POST.get('q' + str(question.id))
            if reponseaquestion:
                Resultat.objects.update_or_create(
                    personne_id=pid, question=question, interview_id=intid, assistant=request.user,
                    # (('personne', 'question', 'interview', 'assistant'),)
                    defaults={
                        'reponse_texte': reponseaquestion,
                        'province_id': request.user.profile.province,
                    }
                )
        now = datetime.datetime.now().strftime('%H:%M:%S')
        messages.add_message(request, messages.WARNING, 'Data saved at ' + now)
    # Pour les instruments necessitant la reference aux reponses aux questions
    if intid == '1':
        instruments = Instrument.objects.filter((Q(phase=1) | Q(phase=3)))
    else:
        instruments = Instrument.objects.filter((Q(phase=2) | Q(phase=3)))
    return render(request, 'saveinstrugh.html',
              {
                  'qid': qid,
                  'intid': intid,
                  'pid': pid,
                  'instruments': instruments,
                  'code': nomcode,
                  'questionnaire': questionnaire,
                  'questionfin': questionfin,
                  'interview': interview
              }
              )


def genere_questions(qid, intid):
    # interview (intid) 1 phase=1 or phase=3 pour autres entrevues: phase=2 or phase=3
    phase=1 if intid == '1' else 2
    q = (Q(phase=phase) | Q(phase=3)) & Q(questionnaire__id=qid)
    questions = Question.objects.filter(q)

    enfants = questions.select_related('typequestion', 'parent').filter(question__parent__id__gt=1)
    ascendancesM = {rquestion.id for rquestion in questions.select_related('typequestion').filter(pk__in=enfants)}
    ascendancesF = set()  # liste sans doublons
    for rquestion in questions:
        for fille in questions.select_related('typequestion').filter(parent__id=rquestion.id):
            # #va chercher si a des filles (question_ fille)
            ascendancesF.add(fille.id)
    return ascendancesF, ascendancesM, Question.objects.filter(Q(questionno=str(qid), questionnaire__id=1000) | q), questions


@login_required(login_url=settings.LOGIN_URI)
def saveghrepet(request, qid, intid, pid):#(request, qid, pid, province):
    ascendancesF, ascendancesM, questionstoutes, questions = genere_questions(qid,intid)
    nomcode = Personne.objects.get(id=pid).__str__()
    questionnaire = Questionnaire.objects.get(id=qid).__str__()
    interview = Interview.objects.get(reponse_valeur=intid).__str__()
    if request.method == 'POST':
        actions = request.POST.keys()
        for action in actions:
            if action.startswith('remove_'):
                x = action[len('remove_'):]
                Resultatrepet.objects.filter(personne__id=pid,questionnaire__id=qid,
                                             interview__id=intid, fiche=x, assistant=request.user).delete()
                messages.add_message(request, messages.ERROR, 'Card # ' + str(x) + ' removed')
                continue
            elif action.startswith('current_') or action.startswith('add_'):
                if action.startswith('current_'):
                    x = action[len('current_'):]
                else:
                    x = action[len('add_'):]
                    enregistrement = Resultatrepet.objects.filter(
                                        personne__id=pid,
                                        assistant=request.user,
                                        interview__id = intid,
                                        questionnaire__id=qid).order_by('-fiche').first()
                    ordre = enregistrement.fiche + 1
                    Resultatrepet.objects.create(
                                personne_id=pid,
                                assistant_id=request.user.id,
                                questionnaire_id=qid,
                                interview_id=intid,
                                question_id=1,
                                fiche=ordre,
                                reponsetexte= 10000,
                                province_id=request.user.profile.province
                            )
                    messages.add_message(request, messages.WARNING, '1 Card added ')

                for question in questionstoutes:
                    if question.typequestion_id == 5 or question.typequestion_id == 60:
                        an = request.POST.get('q{}Z_Z{}_year'.format(question.id, x))
                        if an != "":
                            mois = request.POST.get('q{}Z_Z{}_month'.format(question.id, x))
                            jour = request.POST.get('q{}Z_Z{}_day'.format(question.id, x))
                            reponseaquestion = "{}-{}-{}".format(an, mois, jour)
                        else:
                            reponseaquestion = ''
                    else:
                        reponseaquestion = request.POST.get('q{}Z_Z{}'.format(question.id, x))
                    if reponseaquestion:
                        #personne questionnaire question interview fiche assistant
                        Resultatrepet.objects.update_or_create(
                                            personne_id=pid,
                                            questionnaire_id=qid,
                                            question_id=question.id,
                                            interview_id=intid,
                                            fiche=x,
                                            assistant_id=request.user.id,
                                            # update these fields, or create a new object with these values
                                            defaults={
                                                'reponsetexte': reponseaquestion,
                                                      'province_id': request.user.profile.province,
                                                      }
                                        )
                now = datetime.datetime.now().strftime('%H:%M:%S')
                messages.add_message(request, messages.WARNING, 'Data saved at ' + now)

    else:
        if Resultatrepet.objects.filter(personne_id=pid, assistant_id=request.user.id, questionnaire_id=qid, interview_id=intid).count() == 0:
            Resultatrepet.objects.create(
                                personne_id=pid,
                                assistant_id=request.user.id,
                                questionnaire_id=qid,
                                interview_id=intid,
                                question_id=1,
                                fiche=1,
                                reponsetexte=10000,
                                province_id=request.user.profile.province
                            )

    compte, fiches = fait_pagination(pid, qid, intid, request)
    return render(request, 'saveghrepet.html',
                      {
                          'qid': qid,
                          'intid': intid,
                          'pid': pid,
                          'questions': questionstoutes,
                          'ascendancesM': ascendancesM,
                          'ascendancesF': ascendancesF,
                          'fiches': fiches,
                          'compte': compte,
                          'code': nomcode,
                          'questionnaire': questionnaire,
                          'interview': interview
                      }
                      )


@login_required(login_url=settings.LOGIN_URI)
def listedossiers(request, province):
    personnes = Personne.objects.filter(province_id=province)
    interviews = Interview.objects.all()
    date = Question.objects.get(varname='DATEInterview')

    questionsfin = Question.objects.filter(questionnaire__id=1000)


    toutesleslignes = ([])
    entete = []
    ligne = []
    entete.append('Code')
    for interview in interviews:
        entete.append(interview.reponse_en)
        entete.append('Status')

    toutesleslignes.append(entete)
    for personne in personnes:
        ligne = [personne.personne_code]
        for interview in interviews:
            resultat = Resultat.objects.filter(question__id = date.id,
                                                  interview__id=interview.id,
                                                  personne__id=personne.id,
                                                  province__id=personne.province_id).first()
            if resultat:
                ar = resultat.assistant.id
                ligne.append(resultat.reponse_texte)
                fins = []
                for fin in questionsfin:
                    sectionterminee = cherchefin(fin, personne.id, interview.id, resultat.assistant.id, personne.province_id)
                    if sectionterminee:
                        fins.append(fin.questionen)

                ligne.append(fins)
            else:
                ligne.append('-')
                ligne.append('-')

        toutesleslignes.append(ligne)

#    state (reponses a question fin) pour chaque entrevue, + AR

    return render(request, 'saveghtest.html',
                  {
                      'lignes': toutesleslignes
                   })


def fait_pagination(pid, qid, intid, request):
    donnees = Resultatrepet.objects.order_by('fiche').filter(personne__id=pid,questionnaire__id=qid,
                                             interview__id=intid, assistant=request.user
                        ).values_list('fiche', flat=True).distinct()
    #donnees = fiche_list.values_list('fiche', flat=True).distinct()
    compte = donnees.count()
    paginator = Paginator(donnees, 3)  # Show 3 fiches par page
    page = request.GET.get('page')
    try:
        fiches = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        fiches = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        fiches = paginator.page(paginator.num_pages)
    return compte, fiches


def encode_donnee(message):
    PK_path = settings.PUBLIC_KEY_PATH
    PK_name = settings.PUBLIC_KEY_GH
    e = Encrypter()
    #public_key = e.read_key(PK_path + 'Manitoba_public.pem')
    public_key = e.read_key(PK_path + PK_name)
    return e.encrypt(message,public_key)



def cherchefin(questionfin, pid, intid, assistant, province):
    if Resultat.objects.filter(personne_id=pid, question_id=questionfin.id, interview_id=intid, assistant_id=assistant, province_id=province).exists():
        sectionterminee = Resultat.objects.get(personne_id=pid, question_id=questionfin.id, interview_id=intid,
                            assistant_id=assistant)
        if sectionterminee.reponse_texte == '1':
            return True
    return False


class Echo(object):
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


@login_required(login_url=settings.LOGIN_URI)
def gh_csv(request, pid):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="exportation.txt"'
    # The data is hard-coded here, but you could load it from a database or
    # some other source.

    personne = Personne.objects.get(pk=pid)
    csv_data = ([])
    debut = []
    debut.append('Province & File code')
    debut.append(personne.province.reponse_en)
    debut.append(personne.personne_code)
    csv_data.append(debut)
    questionnaires = Questionnaire.objects.filter(id__gt=1).exclude(id=300)
    assistants = User.objects.all()
    entrevues = Interview.objects.all()
    for assistant in assistants:
        for entrevue in entrevues:
            if Resultat.objects.filter(personne__id=pid, assistant_id=assistant.id, interview_id=entrevue.id).exists():
                for questionnaire in questionnaires:
                    ligne2 = []
                    questions = Question.objects.filter(questionnaire_id=questionnaire.id).order_by('questionno')
                    ligne2.append(assistant.username)
                    ligne2.append(questionnaire.nom_en)
                    ligne2.append(entrevue.reponse_en)
                    csv_data.append(ligne2)
                    if questionnaire.id != 4 and questionnaire.id != 3:
                        for question in questions:
                            ligne = []
                            donnee = Resultat.objects.filter(personne__id=pid, question__id=question.id, assistant_id=assistant.id,interview_id=entrevue.id )
                            if donnee:
                                ligne.append(question.varname)
                                ligne.append(question.questionen)
                                reponse = fait_reponsegh(donnee[0].reponse_texte, question, personne.province)
                                ligne.append(reponse)
                            if ligne != []:
                                csv_data.append(ligne)
                    else:
                        donnees = Resultatrepet.objects.order_by().filter(personne__id=pid, assistant__id=assistant.id,
                                                                          interview_id=entrevue.id, questionnaire__id=questionnaire.id).values_list('fiche',
                                                                                                                  flat=True).distinct()
                        compte = donnees.count()
                        ligne2 = []
                        ligne2.append(str(compte) + ' different entries for '+ questionnaire.nom_en)
                        csv_data.append(ligne2)
                        for i in donnees:
                            ligne2 = []
                            ligne2.append(questionnaire.nom_en + ' card number ' + str(i))
                            csv_data.append(ligne2)
                            for question in questions:
                                try:
                                    donnee = Resultatrepet.objects.get(personne_id=pid, question_id=question.id,interview_id=entrevue.id, assistant_id=assistant.id, fiche=i)
                                except Resultatrepet.DoesNotExist:
                                    donnee = None
                                if donnee:
                                    ligne = []
                                    ligne.append(question.varname)
                                    ligne.append(question.questionen)
                                    #reponse = fait_reponsegh(donnee.reponse_texte, question, personne.province)
                                    ligne.append(donnee.reponsetexte)

                                csv_data.append(ligne)

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer, dialect="excel-tab")
    response = StreamingHttpResponse((writer.writerow(row) for row in csv_data),
                                     content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="' + str(personne.personne_code) + '.txt"'
    return response


def fait_reponsegh(reponsetexte, question, province):
    if question.typequestion.nom == 'CATEGORIAL':
        resultat = Reponse.objects.get(question=question.id,reponse_valeur=reponsetexte).__str__()
    elif question.typequestion.nom == 'DICHO':
         resultat = CHOIX_ON[int(reponsetexte)]
    elif question.typequestion.nom == "BOOLEAN" or question.typequestion.nom == "DICHOU"\
        or question.typequestion.nom == "DICHON":
         resultat = CHOIX_ONUK[int(reponsetexte)]
    elif question.typequestion.nom in ("HCR20","START","RAS","CSI","VRAG",
        "SCID","SOS","HCRREL","PROVINCE","PAYS","LANGUE","POSOLOGIE","VIOLATION"):
        resultat = Listevaleur.objects.get(typequestion__id=question.typequestion.id , reponse_valeur = int(reponsetexte))
    elif question.typequestion.nom == "VICTIME":
        resultat = Victime.objects.get(reponse_valeur = int(reponsetexte))
    elif question.typequestion.nom == "CODESTRING" or question.typequestion.nom == "CODEDATE":
        resultat = "Data encrypted"
    else:
        resultat = reponsetexte
    return resultat


@login_required(login_url=settings.LOGIN_URI)
def exportstatsgh(request):
    return render(request, 'choixghstats.html')