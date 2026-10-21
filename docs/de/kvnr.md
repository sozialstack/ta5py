# Krankenversichertennummer (KVNR) — formale Prüfung

Die Bibliothek `ta5py` prüft die **zehnstellige unveränderbare**
Krankenversichertennummer **offline** und **formal**. Das ist die Nummer auf
der elektronischen Gesundheitskarte: ein Buchstabe, acht Ziffern, Prüfziffer
an Stelle 10.

Grundlage ist Anlage 1 zur Richtlinie nach § 290 SGB V. Der Buchstabe wird
durch seine Stelle im Alphabet ersetzt (`A` = `01` … `Z` = `26`). Diese beiden
Ziffern und die Stellen 2–9 werden von links mit den Gewichten
`1,2,1,2,1,2,1,2,1,2` multipliziert. Aus jedem Produkt wird die Quersumme
gebildet. Die Prüfziffer ist die letzte Stelle der Summe (Summe modulo 10).
Das ist **nicht** die Ergänzung auf den nächsten Zehner, wie bei der
Institutskennung oder der LANR.

Ein Kleinbuchstabe an der ersten Stelle gilt als derselbe Buchstabe.
Führende und nachgestellte Leerzeichen werden entfernt. Leerzeichen oder
Bindestriche in der Nummer gelten nicht.

## Was die Prüfung bedeutet

- **Formal gültig** heißt nur: zehnstellige Struktur und Prüfziffer stimmen.
- Es bedeutet **nicht**, dass die Nummer vergeben wurde, dass die Person
  versichert ist, dass eine Kasse die Nachricht annimmt, oder dass dieses
  Projekt testiert / zertifiziert ist.
- Vergaberegeln (zum Beispiel keine Ziffernfolge `666`, nicht mehr als drei
  gleiche Ziffern hintereinander) sind **keine** Ablehnungsgründe dieser
  Prüfung.
- Die 20-stellige Mitgliedsnummer und die 30-stellige
  Familienversichertennummer (Kassen-IK und Gesamt-Prüfziffer) sind **nicht**
  Gegenstand dieser Prüfung.
- Das TA5-Feld Versicherten-Nummer bleibt alphanumerisch mit höchstens 12
  Stellen und bedingt. Diese Prüfung ersetzt das nicht.

## Englische API

Alles auf `ta5py.Kvnr`: `parse`, `is_valid`, `compute_check_digit`, sowie Teile
`letter` / `serial` / `check_digit` und `is_formally_valid` (ausführbare Logik
nur im englischen Quellcode).
