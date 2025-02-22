=============================
ITA - Dichiarazione Intrastat
=============================

.. 
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! This file is generated by oca-gen-addon-readme !!
   !! changes will be overwritten.                   !!
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! source digest: sha256:f900acbf3f17aaa915e8c260680ec67754f71899aed4db599d7e758c005e3069
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-OCA%2Fl10n--italy-lightgray.png?logo=github
    :target: https://github.com/OCA/l10n-italy/tree/16.0/l10n_it_intrastat_statement
    :alt: OCA/l10n-italy
.. |badge4| image:: https://img.shields.io/badge/weblate-Translate%20me-F47D42.png
    :target: https://translation.odoo-community.org/projects/l10n-italy-16-0/l10n-italy-16-0-l10n_it_intrastat_statement
    :alt: Translate me on Weblate
.. |badge5| image:: https://img.shields.io/badge/runboat-Try%20me-875A7B.png
    :target: https://runboat.odoo-community.org/builds?repo=OCA/l10n-italy&target_branch=16.0
    :alt: Try me on Runboat

|badge1| |badge2| |badge3| |badge4| |badge5|

**Italiano**

Questo modulo si occupa di generare la dichiarazione Intrastat e le
relative stampe.

Le specifiche per tali stampe e i file da inviare sono in
https://www.adm.gov.it/portale/-/determinazione-n-c2-b0-493869-del-23-dicembre-2021-nuovi-modelli-degli-elenchi-riepilogativi-delle-cessioni-e-degli-acquisti-intracomunitari-di-beni-e-delle-prestazioni-di-servizio-rese-e-ricevute-in-ambito-comunitario-periodi-di-riferimento-decorrenti-da.

**Table of contents**

.. contents::
   :local:

Usage
=====

**Italiano**

**Dichiarazione Intrastat**

Accedere a *Fatturazione/Contabilità → Contabilità → Intrastat →
Dichiarazioni Intrastat* ed utilizzare il pulsante «Crea» per creare una
nuova dichiarazione.

N.B.: il menù "Contabilità" è visibile solo se vengono abilitate le
funzionalità contabili complete.

Nella parte superiore della maschera, inserire i dati:

-  *Azienda*: popolato in automatico con il nome dell'azienda;
-  *Partita IVA contribuente*: la partita IVA, popolata in automatico
   con il nome dell'azienda;
-  *Data di presentazione*: popolata in automatico con la data corrente;
-  *Anno*: l'anno di presentazione, scelto dal menù a tendina che
   visualizza gli anni fiscali configurati a sistema;
-  *Tipo periodo*: l’orizzonte temporale a cui fa riferimento la
   dichiarazione, scelto da menù a tendina con le voci “Mese” o
   “Trimestre”;
-  *Periodo*: il periodo temporale a cui fa riferimento la
   dichiarazione. Inserire il numero del mese (es. 9 per settembre, se
   nel campo "Tipo periodo" è stato selezionato “Mese”, oppure in numero
   del trimestre (es: 1 per il trimestre gennaio-marzo), se nel campo
   "Tipo periodo" è stato selezionato “Trimestre”;
-  *Caselle di selezione “Cessioni” e “Acquisti”*: da selezionare in
   base alla tipologia di operazioni che si vogliono inserire nella
   dichiarazione;
-  *Numero*: progressivo della dichiarazione proposto in automatico dal
   sistema;
-  *Tipo di contenuto*: selezionare la voce di competenza dal menù a
   tendina;
-  *Casi speciali*: selezionare la voce di competenza dal menù a
   tendina;
-  *Sezione doganale*: selezionare la voce di riferimento dal menù a
   tendina.

Inseriti e salvati i dati, utilizzare il pulsante «Ricalcola» per
popolare la dichiarazione. Per ciascuna scheda (”Cessioni” e “Acquisti”)
verranno inserite nelle sezioni di riferimento:

-  Cessioni:

   -  Cessione beni - Sezione 1 → fatture di vendita di merci
   -  Rettifica beni - Sezione 2 → note di credito su vendita merci
   -  Cessione servizi - Sezione 3 → fatture di vendita di servizi
   -  Rettifica servizi - Sezione 4 → note di credito su vendita servizi

-  Acquisti:

   -  Acquisto beni - Sezione 1 → fatture di acquisto di merci
   -  Rettifica beni - Sezione 2 → note di credito su acquisto merci
   -  Acquisto servizi - Sezione 3 → fatture di acquisto di servizi
   -  Rettifica servizi - Sezione 4 → note di credito su acquisto
      servizi

I dati presi dalle fatture e dalle note di credito indicate come
soggette ad Intrastat, relative al periodo di riferimento.

N.B.: i record presenti nelle schede "Rettifica beni - Sezione 2" e
"Rettifica servizi - Sezione 4", sia per gli acquisti che per le
vendite, vanno modificati per inserire i dati obbligatori mancanti.

Inseriti i dati e salvata la dichiarazione, è possibile procedere
all’elaborazione dei file da inviare all’Agenzia delle Dogane tramite
l’apposito pulsante «Esporta file».

Il pulsante fa partire una procedura guidata, che permette di scegliere
quale tipo di file estrarre:

-  file di invio (complessivo)
-  file acquisti.cee
-  file cessioni.cee

Il file potrà essere scaricato tramite l’apposito link visualizzato
nella maschera della procedura guidata. Di seguito un esempio per lo
scaricamento del file cessioni.cee (il nome del file da scaricare è
SCAMBI.CEE).

Dalla voce *Stampa* è possibile generare gli elenchi riepilogativi delle
cessioni o degli acquisti intracomunitari: modello INTRA-1, INTRA-1 Bis,
INTRA-1 Ter, INTRA-2, INTRA-2 Bis.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/l10n-italy/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us to smash it by providing a detailed and welcomed
`feedback <https://github.com/OCA/l10n-italy/issues/new?body=module:%20l10n_it_intrastat_statement%0Aversion:%2016.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
-------

* Openforce
* Link IT srl
* Agile Business Group

Contributors
------------

-  Alessandro Camilli
-  Lorenzo Battistini
-  Lara Baggio <lbaggio@linkgroup.it>
-  Glauco Prina <gprina@linkgroup.it>
-  Sergio Zanchetta <https://github.com/primes2h>
-  Antonio Maria Vigliotti <antoniomaria.vigliotti@gmail.com>
-  Alex Comba <alex.comba@agilebg.com>

Maintainers
-----------

This module is maintained by the OCA.

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

This module is part of the `OCA/l10n-italy <https://github.com/OCA/l10n-italy/tree/16.0/l10n_it_intrastat_statement>`_ project on GitHub.

You are welcome to contribute. To learn how please visit https://odoo-community.org/page/Contribute.
