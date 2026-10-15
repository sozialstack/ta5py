# Institutskennung (IK) — formale Prüfung

Die Bibliothek `ta5py` prüft Institutskennungen **offline** und **formal**:
neun Ziffern und die Prüfziffer über die Stellen 3–8 (Gewichte 2,1,2,1,2,1;
bei Produkten über 9 wird 9 abgezogen; Summe modulo 10). Die Klassifikation
(Stellen 1–2) geht nicht in die Summe ein. Grundlage ist das Gemeinsame
Rundschreiben IK (Darstellung u. a. bei Wikipedia mit Verweis auf IK 06/2020
auf gkv-datenaustausch.de).

## Was die Prüfung bedeutet

- **Formal gültig** heißt nur: Struktur und Prüfziffer stimmen.
- Es bedeutet **nicht**, dass die Einrichtung in einem Verzeichnis existiert,
  dass eine Kasse die Nachricht annimmt, oder dass dieses Projekt testiert /
  zertifiziert ist.
- Ob eine Kostenträger-IK in der offiziellen Kostenträgerdatei steht und wohin
  §‑302 adressiert wird, steht in
  [kostentraeger-ik.md](kostentraeger-ik.md) (Registerprüfung).


## Ersatzkennzeichen

Selbstzahler-Ersatzkennzeichen (z. B. Muster wie `97…`), die analog zu den
ARGE-IK-Vorgaben gebildet sind, können die Prüfziffer ebenfalls erfüllen.
Die **Standardprüfung schließt sie nicht aus**. Wer sie ablehnen will, braucht
eine **eigene, explizite Geschäftsregel** — nicht die formale IK-Prüfung.

## Siebenstellige Kassennummer

Ältere Gesundheitskarten zeigen teils eine siebenstellige Kassennummer.
Mit Präfix `10` entsteht ein neunstelliger IK-Kandidat; die Prüfziffer muss
danach weiterhin zur formalen Regel passen.

## Englische API

Alles auf `ta5py.Ik`: `parse`, `is_valid`, `compute_check_digit`,
`from_kassennummer`, sowie Teile `classification` / `region` / `serial` /
`check_digit` und `is_formally_valid` (ausführbare Logik nur im englischen
Quellcode).
