# Betriebsstättennummer (BSNR) — formale Prüfung

Die Bibliothek `ta5py` prüft Betriebsstättennummern **offline** und **formal**
als **Struktur**: genau neun Ziffern nach Trim. Stellen 1–2 sind der
KV-Landes-/Bezirksstellenschlüssel (bzw. besondere Versorgungsbereich-Präfixe);
Stellen 3–9 kennzeichnen die Betriebsstätte. Es gibt **keine** öffentliche
Prüfziffer für die BSNR in der KBV-Arztnummern-Richtlinie.

## Was die Prüfung bedeutet

- **Formal gültig** heißt nur: neun Ziffern, keine anderen Zeichen.
- Es bedeutet **nicht**, dass die Betriebsstätte existiert, dass eine KV die
  Nummer vergeben hat, dass eine Kasse die Nachricht annimmt, oder dass dieses
  Projekt testiert / zertifiziert ist.
- KV-Präfix-Kataloge (Whitelist) sind **eigene Geschäftsregeln** — nicht Teil
  der Standardprüfung.

## Englische API

Alles auf `ta5py.Bsnr`: `parse`, `is_valid`, sowie Teile `kv_region` / `site`
und `is_formally_valid` (ausführbare Logik nur im englischen Quellcode).
