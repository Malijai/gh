from django.conf.urls import url
from .views import SelectDossier, savegh, saveghrepet, saveinstrugh, creerdossier, listedossiers, \
                    gh_csv, ghquestions_pdf, gh_resultats_tous, fait_entete_spss, fait_entete_stata, exportstatsgh, \
                    gh_res_repet_tous, gh_decrypte_personne
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^$', SelectDossier, name='SelectDossier'),
    url(r'^savegh/(?P<qid>[-\w]+)/(?P<intid>[-\w]+)/(?P<pid>[-\w]+)/$', savegh, name='savegh'),
    url(r'^saveghrepet/(?P<qid>[-\w]+)/(?P<intid>[-\w]+)/(?P<pid>[-\w]+)/$', saveghrepet, name='saveghrepet'),
    url(r'^saveinstrugh/(?P<intid>[-\w]+)/(?P<pid>[-\w]+)/$', saveinstrugh, name='saveinstrugh'),
    url(r'^new/$', creerdossier, name='creerdossier'),
    url(r'^liste/(?P<province>[-\w]+)/$', listedossiers, name='listedossiers'),
    url(r'^txt/(?P<pid>[-\w]+)', gh_csv, name='gh_csv'),
    url(r'^datas/(?P<qid>[-\w]+)/(?P<intid>[-\w]+)/$', gh_resultats_tous, name='gh_csv_tous'),
    url(r'^SPSSsyntax/(?P<qid>[-\w]+)/(?P<intid>[-\w]+)/$', fait_entete_spss, name='fait_entete_spss'),
    url(r'^STATAsyntax/(?P<qid>[-\w]+)/(?P<intid>[-\w]+)/$', fait_entete_stata, name='fait_entete_stata'),
    url(r'^exportstats/$', exportstatsgh, name='exportstatsgh'),
    url(r'^datasrepet/(?P<qid>[-\w]+)/$', gh_res_repet_tous, name='gh_res_repet_tous'),
    url(r'^decrypte/$', gh_decrypte_personne, name='gh_decrypte_personne'),
    url(r'^pdf/(?P<pk>[-\w]+)/(?P<intid>[-\w]+)/$', ghquestions_pdf, name='dogh_questions_pdf'),
]
