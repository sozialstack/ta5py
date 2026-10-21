# Glossar — ta5py

Fachvokabular für SGB V TA5/EDIFACT: Nachrichtengestalt, Nutzsegmente,
syntaktische Prüfung und formale bzw. Registerprüfung der genannten Nummern.
Englischer Index: [GLOSSARY.md](../../../../GLOSSARY.md).

**Formal gültig** heißt nur: Struktur und, wo es eine öffentliche Regel gibt,
Prüfziffer stimmen. Es heißt nicht, dass die Nummer vergeben wurde, dass eine
Person versichert ist, dass eine Einrichtung existiert, dass eine Kasse die
Nachricht annimmt, oder dass dieses Projekt ein Testat stellt. Der Begriff
Testat steht bei
[leistungen](../../../leistungen/docs/de/glossar.md#community-testat).

Diese Begleitung enthält **keine** ausführbare Logik. Der englische Quellcode
bleibt ohne dieses Paket vollständig.

**Haftung:** Dieses Projekt ist nicht kassenseitig zertifiziert und stellt kein
Testat dar.

## Betriebsstättennummer (BSNR)

Neunstellige Nummer einer Betriebsstätte. Die Prüfung ist nur die Struktur
(neun Ziffern); eine öffentliche Prüfziffer gibt es hier nicht. Langfassung:
[bsnr.md](bsnr.md).

## EDIFACT

Nachrichtensyntax, in der TA5-Nachrichten aufgebaut sind. `ta5py` kodiert,
dekodiert und prüft sie syntaktisch (Pflichtfelder, Feldlängen, Segmentfolge).
Die Abrechnungsregeln stehen nicht hier.

## Ersatzkennzeichen

Selbstzahler-Ersatzkennzeichen, die analog zu den IK-Vorgaben gebildet sind,
können die Prüfziffer der Standardprüfung erfüllen. Die Standardprüfung
schließt sie nicht aus. Wer sie ablehnen will, braucht eine eigene
Geschäftsregel. Langfassung: [ik.md](ik.md).

## Institutskennung (IK)

Neunstellige Kennung einer Einrichtung. Die formale Prüfung deckt Struktur und
Prüfziffer ab. Ob eine Kostenträger-IK in der geladenen Kostenträgerdatei
steht und welche Empfänger-IK sich für § 302 ergibt, ist die Registerprüfung.
Langfassung: [ik.md](ik.md), Register:
[kostentraeger-ik.md](kostentraeger-ik.md).

## Kassennummer

Siebenstellige Kassennummer auf älteren Karten. Mit Präfix `10` wird daraus
ein neunstelliger IK-Kandidat; die Prüfziffer muss danach weiterhin zur
formalen IK-Regel passen. Langfassung: [ik.md](ik.md).

## Kostenträgerdatei

Lokal geladene Kostenträgerdatei des GKV-Spitzenverbands (SLE, EDIFACT). Sie
beantwortet, ob eine Kostenträger-IK enthalten ist und welche Annahme- oder
Abrechnungs-IK sich daraus ergibt. Ein Treffer ist kein Testat. Ohne geladene
Datei gibt es keinen positiven Existenztreffer. Langfassung:
[kostentraeger-ik.md](kostentraeger-ik.md).

## Krankenversichertennummer (KVNR)

Zehnstellige unveränderbare Versichertennummer (Buchstabe, acht Ziffern,
Prüfziffer). Die formale Prüfung ersetzt nicht die Vergabe, den
Versichertenstatus und nicht das TA5-Feld Versicherten-Nummer. Die 20- und
30-stelligen kasseninternen Nummern gehören nicht dazu. Langfassung:
[kvnr.md](kvnr.md).

## Lebenslange Arztnummer (LANR)

Neunstellige Arztnummer mit Prüfziffer an Stelle 7. Fachgruppe und Zuweisung
werden nicht geprüft. Langfassung: [lanr.md](lanr.md).

## Nutzsegment

Fachsegment einer TA5-Nachricht, zum Beispiel FKT, REC, SRD, INV, ELS.
`ta5py` kennt Aufbau und syntaktische Prüfung, nicht die Bedeutung der
Leistungsart.

## Prüfziffer

Kontrollziffer einer formalen Nummernprüfung. Die Regel ist bei
Institutskennung, LANR und KVNR nicht dieselbe; die Rechenschritte stehen in
den verlinkten Notizen, nicht hier. Eine stimmige Prüfziffer ist nur formale
Gültigkeit.

## SLLA / SLGA

SLLA ist der Nachrichtentyp Abrechnungsdaten, SLGA die Gesamtaufstellung der
Abrechnung. SLLA:E ist die Variante Krankentransportleistungen, die diese
Bibliothek kodiert. Andere SLLA-Varianten sind Nachrichtengestalt, keine
Abrechnungslogik.

## TA5 / TP5

Technisches Verfahren für sonstige Leistungserbringer nach § 302. Die 5 im
Paketnamen ist dieses Verfahren, nicht Anlage 5. Anlage 5 beschreibt
Urbeleg-Inhalte und gehört fachlich zu leistungen.

## UNA / UNH / UNT

Dienstsegmente der Nachricht: UNA setzt die Trennzeichen, UNH eröffnet die
Nachricht, UNT schließt sie. Sie gehören zur Gestalt, nicht zur
Abrechnungsentscheidung.
