# Kostenträger-IK — Registerprüfung (§ 302)

Für Krankenkassen und andere Kostenträger ist die **Kostenträgerdatei** des
GKV-Spitzenverbands (EDIFACT, Abruf über gkv-datenaustausch.de) die
verlässliche Quelle. `ta5py` prüft gegen eine **lokal geladene** Datei:

1. Ist die Karten-/Kostenträger-IK in der Datei enthalten?
2. Welche Annahme-/Abrechnungsstellen-IK ergibt sich aus den Verknüpfungen
   für den §‑302- / SLE-Kontext?

## Was die Prüfung bedeutet

| Aussage | Bedeutung |
|---------|-----------|
| **Im Register gefunden** | Die IK steht in der geladenen Kostenträgerdatei; ggf. ist eine Empfänger-IK auflösbar. |
| **Formal gültig** | Nur Struktur/Prüfziffer (`docs/de/ik.md`) — **ersetzt nicht** die Registerprüfung. |
| **Testat / Zertifizierung** | Ein Treffer in der Datei ist **kein** Projekt-Testat und keine Zusage, dass eine Kasse einen konkreten Leistungsnachweis annimmt. |

Formal gültige, aber nicht gelistete IKs bleiben **nicht gefunden**. Ohne geladene
Datei gibt es keinen positiven Existenz-Treffer („Register nicht verfügbar“).

## Aktualisierung

Operatoren laden die aktuelle SLE-Kostenträgerdatei vom offiziellen Kanal
(siehe `var/kostentraeger/README.md` bzw. `make download-kostentraeger`) und
spielen sie ein. Die Prüfung selbst braucht keinen Netzaufruf.

## Englische API

`verify_kostentraeger_ik`, `resolve_acceptance_ik`,
`KostentraegerVerificationResult` / `VerificationStatus` (ausführbare Logik nur
im englischen Quellcode).
