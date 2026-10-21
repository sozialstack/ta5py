# ta5py — deutsche Begleitung

Operator-Dokumentation und Fachvokabular für SGB V TA5/EDIFACT
(Segmente, Nutzdaten, syntaktische KK-Prüfung).

Diese Begleitung enthält **keine** ausführbare Logik. Der englische Quellcode
in `ta5py` bleibt ohne dieses Paket vollständig.

**Haftung:** Dieses Projekt ist nicht kassenseitig zertifiziert und stellt kein
Testat dar.

## Themen

- [Glossar](glossar.md) — TA5/TP5, EDIFACT, Nutzsegmente, IK, LANR, BSNR, KVNR,
  Kostenträgerdatei
- [Institutskennung (IK) — formale Prüfung](ik.md) — Prüfziffer, Ersatzkennzeichen,
  siebenstellige Kassennummer (Präfix `10`)
- [Lebenslange Arztnummer (LANR) — formale Prüfung](lanr.md) — Prüfziffer,
  formal ≠ Zuweisung / Fachgruppe / Testat
- [Betriebsstättennummer (BSNR) — formale Prüfung](bsnr.md) — nur Struktur
  (keine öffentliche Prüfziffer)
- [Krankenversichertennummer (KVNR) — formale Prüfung](kvnr.md) — zehnstellige
  Kartennummer, Prüfziffer Summe modulo 10, formal ≠ vergeben / versichert / Testat
- [Kostenträger-IK — Registerprüfung (§ 302)](kostentraeger-ik.md) —
  Kostenträgerdatei als Quelle, Existenz und Empfänger-IK
