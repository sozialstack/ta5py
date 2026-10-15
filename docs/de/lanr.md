# Lebenslange Arztnummer (LANR) — formale Prüfung

Die Bibliothek `ta5py` prüft Lebenslange Arztnummern **offline** und **formal**:
neun Ziffern und die Prüfziffer an Stelle 7 aus den Stellen 1–6 (Gewichte
4,9,4,9,4,9; Prüfziffer = (10 − Summe modulo 10) modulo 10). Der
Arztgruppenschlüssel (Stellen 8–9) geht nicht in die Summe ein. Grundlage ist
die KBV-Arztnummern-Richtlinie nach § 75 Abs. 7 SGB V.

## Was die Prüfung bedeutet

- **Formal gültig** heißt nur: Struktur und Prüfziffer stimmen.
- Es bedeutet **nicht**, dass die Ärztin/der Arzt zugewiesen ist, dass der
  Fachgruppenschlüssel fachlich korrekt ist, dass eine Kasse die Nachricht
  annimmt, oder dass dieses Projekt testiert / zertifiziert ist.
- Fachgruppenkataloge sind **eigene Geschäftsregeln** — nicht Teil der
  Standardprüfung.

## Englische API

Alles auf `ta5py.Lanr`: `parse`, `is_valid`, `compute_check_digit`, sowie Teile
`physician` / `check_digit` / `specialty` und `is_formally_valid` (ausführbare
Logik nur im englischen Quellcode).
