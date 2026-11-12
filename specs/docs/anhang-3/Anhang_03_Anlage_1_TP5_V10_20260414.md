# Anhang_03_Anlage_1_TP5_V10_20260414.pdf

<!-- source-pdf: Anhang_03_Anlage_1_TP5_V10_20260414.pdf -->

## Page 1

Anhang 3 

zur 

Anlage 1 

Kapitel 10 "Kostenträgerdatei" 

zu den 

Richtlinien der Spitzenverbände der Krankenkassen nach § 302 Abs. 2 SGB V über 

Form und Inhalt des Abrechnungsverfahrens mit "Sonstigen Leistungserbringern" 

sowie mit Hebammen und Entbindungspflegern (§ 301a SGB V) 

Stand des Anhang 3: 

14.04.2026 

Version: 

Anzuwenden ab: 

10 

01.02.2027

## Page 2

Anhang 3 zur Technische Anlage 1 

zu den Richtlinien über Form und Inhalt des Abrechnungsverfah-

rens nach § 302 SGB V 

Stand: 14.04.2026 

Seite 2 von 34 

Änderungshistorie 

Version 

Status 

Datum 

Redaktion  Abschnitt 

Erläuterung 

10 

09 

Abgestimmt 

14.04.2026 

GKV-SV 

8.14 

Einfügen neuer Schlüsselwerte für Haus-

haltshilfe 

Abgestimmt 

14.04.2026 

GKV-SV 

gesamtes Do-

Inkrafttreten Version 09 auf 01.06.2026 

09 

Abgestimmt 

18.02.2026 

GKV-SV 

5.2, 7.2 (DFU, 

Erweiterungen für vollelektronisches Ab-

kument 

vorgezogen und "Einfügen neuer Schlüssel-

werte für Haushaltshilfe" in Abschnitt 8.14 

auf Version 10 verschoben 

VKG), 8.2, 8.3, 

rechnungsverfahren 

8.5, 8.11, 8.16 

Abgestimmt 

18.02.2026 

GKV-SV 

6 

„SB“ als zusätzliche Endung für Kostenträ-

gerdateien eingefügt 

Abgestimmt 

23.05.2023 

GKV-SV 

7.2 

Segment VKG, Feld "Abrechnungscode": 

Typ als "AN" definiert 

Abgestimmt 

23.05.2023 

GKV-SV 

8.14 

Abrechnungscodes "A0" bis "A8" und "B1" 

Abgestimmt 

16.06.2020 

GKV-SV 

Abgestimmt 

08.04.2020 

GKV-SV 

Abgestimmt 

01.11.2019 

GKV-SV 

Abgestimmt 

05.04.2019 

GKV-SV 

Abgestimmt 

20.09.2017 

GKV-SV 

Abgestimmt 

01.09.2017 

GKV-SV 

Abgestimmt 

01.09.2017 

GKV-SV 

8.14 

8.14 

8.14 

8.14 

8.5 

7.2 

8.5 

ergänzt 

Gruppenschlüssel "90" eingefügt 

Abrechnungscodes "91", "92", "93" und 

"94" ergänzt 

Abrechnungscode "76" ergänzt 

Text bei Schlüssel "99" präzisiert 

Nicht-IP-Basierte Schlüsselwerte entfernt; 

Schlüsselwert "023" ergänzt. 

Segment VKG: Fußnote 4 präzisiert 

Schlüsselwert "016" ergänzt 

Abgestimmt 

01.09.2017 

GKV-SV 

8.14 

Abrechnungscodes "63", "69", "73" und 

"74" ergänzt 

Abgestimmt 

01.09.2017 

GKV-SV 

8.15 

Schlüssel Tarifkennzeichen 3.-5. Stelle 

analog TA 3 aktualisiert 

Abgestimmt 

12.09.2012 

GKV-SV 

gesamtes Do-

Layout vereinheitlicht, mehrere kleine re-

kument 

daktionelle Anpassungen durchgeführt 

Abgestimmt 

12.09.2012 

GKV-SV 

7.2 

Segment KTO: Anpassungen für SEPA vor-

genommen 

Abgestimmt 

12.09.2012 

GKV-SV 

7.2 

Segment VKG: Feld "Tarifkennzeichen" er-

Abgestimmt 

12.09.2012 

GKV-SV 

Abgestimmt 

12.09.2012 

GKV-SV 

8.14 

8.15 

Abrechnungscode für SAPV ergänzt 

Schlüssel Tarifkennzeichen eingefügt 

gänzt 

09 

08 

08 

07 

07 

06 

05 

04 

03 

03 

03 

03 

02 

02 

02 

02 

02 

Anhang 3 zur Anlage 1 

anzuwenden ab 01.02.2027 

GKV-Spitzenverband

## Page 3

Anhang 3 zur Technische Anlage 1 

zu den Richtlinien über Form und Inhalt des Abrechnungsverfah-

rens nach § 302 SGB V 

Stand: 14.04.2026 

Seite 3 von 34 

Inhaltsverzeichnis "Kostenträger" 

1.  VERWENDUNGSZWECK ................................................................................................. 4 

2.  VERÖFFENTLICHUNG ................................................................................................... 4 

3.  ALLGEMEINE SYSTEMATIK DER KOSTENTRÄGERDATEI ................................................... 5 

4.  LOGISCHES DATENMODELL .......................................................................................... 7 

5.  VERKNÜPFUNGSREGELN ............................................................................................... 8 
VERKNÜPFUNG ZUM KOSTENTRÄGER .................................................................................. 8 
5.1 
VERKNÜPFUNG ZU DATENANNAHMESTELLEN ........................................................................ 8 
5.2 
5.2.1  Verknüpfung zur Datenannahmestelle mit und ohne Berechtigung zur 

Entschlüsselung ....................................................................................................... 8 
5.2.2  Zuordnung zum regional zuständigen Kommunikationspartner ............................... 9 
VERKNÜPFUNG ZU PAPIERANNAHMESTELLEN......................................................................... 9 
5.3 

6.  DATEINAME ...............................................................................................................10 

7.  DATEISTRUKTUR ........................................................................................................12 
SERVICESEGMENTE ....................................................................................................... 13 
7.1 
NUTZSEGMENTE .......................................................................................................... 15 
7.2 

8.  SCHLÜSSELVERZEICHNIS .............................................................................................21 
ART DER ANSCHRIFT .................................................................................................... 21 
8.1 
ART DER DATENLIEFERUNG ............................................................................................ 21 
8.2 
ART DER VERKNÜPFUNG ZWISCHEN INSTITUTIONSKENNZEICHEN .............................................. 21 
8.3 
BUNDESLAND ............................................................................................................. 23 
8.4 
DFÜ-PROTOKOLL ....................................................................................................... 23 
8.5 
KOMPRIMIERUNGSART .................................................................................................. 23 
8.6 
KV-BEZIRK ............................................................................................................... 25 
8.7 
LEISTUNGSERBRINGERGRUPPE ......................................................................................... 27 
8.8 
ÜBERMITTLUNGSMEDIUM ............................................................................................... 27 
8.9 
ÜBERMITTLUNGSMEDIUM-PARAMETER .............................................................................. 27 
8.10 
ÜBERMITTLUNGSZEICHENSATZ ........................................................................................ 28 
8.11 
ÜBERTRAGUNGSTAGE ................................................................................................... 28 
8.12 
VERARBEITUNGSKENNZEICHEN ........................................................................................ 29 
8.13 
SCHLÜSSEL ABRECHNUNGSCODE ..................................................................................... 29 
8.14 
SCHLÜSSEL TARIFKENNZEICHEN ...................................................................................... 32 
8.15 

Anhang 3 zur Anlage 1 

anzuwenden ab 01.02.2027 

GKV-Spitzenverband

## Page 4

Anhang 3 zur Technische Anlage 1 

zu den Richtlinien über Form und Inhalt des Abrechnungsverfah-

rens nach § 302 SGB V 

Stand: 14.04.2026 

Seite 4 von 34 

1.  Verwendungszweck 

Beim  maschinellen  Datenaustausch  zwischen  Krankenkassen  und  Leistungserbrin-

gern  werden  die  Kommunikationspartner  auf  beiden  Seiten  durch  ihr  Institutions-

kennzeichen (IK) identifiziert. In § 293 SGB V sowie in den ergänzenden Rahmenver-

einbarungen ist festgelegt, dass dieses im Schriftverkehr und für Abrechnungszwecke 

zu verwenden ist. 

Da der Leistungserbringer im Hinblick auf seine Abrechnung als primäre Information 

über den Versicherten nur dessen Krankenversichertenkarte zur Verfügung hat, stel-

len die Krankenkassen den Leistungserbringern ein Verzeichnis zur Verfügung, das - 

ausgehend vom IK der Krankenversichertenkarte - folgende Funktionen erfüllt: 
 
 

Anschrift(en) und Routing-Informationen für die datenannehmenden Stelle(n), 

Zuordnung des Kostenträgers, 

wobei  hier  ggf.  nach Leistungserbringergruppe  und  Medium  der  Datenüber-

mittlung differenziert werden kann, 

 

Bereitstellung  von Schlüsseln  für  die kryptografische  Verschlüsselung  (Public 

Key und Zertifikat des Public Key, wenn die Institution eine zur Entschlüsselung 

berechtigte Stelle ist). 

2.  Veröffentlichung 

Die  Kostenträgerdateien  werden  von  den  Spitzenverbänden  der  Krankenkassen  er-

stellt und können über www.gkv-datenaustausch.de abgerufen werden. 

Die Aktualisierung der Kostenträgerdatei erfolgt jeweils zum 1. eines jeden Kalender-

vierteljahres. Die aktualisierte Fassung wird spätestens 4 Wochen vor Beginn des je-

weiligen Kalendervierteljahres bereitgestellt. 

Anhang 3 zur Anlage 1 

anzuwenden ab 01.02.2027 

GKV-Spitzenverband

## Page 5

Anhang 3 zur Technische Anlage 1 

zu den Richtlinien über Form und Inhalt des Abrechnungsverfah-

rens nach § 302 SGB V 

Stand: 14.04.2026 

Seite 5 von 34 

3.  Allgemeine Systematik der Kostenträgerdatei 

Die  Kostenträgerdatei  ist  wie  jede  andere  Datei  im  Projekt  Datenaustausch  in 

EDIFACT-Struktur aufgebaut, wobei Servicesegmente entsprechend dem internatio-

nalen Standard, Nutzsegmente dagegen in EDIFACT-Syntax vom Projekt selbst defi-

niert und damit Teil des projektspezifischen Branchensubsets sind. Die folgende Dar-

stellung der allgemeinen Systematik berücksichtigt nur die Nutzsegmente. 

Jede Nachricht wird durch ein Identifikationssegment als Schlüsselsegment erschlos-

sen und bildet Funktionen bzw. Eigenschaften von Einrichtungen ab, die für den Da-

tenaustausch  relevant  sind.  Die  Funktionen  werden  in  weiteren  Segmenten  darge-

stellt, von denen jedes mit jeder neuen Ausprägung seiner Merkmale wiederholt wird. 

Jede  Nachricht  kann  über  ein oder  mehrere Verknüpfungssegment(e)  auf  eine  oder 

mehrere andere Nachrichten verweisen. 

Folgende Segmente finden in der Kostenträgerdatei Verwendung: 

⇒ 

⇒ 

⇒ 

⇒ 

⇒ 

IDK 

Identifikationssegment, tritt als Schlüsselsegement je Nachricht einmal 

und obligatorisch auf; 

VDT 

Verwaltungsdatensegment,  obligatorisch  dem  IDK  zugeordnet,  kann 

optional auch jedem anderen Segment zugeordnet werden, dessen Gültigkeits-

zeitraum vom IDK abweicht; 

FKT 

Funktionssegment,  einmal  und  obligatorisch,  zur  Kennzeichnung  der 

Funktion einer Nachricht 

KTO 

Kontosegment,  optional,  entsprechend  einer  Bankverbindung  aus  der 

bei der Sammel- und Verteilungsstelle Institutionskennzeichen (SVI) gespeicher-

ten Datei. Zu jedem IK ist bei der SVI nur eine Kontoverbindung möglich; 

VKG 

Verknüpfungssegment, optional und wiederholbar; die Verknüpfung er-

folgt vom IK der Versichertenkarte zum IK des Kostenträgers und von dort zu 

seinen Daten annehmenden Stellen; 

⇒  NAM  Namenssegment, einmal und obligatorisch; 
⇒  ANS 

Anschriftensegment,  einmal  obligatorisch  und  (optional)  bis  zu  2  mal 

wiederholbar; es kann eine Haus-, Postfach- und eine Großkundenanschrift ge-

speichert werden (daher maximal 3 ANS-Segmente je Nachricht). 

⇒  ASP 

Ansprechpartner, optional und wiederholbar; 

Anhang 3 zur Anlage 1 

anzuwenden ab 01.02.2027 

GKV-Spitzenverband

## Page 6

Anhang 3 zur Technische Anlage 1 

zu den Richtlinien über Form und Inhalt des Abrechnungsverfah-

rens nach § 302 SGB V 

Stand: 14.04.2026 

Seite 6 von 34 

⇒  UEM 

Übermittlungssegment, optional und wiederholbar, zur Darstellung der 

Medien, die über die durch das IK bezeichnete Einrichtung übermittelt werden 

können; 

⇒  DFU 

Datenfernübertragungssegment. Wenn in einem Übermittlungssegment 

die Datenfernübertragung als Medium genannt wurde, ist das DFU-Segment ein-

mal obligatorisch und (optional) wiederholbar. Es dient zur Darstellung der DFÜ-

Arten,  die  über  die  durch  das  IK  bezeichnete  Einrichtung  abgewickelt  werden 

können. 

Die Basis der Kostenträgerdatei bildet die Summe der IK, die auf den Versicherten-

karten  Verwendung  finden.  Für  diese  IK  werden  Nachrichten  bereitgestellt,  die  von 

den Anwendungsprogrammen der Leistungserbringer (LE) bei der Vorbereitung einer 

Datensendung genutzt werden können, um folgende Informationen zu erschließen: 
 
 

den Empfänger von Daten, ggf. unterschiedlich für verschiedene Medien; dabei 

den Kostenträger, 

sind zwei Fälle zu unterscheiden: 
 

Empfänger, die nur befugt sind, kryptografisch verschlüsselte Daten zu 

verteilen bzw. weiterzuleiten, 

Empfänger, die zur Entschlüsselung der Daten befugt sind; 

 
die Bankverbindung des Kostenträgers, die für einen Zahlungsfluss vom LE zum 

 

Kostenträger zu nutzen ist (optional). 

Bei einer Datenübermittlung von der Krankenkasse zum LE sollen die Anwendungs-

programme des LE zur Überprüfung der übermittelten Daten auf die Kostenträgerda-
tei zugreifen können, um auf allen Ebenen1, in denen IK in Service- und Nutzsegmen-
ten geliefert werden, die Zulässigkeit der übermittelten IK zu prüfen. 

1  Für den Fallbezug muss das IK der Versichertenkarte an den LE übermittelt werden, weitere Ebenen 
betreffen den Kostenträger, sofern vom IK der Versichertenkarte abweichend, sowie den Datenemp-

fänger mit und ohne Befugnis zur Entschlüsselung. 

Anhang 3 zur Anlage 1 

anzuwenden ab 01.02.2027 

GKV-Spitzenverband

## Page 7

Anhang 3 zur Technische Anlage 1 

zu den Richtlinien über Form und Inhalt des Abrechnungsverfah-

rens nach § 302 SGB V 

Stand: 14.04.2026 

Seite 7 von 34 

4.  Logisches Datenmodell 

Die Art der Beziehungen zwischen den Objekten (Segmenten) ist vom IDK aus zu se-

hen. 

IDK 

1:CN 

VKG 

1:1 

FKT 

1:C 

1:1 

1:CN 

1:CN 

KTO 

NAM 

ASP 

UEM 

1:N 

1:CN 

ANS 

DFU 

VDT-Segmente sind im logischen Datenmodell nicht aufgeführt. 

Je nach Art der Institution ergeben sich typische Strukturen, für die im folgenden Bei-

spiele dargestellt werden. (Optionale Segmente sind schattiert dargestellt.) 

IK der Versichertenkarte, nicht identisch mit dem Haupt-IK des Kostenträgers 

IDK 

FKT 

KTO 

VKG 

NAM 

ANS 

Kostenträger, der nicht selbst Daten annimmt 

IDK 

FKT 

KTO 

VKG 

NAM 

ANS 

ASP 

Datenannahmestelle ohne Entschlüsselungsbefugnis 

IDK 

FKT 

VKG 

NAM 

ANS 

ASP 

UEM 

DFU 

Datenannahmestelle mit Entschlüsselungsbefugnis (Kassen-DAV) 

IDK 

FKT 

NAM 

ANS 

ASP 

UEM 

DFU 

Anhang 3 zur Anlage 1 

anzuwenden ab 01.02.2027 

GKV-Spitzenverband

## Page 8

Anhang 3 zur Technische Anlage 1 

zu den Richtlinien über Form und Inhalt des Abrechnungsverfah-

rens nach § 302 SGB V 

Stand: 14.04.2026 

Seite 8 von 34 

5.  Verknüpfungsregeln 

Die Erschließung von Informationen, die einem anderen IK als dem der Versicherten-

karte  zugeordnet  sind,  erfolgt  über  das  Verknüpfungssegment  VKG,  das  den  Ver-

knüpfungszweck bzw. die Art der Verknüpfung in Form eines Qualifiers und das Ver-

knüpfungsziel in Form eines IK darstellt. 

5.1  Verknüpfung zum Kostenträger 

Bilden mehrere IK der Versichertenkarte auf einen Kostenträger ab, so wird das IDK 

der  Versichertenkarte  zum  IDK  des  Kostenträgers  verknüpft.  Dies  gilt  z.B.  für  den 

Ersatzkassenbereich,  in  dem  für  jeden  Kostenträger  23  IK’s  bereitgestellt  werden, 

aber auch für fusionierte Kostenträger anderer Kassenarten. Dem IDK der Versicher-

tenkarte wird dann nur ein VKG zugeordnet mit der Verknüpfungsart 01 = Verweis 

vom IK der Versichertenkarte zum Kostenträger. 

5.2  Verknüpfung zu Datenannahmestellen 

Darüber hinaus erfolgt ein Verweis vom Kostenträger mit Verknüpfungsart 02 oder 

03 auf eine Datenannahmestelle. Dieser Verweis ist nur gültig in Verbindung mit dem 

Schlüssel 07 oder dem Schlüssel 30 bei "Art der Datenlieferung". 

5.2.1  Verknüpfung zur Datenannahmestelle mit und ohne Berechtigung zur Ent-

schlüsselung 

Die Entschlüsselung der Daten wird nur in kasseneigenen Datenannahme- und -ver-

teilstellen vorgenommen. Die Daten sind daher mit dem Public Key der kasseneigenen 

DAV zu verschlüsseln. Wird ein Netzbetreiber eingeschaltet, so hat dieser nicht das 

Privileg, die Daten zu entschlüsseln. 

In jedem Fall muss also definiert werden, ob der Datenempfänger zur Entschlüsselung 

berechtigt ist oder nicht. Ist er hierzu berechtigt, ist die Nachricht mit seinem Public 

Key zu verschlüsseln. Trifft dies jedoch, wie beim Netzbetreiber, nicht zu, muss zu-

sätzlich der nachfolgende Empfänger bekannt sein, der zur Entschlüsselung berech-

tigt ist und dessen Public Key zur Verschlüsselung zu verwenden ist. 

Anhang 3 zur Anlage 1 

anzuwenden ab 01.02.2027 

GKV-Spitzenverband

## Page 9

Anhang 3 zur Technische Anlage 1 

zu den Richtlinien über Form und Inhalt des Abrechnungsverfah-

rens nach § 302 SGB V 

Stand: 14.04.2026 

Seite 9 von 34 

Die  Unterscheidung  erfolgt  über  den  Schlüssel  "Art  der  Verknüpfung".  Erfolgt  eine 

Verknüpfung auf eine Datenannahmestelle mit Entschlüsselungsbefugnis, muss in der 

Nachricht dieser Institution geprüft werden, ob eine Verknüpfung zu einer Datenan-

nahmestelle ohne Entschlüsselungsbefugnis vorhanden ist. 

5.2.2  Zuordnung zum regional zuständigen Kommunikationspartner 

Es ist vorgesehen, dass jeder Leistungserbringer je Kassensystem nur einen Kommu-

nikationspartner haben soll: Wer mit dem AOK-System Daten austauscht, kommuni-

ziert  mit  allen  zugelassenen  Medien  mit  der  für  ihn  regional  zuständigen  DAV  des 

AOK-Systems. Das gleiche Prinzip gilt auch, wenn Netzbetreiber eingesetzt werden; 

in  diesem  Fall  wird  bei  Datenfernübertragung  mit  einem  zentralen  oder  regionalen 

Knotenpunkt kommuniziert. 

Dies verlangt, dass der Zugang des LE zu den Kommunikationsdaten der Kostenträger 

neben dem IK über einen zweiten Schlüssel organisiert wird, nämlich einem Regio-

nalschlüssel, dem der LE seinen eigenen Standort zuordnet. Dafür kann das zweistel-
lige Länderkennzeichen2 stehen, eine weitere Differenzierung ist möglich. 

Die regionale Zuordnung ist in den Anwendungsprogrammen so einzurichten, dass 

der Anwender, also in der Regel der Leistungserbringer, aus dem Gesamtpotential der 

Kommunikationspartner,  das  für  eine  Kassenart  besteht,  den  Partner  auswählt,  der 

ihm räumlich am nächsten liegt oder sonst wie die günstigsten Kommunikationsbe-

ziehungen bietet. Die Auswahl kann in der Regel durch das Regionalkennzeichen im 

Verknüpfungssegment erfolgen, das den Standort des Kommunikationspartners für 

die Kassenart bezeichnet. 

5.3  Verknüpfung zu Papierannahmestellen 

Des weiteren sind Verknüpfungen auf Papierannahmestellen, Verknüpfungsart 09 an-

zugeben: entweder mindestens zwei Verknüpfungen mit den Gruppenschlüsseln 28 

und  29  bei  "Art  der  Datenlieferung"  oder  mehrere  Verknüpfungen  mit  den  Einzel-

schlüsseln 21, 24, 26, 27. 

2  Schlüssel der Regionalsystematik des Statistischen Bundesamtes, der zweistellig die Länder, dreistel-

lig die Regierungsbezirke kennzeichnet. 

Anhang 3 zur Anlage 1 

anzuwenden ab 01.02.2027 

GKV-Spitzenverband

## Page 10

Anhang 3 zur Technische Anlage 1 

zu den Richtlinien über Form und Inhalt des Abrechnungsverfah-

rens nach § 302 SGB V 

Stand: 14.04.2026 

Seite 10 von 34 

Der  Verweis  auf  die  Papierannahmestellen  erfolgt  in  der  Kostenträgerdatei,  ausge-

nommen, die Papierannahmestellen werden auf anderem Wege durch den Kostenträ-

ger dem Leistungserbringer bekannt gegeben. 

6.  Dateiname 

Die Festlegung der Namenskonvention für die Kostenträgerdateien der Kassenarten 

gelten sowohl für den physischen Dateinamen, als auch für den logischen Dateina-

men. 

Im Rahmen der DOS-Konventionen stehen 8+3 alphanumerische Stellen zur Verfü-

gung. Da auch heute  noch DOS-Systeme zum Einsatz kommen, müssen diese Ein-

schränkungen berücksichtigt werden. Durch eine geeignete Kodierung sollen alle we-

sentlichen Angaben aus dem Dateinamen hervorgehen. 

Stellen 

Inhalt 

Bedeutung 

Dateiname   

1 - 2 

AA 

Kassenart 

AO = AOK 

EK = Ersatzkassen 

BK = Betriebskrankenkassen 

IK = Innungskrankenkassen 

BN = Knappschaft-Bahn-See 

LK = Landwirtschaftliche Krankenkassen 

GK = Gesetzliche Krankenversicherung 

SB = Sonstige Kostenträger mit Bitmarck als Dienstleister  

3 - 4 

NA 

Verfahren 

01 = Datenaustausch Teilprojekt Ärzte 

02 = Datenaustausch Teilprojekt Zahnärzte 

03 = Datenaustausch Teilprojekt Apotheken 

4A = Datenaustausch Teilprojekt Krankenhäuser 

4B = Datenaustausch Teilprojekt Reha-Einrichtungen 

05 = Datenaustausch Teilprojekt Sonstige Leistungserbringer 

06 = Datenaustausch Teilprojekt Leistungserbringer Pflege 

5 - 6 

AN 

Gültigkeit ab 

01 bis 12 = gültig ab Monat 

Q1 bis Q4 = gültig ab 1. bis 4. Quartal 

Anhang 3 zur Anlage 1 

anzuwenden ab 01.02.2027 

GKV-Spitzenverband

## Page 11

Anhang 3 zur Technische Anlage 1 

zu den Richtlinien über Form und Inhalt des Abrechnungsverfah-

rens nach § 302 SGB V 

Stand: 14.04.2026 

Seite 11 von 34 

7 - 8 

NN 

Jahreszahl (zweistellig) 

Erweite-

rung 

1 

2 

A 

A 

Einsatzgebiet 

K = Kostenträgerdatei Datenaustausch 

Format 

D = Datenbankformat 

E = EDIFACT-Format 

X = Excel-Format 

3 

N 

Version 

1 bis 9 = Nachtrag 

0 = Standardangabe 

Falls innerhalb eines Quartals die Notwendigkeit besteht, eine 

Versionsanpassung der Datei vorzunehmen, gibt es hier die 

Möglichkeit, fortlaufend zu nummerieren 

Anhang 3 zur Anlage 1 

anzuwenden ab 01.02.2027 

GKV-Spitzenverband

## Page 12

Anhang 3 zur Technische Anlage 1 

zu den Richtlinien über Form und Inhalt des Abrechnungsverfah-

rens nach § 302 SGB V 

Stand: 14.04.2026 

Seite 12 von 34 

7.  Dateistruktur 

Die Datei beginnt mit einem "Festlegungssegment (UNA)" (optional) und einem "Kopf-

segment Datei (UNB)" und endet mit einem "Endesegment Datei (UNZ)". 

Jede Nachricht - das sind alle Daten zu einem Institutionskennzeichen - wird mit ei-

nem  "Kopfsegment  Nachrichtentyp (UNH)"  eingeleitet  und mit  einem  "Endesegment 

Nachrichtentyp (UNT)" beendet. 

Bei der Datenübermittlung auf Datenträgern wird jedes Segment als Einzelsatz dar-

gestellt (bei Disketten: Satzende = Carriage Return / Line Feed). 

Bei der Darstellung der Dateistruktur wird folgende Symbolik benutzt : 

Symbol 

Bedeutung 

+ 

(...) 

{...} 

gefolgt von, plus 

optional 

Wiederholung 

Darstellung der Segmentfolge in der Datei 

(UNA +) 

   UNB 

  Festlegungssegment 

  Kopfsegment Datei 

{+ UNH 

  Kopfsegment Nachrichtentyp KOTR (Kostenträger) 

  + IDK 

  + FKT 

 + VDT 

 (+ KTO 

(+ VDT)) 

({+ VKG 

(+ VDT)}) 

  + NAM 

(+ VDT) 

 {+ ANS 

(+ VDT)} 

(bis zu 2x wiederholbar) 

({+ ASP 

(+ VDT)}) 

({+ UEM 

(+ VDT) 

({+ DFU 

(+VDT)})}) 

 + UNT} 

  Endesegment Nachrichtentyp KOTR 

+ UNZ 

  Endesegment Datei 

Anhang 3 zur Anlage 1 

anzuwenden ab 01.02.2027 

GKV-Spitzenverband

## Page 13

Anhang 3 zur Technische Anlage 1 

zu den Richtlinien über Form und Inhalt des Abrechnungsverfah-

rens nach § 302 SGB V 

Stand: 14.04.2026 

Seite 13 von 34 

7.1  Servicesegmente 

Festlegungssegment 

Seg-

ment 

Feldbezeichnung 

Feld

Feld

Anz. 

Bemerkungen 

UNA  Festlegungssegment 

TZ innerh. Datenelemente 

-Art 

-

Stell

Typ 

C 

C 

. 

3 

1 

M 

M 

'UNA' 

':'  (Trennkennzeichen innerhalb zu-

sammengesetzter Datenelemente) 

TZ Datenelemente 

M 

C 

1 

'+' (Trennkennzeichen Datenele-

Dezimalzeichen 

Aufhebungszeichen 

Reserviert 

Segmentendezeichen 

M 

M 

M 

M 

C 

C 

C 

C 

1 

1 

1 

1 

mente) 

','  

'?’ (für Steuerzeichen) 

leer 

''' 

Kopfsegment Datei 

Seg-

ment 

Feldbezeichnung 

Feld

Feld

Anz. 

Bemerkungen 

-Art 

-

Stell

UNB  Kennung 

Syntax 

Syntax-Kennung 

Syntax-Version 

Absender der Datei 

Empfänger der Datei 

Datum-Uhrzeit 

Datum 

Uhrzeit 

Dateinummer 

Freifeld 

Dateiname 

Typ 

M 

C 

M 

M 

M 

M 

M 

M 

M 

K 

M 

C 

C 

C 

C 

N 

N 

C 

C 

C 

. 

3 

4 

1 

9 

9 

6 

4 

5 

1 

'UNB' 
'UNOC:3' 

IK des Absenders 

IK des Empfängers, wenn bekannt, 
'999999999' bei Datei für eine Mail-
box 

JJMMTT:HHMM 

fortlaufende Nummer 

leer 

11  Siehe hierzu Kapitel 6 

Anhang 3 zur Anlage 1 

anzuwenden ab 01.02.2027 

GKV-Spitzenverband

## Page 14

Anhang 3 zur Technische Anlage 1 

zu den Richtlinien über Form und Inhalt des Abrechnungsverfah-

rens nach § 302 SGB V 

Stand: 14.04.2026 

Seite 14 von 34 

Kopfsegment Nachrichtentyp 

Feldbezeichnung 

Feld

Feld

Anz. 

Bemerkungen 

- 

-

Stell

Art 

Typ 

M 

M 

M 

M 

M 

M 

C 

C 

C 

C 

C 

C 

. 

3 

5 

4 

2 

3 

2 

'UNH' 

laufende Nummer (innerhalb UNB / 

UNZ) 
Beispiel: 'KOTR:02:001:KV' 
'KOTR' 
'02' 
'001' 
'KV' 

UNH  Kennung 

Nachrichtenreferenz 

Nachrichtenkennung 

Typ 

Version 

Freigabenummer 

Verwaltende Organisation 

Endesegment Nachrichtentyp 

Seg-

ment 

Seg-

ment 

Feldbezeichnung 

Feld

Feld

Anz. 

Bemerkungen 

UNT  Kennung 

Anzahl Segmente im Nach-

richtentyp 

- 

-

Stell

Art 

Typ 

M 

M 

C 

N 

. 

3 

6 

'UNT' 

Summe der Segmente von UNH bis 

UNT (einschl. UNH und UNT) 

Nachrichtenreferenz 

M 

C 

5  wie in UNH 

Endesegment Datei 

Seg-

ment 

Feldbezeichnung 

Feld

Feld

Anz. 

Bemerkungen 

- 

-

Stell

UNZ  Kennung 

Anzahl Nachrichtentypen 

Datei 

Art 

Typ 

M 

M 

C 

N 

. 

3 

'UNZ' 

6  Anzahl der UNH’s in der Datei 

Dateinummer 

M 

C 

5  wie in UNB 

Anhang 3 zur Anlage 1 

anzuwenden ab 01.02.2027 

GKV-Spitzenverband

## Page 15

Anhang 3 zur Technische Anlage 1 

zu den Richtlinien über Form und Inhalt des Abrechnungsverfah-

rens nach § 302 SGB V 

Stand: 14.04.2026 

Seite 15 von 34 

7.2  Nutzsegmente 

Alle Segment-Kennungen werden als Muss-Felder deklariert, da bei Auftreten des je-

weiligen Segmentes die Benennung des Segmentes obligatorisch ist. Ob ein Segment 

insgesamt optional oder obligatorisch ist, kann der Aufstellung in Kapitel 2 entnom-

men werden. Der besseren Übersicht wegen wurde diese Information zusätzlich jeder 

der nachfolgenden Segment-Beschreibungen vorangestellt. 

IDK-Segment: einmal obligatorisch 

Seg-

Inhalt 

ment 

Art  Typ  Länge  Faktor  Inhalt/Erläuterung 

IDK  Segment Identifikation 

Institutionskennzeichen 

Art der Institution 

M  C 

M  N 

M  N 

3 

9 

2 

IDK 

Schlüssel Art der In-

stitution = 99 
(Dummy) 3 

Kurzbezeichnung 

M  C 

...30 

VKNR 

K  N 

5 

Angabe ist nicht er-

forderlich, auch, 

wenn es sich bei der 

Institution um eine 

Krankenkasse handelt  

VDT-Segment: einmal obligatorisch zum IDK, optional bei anderen Segmenten 

VDT  Segment Verwaltungsdaten 

Gültigkeitsdatum ab 

Gültigkeitsdatum bis 

FKT-Segment: einmal obligatorisch 

FKT  Segment Funktion 

Verarbeitungskennzeichen 

M  C 

M  N 

K  N 

M  C 

M  C 

3 

8 

8 

3 

2 

VDT 

JJJJMMTT 

JJJJMMTT 

‘FKT’ 

Schlüssel Verarbei-

tungskennzeichen 

3 gilt nur für TP5, da alle Informationen zum IK aus dem VKG-Segment abzuleiten sind. 

Anhang 3 zur Anlage 1 

anzuwenden ab 01.02.2027 

GKV-Spitzenverband

## Page 16

Anhang 3 zur Technische Anlage 1 

zu den Richtlinien über Form und Inhalt des Abrechnungsverfah-

rens nach § 302 SGB V 

Stand: 14.04.2026 

Seite 16 von 34 

KTO-Segment: einmal optional 

Seg-

Inhalt 

ment 

KTO  Segment Kontoverbindung 

Kontonummer 

Bankleitzahl 

Bezeichnung der Bank 

Kontoinhaber 

Art  Typ  Länge  Faktor  Inhalt/Erläuterung 

M  C 

K  N 

K  N 

3 

10 

8 

M  C 

...30 

KTO 

siehe Anmerkung 

siehe Anmerkung 

K 

C 

...30 

wenn anders als in 

IDK 

IBAN - International Bank Account 

K 

C 

...34 

siehe Anmerkung 

Number 

BIC - Business Identifier Code 

K 

C 

...11 

siehe Anmerkung 

Anmerkung: 

Bei Verwendung des KTO-Segments muss mindestens eine Bankverbindung angegeben wer-

den: Entweder eine nationale Bankverbindung, bestehend aus Kontonummer und Bankleitzahl, 

oder eine internationale Bankverbindung nach dem SEPA-Standard, bestehend aus IBAN und 

BIC. 

Anhang 3 zur Anlage 1 

anzuwenden ab 01.02.2027 

GKV-Spitzenverband

## Page 17

Anhang 3 zur Technische Anlage 1 

zu den Richtlinien über Form und Inhalt des Abrechnungsverfah-

rens nach § 302 SGB V 

Stand: 14.04.2026 

Seite 17 von 34 

VKG -Segment: optional, wiederholbar (siehe hierzu auch die Verknüpfungsregeln) 

VKG  Segment Verknüpfung 

Art der Verknüpfung 

IK des Verknüpfungspartners 

Leistungserbringergruppe 

IK der Abrechnungsstelle 

M  C 

M  N 

M  N 

K  N 

K  N 

Art der Datenlieferung 

K  N 

Art des Übermittlungsmediums 

K  N 

Standort des Leistungserbringers 

K  N 

nach Bundesland 

Standort des Leistungserbringers 

K  N 

3 

2 

9 

1 

9 

2 

1 

2 

2 

wdh.  VKG 

Schlüssel Art der Ver-

knüpfung 

Institutionskennzeichen 

Schlüssel LE-Gruppe 

IK der Abrechnungsstelle, 

für welche dieser Verweis 

gültig ist. Fehlt dieser 

Eintrag, ist der Verweis 

für alle Stellen gültig. 

Schlüssel Art der Daten-

lieferung 

Schlüssel Übermittlungs-

medium 

Schlüssel Bundesland 

Schlüssel KV-Bezirk 

nach KV-Bezirk 
Abrechnungscode4  
(Leistungserbringerart) 

K  AN 

2 

Schlüssel Abrechnungs-

code 

Tarifkennzeichen 

K  N 

5 

Schlüssel Tarifkennzei-

chen 

4 Der Abrechnungscode ist zwingend für das Teilprojekt 5 anzugeben. Der Sammelschlüssel schließt 
die Verwendung von Gruppen- und Einzelschlüsseln sowie den Sonderschlüssel 99 aus. Wird ein 

Gruppenschlüssel aufgeführt, können zu einem IK nicht die zugehörigen Einzelschlüssel zusätzlich 

angegeben werden (z.B. bei Gruppenschlüssel 20 nicht der Einzelschlüssel 22). 

Folgende Konstellationen sind möglich: 

Einzelschlüssel z. B. 47: Krankenkasse wickelt Krankentransportleistungen über mehrere Stellen ab, 

sie kann differenzieren und die "Untergruppe" bzw. den Einzelschlüssel "47 Leistungserbringer von 

Flugrettungs- und Transportleistungen" in das VKG-Segment (Verknüpfungssegment) schreiben 

und z. B. den Einzelschlüssel "44 Johanniter Unfallhilfe" in ein weiteres. 

Gruppenschlüssel z. B. 40: Krankenkasse wickelt alle Krankentransportleistungen über eine Stelle 

ab, in der Kostenträgerdatei wird der Gruppenschlüssel "40" gesetzt, Schlüssel "47" wäre unter die-

sem subsummiert. 

Sammelschlüssel 00: gilt für alle Leistungen für TP 5; 

Sonderschlüssel 99: gilt für nicht aufgeführte Gruppen- und Einzelschlüssel 

Anhang 3 zur Anlage 1 

anzuwenden ab 01.02.2027 

GKV-Spitzenverband

## Page 18

Anhang 3 zur Technische Anlage 1 

zu den Richtlinien über Form und Inhalt des Abrechnungsverfah-

rens nach § 302 SGB V 

Stand: 14.04.2026 

Seite 18 von 34 

Unterverfahren 

K  AN 

3 

Schlüssel Unterverfahren 

Bedingtes Mussfeld: 

Wenn „Art der Datenliefe-

rung“ = 30 und Leis-

tungsbereich HKP oder 

Haushaltshilfe, dann 

zwingend zu füllen, sonst 

leer. 

Anhang 3 zur Anlage 1 

anzuwenden ab 01.02.2027 

GKV-Spitzenverband

## Page 19

Anhang 3 zur Technische Anlage 1 

zu den Richtlinien über Form und Inhalt des Abrechnungsverfah-

rens nach § 302 SGB V 

Stand: 14.04.2026 

Seite 19 von 34 

NAM-Segment: einmal obligatorisch 

Seg-

Inhalt 

ment 

NAM  Segment Name 

Laufende Nr.  

Name-1 

Name-2 

Name-3 

Name-4 

Art  Typ  Länge  Faktor  Inhalt/Erläuterung 

NAM 

01 bis 03 

M  C 

M  N 

3 

2 

M  C 

...30 

K 

K 

K 

C 

C 

C 

...30 

...30 

...30 

ANS-Segment: einmal obligatorisch, optional wiederholbar 

ANS  Segment Anschrift 

Art der Anschrift 

Postleitzahl 

Ort 

wdh.  ANS 

Schl. Art der An-

schrift 

M  C 

M  N 

3 

1 

M  N 

5 

M  C 

...25 

Straße, Hausnr. / Postfach 

K 

C 

...30 

Straße und Hausnr. 

oder Postfach 

ASP-Segment: optional, wiederholbar 

ASP  Segment Ansprechpartner 

Laufende Nummer 

Telefon 

Fax 

Name 

Arbeitsgebiet des Ansprechpartners 

M  C 

M  N 

3 

2 

wdh.  ASP 

Laufende Numerie-

rung innerhalb einer 

Nachricht 

K 

C 

...15 

Form: Vorwahl/Teil-

nehmernummer 

K 

C 

...15 

Form: Vorwahl/Teil-

K 

K 

C 

C 

...30 

...70 

nehmernummer 

Klartext, z. B. 

Datenaustausch 

Anhang 3 zur Anlage 1 

anzuwenden ab 01.02.2027 

GKV-Spitzenverband

## Page 20

Anhang 3 zur Technische Anlage 1 

zu den Richtlinien über Form und Inhalt des Abrechnungsverfah-

rens nach § 302 SGB V 

Stand: 14.04.2026 

Seite 20 von 34 

UEM-Segment: optional, wiederholbar 

Seg-

Inhalt 

ment 

UEM  Segment Übermittlungsmedium 

Art des Übermittlungsmediums 

Art  Typ  Läng

Fak-

Inhalt/Erläuterung 

M  C 

M  N 

e 

3 

1 

tor 

wdh.  UEM 

Schlüssel Übermitt-

lungsmedium 

Parameter 

M  N 

2 

Schlüssel Übermitt-

Zeichensatz 

M  C 

2 

Schlüssel Übermitt-

lungszeichensatz 

Art der Komprimierung 

K 

C 

2 

Schl. Komprimie-

rungsart 

lungsmedium-Para-

meter 

DFU-Segment: optional, wiederholbar. Obligatorisch, wenn bei UEM DFÜ angegeben wurde 

DFU  Segment DFÜ 

Laufende Nummer 

M  C 

M  N 

3 

2 

wdh.  DFU 

Numerierung inner-

halb UEM 

Übertragungsprotokoll 

M  N 

3 

Schlüssel DFÜ-

Protokoll 

Benutzerkennung 

K 

C 

8 

wenn abweichend 

vom IK 

Übertragung von 

K  N 

4 

Zeitfenster von 

(HHMM) 

Übertragung bis 

K  N 

4 

Zeitfenster bis 

(HHMM) 

Übertragungstage 

K  N 

1 

Schlüssel Übertra-

gungstage 

Kommunikationskanal 

M  C 

...24

DFÜ-Adresse / -Ken-

0 

nung / Telefonnum-

mer / E-Mail-Ad-

resse/ KIM-Mail-

Adresse / Kennzei-

chen „VZD“ bei Ver-

wendung des Ver-

zeichnisdienstes der 

TI 

Anhang 3 zur Anlage 1 

anzuwenden ab 01.02.2027 

GKV-Spitzenverband

## Page 21

Anhang 3 zur Technische Anlage 1 

zu den Richtlinien über Form und Inhalt des Abrechnungsverfah-

rens nach § 302 SGB V 

Stand: 14.04.2026 

Seite 21 von 34 

8.  Schlüsselverzeichnis 

8.1  Art der Anschrift 

1 
2 
3 

Hausanschrift 
Postfachanschrift 
Großkundenanschrift 

8.2  Art der Datenlieferung 

21 
24  
26 
27 

07 

28 

29  

30 

Rechnungs- und Abrechnungsdaten SLGA und SLLA digi-
talisiert 
Rechnung (Papier) 
maschinenlesbarer Beleg  
Verordnung (Papier) 
Kostenvoranschlag (Papier) 
Gruppenschlüssel (Einzelschlüssel 21, 26, 27) 
papiergebundene Unterlagen einer digitalen Abrechnung 
(Verordnung, ggf. Kostenvoranschlag, ggf. Rechnung)  
Gruppenschlüssel (Einzelschlüssel 24, 26, 27) 
maschinenlesbarer Beleg einschließlich der dazugehöri-
gen Abrechnungsunterlagen 
Vollelektronische Abrechnung einschließlich elektroni-
schem Leistungsnachweis 

8.3  Art der Verknüpfung zwischen Institutionskennzeichen 

01 
02 

03 

Verweis vom IK der Versichertenkarte zum Kostenträger 
Verweis auf eine Datenannahmestelle (ohne Entschlüsselungsbe-
fugnis) 
Schlüssel ist nur gültig in Verbindung mit dem Schlüssel 07 oder 
30 "Art der Datenlieferung" 
Verweis auf eine Datenannahmestelle (mit Entschlüsselungsbefug-
nis) 
Schlüssel ist nur gültig in Verbindung mit dem Schlüssel 07 oder 
30 "Art der Datenlieferung" 

Anhang 3 zur Anlage 1 

anzuwenden ab 01.02.2027 

GKV-Spitzenverband

## Page 22

Anhang 3 zur Technische Anlage 1 

zu den Richtlinien über Form und Inhalt des Abrechnungsverfah-

rens nach § 302 SGB V 

Stand: 14.04.2026 

Seite 22 von 34 

09 

Verweis auf eine Papierannahmestelle 

Anhang 3 zur Anlage 1 

anzuwenden ab 01.02.2027 

GKV-Spitzenverband

## Page 23

Anhang 3 zur Technische Anlage 1 

zu den Richtlinien über Form und Inhalt des Abrechnungsverfah-

rens nach § 302 SGB V 

Stand: 14.04.2026 

Seite 23 von 34 

8.4  Bundesland 

01 
02 
03 
04 
05 
06 
07 
08 
09 
10 
11 
12 
13 
14 
15 
16 
99 

Schleswig-Holstein 
Hamburg 
Niedersachsen 
Bremen 
Nordrhein-Westfalen 
Hessen 
Rheinland-Pfalz 
Baden-Württemberg 
Bayern 
Saarland 
Berlin 
Brandenburg 
Mecklenburg-Vorpommern 
Sachsen 
Sachsen-Anhalt 
Thüringen 
Alle Bundesländer (bei Datenlieferungen) 

8.5  DFÜ-Protokoll 

Schlüssel 

016 

(023 

070 

080 

FTAM 

FTP 

TCP/IP 

TCP/IP 

SMTP 

TCP/IP 

Internet 

Internet) 

E-Mail/Internet 

KIM-Mail inner-

halb der TI 

Die  in  Klammern  gefassten  Ausprägungen  entsprechen  nicht  den  in  den  Techni-

schen Anlagen zur § 301-Vereinbarung beschriebenen Standardwerten, so dass ihre 

Verwendung im Datenaustausch nur nach bilateraler Absprache möglich ist. 

8.6  Komprimierungsart 

Schlüssel ist noch zu erstellen 

Anhang 3 zur Anlage 1 

anzuwenden ab 01.02.2027 

GKV-Spitzenverband

## Page 24

Anhang 3 zur Technische Anlage 1 

zu den Richtlinien über Form und Inhalt des Abrechnungsverfah-

rens nach § 302 SGB V 

Stand: 14.04.2026 

Seite 24 von 34 

Anhang 3 zur Anlage 1 

anzuwenden ab 01.02.2027 

GKV-Spitzenverband

## Page 25

Anhang 3 zur Technische Anlage 1 

zu den Richtlinien über Form und Inhalt des Abrechnungsverfah-

rens nach § 302 SGB V 

Stand: 14.04.2026 

Seite 25 von 34 

8.7  KV-Bezirk 

KV-LDST 

KV- 
ABRST 

Klartext 

01 
02 
03 
17 

20 

38 

46 

47 
48 

Schleswig-Holstein 
Hamburg 
Bremen 
Niedersachsen 
Bezirksstelle Aurich 
Bezirksstelle Braunschweig 
Bezirksstelle Göttingen 
Bezirksstelle Hannover 
Bezirksstelle Hildesheim 
Bezirksstelle Lüneburg 
Bezirksstelle Oldenburg 
Bezirksstelle Osnabrück 
Bezirksstelle Stade 
Bezirksstelle Verden 
Bezirksstelle Wilhelmshaven 
Westfalen-Lippe 
Verwaltungsstelle Dortmund  
Verwaltungsstelle M ünster 
Nordrhein 
Bezirksstelle Aachen 
Bezirksstelle Düesseldorf 
Bezirksstelle Duisburg 
Bezirksstelle Köln 
Bezirksstelle Linker Niederrhein 
Bezirksstelle Ruhr 
Bezirksstelle Bergisch-Land 
Hessen 
Bezirksstelle Darmstadt 
Bezirksstelle Frankfurt 
Bezirksstelle Giessen 
Bezirksstelle Kassel 
Bezirksstelle Limburg 
Bezirksstelle Marburg 
Bezirksstelle Wiesbaden 
Koblenz 
Rheinhessen 

06 
07 
08 
09 
10 
11 
12 
13 
14 
15 
16 

18 
19 

21 
24 
25 
27 
28 
31 
37 

39 
40 
41 
42 
43 
44 
45 

Anhang 3 zur Anlage 1 

anzuwenden ab 01.02.2027 

GKV-Spitzenverband

## Page 26

Anhang 3 zur Technische Anlage 1 

zu den Richtlinien über Form und Inhalt des Abrechnungsverfah-

rens nach § 302 SGB V 

Stand: 14.04.2026 

Seite 26 von 34 

49 
50 
55 

60 

61 
62 
71 

72 
73 
78 
83 

88 

93 

98 

Pfalz 
Trier 
Nordbaden 
Abrechnungsstelle Karlsruhe 
Abrechnungsstelle Mannheim 
Abrechnungsstelle Pfortzheim 
Abrechnungsstelle Baden-Baden 
Südbaden 
Abrechnungsstelle Freiburg 
Abrechnungsstelle Konstanz 
Abrechnungsstelle Offenburg 
Nordwürttemberg 
Südwürttemberg 
Bayerns 
Bezirksstelle München Stadt u. Land 
Bezirksstelle Oberbayern 
Bezirksstelle Oberfranken 
Bezirksstelle Mittelfranken 
Bezirksstelle Unterfranken 
Bezirksstelle Oberpfalz 
Bezirksstelle Niederbayern 
Bezirksstelle Schwaben 
Berlin 
Saarland 
Mecklenburg-Vorpommern 
Brandenburg 
Abrechnungsstelle Potsdam 
Abrechnungsstelle Cottbus 
Abrechnungsstelle Frankfurt/oder 
Sachsen-Anhalt 
Abrechnungsstelle Magdeburg 
Abrechnungsstelle Halle 
Abrechnungsstelle Dessau 
Thüringen 
Abrechnungsstelle Erfurt 
Abrechnungsstelle Gera 
Abrechnungsstelle Suhl 
Sachsen 
Bezirksstelle Chemnitz 

52 
53 
54 
56 

57 
58 
59 

63 
64 
65 
66 
67 
68 
69 
70 

79 
80 
81 

85 
86 
87 

89 
90 
91 

94 

Anhang 3 zur Anlage 1 

anzuwenden ab 01.02.2027 

GKV-Spitzenverband

## Page 27

Anhang 3 zur Technische Anlage 1 

zu den Richtlinien über Form und Inhalt des Abrechnungsverfah-

rens nach § 302 SGB V 

Stand: 14.04.2026 

Seite 27 von 34 

95 
96 

Bezirksstelle Dresden 
Bezirksstelle Leipzig 

8.8  Leistungserbringergruppe 

5  

Sonstige Leistungserbringer 

8.9  Übermittlungsmedium 

1 
2 
3 
4 
5 
6 
7 
9 

DFÜ 
Magnetband 
Magnetbandkassette 
Diskette 
Maschinenlesbarer Beleg 
Nicht maschinenlesbarer Beleg 
CD-ROM 
Alle Datenträger (Schlüssel 2 bis 4 und 7) 

8.10  Übermittlungsmedium-Parameter 

00 

(01 
02 
03 
04 
05 
(06 
(07 
08 
09 
10 

kein Parameter (DFÜ-Parameter sind im Segment DFU 
hinterlegt) 
Magnetband 1600 bpi) 
Magnetband 6250 bpi 
Magnetbandkassette 3480 
Magnetbandkassette 3490 - 18 Spur 
Magnetbandkassette 3490 - 36 Spur 
Magnetbandkassette DAT) 
Magnetbandkassette 8 mm) 
Diskette 3,5" - 720 KB - DOS-Format 
Diskette 3,5" - 1,44 MB - DOS-Format 
Diskette 3,5" - 2,88 MB - DOS-Format 

Anhang 3 zur Anlage 1 

anzuwenden ab 01.02.2027 

GKV-Spitzenverband

## Page 28

Anhang 3 zur Technische Anlage 1 

zu den Richtlinien über Form und Inhalt des Abrechnungsverfah-

rens nach § 302 SGB V 

Stand: 14.04.2026 

Seite 28 von 34 

(11 
(12 
(13 
14 

Diskette 5,25" - 360 kB - DOS-Format) 
Diskette 5,25" - 1,2 MB - DOS-Format) 
Diskette 3,5" - 1,44 MB - UNIX-TAR-Format) 
CD-ROM, 12 cm, 650 MB 

Die in Klammern gefassten Ausprägungen entsprechen nicht den in den Tech-

nischen  Anlagen  zur  § 301-Vereinbarung  beschriebenen  Standardwerten,  so 

dass ihre Verwendung im Datenaustausch nur nach bilateraler Absprache mög-

lich ist. 

8.11  Übermittlungszeichensatz 

I7 
I8 
U8 

ASCII 7-Bit 
ASCII 8-Bit 
UTF-8 

8.12  Übertragungstage 

1 

2 

3 

Übertragung an allen Tagen 

Übertragung nur an Werktagen 

(Montag bis Samstag außer Feiertag) 

Übertragung nur an Arbeitstagen 

(Montag bis Freitag außer Feiertag) 

Anhang 3 zur Anlage 1 

anzuwenden ab 01.02.2027 

GKV-Spitzenverband

## Page 29

Anhang 3 zur Technische Anlage 1 

zu den Richtlinien über Form und Inhalt des Abrechnungsverfah-

rens nach § 302 SGB V 

Stand: 14.04.2026 

Seite 29 von 34 

8.13  Verarbeitungskennzeichen 

01 
02 
03 
04 

Neuanmeldung 
Änderung 
Stornierung 
Unverändert 

8.14  Schlüssel Abrechnungscode 

00 

99 

Sammelschlüssel für alle Leistungsarten 

Sonderschlüssel, gilt für alle in der Kostenträgerdatei nicht 

aufgeführten Gruppen- und Einzelschlüssel 

10 

Gruppenschlüssel Hilfsmittellieferant (Schlüssel 11-19) 

11  Apotheke (mit gesonderter Zulassung nach § 126 SGB V) 
12  Augenoptiker  
13  Augenarzt 
14  Hörgeräteakustiker 
15  Orthopädiemechaniker, Bandagist, Sanitätshaus 
16  Orthopädieschuhmacher 
17  Orthopäde 
18 

Sanitätshaus (Bei neuen Verträgen bzw. Vertragsanpassungen  

ist eine Umschlüsselung mit dem Abrechnungscode 15 vorzu-

nehmen. Der Abrechnungscode 18 wird für Sanitätshäuser zum 

31.12.2005 aufgehoben.) 

19 

Sonstiger Hilfsmittellieferant 

20 

Gruppenschlüssel Heilmittelerbringer (Schlüssel 21-29) 

21  Masseur / Medizinischer Badebetrieb 
22  Krankengymnast/Physiotherapeut 
23 

Logopäde/Atem-, Sprech- und Stimmlehrer / stattl. Anerkann-

ter Sprachtherapeut 

24 

25 

Sprachheilpädagoge / Dipl. Pädagoge 

Sonstiger Sprachtherapeut 

Anhang 3 zur Anlage 1 

anzuwenden ab 01.02.2027 

GKV-Spitzenverband

## Page 30

Anhang 3 zur Technische Anlage 1 

zu den Richtlinien über Form und Inhalt des Abrechnungsverfah-

rens nach § 302 SGB V 

Stand: 14.04.2026 

Seite 30 von 34 

26 

Ergotherapeut 

27  Krankenhaus 
28  Kurbetrieb 
29 

Sonstige therapeutische Heilperson 

30 

Gruppenschlüssel Häusliche Krankenpflege (Schlüssel 31-34) 

31 

32 

33 

34 

freigemeinnützige Anbieter (Sozialstatio)n 

privatgewerbliche Anbieter 

öffentliche Anbieter 

sonstige Pflegedienste 

40  

Gruppenschlüssel Krankentransportleistungen (Schlüssel 41-

49) 

41  Öffentlicher Träger (z.B. Feuerwehr) 
42  Deutsches Rotes Kreuz (DRK) 
43  Arbeiter-Samariter-Bund (ASB) 
44 

Johanniter-Unfall-Hilfe (JUH) 

45  Malteser-Hilfsdienst (MHD) 
46 

Sonstiger Leistungserbringer von bodengebundenen Trans-

portleistungen (Taxi / Mietwagen) 

47 

49 

Leistungserbringer von Flugrettungs- und Transportleistungen 

Sonstiger Leistungserbringer von Krankentransportleistungen ( 

z.B. Bergwacht, Wasserwacht, usw.)) 

50  Hebamme / Entbindungspfleger 
55 

Sonstiger Leistungserbringer von nichtärztlichen Dialysesach-

leistungen 

56  Kuratorium für Heimdialyse (KfH) 
57 

Patienten-Heimversorgung (PHV) 

60 

61 

62 

63 

65 

Betriebshilfe 

Leistungserbringer von Rehabilitationssport 

Leistungserbringer von Funktionstraining 

Leistungserbringer für ergänzende Rehabilitationsmaßnahmen 

Sonstige Leistungserbringer 

Anhang 3 zur Anlage 1 

anzuwenden ab 01.02.2027 

GKV-Spitzenverband

## Page 31

Anhang 3 zur Technische Anlage 1 

zu den Richtlinien über Form und Inhalt des Abrechnungsverfah-

rens nach § 302 SGB V 

Stand: 14.04.2026 

Seite 31 von 34 

66 

Leistungserbringer von Präventions- und Gesundheitsförde-

rungsmaßnahmen im Rahmen von ambulanten Vorsorgeleis-

tungen 

67  Ambulantes Rehazentrum 
68 

Sozialpädiatrische Zentren/Frühförderstellen 

69 

71 

73 

Soziotherapeutische Leistungserbringer 

Podologen 

Leistungserbringer von Ernährungstherapie für seltene ange-

borene Stoffwechselerkrankungen 

74 

Leistungserbringer von Ernährungstherapie für Mukoviszidose 

72  Med. Fußpfleger (gemäß § 10 Abs. 4 bis 6 PodG) 
75 

Spezialisierte ambulante Palliativversorgung (SAPV) 

76 

B1 

Leistungserbringer nach § 132g SGB V 

Leistungserbringer von Modellvorhaben nach § 64d SGB V 

A0 

Gruppenschlüssel außerklinische Intensivpflege (AKI) 

ambulante AKI: 

freigemeinnütziger Anbieter 

privatgewerbliche Anbieter 

öffentlicher Anbieter 

sonstiger Anbieter 

stationäre AKI 

freigemeinnütziger Anbieter 

privatgewerbliche Anbieter 

öffentlicher Anbieter 

sonstiger Anbieter 

A1 

A2 

A3 

A4 

A5 

A6 

A7 

A8 

90 

Gruppenschlüssel Kurzzeitpflege (Schlüssel 91-94) 

91  Kurzzeitpflege, privat gewerblicher Anbieter 
92  Kurzzeitpflege, frei gemeinnütziger Anbieter (gemeinnützige 

private Anbieter) 

93  Kurzzeitpflege, öffentlicher Anbieter 
94  Kurzzeitpflege, sonstige Pflegeeinrichtung 

C0 

Gruppenschlüssel Haushaltshilfe 

C1 

C2 

freigemeinnützige Anbieter (Sozialstation) 

privatgewerbliche Anbieter 

Anhang 3 zur Anlage 1 

anzuwenden ab 01.02.2027 

GKV-Spitzenverband

## Page 32

Anhang 3 zur Technische Anlage 1 

zu den Richtlinien über Form und Inhalt des Abrechnungsverfah-

rens nach § 302 SGB V 

Stand: 14.04.2026 

Seite 32 von 34 

C3 

C4 

öffentliche Anbieter 

Sonstige Pflegedienste 

8.15  Schlüssel Tarifkennzeichen 

1. und 2. Stelle 

Tarifbereich 

00 

01 

02 

03 

04 

05 

06 

07 

08 

09 

10 

11 

12 

13 

14 

15 

16 

17 

18 

19 

20 

21 

22 

23 

24 

25 

Bundeseinheitlicher Tarif (gültig für Ost und West) 

Baden-Württemberg 

Bayern 

Berlin Ost 

Bremen 

Hamburg 

Hessen 

Niedersachsen 

Nordrhein-Westfalen 

Rheinland-Pfalz 

Saarland 

Schleswig-Holstein 

Brandenburg 

Sachsen 

Sachsen-Anhalt 

Mecklenburg-Vorpommern 

Thüringen 

Stuttgart und Karlsruhe 

Freiburg und Tübingen 

Berlin West 

Nordrhein 

Westfalen-Lippe 

Lippe 

Berlin (gesamt) 

Bundeseinheitlicher Tarif (West) 

Bundeseinheitlicher Tarif (Ost) 

26 bis 49 

50 

noch zu vergeben 

Bundesvertrag 

Anhang 3 zur Anlage 1 

anzuwenden ab 01.02.2027 

GKV-Spitzenverband

## Page 33

Anhang 3 zur Technische Anlage 1 

zu den Richtlinien über Form und Inhalt des Abrechnungsverfah-

rens nach § 302 SGB V 

Stand: 14.04.2026 

Seite 33 von 34 

51 

52 

53 

54 

55 

56 

57 

58 

59 

60 

61 

62 

63 

64 

65 

66 

67 

68 

69 

70 

71 

72 

73 

74 

75 

76 bis 89 

90 

91-99 

Baden-Württemberg 

Bayern 

Berlin Ost 

Bremen 

Hamburg 

Hessen 

Niedersachsen 

Nordrhein-Westfalen 

Rheinland-Pfalz 

Saarland 

Schleswig-Holstein 

Brandenburg 

Sachsen 

Sachsen-Anhalt 

Mecklenburg-Vorpommern 

Thüringen 

Stuttgart und Karlsruhe 

Freiburg und Tübingen 

Berlin West 

Nordrhein 

Westfalen-Lippe 

Lippe 

Berlin (gesamt) 

Bundeseinheitlicher Tarif (West) 

Bundeseinheitlicher Tarif (Ost) 

noch zu vergeben 

sonstiger länderübergreifender Tarif 

Vertrag auf Kassenebene 

3. bis 5. Stelle 

Sondertarife 

000 - 090 

A00 - A90 

ohne Besonderheiten 

Anhang 3 zur Anlage 1 

anzuwenden ab 01.02.2027 

GKV-Spitzenverband

## Page 34

Anhang 3 zur Technische Anlage 1 

zu den Richtlinien über Form und Inhalt des Abrechnungsverfah-

rens nach § 302 SGB V 

Stand: 14.04.2026 

Seite 34 von 34 

091 - 098 

nicht besetzt  

A91 - A98 

U00 - ZZZ 

(wird von den Verbänden der Krankenkassen auf Bundesebene 

belegt) 

099 

Leistung ohne preisliche Regelung und daher Abrechnung nach 

genehmigten Kostenvoranschlag 

100 - 999 

Sondertarifvereinbarungen zwischen einem oder mehreren Leis-

A99 - TZZ 

tungserbringern und einem oder mehreren Kostenträgern 

(Das Kennzeichen für Sondertarife wird von den Vertragspart-

nern festgelegt.) 

Alle übrigen 

Sondertarifvereinbarungen zwischen einem oder mehreren Leis-

Zahlen-/Buch-

tungserbringern und einem oder mehreren Kostenträgern (Das 

stabenkombi-

Kennzeichen für Sondertarife wird von den Vertragspartnern 

nationen, die 

festgelegt.) 

nicht in die o. g. 

reservierten Be-

reiche Fallen 

8.16  Unterverfahren 

HKP 
HHH 

Häusliche Krankenpflege 
Haushaltshilfe 

Anhang 3 zur Anlage 1 

anzuwenden ab 01.02.2027 

GKV-Spitzenverband
