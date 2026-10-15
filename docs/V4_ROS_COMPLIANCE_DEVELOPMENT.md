# R3D-Planner V4
# ROS 2 Compliance Development

Stand: 15. Oktober 2026; fortgeführt bis V4-028. M01 ist freigegeben und implementiert, M02 ausdrücklich zurückgestellt und ausschließlich als Vorschlag dokumentiert. Historische Abschnitte beschreiben ihren jeweils datierten Entwicklungsstand; der aktuelle Überblick steht in4,7–9 und18. Dieses Dokument ist das einzige zentrale Entwicklungsprotokoll für V4. Es trennt den historischen Bestand, geplante Maßnahmen, tatsächlich durchgeführte Änderungen und deren Nachweise. Die Erstinitialisierung verändert ausschließlich dieses Dokument und legt den Branch V4 an. Sie enthält keine Implementierung der Arbeitspakete AP01 bis AP10.

## 1. Zielsetzung

V4 soll die bestehende funktionale R3D-Planner-Implementierung für eine nachvollziehbare öffentliche Bereitstellung im ROS-2-Ökosystem vorbereiten. Gegenstand sind Paketmetadaten, Dependency-Deklarationen und rosdep, Lizenz- und Datenrechte, installationsunabhängige Ressourcen, öffentliche ROS-Verträge, Tests, CI/CD, Nutzungsdokumentation und Releasevorbereitung. Die beiden ursprünglichen Pakete behalten `ament_python` und setuptools. Das freigegebene zusätzliche Paket `r3d_interfaces` verwendet für ROS-IDL `ament_cmake`/rosidl; die Pythonpakete werden nicht in CMake konvertiert.

PCD-Verarbeitung, Traversierbarkeitsanalyse, Graphrekonstruktion, A*, Navigationseinstiegspunkte und die V3-Integration sind Vorleistungen. V4 werden ausschließlich begründete und nachgewiesene Änderungen nach dem Baseline-Commit zugerechnet. Neue SLAM-/Mappingverfahren, der Ersatz des Planners, ein vollständiges Nav2-Redesign und neue Hardwaretreiber sind keine primären Ziele.

Die Initialisierung ist noch keine Freigabe für Codeänderungen. Gemäß Abschnitt 11 des Auftrags muss der initiale Plan zunächst vorgelegt werden; der Beginn des ersten Implementierungsarbeitspakets benötigt eine ausdrückliche Freigabe. Pushes, Releases und Pull Requests sind nicht beauftragt.

**Nutzerentscheidung vom 13. Oktober 2026:** „Überspringe die Lizenzierung vorerst, hierzu muss ich erst noch recherchieren“. AP01 wird deshalb zurückgestellt und als `BLOCKED` geführt. Diese Entscheidung erlaubt keine Annahme einer Projektlizenz und beseitigt keine Veröffentlichungshindernisse. Unabhängige technische Arbeiten können nach Planfreigabe beginnen. Es wird keine Lizenz ausgewählt, angewendet oder stillschweigend aus `setup.py` übernommen.

**Fortführung am 13. Oktober 2026:** Der folgende Auftrag hebt die Rückstellung ausschließlich für Recherche, Copyright-/Provenienzbewertung und wissenschaftliche Dokumentation auf. Der ergänzte Auftrag enthält die Entwicklererklärung Bastian Aumers und erlaubt ausdrücklich die Analyse der benannten externen LiDAR-Repositories. Verbindliche Lizenzwahl, Lizenz-/Headeranwendung, AP02/AP03-Implementierung und GitHub-/Remoteänderungen bleiben nicht freigegeben. V4-002/V4-003 dokumentieren diese neue Abgrenzung; die frühere Rückstellung bleibt historisch nachvollziehbar.

**Verbindliche Fortführung V4-004, 13. Oktober 2026:** Der neue Nutzerauftrag wählt **Apache License 2.0 (Apache-2.0)** für autorisierte eigene Softwarebestandteile von r3d_planner und r3d_preprocessor und gibt die technische Anwendung ausdrücklich frei. Root-LICENSE, zwei Manifest-Lizenzfelder und SPDX-Kommentarheader der 18 bereits zugeordneten eigenen Python-Dateien sind umgesetzt und statisch geprüft. Copyright-Attribution: **2026 Bastian Aumer**, vorhandene eigene Hinweise erhalten. Die früheren Rückstellungen/Recherchegrenzen oben und in V4-001 bis V4-003 beschreiben ihren damaligen Stand und sind durch diese gezielte Freigabe für AP01 überholt.

**Geltungsbereich der Root-LICENSE:** Der unveränderte Apache-Text gilt für die eigenen Softwarebestandteile, für die Bastian Aumer die erforderlichen Rechte besitzt. Die Datei ersetzt keine Bedingungen fremder Software. Die sechs OSRF-Testtemplates behalten ihre eigenen Apache-/Copyright-Hinweise; externe Libraries und LiDAR-Software behalten ihre Originallizenzen. **Die früheren beiden PCD-Karten wurden unter V4-005 aus dem aktiven Tree entfernt; keine Apache-Freigabe für historische Objekte.** Unbekannte Herkunft, Dokumentations-/Ressourcenrechte, ältere Bytecode-Artefakte sowie arbeits-/dienstvertragliche Befugnisse werden nicht durch einen Root-Text oder Manifesttag als geklärt dargestellt. Technische Lizenzimplementierung ist keine vollständige rechtliche Releasefreigabe. AP02/AP03 sind nicht begonnen; kein Push oder Release.

**V4-005, 14. Oktober 2026:** Die beiden alten PCD-Beispielkarten sind aus dem aktiven V4-Tree entfernt; beim Eingang waren beide Löschungen bereits im Working Tree vorhanden. Keine Ersatzkarten. Nutzer konfigurieren eigene PCD-Dateien, shipped maps-Werte sind leer. Die externe Konfiguration über R3D_CONFIG_DIR funktioniert auch ohne den ursprünglichen Source-Checkout. Historische Inventare, ältere V4-Einträge und das unveränderte PDF beschreiben weiterhin korrekt den früheren Kartenbestand. **Die Git-Historie enthält die alten Daten weiterhin**; ein vollständiger Git-Klon ist nicht mit einem datenfreien Tree-/Paketartefakt gleichzusetzen.

**V4-006, 14. Oktober 2026:** Technische AP01-Verifikation **VERIFIED** für Originaltext, 18 eigene SPDX-/Copyrightheader, Apache-Manifeste/Setup, erhaltene sechs Fremdtemplates, dokumentierte LiDAR-Trennung/Notice, datenfreien aktiven Tree und tatsächlich geprüfte Lizenzmitnahme in sdists, Wheels und Copy-colcon-Shares. Je Paket ist eine identische lokale LICENSE-Kopie hinzugefügt; Root-LICENSE unverändert. Keine vollständige rechtliche/transitive/Debian-/Buildfarm-Freigabe. Arbeitspaket AP01 insgesamt bleibt BLOCKED für individuelle Rechts-/Release-Gates, AP04/AP06/AP08/AP10 IN PROGRESS; AP02/AP03 NOT STARTED.

**V4-007, 14. Oktober 2026:** Das zuvor unversionierte historische PDF ist unverändert in Git aufgenommen: 33 Seiten, 298707 Byte, SHA-256 8c3603ec2dac85c5cabcca7ae7e85c8d8c709663fa02fabd09039274a2b35383. Frühere Angaben „unversioniert“ beschreiben den jeweiligen früheren Eingangszustand, keine aktuelle Anweisung. Historischer Inhalt/alte Kartendarstellung und Software-Lizenzgrenzen bleiben unverändert.

**V4-008/V4-009, 14. Oktober 2026:** AP02 im freigegebenen technischen Umfang **VERIFIED**: beide Manifeste und setup.py konsistent Version 0.0.1, fachliche englische Beschreibungen, vorhandene Repository-/Bugtracker-URLs und bekannte Autorrolle. Maintainer bauya/baau1001@stud.hs-kl.de, Namen, ament_python, Dependencies, Entry-Points und Lizenzressourcen unverändert. Entwicklungsversion, kein ROS-Release. Der Entwickler erklärt eigene Aufnahme/Verarbeitung der früheren PCDs und keine verletzten Datenschutzauflagen; das ist dokumentierte Selbstauskunft, kein unabhängiger Rechtenachweis. V4 bleibt datenfrei; gewünschte spätere Kartenentfernung aus V1/V2/V3/main ist nur dokumentiert und nicht ausgeführt.

**V4-010/V4-011, 14. Oktober 2026 – aktueller Stand:** Historische lokale V1/V2/V3/main-Trees durch vier neue getrennte Commits datenfrei, Ursprung/13 alte Commits/Remote-Trees/PDF unverändert. AP03-Manifeste korrigiert, 26 externe Humble/Jammy-Keys und Install-Simulation VERIFIED, Copy-Build/43 Funktionstests VERIFIED. Gesamtsuite: 49 Tests, 45 bestanden, 2 bestehende Flake8-Fehler, 2 Copyright-Skips. AP03 insgesamt **IN PROGRESS**: tatsächliche rosdep-Installation/check in vollständig versorgter isolierter Umgebung nicht ausgeführt; Hostcheck meldet fehlende Apt-Open3D/NetworkX. Kein globaler Python-/System-/Conda-Eingriff, kein Push. Frühere NOT STARTED-Angaben in datierten Einträgen sind historische Snapshots. Aktuelle Annahmen und Grenzen in Abschnitt 15.

## 2. Technischer Ausgangsstand

### 2.1 Verbindliche Referenz und lokale Umgebung

| Merkmal | Festgehaltener Ausgangsstand |
| --- | --- |
| Repository | `RoboProjekt/R3D-Planner`, ausschließlich dieses Repository; R3D_null und externe Forks ausgeschlossen |
| Lokaler Pfad | `/home/bauya/Desktop/Gits/Github/R3D-Planner` |
| Baseline-Branch | `main` |
| Baseline-Commit | `c65642fe56015556f696364a724cb5b976a27888` |
| Baseline-Stichtag | 12. Oktober 2026 |
| Commitdatum der Baseline | 17. September 2026, 00:56:32 +02:00; vom Stichtag zu unterscheiden |
| Beginn der V4-Dokumentation | 13. Oktober 2026, Zeitzone Europe/Berlin |
| Entwicklungsbranch | `V4`, unmittelbar vom Baseline-Commit angelegt |
| Primäre Zielumgebung | ROS 2 Humble, Ubuntu 22.04, Python 3.10 |
| Lokal festgestellt | Ubuntu 22.04.5 LTS; `/opt/ros/humble` und dessen Setup-Datei vorhanden; `/usr/bin/python3` meldet 3.10.12; rosdep 0.27.0 und colcon vorhanden |
| Abweichende aktive Python-Umgebung | `python3` auf dem aktuellen PATH ist `/home/bauya/miniconda3/bin/python3` und meldet 3.14.6; das ist nicht die Humble-Zielumgebung |
| ROS-Pakete | `r3d_planner`, `r3d_preprocessor` |
| Build-/Paketierungssystem | Python, setuptools, `ament_python`, colcon; keine CMake-Konvertierung |
| Umfang des Baseline-Trees | 59 versionierte Dateien, darunter 26 Python-Dateien einschließlich Setup, Launch und Tests |
| Historische Referenz | [Historischer Entwicklungsbericht](R3D_Planner_Development_History.pdf), 33 Seiten, vollständig gelesen |
| SHA-256 des unveränderten Berichts | `8c3603ec2dac85c5cabcca7ae7e85c8d8c709663fa02fabd09039274a2b35383` |

Die vorhandene ROS-Installation und statische Parsebarkeit belegen noch keinen erfolgreichen ROS-Import, Clean-Build oder funktionierenden Lauf. Keine Abhängigkeit wurde installiert, aktualisiert oder global repariert. Die Trennung von System-Python und Conda ist bei späteren Nachweisen explizit zu prüfen; bestehende historische Packaging-Konflikte werden nicht als aktuell reproduziert ausgegeben.

### 2.2 Git-Prüfung und Schutz bestehender Arbeit

Vor dem Branchwechsel war `main` aktiv, HEAD entsprach exakt der Baseline. `git cat-file -t` bestätigte ein Commitobjekt; `git merge-base --is-ancestor <Baseline> main` war erfolgreich. Lokal existierte nur `main`; die Entwicklungsstände V1, V2 und V3 waren als `origin/V1`, `origin/V2` und `origin/V3` vorhanden. Zusätzlich bestanden `origin/main` und der Alias `origin/HEAD`. V4 existierte weder lokal noch als vorhandene Remote-Tracking-Referenz. Die lokale Tagliste war leer. Es erfolgte kein Fetch; die Aussage über Remote-Tracking-Refs ist keine neue Serverabfrage.

| Vorhandene Referenz vor V4 | SHA |
| --- | --- |
| `main`, `origin/main` | `c65642fe56015556f696364a724cb5b976a27888` |
| `origin/V1` | `01348f3285a0e7582f70cc5f2ed3d1bf4b7f904b` |
| `origin/V2` | `3abd002e8cc9e7a26cacaf43a5c20b1822664f14` |
| `origin/V3` | `3752404a08867e9e6f3725300b88e148d4d5be37` |

Der Working Tree war nicht vollständig sauber: ausschließlich `docs/R3D_Planner_Development_History.pdf` war unversioniert. Index und versionierte Dateien waren unverändert. Das PDF stammt aus dem vorherigen Dokumentationsauftrag und ist nicht Bestandteil des historischen Commit-Trees. Weil Ausgangs- und Ziel-Tree identisch waren und keine Pfadkollision bestand, gefährdete der Branchwechsel diese Arbeit nicht. Es gab kein Stash, Löschen, Überschreiben oder automatisches Committen vorhandener Arbeit. Das PDF bleibt unverändert und unversioniert; im Initialisierungscommit wird ausschließlich dieses neue V4-Protokoll aufgenommen.

V1/V2/V3/main und die vorhandenen Remote-Tracking-Refs bleiben unverändert. Es werden keine historischen Commits umgeschrieben, keine Tags angelegt und keine Remotes verändert. Der Name V4 ist ein Entwicklungsbranch, keine Festlegung einer Paketversion `4.0.0`.

### 2.3 Bereits vor V4 vorhandene Fähigkeiten

Die Kapitel 4, 6, 7 und 10 des historischen Berichts ordnen die folgenden Fähigkeiten dem Vorbestand zu. Die aktuelle Sichtprüfung bestätigt ihre Dateien am Baseline-Tree.

| Bereich | Bereits bestehende Implementierung | Repository-Nachweis am Baseline-Commit |
| --- | --- | --- |
| Preprocessing | PCD-Laden, Voxelisierung, Bodenaugmentation/-füllung, Roboter-Clearance, floor/narrow/stair_access/obstacle-Klassifikation, RGB-PCD-Export | `r3d_preprocessor/r3d_preprocessor/r3d_pcd_analyser.py`, `VoxelTraversabilityAnalyzer` |
| Planung | Farbabhängige Graphrekonstruktion, SciPy-KDTree-Snapping, NetworkX-Graph, gewichtetes A*, Pfad- und Marker-Ausgabe | `r3d_planner/r3d_planner/r3d_pcd_path.py`, `GlobalGraphPlanner` |
| ROS-Integration | `ComputePathToPose`, Topics, Trigger-Service, RViz-Ziele, lokaler Filter, planarer Path Follower | Planner-, RViz-, Filter- und Follower-Module im gleichnamigen Python-Paket |
| Pose und TF | Standard-Odometry, zeitgestempelte map/odom-Transformation, Frame-/Frischeprüfung, expliziter Startmodus, Null-Twist bei Poseverlust | `r3d_planner/r3d_planner/odometry.py`; Planner `execute_callback`; Follower `control_loop` |
| Konfiguration | Zentrale YAML, Robotwahl Go2W/alternative Datei, gemeinsame Parameter, strikte Schlüssel-/Wertprüfung, Typnormalisierung | `configuration.py`; `config/planner_config.yaml`; `config/robots/Go2W.yaml` |
| Launch | Vier installierte Python-Launchdateien; Planner mit unabhängig optionalem Filter/RViz, Analyse, Kartenanzeige und separater Follower | `r3d_planner/launch/`; `launching.py`; `r3d_planner/setup.py:21-28` |
| Paketgrundlage | Zwei Format-3-Manifeste, Buildtyp-Export, ament-Index-Marker, setup.cfg, Console-Scripts | Beide `package.xml`, `setup.py`, `setup.cfg` und `resource/`-Verzeichnisse |
| Tests | Neun funktionale Testfunktionen mit 20 parametrisierten Fällen; sechs Linter-Templates | `r3d_planner/test/test_configuration.py`; beide `test/`-Verzeichnisse |
| Dokumentation | README, Installation, Architektur, Konfiguration, bekannte Probleme, V3-/Referenzdokumentation | `README.md`, `INSTALL.md`, `docs/ARCHITECTURE.md`, `docs/CONFIGURATION.md`, `docs/KNOWN_ISSUES.md`, `docs/V3_IMPLEMENTATION.md`, `docs/REFERENCE_COMPARISON.md`, `docs/README_AUDIT.md` |

Die frühere V3-Ausführung „20 Tests in 40,07 s“ ist in `docs/V3_IMPLEMENTATION.md:126-145` berichtet. Sie wurde in dieser V4-Initialisierung nicht wiederholt. Der manuelle `path_test` ist ein statischer TF-Publisher, keine automatisierte Testsuite. CMake, C++-Bibliotheken und eigene ROS-IDL-Nachrichten/Services/Actions sind im aktuellen Projekt nicht vorhanden.

### 2.4 Relevante Struktur

```text
R3D-Planner/
  README.md, INSTALL.md, README_r3d_planner.txt
  docs/
    ARCHITECTURE.md, CONFIGURATION.md, KNOWN_ISSUES.md
    README_AUDIT.md, REFERENCE_COMPARISON.md, V3_IMPLEMENTATION.md
    R3D_Planner_Development_History.pdf   unverändert, unversioniert
    V4_ROS_COMPLIANCE_DEVELOPMENT.md     einziges neues Entwicklungsprotokoll
  r3d_planner/
    package.xml, setup.py, setup.cfg, resource/r3d_planner
    config/                             zentrale YAML, Robotprofil, Legacy-Nav2-YAML
    launch/                             vier *.launch.py
    r3d_planner/                        Nodes und gemeinsame Helfer
    test/                               funktionale Tests und Linter
  r3d_preprocessor/
    package.xml, setup.py, setup.cfg, resource/r3d_preprocessor
    maps/                               zwei PCD-Dateien, Rechte ungeklärt
    r3d_preprocessor/                   Analyzer und Publisher
    test/                               drei Linter-Templates
```

Es existieren versionierte `__pycache__/*.pyc`, ältere TXT-Anleitungen und ein alternativer PCD-Publisher ohne Console-Entry. Ihre weitere Behandlung gehört in eine begründete spätere Änderung; bei der Initialisierung werden sie nicht entfernt. Eine CI-Konfiguration, Changelogs und eigenständige Maintenance-/Security-/Stabilitätsrichtlinien sind im aktuellen Dateibestand nicht vorhanden.

### 2.5 Ausgangsbefunde mit Handlungsbedarf

Die folgenden Befunde beschreiben den unveränderten main-Bestand, nicht bereits erledigte V4-Arbeiten. Pfade und Zeilen beziehen sich auf den Baseline-Commit; nach späteren Änderungen ist der historische Bezug beizubehalten.

| ID | Befund und Evidenz | Einordnung / Zuordnung |
| --- | --- | --- |
| B01 | Kein LICENSE/COPYING im Repository; beide Manifeste Zeile 8 enthalten `TODO: License declaration`, Setup nennt `Apache-2.0`; Copyrightheader und Apache-Notices in Testtemplates ergeben keinen geklärten Gesamtgrant | Veröffentlichungshindernis, AP01; auf Nutzerwunsch zurückgestellt |
| B02 | Datenherkunft und Weiterverteilungsrechte der beiden `r3d_preprocessor/maps/*.pcd` sind nicht bestimmbar | Veröffentlichung der gebündelten Daten ungeklärt; AP01/AP04 |
| B03 | Beide Manifeste Zeilen 5-6: Version `0.0.0`, TODO-Beschreibung; Setup-Version `0.0.1`; Maintainer vorhanden, keine Manifest-URL-/Author-Elemente | Versions-/Beschreibungsproblem AP02; URLs/Autoren empfohlen, kein fehlender Maintainer behauptet |
| B04 | Beide Pakete importieren Open3D, Planner zusätzlich NetworkX, std_msgs und sensor_msgs_py; entsprechende direkte Manifestdeklarationen fehlen | Dependency-Vollständigkeit AP03; AST-Importinventar am 13.10.2026 geprüft |
| B05 | `numpy` in beiden Manifesten, `scipy` beim Planner; README Zeile 44 und INSTALL Zeilen 145-163 dokumentieren `--skip-keys="numpy scipy"` | rosdep-Reproduzierbarkeit offen; tatsächliche aktuelle Schlüsselprüfung steht aus, AP03 |
| B06 | `tf2_ros` ist beim Planner bereits deklariert; Python-TF2-Provider, System-/ROS-Schlüssel und Build-/Runtime-/Testkategorien sind gezielt abzugleichen | Kein pauschales „TF2 fehlt“; AP03 |
| B07 | `configuration.py:40-55` akzeptiert Source-/Symlink-Konfiguration, verwirft kopierte Installations-YAML ohne `R3D_CONFIG_DIR`; vorhandener Test Zeile 208 sichert gerade diese alte Politik ab | Demonstrierte Installationsbeschränkung; Verhalten und zugehöriger Test müssen gemeinsam geändert werden, AP04/AP06 |
| B08 | `planner_config.yaml:5-6` verweist auf benachbarte Source-Karten; Preprocessor `setup.py:22-27` installiert keine Karten; Analyzer Zeilen 354-358 schreibt neben die Eingabedatei | Installationspfade und Schreibrechte getrennt lösen; Karten nicht ohne Rechteklärung neu distribuieren, AP04 |
| B09 | Planner `r3d_pcd_path.py:261-267` setzt narrow als z=1, w=1; Follower Zeile 145 wertet orientation.z als Flag aus | Ungültige Quaternion und semantischer Missbrauch; interne Verbraucher gemeinsam migrieren, AP05/AP06 |
| B10 | Absolute Pfad-/RViz-/Filtertopics und absoluter RViz-Action-Client bei relativem Server; `configuration.py:92-97` verlangt absolute konfigurierte Topics | Namespace-Komposition eingeschränkt; absolute Namen sind für sich kein verbotener ROS-Name, AP05 |
| B11 | Filter `r3d_local_filter.py:74-89` interpretiert Bytes als drei dicht gepackte float32-Werte; kein allgemeines Feld-/Stride-/Endian-/Framehandling | Konkrete PointCloud2-Portabilitätsgrenze, AP05/AP06 |
| B12 | Planner `execute_callback:208-274` prüft Frames/use_start, aber keine Cancellation-Behandlung; planner_id ohne Auswertung, Ergebnisdaten begrenzt, Nearest-Snapping ohne Maximaldistanz | Vorhandene Prüfung erhalten; Vertrag distributionsbezogen klären und testen, AP05/AP06/AP09 |
| B13 | Follower konsumiert Hindernisse, nicht Cliff-/Stair-Ausgänge; Hindernisfrische/Watchdog fehlt; Filterradius 0,65 m versus Stopfenster 0,6 m | Belegte Integrationsgrenzen, kein gemessener Vorfall und keine allgemeine Indexpflicht; Bewegungsvertrag vor Einsatz prüfen, AP05/AP06 |
| B14 | Copyrighttests sind übersprungen; historische Legacy-Flake8-Befunde und Testmodulnamenskonflikte sind dokumentiert; keine umfassenden Algorithmus-/Cloud-/Action-/Copy-Install-Regressionen | Tests vorhanden, Nachweislücken AP06; historische Fehlerzahlen nicht als neuer V4-Testlauf darstellen |
| B15 | Kein CI-Workflow, keine Coverageautomation, keine Quality Declaration; bisher nur Humble-Ziel dokumentiert | AP07/AP09/AP08; Quality Level und Multi-Distro-Support nicht behaupten |
| B16 | Keine Tags und Paket-Changelogs; Versions-/API-/Support-/EOL-Politik und Releaseprozess nicht festgelegt | AP08/AP10; fehlender Changelog relevant für geplanten Releaseablauf, Policies nicht pauschal Indexpflicht |

**Präzisierung gegenüber möglichen Fehlinterpretationen der Historienanalyse:** Das Fehlen eines `buildtool_depend` ist als Tatsache belegt, aber bei einem reinen `ament_python`-Paket allein kein nachgewiesener Mangel. Der offizielle Humble-Paketgenerator setzt für diesen Buildtyp ebenfalls keinen pauschalen `ament_python`-Buildtool-Eintrag. Deshalb wird kein ungeprüfter rosdep-Key `ament_python` ergänzt. Tatsächlich benötigte Packaging-Werkzeuge werden in AP03/AP04 anhand des Buildprozesses geprüft. Die historische PDF bleibt unverändert. Nachweis: [ros2pkg-Generator, Humble](https://github.com/ros2/ros2cli/blob/humble/ros2pkg/ros2pkg/verb/create.py), Initialisierung von `buildtool_depends` und Auswahl des Python-Buildtyps; zusätzlich lokal installierter Generator geprüft.

## 3. Anforderungen an die Veröffentlichung

### 3.1 A - ROS Index / rosdistro-Quellregistrierung

Nach den aktuellen rosdistro-Reviewkriterien sind öffentlich zugängliche Quellen, ROS-Pakete, passende Paketnamen und ein nachvollziehbarer Open-Source-Lizenztext mit entsprechender Manifestdeklaration grundlegende Prüfpunkte. Die Source-Registrierung verwendet Repository-URL, Zielbranch und Entwicklungsstatus. Aufnahme und späterer Binärrelease sind getrennte Vorgänge; eine Source-Registrierung beweist keinen erfolgreichen Buildfarm-Lauf. Der finale Eintrag unterliegt externer Prüfung. Quelle: [rosdistro Review Guidelines](https://github.com/ros/rosdistro/blob/master/REVIEW_GUIDELINES.md), insbesondere New package review checklist; [Humble: Index Your Packages](https://github.com/ros2/ros2_documentation/blob/humble/source/How-To-Guides/Releasing/Index-Your-Packages.rst).

Die Paketnamen `r3d_planner` und `r3d_preprocessor` erfüllen die lexikalischen REP-144-Pflichtregeln: Kleinbuchstaben/Ziffern/einfache Unterstriche, alphabetischer Anfang und mindestens zwei Zeichen. Der Projektpräfix besteht bereits. Eine Umbenennung ist daraus nicht erforderlich. Globale Namenskollisionen und die aktuelle öffentliche Erreichbarkeit wurden noch nicht erneut geprüft. Für einen künftigen rosdistro-Eintrag ist ein passender Repository-Schlüssel zu wählen; aus dem GitHub-Anzeigenamen wird hier keine erforderliche Repository-Umbenennung abgeleitet. Quelle: [REP-144](https://github.com/ros-infrastructure/rep/blob/master/rep-0144.rst).

### 3.2 B - Dependency-Deklaration und rosdep

Die Manifeste müssen die tatsächlich benötigten externen Abhängigkeiten mit passenden ROS-Paketnamen oder rosdep-Schlüsseln abbilden. Zu prüfen sind Zielbetriebssystem/-distribution, Kategorien und das Verhältnis zwischen Workspace-Paketen und Systempaketen. Für reine Python-Runtime-Imports ist `exec_depend` regelmäßig passend; Testbedarf wird separat abgebildet. Ein lokaler erfolgreicher Import reicht für Dependency-Vollständigkeit nicht aus. Quelle: [Humble rosdep-Tutorial](https://github.com/ros2/ros2_documentation/blob/humble/source/Tutorials/Intermediate/Rosdep.rst).

Die Pflichtfelder des Format-3-Manifests sind Name, numerische Version im Format MAJOR.MINOR.PATCH, Beschreibung, Maintainer mit E-Mail und Lizenzangabe. URL-/Author-Tags sind optionale empfohlene Metadaten. Ein gewähltes SemVer-Stabilitätsversprechen ist davon getrennt. Quelle: [REP-149](https://github.com/ros-infrastructure/rep/blob/master/rep-0149.rst), Required Tags, version und Dependency tags.

**Projektabnahme AP03:** vollständige Humble-/Jammy-Auflösung ohne `--skip-keys`, anschließend Installation und `rosdep check` in einer isolierten, dokumentierten Umgebung. Schlüssel wie `python3-numpy` und `python3-scipy` sind zunächst Kandidaten; Open3D-/NetworkX-/TF2-Provider müssen ebenfalls validiert werden. In dieser Initialisierung wurde kein `rosdep resolve`, `rosdep update`, `rosdep install` oder `rosdep check` ausgeführt. Eine Aktualisierung des lokalen rosdep-Caches und Systeminstallationen gehören erst zum genehmigten Folgeschritt.

### 3.3 C - Bloom und ROS Buildfarm

Für den vorgesehenen Releaseweg sind konsistente Paketversionen, nachvollziehbare Upstream-Refs, geeignete Release-Metadaten und ein Release-Repository/-Track vorzubereiten. Der offizielle Erst-Release-Leitfaden sieht paketweise `CHANGELOG.rst` und einen Versionsschritt vor. Die konkreten Releasewerkzeuge und der Zielstand sind zum Ausführungszeitpunkt erneut zu prüfen. Quelle: [Humble: First Time Release](https://github.com/ros2/ros2_documentation/blob/humble/source/How-To-Guides/Releasing/First-Time-Release.rst).

Technisch sind vollständige für die Zielplattform verfügbare Dependencies und funktionierende installierte Pakete nachzuweisen. Die rosdistro-Richtlinien unterscheiden systempaketbasierte Dependencies von pip-only-Schlüsseln; letztere eignen sich laut Richtlinie nicht für den offiziellen Binärrelease. Eine lokale pip-Umgebung oder ein Skip-Workaround genügt daher nicht als Buildfarm-Lösung. Quelle: [rosdistro Review Guidelines, pip keys](https://github.com/ros/rosdistro/blob/master/REVIEW_GUIDELINES.md#pip-keys-standard-disclaimer).

**Projektabnahme AP04/AP10:** normaler Copy-Install, verfügbare read-only Ressourcen, beschreibbare separate Analyseausgaben und nicht vom Source-Checkout abhängige Launch-/Node-Einstiege. Ein offizieller Buildfarm-Erfolg kann erst nach einem tatsächlich erfolgten Release unabhängig bestätigt werden. Hier werden weder Bloom noch Release-/PR-Erzeugung gestartet.

### 3.4 D - ROS-Konventionen und bewährte Verfahren

Konsistente Namespaces/Remapping, verständliche Node-/Topicnamen, gültige Quaternionen, korrekte PointCloud2-Feldinterpretation, dokumentierte Frame-/Zeit-/QoS-Verträge und gezielte Regressionen sind technische Interoperabilitätsziele. Konkrete Verletzungen eines Nachrichtensemantikvertrags sind von einer bloßen Präferenz für bestimmte Namensstile zu unterscheiden. Ein neues Systemlaunch ist nur bei belegtem Nutzerbedarf vorgesehen; die vier vorhandenen Subsystemlaunches werden erhalten und verbessert.

CI, konsistente Lints und aktualisierte Nutzungsanleitungen sind Projektziele für reproduzierbare Pflege. Das Vorhandensein eines bestimmten Formatters, clang-Werkzeugs oder CMake-Testschalters wird bei diesen Python-Paketen nicht zur allgemeinen ROS-Releasepflicht erklärt.

### 3.5 E - Optionale Qualitätsziele / REP-2004

REP-2004 beschreibt abgestufte Qualitätskonzepte zu Versionierung, Änderungskontrolle, API/ABI, Dokumentation, Tests/Coverage, Dependencies, Plattformen und Security. Eine Quality Declaration setzt belegte Aussagen für ein bewusst gewähltes Ziel voraus. V4 beansprucht noch keinen Quality Level. Coverage-Schwellen, umfassende Security-/EOL-Policies, Typprüfung und weitere Plattformen werden proportional zum Projektumfang entschieden und nicht pauschal als Source-Index-Voraussetzung behandelt. Quelle: [REP-2004](https://github.com/ros-infrastructure/rep/blob/master/rep-2004.rst).

### 3.6 Quellenstand und Grenzen

Die verlinkten offiziellen Spezifikationen, ROS-Dokumentationsquellen und rosdistro-Richtlinien wurden am 13. Oktober 2026 gelesen. Die HTML-Endpunkte von docs.ros.org/ros.org lieferten teils eine Zugriffssperre; gelesen wurden die offiziellen GitHub-/Raw-Quellen. Branchlinks sind veränderlich und vor einer tatsächlichen Veröffentlichung erneut zu prüfen. Eine externe Annahmeentscheidung, aktuelle Namensreservierung oder rechtliche Freigabe wird daraus nicht abgeleitet. Repositorybefunde und rechtliche Unbekannte bleiben getrennt.

## 4. Entwicklungsplanung

### 4.1 Status und Prioritäten

`NOT STARTED`: Umsetzung nicht begonnen. `IN PROGRESS`: Teile in Bearbeitung. `BLOCKED`: ein explizit benannter Sachverhalt verhindert den Abschluss. `COMPLETED`: Umsetzung erfolgt, Abnahme noch nicht vollständig belegt. `VERIFIED`: sämtliche für den konkreten Eintrag definierten Kriterien tatsächlich geprüft. Ein verifizierter Dokumentationseintrag verifiziert nicht automatisch sein gesamtes Arbeitspaket.

P0 bezeichnet ein Hindernis für die vorgesehene Veröffentlichung oder deren grundlegenden technischen Nachweis, P1 wichtige ROS-/Interoperabilitätsarbeit, P2 empfohlene Qualitätsverbesserung und P3 optionale Ergänzung. Die Priorität ist keine Aussage, dass jeder einzelne Teilpunkt formal verpflichtend wäre.

### 4.2 AP01 - Lizenzierung und Distributionsrechte

| Feld | Planung |
| --- | --- |
| Ausgangsstand | Setup nennt Apache-2.0; Manifest-TODO, Copyrightheader und fremde Testtemplate-Notices; kein LICENSE; zwei Karten gebündelt |
| Probleme | B01/B02: Code-/Datenprovenienz, Berechtigung zur Lizenzwahl, Umfang und notwendige Notices nicht bestimmbar |
| Geplante Änderung | Lizenzvergleich/Inventur liegen vor; Apache-2.0-Entscheidung und technische Anwendung für zugeordnete Eigenanteile unter V4-004 abgeschlossen. Übrig bleiben Vertrags-/Karten-/konkrete Artefakt- und Distributionsnachweise |
| Priorität | P0 |
| Abhängigkeiten | Lizenzwahl und technische Anwendung am 13.10.2026 ausdrücklich autorisiert; Entwicklererklärung dokumentiert. Unabhängige Vertrags-/Befugnis-/Datenklärung und konkrete Distributionsprüfung bleiben offen |
| Abschlusskriterien | Rechte und Distributionsumfang nachvollziehbar; autorisierte Lizenzentscheidung; konsistente Dateien/Metadaten, mitzugebende Notices geklärt; keine unbelegten Bibliotheks-Kompatibilitätsbehauptungen |
| Aktueller Status | **BLOCKED** insgesamt für vollständige rechtliche Releasefreigabe; technische AP01-Implementierung inklusive aktiver Kartenentfernung/Lizenzmitnahme **VERIFIED** (V4-004 bis V4-006) |

AP01-Teilstände nach V4-004 (damalige Abnahme), fortgeführt durch V4-005/V4-006: Vergleich/Inventur/abgegrenzter Dependency-/LiDAR-Abgleich bleiben VERIFIED. **Apache-2.0 verbindlich gewählt; technische Lizenzimplementierung für 18 zugeordnete Eigenanteile und beide Manifeste COMPLETED, Dateien statisch VERIFIED.** Die rechtliche Rechteketten-/Arbeitgeber-/Karten-/Binärabnahme ist nicht verifiziert, daher Gesamtstatus BLOCKED. Lizenzwahl muss für die weitere technische Standardisierung nicht wiederholt werden; neue konkrete entgegenstehende Rechte würden die betroffenen Teile erneut blockieren. Aktiver Karten-Tree und konkrete sdist-/Wheel-/Copy-Sharemitnahme sind nun ebenfalls VERIFIED. Historische Gitkarten und vollständige Rechts-/Bundlefreigabe bleiben separat offen. Details: 11.19-11.21.

### 4.3 AP02 - Paketmetadaten

| Feld | Planung |
| --- | --- |
| Ausgangsstand | Zwei syntaktisch lesbare Format-3-Manifeste; passende Namen, Maintainer, ament_python-Export; Version 0.0.0 vs Setup 0.0.1 |
| Probleme | B03: TODO-Beschreibung, Versionswiderspruch, fehlende empfohlene URLs; rechtliche Angaben ungelöst |
| Geplante Änderung | Unter V4-008 umgesetzt: Version 0.0.1, konsistente Beschreibungen/URLs/Author; Maintainer/Lizenz erhalten. Releasepolitik/Kontaktzuständigkeit/Serverreview bleiben AP10, keine AP03-Keys geändert |
| Priorität | P0 für Release-Metadaten, P1 für empfohlene Ergänzungen |
| Abhängigkeiten | Freigabe des ersten Implementierungsschritts; Lizenzabschluss hängt von AP01 ab, übrige Korrekturen nicht |
| Abschlusskriterien | Manifest-/Setup-Metadaten konsistent und geprüft; übrige Platzhalter technisch soweit zulässig entfernt; Lizenzdeklarationen aus AP01 erhalten, rechtliche Gesamtfreigabe separat offen |
| Aktueller Status | **VERIFIED** - technische Metadaten/0.0.1/URL-/Author-/Maintainer-/Python-Konsistenz geprüft; vollständige ROS-/Rechtsfreigabe separat |

### 4.4 AP03 - Dependencies und rosdep

| Feld | Planung |
| --- | --- |
| Ausgangsstand | ROS-/Science-Deklarationen und Apt-Anleitung vorhanden; direkter Importabgleich initial erstellt; Skip-Workaround dokumentiert |
| Probleme | B04-B06: direkte Dependencies fehlen, Systemschlüssel und Kategorien ungesichert; Python-TF2-Provider prüfen; install_requires ist kein vollständiger ROS-Distributionsvertrag |
| Geplante Änderung | V4-011 korrigiert direkte Runtime-/Buildtool-/Testverträge und aktive Installationsanleitung; offene echte Installation/check in isolierter Umgebung als nächsten AP03-Nachweis behandeln |
| Priorität | P0 |
| Abhängigkeiten | Planfreigabe; AP02-Namens-/Metadatenkonsistenz; dokumentierte isolierte Humble-/Jammy-Umgebung ohne globale Reparatur; kein Lizenzentscheid für technische Schlüsselauskunft notwendig |
| Abschlusskriterien | Import-/Manifest-Abgleich und alle 26 externen Keys Humble/Jammy VERIFIED; vollständige tatsächliche Dependency-Installation und rosdep check ohne Skip bleiben erforderlich; Copy-Build/Funktionstests getrennt von Lint-/OS-Gesamtnachweis |
| Aktueller Status | VERIFIED für aktuellen Drei-Paket-Stand auf Humble/Jammy:32 externe Keys einzeln, tatsächliche rosdep install/check; neue Targets separat18.8 |

### 4.5 AP04 - Build und Installationsportabilität

| Feld | Planung |
| --- | --- |
| Ausgangsstand | setuptools, Marker-/Script-/Config-/Launchinstallation vorhanden; Source-/Symlink-Konfiguration wird bevorzugt |
| Probleme | B07/B08: Copy-Config absichtlich abgelehnt, Source-Kartenpfade, Karten nicht installiert, Ausgaben neben Eingabe; Conda-/System-Python-Abgrenzung erforderlich |
| Geplante Änderung | Normale Share-Ressourcenfindung, dokumentierter Override für Nutzerkonfiguration, strikte Validierung erhalten; installierte Eingaben von beschreibbaren Ausgaben trennen; Datenstrategie rechtlich separat klären |
| Priorität | P0 |
| Abhängigkeiten | AP03 für vollständigen Clean-Build; AP01 für öffentliche Mitlieferung der vorhandenen Karten, nicht für synthetische Installationsfixtures; AP06-Regressionen begleitend |
| Abschlusskriterien | Copy-Build/Install ohne Symlink; Tests bei nicht zugänglichem ursprünglichem Source-Checkout; Nodes/Launches/Config/Robotprofile auffindbar; Analyse schreibt ausschließlich in gewählten beschreibbaren Datenpfad; Source-/Override-Verhalten dokumentiert |
| Aktueller Status | VERIFIED für Humble-Copyinstallation, readonly Source-freie Ressourcen/Interfaces und getrennte Ausgabe; kein Relokations-/Debian-/Mehrplattformnachweis |

### 4.6 AP05 - ROS-Schnittstellen und Konfiguration

| Feld | Planung |
| --- | --- |
| Ausgangsstand | Standardnachrichten, Action, Service, Odometry/TF, QoS-Profile, YAML und vier Launches bereits vorhanden |
| Probleme | B09-B13: narrow-Quaternion, absolute/relative Namen, Cloud-Layout/Frameannahmen, Action-/QoS-/Integrationsgrenzen |
| Geplante Änderung | Jeweils eine belegte Vertragsgrenze korrigieren; alten/neuen Vertrag beschreiben; narrow-Metadaten getrennt von Orientierungen führen und alle internen Verbraucher migrieren; Namespaces/Remaps, Cloudfelder/Frames, Result-/Fehler-/Cancel-Verhalten prüfen |
| Priorität | P1; Kopplung an geplante öffentliche API vor Release klären |
| Abhängigkeiten | AP03/AP04 für reproduzierbare Ausführung; AP06 pro Vertragsänderung; AP09 bei distributionsverschiedenen Action-/Python-APIs |
| Abschlusskriterien | Normierte semantisch sinnvolle Orientierungen; erhaltenes Engstellenverhalten; konsistente interne Namen und Namespace-Test; Cloud-Varianten und Frames geprüft; Action-Erfolg/Fehler/Cancel entsprechend dokumentiertem Zielvertrag; keine stille API-Änderung |
| Aktueller Status | IN PROGRESS insgesamt: M01, Cloud-, Action-, Namespace-, RViz-/TF-Eingangs- und QoS-Korrekturen VERIFIED; M02 auf Nutzerwunsch nur Vorschlag, keine Überwachung implementiert |

### 4.7 AP06 - Tests und Qualitätssicherung

| Feld | Planung |
| --- | --- |
| Ausgangsstand | 20 funktionale Fälle, sechs Linter-Templates, strikte Config-/Posevalidierung; historische Ausführung berichtet |
| Probleme | B14: unvollständige Regressionen, skip/Legacy-Lint, Namenskonflikte bei gemeinsamer Pytest-Sammlung; keine neue Baseline-Laufzeitprüfung |
| Geplante Änderung | Bestehende Suite erhalten; gezielte Regressionen für jede V4-Änderung; alten Copy-Install-Ablehnungstest transparent migrieren; Importsammlung und sinnvolle Lints korrigieren; Algorithmusfixtures ergänzen, soweit für Regression nötig |
| Priorität | P1; Voraussetzung für Nachweis jedes technischen Schritts |
| Abhängigkeiten | Begleitet AP02-AP05; vollständige ROS-Läufe nach AP03; Copyright-Lizenzprüfung hängt von AP01 ab; keine Bewegung/hardwareabhängige Prüfung automatisch ausführen |
| Abschlusskriterien | Dokumentierte Auswahl und Abdeckung; neue Regressionen und Bestandsfälle erfolgreich; colcon test und test-result mit ausgewiesenen Skips; bekannte Restfehler nicht verstecken; keine historischen Ergebnisse als V4-Nachweis übernehmen |
| Aktueller Status | VERIFIED für implementierten Humble-Umfang: finale225PASS/0FAIL/0ERROR/0SKIP,169SourcefreieFälle; keine Coverage-/Hardware-/M02-/vollständige Neuere-ROS-Abnahme |

### 4.8 AP07 - CI/CD

| Feld | Planung |
| --- | --- |
| Ausgangsstand | Manuelle Build-/Testanleitungen, keine Pipeline |
| Probleme | B15: kein unabhängiger reproduzierbarer Build-/Install-/Testnachweis |
| Geplante Änderung | Zunächst Ubuntu 22.04/Humble: rosdep, Copy-Build, Tests, test-result, Lints und installierte Ressourcen prüfen; Code/Workflow ohne unbewiesene weitere Distro-Matrix vorbereiten |
| Priorität | P1 |
| Abhängigkeiten | AP03/AP04 und tragfähige AP06-Tests; Lizenzprüfung als offenes Release-Gate sichtbar halten |
| Abschlusskriterien | Workflow geprüft; tatsächlicher CI-Lauf samt Commit und Ergebnis nachweisbar; Konfigurationsdatei allein ist kein ausgeführter CI-Nachweis; Fernlauf nicht durch ungefragten Push erzwingen |
| Aktueller Status | **IN PROGRESS** — Workflow/Skripte IMPLEMENTED, lokaler exakter Dockerlauf225+169PASS VERIFIED; NOT REMOTELY VERIFIED, tatsächlicher GitHub-Lauf nach autorisiertem späterem Push offen |

### 4.9 AP08 - Dokumentation und Wartung

| Feld | Planung |
| --- | --- |
| Ausgangsstand | Umfangreiche Bestandsdokumentation; historische PDF unverändert; dieses Protokoll wird initial angelegt |
| Probleme | Veraltete Installations-/Interfaceaussagen, keine festgelegte Versionierungs-/API-/Supportpolitik; Forschungsbeitrag muss vom Vorbestand getrennt bleiben |
| Geplante Änderung | Dieses Dokument kontinuierlich führen; bestehende Installation/Usage/Config bei Änderungen aktualisieren; passende Wartungszusagen im bestehenden Dokumentationsbestand festhalten; erforderliche Release-Metadaten separat, keine zusätzlichen Forschungsberichte |
| Priorität | P1 für korrekte Nutzung; P2/P3 für weitergehende Policies |
| Abhängigkeiten | Begleitet alle APs; Lizenztext nur nach AP01; konkrete Support-/API-Zusagen erst anhand AP06/AP09 |
| Abschlusskriterien | Nachvollziehbare Änderungs-IDs und Commitreferenzen, zutreffende Prüfberichte, reproduzierbare aktualisierte Nutzeranleitungen; dokumentierte Grenzen statt pauschaler Quality-Level-/ABI-Garantie |
| Aktueller Status | VERIFIED für aktualisierte Nutzer-/Wartungsdokumentation, drei installierte Forthcoming-Changelogs und zentrale Nachweise; keine garantierte API/ABI-/Supportzusage |

### 4.10 AP09 - ROS-Distributionskompatibilität

| Feld | Planung |
| --- | --- |
| Ausgangsstand | Humble/Jammy/Python 3.10 als Ziel, generische rclpy-/Launch-/TF-Verwendung; keine belegte Jazzy-/Neuer-Matrix |
| Probleme | B15: tatsächliche saubere Humble-Ausführung nicht neu belegt; Abhängigkeiten und Action-/PointCloud2-APIs können distributionsabhängig sein |
| Geplante Änderung | Zuerst Humble reproduzieren; weitere Ziele ausdrücklich auswählen und getrennt testen; nur nachgewiesene Inkompatibilitäten korrigieren; keine vorsorgliche Portierung |
| Priorität | P1 für Humble; P2 für weitere freigegebene Ziele |
| Abhängigkeiten | AP03-AP06; CI kann später geeignete Matrixnachweise liefern |
| Abschlusskriterien | Zielbezogene Dependency-/Build-/Test-/Installnachweise mit OS/Python/ROS-Versionen; weitere Distributionen erst nach Ausführung als unterstützt bezeichnen |
| Aktueller Status | VERIFIED für den bisherigen Humble/Jammy/Python3.10-Umfang; neue M02-Abnahme folgt. Verbindlich einziges Releaseziel. Neuere Distributionen ausdrücklich verschoben, kein Humble-Releaseblocker (V4-030) |

### 4.11 AP10 - ROS Index und Releasevorbereitung

| Feld | Planung |
| --- | --- |
| Ausgangsstand | Source-Pakete und historische Git-Referenzen vorhanden; Index-/Bloom-Kriterien initial getrennt recherchiert; kein hier erzeugtes Release |
| Probleme | B01-B08/B16: ungelöste Rechte/Metadaten/Dependencies/Installation; Releaseversion, Changelogs, Zielbranch, Namenskollisionen und organisatorische Zuständigkeiten offen |
| Geplante Änderung | Readiness zielbezogen aktualisieren; zunächst Source-Registrierung und Binärrelease getrennt vorbereiten; notwendige Paket-Changelogs/Release-Metadaten erst bei passendem Stand; keine PRs/Pushes/Releases ohne neuen Auftrag |
| Priorität | P0 für offene Release-Gates; Umsetzung nach technischen Grundlagen |
| Abhängigkeiten | AP01-AP04 zwingend für belastbaren Abschluss; AP05/AP06 für vorgesehenen Produktvertrag; AP08/AP09 für Ziel-/Wartungszusagen; AP07 als Projektqualitätsnachweis |
| Abschlusskriterien | Geprüfte Checkliste, konsistente Version/Ref, vollständige Dependencies, funktionierender Copy-Install, geklärte Rechte; Veröffentlichung nur nach gesonderter Autorisierung und externer Bestätigung |
| Aktueller Status | IN PROGRESS – aktuelle Checkliste VERIFIED; Index/Bloom/Buildfarm NOT READY wegen konkret dokumentierter Rechte-/Publikations-/Versions-/Organisations- und externer Abnahmegates |

### 4.12 Aktuelle Reihenfolge und Entscheidungsgrenzen

Die freigegebenen technischen AP05–AP10-Phasen wurden nach der konkreten M01-Freigabe fortgesetzt. M02 bleibt auf Nutzerwunsch unimplementiert; Vorschlag und Testplan stehen in18.2. Alle davon unabhängigen Arbeiten sind ausgeführt oder mit ihrem konkreten externen Blocker abgegrenzt. Offene Vertrags-, Karten- und konkrete Distributionsrechte sperren die Veröffentlichung, nicht die technische Forschung. Die bereits autorisierte Apache-Wahl wird nicht erneut aufgerollt.

Humble ist der vollständig geprüfte technische Zielumfang. Remote-CI bleibt ohne Pushfreigabe offen, neuere Zielplattformen haben die in18.8 belegten Grenzen. Die nächste verhaltensändernde Entscheidung betrifft M02, daneben die Ziel-/Dependency-/Actionstrategie einer neueren ROS-Distribution und die spätere Releaseorganisation. Kein Push, Release oder Hardwaretest wird aus dieser Reihenfolge abgeleitet.

## 5. Entwicklungsprotokoll

### 5.1 Verbindlicher Arbeitsablauf für Folgeänderungen

Vor jeder Implementierung werden Branch V4, Working Tree und bestehendes Protokoll geprüft. Anschließend wird hier eine neue fortlaufende ID mit Ausgangszustand und Ziel angelegt, bevor die betroffenen Implementierungsdateien geändert werden. Es folgen minimale Umsetzung, passende Tests, Aktualisierung desselben Eintrags, Versionsvergleich und AP-Status. Unabhängige Änderungen erhalten getrennte Commits; Quelländerung und zugehöriges Protokoll werden gemeinsam committed. Bestehende uncommittete Arbeit wird nicht überschrieben, gestasht oder ungefragt aufgenommen.

Jeder Eintrag verwendet die Felder Datum, Arbeitspaket, betroffene Dateien, Git-Commit und Status sowie die Unterabschnitte Ausgangssituation, Ziel der Änderung, Technische Umsetzung, Begründung, Verifikation, Ergebnis und Auswirkungen. IDs werden nicht wiederverwendet; verworfene Pläne bleiben mit Erklärung erhalten. Eine selbstreferenzielle Commit-SHA wird nicht durch Amend erzwungen: stabiler Commit-Subject plus Git-Historie oder SHA im nächsten regulären Update sind zulässig.

### V4-001 - Entwicklungsbranch und zentrale Baseline-/Planungsdokumentation initialisieren

**Datum:** 13. Oktober 2026 (Europe/Berlin)
**Arbeitspaket:** AP08; initiale Anforderungsaufnahme AP10, keine technische Implementierung
**Betroffene Dateien:** ausschließlich `docs/V4_ROS_COMPLIANCE_DEVELOPMENT.md`; zusätzlich neue Git-Referenz `refs/heads/V4`
**Git-Commit:** stabiler Subject `docs(v4): initialize ROS compliance development protocol`; SHA nach Erstellung über `git log V4 --format='%H %s' -- docs/V4_ROS_COMPLIANCE_DEVELOPMENT.md` bestimmbar; keine Einfügung der eigenen SHA durch Amend
**Status:** **VERIFIED** hinsichtlich der unten abgegrenzten Initialisierungsabnahme; kein Nachweis technischer AP-Abnahme

#### Ausgangssituation

main stand exakt auf der vereinbarten historischen Baseline. V4, Tags und ein zentrales V4-Protokoll fehlten. Das historische PDF lag als einzige unversionierte Datei vor. Die funktionale Implementierung, V3-Konfiguration, Launches und Tests waren bereits vorhanden. Veröffentlichungshindernisse waren historisch beschrieben, aber nicht systematisch als V4-Arbeitspakete mit Abnahmekriterien geführt.

#### Ziel der Änderung

Eine geschützte, eindeutig zuordenbare Entwicklungslinie und ein einzelnes wissenschaftliches Protokoll herstellen. Vorbestand, V4-Planung, offene Entscheidungen und neue Nachweise werden getrennt. Sämtliche Implementierungsphasen bleiben bis zur angeforderten Planfreigabe unbegonnen.

#### Technische Umsetzung

Baselineobjekt, main-Abstammung, Branch-/Tagbestand und Index/Working Tree wurden geprüft. Die Unbedenklichkeit des identischen Checkout-Trees mit dem bestehenden PDF wurde bestätigt. Anschließend wurde `git switch -c V4 c65642fe56015556f696364a724cb5b976a27888` erfolgreich ausgeführt.

Der historische Bericht wurde vollständig textuell gelesen; seine geprüfte vorhandene Fassung wird per SHA-256 identifiziert. Die aktuelle Paketstruktur, Metadaten, Imports, Konfigurationspfade, relevante ROS-Verträge, Tests und Dokumentation wurden gelesen. Alle 26 Python-Dateien wurden statisch mit `ast.parse`, beide Manifeste mit `xml.etree.ElementTree.parse` gelesen. Ein paketweises AST-Importinventar wurde mit den Manifesten verglichen. Es wurden keine ROS-Nodes gestartet oder Projektmodule importiert.

Dieses Dokument initialisiert alle zehn geforderten Abschnitte, AP01-AP10, Befunde B01-B16, offene Entscheidungen, eine Nachweistabelle und den main→V4-Vergleich. Aktuelle offizielle ROS-/rosdistro-Kriterien wurden als Quellen verlinkt. Die Nutzerentscheidung zur vorläufigen Rückstellung der Lizenzierung ist in Planung, Blockerstatus und Reihenfolge berücksichtigt. Technische Dateien, öffentliche Bestandsanleitungen und historisches PDF bleiben unverändert.

#### Begründung

Die eindeutig geschützte Referenz und die Trennung von Beobachtung, Planung und Ausführung ermöglichen eine spätere wissenschaftliche Bewertung. Nachweise für bestehende Funktionen werden nicht als neue V4-Leistung ausgegeben. Die Einordnung der Veröffentlichungskriterien verhindert, dass optionale Tools oder Policydateien zu vermeintlichen Pflichtanforderungen werden.

#### Verifikation

Die Abnahmekriterien dieses Eintrags sind: V4 basiert unmittelbar auf dem vereinbarten Commit; bestehende Referenzen und alle 59 versionierten Dateien bleiben unverändert; die PDF-Prüfsumme bleibt gleich; ausschließlich das zentrale V4-Dokument kommt hinzu; alle zehn Hauptabschnitte/APs und die einheitliche Eintragsstruktur sind vorhanden; Tabellen und lokale Dokumentlinks sind konsistent; keine technische Testausführung wird erfunden. Das vor dem Commit prüfbare Commit-Gate fordert zusätzlich: aktiver Branch V4, vorgesehener Parent gleich Baseline und ausschließlich dieses Dokument im Index. Der erzeugte Commit ist anschließend nochmals auf diese Merkmale zu kontrollieren.

Ausgeführt:

```bash
git status --short --untracked-files=all
git branch --show-current
git rev-parse HEAD
git branch -avv
git tag --list
git cat-file -t c65642fe56015556f696364a724cb5b976a27888
git merge-base --is-ancestor c65642fe56015556f696364a724cb5b976a27888 main
git switch -c V4 c65642fe56015556f696364a724cb5b976a27888
git diff --exit-code
git diff --cached --exit-code
/usr/bin/python3 --version
/usr/bin/rosdep --version
```

Die statische Prüfung lässt sich im Repository-Root ohne Modulimporte und ohne Bytecode-Erzeugung wiederholen:

```bash
/usr/bin/python3 -B - <<'PYTHON'
import ast
import re
import xml.etree.ElementTree as ET
from pathlib import Path

root = Path('.')
files = list(root.glob('r3d_*/**/*.py'))
for path in files:
    ast.parse(path.read_text(), filename=str(path))
for package in ('r3d_planner', 'r3d_preprocessor'):
    manifest = ET.parse(root / package / 'package.xml').getroot()
    name = manifest.findtext('name')
    assert len(name) >= 2
    assert re.fullmatch('[a-z][a-z0-9_]*', name) and '__' not in name
    imports = set()
    for path in (root / package / package).glob('*.py'):
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split('.')[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and not node.level and node.module:
                imports.add(node.module.split('.')[0])
    print(package, sorted(imports))
print('Parsed Python files:', len(files))
PYTHON
```

Zusätzlich wurden ein temporärer Prüfsummenvergleich aller ursprünglichen versionierten Dateien und des PDFs sowie eine externe, nur temporär gespeicherte Dokumentstruktur-/Linkprüfung ausgeführt. Die statische Python-/XML-Prüfung war erfolgreich: 26 Python-Dateien, zwei XML-Manifeste; beide Namen erfüllen die obligatorischen lexikalischen REP-144-Regeln. Die Prüfung verwendet `python -B`/AST und erzeugt keine Projekt-Bytecode-Dateien. Das Protokoll enthält keine Behauptung eines neu bestandenen rosdep-, Build-, Test-, Lint- oder Hardwarelaufs. Die konkrete Nachweistabelle steht in Abschnitt 6.

Dokumentinhalt, lokale Linkziele und Tabellen wurden vor Veröffentlichung geprüft. Nach gezieltem Staging wird unmittelbar vor dem Commit nochmals `git diff --cached --check` mit Index-/Branch-/Parent-Gate ausgeführt. Dieser Eintrag dokumentiert den geprüften Initialisierungsinhalt, nicht eine bereits ausgeführte externe Veröffentlichung. Nach Erstellung ist der fokussierte Commit nochmals auf Parent, Subject und Dateiumfang zu kontrollieren; seine Daten bleiben über die stabile Subject-Referenz nachvollziehbar. T06 bezieht sich ausschließlich auf das vor Commit tatsächlich geprüfte Gate.

#### Ergebnis

Branch und initiales Forschungsprotokoll sind hergestellt. Baseline, bestehende Fähigkeiten, Veröffentlichungskategorien, Prioritäten, Abhängigkeiten und überprüfbare Abschlusskriterien sind festgehalten. Alle technischen Arbeitspakete stehen noch vor Umsetzung; AP01 ist ausdrücklich zurückgestellt. Die Planfreigabe für den ersten Code-/Metadatenschritt steht aus.

#### Auswirkungen

Keine Änderung an Algorithmen, ROS-Topics/Actions/Services, Konfigurationsschema, Dependencies, Installation oder bestehenden Tests. Ein neuer lokaler Branch und eine neue versionierte Dokumentdatei entstehen. Bestehende Branches bleiben unverändert. Das historische PDF bleibt lokal unverändert und unversioniert; ein sauberer späterer Clone enthält es dadurch noch nicht. Keine Pushes, Releases, Pull Requests, Systeminstallationen oder weiteren Entwicklungsberichte.

Nachtrag zur bereits abgeschlossenen Initialisierung V4-001: Commit `d355db9bbb284024fad0d1295ba768cd0001a5ee`, Subject `docs(v4): initialize ROS compliance development protocol`, Parent ist der Baseline-Commit. Dieser SHA-Nachtrag erfolgt im nächsten regulären Dokumentationsupdate, ohne Amend oder Änderung der historischen Aussage.

### V4-002 - Lizenzrecherche integrieren und private V4-Entwicklung untersuchen

**Datum:** 13. Oktober 2026 (Europe/Berlin)

**Arbeitspaket:** AP01 (Recherche), AP08 und AP10; AP03 bleibt NOT STARTED

**Betroffene Dateien:** ausschließlich `docs/V4_ROS_COMPLIANCE_DEVELOPMENT.md`

**Git-Commit:** gemeinsamer stabiler Subject `docs(license): document license evaluation and copyright attribution`. Der zuerst geplante Subject `docs(license): document open-source license evaluation` wurde vor dem ersten Commit auf den erweiterten Nutzerauftrag angepasst; kein bestehender Commit wird geändert oder dupliziert.

**Status:** **VERIFIED** für Recherche-/Dokumentationsabnahme; keine rechtliche Gesamtfreigabe

#### Ausgangssituation

AP01 war durch V4-001 zurückgestellt. Das zugängliche siebenseitige Recherche-PDF und frühere Befunde lagen vor. Eingang-HEAD war weiterhin d355db9…; keine zusätzlichen V4-Commits, kein V4-Upstream und nur das bekannte unversionierte historische PDF. Die Datei war vor diesem Auftrag nicht verändert. Der V4-002-Plan wurde vor der inhaltlichen Änderung in diesem Dokument erfasst.

#### Ziel der Änderung

Vier permissive Kandidaten anhand Primärquellen wissenschaftlich vergleichen, pauschale Aussagen korrigieren, direkte Dependency-Hauptlizenzen/Binärgrenzen prüfen und private GitHub-Entwicklung ohne voreilige Veröffentlichung vorbereiten. Empfehlung, Rechteklärung, Entscheidung und Lizenzanwendung sind getrennt.

#### Technische Umsetzung

Das vollständige Recherche-PDF wurde gelesen; die unveränderte historische Referenz wurde berücksichtigt. Apache-2.0, MIT, BSD-2-Clause und BSD-3-Clause wurden anhand Originaltexte, SPDX, ROS-/rosdistro-/REP-149-Quellen und UrhG/BGB ausgewertet. Die qualitative Entscheidungsmatrix benennt Ausschlusskriterien und Präferenzordnung. K01-K12 in Kapitel 11 berichtigen konkrete Aussagen des Recherche-PDFs. AST-Importinventar, lokale installierte Metadaten und upstream License-/Paketdateien liefern den begrenzten Dependency-Abgleich. Das NumPy-Wheel mit GCC-/LGPL-Zusatzhinweisen ist getrennt erfasst.

Die GitHub-Prüfung bestätigt public für R3D-Planner, vier Serverbranches ohne V4 und fehlendes V4-Tracking. Für R3D-Planner-Development ergab ein Get-Repo 404 ohne sichere Unterscheidung von Nichtexistenz und fehlendem Zugriff. Optionen A/B und ein nicht ausgeführter Pushschutz-/Private-Remote-Vorschlag stehen in Abschnitt 12. Der ergänzte Auftrag erweitert denselben Analysebestand unter V4-003; das gemeinsame Lizenzkapitel enthält 22 Unterkapitel statt einer redundanten zweiten Analyse.

#### Begründung

Primärquellen und explizite Nachweisgrade verhindern unbelegte Lizenz-/Patent-/Haftungs-/Kompatibilitätsfreigaben. Die private Entwicklungsplanung verändert keine GitHub-Sichtbarkeit und hält die öffentliche Baseline frei von V4-Commits.

#### Verifikation

T19-T21/T24-T26 erfassen die tatsächlichen Analyse-/Dokumentprüfungen. Ausgeführt wurden die beauftragten Git-Lesebefehle, AST-/XML-/Metadaten-/Headerlektüre, Source-/SPDX-/Quellenvergleich und lesende GitHub-API-Abfragen. Alle benannten Lizenz-/Gesetzestexte wurden gelesen. Einzelne Webabrufe amtlicher Normen scheiterten mit Timeouts; die Originaltexte wurden danach erfolgreich per lesendem HTTPS-Abruf temporär bezogen. Ein erster HTML-Hilfsversuch scheiterte an fehlendem bs4 und anschließend an der angenommenen UTF-8-Kodierung; der Standardbibliotheksparser mit tatsächlicher ISO-8859-1-Kodierung konnte die Gesetzesabsätze lesen. Keine Parserabhängigkeit wurde installiert.

Quellen-/Tabellen-/ID-/Strukturprüfung und Diffreview prüfen die 22 Unterkapitel, vier Kandidaten, Quellenstatus, Entwickler-/Fremdrechte-Abgrenzung, offene Gate-Entscheidungen und das einzige zentrale Forschungsdokument. Prüfsummenvergleich schützt alle 59 übrigen versionierten Dateien sowie beide PDFs; Ref-/Configvergleich schützt bestehende Branches, Remotes und Tracking. Keine ROS-/colcon-/rosdep-/Lintausführung wird als neues Ergebnis behauptet. Das Commit-Gate erlaubt ausschließlich diese Dokumentdatei und den geprüften Eingang-HEAD als Parent; die anschließende Commitidentität bleibt über den stabilen Subject nachvollziehbar.

#### Ergebnis

Lizenzvergleich, begründete unverbindliche Apache-Präferenz, dokumentierte Korrekturen und private Entwicklungsoption sind nachvollziehbar integriert. AP01 bleibt insgesamt BLOCKED; keine verbindliche Lizenzentscheidung. Die neuen LiDAR-/Copyrightdetails werden durch V4-003 ergänzt.

#### Auswirkungen

Nur Forschungstext: keine LICENSE, keine Lizenz-/Copyright-/SPDX-Headeranwendung, keine Code-/Dependency-/Kartendatenänderung, keine Systeminstallation. Keine Änderung von R3D-Remotes/-Sichtbarkeit, keine neue GitHub-Repositoryerstellung, kein Push, keine Veröffentlichung. Alle Befehle für einen späteren privaten Workflow bleiben ausdrücklich nicht ausgeführte Vorlagen.

### V4-003 - Copyright-Erklärung und externe LiDAR-Provenienz ergänzen

**Datum:** 13. Oktober 2026 (Europe/Berlin)

**Arbeitspaket:** AP01 (Analyse), AP08 und AP10; keine Lizenzimplementierung

**Betroffene Dateien:** ausschließlich `docs/V4_ROS_COMPLIANCE_DEVELOPMENT.md`

**Git-Commit:** gemeinsamer stabiler Subject `docs(license): document license evaluation and copyright attribution`; V4-002 war bei Auftragserweiterung noch nicht committed

**Status:** **VERIFIED** für abgegrenzte Quellen-/Diff-/Dokumentationsprüfung; Rechts-/Deployment-/Binärfreigaben nicht verifiziert

#### Ausgangssituation

Während V4-002 beauftragte der Nutzer ausdrücklich die Fortsetzung einschließlich Alleinentwicklererklärung und der beiden externen LiDAR-Repositories. Im R3D-Working Tree bestand nur der eigene 40-zeilige V4-002-Plan plus unverändertes historisches PDF. Der Plan war unvollständig und nicht committed; keine fremde/unbekannte Änderung wurde überschrieben. V4-003 wurde als nächste freie ID vor der Erweiterung hier angelegt.

#### Ziel der Änderung

Die Selbstauskunft Bastian Aumers korrekt wiedergeben, alle Python-/relevanten Projektdateien inventarisieren, die tatsächliche externe Git-Ableitung und Lizenzvarianten prüfen und eine nachweisgebundene Modification Notice vorbereiten. Originalbedingungen bleiben separat erhalten, unbelegte Felder NOT VERIFIED.

#### Technische Umsetzung

Kapitel 11 enthält nun genau einen Lizenz-/Copyright-Hauptabschnitt mit 22 Unterkapiteln. Die Erklärung wird als dokumentierte Selbstauskunft und nicht als unabhängige Rechtsabnahme gekennzeichnet. Das Inventar erfasst alle 60 eingangs versionierten Pfade, darunter 26 Python-Dateien, 18 vorhandene Namensheader, sechs unveränderte OSRF-Testtemplates und neun Bytecode-Artefakte; PCD-Herkunft/-SHA und Lizenzgrenzen sind separat erfasst.

Die externen Repositories wurden nur über API und temporäre Bare-Caches ohne Checkout/Build analysiert. Merge-Base und Parent belegen 2f875385… als Ausgangspunkt der lidar-odometry-Linie; drei Parent-Diffs bis 69c0e093… liefern die Änderungsübersicht. Root-LICENSE-Blob und NDT-Gitlink 497411279… sind unverändert. Der spezifische Rootgrant ist BSD-2-Clause mit Ryohei Sasaki; NDT-Roottext nennt k.koide/BSD-2-Clause, konkrete PCL-Header enthalten zusätzlich BSD-3-Clause. CMake kompiliert Submodulsource statisch. Weitere System-/Binär-/Deploymentgrenzen sind benannt, statt Hauptlizenzen pauschal gleichzusetzen.

Die vorbereitete Modification Notice bleibt ausschließlich Text in diesem Protokoll. Sie enthält analysierte Original-/Modified-Revision, Originalcopyright, durch Diffs belegte Änderungen, Entwicklerattribution mit Evidenzgrad und NOT VERIFIED für fehlende Deployment-/Vollständigkeitsnachweise. Keine externe Datei wurde verändert. Die drei Implementierungscommits vom 16.09.2026 werden ausdrücklich als Vorbestand, nicht als neue V4-Implementierung erfasst.

#### Begründung

Persönliche Attribution des eigenen R3D-Codes, fremde Testtemplates, abgeleitete LiDAR-Source und statisch eingebundene Fremdsource haben unterschiedliche Rechte-/Distributionsgrenzen. Die belegte ROS-Node-Kommunikation rechtfertigt keine pauschale Neulizenzierung des externen Bestands. Vertrags-/Arbeitgeber-/Kartenrechte bleiben trotz Entwicklererklärung offen.

#### Verifikation

T20-T26: Header-/Templatevergleich, exaktes Dateiinventar, 26 Python-/zwei XML-Dateien gelesen, sämtliche drei externen Parent-Diffs und aktueller Sourcevertrag ausgewertet. 286 netto geänderte externe Pfade und Treeumfang 279→16 anhand Git bestätigt; sieben vorhandene GTest-Blöcke gezählt, nicht ausgeführt. Gepinnte NDT-LICENSE und benutzte Header-/Translation-Unit-Quellen gelesen. LICENSE-Blobidentität und Gitlinkidentität sind technisch verifiziert; tatsächlicher Roboterstand, vollständige ursprüngliche Rechteinhaberliste und Binärdistribution bleiben ausdrücklich nicht verifiziert.

Vor Commit werden V4, Dokumentstruktur, erhaltene V4-001-Historie, Quellen-/Matrix-/Inventarvollständigkeit, unveränderte Lizenzfelder/Quellcode/Daten und unveränderte R3D-Konfiguration/Refs nochmals geprüft. Ausschließlich das zentrale Dokument wird gezielt gestaged; `git diff --cached --check` und Dateiumfang bilden das Commit-Gate. Keine Behauptung eines bereits vor Erzeugung ausgeführten eigenen Commitchecks; die erzeugte SHA und der endgültige Commitumfang werden nach Erstellung separat geprüft und sind in Git über den Subject belegt.

#### Ergebnis

Der beauftragte Recherche-/Attributions-/Provenienzbestand ist dokumentiert und für den benannten Umfang verifiziert. Apache-2.0 bleibt bevorzugter Kandidat der eigenen R3D-Komponenten, externe BSD-Bedingungen bleiben getrennt. AP01 BLOCKED, AP08/AP10 IN PROGRESS; Lizenzanwendung und AP02/AP03 nicht begonnen.

#### Auswirkungen

Keine technische Implementierungs-/Lizenzänderung, keine neuen Forschungsberichte, keine neue PDF. Externe Git-Caches sind temporäre Lesekopien, keine Änderungen an Originalrepositorys. Historische R3D-Branches, PDFs, PCDs und Remotes bleiben unverändert. Kein Push, keine Sichtbarkeitsänderung, keine Veröffentlichung. Die weitere Arbeit wartet auf den nächsten Nutzerauftrag.

### V4-004 - Apache-2.0 auswählen und für eigene R3D-Software implementieren

**Datum:** 13. Oktober 2026 (Europe/Berlin)

**Arbeitspaket:** AP01; begleitend AP08/AP10, keine AP02-/AP03-Implementierung

**Betroffene Dateien:** neue `LICENSE`, beide `package.xml`, 18 zugeordnete eigene Python-Dateien einschließlich beider `setup.py` und vier Launchdateien; ausschließlich `docs/V4_ROS_COMPLIANCE_DEVELOPMENT.md` als Forschungsdokumentation. Genau 22 Commitpfade: 21 vorhandene Dateien plus LICENSE. Vollständige Headerpfade in 11.21.2.

**Git-Commit:** stabiler Subject `chore(license): adopt Apache-2.0 for R3D packages`; Parent 9f11996f6d6d5fda5f38ffb5866fb6d736983668. Eigene SHA nach Erstellung per Git bestimmbar; kein Amend zur selbstreferenziellen SHA-Einfügung. Vorgänger V4-002/V4-003: gemeinsamer Commit 9f11996f6d6d5fda5f38ffb5866fb6d736983668.

**Status:** **VERIFIED** für beauftragte Dateiumsetzung und statische Unverändertheitsprüfung; Entscheidung/Implementierung COMPLETED, vollständige rechtliche Releasefreigabe nicht verifiziert

#### Ausgangssituation

V4 stand auf 9f11996f6d6d5fda5f38ffb5866fb6d736983668 und stammt nach Git-Ancestryprüfung von c65642fe56015556f696364a724cb5b976a27888 ab. V4-001 bis V4-003 und das bestehende 22-teilige Lizenzkapitel wurden berücksichtigt, keine zusätzliche Vollrecherche begonnen. Versionierte Dateien und Index waren sauber; ausschließlich das bekannte historische PDF war unversioniert. Keine fremde/unbekannte Änderung wurde überschrieben. V4-004 wurde vor der Implementierung als IN-PROGRESS-Plan in diesem Protokoll angelegt.

#### Ziel der Änderung

Die ausdrückliche Apache-2.0-Entscheidung für autorisierte eigene Software in eine vollständige offizielle Root-LICENSE, konsistente ROS-Lizenzfelder und persönliche SPDX-Attribution umsetzen. Vorhandene Fremdnotices, Karten und unbekannte Zuordnung bleiben getrennt; die vollständige Rechts-/Releasefreigabe wird nicht erfunden.

#### Technische Umsetzung

Der offizielle ASF-TXT-Download wurde unverändert als LICENSE übernommen: 11358 Byte, 202 physische Textzeilen, SHA-256 `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`. Ein erster Abruf in der eingeschränkten Netzwerkumgebung scheiterte an DNS; der gezielt freigegebene HTTPS-Abruf war erfolgreich. Keine Installation/Dependencyänderung. Alle neun Lizenzabschnitte und der vollständige Appendix einschließlich unveränderter Platzhalter sind enthalten; keine eigenen Bedingungen oder projektspezifischen Zusätze im Originaltext.

18 bereits mit eigenem Namensheader versehene Python-Dateien erhalten exakt die zwei zusätzlichen Kommentarzeilen `SPDX-FileCopyrightText: 2026 Bastian Aumer` und `SPDX-License-Identifier: Apache-2.0`. Bestehende `Copyright (c) Bastian Aumer`-Zeilen bleiben erhalten. Beide package.xml ersetzen ausschließlich den TODO-Lizenztext durch Apache-2.0. Beide setup.py hatten bereits diesen Lizenzwert; dort ändern sich nur Kommentare. Keine Version, Dependency, Entry-Point, Buildtyp, Import, Implementierungslogik oder Installationsregel wurde geändert.

Das bestehende Kapitel dokumentiert die verbindliche Entscheidung und Matrixbegründung, den abgegrenzten Geltungsbereich, aktuellen Inventar-Delta und Lizenz-/Release-Teilstände. Die vorhandene LiDAR-Notice wurde innerhalb desselben Kapitels dokumentarisch abgeschlossen; das separate externe Repository wurde nicht geändert und keine fremde Source kopiert. Verifizierte historische LiDAR-Diffs bleiben Vorbestand. Eine konditionale Pflichttextübersicht für spätere Binärdistribution ist ergänzt; kein konkretes Releaseartefakt wurde erzeugt oder freigegeben.

#### Begründung

Die vorhandene qualitative Matrix bevorzugt unter den offengelegten Projektpräferenzen die permissive Weiterverwendung einschließlich kommerzieller Nutzung, ausdrückliche begrenzte Patentlizenz, nachvollziehbare Hinweispflichten und ROS-Eignung. Der Entwickler hat diese Wahl nun verbindlich getroffen. Die eigenen Erklärungen ersetzen keine unabhängige Prüfung arbeits-/dienstvertraglicher Befugnisse; kein Patentfreiheitsnachweis und kein Gesamtgrant für fremde Source oder Karten.

#### Verifikation

T28-T35 dokumentieren tatsächlich ausgeführte statische Prüfungen mit System-Python 3.10.12 und `-B`: offizieller Lizenz-Byte-/Hashvergleich, AST- und semantischer Tokenvergleich aller 26 Python-Dateien, exakte Kommentar-/XML-Whitelist, XML- und Setup-AST-Lizenzabgleich, unveränderte Versionen/Dependencies/Entry-Points/Buildtypen. Alle 39 übrigen eingangs versionierten Dateien, sechs Fremdtemplates, beide PCDs, neun Bytecode-Dateien und beide PDFs sind per SHA-256 geschützt. Historische Branch-/Remote-/Tagreferenzen und .git/config bleiben unverändert; V4 ohne konfiguriertes Upstream-/Pushziel. Keine 26 neu ausgeführten Funktionstests behauptet: es sind 26 statisch verglichene Python-Dateien.

Dokumentstruktur, genau ein Lizenzkapitel mit 22 Unterkapiteln, vier fortlaufende V4-IDs, erhaltene historische Einträge, Quellen-/Inventar-/Statuskonsistenz sowie Git-Diff/Whitespace werden geprüft. Das Commit-Gate fordert ausschließlich die 22 freigegebenen Pfade im Index, den unveränderten Eingang-HEAD als Parent und `git diff --cached --check`. Nach Erzeugung werden SHA/Parent/Dateiumfang/Status separat geprüft, ohne vorab eine bereits vorhandene eigene Commit-SHA zu behaupten. Keine ROS-/colcon-/rosdep-/Hardware-/Build-/Install-/Linterausführung in diesem Arbeitsschritt.

#### Ergebnis

Apache-2.0 ist für die autorisierten eigenen Softwarebestandteile verbindlich ausgewählt und technisch implementiert; die konkreten Lizenzdateien und Unverändertheitskriterien sind statisch verifiziert. AP01-Lizenzentscheidung/Implementierung COMPLETED; AP01 insgesamt BLOCKED für offene Rechts-/Distributionsfragen. AP08/AP10 IN PROGRESS, AP02/AP03 NOT STARTED. Diese offenen Fragen werden nicht als Anlass für erneute Lizenzvergleichsarbeit ausgegeben.

#### Auswirkungen

Änderung ausschließlich an LICENSE, eigenen Kommentarheadern, zwei Lizenzfeldern und diesem Protokoll. Sechs OSRF-Templates und unbekannte Dateizuordnungen unverändert; keine Apache-Zuordnung der PCDs. Root-LICENSE ersetzt keine externen BSD-/MIT-/MPL-/sonstigen Bedingungen. Keine neuen Forschungsberichte, keine PDF-/historischen Dokumentänderungen, keine Änderungen externer LiDAR-Repositories oder anderer R3D-Branches, kein Remote-/Sichtbarkeitswechsel, kein Push und kein Release. Weitere APs warten auf den nächsten Auftrag.

### V4-005 - Mitgelieferte PCD-Karten aus aktivem V4-Tree entfernen

**Datum:** 14. Oktober 2026 (Europe/Berlin)
**Arbeitspaket:** AP01 Datenumfang; gezielte AP04-/AP06-/AP08-/AP10-Teilmaßnahmen
**Betroffene Dateien:** zwei maps-PCDs, planner_config.yaml, configuration.py, test_configuration.py; README.md, INSTALL.md, README_r3d_planner.txt, beide Paket-README.txt, docs/CONFIGURATION.md, ARCHITECTURE.md, KNOWN_ISSUES.md und dieses Protokoll (14 Pfade insgesamt)
**Git-Commit:** stabiler Subject `refactor(data): remove bundled PCD maps`; Parent 87e213889638ff92cbee85b76fdb95a916c71193. SHA nach Erzeugung separat kontrolliert.
**Status:** **VERIFIED** für aktiven Tree-/Konfigurations-/Regressionsumfang; keine historische Daten-/Rechtsfreigabe

#### Ausgangssituation

V4/HEAD entsprachen dem zuletzt gemeldeten Commit und stammen von c65642f… ab. Beide beauftragten Karten waren beim Eingang bereits uncommitted gelöscht; diese vorhandene Arbeit wurde ohne Wiederherstellung übernommen. Alle übrigen versionierten Dateien/Index waren unverändert, das bekannte historische PDF unversioniert. V4-005 wurde vor Änderungen als Plan im Protokoll angelegt. Existierende PCD-Algorithmen, Modeauswahl, Source-/Symlink-/R3D_CONFIG_DIR-Vertrag und synthetische Suite sind Vorbestand.

#### Ziel der Änderung

Nur die mitgelieferten konkreten Karten aus dem aktiven Tree nehmen, ihre aktiven Verweise entfernen und vom Nutzer bereitgestellte PCDs verlangen. Keine Beispielkarte nachladen, generieren oder ersetzen; keine Algorithmus-/ROS-Interfaceänderung. Minimaler Konfigurationsdelta, kein vollständiger AP04-Refactor.

#### Technische Umsetzung

Git-Löschungen: `r3d_preprocessor/maps/voxel_05_minhits_7.pcd` (19284059 Byte, SHA-256 1b36ce3ac8b0a57e9bea5cfeb5563db3478c3e1105d68d38a37a395322bab404) und `r3d_preprocessor/maps/voxel_05_minhits_7_analysed.pcd` (8905560 Byte, SHA-256 fff00cb9eb9fdaf96cb3c8bbf9c6ed2bd323a7b11e734dfea05ad52d9aadb22c). Diese Dateien waren in Git getrackt, aber bei Auftragseingang bereits nicht mehr auf Disk. Kein weiteres PCD im Repository identifiziert; historische Blobs bleiben unverändert.

Zentrale maps-Werte sind explizit leer. Die gewählte Mode verlangt einen konfigurierten vorhandenen regulären .pcd-Pfad und meldet Feld/aufgelösten Pfad; der unbenutzte maps-Wert darf leer oder zukünftiger Output sein. Modeauswahl bleibt preprocessor→pcd_path, planner/map/follower→map_name. Relative Pfade sind YAML-relativ, absolute Pfade und ~ bleiben unterstützt. Keine implizite Beispielkarte. R3D_CONFIG_DIR wird im Fehlertext und in aktiven Anleitungen als Nutzerverzeichnis mit YAML/Robotprofilen beschrieben, ohne notwendiges Source-Repository. Implizite Copy-Default-Ablehnung bleibt unverändert für späteren AP04-Schritt.

23 parametrische Fälle wurden im bestehenden Testmodul ergänzt: ungesetzte Defaults in vier Modes, fehlende/falsche Endung/Verzeichniseingaben in vier Modes, drei Pfadformen und leerer unbenutzter Wert in vier Modes. Alte Tests/Syntheticfixtures bleiben erhalten. Acht vorhandene Nutzeranleitungen/Datenübersichten wurden angepasst; historische Forschungsberichte/V3-Implementierungsbericht/PDF unverändert. Standalone-Node-Defaults sind allgemeine Dateinamen und nicht Verweise auf die gelöschten konkreten Karten; sie wurden nicht als neue ROS-Interfaceänderung ersetzt.

#### Begründung

Aktive Source-/Installartefakte benötigen keine ungeklärten mitgelieferten Karten mehr. Nutzer liefern Daten und deren Berechtigung selbst. Das ändert weder historische Gitverteilung noch Herkunftsrechte an alten Objekten. Analyse schreibt weiterhin neben eine Nutzereingabe, daher beschreibbarer Nutzerpfad erforderlich; getrennte Ausgabepolitik bleibt AP04.

#### Verifikation

System-Python 3.10.12, ROS 2 Humble/Ubuntu 22.04, pytest 6.2.5. 40 nicht-nodeausführende Fälle unter PYTHONNOUSERSITE=1 bestanden (0,36 s); drei bestehende ROS-/Launchfälle mit bereits vorhandenen User-Site Open3D 0.19/NetworkX 3.4.2/NumPy 1.26.4 bestanden (39,94 s), darunter vier echte Planner-Komponentenkombinationen und Analyzerlaunch. DDS isoliert mit ROS_LOCALHOST_ONLY=1, ROS_DOMAIN_ID=191, RMW_IMPLEMENTATION=rmw_fastrtps_cpp; kein Followerlaunch/Hardware-/Bewegungsbefehl. SciPy 1.8.0 warnt weiterhin zu NumPy 1.26.4; keine Dependencyänderung, kein sauberer rosdep-/Gesamtumgebungsnachweis.

Erster Unitlauf: 35 passed/5 failed; vier LaunchContext-Fälle scheiterten an nicht erlaubtem ~/.ros/log, behoben durch ROS_LOG_DIR im temporären Verzeichnis. Der neue Tilde-Test mockte eine von Path.expanduser gebundene Funktion und scheiterte; ein zweiter Versuch hatte noch einen Tilde-Fehler (39 passed/1 failed). Der finale Test verwendet eine echte Home-relative Referenz auf die temporäre Fixture ohne HOME-Änderung. Das Hilfsskript hatte vor Ausführung einen Syntaxfehler, wurde vor Projektänderungen korrigiert. Diese Fehler sind keine behaupteten Produktionsregressionen.

Copy-colcon-Build ohne Symlinks in temporären Paketkopien: 2 packages finished in 0,90 s; absichtlich deaktiviertes Bytecompiling erzeugt zwei Warnungen. Build-Python ohne User-Site enthält kein Open3D/NetworkX, Packaging funktioniert trotzdem; das beweist keine vollständige Runtime-Dependencyauflösung. Nach Umbenennen der temporären Source-Kopie importiert ein Probeprozess tatsächlich das installierte configuration.py und lädt eigene YAML/Robotprofile erfolgreich. Installbaum enthält 0 PCDs. AST/Hashes belegen unveränderte Analyse-/Planungsnodes, Launch-/Odometry-/ROS-Verträge, Manifeste/Setup/Original-LICENSE/18 Copyrightheader; nur Konfigurationspfadvalidierung und neue Tests sind semantisch geändert.

Befehle/Details T37-T41. Vor Commit: exakter 14-Pfad-Whitelist-/Git-Lösch-/Diff-/Dokument-/Ref-/PDFcheck, danach SHA/Parent/Dateiumfang/Status. Keine fremde Arbeit übernommen, keine zusätzlichen Forschungsdateien.

#### Ergebnis

Aktiver V4-Tree und getesteter Installbaum ohne Beispielkarten; Nutzerkonfiguration und bestehende PCD-Funktionen mit temporären Fixtures geprüft. 43 Fälle insgesamt bestanden (40+3 getrennte Ausführung). Keine neue Standardkarte. Karten-Tree-Mitdistribution beseitigt; historische Git-/Fork-/Kopienrechte nicht geklärt. Lizenzinstallation folgt als getrennte V4-006.

#### Auswirkungen

maps-Defaults müssen explizit gesetzt werden; unbenutzter Modepfad darf nun leer sein. ROS-Parameter-/Topic-/Actionnamen, Algorithmen, Versions-/Dependency-/Buildtypwerte unverändert. Zwei Kartenlöschungen in normalem Commit, keine History-Rewrites/Tags/anderen Branchänderungen/externen Repositoryänderungen/GitHubänderungen/Pushes. AP02/AP03 nicht begonnen.

### V4-006 - Lizenzverifikation und minimale Lizenzmitnahme abschließen

**Datum:** 14. Oktober 2026 (Europe/Berlin)
**Arbeitspaket:** AP01; minimale AP04-/AP06-/AP08-/AP10-Teilmaßnahmen
**Betroffene Dateien:** r3d_planner/LICENSE, r3d_preprocessor/LICENSE, beide setup.py, dieses zentrale Protokoll (fünf Pfade)
**Git-Commit:** stabiler Subject `chore(license): finalize licensing verification`; Parent/Kartencommit 3aee536078ce495749d8afdcaf0141dca5c5bfcb. Eigene SHA nach Erzeugung separat geprüft und per Subject auffindbar; kein Amend.
**Status:** **VERIFIED** für technische Lizenzprüfung und konkrete Lizenzmitnahme; rechtliche Gesamtfreigabe NOT VERIFIED/BLOCKED

#### Ausgangssituation

V4-005 committed: aktiver Tree ohne Beispiel-PCDs, Nutzerconfig und 43 Fälle geprüft, historische Datenobjekte unverändert. Versionierte Dateien/Index sauber; bekanntes PDF unversioniert. Root-LICENSE/18 eigene SPDX-Header/Apache-Manifeste und sechs Originaltemplates vorhanden. Die bisherigen setup.py nahmen nur package.xml in Shares auf; Root-LICENSE außerhalb isolierter Paketroots. V4-006 wurde vor Packagingänderung als Plan erfasst.

#### Ziel der Änderung

Die bestehende Lizenzimplementierung konsistent abschließend prüfen und den Originaltext bei isolierter Source-/Wheel-/Copy-colcon-Distribution nachweisbar mitliefern. Keine Source-Neulizenzierung fremder Software, kein vollständiger Transitiv-/Binärrechtsaudit und keine tatsächliche Veröffentlichung.

#### Technische Umsetzung

Offizieller ASF-TXT-Text am 14.10.2026 erneut erfolgreich heruntergeladen und bytegenau mit Root-LICENSE verglichen: 11358 Byte, 202 Zeilen, SHA-256 cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30. Je eine identische LICENSE liegt nun im Paketroot; beide setup.py ergänzen ausschließlich LICENSE im share-data_files-Eintrag und license_files=['LICENSE']. Kein ../LICENSE-/Workspacepfad, keine neue Lizenzbedingung, keine Versions-/Dependency-/Entry-Point-/Buildtypänderung. Kopien sind für isolierte Paketroots notwendig und gegen den unveränderten Roottext geprüft.

Das bestehende Lizenzinventar/22-teilige Kapitel ist ergänzt, nicht neu recherchiert. 18 vorhandene SPDX-Attributionen 2026 Bastian Aumer bleiben erhalten; das Jahr entspricht der ausdrücklichen Entwicklerentscheidung, ist kein Beweis ausschließlicher Entstehung aller Codezeilen in 2026. Sechs OSRF-Templates tragen ihren ursprünglichen Namen/2015 bzw. 2017/Apachetext unverändert. Leere Marker, YAML-/Dokumentations-/Metadaten-/TXT-/Bytecodebestände erhalten keine unbelegte reine Eigenentwicklungsattribution. Fehlende Header allein sind kein nachgewiesener Lizenzverstoß; genaue Provenienz und Distributionsbefugnis solcher Anteile bleiben differenziert.

LiDAR-Git-Nachweise werden aus vorhandenem Cache kontrolliert: Original-/Modified-Root-LICENSE-Blob identisch 4b3333d…, Copyright 2020 Ryohei Sasaki, genau drei bereits dokumentierte Folgecommits. NDT k.koide/BSD-2 und konkrete PCL-Dateien BSD-3 bleiben aus zuvor verifizierten gepinnten Quellen dokumentiert; keine neue vollständige Upstream-/Deploymentprüfung und keine externe Änderung. Modification Notice im Protokoll abgeschlossen, externe Anwendung separat offen. Extern installierte Libraries sind nicht im Wheel vendort; NumPy-Wheel-Zusätze bleiben für mögliche gemeinsame Bundles relevant.

#### Begründung

Root-Lizenz allein garantiert keine Mitnahme in isolierten ROS-/Pythonpaketen. Paketlokale identische Kopien plus explizite Share-/Lizenzmetadaten lösen diese konkrete Lücke minimal. Datenfreier aktiver Tree/Artefakte beheben keine Rechte an historischen Gitobjekten oder unbekannten Verträgen. Source/ROS Index/rosdep/Debian-Buildfarm haben getrennte Nachweisanforderungen.

#### Verifikation

System-Python 3.10.12 mit PYTHONNOUSERSITE=1/PYTHONDONTWRITEBYTECODE=1, setuptools 59.6.0, wheel 0.37.1. Temporäre vollständige Paketkopien einschließlich vorhandener PYC: je sdist und Wheel erfolgreich erzeugt. sdists enthalten je eine identische LICENSE und alle drei fremden Tests byteidentisch; Wheels je zwei Originaltextkopien (.dist-info/LICENSE und .data/data/share/<pkg>/LICENSE), Metadaten License: Apache-2.0 und License-File: LICENSE. Alle vier Artefakte enthalten 0 PCDs/0 PYC. Hashes und Befehle in 11.21.5/T42-T48.

Aus beiden extrahierten sdists erfolgte ein Copy-colcon-Build: zwei Pakete erfolgreich, Summary 1min 1s; nur absichtlich deaktiviertes Bytecompiling warnt. Kein übergeordneter Repository-Root-Lizenzpfad erforderlich. Beide installierten Package-Shares besitzen identische LICENSE; gesamter Installbaum ohne PCDs. Nach Umbenennen extrahierter Source importiert der Probeprozess das installierte configuration.py und lädt die externe Nutzerkonfiguration erfolgreich. Ein Probeversuch war vor Fertigstellung des asynchronen Builds zu früh und fand install/setup.bash noch nicht; temporäre Source wiederhergestellt, erfolgreicher Buildabschluss abgewartet und Probe danach erfolgreich. Kein Repo-/Hardware-/Rechtsfehler daraus abgeleitet.

Statischer XML-/Setup-/SPDX-/AST-/Hashscope: Nur zwei erlaubte Setupkeywords/Sharedateien gegenüber V4-005; alle anderen Python-/ROS-/Analyse-/Planungsalgorithmen unverändert, 18 Header und sechs Fremdtemplates erhalten, Roottext/Versions-/Dependency-/Entry-Points unverändert. PDFs, ursprüngliche Branch-/Remote-/Tagreferenzen und .git/config geschützt. Keine erneut ausgeführte Hardware-/Gesamtlint-/colcon-test-/rosdep-/Debianprüfung behauptet. Die vorhandenen 43 Kartenfälle sind im unverändert übernommenen Code bereits unter V4-005 gelaufen.

Vor Commit fünf Pfade im Index/Working Tree, Diff-/Dokument-/Commit-Gate; danach SHA/Parent/Umfang/Status separat. Alle temporären PCD-Testfixtures entfernt, keine Standardkarte eingebunden. Ein erster Cleanup-Helfer versuchte eine testweise leere directory.pcd als Datei zu löschen (IsADirectoryError); die Unterscheidung Datei/leeres Testverzeichnis wurde korrigiert, Cleanup erfolgreich. Keine zusätzliche Forschungsdatei/PDF erzeugt.

#### Ergebnis

Technische AP01-Implementierung im benannten Umfang VERIFIED: Lizenzentscheidung/Originaltext/Attribution/Metadaten/Fremdnotices/Notice/aktiver Datenumfang und getestete Source-/Wheel-/Copy-Sharemitnahme. Vollständige rechtliche Releasefreigabe bleibt NOT VERIFIED; Gesamt-AP01 BLOCKED für Vertrags-/historische Daten-/sonstige Herkunfts-/tatsächliche Bundlefragen. ROS Index/Bloom/Buildfarm NOT READY. AP04/AP06/AP08/AP10 IN PROGRESS, AP02/AP03 NOT STARTED.

#### Auswirkungen

Fünf fokussierte Commitpfade; keine Änderungen an Root-LICENSE, Manifeste/Versionen/Dependencies/ROS-Interfaces/PCD-Algorithmen oder externen Repositories. Keine Historienumschreibung, keine Datenlöschung aus historischen Gitobjekten, kein Push/Release/GitHub-/Sichtbarkeitswechsel. Weitere Arbeit wartet auf den nächsten Auftrag.

### V4-007 - Historische Entwicklungsbaseline unverändert versionieren

**Datum:** 14. Oktober 2026 (Europe/Berlin)
**Arbeitspaket:** AP08; wissenschaftlicher Baselineschutz, keine technische Funktion
**Betroffene Dateien:** docs/R3D_Planner_Development_History.pdf und dieses zentrale Protokoll
**Git-Commit:** stabiler Subject `docs(history): track historical development baseline`; Parent 78afba0667c658df3e37e14f64b2df4b26075e86, eigene SHA nach Erzeugung separat geprüft
**Status:** **VERIFIED** für unveränderte PDF-Bytes und gezielte Git-Aufnahme; keine neue Softwarefunktion

#### Ausgangssituation

V4/HEAD 78afba0667c658df3e37e14f64b2df4b26075e86, Baseline c65642f… ist Vorfahr. Keine Änderungen versionierter Dateien/Index, ausschließlich bekanntes historisches PDF unversioniert. Bisher V4-001..006 und bestehendes Lizenzkapitel liegen unverändert vor. Das PDF beschreibt weiterhin V1 bis main einschließlich alter Karten und ist keine aktuelle V4-Anleitung.

#### Ziel der Änderung

Bestehende identische historische Referenz dauerhaft in Git aufnehmen, ohne PDF-Neuerzeugung, Inhaltsänderung oder rückwirkende Anpassung. Separater Commit, keine Metadatenimplementierung in diesem Vorgang.

#### Technische Umsetzung

Vorhandenes 33-seitiges PDF nach Prüfsummenvergleich gezielt zur Git-Aufnahme ausgewählt; ausschließlich PDF plus Protokoll im Commit-Gate. Geprüfter Hash 8c3603ec2dac85c5cabcca7ae7e85c8d8c709663fa02fabd09039274a2b35383 entspricht Vorgabe. PDF-Inhalt bleibt unverändert.

#### Begründung

Git-Clones sollen die wissenschaftliche Ausgangsreferenz enthalten. Versionierung einer schon vorhandenen Dokumentation ist keine neue Planner-/Preprocessor-Funktion oder rückwirkende Lizenzklärung.

#### Verifikation

Dateiexistenz/Tracking/Hash und /usr/bin/pdfinfo: 33 Seiten, 298707 Byte. Auf PATH lag zunächst ein gebündeltes pdfinfo, das wegen fehlender GLIBC_2.38 nicht startete; System-pdfinfo funktioniert. Kein Paket installiert und kein PDF geändert. Ein erster git diff --cached --check behandelte das ASCII-kodierte PDF als Text und beanstandete PDF-Format-Leerzeichen. Der Originalhash blieb identisch; für die erneute Reviewprüfung wurde PDF ausschließlich kommando-lokal über eine temporäre core.attributesFile als Binärdatei klassifiziert. Keine .gitattributes/Repo-Konfiguration geändert, keine PDF-Bytes reformatiert. Commit-Gate: V4/Parent/Einschluss exakt zwei Pfade, Originalbytes und Hash erhalten, Diff/Indexcheck; anschließend SHA/Parent/Status prüfen.

#### Ergebnis

PDF-Prüfung und Scope-/Index-Gate erfolgreich; identische historische Referenz gezielt versioniert. SHA/Parent/Commitumfang/Tracking werden nach Commiterzeugung separat bestätigt. Keine Dateiersetzung, kein Neuerzeugen und kein Rechtsfreigabenachweis.

#### Auswirkungen

Nur Versionierung derselben historischen Bytes; frühere PCD-Beschreibungen bleiben korrekt. Keine Karte zurückkopiert, keine andere Branchänderung, kein Push/History-Rewrite/GitHubzugriff mit Mutation.

### V4-008 - AP02-Paketmetadaten und Entwicklungsversion vereinheitlichen

**Datum:** 14. Oktober 2026 (Europe/Berlin)
**Arbeitspaket:** AP02; begleitend AP06/AP08/AP10, keine AP03-Umsetzung
**Betroffene Dateien:** beide package.xml/setup.py, README.md und dieses zentrale Protokoll (sechs Pfade)
**Git-Commit:** stabiler Subject `fix(ros): standardize ROS package metadata`; Parent/PDF-Commit 0d267f593100f385e989525273ff9b81c8c36748. Eigene SHA nach Erzeugung separat kontrolliert, kein Amend.
**Status:** **VERIFIED** für die 15 technischen AP02-Abnahmekriterien; keine vollständige ROS-/Rechts-/Releasefreigabe

#### Ausgangssituation

V4 war auf dem erwarteten 78afba0… und stammt von c65642f… ab. V4-007 versionierte zuvor das identische historische PDF. Versionierte Dateien/Index sauber, keine fremde Arbeit überschrieben. Protokoll mit V4-001..007 und Lizenzkapitel berücksichtigt; V4-008 als Plan vor Änderungen erfasst. Beide Format-3-Manifeste schon syntaktisch/mit catkin_pkg parsebar, aber Version 0.0.0 und TODO-Beschreibung; setup.py 0.0.1 mit uneinheitlichen Kurzbeschreibungen. Fehlende optionale URLs/Author, vorhandene konsistente Maintainerkontakte, ament_python-/Index-/Console-Script-Struktur und technisch verifiziertes AP01 sind Vorbestand.

#### Ziel der Änderung

Freigegebene Entwicklungsversion 0.0.1 und konsistente englische Beschreibungen in beiden Metadatenquellen, reale Projekt-/Issue-URLs und bekannte Autorrolle. Keine neuen Kontaktdaten oder Maintaineridentität erfinden. Namen, Lizenz, Buildtyp, Dependencies, Skripte, Launches, ROS-Verträge und Algorithmen unverändert; AP03 nicht vorziehen.

#### Technische Umsetzung

XML-Versionen 0.0.0→0.0.1; beide Setup-Versionen waren bereits 0.0.1 und bleiben so. TODOs durch die in Kapitel 13 wörtlich dokumentierten Beschreibungen ersetzt, Setup-Beschreibungen identisch. Beide XMLs ergänzen author Bastian Aumer sowie url type repository und bugtracker; setup.py ergänzt author, url und project_urls/Bug Tracker mit denselben Projektzielen. Keine Author-E-Mail ergänzt. Maintainer bauya/baau1001@stud.hs-kl.de bleiben aus den gültigen konsistenten Projektmetadaten unverändert; ihr Alias ist nicht automatisch durch den Copyrightnamen ersetzt. Die optionale Author-Angabe folgt der dokumentierten Erklärung für eigenen Code und ersetzt keine Fremdattribution.

README ergänzt knappe Paket-/Version-/Repository-/Lizenz-/lokale V4-/Releasehinweise und grenzt vorhandene öffentliche V3-Cloneanweisungen vom unveröffentlichten V4 ab. INSTALL/CONFIGURATION enthalten keine durch diese Metadatenänderung neu falschen Versions-/Kontakt-/Lizenzangaben und blieben unverändert. Keine neue Forschungsdatei. PCD-Karten bleiben entfernt; separate Selbstauskunft/Future-Branchentscheidung in V4-009 ohne Ausführung.

#### Begründung

REP-149 beschreibt Manifeststruktur; REP-144 regelt Namen. Die gelesene Humble-Python-Anleitung verlangt konsistente Paket-/Setupmetadaten und beschreibt Resource-/setup.cfg-/Paketstruktur. URLs/Author sind optionale sinnvolle Ergänzungen, keine allgemeine Pflicht zu Website/Author-E-Mail. 0.0.1 ist ausdrücklich autorisierte Entwicklungsversion, nicht 4.0.0 oder bereits veröffentlichte Version. Release-/API-/Stabilitäts-/Versionierungspolitik verbleibt AP10.

#### Verifikation

System-Python 3.10.12, catkin_pkg 1.1.1, ElementTree, pytest 6.2.5, setuptools 59.6.0/wheel 0.37.1. Beide parse_package/Package.validate mit warnings-Liste erfolgreich, keine Warnungen (Exit 0). Explizit Format 3, lexikalische Namen, Version/Description/License, Maintainerstruktur, optionale Authorrolle, zwei richtige URL-Typen/kanonische HTTPS-Ziele und ament_python geprüft. Kontaktzustellung/Email-Befugnis oder aktuelle Live-URL-Erreichbarkeit nicht unabhängig geprüft; bestehende deklarierte Kontakte und Nutzer-URLs bleiben erhalten.

26 Python-Dateien parsebar; ausschließlich zwei Setup-ASTs ändern vier Metadatenkeywords description/author/url/project_urls. Nach Entfernen genau dieser Metadatenschlüssel sind ASTs vor/nach identisch; alle anderen 24 Python-ASTs und alle Laufzeit-/Launch-/Algorithmusbytes unverändert. XML-Dependency-Elemente inklusive Kategorien/Attribute bytegleich, Python install_requires/tests_require/Entry-Points/Versions-/Lizenz-/data_files-/license_files-Konfiguration erhalten. Indexmarker und Console-Script-Ziele auf vorhandene main-Funktionen geprüft; drei Original-LICENSEs/18 SPDX-/sechs Fremdheader/PDF unverändert.

40 passende bestehende Konfigurationsfälle bestanden, 3 native ROS-/Launchfälle bewusst nicht wiederholt (0,36 s, Exit 0). Diese drei waren unter V4-005 bestanden; sie werden nicht als neuer AP02-Lauf ausgegeben. Zwei temporäre Wheels erfolgreich erzeugt: Version/Beschreibung/Author/Maintainer/Home-page/Bugtracker/Apache-Metadaten sowie Share-Manifeste, Lizenzkopien und ament-Marker geprüft, 0 PCDs. Erster Wheelchecker verlangte fälschlich Name gleich ROS-Underscorename; Python-Metadaten normalisieren zu r3d-planner/r3d-preprocessor. Nach Abgleich gegen PyPA/packaging.utils.canonicalize_name korrekt geprüft, keine ROS-/Importnamen geändert. Ein weiterer Hilfsvergleich suchte die Description als zusammenhängenden Quelltext nach reinem Zeilenumbruch; er wurde auf den tatsächlichen AST-Stringwert korrigiert. Keine Produktions-/Metadatenregression aus diesen Hilfsfehlern. Die Wheel-Builds melden absichtlich deaktiviertes Bytecompiling und SetuptoolsDeprecationWarning für den vorhandenen setup.py-install-Unterprozess; beide Exit 0. Keine tatsächliche Wheelinstallation/colcon-/Debian-/Buildfarm-/rosdepabnahme behauptet.

Die ros.org/docs.ros.org-Endpunkte lieferten Access Denied; relevante offizielle GitHub-Raw-REPs/Humble-Quelldokumentation gelesen. Das PDF wurde bereits separat hashidentisch versioniert; seine Byteprüfung bleibt gültig. T50-T54/13.3 dokumentieren Befehle, Exitcodes, Grenzen und Quellen. Vor Commit: sechs genaue Pfade, V4/Parent/Index-/Diff-/Dokumentgate; danach SHA/Parent/Umfang/sauberer Status kontrolliert. Keine System-/Conda-/Globalpip-/Hardwareänderung.

#### Ergebnis

AP02-Metadaten im beauftragten technischen Umfang VERIFIED; keine offene notwendige AP02-Korrektur aus diesen Prüfungen. Maintainerkontakt organisatorisch vor Release zu bestätigen, Namenskollisionen/live URLs/Versionierungspolitik als Releasefragen nicht als erledigte AP02-Serverprüfung ausgeben. AP01 technisch VERIFIED, Rechtsgesamtfreigabe weiterhin getrennt; AP03 NOT STARTED. Kein Quality-/Runtime-/rosdep-/Index-/Bloom-Freigabenachweis aus Metadatenprüfung.

#### Auswirkungen

Nur Paketmetadaten und README/Protokoll; keine Algorithmen, ROS-Themen/Actions/Sicherheitsmechanismen, Dependencies, Buildtypen, Entry-Points, Launches, Konfiguration oder Lizenzentscheidung geändert. Historische Entwicklungsleistungen nicht rückwirkend AP02 zugerechnet. Historisches PDF identisch, keine PCDs zurückkopiert, keine anderen Branches/Merges/History-Rewrites/Remotes/GitHub-/Push-/Releaseaktionen. AP03 als nächster technischer Schritt nur vorgeschlagen, Freigabe abwarten.

### V4-009 - Entwicklererklärung und spätere historische Kartenbereinigung dokumentieren

**Datum:** 14. Oktober 2026 (Europe/Berlin)
**Arbeitspaket:** AP01-Rechteabgrenzung/AP08/AP10; reine Dokumentation
**Betroffene Dateien:** ausschließlich dieses bestehende zentrale Protokoll
**Git-Commit:** gemeinsam mit V4-008 unter `fix(ros): standardize ROS package metadata`; keine fremden Branchcommits
**Status:** **COMPLETED** für zutreffende Erklärungsdokumentation; zugrunde liegende Rechte-/Datenschutzsachverhalte nicht unabhängig verifiziert

#### Ausgangssituation

Die bisherigen PCDs sind seit V4-005 aus aktivem V4 entfernt, historische Gitobjekte/PDFbeschreibungen bestehen. Der Nutzer ergänzt ausdrücklich eine Herkunfts-/Datenschutzselbstauskunft und möchte eine spätere Branchbereinigung.

#### Ziel der Änderung

Die neue Information korrekt als Entwicklererklärung aufnehmen und die verlangte Dokumentation von einer nicht autorisierten technischen Branch-/Historienänderung trennen.

#### Technische Umsetzung

Bastian Aumer erklärt, die ursprünglichen PCD-Beispielkarten selbst aufgenommen und verarbeitet zu haben und dabei keine Datenschutzauflagen verletzt zu haben. Unabhängig davon sollen Karten künftig aus den aktiven Beständen von V1, V2, V3 und main entfernt werden. V4 ist schon bereinigt. Hier wurde ausschließlich dieser Wunsch dokumentiert; Ausführung ist separate zukünftige Aufgabe mit eigenem explizitem Auftrag. Keine Branchwechsel, fremden Commits/Merges/Remoteänderungen/Objektlöschung/History-Rewrites/Force-Pushes.

#### Begründung

Selbstauskunft verbessert die dokumentierte Herkunftslage, ersetzt aber keine unabhängige Nutzungs-/Vertrags-/Datenschutzprüfung oder rückwirkende Entfernung veröffentlichter Objekte. Ein neuer Löschcommit auf einem historischen Branch wäre zudem nicht gleichbedeutend mit Löschung seiner alten Gitobjekte; hier ist beides unbegonnen.

#### Verifikation

Erklärung gegen den aktuellen Nutzerauftrag vollständig abgeglichen. Refs-/Config-/PDFhashes vor/nach schützen main/origin/V1/V2/V3/main und alle historischen Objekte; keine weiteren Branchaktionen ausgeführt. Historische PDF kann alte Karten weiterhin korrekt beschreiben; SHA unverändert. T54 ist Dokument-/Scopeprüfung, keine Rechtsprüfung.

#### Ergebnis

Herkunft/Datenschutz laut Entwickler dokumentiert. Gewünschte Kartenentfernung aus anderen Branches NOT STARTED; technische Datenfreiheit von V4 weiterhin VERIFIED; unabhängige historische Rechtsfreigabe NOT VERIFIED.

#### Auswirkungen

Nur Dokumentation, keine Daten-/Lizenz-/Branch-/Objektänderung. Späterer eigener Auftrag notwendig, kein Push und keine Veröffentlichung.

### V4-010 - Aktuelle historische Branch-Trees von PCD-Beispielkarten bereinigen

**Datum:** 14. Oktober 2026. **Arbeitspakete:** Datenumfang/AP01, AP08/AP10; getrennt von AP03. **Status:** VERIFIED für die lokalen aktuellen Trees und statische Folgeprüfung, keine historische Objektlöschung/Runtime- oder Rechtsgesamtfreigabe.

**Ausgangslage und Freigabe:** V4-HEAD `d2e05e696f259be155d943f80de4a7c849be53ae`, sauberer Index/Tree, ein bestehender V4-Worktree. V1/V2/V3 nur als origin-Trackingrefs, main lokal auf der Forschungsbaseline. Auftrag erlaubt die Bereinigung ausdrücklich; automatische Ausführungsprüfung lehnte zunächst die als Attachment übermittelte Autorisierung ab. Keine Mutation erfolgte dabei. Der Nutzer bestätigte daraufhin im Chat „Ja, beide Teile wie im Auftrag ausführen“. Keine Systeminstallation, keine Veröffentlichung. Die zuvor auf V4 entfernten Dateien bilden auch auf allen vier historischen Tips den vollständigen PCD-Bestand, keine zusätzlichen PCD-Testfixtures.

**Entscheidung:** ausschließlich die zwei identischen gebündelten Beispielkarten entfernen. V1/V2 besitzen keine zentrale Karten-YAML, ihre nodeeigenen generischen Defaults (`environment.pcd`, `map_analysed.pcd`) werden nicht modernisiert; dokumentierte konkrete Beispielkommandos auf eigene absolute Pfade ändern. V3/main bekommen leere maps-Werte; der bereits vorhandene unveränderte Loader lehnt diese mit `maps.pcd_path: expected a path` ab. Er verlangt beide nichtleeren Pfade, auch einen zukünftigen analysierten Ausgabepfad vor der Vorverarbeitung. Keine V4-Modevalidierung, Odometry-/Metadaten-/Lizenz-/Versionsarbeit in historische Branches übernommen.

**Umsetzung:** Reihenfolge V1 → V2 → V3 → main, je neuer temporärer Worktree unter `/tmp/r3d-v4-ap03/history-<Branch>`. V1/V2/V3 als lokale gleichnamige Branches vom jeweils vorhandenen Remote-Tip angelegt, main vom lokalen Tip; `git rm --` mit den beiden einzeln inventarisierten Pfaden. Pro Branch genau ein Commit `chore(data): remove bundled PCD example maps`. Nur diese neuen Worktrees nach Commit/sauberer Prüfung entfernt; lokale Branches bleiben. Kein V4-Checkoutwechsel, Merge oder Cherry-Pick. Die neu erzeugten branch.V1/V2/V3 Trackingkonfigurationen referenzieren origin; vorhandene Remote-URLs/Remote-Trackingrefs bleiben unverändert.

**Inventar vor jeder Löschung:**

| Branch | Dateipfad | Bytes | Blob-SHA | Zweck / Referenz / Entscheidung |
|---|---|---:|---|---|
| V1 | `r3d_preprocessor/maps/voxel_05_minhits_7.pcd` | 19284059 | `33c0cea4ff7e7ae55bcbbf0ded436cf0c7fb7a5c` | Roh-PCD für Vorverarbeitung; README/INSTALL/README_r3d_planner.txt Beispiele; DELETE, gebündelte Beispielkarte |
| V1 | `r3d_preprocessor/maps/voxel_05_minhits_7_analysed.pcd` | 8905560 | `2bc0be5f7d1f5c5e2aa77ba44a5f798558ff8744` | RGB-klassifizierte Planungs-/Visualisierungseingabe; README/INSTALL/README_r3d_planner.txt Beispiele; DELETE, gebündelte Beispielkarte |
| V2 | `r3d_preprocessor/maps/voxel_05_minhits_7.pcd` | 19284059 | `33c0cea4ff7e7ae55bcbbf0ded436cf0c7fb7a5c` | Roh-PCD für Vorverarbeitung; README/INSTALL/README_r3d_planner.txt Beispiele; DELETE, gebündelte Beispielkarte |
| V2 | `r3d_preprocessor/maps/voxel_05_minhits_7_analysed.pcd` | 8905560 | `2bc0be5f7d1f5c5e2aa77ba44a5f798558ff8744` | RGB-klassifizierte Planungs-/Visualisierungseingabe; README/INSTALL/README_r3d_planner.txt Beispiele; DELETE, gebündelte Beispielkarte |
| V3 | `r3d_preprocessor/maps/voxel_05_minhits_7.pcd` | 19284059 | `33c0cea4ff7e7ae55bcbbf0ded436cf0c7fb7a5c` | Roh-PCD für Vorverarbeitung; planner_config.yaml maps.pcd_path; DELETE, gebündelte Beispielkarte |
| V3 | `r3d_preprocessor/maps/voxel_05_minhits_7_analysed.pcd` | 8905560 | `2bc0be5f7d1f5c5e2aa77ba44a5f798558ff8744` | RGB-klassifizierte Planungs-/Visualisierungseingabe; planner_config.yaml maps.map_name; DELETE, gebündelte Beispielkarte |
| main | `r3d_preprocessor/maps/voxel_05_minhits_7.pcd` | 19284059 | `33c0cea4ff7e7ae55bcbbf0ded436cf0c7fb7a5c` | Roh-PCD für Vorverarbeitung; planner_config.yaml maps.pcd_path; DELETE, gebündelte Beispielkarte |
| main | `r3d_preprocessor/maps/voxel_05_minhits_7_analysed.pcd` | 8905560 | `2bc0be5f7d1f5c5e2aa77ba44a5f798558ff8744` | RGB-klassifizierte Planungs-/Visualisierungseingabe; planner_config.yaml maps.map_name; DELETE, gebündelte Beispielkarte |

V4: keine PCD-Datei, NO CHANGE REQUIRED an V4-Karten. Beide Karten wurden nie über die betreffenden setup.py-data_files installiert; keine Installregel musste geändert werden. Pickles, Quellcode, bestehende pyc, Lizenz- oder sonstige Artefakte nicht entfernt. Historische ARCHITECTURE-Inventare als frühere Bestände gekennzeichnet, keine mitgelieferten Karten mehr zugesagt.

| Branch | Alter HEAD | Neuer HEAD / Löschcommit | Gelöscht | Statische Prüfungen |
|---|---|---|---|---|
| V1 | `01348f3285a0e7582f70cc5f2ed3d1bf4b7f904b` | `91ccb1a824e7d2d7163433f13594d6c07855b1c5` | 2 PCDs | 21 Python-ASTs, 1 YAMLs, 2 Manifeste/0 Warnungen; exakte Diff-Whitelist, Vorfahrprüfung, Tree frei von PCD |
| V2 | `3abd002e8cc9e7a26cacaf43a5c20b1822664f14` | `cc2f5bef269b3dcb1664bc52bba1d9c0be1bd1ca` | 2 PCDs | 18 Python-ASTs, 1 YAMLs, 2 Manifeste/0 Warnungen; exakte Diff-Whitelist, Vorfahrprüfung, Tree frei von PCD |
| V3 | `3752404a08867e9e6f3725300b88e148d4d5be37` | `a914f0e4cd793f1ed7f35501e09a7ca865914b67` | 2 PCDs | 26 Python-ASTs, 3 YAMLs, 2 Manifeste/0 Warnungen; exakte Diff-Whitelist, Vorfahrprüfung, Tree frei von PCD |
| main | `c65642fe56015556f696364a724cb5b976a27888` | `51a08ed3da1bd43f06d89c6a84bbbd540aaf5861` | 2 PCDs | 26 Python-ASTs, 3 YAMLs, 2 Manifeste/0 Warnungen; exakte Diff-Whitelist, Vorfahrprüfung, Tree frei von PCD |

**Betroffene Dateien:** V1/V2: die zwei Karten, README.md, INSTALL.md, README_r3d_planner.txt, docs/ARCHITECTURE.md. V3/main: die zwei Karten, r3d_planner/config/planner_config.yaml, README.md, docs/CONFIGURATION.md, docs/ARCHITECTURE.md. Ausschließlich Markdown-/Beispielpfade und zwei YAML-Skalare korrigiert. Alle Python-Dateien einschließlich setup.py, package.xml, Lizenzen, übrige Konfiguration und Tests bytegleich zum jeweiligen alten Tip. Somit Funktionen zum PCD-Laden, Analysieren/Klassifizieren/Schreiben, Graphaufbau, Pickle-Verarbeitung (V1) und A* unverändert; kein funktionaler Lauf mit den entfernten Karten behauptet.

**Verifikation/Befehle:** `git status --short`, `git branch -avv`, `git branch --show-current`, `git log -10 --oneline`, `git remote -v`, `git worktree list`; `git ls-tree -r -l <Tip>` für Pfad/Blob/Größe; `git grep -n -I voxel_05_minhits_7 <Tip>` für Referenzen; `git worktree add [-b <fehlender lokaler Branch>] <neuer Temp-Pfad> <verifizierter Branch/Remote-Tip>`, explizites `git rm`, gezieltes git add, `git diff --cached --check`, Python3.10-AST/YAML/catkin_pkg-Parsing, `git commit`, `git merge-base --is-ancestor <alt> <neu>`, `git ls-tree -r --name-only HEAD`, `git worktree remove <eigener neuer Pfad>`. Statische Gates und Commitbefehle jeweils Exit 0; negative Referenzsuche Exit 1 bedeutet keine aktive Fundstelle. V3/main-Loaderprobe liefert erwartete ConfigurationError. Keine neuen historischen Tests erstellt. Historische sechs Linttests bzw. zusätzlich V3/main-Konfigurations-/ROS-Tests nicht ausgeführt: kein voller Branch-Test-PASS. Automatische Tests referenzieren die beiden konkreten Kartennamen nicht; datenabhängige manuelle Beispiele brauchen nun eigene Daten.

**Baseline/Historie:** `c65642fe56015556f696364a724cb5b976a27888` bleibt dasselbe Commitobjekt und Vorfahr von main/V4. Alle ursprünglichen Tips/13 historischen Commits bleiben erreichbar, alte Trees enthalten die identischen Kartenblobs weiterhin. Das 33-seitige PDF ist unverändert: SHA256 `8c3603ec2dac85c5cabcca7ae7e85c8d8c709663fa02fabd09039274a2b35383`. Öffentliche GitHub-Trees, Forks und Kopien wurden nicht verändert; keine vollständige rückwirkende Entfernung behaupten. V4-Code am Ende von Teil A weiterhin d2e05e6/bytegleich/sauber. Dokumentationscommit: der Commit, der V4-010 enthält (auflösbar via `git log -- docs/V4_ROS_COMPLIANCE_DEVELOPMENT.md`); historische Commitreferenzen oben vollständig.

### V4-011 - Direkte Dependencies und Humble/Jammy-rosdep-Verträge korrigieren

**Datum:** 14. Oktober 2026. **Arbeitspaket:** AP03, begleitend AP04/AP06/AP08/AP09/AP10 nur Nachweise/Planung. **Status:** Implementierung/Importabgleich/Key-Auflösung/Copy-Build/43 Funktionstests VERIFIED; AP03 insgesamt IN PROGRESS, Installations-/Check-Gate BLOCKED in der derzeit ohne Systeminstallation zugelassenen Umgebung. Keine vollständige Clean-OS-/Lint-/Release-Verifikation.

**Vor Umsetzung dokumentierter Scope:** Nach gesondertem Abschluss von V4-010 ist AP03 ausdrücklich freigegeben. Ausgangs-V4 d2e05e6; vor Dependencyänderung separater V4-Dokumentationscommit `b8967211a2a6696f3bfebdd32e8793a315d6eb86`. Nur beide XML-Dependencyblöcke und bestehende README/INSTALL/KNOWN_ISSUES/Paket-READMEs/Protokoll ändern. setup.py/setup.cfg, Algorithmen, ROS-Verträge, Launchdateien, Testdateien, Entry-Points, Lizenztexte und AP02-Metadaten bytegleich erhalten. Kein globales pip/Apt-/Conda-Update; ausschließlich aktuelle offizielle rosdep-Regeln und isoliert entpackte Jammy-Apt-Archive für Prüfungen. Keine eigenen Keys, keine Skip-Endlösung, keine AP04-Implementierung.

**Ausgangsstand/Problem:** ROS-/Science-Manifestangaben und Apt-Liste vorhanden, aber 128 AST-Importstellen in 26 Python-Dateien zeigen direkte Lücken (Open3D beide Pakete, NetworkX/std_msgs/sensor_msgs_py Planner); numpy/scipy sind ungültige Keys. tf2_ros war vorhanden, bezeichnet jedoch nicht den direkt importierten Python-Provider. Externe Robotikpublisher/Hesai/SLAM/Unitree/Nav2-Bringup sind keine eingebauten Bibliotheken. setuptools/tests_require/Marker-/Script-/License-/Launch-/Config-Mitnahme bestanden bereits vor AP03.

**Entscheidung/Umsetzung:** Alle reinen Python-/ROS-Runtimeimporte als exec_depend; kein pauschaler depend mit unbelegten Compile-/Exportrollen. NumPy → python3-numpy beide, SciPy → python3-scipy Planner; Open3D beide und NetworkX/sensor_msgs_py/std_msgs Planner ergänzt; tf2_ros durch tf2_ros_py ersetzt. Planner behält launch/launch_ros/ament_index_python/python3-yaml/r3d_preprocessor. Beide Pakete deklarieren python3-setuptools als buildtool_depend (setup.py/colcon) und exec_depend (bestehendes install_requires); verschiedene Rollen, kein doppelter identischer Tag. ament_python bleibt build_type, nicht erfundener Buildtool-Key. Vier vorhandene Testdeps bleiben; Planner ergänzt ros2cli/ros2launch/ros2param für tatsächlich ausgeführte CLI-Integrationstests. Keine Paketstruktur-, Lizenz-, Versions- oder Algorithmusänderung. setup.py bleibt vollständig bytegleich: install_requires=['setuptools'], tests_require=['pytest']; kein ROS-/Science-pip-Parallelresolver. Source/colcon hat Vorrang, kein PyPI-Vollruntimevertrag zugesagt.

**Dokumentation:** Aktive V4-README/INSTALL-Anleitung mit normalem rosdep ohne Skip-Liste. Unveröffentlichter lokaler V4-Clone gegenüber unveränderten öffentlichen V3-Metadaten ausdrücklich unterschieden; kein erfundener origin/V4. Manuelle Voll-Apt-Liste durch manifestbasierten Prozess ersetzt, Workspace-Buildtools separat, RViz/TF-CLI/Hesaisensor/Odometry/Robotadapter optional/extern. KNOWN_ISSUES und beide Paket-READMEs aktualisiert statt den behobenen Keyfehler weiter als aktuellen V4-Blocker auszugeben. Historisch eingefrorener V2-REFERENCE_COMPARISON-Bericht bleibt unverändert und benennt frühere rosdep-Exclusions ausdrücklich für seinen Snapshot.

**Verifikation/Ergebnis:** 2 Manifeste mit catkin_pkg 1.1.1/Package.validate und 0 Warnungen; AP02-Metadaten und 24 sonstige Python-Dateien sowie beide setup.py/AP01-Lizenzen bytegleich. 26 tatsächlich deklarierte externe Keys lösen unter Humble/Jammy via apt auf (Exit 0 je Key); r3d_preprocessor ist lokales Paket/kein externer rosdep-Key. rosdep install --simulate Exit 0, rosdep check Exit 1 ausschließlich python3-open3d/python3-networkx nicht installiert. Isolierte Copy-colcon-Builds Exit 0, beide Pakete/7 Entry-Points/2 LICENSEs/4 Launches/3 YAML-Ressourcen verifiziert, keine PCD-Artefakte. Vorhandene Funktionstests 43 PASS; finale Gesamtsuite 49 Tests: 45 PASS, 2 Flake8 FAIL (166/150 Befunde), 2 Copyright SKIP; colcon test Exit 0 ist trotz Fehlern keine grüne Gesamtsuite, test-result Exit 1. Kein neuer Testcode/keine Formatierung. Details und initiale Fehlversuche in Abschnitt 15.

**Grenzen:** keine tatsächliche apt-/rosdep-Installation, kein rosdep-check-PASS, kein Docker-/frischer OS-/Buildfarmlauf. Open3D 0.14.1/NetworkX 2.4 aus 17 ausschließlich nach /tmp geladenen und entpackten Jammy-Debs mit System-NumPy 1.21.5/SciPy 1.8.0 und nativem Humble getestet; vorhandene hostseitige ROS-/Systempakete weiterhin Voraussetzung. User-Site-NumPy 1.26.4/SciPy 1.8.0 produziert nachgewiesene Kompatibilitätswarnung; native getestete Kombination nicht. NetworkX 2.4 meldet bestehende np.int-Deprecations, keine globale Reparatur. Noble-Open3D-Regel ausdrücklich unavailable: AP09-Teilblocker, kein Jazzy-Runtimeversuch. Lizenz-/Defaultconfig-/Ausgabepfade-/CI-/Versionpolicy-/Release-Gates bleiben offen. AP04 als nächsten gesondert freizugebenden Schritt vorschlagen, hier nicht beginnen.

**Betroffene Dateien:** r3d_planner/package.xml; r3d_preprocessor/package.xml; README.md; INSTALL.md; r3d_planner/README.txt; r3d_preprocessor/README.txt; docs/KNOWN_ISSUES.md; docs/V4_ROS_COMPLIANCE_DEVELOPMENT.md. Commitreferenz: fokussierter Commit `fix(deps): correct ROS dependencies and rosdep keys`; SHA `d177d3052d9554b3a2a9a160a7a79ddb52c94e6f`; ergänzender Abschlussnachweis in Abschnitt 15.12. Historische Branchcommits/PDF/Historienobjekte davon getrennt.

### V4-012 - Tatsächliche Humble-Dependencyinstallation verifizieren

**Datum:** 14. Oktober 2026 (Europe/Berlin). **Arbeitspaket:** AP03, AP08/AP10 Nachweise. **Betroffene Dateien:** nur zentrales Protokoll; keine Manifest-/Hoständerung. **Git-Commit:** `test(deps): verify rosdep installation on Humble`, Parent e204fee7e71aa915d76245223fb78003e268d158, eigene SHA als abgeschlossener Commit unten ergänzt. **Status:** VERIFIED im definierten Humble/Jammy-Umfang.

#### Ausgangssituation

V4 sauber auf e204fee, ursprüngliche Baseline Vorfahr, V4-001..011 vollständig gelesen. Andere Branches/Remotes/Worktree/PDF geschützt. Bisher 26 gültige Keys/Simulation/entpackte Debs, aber kein Install-/Check-PASS; Host-Apt-Open3D/NetworkX weiterhin fehlen. Aktive Shell enthält Conda3.14 und fremde ROS-Overlays; System-Python3.10 vorhanden.

#### Ziel der Änderung

Tatsächliche Installation plus Check/Imports im isolierten Humble/Jammy-System, ohne Skip oder globalen Hosteingriff. AP04/AP06 gezielt weiter ausdrücklich freigegeben; AP05/AP07 weiterhin nicht beginnen.

#### Technische Umsetzung

Docker29.1.3 funktioniert außerhalb Sandbox; dort nur Socket-Sandboxzugriff zunächst abgelehnt, Hostkonfiguration unverändert. Offizielles ros:humble-ros-base gezogen, gepinnter Digest sha256:860e53793ccf575e5369b5e9a19939de2bfcfb46a299954d06f54f2af54fed19. Temporärer Container r3d-v4-humble-completion-20261014, kein privileged/host-network/sensitiver Mount. Nur /r3d-source readonly, temporäre /tools readonly und getrennte /results. ROS_DOMAIN_ID201/localhost/FastDDS, Python-System/Apt ohne Conda/User-Site. Container-Apt-Update und Workspacewerkzeuge, rosdep update/install/check; keine Paketversionpins oder Dependencykorrektur nötig.

#### Begründung

Realer Apt-/dpkg-Satz und Exit0-Check schließen das bisherige Installationsgate; entpackte Bibliotheken sind nicht mehr der alleinige Nachweis. Import-, Build-, Runtime- und Releaseabnahme bleiben unterschiedliche Prüfungen.

#### Verifikation

Container Ubuntu22.04/Python3.10.12/ROS Humble, rosdep0.27.0/colcon-core0.21.3/setuptools59.6.0/pytest6.2.5. 26 individuelle rosdep resolve --rosdistro humble --os=ubuntu:jammy Exit0. Tatsächliches rosdep install --from-paths /r3d-source/r3d_planner /r3d-source/r3d_preprocessor --ignore-src --rosdistro humble --os=ubuntu:jammy -y Exit0, kein simulate/skip; anschließend rosdep check mit denselben Pfaden Exit0, „All system dependencies have been satisfied“. NumPy1.21.5/SciPy1.8.0/Open3D0.14.1/NetworkX2.4/YAML5.4.1 und benötigte ROS-Module importierbar. Keine SciPy/NumPy-Inkompatibilitätswarnung; alte NetworkX-np.int-Deprecations vorhanden. Module /usr/lib/python3/dist-packages und /opt/ros/humble, keine User-Site/Conda-/alten R3D-Overlays. Beide XMLs gültig/unverändert. Unveränderte Eingangssuite frisch im Container gebaut/getestet: 49 Testcases/45 PASS/2 Flake8 FAIL/2 Copyright SKIP, test-result Exit1, keine künstliche Gesamtabnahme.

Fehlversuche: temporäres Bootstrap-nounset brach vor Apt bei ROS setup.bash mit AMENT_TRACE_SETUP_FILES unbound ab; Helper korrigiert, während Sourcen nounset aus. Erster tatsächlicher Install-/Checklauf bestand, spätere Hilfsabfrage des Debian-Metadatennamens catkin-pkg scheiterte; Versionprobe korrigiert, vollständiger finaler Bootstrap Exit0. Keine fehlerhafte Paketdeklaration daraus abgeleitet. Vollständige relevante Kommandos/Ausgaben in Abschnitt16.1; weitere Test-/Codeänderungen eigene IDs.

#### Ergebnis

AP03 ursprüngliche Humble-Kriterien jetzt VERIFIED: vorhandene konsistente Manifeste/26 Keys plus tatsächliche Installation/Check/Imports/reproduzierbares Verfahren. Kein Host-System-/pip-/Conda-/NVIDIA-/ROS-Eingriff. Hostdpkg meldet weiter keine python3-open3d/python3-networkx; Erfolg gilt für Container. Keine Multi-Distro-/CI-/Buildfarm-/Rechtsfreigabe.

**Abgeschlossener Commit:** `7a476588ba3e50550074c14920b95d3658e45a03`.

#### Auswirkungen

Nur Dokumentation, keine Dependency-/Algorithmus-/ROS-Namens-/Lizenz-/Versionsänderung. Vorhandene Dockerimages nicht gelöscht, kein Push/Release, keine fremden Branches. AP04/AP06 folgen mit eigener Dokumentation und zielgerichteten Änderungen.

### V4-013 - Kopierte Package-Share-Konfiguration regulär auflösen

**Datum:** 14. Oktober 2026. **Arbeitspaket:** AP04, begleitend AP06/AP08. **Status:** VERIFIED für gezielte Share-Auflösung/40 Konfigurationsfälle; Gesamt-AP04 bis V4-016 IN PROGRESS. **Git-Commit:** `fix(install): support source-independent ROS installation`. **Betroffene Dateien:** configuration.py, bestehender test_configuration.py, aktuelle Konfig-/Installationsanleitungen und zentrales Protokoll.

#### Ausgangssituation

AP03 im Container VERIFIED, Configloader bevorzugt live Source/Symlink und verweigert noch kopierte Share-YAML. Vorhandener Test sichert alte Ablehnung ab. Kein impliziter Kartenfallback; vorhandene Nutzer-Overrides/strikte Schemaprüfung erhalten.

#### Ziel der Änderung

R3D_CONFIG_DIR zuerst, direkte Source-/Symlinkentwicklung weiter möglich, ansonsten reguläre über ament_index_python gefundene installierte YAML inklusive Robotprofil. Keine Sourcepflicht für Copy-Installation, keine unbemerkte Rückkehr von ungültigen Nutzerpfaden zum Default.

#### Technische Umsetzung

Gezielte Änderung der Defaultauflösung auf reguläre Sharedatei, bestehende Testpolitik passend migrieren; keine Änderung von Schema/ROS-Namen, Planungs-/Sensor-/Followeralgorithmen. Vollständige Ressourcen-/Source-ausblendende Launchabnahme folgt unter eigenem V4-016.

#### Begründung

Copy-Paketressourcen sind normale ROS-Installation. Nutzer können eigene editierbare Kopien explizit wählen; installiertes Default ist schreibgeschützte Vorlage und erfordert weiterhin passende nutzerseitige PCDs.

#### Verifikation

Ausgeführt im gepinnten Apt/Humble-Container: python3 -m pytest -p no:cacheprovider --basetemp=/work/config-pytest-final test/test_configuration.py -k "not effective_ros_parameters_and_odometry and not preprocessor_real_launch and not real_launch_restart_and_all_components" -q, Exit0: 40 passed/3 deselected in 0.34s. Migrierter vorhandener Test prüft echte temporäre share/config-YAML samt Robotprofil und expliziten Override. Erster Lauf 39 PASS/1 FAIL, weil der Test-Share ohne notwendige config-Unterebene angelegt war; Fixture korrigiert, kein Produktionsfallback eingeführt. Kompletter tatsächlicher Copy-/Source-unavailable-/Launchnachweis folgt unter V4-016, hier nicht vorwegnehmen.

#### Ergebnis

Sharepolitik gezielt implementiert und statisch/mit 40 Fällen geprüft; Gesamt-AP04/AP06 IN PROGRESS bis vollständiger Installationsabnahme.

**Abgeschlossener Commit:** `c702da4ac241f3173d3732da3bdd1a754a04d949`.

#### Auswirkungen

Nur notwendige Installationspolitik und zugehörige Bestandsanleitung/Test; keine Versions-/Lizenz-/Dependency-/ROS-Interfaceänderung. AP05/AP07 nicht beginnen.

### V4-014 - PCD-Eingabe und beschreibbare Analyseausgabe trennen

**Datum:** 14. Oktober 2026. **Arbeitspaket:** AP04/AP06/AP08. **Status:** VERIFIED für Output-I/O/10 neue Fälle und 40 bestehende Configfälle; vollständiger Install-/Nodeumfang folgt V4-016. **Git-Commit:** `fix(config): separate PCD input and output paths`. **Betroffene Dateien:** optionaler preprocessing.output_dir/YAML/Loader, Analyzer-I/O, neuer eigener Outputhelfer und gezielte Outputtests, bestehende Configfixture/Anleitungen, Protokoll.

#### Ausgangssituation

Analyzer schreibt <input>_analysed.pcd neben Input, prüft write_point_cloud-Ergebnis nicht und kann bestehende Dateien überschreiben; main meldet nach abgefangenen I/O-Fehlern keinen Fehlerexit. Share/default und explizite Nutzerconfig sind getrennt, Input darf außerhalb Paketen liegen.

#### Ziel der Änderung

Schreibgeschützte Inputs verarbeiten, Ausgabe in gewähltem beschreibbarem Verzeichnis; sicherer datenfreier Nutzerdefault statt Package-Share. Bestehende Filename-/Klassifikations-/Graphalgorithmen erhalten, keine fremden Outputs überschreiben, klare Fehler und Regressionen.

#### Technische Umsetzung

Implementiert: optionaler output_dir-String in preprocessing, YAML-relative/absolute/~ Auflösung; leeres Default führt zu XDG_DATA_HOME/r3d_preprocessor bzw. ~/.local/share/r3d_preprocessor. Echte exklusive Ausgabepublikation über temporäre PCD im Zielverzeichnis und os.link ohne überschreibenden Replace; vorhandene Dateien/Symlinks ablehnen, temporäres Artefakt bei Fehlern entfernen. Open3D-Schreibfehler und Exitstatus sichtbar. Nur I/O/Packaging-Konformitätsänderung, keine neue Planung/SLAM/API-Überarbeitung.

#### Begründung

Inputbesitz und Outputschreibrechte unabhängig, Package-Share ist Ressource. Optionaler Schlüssel hält alte gültige YAMLs ohne neues Feld kompatibel. Neue Parameter ausdrücklich dokumentieren.

#### Verifikation

Ausgeführt im Apt/Humble-Container als r3dtest UID1000: python3 -m pytest -p no:cacheprovider --basetemp=/work/tests-user/output test/test_output.py -q → Exit0, 10 passed in 0.19s, kein Skip. Reale Open3D-Ausgabe/Readback und unveränderter SHA eines 0444-Inputs in 0555-Inputverzeichnis; File-/dangling-Symlink-Kollisionen unverändert, simulated Open3Dfalse mit vollständigem Tempcleanup, tatsächlich unwritable 0555-Outputdir PermissionError. Defaults XDG/fallback und fehlende/directory/suffix-Inputs geprüft. Bestehende passende Configfälle erneut Exit0, 40 passed/3 deselected in 0.34s. ASTs aller Voxel-/Boden-/Clearance-/Traversierbarkeits-/Treppenfunktionen vor/nach identisch; nur save_colored_pcd-I/O, run_processing-Output und main-Exit bewusst verändert. Gesamte installierte Node-/Launchsuite folgt V4-016, keine vorweggenommene Bestätigung.

#### Ergebnis

Output-I/O und 50 passende Fälle bestanden, keine unerwartete Configregression. Gesamt-AP04/AP06 bleiben bis installierter Gesamtabnahme IN PROGRESS.

**Abgeschlossener Commit:** `370cf5f9246791c570600fffceab637c3c4b564b`.

#### Auswirkungen

Kein neuer Topic/Action/Frame/Controller, keine Version-/Manifest-/Lizenztextänderung. Alte Daten unverändert, Tests nur temporäre synthetische PCDs.

### V4-015 - Flake8 und Copyrightprüfungen tatsächlich ausführen

**Datum:** 14. Oktober 2026. **Arbeitspaket:** AP06, AP08. **Status:** VERIFIED für tatsächliche Lints/Copyright/AST-/Notice-Anwendung; Gesamt-AP06 folgt V4-016. **Git-Commit:** `test(quality): resolve lint and copyright checks`. **Betroffene Dateien:** 22 Python-Dateien und zentrales Protokoll; genaue Diff-/AST-Liste unten in 16.4. Root-/Paket-LICENSEs/Manifeste/Setupmetadaten unverändert.

#### Ausgangssituation

Eingang im frischen Apt/Humble-Container reproduziert: 49 Tests, 45 PASS/2 Flake8 FAIL/2 Copyright SKIP. Flake8 166 Planner-/150 Preprocessorbefunde, bestehende und frühere V4-Config-/Teststyles; keine alleinige Zuschreibung an historische Source. Direkter Copyrightlauf am Eingang 13/3 Fehler: traditioneller Humble-Parser erkennt alte eigene SPDX-only/no-year-Header nicht. OSRF-Header gültig, leere Marker kein Fehler.

#### Ziel der Änderung

Bestehende Linter regulär grün ohne globale Threshold-/Ignore-Abschwächung, Copyright-Skips entfernen, Original-Fremdnotices und AP01-SPDX bewahren. Keine Algorithmen oder ROS-Verträge ändern.

#### Technische Umsetzung

Temporärer Containerformatter autopep8 1.6.0, nur E/W und max-line-length99/aggressive0. Manuelle AST-erhaltende Restumbrüche für Strings/Importlisten/Comprehensions/Kommentare. Drei unbenutzte Standardbibliotheksimports math/struct/os entfernt, unbenutzte except-e-Bindung im Follower entfernt, f-Präfix eines konstanten Logstrings im Analyzer entfernt (text-/berechnungsidentisch). Diese kleinen Ausnahmen vom exakten AST-Dump separat normalisiert, sonst AST-Gleichheit. 18 bereits zugeordnete eigene Dateien ergänzen unveränderten traditionellen Apache-Hinweis mit Copyright2026Bastian, vorhandene Namens-/SPDX-Zeilen erhalten. Zwei neue eigene Outputdateien SPDX hinter vollständigem Lizenzblock anordnen, damit Humble-Parser die License erkennt. Beide Copyright-Skipdecorators entfernen; sechs originale OSRF-Copyright-/Lizenzblöcke unverändert, keine Fremdrechte überschrieben.

#### Begründung

Ein gültiger SPDX-Identifier allein wird vom traditionellen ament_copyright 0.12-Parser nicht unterstützt; ergänzender gleichlautender Standardhinweis ermöglicht echten Test statt Skip. Stilfehler beheben, nicht globale Regeln lockern. Unbenutzte Standardbibliothek/Exceptionbindung und konstanter Logfstring ändern weder Zahlen noch ROS-Verhalten.

#### Verifikation

Vor Anwendung an Containerkopien beide Pakete je pytest -k "copyright or flake8 or pep257" Exit0: 3 passed, keine Skips (0.36/0.38s), 43 bzw.10 Funktionsfälle bewusst für diesen Lintlauf deselected und später vollständig geprüft. Erste Formatterprobe ließ 16/4 Lintbefunde sowie zwei Licenseunknowns neuer SPDX-vor-Notice-Dateien zurück, gezielt korrigiert, keine Ignore-Endlösung. AST-Vergleich vor/nach normalisiert ausschließlich drei Standardimporte, die tote Exceptionbindung, konstanten fstring und die zwei Skipdecorators; übrige Funktionstokens/-ASTs unverändert. Alle sechs Original-Noticeblöcke byteidentisch, Root-/Paketlizenzhashes/Manifeste/Setupaufrufe geschützt. Vollständige native Gesamtsuite folgt V4-016; hier kein pauschaler AP06-/Coverageabschluss.

#### Ergebnis

Beide Qualitätsgates bestanden, alle 22 angewandten Dateien bytegleich zu geprüften finalen Kopien; alle Pythondateien parsebar, sechs Noticeblöcke geschützt, exakte Commit-Whitelist. AP06 IN PROGRESS bis Gesamtsuite/Installregressionen; keine Hardware/CI/Multi-Distrobehauptung.

**Abgeschlossener Commit:** `bb578b36fc6ac72dddb043f35a474fe15c25da30`.

#### Auswirkungen

Keine neue Lizenzwahl/Versions-/Dependency-/ROS-Namens-/Parameter-/Algorithmusänderung. B09-B13-Interfaceprobleme bewusst für AP05 erhalten, keine kosmetische Korrektur als neue Planung ausgeben.

### V4-016 - Source-freie Installation und vollständige Regressionen nachweisen

**Datum:** 14. Oktober 2026 (Europe/Berlin). **Arbeitspaket:** AP04/AP06, begleitend AP08/AP10. **Status:** VERIFIED für den beauftragten Humble-Installations-/Testumfang. **Git-Commit:** `test(install): add clean installation regression coverage` (eigener Commit über den eindeutigen Subject/Parent auflösbar; SHA nicht selbstreferenziell im selben Commit erzeugbar), Parent bb578b36fc6ac72dddb043f35a474fe15c25da30. **Betroffene Dateien:** neuer test_installation.py, README.md, INSTALL.md, docs/CONFIGURATION.md, docs/KNOWN_ISSUES.md, beide Paket-README.txt und dieses Protokoll.

#### Ausgangssituation

Vorher Shareauflösung/Outputpfad korrigiert, 40 bestehende Configfälle, zehn neue Outputfälle und sechs Lints getrennt bestanden. Vollständiger Copy-/Source-free-/Gesamtnachweis fehlte. Neuer Eintrag wurde vor Testimplementierung als IN PROGRESS angelegt, jetzt mit tatsächlichen Ergebnissen abgeschlossen.

#### Ziel der Änderung

Dauerhafte Regressionen für installierte Standard-/Overridekonfiguration, Robotprofile, Pfade, Ressourcen, sieben Entry-Points, vier Launches und echtes readonly-PCD-I/O; alle Bestandsfälle erhalten. Zwei leere Copy-Workspaces und eigener Source-freier Prozess; keine API-/CI-/Hardwarearbeit.

#### Technische Umsetzung

27 parametrisierte Installed-Testfälle mit neutralem cwd und tatsächlichen installierten Modulursprüngen. Zwei frische Workspaces /work/final2 und /work/final3 in vollständig versorgtem isoliertem Humble-Container, Build ohne --symlink-install und ohne alte R3D-Overlays. Ausführung als r3dtest UID1000. Zweiter frischer Container mit demselben gepinnten Image, eigener echter rosdep-Installation aus zwei Manifestkopien, nur readonly-Installbaum am ursprünglichen Installprefix, readonly-Testdateien/Manifestkopien/temporäre Tools und getrennten Ergebnissen. Kein Repository-/Source-/Buildworkspace-Mount dort; /r3d-source und /work/final1/src bis /work/final3/src fehlen nachweislich.

#### Begründung

Discovery/Import, Nodeinitialisierung und funktionale Ausführung werden getrennt. Readonly-Installation und ordinary-user-DAC beweisen tatsächliche Quellen-/Schreibortunabhängigkeit; kein root-Pseudobeweis. Quelldaten synthetisch erzeugt, keine alten Karten zurückgebracht.

#### Verifikation

Beide Copy-Builds Exit0, jeweils colcon test Exit0 und test-result Exit0: 86 PASS, 0 FAIL, 0 ERROR, 0 SKIP. 43 Bestandsfunktionen (einschließlich tatsächlicher Launchkombinationen/Odometry/action), zehn neue Outputfälle, 27 Installed-Fälle und sechs aktive Lints. Im zweiten Source-freien Container zusätzlich 37 PASS/0 FAIL/0 SKIP (27 Installed plus zehn Output), pytest Exit0. Alle 26 Keys weiterhin gültig; rosdep install/check dort Exit0. Ressourcen: zwei Manifeste, zwei LICENSEs, zwei Amentmarker, sieben Scripts/Importe, vier Launches, drei YAMLs, null PCDs. Die drei YAMLs umfassen zentrale Konfiguration, Go2W-Profil und den weiterhin nicht geladenen Legacy-Nav2-Fragment; nicht drei aktive Konfigurationen.

Vier `ros2 launch ... --show-args` erfolgreich, kein Followerstart daraus. Alle sieben Nodekonstruktoren mit temporären Inputs/Overrides initialisiert und zerstört; Commandtopic /r3d_install_test/cmd_vel, kein Follower-spin/control_loop. Analyzer tatsächlich als installiertes Console-Script mit readonly Input erfolgreich (Exit0); vorhandener Output oder ungültige PCD jeweils Exit1, bestehende Daten unverändert. Weitere umfassende Navigation-/Hardware-/GUItests nicht daraus abgeleitet.

Erster Vollversuch /work/final1: Build0, colcon test0, aber test-result1 mit 85PASS/1FAIL/0SKIP. Ursache ausschließlich neuer Testhelper: `AttributeError: module 'rclpy' has no attribute 'node'`; expliziter `from rclpy.node import Node` korrigiert, Produktionscode dafür unverändert. Zweite/dritte frische Workspaces danach beide fehlerfrei. Colcon test Exit0 allein reicht ausdrücklich nicht als erfolgreiche Suite.

33 Share-Ressourcenkeys in beiden Builds identisch; 31 Inhalte byteidentisch. Zwei generierte package.sh enthalten erwartete /work/final2 gegenüber /work/final3 Prefixe, nach ausschließlich dieser Prefixnormalisierung identisch. Alle 20 installierten Pythondateien byteidentisch: 18 Paketmodule/Launches einschließlich leerer Marker sowie zwei generierte Colcon-Setuphelper. Initialer pauschaler Hashgleichheitscheck deshalb nicht bestanden; keine Bitreproduzierbarkeit sämtlicher Artefakte behauptet. NetworkX-np.int-/ament-Deprecations bleiben sichtbar; frühere SciPy/NumPy-Kompatibilitätswarnung fehlt. Relevante vollständige Kommandos/Ausgaben und konsolidierte T65-T86 in 16.5.

#### Ergebnis

AP03 VERIFIED Humble/Jammy; AP04 VERIFIED gemäß ursprünglichen Copy-/Sourcefrei-/Ressourcen-/Config-/Outputkriterien; AP06 VERIFIED für den bearbeiteten Umfang, Bestandsfälle und neue Regressionen inklusive aktivierter Copyrighttests. Keine Kriterienabschwächung, keine Gruppenabschaltung, keine SKIP-als-PASS-Wertung. Allgemeine Coverage/Algorithmus-/API-/QualityLevel-/CI-/Jazzy-/Hardwareabnahme bleibt offen. Benutzeranleitungen auf tatsächliche Prüfungen und regulären Copy-Build aktualisiert, nur vorhandene Dokumente.

#### Auswirkungen

Manifestbytes/Paketnamen/0.0.1/Apache-2.0 unverändert; neue Tests keine ROS-API-/Algorithmusänderung. Historische Einträge und PDF erhalten. Zwei eigene Testcontainer nach Sicherung relevanter Ergebnisse gestoppt/entfernt; keine vorher vorhandenen Images gelöscht, offizielles gezogenes Image behalten. Host-Apt/pip/Conda/NVIDIA/ROS/Dockerkonfiguration unverändert. Kein Push/Release/Hardwarebetrieb; AP05/AP07 nicht begonnen.

### V4-017 - AP05-Schnittstelleninventar und konkrete Migrationsentscheidung

**Datum:** 14. Oktober 2026. **Arbeitspaket:** AP05, begleitend AP06/AP08/AP10. **Status:** Analyse COMPLETED; inkompatible Migration BLOCKED bis gesonderter Nutzerfreigabe, übrige AP05-Analyse/kompatible Korrekturen freigegeben. **Git-Commit:** `docs(ros): inventory interfaces and propose migration`. **Betroffene Datei:** ausschließlich dieses zentrale Protokoll.

#### Ausgangssituation

Sauberer V4-HEAD22be9830e8d783a9a5a9dffc62e3ddfe223c179c. Keine zusätzlichen fremden Änderungen/Worktrees; Baseline c65642f weiterhin Vorfahr. Alle bisherigen Ereignisse V4-001..016 und vollständiges bereits bearbeitetes Protokoll gelten als historische Nachweise. Frühere86/37Tests werden nicht als neue Ausführung ausgegeben. Geschützte Hash-/Ref-/Gitconfigdaten erneut vor Änderungen gesichert, PDF identisch. Auftrag erlaubt AP05..AP10 in Reihenfolge, verbietet Breaking Changes ohne konkrete Migrationsstrategie und separate Freigabe.

#### Ziel der Änderung

Tatsächliche Node-/Publisher-/Subscriber-/Service-/Action-/Parameter-/TF-/QoS-Verträge erfassen. Konkrete Nachrichtensemantikfehler von optionaler Namingpräferenz trennen; narrow-Funktion weder löschen noch in einem anderen geometrischen Standardfeld verstecken. Entscheidungsfähige Strategie vor Produktionsänderung festhalten.

#### Technische Umsetzung

Statische Untersuchung aller eigenen Node-/Launch-/Loader-/Odometrymodule, parameterbezogener YAMLs, bestehender Tests und Manifeste. Inventar und Risikomatrix in Kapitel17. Humble ComputePathToPose und sensor_msgs_py offiziell neu gelesen; in tatsächlich eingesetztem Container zusätzlich zu prüfen. Keine Algorithmen/API/Manifeste geändert. Neue Planung nach originaler Phasenreihenfolge, keine Veröffentlichung.

#### Begründung

Quaternionflagwriter im Planner und decoder im Follower sind öffentlich gekoppelt: neue geometrisch korrekte Orientierungen machen den alten z>0.5-Decoder unzuverlässig. Ein normalisiertes Flag bleibt eine willkürliche geometrische Kodierung. Bloße Namens- oder QoS-Präferenzen rechtfertigen keinen stillen Defaultbruch.

#### Verifikation

Statisches AST-/Sourceinventar, konkrete Quellen/Zeilen nach17.1/17.2. Git/Branch/Ref/Baseline/PDF vor Änderungen geprüft. Kein neuer colcon-/Runtime-/CI-/Hardware-PASS behauptet. Offizielle Humble-Action besitzt path und planning_time, aber keine error_code-Felder und kein Feedbackpayload; APIstand später aus installiertem Paket bestätigen.

#### Ergebnis

Migration ist konkret vorbereitet und noch nicht implementiert. Verbleibende Freigabe betrifft Quaternion/narrow und den strengeren Follower-Eingangsvertrag. Kompatible PointCloud2-Feldkorrektur kann getrennt getestet werden. AP05 IN PROGRESS, AP06 bisheriger Umfang VERIFIED, spätere neue Gesamtabnahme offen. AP07/AP09 noch nicht begonnen; AP08/AP10 begleiten ohne Releaseaktion.

#### Auswirkungen

Nur Dokumentation, keine öffentliche ROS-Schnittstelle oder Controllerfunktion geändert. Keine Änderungen an V1/V2/V3/main/Remotes/PDF/Lizenztexten, keine externen Projekte, kein Push/Release/Hardwarebetrieb. R3D_null bleibt ausgeschlossen.

### V4-018 - PointCloud2-Feldlayout und organisierte Daten korrekt interpretieren

**Datum:** 14. Oktober 2026. **Arbeitspaket:** AP05/AP06, AP08. **Status:** VERIFIED für PointCloud2-Korrektur und aktuelle Regressionen; AP05 insgesamt IN PROGRESS bis Migrationsentscheidung. **Git-Commit:** `fix(ros): decode PointCloud2 fields and row padding`. **Betroffene Dateien:** neuer eigener cloud.py/test_pointcloud.py, LocalFilter-Dekoder/Outputhelper, Follower-Clouddekoder, INSTALL.md, docs/ARCHITECTURE.md, docs/CONFIGURATION.md, docs/KNOWN_ISSUES.md, r3d_planner/README.txt, README.md und Protokoll.

#### Ausgangssituation

I02: LocalFilter liest gepacktes XYZ12 unabhängig von fields/row_step/endian. Follower verwendet Humble read_points ohne explizite Rowpaddingbehandlung. Filteremptyoutput hat keine XYZ-Felder. narrow-/Followerfrischemigration M01/M02 bleibt unimplementiert bis Freigabe.

#### Ziel der Änderung

Alle gültigen skalaren numerischen XYZ-Layouts korrekt lesen, nichtgeometrische Felder ignorieren, row_step/point_step/Endian beachten und NaN/Inf ungeachtet is_dense ausschließen. Fehlende/malformed Felder nicht als freie Bahn publizieren. Ausgabevertrag und Filterklassifikationslogik erhalten.

#### Technische Umsetzung

Implementiert: sensor_msgs_py.dtype_from_fields für typisierte Felder; strided readonly-NumPyview und explizite Endian-Dtype statt inplace-byteswap. Nur XYZ-Array materialisieren, keine Kopie aller Zusatzkanäle; finite-Maske. Validierung Dimensions-/Buffer-/Feldgrößen, Metadaten auch bei Emptyoutput. Anonyme/Array-Zusatzfelder erlaubt, skalare numerische XYZ erforderlich; float32/float64 und gemischte Integer/Float korrekt. Ein XYZ-Zielarray statt temporärer Einzelkanalkopien; nur bei nichtfiniten Punkten zusätzlicher Selektionsoutput. Vollständige Dichte-/Feldmetadaten auch für leere Ausgaben. Beide internen Cloudconsumer nutzen gemeinsamen Decoder. Keine Frame-/QoS-/Topic-/ROS-Typ-/Controlleränderung.

#### Begründung

Humblehelper allein deckt organisierte Rowpadding-Wolken nicht zuverlässig ab. Verwendete API wiederverwenden, eigenen Stridelayoutteil testen; keinen fremden Code kopieren. numerische XYZ-Datentypen erlauben, vor Geometrieoperationen mindestens float32, sonst Integeroverflow vermeiden.

#### Verifikation

Tatsächliche Humblemessages/Python3.10.12/Ubuntu22.04.5 im isolierten Apt-Container. 83 neue Cloudfälle: 64 Layout-/Endian-/Organized-/Rowpadding-/dense-Kombinationen,8Malformedfälle,6NaN/Inf+dense-Fälle,1MixedNumeric,2Empty/Outputmetadata,1echter Filterconstructor mit äquivalenten Layoutoutputs/invalid-no-publish,1anonymous/array-extra-fields. Alle Inputbytes unverändert. Beide Consumer nutzen denselben Decoder; Produktions-Filtermathematik und Follower-control_loop AST exakt zum Eingang. Keine Message-Typ-/Topic-/Parameter-/Frame-/QoS-/Controllerregel geändert.

Frische Copy-Workspaces /work/cloud6 und /work/cloud7, separate Domains213/215, jeweils list/build/test/test-result Exit0:171PASS/0FAIL/0ERROR/0SKIP (86Bestandsfälle+83Cloud+2V4-019-Helperfälle). Alle sechs Lints aktiv/PASS. Zweiter frischer Apt-Container sourcefrei mit readonly-Install unter /work/cloud6/install; rosdep install/check Exit0, 120Runtime-/Output-/Cloudtests PASS/0FAIL/0SKIP als UID1000, pytest Exit0. Installierte Module und Testkopien beider Workspaces bytegleich zu finalem Code; keine installierten PCDs.

Fehlversuche erhalten: cloud1=166PASS/2LintFAIL/0SKIP (7Flake8+D213); cloud2=168PASS/1Flake8FAIL/0SKIP; cloud3=168PASS/1Flake8FAIL/0SKIP (fehlerhafte erste Einrückungskorrektur). Finale gezielte Lints danach0. cloud4=168PASS/1bestehender CLIqueryFAIL/0SKIP, Lints/Cloudfälle allePASS; V4-019 ergänzt begrenzte Readinessquery und vollständige Diagnostik. cloud5 mit altem Helper in neuer Domain169PASS/0FAIL/0SKIP, keine absolute Flakinessfreiheit daraus abgeleitet. Abschließende cloud6/7 inklusive Helper beide171PASS.

Dekodiermessung mit100000synthetischen finiten Punkten,15Wiederholungen: früherer eigener packed-Decoder Median1.134ms/tracedPeak3302792Bytes; neuer packed-Decoder0.528ms/1609856Bytes; organizedRGB+Rowpadding0.569ms/1609952Bytes. GleicheXYZ-Ausgabe, Inputgrößen1.2MB bzw.3.2016MB, Output1.2MB. Tracemallocpeak ohne gehaltenen Input, kein gesamter RSS-/native-Library-/Roboterperformancebeweis und kein neuer A*-Algorithmusbeitrag. Relevante Kommandos/Ausgaben/T87..T96 in17.5.

#### Ergebnis

PointCloud2-Umfang VERIFIED, neue83Fälle und alle86Bestandsfälle erhalten, begleitende2Testhelperfälle bestanden. Bestehende Benutzeranleitungen gezielt aktualisiert. M01/M02-Freigabe bleibt offen; Path/narrow/Followerframe/Frische und weitere AP05-Arbeit nicht implementiert. Kein AP05..AP10-Gesamtabschluss.

#### Auswirkungen

Kompatible Interpretation gültiger PointCloud2-Eingaben, striktere explizite Zurückweisung kaputter Buffer; keine Legacy-narrow-/Stoppolicy-/Frame-/Namens-/Paketversionsänderung. Filtermathematik/Schwellen erhalten, Inputbytes unverändert; vorhandene86Fälle nicht löschen/skippen.

### V4-019 - Begrenzte Parameterbereitschaft im bestehenden Launchtest prüfen

**Datum:** 14. Oktober 2026. **Arbeitspaket:** begleitendes AP06, AP05-Abnahme. **Status:** VERIFIED für begrenzte Parameterabfrage/Testhelper und frische Vollsuite; neue AP05-Migration separat offen. **Git-Commit:** `test(ros): bound parameter discovery retries`. **Betroffene Dateien:** bestehender test_configuration.py und zentrales Protokoll; keine Produktion.

#### Ausgangssituation

cloud4 Copy-Build0, 169Tests/168PASS/1FAIL/0SKIP: bestehender test_real_launch_restart_and_all_components scheitert mit CalledProcessError bei ros2 param dump /r3d_rviz_interface --no-daemon --spin-time2 (Exit1). Alle83 neuen Cloudfälle und6Lints bestanden. Nodegraph zuvor korrekt; Log zeigt gestartete Nodes und SIGINT-Shutdown des Testcleanup, keine bewiesene Produktions-/Middlewareursache. Bisher check=True verlor stdout/stderr in der Assertion. Discoverytiming als plausible Hypothese, nicht abschließend bewiesen.

#### Ziel der Änderung

Nodegraphsichtbarkeit nicht als sofortige CLI-/Servicebereitschaft behandeln; drei begrenzte echte Abfragen erlauben, bei anhaltendem Fehler aussagekräftiges stdout/stderr liefern. Erfolgs-/Parameter-/Startup-/Schutdownassertions und alle86Bestandsfälle erhalten, keine Gruppenabschaltung.

#### Technische Umsetzung

Implementiert: privater Testhelper _parameter_dump(remote), identisches daemonfreies CLI/Spin2/Timeout12, höchstens3Versuche mit0.2sPause; ausschließlich bei NichtnullExit erneut. Nach dritten Fehler Assertion mit letzter Ausgabe. Testhelper unitgetestet: transienter NichtnullExit->echtesResultat, permanente Fehler->Assertion/exakt3calls. Produktionsnodes/algorithms/topic/Parameter unverändert.

#### Begründung

Begrenztes Warten auf tatsächliche CLIabfrage ergänzt native Discoverybeobachtung, ohne inhaltliche Assertions oder Timeouts unbegrenzt zu lockern. Ist keine Reparatur einer behaupteten ROSMiddlewareursache. Testharness bekommt eigene V4-ID, nicht als neue Plannerfunktion darstellen.

#### Verifikation

Ausgeführt: zwei Helperfälle für transiente/permanente CLIfehler; frischer Workspace /work/cloud6, Copy-Build0, colcon test0, test-result0: 171PASS/0FAIL/0ERROR/0SKIP. Alle86Bestandsfälle plus83Cloudfälle plus2Helperfälle. Dauerfehler-Unitassertion prüft3Queries und erhaltene CLIfehlerausgabe, erfolgreiche zweite Antwort wird inhaltlich geprüft. Zwei neue Blankline-Lintdiagnosen korrigiert; abschließender gezielter Flake8check0 und Gesamt-Flake8/PEP257/Copyright jeweils PASS. Frühere cloud4-CLIfehler und cloud1..3 Stilfehlversuche bleiben dokumentiert, kein Umschreiben als PASS.

#### Ergebnis

Begrenzte Readinessquery im Testwerkzeug VERIFIED; alle vorhandenen Inhalte/Schalter/Nodes/Parameterassertions erhalten. cloud5 mit unverändertem altem Helper in neuer Domain bestand ebenfalls169Tests; das beweist weder die exakte Ursache des cloud4-Fehlers noch eine absolute Flakinessfreiheit. Die Änderung ergänzt begrenztes Warten und bessere Diagnostik statt Produktionsrefactoring. M01/M02-Migrationsfrage bleibt offen, keine AP05-Gesamtabnahme/CI-/Releasebehauptung.

#### Auswirkungen

Nur Testwerkzeug plus Protokoll, kein öffentlicher ROS-Vertragsbruch. Historische86Tests weder gelöscht noch geskippt; zwei sinnvolle neue Fehler-/Erfolgsregressionen.

### V4-020 - M01 – Geometrischer Path und atomare narrow-Metadaten

**Datum:** 15. Oktober 2026 (Europe/Berlin). **Arbeitspaket:** AP05/AP06, AP03/AP04/AP08 begleitend. **Betroffene Dateien:** neues r3d_interfaces, planner manifest/pathbuilder, planner/follower, neue Regressionen und vorhandene Dokumentation. **Status:** VERIFIED für M01-Umfang; M02 nicht implementiert. **Git-Commit:** `fix(ros): replace quaternion flags with atomic path metadata` (eigener Commit enthält diesen Eintrag).

#### Ausgangssituation

V4-Eingang11d594aa5dca45293d14aed185a07a21fcb16d8e, sauber; bisherige V4-001..019 unverändert historisch. 171/120 vorherige Tests nicht als aktueller Nachweis nach Codeänderung ausgeben.

#### Ziel und Freigabe

M01 ausdrücklich im Chat freigegeben am15.10.2026; M02 ausdrücklich zurückgestellt, daher kein neuer Hindernistimeout/keine Sensor-zu-Basis-TF-Stoppolicy. Sonstige AP05..AP10-Phasen weiterhin nach ursprünglichem Auftrag autorisiert, keine erneute pauschale Freigabe nötig.

#### Technische Umsetzung und Begründung

Freigegebene Migration17.4/M01: eigenes ament_cmake/rosidl-Paket mit nav_msgs/Path path und bool[] narrow. Standard-/global_path und Actionresult behalten Typ/Positionen, Quaternionen haben echte normierte XY-Tangentenheading. Gemeinsame PathWithMetadata-Nachricht vermeidet Pairing zweier asynchroner Kanäle, reliable/transient-local/depth1 für Latejoin. Follower prüft Länge/Frames/finite Geometrie/Einheitsquaternionen, ersetzt Path+Flags gemeinsam und liest keine Orientationflags mehr. M02 explizit nicht umsetzen; optionalerFilter-Zusammenhang und Vorschlag werden separat dokumentiert. Alle drei Pakete gemeinsam über rosdep/colcon bauen/installieren; vorhandene171Tests erhalten und neue Schema-/Metadaten-/ROS-/Latejoin-/Narrow-Regressionsfälle ergänzen. Grundlage für Interfacegenerierung: offizielles Humble Custom-ROS2-Interfaces Tutorial, rosidl_default_generators/runtime und nav_msgs explizit deklarieren.

#### Verifikation und Ergebnis

Tatsächliche Humble/Jammy-Installation für alle drei Pakete mit rosdep install/check ohne skip: Exit0. Normaler Copy-Build /work/m01_2 aller drei Pakete: Exit0; colcon test und test-result Exit0, Summary191Tests/0errors/0failures/0skipped. Davon186Pythonfälle (171Bestand+15M01) und5CTest/Lintfälle des neuen CMakepakets. Erster Zwischenlauf ohne erweiterte CMakechecks/nativePaircase185PythonPASS. Native serialisierte Pub/Sub-Vergleiche: /global_path == PathWithMetadata.path == Actionresult.path, flagsFalse/True/False auf synthetischer klassifizierter PCD. QoS-Latejoin, realer Followerconstructor ohne Motiontimer, Narrowgeschwindigkeit trotz gleicher geometrischer Headingquaternionen, Neuplanung/clear/invalid-Daten, Header-/Stamp-/Quaternionvalidierung, generiertes Schema/CDRroundtrip/Paketlicense/Message-Share geprüft. Alle171Bestandsfälle erhalten. M01-Nachrichtenbau linear in Wegpunktanzahl, Graph/A*-AST unverändert. Root-/altePaketlizenzen unverändert, neue identische Paketkopie installiert. M02-Hindernisfrische/TF-/Stopregeln nicht eingeführt; Test prüft fehlenden obstacle_timeout_sec-Parameter. Direkte erste Copyright-CLIprobe prüfte0Dateien und ist kein Lizenz-PASS; tatsächliche CMake-/Pythonlintersuite bestand. Vollständiger Source-freier Schlussnachweis nach weiteren freigegebenen Änderungen erneut auszuführen; vorherige120Tests sind historisch.

#### Auswirkungen

Kein Push/Release/Historyrewrite, keine Änderungen an V1/V2/V3/main/Remotes/historischerPDF. Bestehende Paketversionen0.0.1 und Apache-2.0 erhalten. Keine Algorithmen neu entwickeln; konkrete ROS-Vertragskorrekturen separat testen.

### V4-021 - M02 – Optionalen Filter und konfigurierbare Überwachung untersuchen

**Datum:** 15. Oktober 2026 (Europe/Berlin). **Arbeitspaket:** AP05/AP08 Analyse, M02 nicht zur Implementierung freigegeben. **Betroffene Dateien:** nur zentrales Protokoll. **Status:** VERIFIED als angeforderte Analyse/Vorschlag; Implementierung NICHT FREIGEGEBEN. **Git-Commit:** Begleitdokumentation im M01-Commit; kein M02-Implementierungscommit.

#### Ausgangssituation

V4-Eingang11d594aa5dca45293d14aed185a07a21fcb16d8e, sauber; bisherige V4-001..019 unverändert historisch. 171/120 vorherige Tests nicht als aktueller Nachweis nach Codeänderung ausgeben.

#### Ziel und Freigabe

M01 ausdrücklich im Chat freigegeben am15.10.2026; M02 ausdrücklich zurückgestellt, daher kein neuer Hindernistimeout/keine Sensor-zu-Basis-TF-Stoppolicy. Sonstige AP05..AP10-Phasen weiterhin nach ursprünglichem Auftrag autorisiert, keine erneute pauschale Freigabe nötig.

#### Technische Umsetzung und Begründung

Expliziter Nutzerauftrag15.10: M02 zuerst hinsichtlich optionalem lokalenFilter untersuchen und konfigurierbare Timeout-/TF-/Stopstrategie vorschlagen. Komponentenfalse ist weiter erlaubter Offline-/externerSensorworkflow; zwingende globale Filteraktivierung würde diesen Vertrag brechen. Follower läuft nur separat, daher Überwachung am Follower konfigurieren, nicht Planner/Preprocessing an Hindernisquelle koppeln. Keine neuen Monitorparameter oder Stoppolicy in Source/YAML implementieren; konkreter Vorschlag in18.2.

#### Verifikation und Ergebnis

Statischer Abgleich launching.py/configuration.py/Follower: local_filter ist optional, Follower wird separat gestartet, kein Pflichtmonitor vorhanden. Konkreter Vorschlag18.2 mit enabled=false Legacydefault, required/wait/clear/blocked/stale/TF-/Clockfehlerzuständen, externemPublisher bei Filterfalse, Bounds und Testplan dokumentiert. Keine neuen Monitorparameter, TF-Transformationen oder Timeout-/Stopbedingungen implementiert; keine technische Sicherheitsfreigabe behauptet.

#### Auswirkungen

Kein Push/Release/Historyrewrite, keine Änderungen an V1/V2/V3/main/Remotes/historischerPDF. Bestehende Paketversionen0.0.1 und Apache-2.0 erhalten. Keine Algorithmen neu entwickeln; konkrete ROS-Vertragskorrekturen separat testen.

### V4-022 - Action – Fehlerzustände, Cancel und tatsächliche Humble-Resultfelder

**Datum:** 15. Oktober 2026 (Europe/Berlin). **Arbeitspaket:** AP05/AP06. **Betroffene Dateien:** r3d_pcd_path.py und neue Actionregressionen; Protokoll. **Status:** VERIFIED für dargestellten Humble-Actionumfang. **Git-Commit:** `fix(action): validate results and support cooperative cancellation`.

#### Ausgangssituation

V4-Eingang11d594aa5dca45293d14aed185a07a21fcb16d8e, sauber; bisherige V4-001..019 unverändert historisch. 171/120 vorherige Tests nicht als aktueller Nachweis nach Codeänderung ausgeben.

#### Ziel und Freigabe

M01 ausdrücklich im Chat freigegeben am15.10.2026; M02 ausdrücklich zurückgestellt, daher kein neuer Hindernistimeout/keine Sensor-zu-Basis-TF-Stoppolicy. Sonstige AP05..AP10-Phasen weiterhin nach ursprünglichem Auftrag autorisiert, keine erneute pauschale Freigabe nötig.

#### Technische Umsetzung und Begründung

Konkrete Actiongrenzen: kein Cancellationcallback/SingleThreadexecutor, fehlende Finiteposevalidierung, planning_time nie gesetzt. Additiver CancelResponse.ACCEPT, kooperative Prüfung in bestehender A*-Schleife ohne geänderte Kosten/Heuristik/Topologie; ReentrantActioncallbackgruppe und4Threadexecutor für Bearbeitung von Cancel während Planung. Poseframe/finitePosition/Quaternion prüfen, Fehler abort/emptyResult, Erfolg succeed, Cancellation canceled ohne neue Pfadpublikation. Tatsächliches Humble-Result path+planning_time setzen, kein erfundenes error_code-/Feedbackfeld. planner_id bleibt zur Rückwärtskompatibilität wie dokumentiert akzeptiert/ohne Pluginwahl, insbesondere kein stiller Reject bisher akzeptierter IDs. Fehlplanung/Cancel invalidiert keine zuvor ausgegebenen Pfade und ist kein Roboterstopbefehl; diese Grenze dokumentieren. Kein M02.

#### Verifikation und Ergebnis

Frischer Copy-Build /work/action1 mit allen drei Paketen Exit0; colcon test/test-result Exit0:205PASS/0FAIL/0ERROR/0SKIP. 191bisherige Gesamtfälle erhalten,14neue Actionfälle. Native ActionClient Tests für3Planner-IDs mit jeweils wiederholten Erfolgen;9Fehlerfälle (Frame/nan/Quaternion/Startframe/fehlendePose/stalePose/fehlendeTF/disconnected/emptyPath) jeweilsABORTED/empty; Cancellation während künstlich verlängerter aktiver Execute erreichtCANCELED, echte A*-Schleife zusätzlich kooperativ geprüft. Resultplanungstime>0 und realeSchemafelder geprüft; M01-Pub/Sub-Paarung/Narrow-/Copyright-/Lintfälle unverändert bestanden. Begrenzte4Worker, keine unbeschränkte Concurrency-/Echtzeitgarantie; altePfadpublikation wird bei Fehler/Cancel nicht widerrufen. Logs/xUnit /tmp/r3d-v4-release/results/action1-*, keine Hardware/Hoständerung. Alle AST-basierten Kosten/Heuristik/Graph-/Klassifikationsberechnungen außer optionalem Cancelcheck erhalten. M02 unverändert.

#### Auswirkungen

Kein Push/Release/Historyrewrite, keine Änderungen an V1/V2/V3/main/Remotes/historischerPDF. Bestehende Paketversionen0.0.1 und Apache-2.0 erhalten. Keine Algorithmen neu entwickeln; konkrete ROS-Vertragskorrekturen separat testen.

### V4-023 - ROS-Komposition – Namespace, RViz-Framevalidierung und Sensor-QoS

**Datum:** 15. Oktober 2026 (Europe/Berlin). **Arbeitspaket:** AP05/AP06. **Betroffene Dateien:** launching.py/configuration.py/centralYAML, RViz/Odometry/Filter, neue Kompositions-/TF-/QoSregressionen und Protokoll. **Status:** VERIFIED für implementierten kompatiblen Kompositionsumfang; M02 zurückgestellt. **Git-Commit:** `fix(ros): compose namespaces and validate interface inputs`.

#### Ausgangssituation

V4-Eingang11d594aa5dca45293d14aed185a07a21fcb16d8e, sauber; bisherige V4-001..019 unverändert historisch. 171/120 vorherige Tests nicht als aktueller Nachweis nach Codeänderung ausgeben.

#### Ziel und Freigabe

M01 ausdrücklich im Chat freigegeben am15.10.2026; M02 ausdrücklich zurückgestellt, daher kein neuer Hindernistimeout/keine Sensor-zu-Basis-TF-Stoppolicy. Sonstige AP05..AP10-Phasen weiterhin nach ursprünglichem Auftrag autorisiert, keine erneute pauschale Freigabe nötig.

#### Technische Umsetzung und Begründung

Rootnamen und absolute Robotprofil-Topics bleiben unverändert. Optionaler namespace-Launchparameter plus konsistente interne Remaps für Paths/Metadaten/Marker/Action/RViz/Cliff/Stair/Map erlaubt NS-Komposition; TFframes werden nicht automatisch umbenannt. Relative Robot-Themennamen ergänzend validieren/zulassen, explizite absolute Namen bleiben global. RViz prüft map-Frame/finiteAuswahlen/Quaternionen, normalisiert nur gültige Quaternionen und begrenzt Actionserver-Warten durch optionalen action_server_timeout_sec=1.0 (alte YAMLs kompatibel). Keine konkurrierenden TF-Owner hinzufügen; Odometrymap_pose verwirft nichtfiniteTFtranslation. LiveCloudinput SensorDataQoS/BEST_EFFORT akzeptiert best-effort und reliable Producer, bestehende OutputQos und Odometry-/MapQos erhalten. Follower-SensorTF und Hindernisfrische bleiben ausdrücklich M02 und werden nicht geändert.

#### Verifikation und Ergebnis

Frische dreiPaket-Copy-Builds in /work/compose3 und compose4 jeweils0, Tests/test-result0. compose3:224PASS/0FAIL/0SKIP; zusätzlicher echter ROSRemappingfall danach compose4:225PASS/0FAIL/0ERROR/0SKIP, Domains225/226, UID1000/localhost/FastDDS. 20neue Kompositionsfälle gegenüber205Actionstand:4Topic-/Timeoutconfig,4RVizfaults,8TF/Odometry (statischeTF gültig, missing/stale/nonfinite/invalidQuaternion/futurePose/invalidPose/wrongFrame),2nativeCloudpublisher-QoS,1echter namespacedLaunch samtAction/Path und1explizites nativeTopicremapping. Alle191M01-/205Action-/171früherenFälle erhalten. M02-Cmd-/Inputfrische unverändert.

Fehlversuche compose1:222PASS/2FAIL/0SKIP (100Zeichen Testdekoration und bestehender Rootgraphfall meldet extraRViz); compose2:223PASS/1FAIL/0SKIP. Rootassertion jetzt korrekt root-namespacespezifisch, unverändert strikte Komponentenliste. Verbliebene Kontamination ging mit ersetztem echtemRVizActionclient einher: Humble Node.destroy_node zerstört create_client-Einträge, aber keine Actionwaitables. Test zerstört echtenActionclient ausdrücklich vor Mockersetzung; compose3 danach allePASS, compose4 erneutPASS. Keine Rootassertion entfernt/gelockert, kein globaler DDS-/ROSdaemon-/Produkteingriff. Ein fehlerhafter zwischenzeitlicher Testzeilenumbruch wurde gezielt vor Vollsuite vom Linter abgefangen/korrigiert, nicht als Suite-PASS ausgegeben. Kein Testskip/Regelignore. README/Config-/Architektur-/KnownIssues aktualisiert.

#### Auswirkungen

Kein Push/Release/Historyrewrite, keine Änderungen an V1/V2/V3/main/Remotes/historischerPDF. Bestehende Paketversionen0.0.1 und Apache-2.0 erhalten. Keine Algorithmen neu entwickeln; konkrete ROS-Vertragskorrekturen separat testen.

### V4-024 - AP07 – Reproduzierbare Humble-CI und Source-freier zweiter Container

**Datum:** 15. Oktober 2026 (Europe/Berlin). **Arbeitspaket:** AP07/AP06/AP04, AP08 begleitend. **Betroffene Dateien:** .github/workflows/ros2-humble.yml, scripts/ci/run_humble.sh und inside.sh/check.py, Protokoll. **Status:** IMPLEMENTED / NOT REMOTELY VERIFIED; lokale Reproduktion VERIFIED, AP07 insgesamt IN PROGRESS. **Git-Commit:** `ci: prepare isolated Humble build and runtime verification`.

#### Ausgangssituation

V4-Eingang11d594aa5dca45293d14aed185a07a21fcb16d8e, sauber; bisherige V4-001..019 unverändert historisch. 171/120 vorherige Tests nicht als aktueller Nachweis nach Codeänderung ausgeben.

#### Ziel und Freigabe

M01 ausdrücklich im Chat freigegeben am15.10.2026; M02 ausdrücklich zurückgestellt, daher kein neuer Hindernistimeout/keine Sensor-zu-Basis-TF-Stoppolicy. Sonstige AP05..AP10-Phasen weiterhin nach ursprünglichem Auftrag autorisiert, keine erneute pauschale Freigabe nötig.

#### Technische Umsetzung und Begründung

GitHub Actions mit Ubuntu22.04 und perSHA gepinntem offiziellem Checkoutv7.0.1/Node24; lediglich readcontents, keineCredentialpersistenz/Push-/Releaseaktion. Derselbe lokale Shellrunner startet zwei eigene nichtprivilegierte Humble-Container: Buildcontainer mitSourceReadonly, rosdepactualinstall/check für dreiManifeste, Metadata/Docstrukturprüfung, regulärer Copybuild/fullsuite/colcontest-result als unprivilegierterUser; danach Runtimecontainer nur mitreadonlyInstall/Testfiles/Manifestkopien, ohneSource. KeineHost-Apt/pip/Dockerdaemonänderung, keine sensitivenMounts oder Imagelöschung. M02nichtimplementiert. Lokaler Lauf ist ausdrücklich kein RemoteCI-PASS; AP07 IMPLEMENTED/NOT REMOTELY VERIFIED nach tatsächlichem lokalen Nachweis, ursprüngliches Remoteabnahmekriterium bleibt offen.

#### Verifikation und Ergebnis

Exakter Workflowbefehl bash scripts/ci/run_humble.sh lokal tatsächlich Exit0 ausgeführt. Zwei frisch erzeugte Container, gepinnter Humble-Image-Digest860e5379..., SourceReadonly/noprivileged/bridge/localhost/Domains231/232, unprivilegierteTests. Je echte rosdep install/check0. Metadata/XML/YAML/AST-/strukturellerDoklint0; shell bash -n beiderSkripte0; CIcheck.py Flake8/PEP2570. Normaler dreiPaket-Copybuild0/fullcolcontest0/test-result0:225PASS/0FAIL/0ERROR/0SKIP. RuntimezweiterContainer ohne/r3d-source,/work/ci/src und ohneBuildmount:169PASS/0FAIL/0SKIP, tatsächliches generiertesM01-Modul/CDR/NS/Action/QoS mit enthalten; readonlyInstall am ursprünglichen Prefix. Exports getrennt von Runtimeoutputmount; Sourcefree169 umfasst37Install/Output+83Cloud+15M01+14Action+20Komposition, nicht die restlichen56CTest/Config/Query/Lintfälle. Originalrootbranch/history unverändert. Alle eigenenCIcontainer perID entfernt, keineImages gelöscht. Logs/xUnit /tmp/r3d-ci.WPxUz4NT, Treiber /tmp/r3d-v4-release/ci-first.log. AusgabeCI_LOCAL_BUILD_AND_SOURCEFREE_PASS. Keine neue CI-Funktion durch ungetestete Herstelleractions ersetzt; ausschließlichCheckoutAction v7.0.1-Pin aus offiziellerReleasequelle geprüft, action.ymlNode24. Tatsächlicher CheckoutAction-/GitHubRunner-/RemoteCI-Lauf NICHT ausgeführt/NOT VERIFIED; kein Badge/keinPush/keinePR erzeugt. KeinActionlintlauf behauptet, YAML/Actions/Shell/Python geprüft und Dockerjob tatsächlich reproduziert. Externe NetworkX-/ament-Deprecations sichtbar, kein SciPy/NumPy-Konflikt.

#### Auswirkungen

Kein Push/Release/Historyrewrite, keine Änderungen an V1/V2/V3/main/Remotes/historischerPDF. Bestehende Paketversionen0.0.1 und Apache-2.0 erhalten. Keine Algorithmen neu entwickeln; konkrete ROS-Vertragskorrekturen separat testen.

### V4-025 - AP08 – Nutzungsverträge, Changelogs und proportionale Wartungsregeln

**Datum:** 15. Oktober 2026 (Europe/Berlin). **Arbeitspaket:** AP08/AP10 Metadata, AP06 Prüfnachweise. **Betroffene Dateien:** bestehende README/INSTALL/Architektur/Config/KnownIssues/PaketREADME, CONTRIBUTING.md/MAINTENANCE.md und3Paket-CHANGELOG.rst, Installregeln, Protokoll. **Status:** VERIFIED für dokumentierten AP08-Umfang. **Git-Commit:** `docs: align usage and maintenance metadata with V4 interfaces` (direkter Nachfolger von2dd1097; vollständige Zuordnung siehe Abschluss).

#### Ausgangssituation

V4-Eingang11d594aa5dca45293d14aed185a07a21fcb16d8e, sauber; bisherige V4-001..019 unverändert historisch. 171/120 vorherige Tests nicht als aktueller Nachweis nach Codeänderung ausgeben.

#### Ziel und Freigabe

M01 ausdrücklich im Chat freigegeben am15.10.2026; M02 ausdrücklich zurückgestellt, daher kein neuer Hindernistimeout/keine Sensor-zu-Basis-TF-Stoppolicy. Sonstige AP05..AP10-Phasen weiterhin nach ursprünglichem Auftrag autorisiert, keine erneute pauschale Freigabe nötig.

#### Technische Umsetzung und Begründung

Korrekte aktuelle Root-/Namespace-/Metadaten-/Action-/TF-/QoS-/M02-Grenzen erhalten; reale225/169Nachweise mit historischer Vorleistung trennen. Drei Forthcoming-Changelogs als ReleaseMetadaten, keine endgültigeVersion/Datum/Tag. Kurze Beitrags-/Support-/Version-/API-/ABI-/Security-/Releaseinformationen mit tatsächlichen Zusagen (Humble/Jammyamd64 getestet, keineV4Hardware-/Coverage-/QL-/RemoteCIzusage). Root9AltPYC als bekannt belassen, kein unaufgeforderter Cleanup. PaketChangelogs/InterfaceREADME als Shares installieren; keine Runtimeberechnung/Versionsänderung. StrukturellerDoclint/Metadata/Installpipeline nach Änderungen erneut prüfen.

#### Verifikation und Ergebnis

Frischer normaler Drei-Paket-Copybuild `/work/maintenance1`, UID1000/Humble/FastDDS/Domain227, build/test/test-result jeExit0: **225PASS/0FAIL/0ERROR/0SKIP**. Drei tatsächlich installierte CHANGELOG.rst bytegleich mit Source, docutils-RSTprüfung ohneWarnings; Metadaten/XML/YAML/Python/Markdownstrukturcheck PASS. README-Staleangaben zu2Paketen/fehlendenInterfaces/TODOmanifesten korrigiert; historische Protokolle bleiben datiert. Zwei anfängliche Helperaufrufe scheiterten an fehlendem check.py-Pfadargument bzw. falschem Scratchmountpfad; korrigiert erneut ausgeführt, kein fehlerhafter Aufruf als PASS. Kein spezieller umfassender Markdown-/Rechts-/API-Stabilitätsnachweis. Finale Source-freie CI-Abnahme nach Folgedokumentation folgt. Keine Hardware/Hostinstallation.

#### Auswirkungen

Kein Push/Release/Historyrewrite, keine Änderungen an V1/V2/V3/main/Remotes/historischerPDF. Bestehende Paketversionen0.0.1 und Apache-2.0 erhalten. Keine Algorithmen neu entwickeln; konkrete ROS-Vertragskorrekturen separat testen.

### V4-026 - AP09 – reale Distributionsprüfung und Open3D-Abgrenzung

**Datum:** 15. Oktober 2026 (Europe/Berlin). **Arbeitspaket:** AP09/AP03/AP06/AP08. **Betroffene Dateien:** zentrales Protokoll und aktuelle Kompatibilitätsangaben README/INSTALL/MAINTENANCE/KnownIssues. **Status:** Untersuchung VERIFIED; Gesamtkompatibilität neuerer Targets PARTIAL/BLOCKED. **Git-Commit:** `docs(compat): record native Jazzy and Lyrical investigation` (Nachfolger be44bf4).

#### Ausgangssituation

V4-Eingang11d594aa5dca45293d14aed185a07a21fcb16d8e, sauber; bisherige V4-001..019 unverändert historisch. 171/120 vorherige Tests nicht als aktueller Nachweis nach Codeänderung ausgeben.

#### Ziel und Freigabe

M01 ausdrücklich im Chat freigegeben am15.10.2026; M02 ausdrücklich zurückgestellt, daher kein neuer Hindernistimeout/keine Sensor-zu-Basis-TF-Stoppolicy. Sonstige AP05..AP10-Phasen weiterhin nach ursprünglichem Auftrag autorisiert, keine erneute pauschale Freigabe nötig.

#### Technische Umsetzung und Begründung

Aktuelle offizielle Release-/rosdep-/Docker-/REPquellen prüfen. Tatsächliche isolierte Jazzy/Noble- und aktuelle Lyrical/Resolute-Container mitreadonlySource, ohnepip/skipkeys/Hoständerungen. Installation/check/OS/API tatsächlichen Status protokollieren; fehlendeDependencies separat von API-Kompatibilität betrachten. Optional Interfacepaket allein nativ bauen/testen, ohne Gesamtplanner-Support daraus abzuleiten. Kilted/Rolling als Quellen-/Regeluntersuchung kennzeichnen, nicht ausgeführte Vollsuite behaupten. Keine genehmigungspflichtige neue Vendor-/pip-/Source-Dependencystrategie implementieren.

#### Verifikation und Ergebnis

Humble alle32externenKeys einzeln aufgelöst, Exit0. Jazzy24.04.5/Python3.12.3: volle rosdep install/check jeExit1, python3-open3d noble:null und AptCandidate none; unabhängiges Interfacepaket nativ build/test/test-result Exit0,5PASS, CDR-RoundtripPASS. APIpakete separat aus offiziellerAptquelle installiert, keinOpen3D/pip/skipKey-Gesamterfolg behauptet. Lyrical26.04.1/Python3.14.4: rosdep install/check Exit0, dreiPakete normalcopybuild Exit0; colcon test Exit5 (Pythonpakete NO TESTS RAN), test-result0 zählt nur5CMakechecks und ist ausdrücklich kein GesamtPASS. Direkter pytest jePaketcwd: Preprocessor12PASS/1Flake8FAIL, Planner206PASS/1Flake8FAIL, jeweils0ERROR/0SKIP; neueLintregeln57/95Befunde, keineFunktionsfailure. Initialer direkterTest im falschen Workspacecwd scannte Build/Install mit,1zusätzlicherCopyrightfailure jePaket war Harnessfehler und ist korrigiert; nicht als Produktfehler darstellen. GenerierteNachrichtCDR unterLyricalPASS. Keine SourcefreieLyrical-/JazzyPlanner-/Kilted-/Rolling-/Hardwarevollabnahme. ZentraleMatrix/Quellen/weitereSchritte18.8. Scratchsummaryhelper hatte zunächst nurletztenExit geprüft: LyricalExit5 bleibtFAILED unabhängig von5TestsSummary. TatsächlicheBefehlszeilen/Exits sind imProtokoll maßgeblich.

#### Auswirkungen

Kein Push/Release/Historyrewrite, keine Änderungen an V1/V2/V3/main/Remotes/historischerPDF. Bestehende Paketversionen0.0.1 und Apache-2.0 erhalten. Keine Algorithmen neu entwickeln; konkrete ROS-Vertragskorrekturen separat testen.

### V4-027 - AP10 – zielbezogene Release-Readiness und externe Gates

**Datum:** 15. Oktober 2026 (Europe/Berlin). **Arbeitspaket:** AP10/AP08. **Betroffene Dateien:** nur zentrales Protokoll. **Status:** Checkliste/Untersuchung VERIFIED; Gesamt-AP10 IN PROGRESS / Release NOT READY. **Git-Commit:** `docs(release): prepare scoped readiness and release gates` (Nachfolger b91cdb9).

#### Ausgangssituation

V4-Eingang11d594aa5dca45293d14aed185a07a21fcb16d8e, sauber; bisherige V4-001..019 unverändert historisch. 171/120 vorherige Tests nicht als aktueller Nachweis nach Codeänderung ausgeben.

#### Ziel und Freigabe

M01 ausdrücklich im Chat freigegeben am15.10.2026; M02 ausdrücklich zurückgestellt, daher kein neuer Hindernistimeout/keine Sensor-zu-Basis-TF-Stoppolicy. Sonstige AP05..AP10-Phasen weiterhin nach ursprünglichem Auftrag autorisiert, keine erneute pauschale Freigabe nötig.

#### Technische Umsetzung und Begründung

Aktuelle offizielle Anforderungen von Sourceindex/rosdep/Bloom/ReleaseRepo/Buildfarm/Debian getrennt prüfen. Drei reale Paketnamen/Manifeste/Version0.0.1/Lizenz-/Installressourcen mitV4abgleichen. Offizielle fünf aktiveROSdistribution.yaml-Dateien nurlesen, keineR3D-Namensmatches gefunden; keineweltweiteReservierung/Reviewentscheidung behaupten. VorhandeneRechtsgates11.21 erhaltensowieexterneLiDARModificationNotice nurdokumentarisch,nichtangewendet. SourcebranchV4weiterlokal, keineVeröffentlichung/Versionwahl/Tags/PR/Bloom/Farmoperationen. VorhandeneForthcoming-Changelogs alsVorbereitungkennzeichnen. KlarzwischenformalenIndex-/Binärvoraussetzungen, Projektabnahmekriterien/REP2004undoptionalenQualitätszielen unterscheiden.

#### Verifikation und Ergebnis

Offizielle Index-/REP144-/REP149-/Bloom-/Track-/Reviewquellen erneut gelesen; fünf offizielle distribution.yaml-Dateien tatsächlich geparst, keinR3D-Treffer im beschriebenen Umfang. Lokale dreiManifeste/Versionen/Lizenz- undInstallregeln abgeglichen; strukturelle Metadaten-/DokumentprüfungPASS. Vorhandene22Lizenzunterkapitel nicht umgedeutet, historischeGitkarten undexterneLiDARNotice-Anwendung bleibenseparat offen. KeineReleaseoperation. AktuelleReadiness, bereits vorhandeneStärken undverbleibendeGates in4,7–9,18.9. FinalerHumble-Regressionslauf folgtV4-028, nichtvorweggenommen.

#### Auswirkungen

Kein Push/Release/Historyrewrite, keine Änderungen an V1/V2/V3/main/Remotes/historischerPDF. Bestehende Paketversionen0.0.1 und Apache-2.0 erhalten. Keine Algorithmen neu entwickeln; konkrete ROS-Vertragskorrekturen separat testen.

### V4-028 - Abschluss – finale Humble-Regression und Forschungsabgrenzung

**Datum:** 15. Oktober 2026 (Europe/Berlin). **Arbeitspaket:** AP03/AP04/AP05/AP06/AP07/AP08/AP10. **Betroffene Dateien:** nur zentrales Protokoll; Prüfartefakte ausschließlich temporär. **Status:** VERIFIED für finale Humble-Regression, Schutzprüfung und Forschungsdokumentation; Gesamtgates bleiben offen. **Git-Commit:** `docs(v4): record final regression and research assessment` (Nachfolger aae71c37f4bb663ec408ca0f4487a5c747cda327, keine selbstreferenzielle SHA/kein Amend).

#### Ausgangssituation

V4-Eingang11d594aa5dca45293d14aed185a07a21fcb16d8e, sauber; bisherige V4-001..019 unverändert historisch. 171/120 vorherige Tests nicht als aktueller Nachweis nach Codeänderung ausgeben.

#### Ziel und Freigabe

M01 ausdrücklich im Chat freigegeben am15.10.2026; M02 ausdrücklich zurückgestellt, daher kein neuer Hindernistimeout/keine Sensor-zu-Basis-TF-Stoppolicy. Sonstige AP05..AP10-Phasen weiterhin nach ursprünglichem Auftrag autorisiert, keine erneute pauschale Freigabe nötig.

#### Technische Umsetzung und Begründung

Nach allen produktiven Änderungen/Installregeln erneut den exakten vorbereiteten CI-Befehl bash scripts/ci/run_humble.sh ausführen. Neue normaleCopyinstallation undseparaterSourcefreierReadonly-Container, alle3Pakete,UID1000,DDSlocalhost,keineHardware. Dependencyinstall/check,Manifeste/Syntax/Dokustruktur,vollecolconSuite/test-result,installierteRessourcen/Interfaces/EntryPoints/SyntheticPCD/Graph/A*/Action/Cloud/TF/Namespace/QoS/Follower/Lints prüfen. Danach tatsächlicheProduktions-/Testkopien mitSourcebytesvergleichen, eigeneContaineraufräumen,refs/PDF/LICENSEs/OSRF/alteEvents/Versionen/Algorithmen/altePYC kontrollieren. KonsolidiertenVorher-Nachher-Vergleich,Forschungsbewertung,AP-/Readiness-/Commit-/Testreferenzen imselbenProtokollabschließen. Keine Gesamtprojekt-VERIFIED-Wertung fürzurückgestelltesM02,RemoteCI,neuereTargets,Rechts-/Releasegates.

#### Verifikation und Ergebnis

Erneuter exakter CI-Befehl Exit0 nach allen Code-/Installänderungen: regulärer frischer Humble-Copybuild, colcon test/test-result0 und **225PASS/0FAIL/0ERROR/0SKIP**; zweiter Source-freier readonly-Container **169PASS/0FAIL/0ERROR/0SKIP**. Echte rosdep install/check in beiden0, keine Skipkeys/Pip. Aktuelle Module, sechs Runtime-Testdateien, YAML/Launch/Manifeste/Lizenztexte/Changelogs/Interfaceschema mit Installartefakten bytegleich, keinePCDs. Schutzprüfung0: Baseline/übrigeRefs/Remotes/22Lizenzabschnitte/alteEvents001..019/PDF/Lizenztexte/sechsOSRF-Notices/neunaltePYC erhalten; Preprocessing-/Graph-/A*-Berechnung/Filtergeometrie unverändert; Follower-Hinderniscallback unverändert und Control nurfreigegebeneMetadatenzuordnung. Drei eigeneAnalysecontainer nachexakterID-/Label-/Isolationsprüfung entfernt, CIeigeneContainer durchTrapentfernt, keineImagesgelöscht. Aktueller strukturellerDoc-/Metadata-/Linkcheck0.22Source-/Runtime-Pythonbytevergleiche sowieSharevergleichePASS. KeineHardware,keinPush,keineanderenBranches. Belege/T97..T111/Commitzuordnung/Forschungsbewertung in18.10–18.13.

#### Auswirkungen

Kein Push/Release/Historyrewrite, keine Änderungen an V1/V2/V3/main/Remotes/historischerPDF. Bestehende Paketversionen0.0.1 und Apache-2.0 erhalten. Keine Algorithmen neu entwickeln; konkrete ROS-Vertragskorrekturen separat testen.

### V4-029 - M02 – Konfigurationsvertrag, gemeinsame Dekodierung und validierte Eingangslage

**Datum:** 15. Oktober 2026 (Europe/Berlin). **Arbeitspaket:** AP05/M02, AP06/AP08 begleitend. **Betroffene Dateien:** configuration.py/centralYAML, cloud.py, neues obstacle_monitor.py und Unit-/Konfigurationstests, Protokoll. **Status:** VERIFIED für Konfigurations-/Validierungshelfer bzw. dokumentierte Zielentscheidung; Follower-Stopintegration folgt. **Git-Commit:** `feat(follower): define monitored obstacle input contract` (Nachfolger04d080b).

#### Ausgangszustand und Problem

Eingang04d080b15f9d744086085ccac88d2850d8d555c5, V4 sauber,85 versionierte Dateien. M01 vorhanden;225/169 bisherige Tests sind historische Ausgangsnachweise. Hindernisse bisher ohne Frische-/Frameüberwachung; interner Filter unabhängig optional. Keine neue Lizenz-/Versions-/Releaseentscheidung.

#### Ziel und autorisierte Entscheidung

Die neue Nutzer-Auftragsdatei gibt M02 ausdrücklich frei. Vorherige Rückstellungen bleiben historisch; sie sind für den konkret beschriebenen Monitoringumfang aufgehoben. Kein Push, keine Hardware, keine anderen Branches oder externen Projekte. M01-Schema und alle bisherigen Funktionen bleiben erhalten.

#### Technische Umsetzung und Begründung

Optionales path_follower.obstacle_monitoring mit enabled=false, timeout_sec=1.0, require_transform=true und topic=/local/filtered_obstacles. Fehlende Gruppe bleibt rückwärtskompatibel; vorhandene Gruppe verlangt enabled/timeout_sec/require_transform, topic ist optional; keine unbekannten Schlüssel. ROS-Parameter punktgetrennt und beim Start read-only, keine still ignorierten Laufzeitänderungen. Numerische positive endliche Timeoutvalidierung; Genauigkeit mindestens1ns. Gemeinsam genutzten Decoder für gültige leere Metadaten prüfen; strenger Monitor verwirft jede nichtfinite Geometrie, Legacydecoder behält finiteSelektion. Kein zweiter Byteparser. Kleine Monitor-Klasse mit expliziten Zuständen, Messalter/Steady-Empfangsfrische, exakter Timeoutgrenze einschließlichGleichheit, Rückwärts-/großen Vorwärtssprüngen und invalidiertem Cache; korrekte TF am Messstempel oder AblehnungfremderFrames bei require_transform=false. Bestehende TFbufferinfrastruktur wiederverwenden, nichtblockierender Lookup statt Warten im SingleThread-Callback. Native Integration folgt separat V4-030.

#### Verifikation und Ergebnis

Neuer normaler Drei-Paket-Copybuild /work/core4, UID1000/Humble/Python3.10, Domain91/localhost/FastDDS: build/test/test-result jeExit0, **287PASS/0FAIL/0ERROR/0SKIP**.62 neue deterministische Unit-/Konfigurationsfälle zusätzlich zu225Bestandsfällen. rcl_interfaces jetztdirekteRuntimeabhängigkeitfürreadonlyParameterDescriptor; keineScienceVersionsänderung. Kernprüfungen umfassenReplay, beideZeitgrenzen, Clockreset, TF-Richtung/-Zeit/-Geometrie, Empty/Nonfinite/Layout, alteYAMLohneGruppe undR3D_CONFIG_DIR. Erster Bootstrapaufruf endete nach erfolgreichemrosdep mitfehlenderHarnessvariableR3D_TEST_UID; keinBuildPASS daraus. core1 scheiterte amROS-Start in untauglicherDomain241, nativeProbe/weitereLäufe mitgültigenDomains bestanden; core2/core3 jeweils286PASS/1Flake8FAIL durchvier neueTesteinrückungen, korrigiert undgezielt gelintet. core4 istvollständigPASS. KeinProduktfehler/Skip versteckt. Follower-Gating/nativerTwist/Wiederanlauf/SourcefreieAbnahme werdenerstimnächstenSchritt beansprucht.

#### Auswirkungen und Grenzen

Nur freigegebene additive Konfiguration und opt-in Stopüberwachung. Default deaktiviert erhält bisherigen Followervertrag einschließlich Hindernisreaktion. Kein Hardware-Notstopp oder Sicherheitsnachweis; bekannte Sensor-/Cliff-/Radiusgrenzen bleiben. Historische Events001..028/PDF/übrigeRefs/Lizenztexte erhalten.

### V4-030 - Verbindliches Ziel – ausschließlich Humble/Jammy/Python3.10

**Datum:** 15. Oktober 2026 (Europe/Berlin). **Arbeitspaket:** AP05/M02, AP06/AP08 begleitend. **Betroffene Dateien:** nur zentrales Entwicklungsprotokoll; spätere aktuelle Nutzungs-/Wartungshinweise. **Status:** VERIFIED für Konfigurations-/Validierungshelfer bzw. dokumentierte Zielentscheidung; Follower-Stopintegration folgt. **Git-Commit:** `feat(follower): define monitored obstacle input contract` (Nachfolger04d080b).

#### Ausgangszustand und Problem

Eingang04d080b15f9d744086085ccac88d2850d8d555c5, V4 sauber,85 versionierte Dateien. M01 vorhanden;225/169 bisherige Tests sind historische Ausgangsnachweise. Hindernisse bisher ohne Frische-/Frameüberwachung; interner Filter unabhängig optional. Keine neue Lizenz-/Versions-/Releaseentscheidung.

#### Ziel und autorisierte Entscheidung

Die neue Nutzer-Auftragsdatei gibt M02 ausdrücklich frei. Vorherige Rückstellungen bleiben historisch; sie sind für den konkret beschriebenen Monitoringumfang aufgehoben. Kein Push, keine Hardware, keine anderen Branches oder externen Projekte. M01-Schema und alle bisherigen Funktionen bleiben erhalten.

#### Technische Umsetzung und Begründung

Neue ausdrückliche Nutzerentscheidung: Entwicklung undReleasevorbereitung ausschließlichROS2Humble/Ubuntu22.04Jammy/Python3.10 mitbewährtenSystemabhängigkeiten. KeineJazzy-/Lyrical-/Rollingkorrektur,keineDependencyMigration. HistorischeInkompatibilitäten bleibenbelegt. AP09 wirdbezogenaufHumbleabgenommen; fehlendeMultiDistroUnterstützung istkeinHumbleReleaseblocker. AP07HumbleWorkflowbeibehalten,RemoteCI weiterhinNOTREMOTELYVERIFIED ohnePush; AP08Zielangabenabgleichen; AP10Index/Bloom/Farm/RechtsgatesnurfürgewähltesHumblezielbewerten. M02/HumbleGesamtregression/Sourcefreiheit/lokaleCI priorisieren.

#### Verifikation und Ergebnis

Neuer normaler Drei-Paket-Copybuild /work/core4, UID1000/Humble/Python3.10, Domain91/localhost/FastDDS: build/test/test-result jeExit0, **287PASS/0FAIL/0ERROR/0SKIP**.62 neue deterministische Unit-/Konfigurationsfälle zusätzlich zu225Bestandsfällen. rcl_interfaces jetztdirekteRuntimeabhängigkeitfürreadonlyParameterDescriptor; keineScienceVersionsänderung. Kernprüfungen umfassenReplay, beideZeitgrenzen, Clockreset, TF-Richtung/-Zeit/-Geometrie, Empty/Nonfinite/Layout, alteYAMLohneGruppe undR3D_CONFIG_DIR. Erster Bootstrapaufruf endete nach erfolgreichemrosdep mitfehlenderHarnessvariableR3D_TEST_UID; keinBuildPASS daraus. core1 scheiterte amROS-Start in untauglicherDomain241, nativeProbe/weitereLäufe mitgültigenDomains bestanden; core2/core3 jeweils286PASS/1Flake8FAIL durchvier neueTesteinrückungen, korrigiert undgezielt gelintet. core4 istvollständigPASS. KeinProduktfehler/Skip versteckt. Follower-Gating/nativerTwist/Wiederanlauf/SourcefreieAbnahme werdenerstimnächstenSchritt beansprucht.

#### Auswirkungen und Grenzen

Nur freigegebene additive Konfiguration und opt-in Stopüberwachung. Default deaktiviert erhält bisherigen Followervertrag einschließlich Hindernisreaktion. Kein Hardware-Notstopp oder Sicherheitsnachweis; bekannte Sensor-/Cliff-/Radiusgrenzen bleiben. Historische Events001..028/PDF/übrigeRefs/Lizenztexte erhalten.

## 6. Test- und Validierungsergebnisse

`NOT STARTED` bedeutet in dieser Tabelle nicht ausgeführt, auch wenn historische Ergebnisse vorliegen. `VERIFIED` bezieht sich ausschließlich auf den benannten tatsächlichen Prüfumfang. Insbesondere wird ein statischer Parserlauf nicht als funktionaler ROS-Test gewertet. Alle hier neuen Prüfungen datieren vom 13. Oktober 2026.

| Test ID | Test | Ausgangsstand | V4-Ergebnis | Status | Nachweis |
| --- | --- | --- | --- | --- | --- |
| T01 | Git-/Baselineprüfung | main an geforderter Baseline, kein V4 | Objekt und Abstammung bestätigt; V4 vom identischen Commit erstellt; bestehende Referenzen geschützt | VERIFIED | V4-001; git cat-file, merge-base, branch, rev-parse; Refvergleich vor/nach Initialisierung |
| T02 | Unveränderte Bestandsdateien/PDF | 59 versionierte Dateien plus unversioniertes historisches PDF | SHA-256-Vergleich ohne Bestandsänderung; nur neues V4-Dokument | VERIFIED | V4-001; SHA-256-Manifest vor Initialisierung und Abschlussvergleich; PDF-SHA in 2.1 |
| T03 | Statische Python-/XML-Prüfung | Historisch geparst; keine neue Laufzeitabnahme | 26 Python-Dateien per AST und zwei Manifeste per XML-Parser erfolgreich gelesen | VERIFIED | `/usr/bin/python3 -B` mit ast.parse/ElementTree.parse; V4-001 |
| T04 | Paketnamen und Importinventar | r3d_-Namen vorhanden, Manifestlücken | Beide Namen lexikalisch gültig; direkte Imports paketweise erfasst, B04-B06 identifiziert | VERIFIED | AST-Importvergleich und REP-144-Prüfung, V4-001; kein Kollisions-/rosdep-Nachweis |
| T05 | Entwicklungsdokument | Fehlte | Zehn Hauptabschnitte, zehn APs, vollständiger V4-001-Eintrag, konsistente lokale Links/Tabellen und keine Platzhalter-Testresultate | VERIFIED | Temporäre Struktur-/Linkprüfung und Inhaltsreview; git diff --check, V4-001 |
| T06 | Commit-Gate vor Erstellung | Baseline-HEAD und leerer Index vor Initialisierung | Branch V4, vorgesehener Parent Baseline, ausschließlich zentrales Protokoll zur Aufnahme freigegeben; nach Staging nochmals kontrolliert | VERIFIED | Branch-/HEAD-/Indexprüfung und git diff --cached --check; V4-001. SHA/Ergebnis des anschließend erzeugten Commits über stabilen Subject und Git-Historie, nicht durch selbstreferenziellen Amend |
| T10 | rosdep resolution / installation / check | Skip-Workaround und unvollständige Manifeste dokumentiert | Nicht ausgeführt; Kandidatenschlüssel nicht als validiert behauptet | NOT STARTED | AP03; zukünftige resolve/install/check-Protokolle |
| T11 | colcon build (Copy-Install) | Symlink-Anleitung; historische lokale Konflikte berichtet | Nicht ausgeführt; keine neue Buildaussage | NOT STARTED | AP03/AP04; später isolierter Humble-/System-Python-Workspace |
| T12 | colcon test | 20 funktionale Fälle plus Linter vorhanden | Nicht ausgeführt; historische 20/40,07-s-Aussage nicht übernommen | NOT STARTED | AP06; Bestandsnachweis `test_configuration.py` und V3-Bericht |
| T13 | colcon test-result | Kein neuer vollständiger Nachweis | Nicht ausgeführt | NOT STARTED | AP06/AP07 |
| T14 | Linting | Templates vorhanden, Copyright skip, Legacy-Probleme berichtet | Kein neuer Lintlauf; keine Formatter-/Lintkorrektur | NOT STARTED | AP06; beide test-Verzeichnisse |
| T15 | Paketinstallation und installierte Ressourcen | Scripts/Config/Launch installiert; kopierte Config abgelehnt, Karten nicht installiert | Kein neuer Install-/Source-unavailable-Test | NOT STARTED | AP04/AP06; B07/B08 |
| T16 | ROS-Interface-/Namespace-/Cloud-/Action-Regression | Teilweise Config-/Odometrytests; bekannte Vertragsgrenzen | Keine Node-/Action-/Launchausführung; nur Source-Inspektion | NOT STARTED | AP05/AP06; B09-B13 |
| T17 | Distributionskompatibilität | Humble-Ziel, kein neuer Clean-Nachweis, weitere Distros unbewiesen | Keine Humble-/Jazzy-/Neuer-Laufzeitabnahme | NOT STARTED | AP09; lokale Installationspräsenz allein reicht nicht |
| T18 | CI-Ausführung | Keine Pipeline | Kein Workflow erstellt oder ausgeführt | NOT STARTED | AP07 |

#### 6.1 Ergänzende Nachweise V4-002/V4-003, 13. Oktober 2026

| Test ID | Test | Ausgangsstand | V4-Ergebnis | Status | Nachweis |
| --- | --- | --- | --- | --- | --- |
| T19 | Lizenzvergleich/SPDX/Primärquellen | Recherche-PDF mit pauschalen Aussagen | Vier Texte/IDs geprüft, K01-K12 korrigiert, qualitative Matrix und Quellenstatus nachvollziehbar | VERIFIED | Kapitel 11.3-11.8/11.18/11.22; gelesene Originaltexte |
| T20 | Copyright-/Dateiinventar/Erklärung | Namensheader, sechs Templates, Rechte offen | 60 versionierte Pfade/26 Python-Dateien inventarisiert; sechs Templates nach EmPy-Normalisierung identisch; Entwicklererklärung korrekt als Selbstauskunft | VERIFIED | Kapitel 11.9-11.12; keine rechtliche Rechtekettenabnahme |
| T21 | Direkte Dependency-Lizenzen | Unvollständige projektinterne Lizenzbelege | AST/Manifeste/Upstream-/lokale Lizenzquellen abgeglichen; BSD-Varianten und Eigen-/Fremdgrenzen getrennt | VERIFIED | 11.11; keine Dependency-Änderung/rosdep-Ausführung |
| T22 | Externe LiDAR-Herkunft/Originalgrant | Entwickler nennt externe Ableitung | Merge-Base 2f8753…, drei Folgecommits, LICENSE-Blob und NDT-Gitlink unverändert | VERIFIED | 11.13/11.14, echte Bare-Git-Auswertung |
| T23 | Externe Modifikationen/Notice-Konzept | Änderungen nur allgemein benannt | Drei Diffs, Sourcevertrag und 286 Netto-Pfade geprüft; Notice ausschließlich innerhalb des Protokolls; unbekannte Felder NOT VERIFIED | VERIFIED | 11.14/11.15; keine externe Änderung |
| T24 | Binär-/Dritttext-Stichprobe | Hauptlizenz könnte mit Paketumfang verwechselt werden | NumPy-Runtime-/LGPL-Zusätze und NDT-BSD-2/PCL-BSD-3 nachgewiesen | VERIFIED | 11.11.3/11.13.3; begrenzte Quellenprüfung, kein vollständiger Binary-/SBOM-Audit |
| T25 | GitHub-Sichtbarkeit/Tracking | Public origin, lokales V4 ohne Upstream | Lesende API bestätigt public, V1/V2/V3/main ohne V4; Development-Ziel 404 unklar; Konfiguration unverändert | VERIFIED | Abschnitt 12, G01-G08; keine GitHub-Änderung |
| T26 | Dokument-/Scope-/Commit-Gate | Nur zentrales Protokoll mit eigenen Plänen verändert | Ein gemeinsames 22-teiliges Kapitel, fortlaufende IDs, 59 andere versionierte Dateien und PDFs/Refs/Config geschützt; ausschließlich Dokument für Commit | VERIFIED | Struktur-/Quellen-/Inventar-/Hash-/Diff-/Indexprüfung; V4-002/V4-003 |
| T27 | Konkrete Lizenz-/Vertrags-/Deployment-/Gesamtbinärfreigabe | Fehlende individuelle Nachweise | Nicht durchgeführt; ausdrücklich nicht aus Recherche, Git oder Selbstauskunft abgeleitet | NOT STARTED | R01-R16; AP01 BLOCKED |

#### 6.2 V4-004: Lizenzimplementierung und statische Unverändertheitsprüfung

| Test ID | Prüfung | Tatsächliches Ergebnis | Status | Grenze / Nachweis |
| --- | --- | --- | --- | --- |
| T28 | Git-Eingang/Abstammung | V4 bei 9f11996…, Baseline ist Vorfahr; keine unbekannten versionierten Änderungen | VERIFIED | Vor Umsetzung; bekanntes unversioniertes PDF erhalten |
| T29 | Offizielle Root-LICENSE | Vollständiger ASF-TXT-Download, 11358 Byte/202 Zeilen; identische Bytes und SHA-256 cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30 | VERIFIED | Keine Änderung des Originaltexts/Appendix, keine eigene Bedingung |
| T30 | Eigene SPDX-Kommentare | Exakt zwei zusätzliche Kommentare in 18 bereits zugeordneten eigenen Dateien; bisheriger Namenshinweis erhalten | VERIFIED | Keine Attribution unbekannter/fremder Source; Pfade 11.21.2 |
| T31 | Manifest-/Setup-Lizenzen | Beide XML-Lizenzen Apache-2.0; beide bestehenden Setup-Lizenzwerte Apache-2.0 | VERIFIED | XML exakt nur license-Inhalt geändert; Setup-Code unverändert |
| T32 | Python-AST und Tokenvergleich | Alle 26 Python-Dateien parsebar, ASTs und semantische Tokens vor/nach identisch | VERIFIED | System-Python 3.10.12, -B; keine Runtime-/Hardwareabnahme |
| T33 | Versions-/Dependency-/Interface-Schutz | Versionen, Dependencies, Entry-Points, Buildtypen, Imports und ROS-/Launch-Logik unverändert | VERIFIED | Exakte Source-/XML-Vergleiche; keine funktionale Neuausführung |
| T34 | Fremd-/Daten-/Historien-Schutz | 39 übrige versionierte Dateien einschließlich sechs Templates, zwei PCDs und neun PYC sowie beide PDFs unverändert; historische Refs/Config unverändert | VERIFIED | SHA-256-/Refvergleich; externe LiDAR-Repositories nicht verändert |
| T35 | Dokument-/Diff-/Commit-Gate | Ein bestehendes 22-teiliges Kapitel, vier IDs, erhaltene V4-001 bis V4-003, Scope-/Tabellen-/Quellenprüfung; 22 freigegebene Commitpfade | VERIFIED | Git-Diff/Index-Gate; Commit-SHA/Parent/Umfang nach Erzeugung separat kontrolliert |
| T36 | Vollständige rechtliche Release-/Artefaktfreigabe | Nicht durchgeführt; Vertrags-/Karten-/konkrete Binärfragen offen | NOT VERIFIED | Kein ROS-/colcon-/rosdep-/Build-/Install-/Hardwaretest; AP01-Rechtsgesamtgate BLOCKED |

Die AST-/Tokenprüfung parst Originalbytes aus `git show 9f11996…:<Pfad>` und aktuelle Dateien, ohne Projektmodule zu importieren. Beim Tokenvergleich werden Positionen, Kommentare, Encoding- und nichtsemantische NL-Tokens ausgeblendet; Programm- und Stringtokens bleiben erhalten. Die Änderung an jedem eigenen Python-Pfad muss außerdem exakt der ursprünglichen Datei plus den beiden SPDX-Kommentarzeilen entsprechen. Bei XML ist ausschließlich die exakte TODO→Apache-Ersetzung zulässig. Ein byteidentischer ursprünglicher Syntax-/Interfacefehler wird hierdurch nicht behoben oder als funktional korrekt bestätigt.

Die temporären Prüfhilfen liegen außerhalb des Repositorys und sind keine zusätzlichen Entwicklungsberichte. Seit V4-001 besteht genau ein zentrales Entwicklungsdokument; V4-004 aktualisiert es und erzeugt keinen weiteren Forschungsbericht. Neue Testergebnisse müssen künftig mit vollständigem Befehl, Umgebung, Commit, Exitcode und relevanten Resultaten hier ergänzt werden; Fehler und nicht ausführbare Prüfungen werden ausdrücklich protokolliert.

#### 6.3 V4-005: Kartenentfernung und Nutzerpfade, 14. Oktober 2026

| ID | Prüfung | Ergebnis | Status | Grenze |
| --- | --- | --- | --- | --- |
| T37 | Karteninventar/Löschungen/aktive Referenzen | Zwei exakte getrackte Karten bereits am Eingang fehlend, im Commit gelöscht; 0 andere Repository-PCDs; keine aktiven alten Kartenreferenzen außerhalb historischer zentraler Dokumentation | VERIFIED | Git-Historie bleibt; allgemeine .pcd-Namen und synthetische Fixtures erhalten |
| T38 | Konfiguration/Regressionssuite | 40 cases passed, 3 deselected, 0,36 s; 23 neue parametrische Fälle | VERIFIED | System-Python 3.10/PYTHONNOUSERSITE=1; vorangegangene Log-/Tilde-Hilfsfehler korrigiert |
| T39 | Bestehende nicht bewegungserzeugende ROS-/Launchfälle | 3 passed, 40 deselected, 39,94 s; vier Planner-Kombinationen, Odometry/TF und Analyzerlaunch | VERIFIED | localhost/Domain 191/Fast DDS; vorhandene User-Site Dependencies, SciPy-/NumPy-Warnung; keine Hardware |
| T40 | Temporärer Copy-Build/externes Nutzerconfig-Probe | Zwei Pakete erfolgreich gebaut, installiertes Modul ohne ursprüngliche Source-Kopie konfigurierbar, 0 installierte PCDs | VERIFIED | -B/Bytecompile-Warnungen; keine allgemeine Default-Copy-Policy-/rosdep-/Binärreleaseabnahme |
| T41 | Statischer Scope-/AST-/Hash-/Gitcheck | 26 Python-Dateien parsebar; alle Nodes/Algorithmen/ROS-Launches/Manifeste/Setup/Lizenzheader unverändert; exakte Konfig-/Teständerung, PDFs/Refs geschützt | VERIFIED | V4-005, Git-Whitelist und Commit-Gate; kein History-Rewrite |

Ausgeführt (temporäre Basis `/tmp/r3d-v4-finalize`, Projektpfad wie 2.1):

```bash
# ROS 2 Humble zuvor in der jeweiligen Bash gesourced; keine Installation:
PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 /usr/bin/colcon --log-base /tmp/r3d-v4-finalize/map-check/log build --base-paths /tmp/r3d-v4-finalize/map-check/src --build-base /tmp/r3d-v4-finalize/map-check/build --install-base /tmp/r3d-v4-finalize/map-check/install --packages-select r3d_preprocessor r3d_planner --event-handlers console_direct+
# Source-PYTHONPATH auf die jeweilige geprüfte Paketkopie; ROS_LOG_DIR unter /tmp:
/usr/bin/python3 -B -m pytest -p no:cacheprovider --basetemp=/tmp/r3d-v4-finalize/pytest-unit r3d_planner/test/test_configuration.py -k "not effective_ros_parameters_and_odometry and not preprocessor_real_launch and not real_launch_restart_and_all_components" -q
# Nach Sourcen der temporären Installation, mit Domain 191/localhost/Fast DDS:
/usr/bin/python3 -B -m pytest -p no:cacheprovider --basetemp=/tmp/r3d-v4-finalize/pytest-runtime /tmp/r3d-v4-finalize/map-check/src/r3d_planner/test/test_configuration.py -k "effective_ros_parameters_and_odometry or preprocessor_real_launch or real_launch_restart_and_all_components" -q
```

Der zweite Befehl lief ohne User-Site, der dritte mit bereits vorhandener User-Site und abgesichertem ROS-Domain. Keine pip-/apt-/rosdep-Installation. Temporäre Fixtures sind keine neuen Projektkarten und werden nach der Prüfung entfernt. Der Copy-Probe wurde anschließend mit Source-Kopie am ursprünglichen Pfad nicht verfügbar, installierter Modulherkunft und eigenem R3D_CONFIG_DIR ausgeführt.

#### 6.4 V4-006: technische Lizenz- und Artefaktprüfung, 14. Oktober 2026

| ID | Prüfung | Ergebnis | Status | Grenze |
| --- | --- | --- | --- | --- |
| T42 | Aktueller Online-/Bytevergleich | Root-/zwei Paket-LICENSEs identisch zum erneut geladenen offiziellen ASF-TXT; 11358 Byte/cfc7749b… | VERIFIED | Originaltext unverändert, keine neue Bedingung |
| T43 | Copyright-/SPDX-/Manifest-/Setupscope | 18 eigene Header und sechs OSRF-Templates erhalten, beide XML-/Setup-Lizenzen Apache; nur Share-LICENSE/license_files ergänzt | VERIFIED | Entwicklererklärung keine unabhängige Befugnisprüfung; fehlende Header nicht pauschal Lizenzfehler |
| T44 | sdist/Wheel-Mitnahme | Je ein sdist und Wheel erfolgreich; je 1/2 identische Lizenzkopien; alle sechs sdist-Fremdtemplates erhalten; 0 PCD/0 PYC | VERIFIED | Temporäre konkrete Artefakte, keine transitive/native Bundlefreigabe |
| T45 | Copy-colcon aus extrahierten sdists | 2 packages finished [1min 1s]; Share-LICENSE beider Pakete identisch; 0 installierte PCDs | VERIFIED | Bytecompile deaktiviert/Warnungen; kein tatsächliches Debian/Bloom/Buildfarmartefakt |
| T46 | Source-unavailable installierte Nutzerkonfiguration | Installierter Modulpfad bestätigt, Source umbenannt, externe Nutzer-YAML/Robotprofile erfolgreich | VERIFIED | Ein vorzeitiger Probeversuch fehlgeschlagen; nach Buildabschluss erfolgreich; implizite Defaultpolitik weiter AP04 |
| T47 | Fremd-/LiDAR-/Restdaten-Kontrolle | Templatehashes/Archive geprüft; vorhandene Original-/Modified-LICENSE-Blobs und drei externe Folgecommits bestätigt | VERIFIED begrenzt | NDT/PCL-Lizenzquellen bisher dokumentiert; vollständige Deployment-/Binär-/Historienrechtsfreigabe NOT VERIFIED |
| T48 | Git-/Dokument-/Abschlussgate | Zwei getrennte Commitumfänge, V4-001..005 erhalten, PDFs/Refs/Config unverändert, keine aktive PCD; Setupkeywords minimal | VERIFIED | Rechtliche Gesamtfreigabe/Bloom/Index unverändert offen; Commit-SHA nach Erstellung separat kontrolliert |

Ausgeführte Artefaktprüfung (je temporäres Paketverzeichnis, ohne Systeminstallation):

```bash
PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B setup.py sdist --dist-dir <temporary-dist> bdist_wheel --dist-dir <temporary-dist>
# Unter ROS-Humble-Setup; extrahierte Paketroots besitzen jeweils eigene LICENSE:
PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 /usr/bin/colcon --log-base /tmp/r3d-v4-finalize/license-check/log build --base-paths /tmp/r3d-v4-finalize/license-check/extracted --build-base /tmp/r3d-v4-finalize/license-check/build --install-base /tmp/r3d-v4-finalize/license-check/install --packages-select r3d_preprocessor r3d_planner
```

`<temporary-dist>` ist ein vor Ausführung konkret ersetzter Platzhalter unter /tmp/r3d-v4-finalize/license-check/dist/<Paket>, kein Projektpfad. tarfile/zipfile wurden zum vollständigen Inhalts-/Bytevergleich verwendet; installierte Shares direkt gelesen. Keine pip-/apt-/rosdep-Installation, kein Upload. Ein fehlerhafter früher Probezeitpunkt wurde korrigiert; nur der abgeschlossene Build/Probe gilt als Nachweis.

#### 6.5 V4-007: historische PDF-Versionierung, 14. Oktober 2026

| ID | Prüfung | Ergebnis | Status | Grenze |
| --- | --- | --- | --- | --- |
| T49 | Existenz/Tracking/Hash/PDF-Metadaten/Commitgate | Vorhandenes bislang unversioniertes PDF, 33 Seiten/298707 Byte, exakter Referenzhash 8c3603ec…; nur PDF/Protokoll im Commit-Gate | VERIFIED | /usr/bin/pdfinfo Exit 0; PATH-Version scheiterte an GLIBC_2.38, System-Fallback genutzt; keine Content-/Lizenzänderung |

Ausgeführt: `git ls-files -- docs/R3D_Planner_Development_History.pdf`, `sha256sum docs/R3D_Planner_Development_History.pdf`, `/usr/bin/pdfinfo docs/R3D_Planner_Development_History.pdf`; gezielter Index-Bytevergleich und `git -c core.attributesFile=/tmp/r3d-v4-ap02/pdf-review-attributes diff --cached --check` (PDF binär nur im Prüfbefehl). Nach Commit SHA/Parent/Dateiumfang/Tracking separat kontrolliert. Keine PDF-Neuerzeugung, kein Push.

#### 6.6 V4-008/V4-009: AP02-Metadaten und deklarierte Rechte, 14. Oktober 2026

| ID | Prüfung | Ergebnis/Exitcode | Status | Grenze |
| --- | --- | --- | --- | --- |
| T50 | XML/catkin_pkg/REP-/Versions-/URL-/Maintainerprüfung | Zwei Manifeste parse_package/validate erfolgreich, 0 warnings, Format 3/Namen/0.0.1/Apache/ament_python/konsistente Beschreibungen/URL-Typen; Exit 0 | VERIFIED | Keine rosdep-Auflösung, keine Mailzustellungs-/Live-URL-/Namenskollisionsprüfung |
| T51 | Python-/Dependency-/Interface-/Lizenzscope | 26 Python-Dateien parsebar; zwei Setup-Metadaten-ASTs geändert, nach exakt vier Meta-Keywordmasken identisch; 24 übrige ASTs/Runtimebytes/Deps/Entry-Points/Ressourcen/Lizenz/PDF unverändert; Exit 0 | VERIFIED | Keine Algorithmen-/ROS-/Safetyänderung und keine zusätzliche Lizenzrecherche |
| T52 | Vorhandene passende Konfigurationsfälle | 40 passed, 3 deselected, 0,36 s; Exit 0 | VERIFIED | System-Python 3.10, -B, ohne User-Site; native ROS-/Launchfälle nicht erneut ausgeführt |
| T53 | Zwei erzeugte Wheels/Metadaten-/Share-Regression | Version/Description/Author/Maintainer/URLs/Apache und Share-Manifeste/Lizenz/Indexmarker geprüft, 0 PCDs; Exit 0 | VERIFIED | Normierte Python-Distributionnamen separat; erster naiver Namechecker korrigiert; kein colcon-/Debian-/Releaseartefaktclaim |
| T54 | Dokument-/Erklärungs-/Gitgate | V4-001..007 erhalten, nur sechs AP02-Pfade; Karten-Selbstauskunft vollständig dokumentiert; andere Branch-/Remote-/PDFrefs geschützt | VERIFIED im Dokumentumfang | Unterliegende Rechte/Datenschutz nicht unabhängig geprüft; andere Branchbereinigung NOT STARTED |

#### 6.7 V4-010/V4-011: historische Trees und Dependencies, 14. Oktober 2026

| Test ID | Test | Ausgangsstand | V4-Ergebnis | Status | Nachweis |
|---|---|---|---|---|---|
| T55 | Historische Branchbereinigung | V1/V2/V3/main je zwei PCDs | 21/18/26/26 Python-ASTs, 1/1/3/3 YAMLs, jeweils zwei Manifeste/0 Warnungen; exakte Whitelist/alte Tips Vorfahren | VERIFIED statisch | V4-010 / Abschnitt 14 |
| T56 | Direkter Dependencyabgleich | 128 Imports/26 Python-Dateien | Alle Runtime-/Build-/Testimporte und CLI-Aufrufe erfasst, 2 Manifeste gültig/AP02 unverändert | VERIFIED | V4-011 / 15.1-15.3 |
| T57 | Offizielle Humble/Jammy-Keys | 26 externe Keys plus lokales Paket | Je resolve Exit 0; numpy/scipy/ament_python Gegenproben Exit 1 | VERIFIED Auflösung | 15.4 |
| T58 | rosdep Installation/check | korrigierte Manifeste | Simulation Exit 0; check Exit 1, Apt-Open3D/NetworkX fehlen; keine echte Installation | BLOCKED Gesamtnachweis | 15.5 |
| T59 | Native Apt-/Python-Versionen | System/Benutzer/entpackte Debs | Python3.10/Open3D0.14.1/NetworkX2.4/NumPy1.21.5/SciPy1.8.0; keine SciPy-Kompatibilitätswarnung | VERIFIED begrenzte Kombination | 15.6 |
| T60 | Copy-Build/Artefakte | zwei Pakete | colcon build Exit 0; 7 Entry-Points/2 LICENSEs/4 Launches/3 YAMLs; keine PCDs, installierte Module importierbar | VERIFIED Copy-/Importumfang | 15.7 |
| T61 | Bestehende ROS-Regressionen | 43 Konfigurations-/Launch-/Odometryfälle | 43 PASS, test-result Exit 0 | VERIFIED | 15.8 |
| T62 | Vollständige Bestandsuite | 49 Tests beider Pakete | final 45 PASS/2 Flake8 FAIL/2 Copyright SKIP; test Exit 0, test-result Exit 1 | FAIL Gesamtsuite | 15.8 |
| T63 | Noble-Key-Grenze | python3-open3d | rosdep resolve Ubuntu:Noble Exit 1/unavailable; keine Jazzy-Ausführung | VERIFIED Regelbefund, NOT VERIFIED Runtime | 15.9 |
| T64 | Endzustand Git/Historienschutz | alle fünf Branches | lokale aktuelle Trees PCD-frei, 13 ursprüngliche Commits erhalten, PDF/Remote-URLs/Trackingrefs unverändert; kein Merge/Push | VERIFIED | 15.11 / Abschlusscommit |


Ausgeführt unter `/usr/bin/python3` 3.10.12, catkin_pkg 1.1.1, pytest 6.2.5, setuptools 59.6.0/wheel 0.37.1; ROS-Humble-Setup nur für Configtests gesourced, PYTHONNOUSERSITE=1/PYTHONDONTWRITEBYTECODE=1. `parse_package(path, warnings=[])` und `Package.validate(warnings=...)` für beide Manifeste; gezielte XML-/AST-/URL-/Hash-/Entry-Pointkontrollen ohne Projektmodule/Setupausführung im statischen Check. Wheel-Setupausführung ausschließlich in temporären Paketkopien.

```bash
# Ausgeführt im Projektroot, mit Source-PYTHONPATH und ROS_LOG_DIR unter /tmp:
/usr/bin/python3 -B -m pytest -p no:cacheprovider --basetemp=/tmp/r3d-v4-ap02/pytest r3d_planner/test/test_configuration.py -k "not effective_ros_parameters_and_odometry and not preprocessor_real_launch and not real_launch_restart_and_all_components" -q
# Je temporäre vollständige Paketkopie; keine pip-/Systeminstallation:
PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B setup.py bdist_wheel --dist-dir <temporary-package-dist>
```

Der konkrete Distpfad lag unter /tmp/r3d-v4-ap02/dist/<Paket>; Platzhalter nicht wörtlich ausgeführt. Kein Clean-Build/colcon test/rosdepcheck/Hardwaretest in AP02; vorhandene AP03-Lücken bleiben. Der erste Wheelchecker scheiterte an Python-Namensnormalisierung, der finale kanonische Vergleich und beide Wheels sind erfolgreich. ROS-Web-Endpunkte waren gesperrt; offizielle Raw-Quellen genutzt. Keine rückwirkende Neuinterpretation früherer Testresultate.

## 7. Probleme und offene Entscheidungen

| ID | Beschreibung | Auswirkung | Erforderliche Entscheidung | Vorgeschlagene Lösung | Aktueller Status |
| --- | --- | --- | --- | --- | --- |
| O01 | Apache-2.0 verbindlich gewählt/technisch angewendet; Vertrags-/Befugnislage nicht unabhängig geprüft | Keine vollständige rechtliche Releasefreigabe | Noch offene arbeits-/dienstvertragliche Rechte und Lizenzierungsbefugnis klären | Entscheidung/Dateien aus V4-004 erhalten; konkrete entgegenstehende Hinweise betroffenenbezogen prüfen | BLOCKED nur für Rechtsgesamtgate; Wahl/Implementierung COMPLETED |
| O02 | V4-010 bereinigt lokale aktuelle V1/V2/V3/main-Trees; V4 schon bereinigt | Historische Gitobjekte/öffentliche Remote-Trees bleiben; Selbstauskunft keine unabhängige Rechtsfreigabe | Individuelle Rechts-/Distributionsfragen getrennt prüfen | Normale lokale neue Commits, kein Push/Rewrite | Aktuelle lokale Trees VERIFIED; rechtliche Gesamtfreigabe NOT VERIFIED |
| O03 | AP05–AP10 sind im Folgeauftrag ausdrücklich freigegeben; M01 zusätzlich im Chat | Unabhängige technische Phasen konnten fortgesetzt werden | M02 benötigt weiterhin gesonderte Freigabe | Vorhandene Build-/Tests erhalten; freigegebene Interfaces, CI, Dokumentation und Analyse umgesetzt | M01 VERIFIED; AP05 insgesamt IN PROGRESS wegen zurückgestelltem M02 |
| O04 | Drei Pakete konsistent0.0.1; Dev-/API-/ABI-Grenzen in MAINTENANCE | Keine Metadatendiskrepanz und keine stabile Releasezusage | Endgültige Releaseversion/Ziel/Datum später festlegen | Drei installierte Forthcoming-Changelogs vorbereitet | Technische Metadaten VERIFIED; Releaseentscheidung offen |
| O05 | Host-Conda3.14 neben System-Python3.10; isolierte Apt/Humble-Container eingesetzt | Hostmischung unverändert, Containererfolg nicht als Hostreparatur ausgeben | Native konsistente Humble-Umgebung verwenden | Python3.10.12 mit Apt-Bibliotheken ohne User-Site/Conda | Isolierter Nachweis VERIFIED; Host nicht geändert |
| O06 | Aktuell32 externe Humble-Keys und echte Installation/check; Lyrical-Dependencies regulär vorhanden | Jazzy/Noble-Open3D weiterhin blockiert | Neuere Zielplattform und Dependencystrategie entscheiden | Getrennte reale Container-/API-/Testmatrix18.8 | Humble VERIFIED; Jazzy BLOCKED; Lyrical PARTIAL |
| O07 | Normale Copy-Share-Konfiguration und R3D_CONFIG_DIR, separate exklusive Outputpfade geprüft | Eigene Karten und beschreibbares Outputverzeichnis weiter nötig | Mapname nach Analyse bewusst auf Output setzen | Installierte Ressourcen readonly, Daten nutzerbezogen | AP04 VERIFIED für Humble; Umzug des Installprefix nicht nachgewiesen |
| O08 | Narrow-Quaternion ersetzt; Namespace/Action/QoS/TF-Eingänge korrigiert | Alte externe Narrow-Decoder müssen migrieren | Planner/Follower/Interfacepaket zusammen bereitstellen | Atomare PathWithMetadata plus gültiger Standard-Path, native Regressionen | M01 und implementierte Verträge VERIFIED; neue Nav2-Zusatzfelder offen |
| O09 | Optionaler Filter und Follower haben weiterhin keine vollständige Cloud-Frische-/TF-Überwachung | Kein Sicherheitsnachweis; Nahbereichsradien können ungünstig zusammenspielen | M02 gesondert entscheiden | Konfigurierbarer Monitor mit Legacy-Default, Messstempel-TF und klaren Stopzuständen vorgeschlagen | Analyse VERIFIED; Implementierung ausdrücklich zurückgestellt |
| O10 | Historisches PDF unverändert für Git-Aufnahme freigegeben/geprüft | Referenz nun im V4-Clone verfügbar | Nutzerauftrag zur Versionierung liegt ausdrücklich vor | V4-007, gleicher Referenzhash/33 Seiten; keine inhaltliche Aktualisierung | VERIFIED - dokumentierter Aufnahmeumfang |
| O11 | Humble-Workflow implementiert/lokal reproduziert; neue Distributionen untersucht | Kein Remote-CI-/pauschaler Support-/Releaseerfolg | Spätere Veröffentlichung und konkreten Supportumfang autorisieren | Humble225/169; Jazzy/Lyrical-Matrix und echte Grenzen | AP07 NOT REMOTELY VERIFIED; AP09 PARTIAL |
| O12 | Originalhinweise/konkrete eigene Paketartefakte kontrolliert; Roottext in sdists/Wheels/Shares vorhanden | Keine Lizenzmitnahmelücke in geprüften Artefakten, Gesamtbundles/transitive Nativebinaries offen | Tatsächlichen künftigen Bundle-/Debianumfang festlegen und prüfen | T42-T47/11.21.5; keine automatische Library-Neulizenzierung | Technischer Paketumfang VERIFIED; rechtliche Gesamtbundlefreigabe BLOCKED/NOT VERIFIED |
| O13 | V4 soll nicht öffentlich gepusht werden; origin zeigt weiterhin auf public | Kein konfigurierter privater Pushschutz | Option A/B und konkrete spätere Repository-/Remote-/Pushfreigabe | Empfehlung B, nur nicht ausgeführte Vorlage in Abschnitt 12; aktuelle Remotes unverändert | NOT STARTED - Entscheidung ausstehend |
| O14 | LiDAR-Serverstand/Git-Ableitung belegt, tatsächlicher Deploymentstand fehlt | Keine Aussage über exakt eingesetzte Odometrie-/Submodul-/Systembinaries | Deployment-SHAs und Paket-/Artifactumfang belegen | R14/R15; analysierten Tip nicht mit Runtime gleichsetzen | NOT STARTED |
| O15 | Externe BSD-/PCL-Bedingungen und persönliche Änderungsattribution getrennt | Externe Anwendung/Binärmitnahme weiterhin offen | Spätere Notice-Übernahme und konkrete Distributionsnachweise | Notice in 11.15 dokumentarisch abgeschlossen; kein externes Repo geändert | Dokumentationsabschluss COMPLETED; externe Anwendung NOT STARTED |

Die verbindliche Lizenzentscheidung und technische Eigenanteil-Implementierung sind unter V4-004 erfolgt. Sie ersetzen keine unabhängige Vertrags-/Datenrechteklärung oder konkrete Binärfreigabe. O01/O02/O12 blockieren den öffentlichen Abschluss, nicht jede unabhängige technische Änderung. Bei neuer Information wird der jeweilige Status mit Datum und Nachweis aktualisiert; frühere Einschränkungen bleiben historisch nachvollziehbar.

## 8. Versionsvergleich: historische main-Baseline → V4

Vergleichsreferenz bleibt der festgeschriebene Baseline-Commit, nicht ein später eventuell weiterentwickeltes main. Die Baseline-Spalte bleibt historisch; die V4-Spalte enthält ausschließlich ausgeführte Änderungen mit Nachweis.

| Bereich | Ausgangsstand main | Änderung V4 | Ergebnis | Nachweis |
| --- | --- | --- | --- | --- |
| Entwicklungslinie | main bei `c65642f…`; V1/V2/V3 als Remote-Tracking-Refs | Lokaler Branch V4 unmittelbar von Baseline; ein fokussierter Initial-Dokumentationscommit | Neue getrennte Entwicklungslinie, bestehende Refs unverändert | V4-001, T01/T06, Git-Parent/Refvergleich |
| Forschungsdokumentation | Historischer Bericht und Bestandsdokumentation, PDF zunächst unversioniert | Dasselbe zentrale Protokoll bisV4-027; vorhandene Nutzeranleitungen und zweckgebundene Wartungs-/Release-Metadaten aktualisiert | Keine zusätzlichen Forschungsberichte; historische Ereignisse/PDF unverändert | V4-020..027; Kapitel18 |
| Historische PDF | Vorhandene unveränderte, zunächst unversionierte Baseline-Dokumentation | Identische Bytes in V4 unter Git aufgenommen | Keine neue technische Funktion; SHA unverändert und historische Kartendarstellung erhalten | V4-007/T49 |
| Planung/Preprocessing | Vorhandene PCD-/Voxel-/Traversierbarkeits-/Graph-/A*-Funktionen | Vorhandene Berechnungen erhalten; A* um optionalen kooperativen Cancelcheck ergänzt | Kein neuer Planungsalgorithmus; Nachrichtenausgabe/Actionverträge gezielt korrigiert | V4-022; native Action-/Bestandsregressionen |
| Paketmetadaten | Version 0.0.0 vs 0.0.1, TODO-Beschreibungen, keine URLs/Author | AP02: 0.0.1 konsistent, Beschreibungen/Repo-/Issue-/Authorfelder ergänzt, Maintainer erhalten | Technischer Metadatenumfang VERIFIED, Namen/Buildtyp/Dependencies/Lizenzen erhalten | V4-008/T50-T53; Kapitel 13 |
| Dependencies | Teildeklaration, fehlende Imports, Skip-Workaround | Direkte Manifeste korrigiert; Interface-/Action-Testdependencies ergänzt;32Keys einzeln und reguläre Installation/check geprüft | Humble/Jammy VERIFIED; neuere Ziele getrennt | V4-011/012/020/022/026;18.8 |
| Build/Installation | Copy-Config absichtlich abgelehnt, Sourcepfade und fehlende Paketlizenzmitnahme | Normale Copy-Shareauflösung; externer Override; Lizenzmitnahme; separate exklusive Ausgabe | Zwei Clean-Copy-Builds und Source-freie readonly-Installation bestanden | V4-006/013/014/016; T71-T81 |
| ROS-Interfaces | Action/Topics/Service, RViz, Filter/Follower; bekannte Semantikgrenzen | Atomare Metadaten statt Quaternionflag; validierte Geometrie; Actionfehler/Cancel; Namespace/TF/RViz/QoS | Implementierter Umfang VERIFIED; M02 nur Vorschlag, keine volle Nav2-Zusage | V4-017..023;18.2–18.5 |
| Konfiguration/Launch | Source-Beispielpfade, zentrale strikte YAML, vier Launches | Installierte YAML/Robotprofile, externe Overrides, getrennte Ausgabe und optionaler Namespace; relative Topics erlaubt | Vier Launches erhalten; Rootdefaults und unabhängige Filter/RViz-Schalter erhalten | V4-013/014/023; native Launch-/Remaptests |
| Odometry/TF | Standardisierte Poseeingabe, Frische/Frames, use_start, Poseverlust-Nullbefehl | Bestehende Posefrische/Transformation erhalten; nichtfinite TFtranslation zusätzlich abgewiesen; RViz-Posen validiert | V3-Integration bleibt Vorleistung; keine Sensor→Base-M02-Transformation | V4-023; native TF-/RViztests |
| Tests/Lint | Funktionale Fälle und Linter-Templates bereits vorhanden | Gezielte Regressionen; sechs aktive Pythonlints und fünf CMakechecks; bei aktuellem Eingang171Fälle, nun225 | 225PASS/0FAIL/0SKIP Humble,169SourcefreieFälle; keine Coveragezahl | V4-012..026;18.3–18.8, Schlusslauf18.10 |
| Lizenzierung/Datenrechte | Keine Root-LICENSE, TODOs und ungeklärte gebündelte PCDs | Apache-Eigenanteile samt Pakettexten geprüft; PCDs aus aktivem Tree/Artefakten entfernt | Technischer AP01-Umfang VERIFIED, historische Git-/Vertrags-/Bundlefragen offen | V4-004..006; T42-T48 |
| CI/CD | Keine Pipeline | Gepinnter Humble-Workflow und gleiche lokale Zwei-Container-Prüfung | IMPLEMENTED / NOT REMOTELY VERIFIED; lokal225+169PASS | V4-024;18.6 |
| Kompatibilität | Humble als Ziel dokumentiert | Reale Humble-/Jazzy-/Lyrical-Container; aktuelle Support-/API-/Dependencyanalyse | Humble VERIFIED; Jazzy Open3D BLOCKED; Lyrical PARTIAL; Kilted/Rolling nicht nativ getestet | V4-026;18.8 |
| Release | Kein hier belegter Index-/Bloom-/Buildfarmabschluss | Zielbezogene Index/rosdep/Bloom/Farm/Debian-Checkliste; Forthcoming und Wartungsgrenzen | NOT READY für öffentliche Gesamtveröffentlichung; kein Release/Push/Tag | V4-025/027;18.9 |
| Externe LiDAR-Software | Separates Repository; Standard-Odometry-/TF-Vertrag | Herkunft und ältere Diffs dokumentiert; Notice im Protokoll abgeschlossen | Kein fremder Code integriert/geändert; Originallizenzen getrennt | V4-003/V4-004; 11.13-11.15 |
| Copyright-Attribution | 18 eigene Namensheader plus sechs OSRF-Templates | Traditionelle Apacheheader zusätzlich zur erhaltenen SPDX-/Namensattribution; neue eigene Dateien entsprechend | Sechs OSRF-Noticeblöcke identisch, zwei obsolete Skips entfernt; Root-/Pakettexte unverändert | V4-004/015/016; T70/T82 |
| GitHub-/Remoteverwaltung | origin public, V4 lokal ohne Upstream | Optionen und Pushschutz nur als Vorschlag dokumentiert | Keine Sichtbarkeits-/Remoteänderung; kein Push | Abschnitt 12/T25 |
| PointCloud2 | Gepackte12-byteXYZ-Annahme im Filter, Rowpadding-/Endiangrenze | Feld-/Stride-/Endianbewusster gemeinsamer Decoder, finiteXYZ und complete-empty-Metadata | 83Regressionsfälle, Inputbytegleichheit, äquivalente Filteroutputs | V4-018/T89/T90 |

## 9. Veröffentlichungsstatus

Aktueller Stichtag15.10.2026. Die vollständige Checkliste mit Quellen, Nachweisen und nächsten Maßnahmen steht in18.9; die Distributionsmatrix in18.8. Historische Datierungen in späteren Entwicklungskapiteln sind keine aktuellen Statusmeldungen.

| Gegenstand | Aktueller Status | Konkrete Grenze |
|---|---|---|
| Öffentliche V4-Source / ROS Index | **NOT READY** | Geprüfter V4-Stand lokal; Rechte-/Publikationsentscheidung und externe Review offen |
| rosdep Humble/Jammy | **READY / VERIFIED lokal** |32 externe Keys, reale Installation/check; drei gemeinsam gebaute Pakete |
| rosdep Jazzy/Noble | **BLOCKED** | Open3D-Regel und fehlender Apt-Kandidat |
| rosdep Lyrical/Resolute | **READY im Dependency-Umfang** | Installation/check bestanden; Tests/API-Vertrag nicht vollständig abgenommen |
| Bloom | **NOT READY** | Endgültige Version/Ref, Ziel, Releaseorganisation und Rechts-/Public-Gates offen; Forthcoming vorhanden |
| ROS Buildfarm / Debian-Lieferung | **NOT READY / NOT VERIFIED** | Keine Release-/Farm-/Debianabnahme oder Veröffentlichung ausgeführt |
| Humble22.04/Python3.10 amd64 | **VERIFIED im definierten Umfang** |225 volle und169 Source-freie Tests; kein Hardware-/Coverage-/Sicherheitsnachweis |
| Neuere Targets | **PARTIAL / BLOCKED** | Matrix18.8: Jazzy nur Interface geprüft, Lyrical Build und Funktionen teilweise, Kilted/Rolling nicht nativ |
| CI/CD | **IMPLEMENTED / NOT REMOTELY VERIFIED** | Lokaler gleicher Befehl bestanden; kein autorisierter Push/Remote-Lauf |
| M02 | **Zurückgestellt** | Analyse und konkreter Vorschlag vorhanden; weder Timeout noch Sensor→Base-Stopüberwachung implementiert |

Fehlende optionale Templates, zusätzliche Distributionen oder ein nicht beanspruchter REP-2004-Quality-Level sind keine neu erfundenen allgemeinen Indexblocker. Die belegten grundlegenden Gates bleiben Rechte, öffentlich prüfbarer V4-Source und später zielbezogene Release-/Buildfarm-Abnahme. Version0.0.1 und Apache-2.0 bleiben erhalten. Keine rechtliche Gesamtfreigabe durch lokale Tests.

## 10. Abschließende Bewertung

Der beauftragte technische AP01-Umfang ist nach V4-006 VERIFIED: Apache-2.0-Entscheidung und Originaltext, 18 zugeordnete eigene Copyright-/SPDX-Header, Manifest-/Setup-Lizenzen, erhaltene Fremdtemplates, getrennte externe LiDAR-Originalbedingungen/Modification Notice, aktive Kartenentfernung und konkret geprüfte Paket-Lizenzmitnahme. Roottext ist unverändert; zwei notwendige identische Paketkopien ermöglichen isoliertes Source-/Wheel-/ROS-Paketieren.

Die bisherigen zwei Karten waren bereits beim Auftragseingang im Working Tree gelöscht und sind nun in normalem V4-Commit entfernt. Nutzer liefern eigene PCDs über die vorhandene Konfiguration; die Algorithmen/ROS-Verträge bleiben erhalten. 40 Configfälle plus drei vorhandene ROS-/Launchfälle bestehen. Copy-Installation ohne Karten und externe Nutzerkonfiguration bei nicht verfügbarem ursprünglichem Sourcepfad sind geprüft; allgemeine Copy-Default-/Ausgabepolitik ist nicht umfassend refaktoriert. Systembuild ohne User-Site ist kein vollständiger Runtime-Dependencynachweis, da dort Open3D/NetworkX fehlen; Runtimefälle benutzen vorhandene User-Site und behalten eine SciPy-/NumPy-Warnung.

**Vollständige rechtliche Releasefreigabe nicht verifiziert:** Verträge/Arbeitgeberbefugnisse, sonstige Dateiprovenienz, historische Karten-Gitobjekte und konkrete transitive/native/zusammen verteilte Binaries bleiben offen. Die Karte ist aus aktuellem Tree/Artefakten, nicht aus Git-Historie, Forks oder Kopien entfernt. AP01 insgesamt daher BLOCKED nur für dieses Rechts-/Releasegesamtgate. AP04/AP06/AP08/AP10 IN PROGRESS, AP02 VERIFIED; AP03 NOT STARTED. ROS Index/Bloom/Buildfarm NOT READY; kein neuer Quality Level oder Plattform-Supportanspruch.

Zwei logisch getrennte lokale Commits halten Karten-/Configänderung und Lizenzmitnahme/Verifikation fest. Historische V4-Einträge/Branchreferenzen/PDFs erhalten, keine History-Rewrites, externen Repository-/GitHub-/Remoteänderungen, keine Veröffentlichung und kein Push. Weitere Arbeit wartet auf den nächsten Auftrag.

AP02-Fortschritt V4-008: Version/Description/URLs/Autor-/Maintainer-/Pythonkonstanz im freigegebenen Umfang VERIFIED. V4-007 versioniert unveränderte historische Referenz. V4-009 ergänzt Herkunfts-/Datenschutzselbstauskunft und lediglich den Wunsch späterer anderer Branchbereinigung. AP01 technisch VERIFIED, vollständige Rechtsfreigabe weiterhin getrennt; AP03 NOT STARTED. Metadaten-/Versionsdiskrepanz beseitigt, Releasepolitik/Dependencies/Defaultinstall/Rechte/Serverreview weiterhin offen.

**Aktualisierung V4-010/V4-011:** Die oben datierten bisherigen Test-/Dependency-/Branchbefunde bleiben historische Ergebnisse. Jetzt sind alle fünf lokalen aktiven Trees PCD-frei und der aktuelle Manifest-Import-/Keyvertrag ist korrigiert. Apt-/Humble-Copy-Build, sieben Entry-Point-Imports und 43 Funktionstests erfolgreich; kein erneuter SciPy-/NumPy-Kompatibilitätsfehler in der getesteten Systemkombination. AP03-Gesamtgate echte Installation/check bleibt offen, zwei bestehende Lintfehler/zwei Copyright-Skips getrennt. AP04/AP06/AP08/AP10 IN PROGRESS, AP09 NOT STARTED mit dokumentierter Noble-Open3D-Hürde; ROS Index/Bloom/Buildfarm weiterhin NOT READY. Kein pauschaler Humble-/Jazzy-/Rechts-/Release-Qualitätsanspruch.

**Aktualisierung 14. Oktober 2026, V4-012..016:** Echte isolierte Dependencyinstallation/check, normale Share-Konfiguration, sichere separate Ausgabe, zwei Clean-Copy-Builds und Source-freie Laufzeit bestanden. AP03/AP04 und AP06 im bearbeiteten Umfang VERIFIED, AP08/AP10 IN PROGRESS; AP05/AP07/AP09 nicht begonnen. Keine SciPy/NumPy-Kompatibilitätswarnung in Apt-Kombination; externe Deprecations bleiben. Vollsuite zweimal86PASS/0FAIL/0SKIP, Source-frei37PASS/0FAIL/0SKIP. Frühere hier datierte Befunde bleiben historische Ergebnisse, nicht aktuelle Fehler. Rechtlicher Gesamtgate und ROS Index/Bloom/Buildfarm NOT READY. Details/Kommandoausgaben/Abnahmegrenzen in Kapitel16.

## 11. Open-Source-Lizenzanalyse und Copyright-Strategie

### 11.1 Zielsetzung

Die Untersuchung V4-002/V4-003 bereitete die autorisierte Lizenzwahl für `r3d_planner` und `r3d_preprocessor` vor. V4-004 ergänzt im selben Kapitel die nun verbindliche Apache-2.0-Entscheidung und ihre technische Eigenanteil-Implementierung (11.19/11.21); eine vollständige rechtliche Releasefreigabe folgt daraus nicht. Der nachfolgende Vergleich Apache-2.0/MIT/BSD-2-Clause/BSD-3-Clause dokumentiert weiterhin die Entscheidungsgrundlage. Die bereitgestellte Recherche favorisiert Apache-2.0; diese Präferenz wird anhand der Lizenztexte, ROS-Dokumentation und konkreter Projektbefunde geprüft.

Die Sekundärquelle „Lizenzwahl für den R3D-Planner.pdf“ wurde vollständig gelesen: sieben Seiten, bereitgestellt unter `/home/bauya/Downloads/Lizenzwahl für den R3D-Planner.pdf`, SHA-256 `49cea11cd79aebfa8f6cd3f832ff88818d4339cda0a0330376a394f18d32eb07`. Ihre internen Quellenmarker wie `【14†L95-L102】` enthalten keine unmittelbar auflösbaren bibliographischen URLs. Sie werden deshalb nicht als fertiger Primärquellennachweis übernommen. BSD-2-Clause wird gegenüber dem Schwerpunkt der PDF ausdrücklich ergänzt. Die in der PDF enthaltene Umsetzungscheckliste ist Quelleninhalt, kein Auftrag zum Anlegen einer LICENSE oder zum Ändern von Headern.

Die folgenden Aussagen werden nach ihrer Evidenz getrennt: **Lizenztext** bezeichnet Rechte/Bedingungen im gelesenen Original; **Gesetz** bezeichnet den gelesenen gesetzlichen Rahmen; **Projektbefund** bezeichnet Source-/Git-/Metadatenbeobachtungen; **Bewertung** bezeichnet die offengelegte fachliche Auswahlpräferenz; **offen** bezeichnet nicht nachgewiesene konkrete Rechtsverhältnisse. Die Primärquellen sind in 11.22 mit URL und Zugriff am 13. Oktober 2026 dokumentiert. Gesetzeslektüre ersetzt keine Prüfung der individuellen Verträge oder eine verbindliche rechtliche Freigabe.


Die Auftragserweiterung während V4-002 erlaubt nun ausdrücklich die externe Provenienzanalyse von `rsasaki0109/lidar_slam_ros2` und `RoboProjekt/lidar_odom` sowie ihrer konkret eingebundenen Drittkomponenten. Diese sind Analysegegenstände, keine zusätzlich in R3D eingefügten Implementierungen. Die vorhandene Analyse wird unter V4-002/V4-003 vervollständigt; es entsteht kein zweites Lizenzkapitel.

| Nachweisstufe | Bedeutung in diesem Kapitel |
| --- | --- |
| Verifiziert | Im aktuellen Durchlauf gelesene Datei, Lizenz-/Gesetzesquelle, API-Antwort oder tatsächlich ausgewerteter Git-Diff; nur für den angegebenen Umfang |
| Dokumentiert | Entwicklererklärung oder historischer Bericht; Quelle vorhanden, zugrunde liegende rechtliche/räumliche Tatsachen nicht unabhängig bestätigt |
| Abgeleitet | Fachliche Interpretation verifizierter/dokumentierter Fakten, z. B. bevorzugte Lizenzstrategie |
| Nicht verifiziert | Konkreter Nachweis fehlt; in der Modification Notice als NOT VERIFIED gekennzeichnet |
| Offen | Noch erforderliche rechtliche, technische oder Nutzerentscheidung; keine stillschweigende Zustimmung |

### 11.2 Lizenzanforderungen des R3D-Planners

Die vorhandenen Python-/ROS-Pakete sollen wissenschaftlich nachvollziehbar, kommerziell weiterverwendbar und künftig im ROS-Ökosystem verteilbar sein. Die Baseline enthält bereits funktionale Software; ihre Rechtekette beginnt nicht mit dem V4-Branch. Eine brauchbare Lizenz muss daher sowohl zum gewünschten Nutzungsmodell als auch zu bereits bestehenden Beitrags-, Daten- und Drittanbieterbedingungen passen.

| Anforderung | Herkunft | Bedeutung für die Untersuchung |
| --- | --- | --- |
| Öffentliche ROS-Distribution | Projektziel und rosdistro-Kriterien [Q07] | OSI-Lizenz, nachvollziehbarer Lizenztext und zutreffende Manifestangaben; keine Apache-Exklusivität |
| Kommerzielle und proprietäre Einbindung | Projektpräferenz | Permissive Lizenzkandidaten betrachten, ohne Hinweis-/Weitergabepflichten zu übergehen |
| Explizite Patentregelung | Bewertungspräferenz | Vorteil für einen Kandidaten mit ausdrücklichem begrenztem Patentgrant; keine Annahme konkreter Projektpatente |
| Persönliche Urheberbezeichnung | Nutzerwunsch und Projektheader | Tatsächliche Urheberschaft von Verwertungsbefugnis und Rechten Dritter unterscheiden |
| Bestehende ROS-Testtemplates | Projektbefund | OSRF-Hinweise und deren Apache-2.0-Bedingungen erhalten; keine pauschale Umdeklaration |
| Reproduzierbare Paketverteilung | Technisches Projektziel | Lizenztexte/Notices und konkrete Binärartefakte später im Packaging berücksichtigen |
| Zwei PCD-Beispielkarten | Projektbefund | Herkunft und Nutzungs-/Datenrechte separat prüfen; Softwarelizenz nicht automatisch auf Daten übertragen |
| Nachweis des Forschungsbeitrags | Forschungsziel | Vergleich/Bewertung, Rechteklärung, Entscheidung und technische Anwendung separat protokollieren |

Keine der vier Kandidaten kann fehlende Verteilungsrechte heilen. Diese Voraussetzung wird als Ausschlusskriterium behandelt, nicht durch eine günstige Bewertung kompensiert.


Die spätere gemeinsame Auslieferung von R3D und LiDAR-Odometrie wäre zusätzlich zu bewerten. Die hier belegte technische Kopplung über ROS-Nachrichten erlaubt keine automatische Relizenzierung des externen Codes.

### 11.3 Rechtliche Grundlagen

Permissive Lizenzen erlauben weitreichende Nutzung und Weitergabe unter begrenzten Bedingungen. Die untersuchten Texte verlangen grundsätzlich nicht, dass eigener unabhängiger Code oder jede Modifikation öffentlich unter derselben Lizenz angeboten wird. Proprietäre Produkte sind damit grundsätzlich möglich; übernommene Bestandteile verlieren dadurch ihre ursprünglichen Bedingungen nicht. „Permissiv“ bedeutet weder „gemeinfrei“ noch „ohne Pflichten“.

Die vier Bezeichnungen sind in der SPDX-Lizenzliste standardisiert und als OSI-anerkannt geführt: `Apache-2.0`, `MIT`, `BSD-2-Clause`, `BSD-3-Clause` [Q01-Q05]. SPDX identifiziert einen Text, bestätigt aber weder die Urheberschaft noch die Befugnis einer Person, fremden Code damit zu lizenzieren. Ein Setup-Metadatenstring ohne geklärte Provenienz ist deshalb kein ausreichender Projektfreigabenachweis.


Der folgende Rahmen bezieht sich auf das gelesene deutsche UrhG. Er ist nicht die Feststellung, dass bestimmte Verträge, Miturheberschaft oder ein Arbeitsverhältnis tatsächlich vorliegen.

| Ebene | Gesetzlicher Rahmen | Projektbezogene Konsequenz / offene Prüfung |
| --- | --- | --- |
| A: tatsächliche Urheberschaft | § 7: schöpferische Person; § 13: Anerkennung und Bezeichnung; § 69a: Schutz individueller Programmausdrucksformen, nicht bloßer Ideen/Grundsätze | Der bereits belegte Name Bastian Aumer kann eine eigene Urheberbezeichnung sein. Ob er alle Bestandteile geschaffen hat, ist damit nicht bewiesen |
| B: Nutzungs-/Verwertungsbefugnis | § 31: einfache/ausschließliche und begrenzte Nutzungsrechte; § 29: Urheberrecht grundsätzlich nicht übertragbar, Nutzungsrechtseinräumung getrennt | Persönliche Urheberbezeichnung und Befugnis zur Open-Source-Lizenzierung sind getrennte Fragen; Rechteumfang/Unterlizenzierung nachweisen |
| C: andere Beitragende | § 8: gemeinsames Werk bei nicht gesondert verwertbaren Anteilen; nicht jede Git-Mitwirkung ist automatisch Miturheberschaft | Beiträge und bestehende Lizenzen/Vereinbarungen prüfen; Git-Identitäten allein reichen nicht |
| D: Arbeitgeber / vertraglich Berechtigte | § 69b: vermögensrechtliche Ausübungsbefugnis des Arbeitgebers bei aufgaben-/weisungsbezogenen Arbeitnehmerprogrammen, soweit nichts anderes vereinbart | Beschäftigungs-/Dienst- und sonstige Projektverträge prüfen; aus Hochschul-E-Mail oder Forschungsmodul keine Rechtezuordnung ableiten |
| E: übernommener Code | § 69c: Zustimmung zu relevanten Vervielfältigungs-, Bearbeitungs-, Verbreitungs-/Zugänglichmachungshandlungen, gesetzliche Ausnahmen unberührt | Für fremde Teile tatsächliche Lizenz/Berechtigung nachweisen; eigene Header ersetzen keine Fremdrechte |
| F: Daten / Karten | §§ 2, 87a, 87b: mögliche Werk- bzw. Datenbankherstellerrechte, abhängig von tatsächlichen Voraussetzungen | Nicht jede Punktwolke ist ein geschütztes Werk; ebenso wenig ist jede Punktwolke automatisch frei nutzbar. Einzelfall und Verträge bleiben offen |

Quellen: [Q09-Q18]. Ein Copyright-Hinweis erzeugt keine Urheberschaft und überträgt keine Rechte. Auch ein persönlicher Hinweis bei tatsächlicher Urheberschaft beweist keine ausschließliche Lizenzierungsbefugnis. Vorhandene Fremdhinweise bleiben bestehen. V4-004 ergänzt persönliche SPDX-Attribution nur in bereits zugeordneten eigenen Dateien; unbekannte Autoren oder Rechte werden nicht erfunden.

### 11.4 Apache-2.0

Apache-2.0 ist ein permissiver Kandidat mit ausdrücklich geregelten Copyright- und begrenzten Patentgrants. Die Weitergabe setzt insbesondere Lizenz-/Hinweispflege und Änderungskennzeichnung voraus; eine eventuell mitgelieferte NOTICE-Attribution ist zu berücksichtigen. Eigenständige proprietäre Weiterverwendung bleibt grundsätzlich möglich. Der vollständige Text und die ASF-Erläuterungen sind maßgeblich [Q01/Q06/Q21].

Für R3D sprechen die ROS-Empfehlung und das gewünschte explizite Patentmodell. Dagegen steht mehr Pflegeaufwand als bei sehr kurzen Lizenztexten. Weder vorhandene Setup-Metadaten noch eine wissenschaftliche Präferenz ersetzen die Befugnis zur Anwendung. Die konkrete Patentbegrenzung steht in 11.16, die Abwägung in 11.18. Eine CLA-Pflicht oder automatische Urheberrechtsübertragung wird nicht aus der Lizenz abgeleitet.

### 11.5 MIT

MIT erlaubt Nutzung, Kopieren, Modifizieren, Zusammenführen, Veröffentlichen, Unterlizenzieren und Verkauf unter einer knappen Hinweisbedingung. Copyright- und Erlaubnistext müssen in Kopien bzw. wesentlichen Teilen erhalten bleiben. Der Text enthält Disclaimer, aber keine ausdrückliche Patentlizenz oder gesonderte Änderungs-/NOTICE-Klausel [Q02].

Die kurze Pflege ist ein nachvollziehbarer Vorteil für Forschungssoftware. Daraus folgt keine Entbindung von fremden Rechten, zusätzlichem Binärmaterial oder zwingendem Recht. Für R3D bleibt MIT eine mögliche Alternative bei stärkerer Gewichtung einfacher Lizenzpflege; das fehlende ausdrückliche Patentmodell ist unter der hier gewählten Präferenz ein Nachteil.

### 11.6 BSD-2-Clause

BSD-2-Clause erlaubt Nutzung und Weitergabe in Source- und Binärform mit oder ohne Modifikation. In Source sind Copyright, Bedingungen und Disclaimer zu erhalten; bei Binärweitergabe werden diese in Dokumentation oder Begleitmaterial wiedergegeben. Es gibt keine ausdrückliche Patent- oder Non-Endorsement-Klausel [Q03].

Der Text ist kurz und für die getrennte LiDAR-Komponente konkret belegt. Diese Tatsache verpflichtet R3D nicht automatisch, den gesamten eigenen Code ebenfalls BSD-2-Clause zu lizenzieren. Bei übernommener bzw. gemeinsam verteilter LiDAR-Software sind deren Originalbedingungen unabhängig von der R3D-Kandidatenwahl beizubehalten.

### 11.7 BSD-3-Clause

BSD-3-Clause ergänzt die Source-/Binär-Hinweisbedingungen der zweiklauseligen Variante um eine Einschränkung werblicher Billigung abgeleiteter Produkte durch Namen der Rechteinhaber/Beitragenden ohne vorherige schriftliche Erlaubnis. Es ist kein allgemeines Verbot der Attribution. Eine ausdrückliche Patentlizenz enthält der Text nicht [Q04].

Für R3D ist die Variante als möglicher eigener Kandidat und als Bedingung konkreter externer ROS-/PCL-/NDT-Dateien relevant. Die Prüfung zeigt, weshalb das unspezifische Wort BSD in älteren Paketmanifesten nicht ohne Blick in den tatsächlichen Text normalisiert werden darf.

### 11.8 Vergleich der Lizenzbedingungen

Die Tabelle vergleicht die vier Lizenztexte [Q01-Q04]; die nun gewählte und technisch angewandte Eigenanteil-Lizenz ist Apache-2.0 (11.19/11.21). „Keine ausdrückliche Klausel“ ist keine Aussage über eine mögliche konkludente Rechtslage im Einzelfall.

| Merkmal | Apache-2.0 | MIT | BSD-2-Clause | BSD-3-Clause |
| --- | --- | --- | --- | --- |
| SPDX-Kennung | Apache-2.0 | MIT | BSD-2-Clause | BSD-3-Clause |
| Kommerzielle Nutzung, Änderung, Weitergabe | Grundsätzlich erlaubt, Bedingungen beachten | Grundsätzlich erlaubt, Bedingungen beachten | Grundsätzlich erlaubt, Bedingungen beachten | Grundsätzlich erlaubt, Bedingungen beachten |
| Proprietäre Einbindung | Grundsätzlich möglich | Grundsätzlich möglich | Grundsätzlich möglich | Grundsätzlich möglich |
| Lizenz-/Copyright-Attribution | Lizenz und relevante Hinweise erhalten | Copyright und Erlaubnistext in Kopien/wesentlichen Teilen | Quellhinweise erhalten; bei Binärweitergabe in Begleitmaterial | Wie BSD-2-Clause |
| Explizite Patentlizenz | Abschnitt 3, begrenzter Contributor-Grant | Keine ausdrückliche Klausel | Keine ausdrückliche Klausel | Keine ausdrückliche Klausel |
| Patentbezogene Beendigung | Für den dort definierten Klagefall | Keine entsprechende Klausel | Keine entsprechende Klausel | Keine entsprechende Klausel |
| Änderungen kennzeichnen | Geänderte Dateien deutlich kennzeichnen, Abschnitt 4(b) | Keine gesonderte Änderungsklausel | Keine gesonderte Änderungsklausel | Keine gesonderte Änderungsklausel |
| NOTICE | Relevante Attribution aus mitgeliefertem NOTICE weitergeben, Abschnitt 4(d) | Kein eigenes NOTICE-Konzept | Kein eigenes NOTICE-Konzept | Kein eigenes NOTICE-Konzept |
| Marken / Werbung | Keine allgemeine Markenrechtseinräumung, Abschnitt 6 | Keine gesonderte Werbeklausel | Keine gesonderte Werbeklausel | Namen nicht ohne vorherige schriftliche Erlaubnis für Endorsement/Produktwerbung verwenden |
| Contributor-Regel | Abschnitt 5 für bewusst eingereichte Contributions; separate Vereinbarungen bleiben relevant | Beitragsbefugnis/-bedingungen separat absichern | Beitragsbefugnis/-bedingungen separat absichern | Beitragsbefugnis/-bedingungen separat absichern |
| Gewährleistung / Haftung | Ausschlussklauseln mit Grenzen des anwendbaren Rechts | Ausschlussklauseln | Ausschlussklauseln | Ausschlussklauseln |
| Text-/Pflegeumfang | Höher | Sehr kurz | Kurz | Kurz, zusätzliche Werbeklausel |
| ROS-2-Nutzung | Empfohlener neuer Projektkandidat | Grundsätzlich möglicher OSI-Kandidat | Grundsätzlich möglicher OSI-Kandidat | Grundsätzlich möglicher OSI-Kandidat |
| Wissenschaftliche Software | Reproduzierbare Hinweise und Patentmodell; Projektbewertung | Knappe Weiterverwendungsbedingungen; Projektbewertung | Knappe Source-/Binärbedingungen; Projektbewertung | Zusätzlich Endorsement-Regel; Projektbewertung |
| Lizenzkompatibilität | Konkrete Kombination offen | Konkrete Kombination offen | Konkrete Kombination offen | Konkrete Kombination offen |
| Gewährleistung vs Haftung | Abschnitte 7 bzw. 8 getrennt; keine Garantie der Wirksamkeit | Text enthält beide Ausschlüsse | Text enthält beide Ausschlüsse | Text enthält beide Ausschlüsse |

Non-Endorsement betrifft die werbliche Billigung abgeleiteter Produkte. Es verbietet nicht die vorgeschriebene Attribution und ist kein allgemeines Namensnennungsverbot. Apache-Markenregeln betreffen die Kennzeichen des jeweiligen Lizenzgebers, nicht ausschließlich die ASF [Q01/Q04].

#### 11.8.1 Korrekturen und Grenzen der bereitgestellten Recherche

Die Sekundärquelle wird inhaltlich übernommen, aber die folgenden Pauschalaussagen werden transparent korrigiert. Die Original-PDF bleibt unverändert.

| ID | Aussage / Fundstelle der PDF | Prüfung und Korrektur | Nachweis |
| --- | --- | --- | --- |
| K01 | Uneingeschränkte Nutzung, Seiten 1-2 | Weitreichende Erlaubnisse gelten unter den jeweiligen Bedingungen; Hinweis-/Weitergabepflichten bleiben | Q01-Q04 |
| K02 | Umfassender Patentschutz bzw. keine Patentlizenz „stillschweigend“, Seiten 1-3/6 | Apache gewährt nur bestimmte lizenzierbare Contributor-Patentansprüche; MIT/BSD enthalten keine ausdrückliche Patentklausel. Eine konkludente Lizenz wird hier weder angenommen noch ausgeschlossen | Q01 Abschnitt 3; Q02-Q04 |
| K03 | NOTICE-Datei immer mitführen, Seite 3 | Abschnitt 4(d) knüpft an ein vorhandenes NOTICE des Werks an; relevante Attribution darf an den dort genannten Stellen erscheinen. Nicht jedes neue Apache-Projekt muss allein deshalb ein leeres NOTICE erzeugen | Q01 Abschnitt 4(d); Q06 |
| K04 | Keine Vorlizenzierung, daher Wechsel ohne Genehmigung möglich, Seite 3 | Nicht belegt und nicht tragfähig: fehlende Lizenzdatei schafft keine fremden Rechte; fremde Apache-Templates existieren bereits, Rechte an Importcode bleiben offen | Projektbefund 11.9; Q09-Q14 |
| K05 | package.xml müsse genau eine Lizenz nennen, Seite 4 | REP-149 erlaubt mehrere license-Tags und verlangt die zutreffende Abbildung mehrerer im Paket vorkommender Lizenzen | Q08, license multiple |
| K06 | Alle Dependencies kompatibel / keine Copyleft-Komponenten, Seiten 1/3/4/6 | Direkte Hauptlizenzen und konkrete Binärpakete unterscheiden. Das lokal gelesene NumPy-Artefakt nennt zusätzlich GCC-Runtime und libquadmath; vollständige transitive Freigabe fehlt | 11.11; Q23 |
| K07 | Niemand könne Ansprüche gegen Entwickler geltend machen, Seite 4 | Nicht haltbar. Lizenzdisclaimer sind keine generelle Anspruchssperre; zwingendes Recht und konkrete Vertrags-/Haftungsumstände bleiben relevant | Q01 Abschnitte 7-9; Q02-Q04; Q19/Q20 |
| K08 | Eigene PCD-Daten seien standardmäßig MIT/Apache, Seite 6 | Weder Eigenherstellung noch Ausgabe durch den Analyzer wählt automatisch eine Datenlizenz; Herkunft und mögliche Schutz-/Vertragsrechte sind gesondert zu prüfen | Q17/Q18; 11.12 |
| K09 | CLA als typische Rechteübertragung, Seite 4 | Der Apache-Lizenztext verlangt kein allgemeines CLA und keine Urheberrechtsübertragung. ASF-Beitragsprozesse dürfen nicht mit der Lizenz selbst gleichgesetzt werden | Q01 Abschnitt 5; Q06; Q13 |
| K10 | Apache sei generell der einfachste Weg bei Patentbedenken, Seiten 4-5 | Die Empfehlung gilt nur unter der in 11.18 offengelegten Präferenz und geklärten Rechten. Kein Freedom-to-Operate-/Patentgutachten und keine automatische Lösung von Firmenvorgaben | Q01/Q06; 11.19 |
| K11 | ROS-freundliche Lizenz allein reiche, Seite 3; Apache erfülle rosdep/Bloom-Anforderungen, Seite 7 | Lizenzvergleich ersetzt keine Prüfung von Dependencies, Installation, Versions-/Release-Metadaten oder externe Aufnahmeentscheidung | Q07/Q08; Abschnitte 3 und 9 |
| K12 | Apache schütze vor Namensverwendung, Seite 2/5 | Apache 6 gewährt keine allgemeinen Markenrechte; BSD-3-Clause enthält eine spezielle Endorsement-Beschränkung. Daraus folgt kein vollständiger Name-/Markenschutz | Q01/Q04 |


#### 11.8.2 Weitergabe, Modifikation und Haftungsgrenzen


Für eine spätere Anwendung sind Übernahme, unveränderte Weitergabe, modifizierte Dateien und reine externe Nutzung getrennt zu behandeln. Bei Apache-Werken gehören die Lizenzkopie, Änderungskennzeichnung, relevante Source-Hinweise und gegebenenfalls NOTICE-Attribution zum dokumentierten Verfahren; andere Bedingungen für eigene Modifikationen dürfen die Pflichten am übernommenen Werk nicht beseitigen [Q01 Abschnitt 4; Q21]. Bei MIT stehen Copyright-/Erlaubnistext im Vordergrund; BSD unterscheidet Source-Erhaltung und Begleitmaterial bei Binärdistribution [Q02-Q04].

Die ASF empfiehlt geeignete Lizenz-/Dateihinweise und erläutert, dass fremde Komponenten eigene Texte/Notices erfordern können [Q06]. Eine spätere RELEASE-/Installationsprüfung muss zeigen, welche Texte im tatsächlich ausgelieferten Paket liegen. Ein selbstgewählter Copyrightname darf dabei die OSRF-Attribution der Testtemplates nicht ersetzen.

CLA, DCO oder andere Beitragsregeln sind gesonderte organisatorische Entscheidungen. Apache Abschnitt 5 regelt bewusst eingereichte Contributions, macht aber nicht jede Dateieinsendung unabhängig von ihrer Berechtigung wirksam [Q21]. Für R3D ist kein bestehendes CLA-/DCO-Verfahren belegt.

**Haftung:** Alle vier Texte enthalten Disclaimer. Daraus folgt keine allgemeine Unangreifbarkeit. Beispielsweise untersagt § 276 Absatz 3 BGB den vorausgehenden Erlass der Vorsatzhaftung; § 309 Nr. 7 BGB setzt im Anwendungsbereich der AGB-Kontrolle Grenzen für bestimmte Haftungsausschlüsse. Die konkrete Wirksamkeit, Vertragsart und weitere zwingende Vorschriften bleiben zu prüfen [Q19/Q20]. Es wird keine Zusicherung völliger Haftungsfreiheit ausgesprochen.

### 11.9 Copyright und Urheberschaft

| Kategorie | Repository-/Historiennachweis | Aussagekraft und Grenze |
| --- | --- | --- |
| Eigene Namenshinweise | 18 Python-Dateien mit `Copyright (c) Bastian Aumer`; Commit `c65642f…` fügte jeweils zehn Kommentarzeilen hinzu | Technisch belegter Name; kein vollständiger Rechtekettennachweis und kein neuer Grant |
| Git-Provenienz | Root-Import `ca9f44930a44391577c8fd822c0d7f557fcd9da4`; V3 `3752404a08867e9e6f3725300b88e148d4d5be37`; Baseline `c65642fe56015556f696364a724cb5b976a27888`; historischer Bericht Kapitel 3/8/10 und Anhang A | Git belegt Ablage/Änderungen, nicht allein tatsächliche Urheberschaft, Vertragslage oder Erlaubnis zur Lizenzwahl |
| Direkt enthaltene Fremdquelltexte | Beide Pakete enthalten test_copyright.py, test_flake8.py, test_pep257.py mit OSRF-Copyright 2015 bzw. Flake8 2017 und Apache-2.0-Notice | Sechs konkrete Fremdtemplates sind vorhanden; Hinweise erhalten und im späteren Distributionsumfang berücksichtigen |
| Template-Abgleich | Alle sechs Dateien stimmen mit den lokal installierten offiziellen Humble-Templates nach Ersetzung von EmPy `@@` durch `@` bytegenau überein; Upstream-Beispiel Q51 | Keine zusätzliche funktionale Modifikation dieser Templates nachgewiesen; Anwendung einer generierten Vorlage ist keine eigene Urheberschaft am Vorlagentext |
| Externe Bibliotheken | Runtime-/Launchimporte, Manifeste und Setup | Import allein ist kein Kopieren der gesamten Libraryimplementation; wissenschaftliche Libraries nicht als vendorte Source-Trees identifiziert |
| Modifizierter fremder Algorithmuscode | Keine weitere zuverlässig zuordenbare Upstream-Implementation anhand Dateien/Notices identifiziert | „Nicht identifiziert“ ist kein Beweis vollständiger Eigenentwicklung; Herkunft vor dem Root-Import bleibt offen |
| Generierte Artefakte | Neun versionierte cpython-310-Bytecode-Dateien und ament-Marker/Setup-Gerüste | Bytecode ist kein unabhängiger Rechtegrant; Inhalt/Provenienz nicht allein aus Dateiformat bestimmen |

Die Header-/Templateprüfung V4-002/V4-003 war lesend. V4-004 ergänzt danach die ausdrücklich freigegebenen eigenen SPDX-Kommentare; Fremdnotices bleiben byteidentisch. Der persönliche Name ist für nachgewiesene eigene Beiträge grundsätzlich als gewünschte Urheberbezeichnung plausibel; eine zentrale exklusive Rechteinhaberschaft des gesamten Repositorys ist nicht nachgewiesen. Für den eigenen R3D-Funktionscode liegt nun die Erklärung alleiniger Entwicklung vor (11.10). Bekannte Fremdtemplates bleiben davon ausgenommen; Arbeitgeber-/Vertragsrechte und Lizenzierungsbefugnis sind weiterhin nicht unabhängig geprüft.

### 11.10 Entwicklererklärung Bastian Aumer

**Dokumentierte Erklärung des Projektentwicklers, eingegangen am 13. Oktober 2026 im ergänzten Nutzerauftrag; keine unabhängige rechtsverbindliche Prüfung:**

1. Bastian Aumer erklärt, alleiniger Entwickler des R3D-Planners zu sein.
2. Bastian Aumer erklärt, alleiniger Entwickler des R3D-Preprocessors zu sein.
3. An der Entwicklung dieser beiden Komponenten seien keine weiteren Entwickler beteiligt gewesen.
4. Für die Bereitstellung der LiDAR-Odometrie werde externe Software verwendet.
5. Diese Implementierung basiere auf LiDAR-SLAM bzw. lidar_slam_ros2.
6. Bastian Aumer habe Anpassungen an dieser externen LiDAR-Odometrie vorgenommen.
7. Das Copyright des eigenständig entwickelten R3D-Projektcodes solle auf seinen persönlichen Namen laufen.
8. Ursprüngliche Copyright- und Lizenzrechte fremden Quellcodes sollen bei den ursprünglichen Rechteinhabern verbleiben.
9. Eigene Modifikationen externen Codes sollen separat gekennzeichnet werden.

Diese Erklärung konkretisiert die bisher offene Zuordnung der eigenen Funktionskomponenten. Die sechs nachgewiesenen ROS-Testtemplates und externe Bibliotheken sind weiterhin Fremdmaterial. Die Erklärung wird nicht als Nachweis einer exklusiven Rechteinhaberschaft am gesamten Repository einschließlich solcher Teile oder Kartendaten verstanden. § 7 betrifft Urheberschaft, § 8 gegebenenfalls gemeinsame Werke, § 31 Nutzungsrechte und § 69b mögliche Arbeitgeberbefugnisse; eine persönliche Attribution beantwortet nicht automatisch die anderen Fragen [Q09-Q11/Q14].

**Unter V4-004 angewandte Form in den 18 zugeordneten eigenen Python-Dateien:**

```text
SPDX-FileCopyrightText: 2026 Bastian Aumer
```

**Apache-2.0 wurde im Folgeauftrag ausdrücklich gewählt und für diese eigenen Dateien freigegeben:**

```text
SPDX-License-Identifier: Apache-2.0
```

Beide SPDX-Zeilen sind nun zusätzliche Kommentare in den 18 eigenen Dateien; der bisherige eigene Copyright-Hinweis bleibt erhalten. Die Erklärung wird durch die aktuelle Lizenzentscheidung bekräftigt, aber nicht zu einer unabhängigen Rechtsprüfung. Fremdhinweise und BSD-Lizenzangaben externer Dateien bleiben unverändert; genaue Pfade und Prüfumfang in 11.21.2.

### 11.11 Drittanbieterbibliotheken

#### 11.11.1 Methode und Reichweite

Direkte Imports wurden statisch per AST erfasst, ohne R3D- oder Bibliotheksmodule auszuführen. Lokale installierte Versionsmetadaten wurden mit `importlib.metadata` und ROS-Manifesten unter `/opt/ros/humble/share/<Paket>/package.xml` gelesen. Das Repository pinnt diese Versionen nicht; sie sind eine Beobachtung dieser Workstation, kein festgelegter künftiger Release-Satz. Upstream-Lizenz-/Paketdateien mit Versionstag bzw. Humble-Branch wurden zusätzlich gelesen. Bewegliche Branchquellen können einen anderen Patchstand als die lokale Installation zeigen, insbesondere TF2 lokal 0.25.23 versus gelesener Humble-Branch 0.25.24.

Die Tabelle benennt die nachgewiesene Hauptdeklaration, nicht die vollständige Lizenz jedes enthaltenen Untermoduls oder jedes binären/transitiven Bestandteils. Ältere ROS-Manifeste schreiben etwa „BSD“ oder „Apache License 2.0“; die SPDX-Normalisierung ist als Auswertung gekennzeichnet. BSD-3-Clause wird bei den konkret verwendeten Python-Cloud-/TF2-Modulen anhand ihrer drei Klauseln, einschließlich Non-Endorsement, belegt [Q29/Q30].

#### 11.11.2 Direkte Runtime-/Launch-Abhängigkeiten

A = bei Mitverteilung Apache-Lizenz und einschlägige Hinweise/Änderungs-/NOTICE-Bedingungen prüfen. B = BSD-Hinweise, Bedingungen und Disclaimer in Source bzw. Binärbegleitmaterial, keine unautorisierte Produktbilligung. M = MIT-Copyright-/Erlaubnistext in Kopien bzw. wesentlichen Teilen. Diese Kürzel beschreiben die Lizenztexte; reine externe Installation und eigene Weiterverteilung sind getrennte Nutzungssituationen.

| Komponente | Verwendete Funktion | Lizenz | SPDX | Quelle | Distributionsart | Relevante Pflichten | Prüfstatus |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ROS 2 Humble | Zielökosystem; externe Installation | Keine einheitliche Gesamtprojektlizenz; einzelne Pakete separat | Kein einheitlicher Gesamtidentifier | Q22, nachstehende Paketquellen | Externe Distribution | Nicht alle ROS-Bibliotheken pauschal Apache nennen | Verifiziert: Aggregat, Einzelpakete separat |
| rclpy 3.3.22 | Node, Publisher/Subscriber, Parameter, Action; Import in beiden Paketen | Apache License 2.0 → Apache-2.0 | Apache-2.0 | Q31 | Extern installiert / Runtime- oder Launch-Import | A; Middleware/transitive Implementierungen nicht vollständig inventarisiert | Verifiziert: LICENSE oder Paketdeklaration; keine Gesamtartefaktfreigabe |
| nav2_msgs 1.1.20 | ComputePathToPose Server/Client; Planner/RViz | Apache-2.0 | Apache-2.0 | Q32 | Extern installiert / Runtime- oder Launch-Import | A; Action-Nutzung ist kein Vendoring des Nav2-Stacks | Verifiziert: LICENSE oder Paketdeklaration; keine Gesamtartefaktfreigabe |
| geometry_msgs 4.9.2 | Pose, Point, Transform, Twist; Planner-/Navigationsmodule | Apache License 2.0 → Apache-2.0 | Apache-2.0 | Q33 | Extern installiert / Runtime- oder Launch-Import | A | Verifiziert: LICENSE oder Paketdeklaration; keine Gesamtartefaktfreigabe |
| nav_msgs 4.9.2 | Path und Odometry; Planner/Follower/Poseadapter | Apache License 2.0 → Apache-2.0 | Apache-2.0 | Q34 | Extern installiert / Runtime- oder Launch-Import | A | Verifiziert: LICENSE oder Paketdeklaration; keine Gesamtartefaktfreigabe |
| sensor_msgs 4.9.2 | PointCloud2/PointField; Filter und Publisher | Apache License 2.0 → Apache-2.0 | Apache-2.0 | Q35 | Extern installiert / Runtime- oder Launch-Import | A | Verifiziert: LICENSE oder Paketdeklaration; keine Gesamtartefaktfreigabe |
| sensor_msgs_py 4.9.2 | point_cloud2.read_points; Follower | Manifest BSD; verwendetes point_cloud2-Modul: BSD-3-Clause | BSD-3-Clause, bezogen auf benannte Quelle | Q29/Q36 | Extern installiert / Runtime-Import | B; Willow-Garage-Notice im externen Modul; nicht in R3D kopiert | Verifiziert: Haupttext bzw. konkreter Header; Gesamtartefakt offen |
| tf2_ros / tf2_ros_py 0.25.23 | Buffer, TransformListener, StaticTransformBroadcaster; Odometry/RViz/TF-Helfer | Manifest BSD; geprüfte Python-Header: BSD-3-Clause | BSD-3-Clause, bezogen auf benannte Quelle | Q30/Q37/Q38 | Extern installiert / Runtime-Import | B; Importname tf2_ros und Python-Provider tf2_ros_py unterscheiden; keine Dependency-Korrektur | Verifiziert: Haupttext bzw. konkreter Header; Gesamtartefakt offen |
| std_msgs 4.9.2 | ColorRGBA; Planner | Apache License 2.0 → Apache-2.0 | Apache-2.0 | Q39 | Extern installiert / Runtime- oder Launch-Import | A; direkte Manifestlücke bleibt technisch offen | Verifiziert: LICENSE oder Paketdeklaration; keine Gesamtartefaktfreigabe |
| visualization_msgs 4.9.2 | Marker; Pfadvisualisierung | Apache License 2.0 → Apache-2.0 | Apache-2.0 | Q40 | Extern installiert / Runtime- oder Launch-Import | A; Upstream-Quellenstand kann abweichen | Verifiziert: LICENSE oder Paketdeklaration; keine Gesamtartefaktfreigabe |
| std_srvs 4.9.2 | Trigger; RViz-Neukalibrierung | Apache License 2.0 → Apache-2.0 | Apache-2.0 | Q41 | Extern installiert / Runtime- oder Launch-Import | A | Verifiziert: LICENSE oder Paketdeklaration; keine Gesamtartefaktfreigabe |
| launch 1.0.15 | LaunchDescription, Bedingungen, OpaqueFunction | Apache License 2.0 → Apache-2.0 | Apache-2.0 | Q42 | Extern installiert / Runtime- oder Launch-Import | A; externe Launchbibliothek | Verifiziert: LICENSE oder Paketdeklaration; keine Gesamtartefaktfreigabe |
| launch_ros 0.19.14 | Node-Actions / Parameterweitergabe | Apache License 2.0 → Apache-2.0 | Apache-2.0 | Q43 | Extern installiert / Runtime- oder Launch-Import | A | Verifiziert: LICENSE oder Paketdeklaration; keine Gesamtartefaktfreigabe |
| ament_index_python 1.4.1 | Share-Verzeichnisfindung | Apache License 2.0 → Apache-2.0 | Apache-2.0 | Q44 | Extern installiert / Runtime- oder Launch-Import | A | Verifiziert: LICENSE oder Paketdeklaration; keine Gesamtartefaktfreigabe |
| NumPy 1.26.4 | Arrays, Cloud-/Voxel-/Geometrieoperationen in beiden Paketen | Hauptlizenz BSD-3-Clause | BSD-3-Clause, bezogen auf benannte Quelle | Q24; zusätzlich Q23 und lokales LICENSE | Extern installiert / Runtime-Import | B; tatsächliches Wheel enthält weitere Lizenzteile, siehe 11.11.3 | Verifiziert: Haupttext bzw. konkreter Header; Gesamtartefakt offen |
| SciPy 1.8.0 | scipy.spatial.KDTree; Planner | Hauptlizenz BSD-3-Clause | BSD-3-Clause, bezogen auf benannte Quelle | Q25 | Extern installiert / Runtime-Import | B; Debian-/Ubuntu-Binärumfang separat prüfen | Verifiziert: Haupttext bzw. konkreter Header; Gesamtartefakt offen |
| NetworkX 3.4.2 | Graph/Knoten/Kanten; Planner | BSD-3-Clause | BSD-3-Clause, bezogen auf benannte Quelle | Q26 | Extern installiert / Runtime-Import | B; keine Bibliotheksimplementation im Projekt gebündelt | Verifiziert: Haupttext bzw. konkreter Header; Gesamtartefakt offen |
| Open3D 0.19.0 | PCD-Laden/Voxelisierung/Export; beide Pakete | Hauptlizenz MIT | MIT | Q27 | Extern installiert / Runtime-Import | M; eingebundene native/GUI-/Web-Komponenten nicht als vollständig MIT freigegeben | Verifiziert: Haupttext; Gesamtartefakt offen |
| PyYAML 5.4.1 | SafeLoader, UniqueLoader, Konfiguration/Tests | MIT | MIT | Q28 | Extern installiert / Runtime-Import | M; externe Bibliothek | Verifiziert: Haupttext; Gesamtartefakt offen |
| r3d_preprocessor | Workspace-interner Analyzer/Publisher im Plannerlaunch | Autorisierte eigene Software: Apache-2.0, unter V4-004 gewählt/implementiert | Apache-2.0 | Projektmanifeste/Setup, LICENSE, 11.21 | Workspace-intern | Eigene Apache-Bedingungen; Kartendaten und Fremdmaterial separat | Lizenzdateien statisch verifiziert; vollständige Rechts-/Releaseabnahme offen |

#### 11.11.3 Packaging-/Testbedarf und konkrete Binärgrenzen

| Komponente | Verwendung | Lizenzbefund / Quelle | Prüfumfang |
| --- | --- | --- | --- |
| setuptools 59.6.0 | setup.py / Paketierung | MIT, taggebundener Upstream-Text [Q45]; lokales Metadatenfeld UNKNOWN | Upstream-Beleg, kein vollständiger Audit aller mitgelieferten setuptools-Teile |
| pytest 6.2.5 | Funktionstests und Linter-Sammlung | Lokal MIT; zusätzlich Upstream-Lizenztext gelesen [Q46] | Main-Quelle ist kein versionsidentischer Artefaktbeweis; lokaler Metadatenbefund gesondert |
| ament_copyright 0.12.15 | Copyright-Linter, aktuell übersprungen | Lokal Apache License 2.0 → Apache-2.0 [Q47] | Installiertes Publisher-Manifest gelesen; Web-Cachezugriff scheiterte |
| ament_flake8 0.12.15 | Python-Linter | Apache-2.0-Deklaration [Q48] | Eigenständige nachgelagerte Flake8-Dependencies nicht vollständig geprüft |
| ament_pep257 0.12.15 | Docstring-Linter | Manifest nennt Apache License 2.0 und MIT [Q49] | Mehrere im Paket genannte Lizenzen, keine beliebige Wahl eines einzelnen Tags behauptet |
| Python 3.10 / Standardbibliothek | math, heapq, os, pathlib, struct, traceback | PSF-Lizenzfamilie, u. a. PSF-2.0; eingebundene Teile mit weiteren Bedingungen [Q50] | Externer Interpreter; kein vendorter CPython-Tree; keine pauschale Lizenz aller Standardmodule behauptet |

Im lokalen `numpy-1.26.4.dist-info/LICENSE.txt` sind zusätzlich u. a. OpenBLAS, LAPACK, MIT-/Zlib-Teile, GCC-Runtime und libquadmath dokumentiert. Der GCC-Runtime-Block nennt im historischen Bezeichner `GPL-3.0-with-GCC-exception` libgfortran mit GPL Version 3 oder später und Runtime Exception 3.1; libquadmath ist dort `LGPL-2.1-or-later`. Dieser Wortlaut wird nicht als modernisierte abschließende SPDX-Erklärung aller NumPy-Binaries ausgegeben. Der offizielle NumPy-Wheel-Lizenztext bestätigt die zusätzliche Artefaktebene [Q23].

Das ist ein konkreter Gegenbefund zur Aussage, es gebe ausschließlich MIT-/BSD-Bedingungen in der gesamten Laufzeitumgebung. Es beweist umgekehrt weder eine GPL-Lizenzierung des R3D-Quellcodes noch eine Unmöglichkeit seiner Apache-Veröffentlichung. Eine Distribution ausschließlich des eigenen Sourcepakets mit Systemdependencies ist von einem mitgelieferten Wheel, Container oder Bundle zu unterscheiden. Vor einem solchen Bundle sind die tatsächlich enthaltenen Artefakte, Notices, Ausnahmen und gegebenenfalls weitere Pflichten versions-/plattformbezogen zu prüfen.

**Ergebnis:** Direkte Bibliotheks-Hauptdeklarationen sind nachvollziehbar erfasst. Eine vollständige transitive SBOM, binäre Lizenzprüfung oder pauschale Kompatibilitätsfreigabe ist nicht erbracht. Es wurde nichts installiert, deinstalliert oder aktualisiert; Dependencyangaben in package.xml bleiben unverändert. Nur die beiden license-Felder wurden unter AP01 geändert; AP03 bleibt NOT STARTED.

**Aktualisierung V4-005:** Die folgende 60-Pfad-Inventur ist historisch. Beide PCD-Einträge und SHA-Angaben bezeichnen den früheren Bestand; aktueller Tree enthält diese Daten nicht mehr. Allgemeine Nutzerdaten und temporäre Testfixtures sind nicht als mitgelieferte Standardkarte lizenziert.

### 11.12 Lizenzinventar

Die folgende historische Inventur V4-002/V4-003 umfasst alle 60 damals zum Eingang versionierten Dateien: die 59 Baseline-Dateien plus das bestehende zentrale V4-Protokoll. Damit sind alle 26 Python-Dateien einzeln erfasst. Die unversionierte historische PDF und das externe Recherche-PDF werden anschließend separat aufgeführt. „Eigenanteil laut Erklärung“ ist eine dokumentierte Zuordnung, keine unabhängige Rechtsprüfung. Für normale Projekttexte ohne ausdrücklichen Hinweis wird keine Lizenz erfunden. Die Tabelle hält den Zustand **vor V4-004** und den damaligen Änderungsbedarf fest; der aktuelle Delta mit Root-LICENSE, 18 SPDX-Ergänzungen und zwei Manifesten steht in 11.21.2. Danach umfasst der versionierte Tree 61 Dateien. Historische Copyright-/Lizenzbefunde werden nicht rückwirkend umgeschrieben.

| Dateipfad vor V4-004 | Damaliger Copyright-Hinweis | Damaliger Lizenzhinweis | Erkennbare Herkunft | Eigenentwicklung / Fremdcode | Damaliger Änderungsbedarf; aktueller Delta 11.21.2 |
| --- | --- | --- | --- | --- | --- |
| `INSTALL.md` | Kein eigener Copyright-Dateiheader | Keine eigene Lizenzdeklaration | Projekt-/Konfigurations-/Gerüstbestand; individuelle Herkunft nicht rechtlich geprüft | Projektbestand | Später Distributionsumfang, Rechte und geeignete Lizenzzuordnung prüfen |
| `README.md` | Kein eigener Copyright-Dateiheader | Keine eigene Lizenzdeklaration | Projekt-/Konfigurations-/Gerüstbestand; individuelle Herkunft nicht rechtlich geprüft | Projektbestand | Später Distributionsumfang, Rechte und geeignete Lizenzzuordnung prüfen |
| `README_r3d_planner.txt` | Kein eigener Copyright-Dateiheader | Keine eigene Lizenzdeklaration | Projekt-/Konfigurations-/Gerüstbestand; individuelle Herkunft nicht rechtlich geprüft | Projektbestand | Später Distributionsumfang, Rechte und geeignete Lizenzzuordnung prüfen |
| `docs/ARCHITECTURE.md` | Kein eigener Copyright-Dateiheader | Keine eigene Lizenzdeklaration | Projekt-/Konfigurations-/Gerüstbestand; individuelle Herkunft nicht rechtlich geprüft | Projektbestand | Später Distributionsumfang, Rechte und geeignete Lizenzzuordnung prüfen |
| `docs/CONFIGURATION.md` | Kein eigener Copyright-Dateiheader | Keine eigene Lizenzdeklaration | Projekt-/Konfigurations-/Gerüstbestand; individuelle Herkunft nicht rechtlich geprüft | Projektbestand | Später Distributionsumfang, Rechte und geeignete Lizenzzuordnung prüfen |
| `docs/KNOWN_ISSUES.md` | Kein eigener Copyright-Dateiheader | Keine eigene Lizenzdeklaration | Projekt-/Konfigurations-/Gerüstbestand; individuelle Herkunft nicht rechtlich geprüft | Projektbestand | Später Distributionsumfang, Rechte und geeignete Lizenzzuordnung prüfen |
| `docs/README_AUDIT.md` | Kein eigener Copyright-Dateiheader | Keine eigene Lizenzdeklaration | Projekt-/Konfigurations-/Gerüstbestand; individuelle Herkunft nicht rechtlich geprüft | Projektbestand | Später Distributionsumfang, Rechte und geeignete Lizenzzuordnung prüfen |
| `docs/REFERENCE_COMPARISON.md` | Kein eigener Copyright-Dateiheader | Keine eigene Lizenzdeklaration | Projekt-/Konfigurations-/Gerüstbestand; individuelle Herkunft nicht rechtlich geprüft | Projektbestand | Später Distributionsumfang, Rechte und geeignete Lizenzzuordnung prüfen |
| `docs/V3_IMPLEMENTATION.md` | Kein eigener Copyright-Dateiheader | Keine eigene Lizenzdeklaration | Projekt-/Konfigurations-/Gerüstbestand; individuelle Herkunft nicht rechtlich geprüft | Projektbestand | Später Distributionsumfang, Rechte und geeignete Lizenzzuordnung prüfen |
| `docs/V4_ROS_COMPLIANCE_DEVELOPMENT.md` | Kein eigener Copyright-Dateiheader | Keine eigene Lizenzdeklaration | V4-Forschungsprotokoll, V4-001 und folgende | Dokumentation | Forschungsinhalt von Lizenzanwendung trennen; Dokumentationsrechte später festlegen |
| `r3d_planner/README.txt` | Kein eigener Copyright-Dateiheader | Keine eigene Lizenzdeklaration | Projekt-/Konfigurations-/Gerüstbestand; individuelle Herkunft nicht rechtlich geprüft | Projektbestand | Später Distributionsumfang, Rechte und geeignete Lizenzzuordnung prüfen |
| `r3d_planner/config/planner_config.yaml` | Kein eigener Copyright-Dateiheader | Keine eigene Lizenzdeklaration | Projekt-/Konfigurations-/Gerüstbestand; individuelle Herkunft nicht rechtlich geprüft | Projektbestand | Später Distributionsumfang, Rechte und geeignete Lizenzzuordnung prüfen |
| `r3d_planner/config/r3d_planner_params.yaml` | Kein eigener Copyright-Dateiheader | Keine eigene Lizenzdeklaration | Projekt-/Konfigurations-/Gerüstbestand; individuelle Herkunft nicht rechtlich geprüft | Projektbestand | Später Distributionsumfang, Rechte und geeignete Lizenzzuordnung prüfen |
| `r3d_planner/config/robots/Go2W.yaml` | Kein eigener Copyright-Dateiheader | Keine eigene Lizenzdeklaration | Projekt-/Konfigurations-/Gerüstbestand; individuelle Herkunft nicht rechtlich geprüft | Projektbestand | Später Distributionsumfang, Rechte und geeignete Lizenzzuordnung prüfen |
| `r3d_planner/launch/follower.launch.py` | Copyright (c) Bastian Aumer | Kein Datei-Lizenzgrant / kein SPDX-License-Identifier | R3D-Eigenentwicklung laut Entwicklererklärung; vorhandener Namensheader | Eigenanteil laut Erklärung | Nach Freigabe eigene Attribution und passenden Dateilizenzbezug prüfen |
| `r3d_planner/launch/map.launch.py` | Copyright (c) Bastian Aumer | Kein Datei-Lizenzgrant / kein SPDX-License-Identifier | R3D-Eigenentwicklung laut Entwicklererklärung; vorhandener Namensheader | Eigenanteil laut Erklärung | Nach Freigabe eigene Attribution und passenden Dateilizenzbezug prüfen |
| `r3d_planner/launch/planner.launch.py` | Copyright (c) Bastian Aumer | Kein Datei-Lizenzgrant / kein SPDX-License-Identifier | R3D-Eigenentwicklung laut Entwicklererklärung; vorhandener Namensheader | Eigenanteil laut Erklärung | Nach Freigabe eigene Attribution und passenden Dateilizenzbezug prüfen |
| `r3d_planner/launch/preprocessor.launch.py` | Copyright (c) Bastian Aumer | Kein Datei-Lizenzgrant / kein SPDX-License-Identifier | R3D-Eigenentwicklung laut Entwicklererklärung; vorhandener Namensheader | Eigenanteil laut Erklärung | Nach Freigabe eigene Attribution und passenden Dateilizenzbezug prüfen |
| `r3d_planner/package.xml` | Kein eigener Copyright-Dateiheader | Manifest: TODO: License declaration | ROS-Paketmetadaten | Projektmetadaten | Nach Freigabe tatsächliche Lizenz/-en deklarieren |
| `r3d_planner/points.txt` | Kein eigener Copyright-Dateiheader | Keine eigene Lizenzdeklaration | Projekt-/Konfigurations-/Gerüstbestand; individuelle Herkunft nicht rechtlich geprüft | Projektbestand | Später Distributionsumfang, Rechte und geeignete Lizenzzuordnung prüfen |
| `r3d_planner/r3d_planner/__init__.py` | Kein eigener Copyright-Dateiheader | Kein Datei-Lizenzgrant / kein SPDX-License-Identifier | Leerer Python-Paketmarker; triviales/generiertes Gerüst, Herkunft nicht eigenständig belegt | Gerüst | Später Header-/Umfangspolitik prüfen; keine Urheber erfinden |
| `r3d_planner/r3d_planner/__pycache__/__init__.cpython-310.pyc` | Nicht aus Textheader bestimmbar | Kein belegter eigener Lizenzhinweis | Generiertes Bytecode-Artefakt; Sourcezuordnung nicht rechtlich geprüft | Generiert | Später Umfang/Notices aus Source prüfen; kein neuer Grant |
| `r3d_planner/r3d_planner/__pycache__/r3d_local_filter.cpython-310.pyc` | Nicht aus Textheader bestimmbar | Kein belegter eigener Lizenzhinweis | Generiertes Bytecode-Artefakt; Sourcezuordnung nicht rechtlich geprüft | Generiert | Später Umfang/Notices aus Source prüfen; kein neuer Grant |
| `r3d_planner/r3d_planner/__pycache__/r3d_path_follower.cpython-310.pyc` | Nicht aus Textheader bestimmbar | Kein belegter eigener Lizenzhinweis | Generiertes Bytecode-Artefakt; Sourcezuordnung nicht rechtlich geprüft | Generiert | Später Umfang/Notices aus Source prüfen; kein neuer Grant |
| `r3d_planner/r3d_planner/__pycache__/r3d_path_test.cpython-310.pyc` | Nicht aus Textheader bestimmbar | Kein belegter eigener Lizenzhinweis | Generiertes Bytecode-Artefakt; Sourcezuordnung nicht rechtlich geprüft | Generiert | Später Umfang/Notices aus Source prüfen; kein neuer Grant |
| `r3d_planner/r3d_planner/__pycache__/r3d_pcd_path.cpython-310.pyc` | Nicht aus Textheader bestimmbar | Kein belegter eigener Lizenzhinweis | Generiertes Bytecode-Artefakt; Sourcezuordnung nicht rechtlich geprüft | Generiert | Später Umfang/Notices aus Source prüfen; kein neuer Grant |
| `r3d_planner/r3d_planner/__pycache__/r3d_rviz_interface.cpython-310.pyc` | Nicht aus Textheader bestimmbar | Kein belegter eigener Lizenzhinweis | Generiertes Bytecode-Artefakt; Sourcezuordnung nicht rechtlich geprüft | Generiert | Später Umfang/Notices aus Source prüfen; kein neuer Grant |
| `r3d_planner/r3d_planner/configuration.py` | Copyright (c) Bastian Aumer | Kein Datei-Lizenzgrant / kein SPDX-License-Identifier | R3D-Eigenentwicklung laut Entwicklererklärung; vorhandener Namensheader | Eigenanteil laut Erklärung | Nach Freigabe eigene Attribution und passenden Dateilizenzbezug prüfen |
| `r3d_planner/r3d_planner/launching.py` | Copyright (c) Bastian Aumer | Kein Datei-Lizenzgrant / kein SPDX-License-Identifier | R3D-Eigenentwicklung laut Entwicklererklärung; vorhandener Namensheader | Eigenanteil laut Erklärung | Nach Freigabe eigene Attribution und passenden Dateilizenzbezug prüfen |
| `r3d_planner/r3d_planner/odometry.py` | Copyright (c) Bastian Aumer | Kein Datei-Lizenzgrant / kein SPDX-License-Identifier | R3D-Eigenentwicklung laut Entwicklererklärung; vorhandener Namensheader | Eigenanteil laut Erklärung | Nach Freigabe eigene Attribution und passenden Dateilizenzbezug prüfen |
| `r3d_planner/r3d_planner/r3d_local_filter.py` | Copyright (c) Bastian Aumer | Kein Datei-Lizenzgrant / kein SPDX-License-Identifier | R3D-Eigenentwicklung laut Entwicklererklärung; vorhandener Namensheader | Eigenanteil laut Erklärung | Nach Freigabe eigene Attribution und passenden Dateilizenzbezug prüfen |
| `r3d_planner/r3d_planner/r3d_path_follower.py` | Copyright (c) Bastian Aumer | Kein Datei-Lizenzgrant / kein SPDX-License-Identifier | R3D-Eigenentwicklung laut Entwicklererklärung; vorhandener Namensheader | Eigenanteil laut Erklärung | Nach Freigabe eigene Attribution und passenden Dateilizenzbezug prüfen |
| `r3d_planner/r3d_planner/r3d_path_test.py` | Copyright (c) Bastian Aumer | Kein Datei-Lizenzgrant / kein SPDX-License-Identifier | R3D-Eigenentwicklung laut Entwicklererklärung; vorhandener Namensheader | Eigenanteil laut Erklärung | Nach Freigabe eigene Attribution und passenden Dateilizenzbezug prüfen |
| `r3d_planner/r3d_planner/r3d_pcd_path.py` | Copyright (c) Bastian Aumer | Kein Datei-Lizenzgrant / kein SPDX-License-Identifier | R3D-Eigenentwicklung laut Entwicklererklärung; vorhandener Namensheader | Eigenanteil laut Erklärung | Nach Freigabe eigene Attribution und passenden Dateilizenzbezug prüfen |
| `r3d_planner/r3d_planner/r3d_rviz_interface.py` | Copyright (c) Bastian Aumer | Kein Datei-Lizenzgrant / kein SPDX-License-Identifier | R3D-Eigenentwicklung laut Entwicklererklärung; vorhandener Namensheader | Eigenanteil laut Erklärung | Nach Freigabe eigene Attribution und passenden Dateilizenzbezug prüfen |
| `r3d_planner/resource/r3d_planner` | Kein eigener Copyright-Dateiheader | Keine eigene Lizenzdeklaration | Projekt-/Konfigurations-/Gerüstbestand; individuelle Herkunft nicht rechtlich geprüft | Projektbestand | Später Distributionsumfang, Rechte und geeignete Lizenzzuordnung prüfen |
| `r3d_planner/setup.cfg` | Kein eigener Copyright-Dateiheader | Keine eigene Lizenzdeklaration | Projekt-/Konfigurations-/Gerüstbestand; individuelle Herkunft nicht rechtlich geprüft | Projektbestand | Später Distributionsumfang, Rechte und geeignete Lizenzzuordnung prüfen |
| `r3d_planner/setup.py` | Copyright (c) Bastian Aumer | Apache-2.0 nur als Setup-Metadatum; kein Datei-Lizenzgrant | R3D-Eigenentwicklung laut Entwicklererklärung; vorhandener Namensheader | Eigenanteil laut Erklärung | Nach Freigabe eigene Attribution und passenden Dateilizenzbezug prüfen |
| `r3d_planner/test/test_configuration.py` | Copyright (c) Bastian Aumer | Kein Datei-Lizenzgrant / kein SPDX-License-Identifier | R3D-Eigenentwicklung laut Entwicklererklärung; vorhandener Namensheader | Eigenanteil laut Erklärung | Nach Freigabe eigene Attribution und passenden Dateilizenzbezug prüfen |
| `r3d_planner/test/test_copyright.py` | Copyright 2015 Open Source Robotics Foundation, Inc. | Apache-2.0, ausgeschriebener Header | OSRF-/ROS-Generatorvorlage, Byteabgleich verifiziert | Fremdtemplate | Fremdhinweise vollständig erhalten; nicht durch Bastian Aumer ersetzen |
| `r3d_planner/test/test_flake8.py` | Copyright 2017 Open Source Robotics Foundation, Inc. | Apache-2.0, ausgeschriebener Header | OSRF-/ROS-Generatorvorlage, Byteabgleich verifiziert | Fremdtemplate | Fremdhinweise vollständig erhalten; nicht durch Bastian Aumer ersetzen |
| `r3d_planner/test/test_pep257.py` | Copyright 2015 Open Source Robotics Foundation, Inc. | Apache-2.0, ausgeschriebener Header | OSRF-/ROS-Generatorvorlage, Byteabgleich verifiziert | Fremdtemplate | Fremdhinweise vollständig erhalten; nicht durch Bastian Aumer ersetzen |
| `r3d_preprocessor/Filters.txt` | Kein eigener Copyright-Dateiheader | Keine eigene Lizenzdeklaration | Projekt-/Konfigurations-/Gerüstbestand; individuelle Herkunft nicht rechtlich geprüft | Projektbestand | Später Distributionsumfang, Rechte und geeignete Lizenzzuordnung prüfen |
| `r3d_preprocessor/README.txt` | Kein eigener Copyright-Dateiheader | Keine eigene Lizenzdeklaration | Projekt-/Konfigurations-/Gerüstbestand; individuelle Herkunft nicht rechtlich geprüft | Projektbestand | Später Distributionsumfang, Rechte und geeignete Lizenzzuordnung prüfen |
| `r3d_preprocessor/maps/voxel_05_minhits_7.pcd` | Nicht aus Textheader bestimmbar | Kein belegter eigener Lizenzhinweis | Kartendaten; Herkunft/Rechte offen | Daten | Datenherkunft und separate Freigabe klären |
| `r3d_preprocessor/maps/voxel_05_minhits_7_analysed.pcd` | Nicht aus Textheader bestimmbar | Kein belegter eigener Lizenzhinweis | Kartendaten; Herkunft/Rechte offen | Daten | Datenherkunft und separate Freigabe klären |
| `r3d_preprocessor/package.xml` | Kein eigener Copyright-Dateiheader | Manifest: TODO: License declaration | ROS-Paketmetadaten | Projektmetadaten | Nach Freigabe tatsächliche Lizenz/-en deklarieren |
| `r3d_preprocessor/r3d_preprocessor/__init__.py` | Kein eigener Copyright-Dateiheader | Kein Datei-Lizenzgrant / kein SPDX-License-Identifier | Leerer Python-Paketmarker; triviales/generiertes Gerüst, Herkunft nicht eigenständig belegt | Gerüst | Später Header-/Umfangspolitik prüfen; keine Urheber erfinden |
| `r3d_preprocessor/r3d_preprocessor/__pycache__/__init__.cpython-310.pyc` | Nicht aus Textheader bestimmbar | Kein belegter eigener Lizenzhinweis | Generiertes Bytecode-Artefakt; Sourcezuordnung nicht rechtlich geprüft | Generiert | Später Umfang/Notices aus Source prüfen; kein neuer Grant |
| `r3d_preprocessor/r3d_preprocessor/__pycache__/r3d_pcd_analyser.cpython-310.pyc` | Nicht aus Textheader bestimmbar | Kein belegter eigener Lizenzhinweis | Generiertes Bytecode-Artefakt; Sourcezuordnung nicht rechtlich geprüft | Generiert | Später Umfang/Notices aus Source prüfen; kein neuer Grant |
| `r3d_preprocessor/r3d_preprocessor/__pycache__/r3d_pcd_publisher.cpython-310.pyc` | Nicht aus Textheader bestimmbar | Kein belegter eigener Lizenzhinweis | Generiertes Bytecode-Artefakt; Sourcezuordnung nicht rechtlich geprüft | Generiert | Später Umfang/Notices aus Source prüfen; kein neuer Grant |
| `r3d_preprocessor/r3d_preprocessor/r3d_pcd_analyser.py` | Copyright (c) Bastian Aumer | Kein Datei-Lizenzgrant / kein SPDX-License-Identifier | R3D-Eigenentwicklung laut Entwicklererklärung; vorhandener Namensheader | Eigenanteil laut Erklärung | Nach Freigabe eigene Attribution und passenden Dateilizenzbezug prüfen |
| `r3d_preprocessor/r3d_preprocessor/r3d_pcd_publisher.py` | Copyright (c) Bastian Aumer | Kein Datei-Lizenzgrant / kein SPDX-License-Identifier | R3D-Eigenentwicklung laut Entwicklererklärung; vorhandener Namensheader | Eigenanteil laut Erklärung | Nach Freigabe eigene Attribution und passenden Dateilizenzbezug prüfen |
| `r3d_preprocessor/r3d_preprocessor/r3d_pcd_voxel_publisher.py` | Copyright (c) Bastian Aumer | Kein Datei-Lizenzgrant / kein SPDX-License-Identifier | R3D-Eigenentwicklung laut Entwicklererklärung; vorhandener Namensheader | Eigenanteil laut Erklärung | Nach Freigabe eigene Attribution und passenden Dateilizenzbezug prüfen |
| `r3d_preprocessor/resource/r3d_preprocessor` | Kein eigener Copyright-Dateiheader | Keine eigene Lizenzdeklaration | Projekt-/Konfigurations-/Gerüstbestand; individuelle Herkunft nicht rechtlich geprüft | Projektbestand | Später Distributionsumfang, Rechte und geeignete Lizenzzuordnung prüfen |
| `r3d_preprocessor/setup.cfg` | Kein eigener Copyright-Dateiheader | Keine eigene Lizenzdeklaration | Projekt-/Konfigurations-/Gerüstbestand; individuelle Herkunft nicht rechtlich geprüft | Projektbestand | Später Distributionsumfang, Rechte und geeignete Lizenzzuordnung prüfen |
| `r3d_preprocessor/setup.py` | Copyright (c) Bastian Aumer | Apache-2.0 nur als Setup-Metadatum; kein Datei-Lizenzgrant | R3D-Eigenentwicklung laut Entwicklererklärung; vorhandener Namensheader | Eigenanteil laut Erklärung | Nach Freigabe eigene Attribution und passenden Dateilizenzbezug prüfen |
| `r3d_preprocessor/test/test_copyright.py` | Copyright 2015 Open Source Robotics Foundation, Inc. | Apache-2.0, ausgeschriebener Header | OSRF-/ROS-Generatorvorlage, Byteabgleich verifiziert | Fremdtemplate | Fremdhinweise vollständig erhalten; nicht durch Bastian Aumer ersetzen |
| `r3d_preprocessor/test/test_flake8.py` | Copyright 2017 Open Source Robotics Foundation, Inc. | Apache-2.0, ausgeschriebener Header | OSRF-/ROS-Generatorvorlage, Byteabgleich verifiziert | Fremdtemplate | Fremdhinweise vollständig erhalten; nicht durch Bastian Aumer ersetzen |
| `r3d_preprocessor/test/test_pep257.py` | Copyright 2015 Open Source Robotics Foundation, Inc. | Apache-2.0, ausgeschriebener Header | OSRF-/ROS-Generatorvorlage, Byteabgleich verifiziert | Fremdtemplate | Fremdhinweise vollständig erhalten; nicht durch Bastian Aumer ersetzen |

Die zwei Paketmarker `__init__.py` und die ament-Ressourcen sind leer; das bloße Gerüst begründet hier keine erfundene individuelle Urheberzuordnung. Die neun Bytecode-Dateien sind als generierte Artefakte erkennbar, aber nicht unabhängig auf vollständige Source-/Notice-Provenienz geprüft. Keine Datei wird entfernt oder automatisch neu lizenziert.

Zusätzlich gelesen, unverändert und nicht neu in Git aufgenommen: `docs/R3D_Planner_Development_History.pdf` (unversioniert, SHA in 2.1) und das siebenseitige Recherche-PDF außerhalb des Repositorys (SHA in 11.1). Deren Dokumentations-/Nutzungsrechte werden nicht automatisch aus der beabsichtigten Codelizenz abgeleitet.

#### 11.12.1 PCD-Karten und andere Daten


| Datei | Technischer Inhalt / Größe | SHA-256 | Rechtebefund |
| --- | --- | --- | --- |
| `r3d_preprocessor/maps/voxel_05_minhits_7.pcd` | PCD 0.7, 602619 Punkte, XYZ/intensity/normals/curvature; 19284059 Byte | `1b36ce3ac8b0a57e9bea5cfeb5563db3478c3e1105d68d38a37a395322bab404` | Header enthält Formatdaten, keine nachgewiesene Herkunfts-/Lizenzfreigabe |
| `r3d_preprocessor/maps/voxel_05_minhits_7_analysed.pcd` | PCD 0.7, 556586 Punkte, XYZ/RGB; 8905560 Byte | `fff00cb9eb9fdaf96cb3c8bbf9c6ed2bd323a7b11e734dfea05ad52d9aadb22c` | Analysierte Struktur plausibel, Erzeugungs-/Verteilungsrechte am konkreten Artefakt weiterhin offen |

Die Analysefunktion schreibt klassifizierte PCDs; daraus folgt weder ein automatischer Rechteerwerb an einer fremden Eingabekarte noch eine automatisch gewählte Datenlizenz. Relevant können Werk-, Datenbankhersteller- und vertragliche Aufnahme-/Nutzungsrechte sein. Ihre Voraussetzungen sind für diese beiden Dateien nicht festgestellt [Q17/Q18]. Räumliche Aufnahmen können zusätzlich Freigaben oder personenbezogene/sonstige sensible Informationen betreffen; ob solche Umstände hier vorliegen, ist nicht bestimmbar und wurde nicht behauptet.

Auch Dokumentation, Konfiguration und generierte Binärdateien sind im künftigen Distributionsumfang bewusst abzugrenzen. Bis V4-004 blieben beide PCDs unverändert im lokalen Repository. V4-005 übernimmt ihre bereits vor Auftragseingang vorhandenen Working-Tree-Löschungen in den aktiven Tree; historische Gitobjekte bleiben. Keine Neulizenzierung oder zusätzliche Übertragung. Die getroffene Softwarelizenzentscheidung und eine noch offene Datenlizenzentscheidung bleiben ausdrücklich getrennt.

### 11.13 LiDAR-SLAM-Herkunft

#### 11.13.1 Git-Nachweise und untersuchte Revisionen

Die beiden ausdrücklich benannten öffentlichen Repositories wurden lesend über GitHub sowie in temporären Bare-Objektkopien ohne Checkout/Build untersucht. An den externen Originalrepositorys wurde nichts geändert. Die damalige R3D-Änderung V4-002/V4-003 betraf ausschließlich dieses Protokoll. Die anschließende V4-004-Lizenzimplementierung ergänzt eigene Kommentarheader/Lizenzdateien, ohne externe LiDAR-Dateien, Branchzuordnungen oder Remotes zu ändern. Der R3D-Quellbaum enthält keinen lidar_odom-/lidar_slam_ros2-Implementationstree und kein entsprechendes Submodul. Die externe LiDAR-Software wird deshalb nicht als Bestandteil der beiden R3D-Pakete dargestellt.

| Referenz | Verifizierter Stand / Aussage |
| --- | --- |
| Originalprojekt | `rsasaki0109/lidar_slam_ros2`, öffentlicher Defaultbranch develop |
| Für Vergleich gelesener Originaltip | `a3b83d7ec504332d2ad54bcbf2c3a55d2a3fc8ec` am 13.10.2026; kein behaupteter Deploymentstand |
| Abgeleitetes Repository | `RoboProjekt/lidar_odom`, öffentlicher Defaultbranch lidar-odometry |
| Untersuchter modifizierter Tip | `69c0e093cb19d2367476466716aa547d7c753327` |
| Nachgewiesene Ausgangsrevision | `2f8753853854a528654243c92073a277f4f27226`, gemeinsamer Git-Vorfahr und direkter Parent des ersten eigenen LiDAR-Frontend-Commits |
| Zusätzlicher Branch im abgeleiteten Repository | develop bei `e5d2410683362b928d134161b267460362c84c0c`; Commit auch in Originalhistorie nachgewiesen, Nachfolger der Ausgangsrevision; nicht mit der eigenen lidar-odometry-Linie verwechseln |
| Eigenständige Commits nach Ausgangsrevision | Genau drei auf der untersuchten lidar-odometry-Linie, alle Git-Autor Basti; Zuordnung zu Bastian Aumer durch Entwicklererklärung dokumentiert |
| Tatsächlich auf Roboter/Deployment eingesetzte SHA | **NOT VERIFIED**; aus dem aktuellen Server-Defaultbranch nicht ableitbar |
| Originale Hauptlizenz | BSD 2-Clause License / **BSD-2-Clause**, an Ausgangsrevision und modifiziertem Tip gelesen |
| Originaler Copyright-Wortlaut | `Copyright (c) 2020, Ryohei Sasaki` und `All rights reserved.` |
| Lizenzgleichheit | LICENSE-Blob `4b3333d47ee8c7d1c1cf788fbde465a921d220b2` an beiden Revisionen identisch |
| Vollständige ursprüngliche Entwickler-/Rechteinhaberliste | **NOT VERIFIED**; Ryohei Sasaki ist durch Lizenz/History benannt, weitere Git-Autoridentitäten sind keine abschließende rechtliche Attribution |

Quellen und pinned Links: L01-L07 in 11.22. Der R3D-Historienbericht bleibt die unveränderte Referenz der eigenen Pakete. Die jetzt betrachteten LiDAR-Commits datieren vom 16. September 2026 und liegen vor dem R3D-Baseline-Commit; ihre Implementierung ist keine neue V4-Leistung. Neu in V4 ist diese Provenienz-/Lizenzdokumentation.

#### 11.13.2 Art der Integration

| Integrationsart | Tatsächlicher Befund / Status |
| --- | --- |
| A: externe ROS-Node-Kommunikation | Verifiziert im Sourcevertrag: lidar_odom publiziert standardmäßig `/lidar_odometry` als nav_msgs/Odometry mit odom/base_link sowie odom→base_link-TF; R3D-Konfiguration/Poseadapter erwartet diesen Standardvertrag |
| B: direkt übernommener Code in R3D | Kein LiDAR-Implementationstree oder entsprechender direkter Import in R3D identifiziert; keine Übernahme in dieser Aufgabe |
| C: modifizierter Fremdcode | Im separaten lidar_odom-Repository Git-Ableitung und Änderungen verifiziert; Original-/Subkomponentenbedingungen bleiben relevant |
| D: separat ausgeliefertes Repository | Separates öffentliches Repository verifiziert; tatsächlicher lokaler/Roboter-Buildstand nicht verifiziert |
| E: gemeinsam ausgeliefertes Paket/Container | **NOT VERIFIED**; keine Gesamt-Binärdistribution untersucht oder erzeugt |

R3D bleibt technisch estimatorunabhängig: README und Odometry-Konfiguration verlangen einen Nachrichten-/Framevertrag, keinen direkten Link auf eine bestimmte LiDAR-Implementierung. Externe map→odom-Lokalisierung ist vom lokalen odom→base_link-Frontend zu unterscheiden. Diese Sourcekompatibilität ist noch kein ausgeführter Integrationstest und keine pauschale rechtliche Aussage über jede denkbare Softwarekombination.

#### 11.13.3 Konkret mitgelieferte und verlinkte Fremdkomponenten

Der Gitlink `Thirdparty/ndt_omp_ros2` zeigt vor und nach der Anpassung unverändert auf **497411279593eb261a3e3d04cdcbb4717af33ca3**. Die .gitmodules verweist auf `https://github.com/rsasaki0109/ndt_omp_ros2`, Branch humble; maßgeblich ist dennoch die gepinnte SHA. Die NDT-/GICP-Implementierung wurde an diesem Gitlink nicht geändert. Der aktuelle CMake-Target kompiliert drei Translation Units dieses Submoduls statisch in `lidar_odom_ndt_omp`.

| Komponente | Konkreter Lizenz-/Herkunftsnachweis | Nutzung / mögliche Zusatzpflicht |
| --- | --- | --- |
| lidar_slam_ros2 / lidar_odom-Hauptbestand | BSD-2-Clause; Ryohei-Sasaki-Hinweis identisch erhalten | Originalbedingungen/-Disclaimer und separate Attribution eigener Änderungen |
| ndt_omp_ros2, SHA 4974112… | Root-LICENSE: BSD-2-Clause, `Copyright (c) 2019, k.koide`; Manifest nur BSD | Gepinnte Sourcekomponente, statisch kompiliert; Roottext allein beschreibt nicht alle PCL-Dateien |
| PCL-basierte NDT-/GICP-Header im Submodul | ndt_omp.h, ndt_omp_impl.hpp, gicp_omp.h, gicp_omp_impl.hpp, voxel_grid_covariance_omp.h: drei BSD-Klauseln; Willow Garage/Open Perception, dateispezifische Jahresangaben | **BSD-3-Clause** dieser Dateien zusätzlich erhalten; Kompilation nutzt solche Header/Templates, kein pauschales „nur BSD-2“ |
| PCL | CMake-/Include-Nutzung; offizieller PCL-1.12.1-Lizenztext BSD-3-Clause als Referenz | Tatsächlich verwendete Deploymentversion/alle optionalen PCL-Teile **NOT VERIFIED**; Binärumfang prüfen |
| Eigen3 | CMake und Eigen/Geometry-Header; Eigen-3.4.0-Referenztext MPL-2.0 | Deploymentversion/-Datei-/Distributionsumfang **NOT VERIFIED**; MPL-Bedingungen für betroffene Teile, kein automatischer Lizenzwechsel des gesamten R3D |
| Boost | boost/shared_ptr.hpp in Node; offizieller Boost Software License 1.0-Text | **BSL-1.0** als Referenz; tatsächliche Version und gesamter Linkumfang **NOT VERIFIED** |
| rclcpp, geometry_msgs, nav_msgs, sensor_msgs, pcl_conversions, TF2/tf2_eigen, ament_cmake/gtest | Manifest-/CMake-/Include-Nutzung verifiziert; rclcpp Apache-Text und TF2-/Messagequellen kontrolliert | Separate System-/ROS-Komponenten; vollständiger konkreter Build-/Binärlizenzaudit **NOT VERIFIED** |
| OpenMP | CMake OpenMP::OpenMP_CXX und omp.h | API ist keine einheitliche Librarylizenz; konkrete libgomp-/libomp-Implementierung und Version **NOT VERIFIED** |
| Entfernte Legacy-Komponenten | Im End-Tree kein graph_based_slam, scanmatcher, lidarslam, lidarslam_msgs, Thirdparty/rko_lio oder Thirdparty/3d_bbs mehr | Entfernung aus aktivem Tree verifiziert; historische Git-Objekte können weiterhin enthalten sein; keine pauschale Lizenzbewertung eines vollständigen History-Bundles |

Quellen L08-L17. Anders als die bloße externe Librarynutzung in R3D betrifft NDT hier tatsächlich separat gepinnte und statisch in den LiDAR-Node eingebaute Fremdsource. Der unveränderte Root-Lizenztext allein belegt nicht, dass eine künftige Binärdistribution alle Fremdtexte korrekt mitliefert. CMake installiert Node, Includes, Config und Launch; eine vollständige License-/Notice-Mitnahme wird dadurch nicht nachgewiesen. Es wurde weder kompiliert noch ein Lizenztext installiert.

### 11.14 LiDAR-SLAM-Modifikationen

Die Übersicht basiert auf tatsächlichen Parent-/Commit-Diffs, nicht nur auf README-Aussagen. Exakte Sourceidentität ist für LICENSE und den NDT-Gitlink belegt. Eine vollständige zeilenweise Urheberschaftszuordnung jedes neu hinzugefügten C++-Fragments ist nicht unabhängig verifiziert.

| Commit / Datum (+02:00) | Verifizierte Änderung | Technische Bedeutung / Grenze |
| --- | --- | --- |
| `abfc13d14eab4c7cc04d489083697711d4585f8a`, 16.09.2026 15:31:58 | Zehn Dateien des neuen lidar_odom-Pakets hinzugefügt, README/.gitignore geändert; 12 Dateien, +1067/-161 | Neuer lokaler LiDAR-only-Frontendpfad mit Standard-Odometry/TF, Helfern, YAML/Launch, Tests und CMake; Git-Autor Basti, persönliche Zuordnung dokumentiert |
| `d2c9ed69662b4a892c576bdf8fcea1dcd7d90ed4`, 16.09.2026 15:34:40 | Vier COLCON_IGNORE-Dateien in graph_based_slam/lidarslam/lidarslam_msgs/scanmatcher hinzugefügt | Vorübergehende Trennung alter SLAM-Pakete vom normalen Build |
| `69c0e093cb19d2367476466716aa547d7c753327`, 16.09.2026 16:25:03 | 277 Dateien gelöscht, zehn geändert; +117/-57803. Legacy-SLAM/Tools/Dokumente/Komponenten entfernt; CMake verwendet NDT-Submodulsource statt ndt_omp_ros2::ndt_omp-Exporttarget; Manifestdepend ndt_omp_ros2 entfernt; Timestamp-Helfer und Regression ergänzt | End-Tree auf lokale Odometrie reduziert; keine Änderung des gepinnten NDT-Gitlinks; Dependency-/Buildstrategie tatsächlich geändert, kein neuer Buildtest in diesem Audit |

Nettovergleich Ausgangsrevision→69c0e0: **286 geänderte Pfade** (273 gelöscht, drei geändert, zehn hinzugefügt), **+1106/-57882**; Treeumfang **279→16 Einträge**, einschließlich Gitlinks. Diese Zahlen zählen Git-Pfade, nicht ausgeführte Funktionen oder neue eigene Urheberwerke.

| Betroffene Datei/-gruppe | Im Source/Diff belegte Anpassung |
| --- | --- |
| `lidar_odom/src/lidar_odometry_node.cpp` | PointCloud2-Vorverarbeitung, NDT/GICP-Registrierung, lokale SE(3)-Akkumulation, optionale begrenzte Submap; nav_msgs/Odometry und optionale Path/Clouds/TF-Ausgabe; kein map→odom-Publisher |
| `include/lidar_odom/odometry_math.hpp` | accumulatePose, lidarPoseToBasePose, Body-Twist-Schätzung und später timestampStrictlyIncreases; extrinsische LiDAR/Base-Transformation explizit |
| `include/lidar_odom/odometry_state.hpp` | Zustand übernimmt nur akzeptierte endliche relative Transformationen; Fehlregistrierung soll den akzeptierten Zustand erhalten |
| `include/lidar_odom/local_submap.hpp` | Zeitlich begrenzte Scan-Deque, Maximalzahl, Bewegungs-/Rotationsschwellen; keine globale Karte |
| `config/lidar_odometry.yaml` und `launch/lidar_odometry.launch.py` | Sensortopic, Odometrie, Frames, Preprocessing-/Registration-/Validierungs-/Submap-/Publikationsparameter und installierter Node-Einstieg |
| `CMakeLists.txt` / `package.xml` | ament_cmake/C++17, PCL/Eigen/OpenMP/ROS-Targets, drei statisch kompilierte Submodul-CPPs; BSD-2-Clause-Manifestdeklaration vorhanden |
| `test_local_submap.cpp` / `test_odometry_math.cpp` | Sieben GTest-TEST-Blöcke im aktuellen Source: Submap/Schwellen, SE(3), Extrinsik, Twist, Timestamp und abgelehnte Registrierung; nicht ausgeführt |
| `LICENSE` / `Thirdparty/ndt_omp_ros2` | Root-Lizenzblob und Gitlink unverändert; keine zusätzliche persönliche Namensattribution durch diese Aufgabe |

Der aktuelle Node und drei Helferheader beginnen mit `// Copyright 2026` ohne benannte Person und `// SPDX-License-Identifier: BSD-2-Clause`. Dies belegt vorhandene BSD-Deklaration, aber noch keine vollständig ausdrückliche persönliche Änderungsattribution. Das Manifest nennt weiterhin eine rsasaki0109-E-Mail für „lidar_odom maintainers“; daraus wird keine persönliche Urheberschaft des aktuellen Frontends abgeleitet. Späterer Änderungsbedarf ist zu dokumentieren, hier jedoch nicht umzusetzen.

Reproduzierbare reine Git-Auswertung der öffentlichen Historie, in temporären Kopien ausgeführt:

```bash
# Temporaere Bare-Kopien, kein Original-Checkout, keine Submodule/Builds:
analysis_cache=/tmp/r3d-v4-license
git clone --bare --filter=blob:none --single-branch --branch lidar-odometry   --no-tags https://github.com/RoboProjekt/lidar_odom.git "$analysis_cache/lidar_odom.git"
git clone --bare --filter=blob:none --single-branch --branch develop   --no-tags https://github.com/rsasaki0109/lidar_slam_ros2.git "$analysis_cache/lidar_slam_ros2.git"
# Gemeinsame Objektansicht nur fuer diesen Analysebefehl:
GIT_ALTERNATE_OBJECT_DIRECTORIES="$analysis_cache/lidar_slam_ros2.git/objects"   git --git-dir="$analysis_cache/lidar_odom.git" merge-base   69c0e093cb19d2367476466716aa547d7c753327   a3b83d7ec504332d2ad54bcbf2c3a55d2a3fc8ec
git --git-dir="$analysis_cache/lidar_odom.git" log --reverse   2f8753853854a528654243c92073a277f4f27226..69c0e093cb19d2367476466716aa547d7c753327
git --git-dir="$analysis_cache/lidar_odom.git" diff --name-status   2f8753853854a528654243c92073a277f4f27226 69c0e093cb19d2367476466716aa547d7c753327
git --git-dir="$analysis_cache/lidar_odom.git" show "<SHA>" -- "<Dateipfad>"
```

`analysis_cache` bezeichnet im tatsächlichen Durchlauf `/tmp/r3d-v4-license`; `<SHA>` und `<Dateipfad>` sind vor Nutzung durch eine konkrete Revision und einen zugehörigen Pfad zu ersetzen. Die Clone-Befehle beschreiben die erstmalige Anlage; vorhandene Analyse-Caches wurden danach nur gelesen. Blobnachladung erfolgte ausschließlich in diesen temporären Caches. Keine externen Commits wurden erzeugt und keine Tests gestartet.

### 11.15 Modification Notice: Dokumentationsabschluss

Die folgende Notice ist unter V4-004 **als Dokumentation innerhalb dieses Protokolls abgeschlossen**. Sie ist keine angewendete Datei im externen Repository und keine erzeugte Release-Datei. Original-/Modified-Revision bezeichnen die analysierte Git-Ableitung, nicht einen bestätigten Roboterstand. Die persönliche Änderungszuordnung folgt der Entwicklererklärung zusammen mit den Git-Autorinformationen. Vollständige Drittrechte-/Binärmitnahme bleibt offen.

```text
THIRD-PARTY SOFTWARE MODIFICATION NOTICE

Component:
lidar_odom (LiDAR-only local odometry frontend)

Original Project:
lidar_slam_ros2

Original Repository:
https://github.com/rsasaki0109/lidar_slam_ros2

Original Revision:
2f8753853854a528654243c92073a277f4f27226

Original License:
BSD-2-Clause (project root; third-party file conditions separately apply)

Original Copyright:
Copyright (c) 2020, Ryohei Sasaki
All rights reserved.

Original Developers:
Ryohei Sasaki (named in LICENSE and history)
Complete original developer/rightsholder inventory: NOT VERIFIED

Modified by:
Bastian Aumer (developer declaration; Git author identity Basti)

Modified for:
R3D-Planner (developer declaration; ROS interface connection verified in source)

Modified Revision:
69c0e093cb19d2367476466716aa547d7c753327

Deployment Revision:
NOT VERIFIED

Technical Description of Changes:
---------------------------------
1. abfc13d...: Add lidar_odom package, local scan-to-scan SE(3) odometry,
   optional bounded submap, standard Odometry/TF, YAML/launch and tests.
2. d2c9ed6...: Temporarily exclude four legacy SLAM packages with COLCON_IGNORE.
3. 69c0e09...: Remove obsolete SLAM runtime/tooling, compile unchanged pinned
   NDT-OMP translation units locally, add timestamp helper/regression.

License and Copyright:
----------------------
The original source remains subject to its original license and copyright.
All applicable original conditions, copyright notices and disclaimers
must be retained in any future distribution.
Modifications attributed to Bastian Aumer are separately identified here.
This documentation notice does not replace LICENSE, file headers or third-party notices.
Original root LICENSE and pinned NDT revision are unchanged in the inspected Git history.
No external repository or binary-distribution artifact was modified by V4-004.
Full binary-distribution compliance: NOT VERIFIED.

Additional Third-Party Component:
ndt_omp_ros2, revision 497411279593eb261a3e3d04cdcbb4717af33ca3
Root license: BSD-2-Clause
Copyright (c) 2019, k.koide
PCL-derived headers: BSD-3-Clause; retain their file-specific notices.
```

Dokumentationsabschluss und externe Anwendung sind getrennt. Die Formulierung „must be retained“ ist bewusst eine Anforderung an die spätere Distribution; eine ungeprüfte Behauptung, bereits jedes Binärpaket enthalte alle Texte, wäre unzutreffend. Originaltexte/Disclaimer werden durch diese Notice nicht ersetzt. Bei späterer Umsetzung sind betroffene eigene Bearbeitungen, unveränderte fremde Source und vollständige Pflichttexte getrennt zu behandeln. Fehlende Felder bleiben NOT VERIFIED, statt Urheber, Laufzeitstand oder Rechtevereinbarungen zu erfinden.

### 11.16 Patentregelungen

**Lizenztext:** Apache-2.0 Abschnitt 3 betrifft die vom jeweiligen Contributor lizenzierbaren Ansprüche, die sein Beitrag allein oder zusammen mit dem damaligen Werk notwendigerweise verletzt. Für den dort beschriebenen Patentprozess gegen Werk/Contribution endet der entsprechende Patentgrant. Er ist keine Versicherung gegen Patente außenstehender Dritter [Q01]. Die ASF-FAQ erläutert die Begrenzung auf kontrollierte Ansprüche und den Beitragskontext [Q06].

**Bewertung:** Eine ausdrückliche Regel ist für den gewünschten professionellen Weiterverwendungskontext ein begründeter Vorteil. Ihre tatsächliche Wirkung hängt von Contributors und deren Befugnissen ab. Weder eine Patentlandschaft noch Arbeitgeberpatente wurden untersucht. Das Ergebnis begründet die nun getroffene Lizenzentscheidung, ist aber kein Patentfreigabenachweis. Fehlende ausdrückliche MIT-/BSD-Klauseln werden nicht mit einem nachgewiesenen Verzicht auf sämtliche denkbaren Patentrechte gleichgesetzt.

### 11.17 ROS-2-Release-Anforderungen

Die ROS-2-Dokumentation empfiehlt Apache-2.0 für neue Projekte, auch im Vergleich zur früheren BSD-Empfehlung. Für übernommenen Code fordert der Migrationsleitfaden den Erhalt bestehender Beiträge/Lizenzen und verweist bei einer Änderung auf erforderliche Contributor-Erlaubnisse. Dies stützt eine Präferenz, keine verbindliche Apache-Pflicht für jedes ROS-Paket [Q22].

Die rosdistro-Kriterien betreffen OSI-Lizenztext, zutreffende package.xml-Deklaration und öffentlich zugängliche Quellen für die Aufnahme. Eine private Entwicklungsphase ist damit vereinbar; sie ist noch kein öffentlich registrierbarer V4-Source-Stand [Q07]. REP-149 erlaubt mehrere License-Tags, wenn das Paket unterschiedliche lizenzierte Sourcebestandteile enthält. Externe Bibliotheksimporte werden nicht pauschal als weitere Lizenz des eigenen Sourcecodes in jedes Manifest kopiert [Q08].

SPDX-Angaben müssen mit dem autorisierten Lizenz- und Distributionsumfang übereinstimmen. V4-004 gleicht die beiden XML-Lizenzfelder an die bereits vorhandenen Apache-Setupwerte an und ergänzt eigene SPDX-Kommentare; das ist ausschließlich AP01, keine allgemeine AP02-Metadatenkorrektur. Unabhängige rosdep-/Build-/Installationsprobleme bleiben bestehen; AP03 beginnt nicht.


ROS Index und Bloom-/Buildfarm-Eignung hängen auch bei einer passenden Lizenz von den bereits dokumentierten technischen Voraussetzungen ab. Die externe LiDAR-Komponente wird nicht allein durch ihren BSD-Text als releasefähig erklärt. Die reine Analyse V4-002/V4-003 erzeugte keine LICENSE. V4-004 erzeugt nun ausdrücklich die Root-LICENSE für eigene Software; Release-Dateien, externe Lizenzänderungen oder Releaseausführung entstehen weiterhin nicht.

### 11.18 Entscheidungsmatrix

**Methodik:** qualitatives zweistufiges Verfahren ohne erfundene Punktwerte oder scheinpräzise Gewichte. Zuerst gelten Ausschlusskriterien: Verteilungsbefugnis für Code/Daten und konkreter Dependency-/Artefaktumfang müssen geklärt sein. Alle Kandidaten sind derzeit insoweit offen. Danach werden belegte Eigenschaften und Projektpräferenzen verglichen. Innerhalb der Präferenzen erhalten ausdrückliche Patentregelung und Anschluss an die ROS-Empfehlung Vorrang vor minimaler Textlänge. Das ist eine begründete Projektbewertung, keine objektive Rangfolge für alle Softwareprojekte.

O = Text-/Quelleneigenschaft; P = Projektpräferenz; U = ungeklärtes individuelles Verhältnis. „Offen“ wird nicht durch eine höhere Bewertung anderer Kriterien kompensiert.

| Kriterium / Typ | Apache-2.0 | MIT | BSD-2-Clause | BSD-3-Clause | Bewertungsregel |
| --- | --- | --- | --- | --- | --- |
| ROS-2-Eignung / O+P | Explizit empfohlen | Grundsätzlich möglicher OSI-Kandidat | Grundsätzlich möglicher OSI-Kandidat | Grundsätzlich möglicher OSI-Kandidat | Empfehlung bevorzugt, keine Alleinpflicht; Q07/Q22 |
| Kommerzielle Weiterverwendung / O | Erlaubt unter Bedingungen | Erlaubt unter Bedingungen | Erlaubt unter Bedingungen | Erlaubt unter Bedingungen | Kein ausschlaggebender Unterschied |
| Explizite Patentlizenz / O+P | Begrenzter Grant | Keine ausdrückliche Klausel | Keine ausdrückliche Klausel | Keine ausdrückliche Klausel | Begründeter Vorteil Apache, kein Patentgutachten |
| Umfang der Lizenzpflichten / O+P | Mehr einzelne Pflichten | Sehr geringer Textumfang | Geringer Textumfang | Zusätzlich Endorsement-Regel | Vorteil kurzer Texte nur nachrangige Präferenz |
| Weitergabe / Modifikation / O | Lizenz, Änderung, einschlägige Hinweise/NOTICE | Hinweis-/Textpflicht | Source-/Binär-Hinweispflichten | Wie BSD-2 plus Endorsement | Aufwand bei konkreter Distribution prüfen |
| Copyright-Attribution / O | Vorhandene Hinweise erhalten | Vorhandene Hinweise erhalten | Vorhandene Hinweise erhalten | Vorhandene Hinweise erhalten | Kein Kandidat erlaubt das Tilgen fremder Attribution |
| Integration fremder Beiträge / O+U | Contributor-Regel vorhanden, Befugnis offen | Beitragserlaubnis nachweisen | Beitragserlaubnis nachweisen | Beitragserlaubnis nachweisen | Apache-Regel ersetzt keine Rechtekettenprüfung |
| Verwendete Dependencies / U | Konkreter Gesamtumfang offen | Konkreter Gesamtumfang offen | Konkreter Gesamtumfang offen | Konkreter Gesamtumfang offen | Keine Freigabepunkte für ungeprüfte Kompatibilität |
| Zukünftiger Releaseaufwand / P+U | Mehr Notice-/Änderungsdisziplin; Anschluss an ROS-Praxis | Kurze eigene Lizenzpflege | Kurze eigene Lizenzpflege | Zusätzliche Werberegel beachten | Fremdnotices/Packaging können bei allen dominieren |
| Änderungskennzeichnung / O | Explizit für modifizierte Dateien | Kein eigener Änderungshinweisparagraph | Kein eigener Änderungshinweisparagraph | Kein eigener Änderungshinweisparagraph | Provenienzdisziplin bleibt Projektziel |
| ROS Index / O+U | Lizenzkandidat grundsätzlich geeignet | Lizenzkandidat grundsätzlich geeignet | Lizenzkandidat grundsätzlich geeignet | Lizenzkandidat grundsätzlich geeignet | Rechte, Texte und tatsächliche Aufnahme weiterhin offen |
| Bloom / Buildfarm / O+U | Keine automatische Freigabe | Keine automatische Freigabe | Keine automatische Freigabe | Keine automatische Freigabe | Dependencies/Artefakte/Installation separat prüfen |
| Industrielle Nutzung / P+U | Expliziter Patentrahmen vorteilhaft | Kurzer Text vorteilhaft | Kurzer Text vorteilhaft | Endorsement-Regel vorteilhaft bei diesem Bedarf | Kein Kandidat garantiert Patentfreiheit oder Systemtauglichkeit |
| Rechtliche Unsicherheit / U | Rechte/Karten/Verträge offen | Rechte/Karten/Verträge offen | Rechte/Karten/Verträge offen | Rechte/Karten/Verträge offen | Unverzichtbares Rechtsgate; Lizenzentscheidung ist kein Freigabenachweis |

**Sensitivität:** Würde das Projekt ausschließlich minimale Text-/Pflegepflichten bevorzugen und keine ausdrückliche Patentregelung verlangen, könnten MIT oder BSD-2-Clause vorrangig sein. BSD-3-Clause wäre bei gewünschter expliziter Non-Endorsement-Bedingung nachvollziehbar. Unter der hier gewählten Präferenzordnung ist Apache-2.0 der bevorzugte Kandidat. Die Matrix macht diese Abhängigkeit sichtbar, statt die Präferenz als Rechtszwang darzustellen.

### 11.19 Verbindliche Lizenzentscheidung und Begründung

**Verbindliche Projektentscheidung des Entwicklers im Folgeauftrag vom 13. Oktober 2026: Apache License 2.0 (SPDX Apache-2.0) für autorisierte eigene Softwarebestandteile von r3d_planner und r3d_preprocessor; Copyright-Attribution 2026 Bastian Aumer.** Die Entscheidung erlaubt LICENSE, eigene SPDX-Kommentare und Lizenzfeldanpassungen. Sie ist keine Feststellung einer vollständig unabhängig geprüften Lizenzierungsbefugnis oder Freigabe aller Repositoryartefakte.

Die Begründung folgt der vorhandenen qualitativen Matrix 11.18: Apache ist permissiv und erlaubt grundsätzlich kommerzielle Nutzung, Modifikation, Weitergabe und proprietäre Einbindung unter ihren Bedingungen. Die ausdrückliche, begrenzte Contributor-Patentlizenz und nachvollziehbaren Lizenz-/Änderungs-/Hinweispflichten passen zur offengelegten Projektpräferenz; die ROS-Empfehlung stützt die Wahl, erzwingt sie nicht [Q01/Q22]. Der höhere Hinweisaufwand gegenüber MIT/BSD wird bewusst akzeptiert. MIT und beide BSD-Varianten bleiben fachlich plausible Vergleichsalternativen; die Lizenzanalyse wird nicht erneut durchgeführt. Kein Kandidat garantiert Freiheit von fremden Patenten oder heilt fehlende Nutzungsrechte.

| Bestandteil | Verbindlicher/erhaltener Stand nach V4-004 | Grenze |
| --- | --- | --- |
| Zugeordnete eigene R3D-Python-Software | Apache-2.0, zusätzliche SPDX-Attribution 2026 Bastian Aumer | 18 konkrete Pfade; Entwicklererklärung dokumentiert, Verträge/Befugnisse nicht unabhängig geprüft |
| Root-LICENSE und ROS-Lizenzfelder | Vollständiger unveränderter ASF-Text, beide package.xml Apache-2.0, Setupwerte bereits passend | Geltung für autorisierte Eigenanteile; kein Override fremder Bedingungen oder der Kartenausnahme |
| Sechs ROS-Testtemplates | Ursprüngliche Apache-/OSRF-Hinweise vollständig erhalten | Keine eigene Copyright-Zuordnung oder Änderung der Vorlagen |
| Externe LiDAR-Odometrie | Separates BSD-2-Clause-Projekt; eigene Modifikationsattribution im Dokument | NDT-/PCL-/weitere Originalbedingungen bleiben; keine externe Datei geändert |
| Externe ROS-/Python-Libraries | Jeweilige Originallizenzen wie inventarisiert | Import vs tatsächliche Source-/Binärmitlieferung unterscheiden |
| Unklar zugeordnete Texte/Ressourcen, Marker und alte PYC | Keine neuen persönlichen Header oder ungeprüfte Dateilizenzzuordnung | Tatsächlichen künftigen Distributionsumfang/dateibezogene Rechte bewusst prüfen |
| Frühere PCD-Karten | Unter V4-005 aus aktuellem Tree entfernt, keine Apache-Freigabe historischer Objekte | Git-Historie/Forks/Kopien weiterhin eigenes Rechte-/Releaseumfangsthema |

In den vorhandenen Unterlagen ergab sich kein konkreter dokumentierter entgegenstehender Rechteanspruch an den 18 Eigenanteilen. Das ist kein Beweis der Abwesenheit solcher Rechte und keine Vertragsprüfung. Bei einem konkreten späteren Hinweis ist die betroffene Implementierung/Distribution zu stoppen und ein Blocker zu dokumentieren. Die übrigen offenen Fragen stehen in 11.20; allgemeine hypothetische Befugnisfragen werden nicht als bereits geklärt dargestellt.

### 11.20 Offene rechtliche Fragen

Der Fragenkatalog ist als konkrete Abnahmevorbereitung zu beantworten, möglichst mit nachvollziehbaren Projekt-/Vertragsunterlagen. Offene Punkte bleiben ausdrücklich sichtbar.

| Frage | Zu bestätigender Sachverhalt | Benötigter Nachweis / Entscheidung |
| --- | --- | --- |
| R01 | Alleinige Entwicklung der beiden eigenen Funktionskomponenten erklärt; Reichweite einschließlich Vorarbeiten von bekannten Fremdtemplates abgrenzen | Entwicklererklärung dokumentiert; dateibezogene Herkunft/etwaige Vertragsunterlagen weiterhin für endgültige Befugnis relevant |
| R02 | Laut Entwickler keine weiteren Entwickler der beiden eigenen Komponenten; Fremdtemplates und externe LiDAR-Contributors bestehen separat | Erklärung erhalten; fremde Attribution/Originalbedingungen nicht als eigene Entwicklung vereinnahmen |
| R03 | Entstand Code im Arbeits-/Dienstverhältnis, weisungsgebunden oder unter institutionellen/Projektverträgen? | Relevante Vereinbarungen und Berechtigung zur vermögensrechtlichen Freigabe, einschließlich § 69b-Kontext |
| R04 | Bestehen ausschließliche Nutzungsrechte, Geheimhaltungs-, Sponsor-, Hochschul- oder sonstige Vertragsbindungen? | Geltender Umfang und etwaige Zustimmung zur Open-Source-Verteilung; keine Vereinbarungen erfinden |
| R05 | Deckt die Berechtigung Source, Binärpakete, Modifikationen, Unterlizenzierung und erforderliche Patentgrants ab? | Dokumentierte Autorisierung für vorgesehenen Distributionsumfang |
| R06 | Welche Lizenz galt bereits für vor dem Root-Import übernommene Teile? | Originaltexte/Notices; Apache-Templates bestätigt, weitere Herkunft offen |
| R07 | Eigene historische Kartenaufnahme und Verarbeitung laut Entwickler bestätigt; V4 ohne aktive PCDs | Selbstauskunft dokumentiert, unabhängige Vertrags-/Nutzungs-/historische Verteilungsrechte weiterhin separat prüfen |
| R08 | Entwickler erklärt keine verletzten Datenschutzauflagen bei den eigenen Kartenaufnahmen | Erklärung dokumentiert, keine unabhängige Datenschutz-/Inhalts-/Vertragsprüfung; spätere Branchbereinigung eigene Aufgabe |
| R09 | Welche exakten Dependencies/Artefakte werden beim späteren Release tatsächlich mitgeliefert? | Versions-/Plattforminventar, mitzugebende Texte/Notices und gegebenenfalls besondere Binärbedingungen |
| R10 | Gibt es bekannte Patentansprüche oder Rechtebeschränkungen bei Beitragenden/Arbeitgebern? | Gezielte Auskunft; keine allgemeine Patentfreiheit behaupten |
| R11 | Wie werden künftige externe Beiträge und deren Berechtigungsbestätigung behandelt? | Passende Contribution-Regel; CLA/DCO nur bewusst wählen, keine Urheberrechtsübertragung voraussetzen |
| R12 | Persönliche Attribution nur eigener Beiträge, Fremdhinweise erhalten | Durch Nutzerauftrag für 18 eigene Dateien entschieden und umgesetzt; keine Gesamt-Rechteübertragung behauptet |
| R13 | Softwarelizenz gewählt; Dokumentations-/Ressourcen-/Datenrechte nicht pauschal gleichgesetzt | Apache-2.0 für autorisierte Eigenanteile verbindlich; Karten und weitere unklar zugeordnete Artefakte separat offen |
| R14 | Welche lidar_odom-/NDT-/Systemrevision ist tatsächlich im Zieldeployment eingesetzt? | Dokumentierter Build-/Deploymentstand; Server-Defaulttip allein genügt nicht |
| R15 | Wie werden Root-BSD-2-Clause, PCL-BSD-3-Clause, Eigen-/Runtimebedingungen und Notices bei gemeinsamer Binärverteilung erfüllt? | Konkrete Artefakt-/Packagingprüfung, keine pauschale Library-Kompatibilität |
| R16 | Modification Notice im V4-Dokument abgeschlossen, spätere externe Übernahme offen | Externe Anwendung bleibt separate Aufgabe mit ausdrücklicher Freigabe und konkret geprüftem Distributionsumfang |

### 11.21 Technische Lizenzimplementierung und Abschlussstatus

| Ebene / Teilaufgabe | Stand nach V4-004 | Status |
| --- | --- | --- |
| Wissenschaftlicher Vergleich / Inventur | Vorhandener Quellen-/Matrix-/Dependency-/LiDAR-Bestand genutzt | VERIFIED im dokumentierten Rechercheumfang |
| Lizenz ausgewählt | Ausdrücklicher Nutzerentscheid Apache-2.0 für autorisierte eigene Software | COMPLETED |
| Lizenz technisch implementiert | Root-/zwei paketlokale Originaltexte, XML/Setup und 18 eigene SPDX-Header; aktive Karten entfernt | VERIFIED im beauftragten technischen Umfang |
| Konkrete Lizenzdateien/Artefakte geprüft | Frischer Online-Bytevergleich, XML-/Setup-/Headerabgleich, sdist/Wheel/Copy-Shares | VERIFIED, keine Debian-/Gesamtbundlefreigabe |
| Persönliche Urheberschaft | Alleinentwicklererklärung bekräftigt; bisherige Namenshinweise erhalten | DOKUMENTIERT, keine unabhängige Rechtsprüfung |
| Rechtliche Freigabe vollständig geklärt | Arbeits-/Dienst-/sonstige Vertrags-/Befugnisfragen offen | NOT VERIFIED |
| Aktiver Datenumfang / historische Datenrechte | Aktiver Tree und geprüfte Pakete ohne PCDs; historische Gitobjekte/Rechte unverändert | Tree-Maßnahme VERIFIED, historische Rechtsfreigabe NOT VERIFIED |
| LiDAR-Modification-Notice-Dokumentation | Verifizierte historische Revisionen/Diffs und markierte unbekannte Felder | COMPLETED; keine externe Anwendung |
| AP01 insgesamt | Technische Teilmaßnahmen abgeschlossen, rechtliches Gesamtgate offen | BLOCKED |
| AP08 / AP10 | Dokumentation/Releasevorbereitung laufend | IN PROGRESS |
| AP02 / AP03 | AP02-Metadaten unter V4-008 abgenommen; Dependencyarbeit nicht begonnen | AP02 VERIFIED / AP03 NOT STARTED |

#### 11.21.1 Offizielle LICENSE und unveränderter Geltungsbereich

`LICENSE` ist byteidentisch zur vorgegebenen Quelle [Q52], inklusive aller neun Abschnitte und vollständigem Appendix: **11358 Byte, 202 physische Textzeilen, SHA-256 cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30**. Der Appendix bleibt Originaltext mit Platzhaltern; projektbezogene Attribution steht in den eigenen SPDX-Dateihinweisen und hier, nicht als Änderung des offiziellen Lizenztextes. Die Root-LICENSE hebt keine Fremdbedingungen auf und lizenziert die Karten nicht. Keine zusätzliche NOTICE-Datei wurde ohne nachgewiesenen Bedarf erzeugt; einschlägige bestehende Attributionen/gegebenenfalls NOTICE-Inhalte sind bei konkreter Distribution dennoch zu erhalten.

#### 11.21.2 Datei-Delta der AP01-Implementierung

Die historische 60-Pfad-Inventur 11.12 bleibt die Referenz vor V4-004. Neu kommt ausschließlich LICENSE hinzu; 61 versionierte Dateien nach Commit, keine neue Forschungsdatei. 18 zugeordnete Python-Dateien erhalten **je exakt zwei Kommentarzeilen**. In allen bleibt die bisherige Zeile `Copyright (c) Bastian Aumer` erhalten:

| Eigene Datei | Implementierte Änderung |
| --- | --- |
| `r3d_planner/launch/follower.launch.py` | `SPDX-FileCopyrightText: 2026 Bastian Aumer`; `SPDX-License-Identifier: Apache-2.0` ergänzt |
| `r3d_planner/launch/map.launch.py` | `SPDX-FileCopyrightText: 2026 Bastian Aumer`; `SPDX-License-Identifier: Apache-2.0` ergänzt |
| `r3d_planner/launch/planner.launch.py` | `SPDX-FileCopyrightText: 2026 Bastian Aumer`; `SPDX-License-Identifier: Apache-2.0` ergänzt |
| `r3d_planner/launch/preprocessor.launch.py` | `SPDX-FileCopyrightText: 2026 Bastian Aumer`; `SPDX-License-Identifier: Apache-2.0` ergänzt |
| `r3d_planner/r3d_planner/configuration.py` | `SPDX-FileCopyrightText: 2026 Bastian Aumer`; `SPDX-License-Identifier: Apache-2.0` ergänzt |
| `r3d_planner/r3d_planner/launching.py` | `SPDX-FileCopyrightText: 2026 Bastian Aumer`; `SPDX-License-Identifier: Apache-2.0` ergänzt |
| `r3d_planner/r3d_planner/odometry.py` | `SPDX-FileCopyrightText: 2026 Bastian Aumer`; `SPDX-License-Identifier: Apache-2.0` ergänzt |
| `r3d_planner/r3d_planner/r3d_local_filter.py` | `SPDX-FileCopyrightText: 2026 Bastian Aumer`; `SPDX-License-Identifier: Apache-2.0` ergänzt |
| `r3d_planner/r3d_planner/r3d_path_follower.py` | `SPDX-FileCopyrightText: 2026 Bastian Aumer`; `SPDX-License-Identifier: Apache-2.0` ergänzt |
| `r3d_planner/r3d_planner/r3d_path_test.py` | `SPDX-FileCopyrightText: 2026 Bastian Aumer`; `SPDX-License-Identifier: Apache-2.0` ergänzt |
| `r3d_planner/r3d_planner/r3d_pcd_path.py` | `SPDX-FileCopyrightText: 2026 Bastian Aumer`; `SPDX-License-Identifier: Apache-2.0` ergänzt |
| `r3d_planner/r3d_planner/r3d_rviz_interface.py` | `SPDX-FileCopyrightText: 2026 Bastian Aumer`; `SPDX-License-Identifier: Apache-2.0` ergänzt |
| `r3d_planner/setup.py` | `SPDX-FileCopyrightText: 2026 Bastian Aumer`; `SPDX-License-Identifier: Apache-2.0` ergänzt |
| `r3d_planner/test/test_configuration.py` | `SPDX-FileCopyrightText: 2026 Bastian Aumer`; `SPDX-License-Identifier: Apache-2.0` ergänzt |
| `r3d_preprocessor/r3d_preprocessor/r3d_pcd_analyser.py` | `SPDX-FileCopyrightText: 2026 Bastian Aumer`; `SPDX-License-Identifier: Apache-2.0` ergänzt |
| `r3d_preprocessor/r3d_preprocessor/r3d_pcd_publisher.py` | `SPDX-FileCopyrightText: 2026 Bastian Aumer`; `SPDX-License-Identifier: Apache-2.0` ergänzt |
| `r3d_preprocessor/r3d_preprocessor/r3d_pcd_voxel_publisher.py` | `SPDX-FileCopyrightText: 2026 Bastian Aumer`; `SPDX-License-Identifier: Apache-2.0` ergänzt |
| `r3d_preprocessor/setup.py` | `SPDX-FileCopyrightText: 2026 Bastian Aumer`; `SPDX-License-Identifier: Apache-2.0` ergänzt |

| Weitere Datei | Implementierte Änderung / Grenze |
| --- | --- |
| `LICENSE` | Vollständiger offizieller Apache-2.0-Text neu, unverändert |
| `r3d_planner/package.xml` | Ausschließlich license-TODO → Apache-2.0 |
| `r3d_preprocessor/package.xml` | Ausschließlich license-TODO → Apache-2.0 |
| Beide `setup.py` | Lizenzwert Apache-2.0 bereits vorhanden; nur oben erfasste Headerkommentare ergänzt |
| `docs/V4_ROS_COMPLIANCE_DEVELOPMENT.md` | Bestehendes Protokoll/22-teiliges Kapitel aktualisiert, V4-004 angefügt; kein zweiter Bericht |
| Sechs OSRF-Testtemplates / zwei leere Python-Marker | Byteidentisch; keine persönliche Attribution hinzugefügt |
| Konfiguration, übrige Texte/Ressourcen, neun PYC, beide PCDs | Byteidentisch; keine neue ungeprüfte Header-/Datenlizenzzuordnung |

Die Kommentardaten „Last modified“ des vorhandenen Standardheaders werden nicht als Funktionseingriff umgeschrieben; V4-004/Commit dokumentieren den Lizenzkommentar-Delta. Kein `setup()`-Aufruf oder Projektimport wurde für den Metadatencheck ausgeführt.

#### 11.21.3 Pflichttexte bei einer späteren Binärdistribution

Diese Übersicht ist eine **konditionale Packaging-Prüfliste**, keine bereits freigegebene Binärdistribution oder vollständige transitive SBOM. Nur tatsächlich mitgelieferte Source-/Binärkomponenten lösen die entsprechenden Weitergabepflichten aus; eine extern installierte Dependency wird nicht automatisch Teil des eigenen Sourcepakets. Die Originaltexte in 11.11/11.13 sind maßgeblich. Der Nutzerauftrag verlangt hier keine neue Binärdatei, kein Wheel, keinen Container und keinen Release.

| Tatsächlich mitgelieferter Bestandteil, falls zutreffend | Mitzugebende Hinweise / zu prüfende Pflichten | Noch erforderlicher Nachweis |
| --- | --- | --- |
| Eigene R3D-Software | Vollständige Apache-2.0-Lizenzkopie, relevante eigene Copyright-/Attributionshinweise, Änderungskennzeichnung, gegebenenfalls einschlägige NOTICE-Inhalte | Root-Source-Text vorhanden; tatsächliche sdist/Wheel/Debian-/Install-Mitnahme noch nicht getestet |
| Sechs OSRF-Templates, falls im Source-/Bundleumfang | Bestehende OSRF-Copyright-/Apache-Hinweise und Apache-Lizenz erhalten | Source-Dateien jetzt byteidentisch; tatsächlicher Paketinhalt später prüfen |
| Apache-lizenzierte ROS-Komponenten | Deren Apache-Texte, relevante Originalhinweise/Änderungs-/gegebenenfalls NOTICE-Bedingungen | Exakte mitgelieferte Pakete/Versionen; bei rein externer Installation keine pauschale Kopie aller ROS-Texte in R3D verlangen |
| BSD-3-Clause-Teile: NumPy-Hauptbestand, SciPy, NetworkX, konkrete sensor_msgs_py-/TF2-Module | Dateispezifische Copyrights, BSD-Bedingungen und Disclaimer in vorgeschriebenem Source-/Binärbegleitmaterial, Non-Endorsement beachten | Tatsächliche Versionen/Artefakte und weitere enthaltene Teile prüfen |
| MIT-Teile: Open3D-Hauptbestand, PyYAML, ggf. setuptools | Copyright-/Erlaubnistext in Kopien bzw. wesentlichen Teilen; zusätzliche native/andere Komponenten separat | Kein pauschales MIT-Gesamtetikett für alle Binaries; konkrete Bundledateien inventarisieren |
| NumPy-Wheel mit OpenBLAS/LAPACK/GCC-Runtime/libquadmath | Jeweilige Lizenz-/Copyrighttexte, GCC-Runtime-Ausnahmetext und LGPL-Hinweise; weitere Source-/Änderungs-/Relinkingpflichten anhand der konkreten Weitergabe prüfen | Tatsächliches Wheel/Plattform/Bibliotheken; bestehender lokaler Befund ersetzt keine Gesamtfreigabe und macht R3D-Source nicht automatisch GPL |
| Separate LiDAR-Odometrie und NDT | BSD-2-Clause mit Ryohei-Sasaki-/k.koide-Hinweisen, Bedingungen/Disclaimer; eigene Modifikationen separat attributieren | Konkrete Deployment-/Bundle-SHAs, Originaltexte im tatsächlichen Binärbegleitmaterial; Dokumentationsnotice ersetzt sie nicht |
| PCL-basierte Dateien/System-PCL | Zusätzliche BSD-3-Clause-Copyrights von Willow Garage/Open Perception und dateispezifische Bedingungen/Disclaimer | Gepinnte NDT-Header bekannt; konkreter PCL-/Binärumfang offen |
| Eigen-/Boost-/weitere System-/Python-/OpenMP-Teile | Betroffene MPL-2.0-/BSL-1.0-/PSF-/sonstige tatsächliche Texte und deren weitergehende Pflichten | Datei-/Versions-/Link-/Artefaktumfang, MPL-Sourcebereitstellung soweit einschlägig; keine einheitliche OpenMP-Librarylizenz behaupten |
| Alte versionierte PYC / unbekannte Ressourcenherkunft | Keine neu erfundene eigene Lizenzzuordnung aus dem Dateiformat ableiten | Vor späterer Verteilung Provenienz/Sourceidentität oder begründete Umfangsentscheidung; keine Entfernung in V4-004 |
| Historische PCD-Karten | Nicht Teil des aktiven Tree/erzeugten sdists/Wheels/Installbaums | Keine Rechteheilung/Löschung historischer Gitobjekte; künftig keine Wiedereinbindung ohne Freigabe |

V4-004 ließ Installationsregeln unverändert. V4-006 ergänzt nun paketlokale identische LICENSEs, explizite Sharemitnahme und license_files und weist Originaltextkopien in beiden sdists, Wheels und Copy-colcon-Shares konkret nach. Das ist kein Nachweis eines tatsächlichen Debian-/Buildfarmartefakts oder jeder künftigen Distribution; solche Nachweise bleiben AP04/AP10. Bei einem gemeinsamen Container/Bundle sind auch transitive und native Komponenten tatsächlich zu inventarisieren.

#### 11.21.4 Abschluss und verbleibende Gates

Für den beauftragten eigenen Code sind Auswahl, Attribution, Lizenzdatei und Lizenzfelder umgesetzt und statisch geprüft. Keine weitere allgemeine Lizenzrecherche ist für den nächsten unabhängigen technischen AP vorgesehen. Noch offen sind konkrete arbeits-/dienstvertragliche Rechte, Rechte an historischen Karten-Gitobjekten, unklare Artefaktprovenienz und sämtliche zusätzlichen Texte/Pflichten bei einer vollständigen transitiven/nativen Binärdistribution. Die aktive Karte ist entfernt und eigene sdist-/Wheel-/Copy-Sharetextmitnahme ist unter V4-006 geprüft. Diese Grenzen bleiben AP01-Rechtsgesamtgate/AP10-Releasegate; keine rechtliche Gesamtfreigabe, Patentgarantie oder Veröffentlichung. AP02 wurde unter V4-008 separat beauftragt/technisch verifiziert; AP03 wird erst nach einem neuen Auftrag begonnen.

#### 11.21.5 Abschließende Verifikation und Distributionsgrenzen, 14. Oktober 2026

Die 18 zugeordneten eigenen Python-Dateien einschließlich Launch-/Setup-/Testdatei haben weiterhin exakt die angewandten persönlichen SPDX-Zeilen. Sechs OSRF-Testtemplates behalten Originalcopyright und Apache-Hinweise; ihr Sourcearchiveinhalt wurde byteidentisch geprüft. Leere Python-/ament-Marker, Paketmetadaten, YAML, TXT/Dokumentation und neun ältere PYC bekommen keine neue unbelegte Autorzuordnung. PYC-Provenienz ist im Repository nicht unabhängig geklärt; die konkret erzeugten sdists/Wheels enthalten jedoch keine PYC. `r3d_planner/points.txt` enthält weiterhin ortsspezifische CLI-Koordinaten/Bezeichnungen; Daten-/Vertragsprovenienz nicht verifiziert, daraus allein kein nachgewiesener Copyright- oder Lizenzverstoß. Keine anderen mitgelieferten PCD-Beispieldaten identifiziert. Temporäre Synthesefälle sind Testfixtures, keine veröffentlichte Standardkarte.

Roottext und zwei paketlokale LICENSEs entsprechen dem erneut abgerufenen offiziellen ASF-TXT. Lizenztexte/Originalheader in fremden Templates sind erhalten. Für die im R3D-Tree enthaltenen Fremdtemplates ist keine separate upstream NOTICE-Datei identifiziert; daraus wird keine Aussage über sämtliche externen ROS-/Native-Binaries abgeleitet. Die bedingten Noticepflichten aus 11.8/11.21.3 gelten nach tatsächlichem Distributionsumfang. Die getrennte LiDAR-Dokumentationsnotice ersetzt weder BSD-Texte noch PCL/NDT-Dateihinweise; tatsächliche externe Deployment-/Bundlemitnahme bleibt NOT VERIFIED.

| Distributionsweg | Aktueller Nachweis | Rechts-/Technikgrenze |
| --- | --- | --- |
| Aktueller Source-Tree/Sourcearchive | Keine PCDs, Root-/Paket-Lizenztexte und Originaltemplates erhalten; zwei konkrete sdists geprüft | Vollständiger Git-Klon enthält historische Kartenobjekte; individuelle Befugnisse/sonstige Provenienz offen |
| ROS-Index-Registrierung | Lizenzfelder/Text und datenfreier aktiver Tree vorhanden | Public-V4-Ref nicht übertragen; AP02-Metadaten geprüft, Namenskollision/Serverreview/individuelle Rechte weiter offen |
| Installation über rosdep | Lizenzwahl verändert weder Keys noch installierte Dependencies | AP03 nicht begonnen; keine rosdep-Auflösung/Installation/Gesamtlizenzfreigabe |
| Wheels / colcon-Copy-Shares | Beide Wheels mit .dist-info- und Share-LICENSE; zwei Shares aus isolierten sdists; 0 PCDs | Konkrete temporäre Artefakte, keine transitive Librarymitlieferung bzw. allgemeine Copy-Defaultabnahme |
| Debian/Bloom/Buildfarm | Paketlokale Originaltexte und data_files schaffen technische Voraussetzung | Kein Debianpaket/Farmjob erzeugt; Entwicklungsversionskonsistenz durch AP02 geprüft, Releasepolitik/Dependencies/Installverträge/sonstige Rechte weiterhin offen |
| Gemeinsames LiDAR-/NumPy-/Native-Bundle | Inventar trennt Eigen-/Fremdsource, externe Installation und mögliche Runtime-/LGPL-/BSD-/MPL-Anteile | Vollständige transitive/native SBOM und Pflichttext-/Source-/Binärprüfung nicht durchgeführt |

| Temporäres Artefakt | SHA-256 | Lizenz-/Datenprüfung |
| --- | --- | --- |
| `r3d_planner-0.0.1.tar.gz` | `8a7ac8336e6d038b17ee902ca5f8c964e3f6be696c256c72a96dccf7dd614fb6` | Originaltext enthalten; 0 PCD/0 PYC |
| `r3d_planner-0.0.1-py3-none-any.whl` | `9b08b499056fac1d67d8bf61c68a2bfef256df830d5a31647780a3b0889ba061` | Originaltext enthalten; 0 PCD/0 PYC |
| `r3d_preprocessor-0.0.1.tar.gz` | `dde79e940e92d1fe74255998b008ba361218880f3d84bde870a86308dbceca2b` | Originaltext enthalten; 0 PCD/0 PYC |
| `r3d_preprocessor-0.0.1-py3-none-any.whl` | `2867b781953225090cff7af92b33dd25482431d1e14a685e2da3a6035c56b2ab` | Originaltext enthalten; 0 PCD/0 PYC |

Die Archive liegen nur in temporären Prüfverzeichnissen und wurden nicht committed, hochgeladen oder als Release verteilt. Paketkopien liegen nach Commit in r3d_planner/LICENSE/r3d_preprocessor/LICENSE; Roottext bleibt maßgebliche unveränderte Referenz. Technische AP01-Kriterien sind VERIFIED, vollständige rechtliche/Releasefreigabe NOT VERIFIED/BLOCKED.

### 11.22 Quellenverzeichnis

Die Recherchequellen wurden unter V4-002/V4-003 am **13. Oktober 2026** gelesen, sofern nicht ausdrücklich ein gescheiterter Webzugriff mit lokalem Ersatz genannt ist. Q52 wurde unter V4-006 am **14. Oktober 2026** erneut abgerufen; Original-/Modifikations-Gitobjekte und lokale Copyright-/Artefaktbelege wurden gezielt kontrolliert, ohne die übrige Recherche als erneut online geprüft auszugeben. Die Lizenztexte sind maßgeblich; deutsche Zusammenfassungen sind Auswertungen. Versions-Tags sind konkrete Upstream-Referenzen, Humble-/main-Links bewegliche Stände. Die Quellenliste enthält keine erfundenen URLs aus den unauflösbaren Markern der Sekundär-PDF.

| ID | Primärquelle und URL | Verwendungszweck / Zugriff | Nachweisstatus |
| --- | --- | --- | --- |
| Q01 | [Apache License 2.0, ASF](https://www.apache.org/licenses/LICENSE-2.0.html) | Abschnitte 1-9; Zugriff 13.10.2026 | Verifiziert im benannten Umfang |
| Q02 | [MIT, OSI](https://opensource.org/license/mit) | Text und Kennung; Zugriff 13.10.2026 | Verifiziert im benannten Umfang |
| Q03 | [BSD-2-Clause, OSI](https://opensource.org/license/bsd-2-clause) | Text und Kennung; Zugriff 13.10.2026 | Verifiziert im benannten Umfang |
| Q04 | [BSD-3-Clause, OSI](https://opensource.org/license/bsd-3-clause) | Text und Non-Endorsement; Zugriff 13.10.2026 | Verifiziert im benannten Umfang |
| Q05 | [SPDX License List](https://spdx.org/licenses/) | Vier Kennungen/OSI-Zuordnung; Zugriff 13.10.2026 | Verifiziert im benannten Umfang |
| Q06 | [ASF Licensing and Distribution FAQ](https://www.apache.org/foundation/license-faq.html) | Abgrenzung Patentumfang, Notice-/Beitrags-/ASF-Prozess; Zugriff 13.10.2026 | Verifiziert im benannten Umfang |
| Q07 | [rosdistro Review Guidelines](https://github.com/ros/rosdistro/blob/master/REVIEW_GUIDELINES.md) | Index-/Releasekriterien; offizieller Raw-Text gelesen, Zugriff 13.10.2026 | Verifiziert im benannten Umfang |
| Q08 | [REP-149](https://www.ros.org/reps/rep-0149.html), [offizieller Quelltext](https://github.com/ros-infrastructure/rep/blob/master/rep-0149.rst) | Mehrere License-Tags, Quellenfassung gelesen; Zugriff 13.10.2026 | Verifiziert im benannten Umfang |
| Q09 | [§ 7 UrhG](https://www.gesetze-im-internet.de/urhg/__7.html) | Urheber; Zugriff 13.10.2026 | Verifiziert im benannten Umfang |
| Q10 | [§ 8 UrhG](https://www.gesetze-im-internet.de/urhg/__8.html) | Miturheber; Zugriff 13.10.2026 | Verifiziert im benannten Umfang |
| Q11 | [§ 31 UrhG](https://www.gesetze-im-internet.de/urhg/__31.html) | Nutzungsrechte; Zugriff 13.10.2026 | Verifiziert im benannten Umfang |
| Q12 | [§ 69a UrhG](https://www.gesetze-im-internet.de/urhg/__69a.html) | Programm-/Ideenschutz; direkter amtlicher HTTPS-Abruf nach Web-Timeout, 13.10.2026 | Verifiziert im benannten Umfang |
| Q13 | [§ 29 UrhG](https://www.gesetze-im-internet.de/urhg/__29.html) | Urheberrecht vs Nutzungsrechte; amtlicher HTTPS-Abruf, 13.10.2026 | Verifiziert im benannten Umfang |
| Q14 | [§ 69b UrhG](https://www.gesetze-im-internet.de/urhg/__69b.html) | Arbeits-/Dienstverhältnisse; Zugriff 13.10.2026 | Verifiziert im benannten Umfang |
| Q15 | [§ 69c UrhG](https://www.gesetze-im-internet.de/urhg/__69c.html) | Vermögensrechtliche Handlungen; amtlicher HTTPS-Abruf, 13.10.2026 | Verifiziert im benannten Umfang |
| Q16 | [§ 13 UrhG](https://www.gesetze-im-internet.de/urhg/__13.html) | Urheberbezeichnung; amtlicher HTTPS-Abruf, 13.10.2026 | Verifiziert im benannten Umfang |
| Q17 | [§ 2 UrhG](https://www.gesetze-im-internet.de/urhg/__2.html) | Werkvoraussetzungen/Karten; amtlicher HTTPS-Abruf, 13.10.2026 | Verifiziert im benannten Umfang |
| Q18 | [§ 87a UrhG](https://www.gesetze-im-internet.de/urhg/__87a.html), [§ 87b UrhG](https://www.gesetze-im-internet.de/urhg/__87b.html) | Datenbankherstellerrechte; amtlicher HTTPS-Abruf, 13.10.2026 | Verifiziert im benannten Umfang |
| Q19 | [§ 276 BGB](https://www.gesetze-im-internet.de/bgb/__276.html) | Vorsatzhaftung; amtlicher HTTPS-Abruf, 13.10.2026 | Verifiziert im benannten Umfang |
| Q20 | [§ 309 BGB](https://www.gesetze-im-internet.de/bgb/__309.html) | Grenzen im AGB-Anwendungsbereich, insbesondere Nr. 7; amtlicher HTTPS-Abruf, 13.10.2026 | Verifiziert im benannten Umfang |
| Q21 | [Apache-2.0 bei OSI](https://opensource.org/license/apache-2-0), [SPDX-Text](https://spdx.org/licenses/Apache-2.0.html) | Kontrollfassung des Lizenztextes; Zugriff 13.10.2026 | Verifiziert im benannten Umfang |
| Q22 | [ROS 2 Humble: Migrating Packages, Licensing](https://github.com/ros2/ros2_documentation/blob/humble/source/How-To-Guides/Migrating-from-ROS1/Migrating-Packages.rst) | Apache-Empfehlung und bestehende Beitragsrechte; Zugriff 13.10.2026 | Verifiziert im benannten Umfang |
| Q23 | [NumPy v1.26.4 Wheel-Lizenzen](https://github.com/numpy/numpy/blob/v1.26.4/tools/wheels/LICENSE_linux.txt) | Zusätzliche Binärkomponenten; Zugriff 13.10.2026; lokales dist-info/LICENSE.txt zusätzlich gelesen | Verifiziert im benannten Umfang |
| Q24 | [NumPy v1.26.4 LICENSE](https://github.com/numpy/numpy/blob/v1.26.4/LICENSE.txt) | Hauptlizenz; Zugriff 13.10.2026 | Verifiziert im benannten Umfang |
| Q25 | [SciPy v1.8.0 LICENSE](https://github.com/scipy/scipy/blob/v1.8.0/LICENSE.txt) | Hauptlizenz; Zugriff 13.10.2026 | Verifiziert im benannten Umfang |
| Q26 | [NetworkX 3.4.2 LICENSE](https://github.com/networkx/networkx/blob/networkx-3.4.2/LICENSE.txt) | Hauptlizenz; Zugriff 13.10.2026 | Verifiziert im benannten Umfang |
| Q27 | [Open3D v0.19.0 LICENSE](https://github.com/isl-org/Open3D/blob/v0.19.0/LICENSE) | Hauptlizenz; Zugriff 13.10.2026 | Verifiziert im benannten Umfang |
| Q28 | [PyYAML 5.4.1 LICENSE](https://github.com/yaml/pyyaml/blob/5.4.1/LICENSE) | Hauptlizenz; Zugriff 13.10.2026 | Verifiziert im benannten Umfang |
| Q29 | [sensor_msgs_py point_cloud2.py, Humble](https://github.com/ros2/common_interfaces/blob/humble/sensor_msgs_py/sensor_msgs_py/point_cloud2.py) | Verwendeter Modulheader mit drei BSD-Klauseln; Zugriff 13.10.2026 | Verifiziert im benannten Umfang |
| Q30 | [Python-TF2 __init__.py, Humble](https://github.com/ros2/geometry2/blob/humble/tf2_ros_py/tf2_ros/__init__.py) | BSD-3-Clause-Header; Zugriff 13.10.2026 | Verifiziert im benannten Umfang |
| Q31 | [rclpy LICENSE, Humble](https://github.com/ros2/rclpy/blob/humble/LICENSE) | Apache-Text; Zugriff 13.10.2026 | Verifiziert im benannten Umfang |
| Q32 | [nav2_msgs package.xml, Humble](https://github.com/ros-navigation/navigation2/blob/humble/nav2_msgs/package.xml) | Apache-2.0-Deklaration; Zugriff 13.10.2026 | Verifiziert im benannten Umfang |
| Q33 | [geometry_msgs package.xml](https://github.com/ros2/common_interfaces/blob/humble/geometry_msgs/package.xml) | Deklaration; Zugriff 13.10.2026 | Verifiziert im benannten Umfang |
| Q34 | [nav_msgs package.xml](https://github.com/ros2/common_interfaces/blob/humble/nav_msgs/package.xml) | Deklaration; Zugriff 13.10.2026 | Verifiziert im benannten Umfang |
| Q35 | [sensor_msgs package.xml](https://github.com/ros2/common_interfaces/blob/humble/sensor_msgs/package.xml) | Deklaration; Zugriff 13.10.2026 | Verifiziert im benannten Umfang |
| Q36 | [sensor_msgs_py package.xml](https://github.com/ros2/common_interfaces/blob/humble/sensor_msgs_py/package.xml) | Generische BSD-Deklaration; Zugriff 13.10.2026 | Verifiziert im benannten Umfang |
| Q37 | [tf2_ros package.xml](https://github.com/ros2/geometry2/blob/humble/tf2_ros/package.xml) | Generische BSD-Deklaration; Zugriff 13.10.2026 | Verifiziert im benannten Umfang |
| Q38 | [tf2_ros_py package.xml](https://github.com/ros2/geometry2/blob/humble/tf2_ros_py/package.xml) | Python-Provider/Deklaration; Zugriff 13.10.2026 | Verifiziert im benannten Umfang |
| Q39 | [std_msgs package.xml](https://github.com/ros2/common_interfaces/blob/humble/std_msgs/package.xml) | Deklaration; Zugriff 13.10.2026 | Verifiziert im benannten Umfang |
| Q40 | [visualization_msgs package.xml](https://github.com/ros2/common_interfaces/blob/humble/visualization_msgs/package.xml) | Deklaration; Zugriff 13.10.2026; lokaler 4.9.2-Stand separat gelesen | Verifiziert im benannten Umfang |
| Q41 | [std_srvs package.xml](https://github.com/ros2/common_interfaces/blob/humble/std_srvs/package.xml) | Deklaration; Zugriff 13.10.2026 | Verifiziert im benannten Umfang |
| Q42 | [launch package.xml](https://github.com/ros2/launch/blob/humble/launch/package.xml) | Deklaration; Zugriff 13.10.2026 | Verifiziert im benannten Umfang |
| Q43 | [launch_ros package.xml](https://github.com/ros2/launch_ros/blob/humble/launch_ros/package.xml) | Deklaration; Zugriff 13.10.2026 | Verifiziert im benannten Umfang |
| Q44 | [ament_index_python package.xml](https://github.com/ament/ament_index/blob/humble/ament_index_python/package.xml) | Deklaration; Zugriff 13.10.2026 | Verifiziert im benannten Umfang |
| Q45 | [setuptools v59.6.0 LICENSE](https://github.com/pypa/setuptools/blob/v59.6.0/LICENSE) | MIT-Text statt lokalem UNKNOWN-Feld; Zugriff 13.10.2026 | Verifiziert im benannten Umfang |
| Q46 | [pytest LICENSE, main](https://github.com/pytest-dev/pytest/blob/main/LICENSE) | Aktuelle Kontrollquelle; Zugriff 13.10.2026; lokales 6.2.5-Metadatum separat gelesen | Verifiziert im benannten Umfang |
| Q47 | [ament_copyright package.xml](https://github.com/ament/ament_lint/blob/humble/ament_copyright/package.xml) | Web-Cacheabruf fehlgeschlagen; stattdessen `/opt/ros/humble/share/ament_copyright/package.xml` als lokale Primärdatei am 13.10.2026 gelesen | Verifiziert im benannten Umfang |
| Q48 | [ament_flake8 package.xml](https://github.com/ament/ament_lint/blob/humble/ament_flake8/package.xml) | Deklaration; Zugriff 13.10.2026 | Verifiziert im benannten Umfang |
| Q49 | [ament_pep257 package.xml](https://github.com/ament/ament_lint/blob/humble/ament_pep257/package.xml) | Apache und MIT; Zugriff 13.10.2026 | Verifiziert im benannten Umfang |
| Q50 | [Python 3.10: History and License](https://docs.python.org/3.10/license.html) | PSF-Rahmen und weitere eingebundene Lizenzen; Zugriff 13.10.2026; kein versionsidentischer 3.10.12-Gesamtaudit | Verifiziert im benannten Umfang |
| Q51 | [ros2pkg Humble Testtemplate](https://github.com/ros2/ros2cli/blob/humble/ros2pkg/ros2pkg/resource/ament_python/test_flake8.py.em) | Fremdcode-/Notice-Beispiel; Zugriff 13.10.2026; alle drei lokalen Vorlagen zusätzlich verglichen | Verifiziert im benannten Umfang |
| Q52 | [Offizieller Apache-2.0-TXT-Text, ASF](https://www.apache.org/licenses/LICENSE-2.0.txt) | V4-004 Originaldownload 13.10.2026; V4-006 erneut frisch abgerufen 14.10.2026; 11358 Byte/cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30 | Verifiziert: Root-/Paket-/Artefaktkopien byteidentisch; keine Lizenzzusätze |

Sekundär-/Projektquellen: bereitgestellte siebenseitige Lizenzrecherche mit SHA in 11.1; unveränderte historische 33-seitige PDF mit SHA in 2.1; Code/Manifeste/Setup am Baseline-Commit; zentraler Initialisierungscommit `d355db9bbb284024fad0d1295ba768cd0001a5ee`. Sie ersetzen keine der vorgenannten Primärquellen. Keine PDF wurde in das Repository kopiert oder verändert.

#### 11.22.1 Externe LiDAR-Quellen und Git-Nachweise

Alle Zugriffe am **13. Oktober 2026**. Pinned Source-/Diff-Links beziehen sich auf die tatsächlich untersuchten Objekte. Die Bare-Analyse bestätigt Git-Abstammung und Dateiinhalt, keine vollständige rechtliche Rechtekette.

| ID | Primärquelle / URL | Relevante Aussage | Nachweisstatus |
| --- | --- | --- | --- |
| L01 | [Originalrepository](https://github.com/rsasaki0109/lidar_slam_ros2) | Git-/Sourceherkunft, develop-Tip a3b83d7… | Verifiziert per Metadaten und Bare-Historie |
| L02 | [Abgeleitetes Repository](https://github.com/RoboProjekt/lidar_odom/tree/69c0e093cb19d2367476466716aa547d7c753327) | Aktiver untersuchter Source-Tree | Verifiziert |
| L03 | [Ausgangsrevision](https://github.com/rsasaki0109/lidar_slam_ros2/commit/2f8753853854a528654243c92073a277f4f27226) | Gemeinsamer Vorfahr, direkter Ausgangspunkt der Anpassung | Verifiziert per merge-base und Parent |
| L04 | [Original-LICENSE am Ausgangspunkt](https://github.com/rsasaki0109/lidar_slam_ros2/blob/2f8753853854a528654243c92073a277f4f27226/LICENSE) | BSD-2-Clause, Ryohei Sasaki | Verifiziert, identischer Blob im abgeleiteten Tree |
| L05 | [Frontend-Commit](https://github.com/RoboProjekt/lidar_odom/commit/abfc13d14eab4c7cc04d489083697711d4585f8a) | Neues lokales Odometriepaket und zehn Dateien | Verifiziert per Diff |
| L06 | [Ignore-Commit](https://github.com/RoboProjekt/lidar_odom/commit/d2c9ed69662b4a892c576bdf8fcea1dcd7d90ed4) | Vier COLCON_IGNORE-Dateien | Verifiziert per Diff |
| L07 | [Bereinigungs-/Build-Commit](https://github.com/RoboProjekt/lidar_odom/commit/69c0e093cb19d2367476466716aa547d7c753327) | Entfernung, NDT-Buildstrategie, Timestamp-Helfer/Test | Verifiziert per Diff |
| L08 | [NDT-LICENSE am Gitlink](https://github.com/rsasaki0109/ndt_omp_ros2/blob/497411279593eb261a3e3d04cdcbb4717af33ca3/LICENSE) | BSD-2-Clause, k.koide 2019 | Verifiziert |
| L09 | [NDT-Header](https://github.com/rsasaki0109/ndt_omp_ros2/blob/497411279593eb261a3e3d04cdcbb4717af33ca3/include/pclomp/ndt_omp.h) | PCL-/Willow-Garage-/Open-Perception-BSD-3-Clause | Verifiziert |
| L10 | [GICP-Header](https://github.com/rsasaki0109/ndt_omp_ros2/blob/497411279593eb261a3e3d04cdcbb4717af33ca3/include/pclomp/gicp_omp.h) | Weitere konkrete PCL-Attribution | Verifiziert; impl-Header und voxel_grid_covariance_omp.h zusätzlich gelesen |
| L11 | [LiDAR-CMake](https://github.com/RoboProjekt/lidar_odom/blob/69c0e093cb19d2367476466716aa547d7c753327/lidar_odom/CMakeLists.txt) | Statisch kompilierte Submodulsource, Systemabhängigkeiten, Installregeln | Verifiziert im Source; kein Build |
| L12 | [LiDAR-Node](https://github.com/RoboProjekt/lidar_odom/blob/69c0e093cb19d2367476466716aa547d7c753327/lidar_odom/src/lidar_odometry_node.cpp) | ROS-Vertrag, eigenes Copyrightjahr ohne Name, BSD-Identifier | Verifiziert im Source; kein Laufzeitnachweis |
| L13 | [PCL 1.12.1 LICENSE](https://github.com/PointCloudLibrary/pcl/blob/pcl-1.12.1/LICENSE.txt) | BSD-3-Clause-Referenztext | Verifiziert als Referenz, eingesetzte Deploymentversion nicht verifiziert |
| L14 | [Eigen 3.4.0 COPYING.MPL2](https://gitlab.com/libeigen/eigen/-/blob/3.4.0/COPYING.MPL2) | MPL-2.0-Referenztext | Verifiziert als Referenz, Deployment-/Dateiumfang offen |
| L15 | [Boost License 1.0](https://www.boost.org/LICENSE_1_0.txt) | BSL-1.0-Referenztext | Verifiziert als Referenz, konkrete Version offen |
| L16 | [rclcpp LICENSE](https://github.com/ros2/rclcpp/blob/humble/LICENSE), [tf2_eigen package.xml](https://github.com/ros2/geometry2/blob/humble/tf2_eigen/package.xml) | ROS-C++-/TF-Referenzen für externe Komponente | Verifiziert für gelesene Quellen; keine vollständige Binärfreigabe |
| L17 | [NDT-Manifest](https://github.com/rsasaki0109/ndt_omp_ros2/blob/497411279593eb261a3e3d04cdcbb4717af33ca3/package.xml) | Unspezifisches BSD, Build-/PCL-Bedarf | Verifiziert; genaue Headerbedingungen separat |

Entwicklererklärung: ergänzter Nutzerauftrag vom 13.10.2026, dokumentiert in 11.10; kein unabhängiger Rechtsnachweis. GitHub-Sichtbarkeits-/Remotequellen stehen separat in Abschnitt 12. Fremde Repository-AGENTS-Dateien wurden ausschließlich als Sourceinhalt betrachtet; keine dortigen Software-/Buildanweisungen ausgeführt. Der damalige V4-002/V4-003-Projekt-Schreibzugriff betraf ausschließlich dieses Dokument. Die ausdrücklich freigegebene anschließende V4-004-Implementierung betrifft zusätzlich nur LICENSE, eigene Kommentarheader und zwei Manifest-Lizenzfelder; externe Repositorys bleiben unverändert.

## 12. Private V4-Entwicklung auf GitHub

### 12.1 Tatsächlich geprüfter Zustand

Die Prüfung war ausschließlich lesend; API-Zugriff am 13. Oktober 2026. Im R3D-Repository erfolgten kein Fetch, Push oder Ändern von Remotes; auf GitHub kein Erstellen oder Sichtbarkeitswechsel. Die externen LiDAR-Bare-Caches aus V4-003 sind davon getrennte temporäre Analysekopien. Ein GitHub-Branch hat keine vom Repository unabhängige private Sichtbarkeit [G01].

| Gegenstand | Beobachtung | Nachweis |
| --- | --- | --- |
| Aktiver Branch / Eingang-HEAD | V4, `d355db9bbb284024fad0d1295ba768cd0001a5ee` | git branch --show-current; git log -5; keine zusätzlichen Commits seit Initialisierung |
| origin Fetch-/Push-URL | Beide `git@github.com:RoboProjekt/R3D-Planner.git` | git remote -v; kein eigener pushurl konfiguriert |
| Fetch-Refspec | `+refs/heads/*:refs/remotes/origin/*` | git config: alle origin-Branches würden bei einem späteren Fetch erfasst |
| Tracking main | origin/main | branch.main.remote=origin, merge=refs/heads/main |
| Tracking V4 | Kein Upstream, kein eigener pushRemote | Keine branch.V4.remote/merge/pushRemote-Konfiguration |
| Push-Defaults | remote.pushDefault und push.default nicht explizit gesetzt; keine zusätzlichen remote.push-Refspecs gefunden | Gelesene effektive Konfiguration; Git-Standardverhalten ist kein aktiver Veröffentlichungsschutz |
| Server-Sichtbarkeit | public | GitHub get_repo für RoboProjekt/R3D-Planner, visibility=public [G04] |
| Server-Branches | V1, V2, V3, main; Tips entsprechen den bekannten Referenzen | GitHub Branches-API [G05], vollständige vier Einträge bei per_page=100 |
| Remote V4 | Auf dem aktuell konfigurierten Server kein V4 in der Branchliste | G05; Aussage zeitgebunden, nicht über unbekannte andere Repositories |
| Geplanter Name R3D-Planner-Development | Get-Repo-Abfrage lieferte 404 / Not Found | G06; kann Nichtexistenz oder fehlenden Zugriff bedeuten, keine sichere Aussage über alle privaten Repositories |

Ein fehlender Upstream allein verhindert keinen ausdrücklichen `git push origin V4`. Der aktuelle origin ist weiterhin ein öffentliches Pushziel. Die folgende Absicherung ist daher ein **Vorschlag**, noch keine konfigurierte Schutzmaßnahme.

### 12.2 Optionen und Auswirkungen

| Aspekt | Option A: bestehendes Repository PRIVATE | Option B: eigenständiges privates Development-Repository |
| --- | --- | --- |
| Ziel | RoboProjekt/R3D-Planner insgesamt privat machen | Öffentliches RoboProjekt/R3D-Planner unverändert lassen; V4 in RoboProjekt/R3D-Planner-Development entwickeln |
| Sichtbarkeit | Alle Branches dieses Repositorys gemeinsam privat | Öffentliche Baseline bleibt sichtbar; neue V4-Commits ausschließlich im separaten privaten Repository |
| Bestehende Öffentlichkeit | Zugriff öffentlicher Nutzer entfällt; bereits vorhandene externe Kopien/Forks werden nicht zurückgeholt | Bisherige öffentlichen Branches bleiben unverändert |
| GitHub-Nebenwirkungen | Sichtbarkeitswechsel kann Features sowie Stars/Watchers/Fork-Verknüpfungen beeinflussen [G02] | Separater Zugang/Berechtigungen und Pflege zweier Ziele erforderlich |
| Lokale Remotes | URL kann gleich bleiben; Sichtbarkeit vor jeder Übertragung nachweisen | Öffentliches origin als Fetchquelle behalten, Push dorthin sperren; privates Ziel getrennt benennen |
| Historische Nachweise | Git-Historie bleibt technisch erhalten, öffentliches Nachprüfen eingeschränkt | Gemeinsame Baseline-Historie bleibt nachvollziehbar; spätere öffentliche Übernahme separat freigeben |
| Noch erforderliche Entscheidung | Ausdrückliche Freigabe des gesamten Sichtbarkeitswechsels | Ausdrückliche Freigabe eines eigenständigen PRIVATE-Repositorys und der lokalen Remote-Absicherung |

**Empfehlung: Option B**, weil der formulierte Wunsch die vorläufig private V4-Entwicklung betrifft und der bisher öffentliche Bestand unverändert bleiben kann. Ein gewöhnlicher Fork des öffentlichen Repositorys ist dafür ungeeignet: öffentliche Forks sind öffentlich und ihre Sichtbarkeit lässt sich nicht einzeln auf privat umstellen [G03]. Gemeint ist ein unabhängiges privates Repository mit bewusst übernommenen Git-Objekten, kein öffentlicher Fork. Auch private Weitergabe an weitere Personen/Cloudspeicherung ist keine rechtliche Freigabe des Codes; AP01 bleibt unabhängig davon offen.

### 12.3 Vorgeschlagener Remote-Workflow - NICHT AUSGEFÜHRT

Die folgenden Befehle sind ausschließlich eine reviewbare Vorlage nach ausdrücklicher Freigabe. Sie sind nicht Teil der in V4-002 ausgeführten Befehle. Auch ein Dry-Run gegen GitHub wird hier nicht gestartet. Repositoryerstellung, lokale Konfigurationsänderung und tatsächlicher Push sind getrennte Schritte und benötigen die jeweils erforderliche Nutzerfreigabe.

1. Ein unabhängiges leeres privates Repository unter dem abgestimmten Namen anlegen; keine automatische LICENSE-/README-Erzeugung und keine öffentliche Fork-Erstellung. Vorher Verfügbarkeit, Eigentümer und Zugriffsrechte klären, da die aktuelle 404-Abfrage keine definitive Nichtexistenz beweist.
2. Sichtbarkeit und Unabhängigkeit per API bestätigen. Bei anderem Ziel, public-Sichtbarkeit oder unerwartetem fork-Status abbrechen; nicht stillschweigend umstellen.
3. Öffentliche Push-URL im lokalen Repository unbrauchbar setzen, Fetch-URL beibehalten. Private Remote und explizite Pushregeln konfigurieren. Mehrere effektive Push-URLs/Refspecs kontrollieren.
4. Erst nach separater Pushfreigabe ausschließlich V4 übertragen. Keine mirror-/all-/tags-Übertragung und kein öffentlicher V4-Push.
5. Private Remote-Branch-SHA mit lokalem V4-HEAD vergleichen; öffentlich weiterhin V1/V2/V3/main ohne V4 bestätigen. Unversionierte PDFs werden durch einen Git-Push nicht automatisch gespeichert.

```bash
# VORLAGE: erst nach ausdrücklicher Freigabe; hier NICHT ausgeführt.
# A. Separat autorisierte Erstellung, falls noch nicht vorhanden:
gh repo create RoboProjekt/R3D-Planner-Development --private

# B. Nur lesender Gate-Check, bei unerwartetem Ergebnis abbrechen:
gh api repos/RoboProjekt/R3D-Planner-Development \
  --jq '{full_name, visibility, fork}'
# Erwartet: exakt der vereinbarte Name, visibility="private", fork=false.

# C. Separat autorisierte lokale Remote-Absicherung:
git remote set-url --push origin /dev/null
git remote add private git@github.com:RoboProjekt/R3D-Planner-Development.git
git config --local remote.pushDefault private
git config --local branch.V4.pushRemote private
git config --local push.default nothing

# D. Effektive Ziele kontrollieren:
git remote -v
git remote get-url --push --all origin
git remote get-url --push --all private
git config --get-regexp '^remote\..*\.(pushurl|push|mirror)$'
git config --get remote.pushDefault
git config --get branch.V4.pushRemote
git config --get push.default

# E. NUR nach bestätigtem privaten Ziel UND ausdrücklicher Pushfreigabe:
git push --set-upstream private V4:V4
```

`/dev/null` ist unter der Zielumgebung Ubuntu kein Git-Repository und lässt einen Push über den Namen origin scheitern; die öffentliche Fetch-URL bleibt erhalten. `push.default=nothing` verlangt eine explizite Refspec. `remote.pushDefault` und `branch.V4.pushRemote` lenken die Zielauswahl auf private [G07/G08]. Das verändert lokale Konfiguration, nicht die öffentliche Baseline-Historie. Der vorhandene main-Upstream kann als Fetch-/Vergleichsreferenz bleiben; öffentliche Pushes über origin wären ebenfalls absichtlich blockiert.

Diese Einstellungen schützen gegen typische Fehlbedienung, nicht gegen bewusstes Umgehen per direkter öffentlicher URL, weitere Remotes, andere Clones oder gelockerte Konfiguration. Für stärkere organisatorische Absicherung wären getrennte Credentials/Schreibberechtigungen oder geprüfte Push-Policies erforderlich; hier werden keine Tokens, Berechtigungen oder Hooks geändert. Eine Namenwahl „private“ beweist außerdem keine Server-Sichtbarkeit; der API-Gate-Check bleibt notwendig.

### 12.4 Ausstehende Entscheidungen und Quellen

Ausstehend sind: Wahl A/B, bei B die eigenständige Repositoryerstellung und Zugangskonfiguration, Freigabe der lokalen Pushabsicherung und später gesondert der ersten privaten V4-Übertragung. Eine öffentliche Veröffentlichung bleibt unabhängig davon gesperrt. Der Vorschlag wird erst nach ausdrücklicher Nutzerentscheidung umgesetzt. Weder das Fehlen eines Remote-V4 noch der Dokumentationscommit ist eine Freigabe zum Push.

| ID | Quelle / URL | Zugriff und Aussage |
| --- | --- | --- |
| G01 | [GitHub: About repositories](https://docs.github.com/en/repositories/creating-and-managing-repositories/about-repositories) | 13.10.2026; Repository-Sichtbarkeit und Branch als Teil eines Repositorys |
| G02 | [GitHub: Setting repository visibility](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility) | 13.10.2026; Folgen public→private, bestehende öffentliche Forks bleiben öffentlich |
| G03 | [GitHub: Forks](https://docs.github.com/en/pull-requests/reference/forks) | 13.10.2026; öffentliche Forks öffentlich, keine unabhängige private Fork-Sichtbarkeit |
| G04 | [Repository-Metadaten-API](https://api.github.com/repos/RoboProjekt/R3D-Planner) | 13.10.2026 über GitHub-Connector gelesen; visibility=public |
| G05 | [Branches-API](https://api.github.com/repos/RoboProjekt/R3D-Planner/branches?per_page=100) | 13.10.2026 über Connector gelesen; vier bekannte Branches, kein V4 |
| G06 | [Geplantes Development-Ziel, Get-Repo-API](https://api.github.com/repos/RoboProjekt/R3D-Planner-Development) | 13.10.2026, 404; Nichtexistenz vs fehlender Zugriff nicht abschließend unterscheidbar |
| G07 | [Git: git-config](https://git-scm.com/docs/git-config) | 13.10.2026; push.default, pushurl, remote.pushDefault, branch.pushRemote |
| G08 | [Git: git-remote](https://git-scm.com/docs/git-remote) | Befehlsvorlage anhand lokalem `git remote -h` und Git-Konfigurationsdokumentation; nicht gegen das Projekt ausgeführt |

## 13. AP02-Metadatenabnahme und neue Kartenerklärung

### 13.1 Paketmetadaten vor/nach V4-008

| Feld | r3d_planner nach AP02 | r3d_preprocessor nach AP02 | Vorbestand / Änderung |
| --- | --- | --- | --- |
| ROS-/Python-Eingangsname | r3d_planner | r3d_preprocessor | Unverändert, gültige lexikalische REP-144-Namen mit bestehendem r3d_-Präfix |
| Manifestformat / Buildtyp | 3 / ament_python | 3 / ament_python | Unverändert; keine CMake-Konvertierung oder neue Buildtool-/Dependencydeklaration |
| Manifestversion | 0.0.1 | 0.0.1 | Vorher jeweils 0.0.0; ausdrücklich auf bestehende Setupversion vereinheitlicht |
| Setupversion | 0.0.1 | 0.0.1 | War schon so; keine Herabstufung/4.0.0-Ableitung |
| Description | Identisch zu setup.py, siehe unten | Identisch zu setup.py, siehe unten | TODO-Manifeste und alte unterschiedliche Setup-Kurztexte ersetzt |
| Maintainer | bauya / baau1001@stud.hs-kl.de | bauya / baau1001@stud.hs-kl.de | Vorhanden/strukturell gültig/konsistent; unverändert, keine neue Kontaktadresse |
| Author | Bastian Aumer, keine Author-E-Mail | Bastian Aumer, keine Author-E-Mail | Bekannte Entwicklererklärung, optional ergänzt; kein Ersatz fremder Copyrights |
| License | Apache-2.0 | Apache-2.0 | Unverändert; Root-/Paket-/Sharetext-/SPDX-Konzept aus AP01 erhalten |
| Repository | https://github.com/RoboProjekt/R3D-Planner | https://github.com/RoboProjekt/R3D-Planner | XML type=repository; Python url/Home-page |
| Bugtracker | https://github.com/RoboProjekt/R3D-Planner/issues | https://github.com/RoboProjekt/R3D-Planner/issues | XML type=bugtracker; Python project_urls/Bug Tracker |
| Console-Scripts | fünf bestehende Ziele | zwei bestehende Ziele | Unverändert, Modulpfade/main-Funktionen vorhanden |
| Indexmarker / setup.cfg / Launches | Bestehender leerer Marker/Scriptinstallation/vier Launches | Bestehender leerer Marker/Scriptinstallation | Unverändert, keine Umstrukturierung |
| Dependencies | Vorhandene XML/Python-Kategorien exakt erhalten | Vorhandene XML/Python-Kategorien exakt erhalten | Noch nicht rosdep-validiert; AP03 folgt erst nach Freigabe |

Neue englische Beschreibungen (jeweils exakt XML=Setup):

- **r3d_planner:** Graph-based A* path planning on classified PCD traversability data with a ComputePathToPose action, RViz integration, local obstacle filtering and path following.
- **r3d_preprocessor:** Offline voxel-based analysis and classification of PCD point clouds for robot-specific clearance and traversability assessment, with classified point-cloud output.

Die Texte benennen bestehende PCD-/Graph-/Action-/RViz-/Filter-/Followerfunktionen und keine SLAM-/Live-Mapping-/universelle Nav2-/Sicherheits-/Hardware-/Releasegarantie. Das ist Metadatenstandardisierung, keine neu implementierte Funktion.

### 13.2 Rollen, Entwicklungsversion und Prüfgrenzen

Author, Maintainer und Copyrightinhaber sind getrennte Rollen. Bastian Aumer als Author folgt der dokumentierten Erklärung zur eigenen Software; sechs OSRF-Templates und externe Originalrechte bleiben getrennt. Der gültige bestehende Maintaineralias/Email wird mangels konkreter Notwendigkeit nicht durch eine neue Identität ersetzt. Parsergültigkeit bedeutet keine Mailzustellungs-/Kontaktbefugnisprüfung; vor öffentlichem Release ist organisatorische Pflegezuständigkeit zu bestätigen.

0.0.1 ist eine vorläufige gemeinsame Entwicklungsversion, keine öffentliche Releaseversion/API-/ABI-Stabilitätszusage. Branch V4 ist keine SemVer-4.0.0-Nummer. Changelog-/Versions-/Releasepolitik gehört AP10; dafür wurden keine Tags, Releases, Repositorys oder PRs angelegt.

Die Eingabenamen in ROS/XML/setup.py und die Importmodule bleiben exakt r3d_planner/r3d_preprocessor. Erzeugte Python-Wheelmetadaten führen normierte Distributionnamen r3d-planner/r3d-preprocessor; dies entspricht der PyPA-Namensnormalisierung und ist kein ROS-Paketrename [M04]. Versionen und übrige Felder wurden im echten Wheel-METADATA geprüft. Keine fremden Bibliotheken oder PCDs im Wheel übernommen.

### 13.3 Nachweismatrix der 15 AP02-Abnahmekriterien

| Kriterium | Nachweis | Status / Grenze |
| --- | --- | --- |
| 1 Gültige XML-Manifeste | ElementTree und catkin_pkg 1.1.1 parse/validate, 0 warnings | VERIFIED |
| 2 Fachliche Beschreibungen | Gegen vorhandene Node-/Analyse-/Planungsfunktionen abgeglichen, XML=Setup | VERIFIED |
| 3 Repository-URLs | type=repository / Python url, exaktes Nutzerziel/HTTPS | VERIFIED strukturell; Live-Erreichbarkeit nicht neu geprüft |
| 4 Bugtracker-URLs | type=bugtracker / project_urls, exaktes Nutzerziel/HTTPS | VERIFIED strukturell; keine Issue-Erstellung/Serveränderung |
| 5 Maintainer-Metadaten | Vorhandene Namen/Emailstruktur konsistent, catkin Person.validate | VERIFIED strukturell; kein Zustellungs-/Befugnisnachweis |
| 6 Versionskonsistenz | Vier Quellen 0.0.1, Wheel-METADATA 0.0.1 | VERIFIED |
| 7 Apache-Metadaten | Zwei XML/Setup/Wheels, Originaltext in Wheel-/Sharebereichen, Hashschutz | VERIFIED technisch, Rechtegesamtgate separat |
| 8 ament_python | Export/get_build_type und unveränderte Python-Paketstruktur | VERIFIED |
| 9 ROS-Paketnamen | REP-144-lexikalische Regeln und Python-Eingangsname | VERIFIED; globale Kollisionen AP10 |
| 10 Dependencies unverändert | Exakte XML-Elementfolge/Attribute und Setup-Keyword-/ASTvergleich | VERIFIED, keine Auflösung/Installation |
| 11 Console-Scripts erhalten | Fünf/zwei Literaldefinitionen gleich, Zielmodule/main-Funktionen existent | VERIFIED, keine Nodebewegung |
| 12 ROS-Interfaces unverändert | Alle Runtime-/Launch-/Konfig-/Algorithmusdateien byte-/ASTgleich | VERIFIED statisch |
| 13 Geeignete statische Werkzeuge | System-Python 3.10/XML/catkin_pkg/URI-/Resource-/AST-/Hashchecks | VERIFIED, keine zusätzliche Installation |
| 14 Keine nachgewiesene AP02-Regression | 40 bestehende passende Configfälle bestanden, Wheels erzeugt/geprüft | VERIFIED im ausgeführten Umfang; drei native Fälle nicht neu ausgeführt |
| 15 Protokoll aktualisiert | V4-007..009, AP-/Version-/Release-/Entscheidungs-/Prüfmatrix | VERIFIED, historische Einträge unverändert |

AP02 VERIFIED ist ausdrücklich keine vollständige Dependency-/Clean-Runtime-/rosdep-/ROS-Index-/Bloom-/Buildfarm-/rechtliche Freigabe. Die Metadatenprüfung liefert keine neue unterstützte Distribution/Plattform.

### 13.4 Neue Nutzererklärung zu historischen Karten

**Erklärung des Projektentwicklers im aktuellen Auftrag, keine unabhängige rechtliche Prüfung:** Die früheren PCD-Beispielkarten wurden von Bastian Aumer selbst aufgenommen und verarbeitet. Er erklärt, dabei keine Datenschutzauflagen verletzt zu haben. Unabhängig davon sollen die Karten künftig auch aus den aktiven Beständen V1/V2/V3/main entfernt werden. V4 ist schon datenfrei. Diese weiteren Löschungen sind nicht Teil von AP02 und wurden nicht ausgeführt.

Die historische Git-Historie bleibt zunächst unverändert. Ein späterer normaler Löschcommit entfernt Daten nur aus dem neuen Tree, nicht aus älteren Gitobjekten/Forks/Kopien. Kein Rewrite/Force-Push/Objektpurge ist hier autorisiert oder vorgenommen. Das nun versionierte historische PDF darf den früheren Bestand weiterhin korrekt darstellen. Separate ausdrückliche Aufgabenfreigabe notwendig; Status anderer Branchbereinigung NOT STARTED. Selbstauskunft ersetzt keine vertragliche Nutzungs-/Verteilungs-/Datenschutzprüfung.

### 13.5 Quellen und nächster technischer Schritt

| ID | Primärquelle / lokaler Nachweis | Zugriff / Aussage |
| --- | --- | --- |
| M01 | [REP-149, offizielle Quelle](https://raw.githubusercontent.com/ros-infrastructure/rep/master/rep-0149.rst) | 14.10.2026; Manifestformat/Metadaten/URL-Typen/Author optional; ros.org-Endpunkt gesperrt |
| M02 | [REP-144, offizielle Quelle](https://raw.githubusercontent.com/ros-infrastructure/rep/master/rep-0144.rst) | 14.10.2026; lexikalische Namensregeln/Empfehlungen, keine globale Kollisionsabfrage |
| M03 | [ROS 2 Humble: Creating Your First ROS 2 Package](https://raw.githubusercontent.com/ros2/ros2_documentation/humble/source/Tutorials/Beginner-Client-Libraries/Creating-Your-First-ROS2-Package.rst) | 14.10.2026; Python-Paket-/Resource-/setup.cfg-Struktur und konsistente XML/Setup-Felder; docs.ros.org-Endpunkt gesperrt |
| M04 | [PyPA: Names and normalization](https://packaging.python.org/en/latest/specifications/name-normalization/) | 14.10.2026; kanonische Distributionnamen, Unterstrich/Bindestrich-Vergleich |
| M05 | Installiertes catkin_pkg.package/Person und packaging.utils unter /usr/lib/python3/dist-packages | 14.10.2026; tatsächlich ausgeführte Parser-/Emailformat-/Namensnormalisierung, catkin_pkg 1.1.1 |

**Nächster vorgeschlagener Schritt: AP03 – Dependency Management und rosdep**, nur nach neuer ausdrücklicher Freigabe. Scope: vollständige ROS-/Python-/Launch-/Build-/Runtime-Dependencies, Open3D/NetworkX/NumPy/SciPy/sensor_msgs_py/std_msgs/tf2_ros-Provider, plattformspezifische rosdep-Keys, reproduzierbare Installation und Beseitigung des bisherigen --skip-keys-Verfahrens. Hier keine Keys geändert, nichts installiert und AP03 nicht begonnen. Weitere Branchbereinigung ist eine eigene Aufgabe, kein automatischer AP03-Schritt. Kein Git-Push oder Veröffentlichung.


## 14. Aktuelle historische Datenbereinigung (V4-010)

Am 14. Oktober 2026 wurden die lokalen aktuellen V1/V2/V3/main-Trees wie in V4-010 inventarisiert bereinigt. Damit sind alle fünf lokalen Branch-Trees frei von PCD-Dateien. Die vorherigen V4-009-Zukunftsaussagen und früheren Rechts-/Branchbefunde bleiben historische Snapshots. Remote-Trees und Gitobjekte sind unverändert; das Projekt besitzt weiterhin keine vollständige rechtliche Releasefreigabe. AP01 technisch VERIFIED / Rechtsgesamtgate BLOCKED; AP02 VERIFIED. AP03 ist jetzt ausdrücklich freigegeben, wird nach dieser getrennten Sicherung/Dokumentation bearbeitet. AP04 nicht erweitert. Für AP03 erfolgten vorbereitende Import-/Key-/Umgebungsproben an separaten Kopien, noch keine Dependency-Mutation in V4. Automatische Freigabeablehnung, zusätzliche Chatbestätigung und nachfolgende erfolgreiche autorisierte Ausführung sind getrennt erfasst.


## 15. AP03 – Dependency Management und rosdep (V4-011)

### 15.1 Umgebung, Inventar und Abgrenzung

Primärziel und tatsächlicher Host: Ubuntu 22.04.5 Jammy amd64, ROS 2 Humble unter /opt/ros/humble, /usr/bin/python3 3.10.12; rosdep 0.27.0, catkin_pkg 1.1.1, setuptools 59.6.0, pytest 6.2.5. Shellinitialisierung enthält Conda /home/bauya/miniconda3 und fremde ROS-Workspaceoverlays (fast_lio/Unitree/LiDAR). Tests laufen mit PATH=/usr/bin:/bin, PYTHONNOUSERSITE=1, PYTHONDONTWRITEBYTECODE=1, ohne CONDA-/PYTHONPATH-/AMENT-/CMAKE-/COLCON-/ROS-/LD-Übernahme und anschließend ausschließlich /opt/ros/humble/setup.bash plus eigene temporäre Copy-Installation. Keine Conda-Umgebung geändert. System-Python 3.10 ist vom PATH-Standard Python3.14 getrennt. Dokumentierte Versionsnummern sind Beobachtungen, keine neuen Manifestpins.

128 AST-Importstellen in allen 26 vorhandenen Python-Dateien einschließlich vier Launches, beiden setup.py und allen Tests geprüft; folgende komplette Einzelstelleninventarliste erfasst auch lokale/Standardbibliotheksimporte. Keine dynamische Allpfad-/Algorithmuscoverage daraus behauptet. Laufzeitübergaben bleiben unverändert.

| Paketdatei:Zeile | Python-Import | Kategorie | Rolle | Zuordnung |
|---|---|---|---|---|
| `r3d_planner/launch/follower.launch.py:14` | `r3d_planner.launching` | Eigenes Modul | Runtime/Launch | kein externer Key |
| `r3d_planner/launch/map.launch.py:13` | `r3d_planner.launching` | Eigenes Modul | Runtime/Launch | kein externer Key |
| `r3d_planner/launch/planner.launch.py:13` | `r3d_planner.launching` | Eigenes Modul | Runtime/Launch | kein externer Key |
| `r3d_planner/launch/preprocessor.launch.py:13` | `r3d_planner.launching` | Eigenes Modul | Runtime/Launch | kein externer Key |
| `r3d_planner/r3d_planner/configuration.py:14` | `math` | Standardbibliothek | Runtime/Launch | kein externer Key |
| `r3d_planner/r3d_planner/configuration.py:15` | `os` | Standardbibliothek | Runtime/Launch | kein externer Key |
| `r3d_planner/r3d_planner/configuration.py:16` | `pathlib` | Standardbibliothek | Runtime/Launch | kein externer Key |
| `r3d_planner/r3d_planner/configuration.py:18` | `yaml` | Extern | Runtime/Launch | python3-yaml |
| `r3d_planner/r3d_planner/configuration.py:50` | `ament_index_python.packages` | Extern | Runtime/Launch | ament_index_python |
| `r3d_planner/r3d_planner/configuration.py:96` | `rclpy.validate_full_topic_name` | Extern | Runtime/Launch | rclpy |
| `r3d_planner/r3d_planner/launching.py:14` | `launch` | Extern | Runtime/Launch | launch |
| `r3d_planner/r3d_planner/launching.py:15` | `launch.actions` | Extern | Runtime/Launch | launch |
| `r3d_planner/r3d_planner/launching.py:16` | `launch.conditions` | Extern | Runtime/Launch | launch |
| `r3d_planner/r3d_planner/launching.py:17` | `launch_ros.actions` | Extern | Runtime/Launch | launch_ros |
| `r3d_planner/r3d_planner/launching.py:18` | `.configuration` | Eigenes Modul | Runtime/Launch | kein externer Key |
| `r3d_planner/r3d_planner/odometry.py:14` | `math` | Standardbibliothek | Runtime/Launch | kein externer Key |
| `r3d_planner/r3d_planner/odometry.py:15` | `geometry_msgs.msg` | Extern | Runtime/Launch | geometry_msgs |
| `r3d_planner/r3d_planner/odometry.py:16` | `nav_msgs.msg` | Extern | Runtime/Launch | nav_msgs |
| `r3d_planner/r3d_planner/odometry.py:17` | `rclpy.qos` | Extern | Runtime/Launch | rclpy |
| `r3d_planner/r3d_planner/odometry.py:18` | `rclpy.time` | Extern | Runtime/Launch | rclpy |
| `r3d_planner/r3d_planner/odometry.py:19` | `tf2_ros` | Extern | Runtime/Launch | tf2_ros_py |
| `r3d_planner/r3d_planner/r3d_local_filter.py:13` | `rclpy` | Extern | Runtime/Launch | rclpy |
| `r3d_planner/r3d_planner/r3d_local_filter.py:14` | `rclpy.node` | Extern | Runtime/Launch | rclpy |
| `r3d_planner/r3d_planner/r3d_local_filter.py:15` | `sensor_msgs.msg` | Extern | Runtime/Launch | sensor_msgs |
| `r3d_planner/r3d_planner/r3d_local_filter.py:16` | `geometry_msgs.msg` | Extern | Runtime/Launch | geometry_msgs |
| `r3d_planner/r3d_planner/r3d_local_filter.py:17` | `numpy` | Extern | Runtime/Launch | python3-numpy |
| `r3d_planner/r3d_planner/r3d_local_filter.py:18` | `math` | Standardbibliothek | Runtime/Launch | kein externer Key |
| `r3d_planner/r3d_planner/r3d_path_follower.py:13` | `rclpy` | Extern | Runtime/Launch | rclpy |
| `r3d_planner/r3d_planner/r3d_path_follower.py:14` | `rclpy.node` | Extern | Runtime/Launch | rclpy |
| `r3d_planner/r3d_planner/r3d_path_follower.py:15` | `geometry_msgs.msg` | Extern | Runtime/Launch | geometry_msgs |
| `r3d_planner/r3d_planner/r3d_path_follower.py:16` | `nav_msgs.msg` | Extern | Runtime/Launch | nav_msgs |
| `r3d_planner/r3d_planner/r3d_path_follower.py:17` | `sensor_msgs.msg` | Extern | Runtime/Launch | sensor_msgs |
| `r3d_planner/r3d_planner/r3d_path_follower.py:18` | `sensor_msgs_py.point_cloud2` | Extern | Runtime/Launch | sensor_msgs_py |
| `r3d_planner/r3d_planner/r3d_path_follower.py:19` | `math` | Standardbibliothek | Runtime/Launch | kein externer Key |
| `r3d_planner/r3d_planner/r3d_path_follower.py:20` | `.odometry` | Eigenes Modul | Runtime/Launch | kein externer Key |
| `r3d_planner/r3d_planner/r3d_path_test.py:13` | `rclpy` | Extern | Runtime/Launch | rclpy |
| `r3d_planner/r3d_planner/r3d_path_test.py:14` | `rclpy.node` | Extern | Runtime/Launch | rclpy |
| `r3d_planner/r3d_planner/r3d_path_test.py:15` | `geometry_msgs.msg` | Extern | Runtime/Launch | geometry_msgs |
| `r3d_planner/r3d_planner/r3d_path_test.py:16` | `tf2_ros` | Extern | Runtime/Launch | tf2_ros_py |
| `r3d_planner/r3d_planner/r3d_pcd_path.py:13` | `rclpy` | Extern | Runtime/Launch | rclpy |
| `r3d_planner/r3d_planner/r3d_pcd_path.py:14` | `rclpy.node` | Extern | Runtime/Launch | rclpy |
| `r3d_planner/r3d_planner/r3d_pcd_path.py:15` | `rclpy.action` | Extern | Runtime/Launch | rclpy |
| `r3d_planner/r3d_planner/r3d_pcd_path.py:16` | `nav2_msgs.action` | Extern | Runtime/Launch | nav2_msgs |
| `r3d_planner/r3d_planner/r3d_pcd_path.py:17` | `geometry_msgs.msg` | Extern | Runtime/Launch | geometry_msgs |
| `r3d_planner/r3d_planner/r3d_pcd_path.py:18` | `nav_msgs.msg` | Extern | Runtime/Launch | nav_msgs |
| `r3d_planner/r3d_planner/r3d_pcd_path.py:19` | `visualization_msgs.msg` | Extern | Runtime/Launch | visualization_msgs |
| `r3d_planner/r3d_planner/r3d_pcd_path.py:20` | `std_msgs.msg` | Extern | Runtime/Launch | std_msgs |
| `r3d_planner/r3d_planner/r3d_pcd_path.py:21` | `open3d` | Extern | Runtime/Launch | python3-open3d |
| `r3d_planner/r3d_planner/r3d_pcd_path.py:22` | `numpy` | Extern | Runtime/Launch | python3-numpy |
| `r3d_planner/r3d_planner/r3d_pcd_path.py:23` | `heapq` | Standardbibliothek | Runtime/Launch | kein externer Key |
| `r3d_planner/r3d_planner/r3d_pcd_path.py:24` | `scipy.spatial` | Extern | Runtime/Launch | python3-scipy |
| `r3d_planner/r3d_planner/r3d_pcd_path.py:25` | `os` | Standardbibliothek | Runtime/Launch | kein externer Key |
| `r3d_planner/r3d_planner/r3d_pcd_path.py:26` | `networkx` | Extern | Runtime/Launch | python3-networkx |
| `r3d_planner/r3d_planner/r3d_pcd_path.py:27` | `ament_index_python.packages` | Extern | Runtime/Launch | ament_index_python |
| `r3d_planner/r3d_planner/r3d_pcd_path.py:28` | `.odometry` | Eigenes Modul | Runtime/Launch | kein externer Key |
| `r3d_planner/r3d_planner/r3d_rviz_interface.py:13` | `rclpy` | Extern | Runtime/Launch | rclpy |
| `r3d_planner/r3d_planner/r3d_rviz_interface.py:14` | `rclpy.node` | Extern | Runtime/Launch | rclpy |
| `r3d_planner/r3d_planner/r3d_rviz_interface.py:15` | `geometry_msgs.msg` | Extern | Runtime/Launch | geometry_msgs |
| `r3d_planner/r3d_planner/r3d_rviz_interface.py:16` | `nav2_msgs.action` | Extern | Runtime/Launch | nav2_msgs |
| `r3d_planner/r3d_planner/r3d_rviz_interface.py:17` | `rclpy.action` | Extern | Runtime/Launch | rclpy |
| `r3d_planner/r3d_planner/r3d_rviz_interface.py:18` | `std_srvs.srv` | Extern | Runtime/Launch | std_srvs |
| `r3d_planner/r3d_planner/r3d_rviz_interface.py:19` | `tf2_ros` | Extern | Runtime/Launch | tf2_ros_py |
| `r3d_planner/r3d_planner/r3d_rviz_interface.py:20` | `math` | Standardbibliothek | Runtime/Launch | kein externer Key |
| `r3d_planner/setup.py:13` | `setuptools` | Extern | Build/Packaging | python3-setuptools |
| `r3d_planner/setup.py:14` | `os` | Standardbibliothek | Build/Packaging | kein externer Key |
| `r3d_planner/setup.py:15` | `glob` | Standardbibliothek | Build/Packaging | kein externer Key |
| `r3d_planner/test/test_configuration.py:14` | `copy` | Standardbibliothek | Test | kein externer Key |
| `r3d_planner/test/test_configuration.py:15` | `pathlib` | Standardbibliothek | Test | kein externer Key |
| `r3d_planner/test/test_configuration.py:16` | `unittest.mock` | Standardbibliothek | Test | kein externer Key |
| `r3d_planner/test/test_configuration.py:18` | `pytest` | Extern | Test | python3-pytest |
| `r3d_planner/test/test_configuration.py:19` | `yaml` | Extern | Test | python3-yaml |
| `r3d_planner/test/test_configuration.py:21` | `r3d_planner.configuration` | Eigenes Modul | Test | kein externer Key |
| `r3d_planner/test/test_configuration.py:96` | `launch` | Extern | Test | launch |
| `r3d_planner/test/test_configuration.py:97` | `r3d_planner.launching` | Eigenes Modul | Test | kein externer Key |
| `r3d_planner/test/test_configuration.py:112` | `rclpy` | Extern | Test | rclpy |
| `r3d_planner/test/test_configuration.py:113` | `rclpy.parameter` | Extern | Test | rclpy |
| `r3d_planner/test/test_configuration.py:114` | `geometry_msgs.msg` | Extern | Test | geometry_msgs |
| `r3d_planner/test/test_configuration.py:115` | `nav_msgs.msg` | Extern | Test | nav_msgs |
| `r3d_planner/test/test_configuration.py:116` | `nav2_msgs.action` | Extern | Test | nav2_msgs |
| `r3d_planner/test/test_configuration.py:117` | `r3d_planner.r3d_pcd_path` | Eigenes Modul | Test | kein externer Key |
| `r3d_planner/test/test_configuration.py:118` | `r3d_preprocessor.r3d_pcd_analyser` | Eigenes Modul | Test | r3d_preprocessor |
| `r3d_planner/test/test_configuration.py:205` | `r3d_planner.configuration` | Eigenes Modul | Test | kein externer Key |
| `r3d_planner/test/test_configuration.py:211` | `r3d_planner.configuration` | Eigenes Modul | Test | kein externer Key |
| `r3d_planner/test/test_configuration.py:212` | `ament_index_python` | Extern | Test | ament_index_python |
| `r3d_planner/test/test_configuration.py:240` | `subprocess` | Standardbibliothek | Test | kein externer Key |
| `r3d_planner/test/test_configuration.py:255` | `os` | Standardbibliothek | Test | kein externer Key |
| `r3d_planner/test/test_configuration.py:256` | `signal` | Standardbibliothek | Test | kein externer Key |
| `r3d_planner/test/test_configuration.py:257` | `subprocess` | Standardbibliothek | Test | kein externer Key |
| `r3d_planner/test/test_configuration.py:258` | `time` | Standardbibliothek | Test | kein externer Key |
| `r3d_planner/test/test_configuration.py:259` | `rclpy` | Extern | Test | rclpy |
| `r3d_planner/test/test_configuration.py:260` | `rclpy.node` | Extern | Test | rclpy |
| `r3d_planner/test/test_configuration.py:368` | `os` | Standardbibliothek | Test | kein externer Key |
| `r3d_planner/test/test_configuration.py:155` | `time` | Standardbibliothek | Test | kein externer Key |
| `r3d_planner/test/test_copyright.py:15` | `ament_copyright.main` | Extern | Test | ament_copyright |
| `r3d_planner/test/test_copyright.py:16` | `pytest` | Extern | Test | python3-pytest |
| `r3d_planner/test/test_flake8.py:15` | `ament_flake8.main` | Extern | Test | ament_flake8 |
| `r3d_planner/test/test_flake8.py:16` | `pytest` | Extern | Test | python3-pytest |
| `r3d_planner/test/test_pep257.py:15` | `ament_pep257.main` | Extern | Test | ament_pep257 |
| `r3d_planner/test/test_pep257.py:16` | `pytest` | Extern | Test | python3-pytest |
| `r3d_preprocessor/r3d_preprocessor/r3d_pcd_analyser.py:13` | `rclpy` | Extern | Runtime/Launch | rclpy |
| `r3d_preprocessor/r3d_preprocessor/r3d_pcd_analyser.py:14` | `rclpy.node` | Extern | Runtime/Launch | rclpy |
| `r3d_preprocessor/r3d_preprocessor/r3d_pcd_analyser.py:15` | `open3d` | Extern | Runtime/Launch | python3-open3d |
| `r3d_preprocessor/r3d_preprocessor/r3d_pcd_analyser.py:16` | `numpy` | Extern | Runtime/Launch | python3-numpy |
| `r3d_preprocessor/r3d_preprocessor/r3d_pcd_analyser.py:17` | `os` | Standardbibliothek | Runtime/Launch | kein externer Key |
| `r3d_preprocessor/r3d_preprocessor/r3d_pcd_analyser.py:18` | `traceback` | Standardbibliothek | Runtime/Launch | kein externer Key |
| `r3d_preprocessor/r3d_preprocessor/r3d_pcd_publisher.py:13` | `rclpy` | Extern | Runtime/Launch | rclpy |
| `r3d_preprocessor/r3d_preprocessor/r3d_pcd_publisher.py:14` | `rclpy.node` | Extern | Runtime/Launch | rclpy |
| `r3d_preprocessor/r3d_preprocessor/r3d_pcd_publisher.py:15` | `sensor_msgs.msg` | Extern | Runtime/Launch | sensor_msgs |
| `r3d_preprocessor/r3d_preprocessor/r3d_pcd_publisher.py:16` | `rclpy.qos` | Extern | Runtime/Launch | rclpy |
| `r3d_preprocessor/r3d_preprocessor/r3d_pcd_publisher.py:17` | `open3d` | Extern | Runtime/Launch | python3-open3d |
| `r3d_preprocessor/r3d_preprocessor/r3d_pcd_publisher.py:18` | `numpy` | Extern | Runtime/Launch | python3-numpy |
| `r3d_preprocessor/r3d_preprocessor/r3d_pcd_publisher.py:19` | `os` | Standardbibliothek | Runtime/Launch | kein externer Key |
| `r3d_preprocessor/r3d_preprocessor/r3d_pcd_voxel_publisher.py:13` | `rclpy` | Extern | Runtime/Launch | rclpy |
| `r3d_preprocessor/r3d_preprocessor/r3d_pcd_voxel_publisher.py:14` | `rclpy.node` | Extern | Runtime/Launch | rclpy |
| `r3d_preprocessor/r3d_preprocessor/r3d_pcd_voxel_publisher.py:15` | `sensor_msgs.msg` | Extern | Runtime/Launch | sensor_msgs |
| `r3d_preprocessor/r3d_preprocessor/r3d_pcd_voxel_publisher.py:16` | `rclpy.qos` | Extern | Runtime/Launch | rclpy |
| `r3d_preprocessor/r3d_preprocessor/r3d_pcd_voxel_publisher.py:17` | `open3d` | Extern | Runtime/Launch | python3-open3d |
| `r3d_preprocessor/r3d_preprocessor/r3d_pcd_voxel_publisher.py:18` | `numpy` | Extern | Runtime/Launch | python3-numpy |
| `r3d_preprocessor/r3d_preprocessor/r3d_pcd_voxel_publisher.py:19` | `os` | Standardbibliothek | Runtime/Launch | kein externer Key |
| `r3d_preprocessor/r3d_preprocessor/r3d_pcd_voxel_publisher.py:20` | `struct` | Standardbibliothek | Runtime/Launch | kein externer Key |
| `r3d_preprocessor/setup.py:13` | `setuptools` | Extern | Build/Packaging | python3-setuptools |
| `r3d_preprocessor/setup.py:14` | `os` | Standardbibliothek | Build/Packaging | kein externer Key |
| `r3d_preprocessor/test/test_copyright.py:15` | `ament_copyright.main` | Extern | Test | ament_copyright |
| `r3d_preprocessor/test/test_copyright.py:16` | `pytest` | Extern | Test | python3-pytest |
| `r3d_preprocessor/test/test_flake8.py:15` | `ament_flake8.main` | Extern | Test | ament_flake8 |
| `r3d_preprocessor/test/test_flake8.py:16` | `pytest` | Extern | Test | python3-pytest |
| `r3d_preprocessor/test/test_pep257.py:15` | `ament_pep257.main` | Extern | Test | ament_pep257 |
| `r3d_preprocessor/test/test_pep257.py:16` | `pytest` | Extern | Test | python3-pytest |

Die Tabelle zählt AST-Importstellen, nicht 128 verschiedene Dependencies. Lokale relative Module, math/os/pathlib/copy/unittest/subprocess/signal/time/heapq/traceback/struct/glob sind Standardbibliothek bzw. eigene Module. Zusätzlich benutzen test_configuration.py:247/283/301/315 die ROS-CLI via subprocess: ros2 launch bzw. ros2 param dump; Provider ros2cli/ros2launch/ros2param als test_depend. Die eigenen Planner-Testimporte benötigen den Preprocessor, der bereits als exec_depend tatsächlich über Launch/Sharezugriff benötigt wird. Kein zirkulärer Preprocessor→Planner-Vertrag.

### 15.2 Dependencyübersicht und bisheriger Vertrag

| Dependency / Key | Verwendung / Import / Zweck | Build/Runtime/Test | Bisher | Neuer Vertrag / Nachweis |
|---|---|---|---|---|
| `ament_copyright` | beide test_copyright.py:15, vorhandene Skips | Test | planner: test_depend; preprocessor: test_depend | r3d_planner: test_depend; r3d_preprocessor: test_depend; Humble/Jammy resolve VERIFIED |
| `ament_flake8` | beide test_flake8.py:15 | Test | planner: test_depend; preprocessor: test_depend | r3d_planner: test_depend; r3d_preprocessor: test_depend; Humble/Jammy resolve VERIFIED |
| `ament_index_python` | configuration.py:50 und r3d_pcd_path.py:27 Share lookup | Runtime/Launch | planner: exec_depend; preprocessor: fehlte | r3d_planner: exec_depend; Humble/Jammy resolve VERIFIED |
| `ament_pep257` | beide test_pep257.py:15 | Test | planner: test_depend; preprocessor: test_depend | r3d_planner: test_depend; r3d_preprocessor: test_depend; Humble/Jammy resolve VERIFIED |
| `geometry_msgs` | Posen/Punkte/Twist/TF | Runtime/Launch | planner: depend; preprocessor: fehlte | r3d_planner: exec_depend; Humble/Jammy resolve VERIFIED |
| `launch` | launching.py:14-16 und Testdescription | Runtime/Launch | planner: exec_depend; preprocessor: fehlte | r3d_planner: exec_depend; Humble/Jammy resolve VERIFIED |
| `launch_ros` | launching.py:17 Node | Runtime/Launch | planner: exec_depend; preprocessor: fehlte | r3d_planner: exec_depend; Humble/Jammy resolve VERIFIED |
| `nav2_msgs` | Planner/RViz ComputePathToPose; kein Nav2-Bringup | Runtime/Launch | planner: depend; preprocessor: fehlte | r3d_planner: exec_depend; Humble/Jammy resolve VERIFIED |
| `nav_msgs` | Path/Odometry | Runtime/Launch | planner: depend; preprocessor: fehlte | r3d_planner: exec_depend; Humble/Jammy resolve VERIFIED |
| `python3-networkx` | r3d_pcd_path.py:26 Graph | Runtime/Launch | planner: fehlte; preprocessor: fehlte | r3d_planner: exec_depend; Humble/Jammy resolve VERIFIED |
| `python3-numpy` | Punktwolken/Voxels/Geometrie, beide | Runtime/Launch | planner: depend; preprocessor: depend | r3d_planner: exec_depend; r3d_preprocessor: exec_depend; Humble/Jammy resolve VERIFIED |
| `python3-open3d` | r3d_pcd_path.py:21, drei Preprocessormodule PCD I/O/Voxel | Runtime/Launch | planner: fehlte; preprocessor: fehlte | r3d_planner: exec_depend; r3d_preprocessor: exec_depend; Humble/Jammy resolve VERIFIED |
| `python3-pytest` | alle Tests / vorhandenes tests_require | Test | planner: test_depend; preprocessor: test_depend | r3d_planner: test_depend; r3d_preprocessor: test_depend; Humble/Jammy resolve VERIFIED |
| `python3-scipy` | r3d_pcd_path.py:24 KDTree | Runtime/Launch | planner: depend; preprocessor: fehlte | r3d_planner: exec_depend; Humble/Jammy resolve VERIFIED |
| `python3-setuptools` | beide setup.py:13, vorhandenes install_requires | Buildtool und Runtime | planner: fehlte; preprocessor: fehlte | r3d_planner: buildtool_depend,exec_depend; r3d_preprocessor: buildtool_depend,exec_depend; Humble/Jammy resolve VERIFIED |
| `python3-yaml` | configuration.py:18, test_configuration.py:19 YAML | Runtime/Launch | planner: exec_depend; preprocessor: fehlte | r3d_planner: exec_depend; Humble/Jammy resolve VERIFIED |
| `rclpy` | Nodes/Actions/QoS/Time/Topicvalidierung beider Pakete | Runtime/Launch | planner: depend; preprocessor: depend | r3d_planner: exec_depend; r3d_preprocessor: exec_depend; Humble/Jammy resolve VERIFIED |
| `ros2cli` | subprocess ros2 Kommando in test_configuration.py | Test | planner: fehlte; preprocessor: fehlte | r3d_planner: test_depend; Humble/Jammy resolve VERIFIED |
| `ros2launch` | subprocess ros2 launch, test_configuration.py:247/283 | Test | planner: fehlte; preprocessor: fehlte | r3d_planner: test_depend; Humble/Jammy resolve VERIFIED |
| `ros2param` | subprocess ros2 param dump, test_configuration.py:301/315 | Test | planner: fehlte; preprocessor: fehlte | r3d_planner: test_depend; Humble/Jammy resolve VERIFIED |
| `sensor_msgs` | PointCloud2/LaserScan beider Pakete | Runtime/Launch | planner: depend; preprocessor: depend | r3d_planner: exec_depend; r3d_preprocessor: exec_depend; Humble/Jammy resolve VERIFIED |
| `sensor_msgs_py` | r3d_path_follower.py:18 read_points | Runtime/Launch | planner: fehlte; preprocessor: fehlte | r3d_planner: exec_depend; Humble/Jammy resolve VERIFIED |
| `std_msgs` | r3d_pcd_path.py:20 ColorRGBA | Runtime/Launch | planner: fehlte; preprocessor: fehlte | r3d_planner: exec_depend; Humble/Jammy resolve VERIFIED |
| `std_srvs` | r3d_rviz_interface.py:18 Trigger | Runtime/Launch | planner: depend; preprocessor: fehlte | r3d_planner: exec_depend; Humble/Jammy resolve VERIFIED |
| `tf2_ros_py` | odometry.py:19 / TF-Helper/RViz; Import tf2_ros | Runtime/Launch | planner: exec_depend; preprocessor: fehlte | r3d_planner: exec_depend; Humble/Jammy resolve VERIFIED |
| `visualization_msgs` | r3d_pcd_path.py:19 Marker | Runtime/Launch | planner: depend; preprocessor: fehlte | r3d_planner: exec_depend; Humble/Jammy resolve VERIFIED |
| r3d_preprocessor (eigenes Paket) | launching.py:25/31 Node package, r3d_pcd_path.py Share, Testimport | Runtime und Tests Planner | bereits exec_depend Planner | erhalten; beide Pakete im selben Workspace, ignore-src, kein externer System-Key erforderlich |
| ament_python | package.xml export build_type / colcon ROS-Python-Erkennung | Buildtyp | bereits exportiert, kein Buildtooltag | unverändert; kein gültiger rosdep-Key, nicht als Dependency erfunden |
| Standardbibliothek/eigene relative Module | vollständige AST-Tabelle oben | Runtime/Build/Test je Datei | implizit System-Python/eigenes Modul | keine zusätzlichen package.xml-Systemkeys |
| colcon / rosdep | Workspace-Orchestrierung/Resolver, keine Sourceimporte | Workspace-Werkzeuge | Apt-Anleitung vorhanden | außerhalb Paket-Runtime, Installanleitung behält python3-colcon-common-extensions/python3-rosdep |
| RViz / TF-CLI / Nav2-Bringup / Sensorfrontends | externe Consumer/Publisher oder optionale Integration | optional/externe Nodes | Deploymentanleitung | keine pauschalen Pflichtdependencies; nav2_msgs/sensor_msgs/nav_msgs sind die tatsächlich benötigten Schnittstellen |
| Hesai / Unitree / LiDAR-odom / externe SLAM-Repositories | PointCloud2/Odometry/TF/cmd_vel-Vertrag | Deployment/Hardware | separat dokumentiert | keine vendorten Quellen/Git-/Hardware-SDK-Abhängigkeit in beiden Paketen ergänzt |

### 15.3 Manifest- und Setuptoolsentscheidung

Alle Sourceimporte der reinen Python-Pakete erfolgen zur Runtime oder zu Tests; keine eigenen Header/Compiler-/Buildexportabnehmer. Alte depend-Tags durch exec_depend ersetzt, ohne Runtimevertrag zu verlieren. Python3-setuptools ist beide Male Buildtool für setup.py/colcon und wegen vorhandenem install_requires zusätzlich Runtime. Das ist zwei Kategorien mit Zweck, kein doppelter Tag. Kein ament_cmake-Paket/CMake-Konvertierung. Beide XMLs format 3/0.0.1/Apache-2.0/Beschreibungen/Maintainer/Autor/URLs/export ament_python exakt erhalten. catkin_pkg-Parser/Package.validate: jeweils Exit 0, Warnungen 0; kein separat ausgeführter XSD-Schemavalidator behauptet.

Humble-Generator lokal /opt/ros/humble/lib/python3.10/site-packages/ros2pkg/verb/create.py:131-162 bestätigt leere pauschale Python-buildtool-Liste; tf2_ros_py-Manifest unter /opt/ros/humble/share/tf2_ros_py/package.xml sowie offizieller Humble-Quellstand bestätigen Python-Provider. Das entfernte tf2_ros ist ein anderer ROS-Packagevertrag, kein „TF2 fehlte vollständig“-Befund. Statisches CLI-Tool ist optional, Python-TF2 zur Laufzeit notwendig.

Beide setup.py und setup.cfg vollständig bytegleich: packages, data_files mit LICENSE/Manifest/Marker, Planner-YAML/Robot-/Launchressourcen, install_requires=['setuptools'], tests_require=['pytest'], sieben Console-Scripts. ROS-Libraries/Science-Pakete werden durch package.xml/rosdep bereitgestellt; keine pip-Runtimevollständigkeit behauptet und kein zusätzlicher pip-Zwang. Keine tatsächlichen neuen pip-Abhängigkeiten, keine Versionspins ohne Bedarf. Metadaten-Vergleich ignoriert nur Dependency-Elemente: alle übrigen XML-Elemente identisch; alle 26 Python-Dateien syntaktisch gültig und bytegleich zum AP02-Stand.

### 15.4 Offizielle rosdep-Auflösung

Aktuelle Regeln am 14.10.2026 von offiziellen ros/rosdistro-Quellen abgerufen; keine lokale erfundene Regel. Beispielbefehl (für jeden der 26 verwendeten externen Keys ausgeführt):

```bash
/usr/bin/rosdep resolve python3-open3d --rosdistro humble --os=ubuntu:jammy \
  -c /tmp/r3d-v4-ap03/rosdep-current-copy
```

| Key | Installer / Ergebnis Humble/Jammy | Exit | Quelle |
|---|---|---:|---|
| `ament_copyright` | `#apt ros-humble-ament-copyright` | 0 | offizielles humble/distribution.yaml / where-defined Exit 0 |
| `ament_flake8` | `#apt ros-humble-ament-flake8` | 0 | offizielles humble/distribution.yaml / where-defined Exit 0 |
| `ament_index_python` | `#apt ros-humble-ament-index-python` | 0 | offizielles humble/distribution.yaml / where-defined Exit 0 |
| `ament_pep257` | `#apt ros-humble-ament-pep257` | 0 | offizielles humble/distribution.yaml / where-defined Exit 0 |
| `geometry_msgs` | `#apt ros-humble-geometry-msgs` | 0 | offizielles humble/distribution.yaml / where-defined Exit 0 |
| `launch` | `#apt ros-humble-launch` | 0 | offizielles humble/distribution.yaml / where-defined Exit 0 |
| `launch_ros` | `#apt ros-humble-launch-ros` | 0 | offizielles humble/distribution.yaml / where-defined Exit 0 |
| `nav2_msgs` | `#apt ros-humble-nav2-msgs` | 0 | offizielles humble/distribution.yaml / where-defined Exit 0 |
| `nav_msgs` | `#apt ros-humble-nav-msgs` | 0 | offizielles humble/distribution.yaml / where-defined Exit 0 |
| `python3-networkx` | `#apt python3-networkx` | 0 | offizielles python.yaml / where-defined Exit 0 |
| `python3-numpy` | `#apt python3-numpy` | 0 | offizielles python.yaml / where-defined Exit 0 |
| `python3-open3d` | `#apt python3-open3d` | 0 | offizielles python.yaml / where-defined Exit 0 |
| `python3-pytest` | `#apt python3-pytest` | 0 | offizielles python.yaml / where-defined Exit 0 |
| `python3-scipy` | `#apt python3-scipy` | 0 | offizielles python.yaml / where-defined Exit 0 |
| `python3-setuptools` | `#apt python3-setuptools` | 0 | offizielles python.yaml / where-defined Exit 0 |
| `python3-yaml` | `#apt python3-yaml` | 0 | offizielles python.yaml / where-defined Exit 0 |
| `rclpy` | `#apt ros-humble-rclpy` | 0 | offizielles humble/distribution.yaml / where-defined Exit 0 |
| `ros2cli` | `#apt ros-humble-ros2cli` | 0 | offizielles humble/distribution.yaml / where-defined Exit 0 |
| `ros2launch` | `#apt ros-humble-ros2launch` | 0 | offizielles humble/distribution.yaml / where-defined Exit 0 |
| `ros2param` | `#apt ros-humble-ros2param` | 0 | offizielles humble/distribution.yaml / where-defined Exit 0 |
| `sensor_msgs` | `#apt ros-humble-sensor-msgs` | 0 | offizielles humble/distribution.yaml / where-defined Exit 0 |
| `sensor_msgs_py` | `#apt ros-humble-sensor-msgs-py` | 0 | offizielles humble/distribution.yaml / where-defined Exit 0 |
| `std_msgs` | `#apt ros-humble-std-msgs` | 0 | offizielles humble/distribution.yaml / where-defined Exit 0 |
| `std_srvs` | `#apt ros-humble-std-srvs` | 0 | offizielles humble/distribution.yaml / where-defined Exit 0 |
| `tf2_ros_py` | `#apt ros-humble-tf2-ros-py` | 0 | offizielles humble/distribution.yaml / where-defined Exit 0 |
| `visualization_msgs` | `#apt ros-humble-visualization-msgs` | 0 | offizielles humble/distribution.yaml / where-defined Exit 0 |

Gegenproben numpy, scipy, ament_python: jeweils Exit 1 `ERROR: no rosdep rule for '<key>'`. Kein ungültiger Key in aktuellen Manifesten; `ament_python` ist gültiger Buildtyp und bleibt exportiert. tf2_ros zusätzlich Exit 0 ros-humble-tf2-ros als alter tatsächlicher Eintrag geprüft, aber nicht direkt benötigter Python-Provider.

**Cache-/Netzwerkbefund:** erster rosdep update -c /tmp/... in Sandbox Exit 1 wegen DNS `Temporary failure in name resolution`; keine Schlussfolgerung über ungültige Regeln. Genehmigte erneute Netzwerkausführung desselben rosdep update --rosdistro humble Exit 0. rosdep 0.27.0 wendet -c auf update nicht wie erwartet an: Ausgabe nennt /home/bauya/.ros/rosdep/sources.cache, dieser Benutzer-Cache wurde tatsächlich aktualisiert (vom Auftrag zulässig). Deshalb die frühere technische Absicht „nur separater Cache“ ausdrücklich nicht als Ergebnis behauptet. Anschließend aktualisierten offiziellen Cache nach /tmp/r3d-v4-ap03/rosdep-current-copy kopiert und sämtliche resolve/check/install-simulation/where-defined daran gebunden. Keine Änderung /etc-Quellen, Systempakete oder Remotes.

### 15.5 Vollständiger Satz, Installation und Hostcheck

Mit bereinigtem Humble-/System-Pythonprozess, cwd /home/bauya/Desktop/Gits/Github/R3D-Planner, tatsächlichen korrigierten V4-Manifesten:

```bash
/usr/bin/rosdep check --from-paths r3d_planner r3d_preprocessor \
  --ignore-src --rosdistro humble --os=ubuntu:jammy \
  -c /tmp/r3d-v4-ap03/rosdep-current-copy
/usr/bin/rosdep install --from-paths r3d_planner r3d_preprocessor \
  --ignore-src --rosdistro humble --os=ubuntu:jammy --simulate \
  -c /tmp/r3d-v4-ap03/rosdep-current-copy
```

check Exit 1: `System dependencies have not been satisfied: apt python3-networkx; apt python3-open3d`. install --simulate Exit 0: würde genau `sudo -H apt-get install python3-open3d` und `sudo -H apt-get install python3-networkx` aufrufen. Diese Installbefehle NICHT ausgeführt. Kein sudo-Systemeingriff, kein pip-/Conda-Eingriff. Derselbe Satz im separaten src-Workspace ergibt dieselben Ergebnisse. rosdep keys Exit 0 zeigt sieben Systemkeys, weil ignore-src bereits installierte ROS-Pakete bzw. lokale Pakete ausnimmt; das ist kein Nachweis, dass alle ROS-Schlüssel geprüft worden wären, deshalb sämtliche 26 externen resolve-Aufrufe separat. Tests/Buildtools nicht über -t wegselektiert, Standardumfang außer doc verwendet.

Tatsächliche vollständige Installation und anschließender erfolgreicher rosdep check sind NOT VERIFIED/BLOCKED für die aktuelle Ausführungsumgebung. Simulation/Importprobe/extrahierte Dateien verändern die dpkg-Paketpräsenz nicht. Ein Check-PASS würde wiederum keinen Clean-Build beweisen. Kein formaler Humble-Auflösungsblocker für Open3D/NetworkX: deren gültige Apt-Regeln existieren; hier fehlt der durchgeführte Installationsnachweis. Eine vollständig bestückte isolierte Zielumgebung oder gesonderte Freigabe für notwendige Systeminstallation kann diesen verbleibenden AP03-Nachweis ermöglichen.

### 15.6 Open3D und NumPy/SciPy: Quellen und tatsächliche Versionen

| Umgebung (System-Python 3.10.12) | NumPy | SciPy | NetworkX | Open3D | Ergebnis |
|---|---|---|---|---|---|
| bestehende User-Site, ursprüngliche Overlays | 1.26.4 ~/.local | 1.8.0 /usr/lib/python3/dist-packages | 3.4.2 ~/.local | 0.19.0 ~/.local | SciPy warnt >=1.17.3/<1.25.0 erwartet; Open3D CUDA-Warnung; keine neue pip-Installation |
| PYTHONNOUSERSITE=1, Systembibliotheken | 1.21.5 Apt | 1.8.0 Apt | fehlt | fehlt | keine NumPy/SciPy-Kompatibilitätswarnung; nicht vollständige Runtime |
| isolierter Humbleprozess + Jammy-Deb-Extraktion /tmp | 1.21.5 Apt | 1.8.0 Apt | 2.4 aus Apt-Deb | 0.14.1 aus Apt-Deb | alle Importe, Copy-Build und 43 Funktionstests erfolgreich; NetworkX np.int-Deprecations |

PyYAML 5.4.1 und setuptools 59.6.0/pytest 6.2.5 stammen aus System-Python. Lokales SciPy __init__.py:140-149 belegt erwarteten NumPybereich >=1.17.3 und <1.25.0, die User-Site-Importwarnung wird aufgezeichnet. Ursache für diese konkrete Warnung ist nachgewiesen: importiertes NumPy außerhalb des dort implementierten Bereichs, mit System-SciPy vermischt. Nicht behauptet: Conda selbst habe diese NumPydateien installiert, jede transitive Paketkombination sei kaputt oder ein Algorithmusfehler sei damit belegt. Die System-Python-Tests benötigen keinen Conda-Interpreter. Gegenmaßnahme konsistenter Apt-Satz, User-Site deaktivieren; bewusst keine globale „Reparatur“.

Offizieller Jammy-Kandidat python3-open3d 0.14.1+dfsg-7build3 (universe), Python-Abhängigkeiten >=3.10~ und <3.11 sowie NumPy>=1.20.0/ABI9. Die tatsächliche Importprobe und vorhandene PCD-Voxel-/Schreib-/Planungsregression bestätigen den geprüften Teilumfang auf Python3.10. Nicht die Open3D0.19-Userinstallation als rosdep-Nachweis verwenden. Apt-Simulation (nur zwei fehlende Pythonkeys) Exit 0: 17 neue Pakete, 0 Upgrades/0 Entfernungen. Exakte Versionen der geladenen Pakete:

| Apt-Paket | heruntergeladene Version | Prüfung |
|---|---|---|
| `fonts-roboto-unhinted` | `2:0~20170802-3` | apt-get download Exit 0, anschließend dpkg-deb --extract Exit 0 |
| `fonts-roboto` | `2:0~20170802-3` | apt-get download Exit 0, anschließend dpkg-deb --extract Exit 0 |
| `libastcenc1d` | `3.3+ds-1` | apt-get download Exit 0, anschließend dpkg-deb --extract Exit 0 |
| `libmeshoptimizer1d` | `0.17+dfsg-1` | apt-get download Exit 0, anschließend dpkg-deb --extract Exit 0 |
| `libspirv-cross-c-shared0` | `2021.01.15-5` | apt-get download Exit 0, anschließend dpkg-deb --extract Exit 0 |
| `libstb0` | `0.0~git20210910.af1a5bc+ds-1` | apt-get download Exit 0, anschließend dpkg-deb --extract Exit 0 |
| `libtinyexr1d` | `1.0.1+dfsg-3` | apt-get download Exit 0, anschließend dpkg-deb --extract Exit 0 |
| `libfilament1.9` | `1.9.25+dfsg2-4build1` | apt-get download Exit 0, anschließend dpkg-deb --extract Exit 0 |
| `libglfw3` | `3.3.6-1` | apt-get download Exit 0, anschließend dpkg-deb --extract Exit 0 |
| `libtmglib3` | `3.10.0-2ubuntu1` | apt-get download Exit 0, anschließend dpkg-deb --extract Exit 0 |
| `liblapacke` | `3.10.0-2ubuntu1` | apt-get download Exit 0, anschließend dpkg-deb --extract Exit 0 |
| `liblzf1` | `3.6-3` | apt-get download Exit 0, anschließend dpkg-deb --extract Exit 0 |
| `libtinyobjloader1` | `2.0.0~rc5+dfsg1-5build1` | apt-get download Exit 0, anschließend dpkg-deb --extract Exit 0 |
| `libopen3d0.14` | `0.14.1+dfsg-7build3` | apt-get download Exit 0, anschließend dpkg-deb --extract Exit 0 |
| `open3d-gui-data` | `0.14.1+dfsg-7build3` | apt-get download Exit 0, anschließend dpkg-deb --extract Exit 0 |
| `python3-networkx` | `2.4-4ubuntu2` | apt-get download Exit 0, anschließend dpkg-deb --extract Exit 0 |
| `python3-open3d` | `0.14.1+dfsg-7build3` | apt-get download Exit 0, anschließend dpkg-deb --extract Exit 0 |

Alle Archive ausschließlich /tmp/r3d-v4-ap03/jammy-debs; Entpacken nach jammy-root, keine Maintainerskripte/dpkg-Installation. PYTHONPATH nur um dortige usr/lib/python3/dist-packages, LD_LIBRARY_PATH um usr/lib/x86_64-linux-gnu erweitert. Bestehende Systembibliotheken/Humble werden benutzt; kein frischer Container/keine vollständig neu angelegte ROS-Installation. Diese temporäre Prüfstrategie ist keine reguläre Installationsanleitung und kein zu veröffentlichender Workaround. Verifikation ohne harte Versionspins; tatsächliche Apt-Installation/check weiterhin ausstehend.

### 15.7 Copy-colcon-Build und installierte Artefakte

Beide Paketquellen in eigenen src-Kopien unter /tmp/r3d-v4-ap03/workspace; keine Repo-/Worktree-Buildartefakte erzeugt. Vorhandene pyc/Cache/egg-info nur beim temporären Kopieren ausgelassen, im Repository unverändert. Alle Pythonbytes der Kopien entsprechen V4; korrigierte Manifeste ebenfalls. Eigene build/install/log-Pfade, keine --symlink-install. Befehle im bereinigten nativen Humble-/Deb-Prozess:

```bash
/usr/bin/colcon list --names-only --base-paths src
/usr/bin/colcon --log-base /tmp/r3d-v4-ap03/workspace/log-build build \
  --base-paths src --build-base build --install-base install \
  --event-handlers console_cohesion+
```

Beide Exit 0, Discovery r3d_planner/r3d_preprocessor. Erstbuild 30.7 s, nach Ergänzung der direkt belegten Test-CLI-Tags nochmal Copy-Build mit log-final-build Exit 0, 91 s. Bytekompilierung absichtlich deaktiviert, entsprechende setuptools-Warnungen kein Buildfehler. Kein apt-/rosdep-Install-/Clean-OS-Gate aus erfolgreichem Python-Paketieren ableiten.

**Artefaktprüfungen Exit 0:** beide installierten share/package.xml identisch zum finalen korrigierten Manifest; LICENSE jeweils Original-Apache-SHA256 cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30; ament-Marker vorhanden; vier Planner-Launchfiles/drei YAML-Dateien identisch; 5 Planner- und 2 Preprocessor-Console-Scripts echte installierte Dateien, Funktionen via importlib.metadata.EntryPoint.load callable aus installierter Copy-Pythonpfadstruktur, keine Source-/Symlinkmodule. Keine main-Funktion/Bewegungsnode durch Import gestartet. Version 0.0.1 und Requires-Dist setuptools, Entry-Points unverändert. Installtrees keine PCD-Datei. Temporäre Test-PCDs sind selbst erzeugte kleine vorhandene Regressionfixtures und gehören nicht zu Installartefakten oder Karteninventar.

Ein erster paralleler Artefaktvergleich während des abschließenden Builds schlug erwartbar wegen noch nicht neu kopiertem XML fehl; nach abgewartetem Build unverändert korrigierte Prüfung PASS. Kein Artefakt-PASS aus dem verfrühten Versuch. AP04-Default-Share-/Ausgabe-/Sourceunabhängigkeit nicht neu umgesetzt; externe R3D_CONFIG_DIR-Laufweise schon vorher vorhanden und beibehalten.

### 15.8 Vorhandene Tests, Failures und Skips

Keine neuen Tests wegen deklarativer Änderungen; vorhandene Tests unverändert. Initial vollständiger colcon-Lauf in Netzwerk-Sandbox: test Exit 0, test-result Exit 1; 49 Testcases mit 3 Failures/2 Skips, 44 Passes. Zwei Flake8-Fehler sowie test_real_launch_restart_and_all_components: PyYAML ReaderError #x001b (ANSI in ros2 param dump stdout). Keine Sourcekorrektur daraus abgeleitet. Erneut in freigegebener nativer lokaler DDS-Umgebung außerhalb Sandbox, ohne fremde Overlays/User-Site, RCUTILS_COLORIZED_OUTPUT=0, ROS_LOCALHOST_ONLY=1, Domain194 bzw.195, keine Hardwaretreiber/Follower gestartet. Diese Umweltänderungen zusammen beseitigen den Fehler im geprüften Lauf; isolierte alleinige Ursache nicht behaupten.

Gezielter vorhandener Funktionssatz:

```bash
/usr/bin/colcon --log-base /tmp/r3d-v4-ap03/workspace/log-functional test \
  --build-base build --install-base install \
  --test-result-base /tmp/r3d-v4-ap03/results-functional \
  --packages-select r3d_planner --event-handlers console_cohesion+ \
  --pytest-args -p no:cacheprovider -k test_configuration \
  --basetemp=/tmp/r3d-v4-ap03/pytest-functional
/usr/bin/colcon test-result --test-result-base /tmp/r3d-v4-ap03/results-functional --verbose
```

Beide Exit 0. Pytest 43 passed / 3 Lintertests deselected in 39.63s; test-result 43 Tests, 0 Errors/Failures/Skips. Umfasst YAML/Robotprofile/Validierung/Kartenpfade, echte ROS-Parameter/Odometry/TF, Preprocessor-Launch mit synthetischem PCD/Output, Planner-Neustarts/alle vier optionalen Komponentenkombinationen. Kein Roboter/keine echte Bewegung. Keine zusätzliche A*-Coverage-/Coverage-Prozentbehauptung.

Final vollständiger unveränderter Satz beider Pakete: gleicher colcon-test-Befehl ohne packages-select/-k, log-final-full, results-final-full, pytest-final-full. test Exit 0, test-result --verbose Exit 1. Pytest Planner 44 passed/1 failed/1 skipped, Preprocessor 1 passed/1 failed/1 skipped. Insgesamt 49 Tests: **45 PASS, 2 FAIL, 2 SKIP**, 0 errors. Failures beide vorhandene test_flake8.py, 166 Planner-/150 Preprocessor-Stilbefunde (unter anderem vorhandene Whitespace/langzeilige/ungenutzte Imports); Tests/Pythondateien durch AP03 bytegleich, keine verursachten Algorithmusänderungen. Beide pep257 PASS. Copyright-Templates behalten vorhandenen @pytest.mark.skip; kein ausgeführter Lizenzlinter daraus behauptet. NetworkX2.4/NumPy1.21.5 np.int-Deprecations und ament_flake8 SelectableGroups-/optparse-Warnungen; kein SciPy-NumPy-Inkompatibilitätswarning im finalen Funktionsprozess. Gesamtsuite nicht als bestanden werten, bloßer colcon-test-Prozess-Exit 0 ist kein Testresult-PASS. AP06/Qualitätsarbeit bleibt offen. Keine Hardwaretests/Commandadapter/Followermain-Aufrufe.

### 15.9 Multi-Distribution-Grenze

Offizielle Regel python3-open3d hat ubuntu:noble null. `rosdep resolve python3-open3d --rosdistro humble --os=ubuntu:noble -c <geprüfter Cache>` Exit 1 explizit „defined as not available“. Zusätzlich mit --rosdistro jazzy und --os=ubuntu:noble Exit 1 dieselbe allgemeine Systemregel (Humble-only ROS-Cache, ROS_DISTRO-Overridewarnung); kein vollständiger Jazzy-Katalogtest/Install-/Build-/Runtimeversuch. Befund allein aus offizieller OS-Regel belastbar, ROS-Verträge nicht portiert. Mögliche spätere AP09-Wege: offiziell geeignete Systembereitstellung prüfen, upstream rosdep/Ubuntu-Verfügbarkeit klären oder getrennt bewertete Vendor-/Source-/isolierte pip-Strategie. Keine stillschweigende Manifestumschaltung auf python3-open3d-pip, keine erfundenen Keys, kein pauschaler neuere-Distributionen-Support. AP09 NOT STARTED für Umsetzung, neuer Teilblocker DOCUMENTED/Regelbefund VERIFIED.

### 15.10 Abnahme, Status und Releasefolgen

| AP03-Kriterium | Ergebnis | Status |
|---|---|---|
| 1 Direkte Dependencies erfasst | 128 AST-Stellen plus Test-CLI/eigene Launchpakete; Standardbibliothek/Hardware getrennt | VERIFIED statisch |
| 2 Konsistente Manifeste | format3/0.0.1/Metadaten erhalten, richtige Kategorien, keine identischen Tagduplikate | VERIFIED |
| 3 Keys Humble/Jammy auflösbar | 26 externe resolve Exit0, lokales Paket ignore-src | VERIFIED |
| 4 Keine ungültigen Keys | numpy/scipy ersetzt, ament_python nicht als erfundener Key | VERIFIED |
| 5 Keine erforderliche Dependency ausgelassen | Source-/Launch-/Testsatz abgedeckt, Test-CLI ergänzt | VERIFIED statisch |
| 6 Buildtools | setuptools Bedarf belegt/deklariert, Buildtyp erhalten | VERIFIED |
| 7 Testdeps | bestehende 4 plus Planner ROS-CLI-Provider, beide Pakete getrennt gesammelt | VERIFIED Deklaration, kein Lint-PASS |
| 8 Setuptools widerspruchsfrei | unverändertes setuptools/pytest, Science/ROS via rosdep statt konkurrierender pip-Anforderungen | VERIFIED für ament_python-Verfahren |
| 9 Nachvollziehbare Installation | Keys/Simulation/korrekte Anleitung, aber keine vollständige echte rosdep-Installation/check | DOCUMENTED / NOT VERIFIED Gesamtgate |
| 10 Build/Tests bzw. Blocker abgegrenzt | Copy-Build/43 Runtimefälle PASS; Apt-Hostcheck und 2 Lintfehler/2 Skips explizit | VERIFIED Teilnachweise, BLOCKED Gesamtabschluss |

Bestehende strengere Projektabnahme in Abschnitt 3/4 verlangt tatsächlich installierten gesamten Satz plus rosdep check ohne Skip in isolierter dokumentierter Umgebung. Das bleibt ausstehend; daher **AP03 IN PROGRESS**, nicht pauschal VERIFIED. Keine weitere Systeminstallation zur künstlichen Statusaufwertung. Humble-Keys selbst vollständig auflösbar, bestehende Lintfehler AP06 und fehlende OS-/Installationsprüfung jeweils getrennt. AP01 technisch VERIFIED/rechtliches Gesamtgate BLOCKED, AP02 VERIFIED. AP04/AP06/AP08/AP10 IN PROGRESS; AP05/AP07 NOT STARTED; AP09 NOT STARTED mit Noble-Regelbefund. Index/Bloom/Buildfarm weiterhin NOT READY aus bekannten übrigen Gates, keine neue Serverfreigabe/Quality-Level-Angabe. Direkte ungültige/fehlende V4-Dependencies sind jetzt behoben, nicht länger als unveränderter aktueller Keyblocker ausgeben.

Noch offene Gates: vollständige rechtliche Befugnis/konkrete transitive/native Distributionspflichten/historische Datenobjekte; vollständige Installation/check/clean-native target; implizite Copy-Share-/Ausgabeportabilität; verbindliche Releaseversion/Changelogs-/Versionierung/Releasevorbereitung; unabhängige CI/weitere Tests nach Projektziel. Lint-/fehlende optionale Werkzeuge nicht als erfundene formale ROS-Indexpflichten umdeuten. Kein externer Robotik-/SLAM-Code in Paketdependencies erzwungen.

### 15.11 Git-Abschluss und Quellen

Vier historische Datencommits und V4-010-Dokumentationscommit getrennt von AP03. V4 weiterhin Nachfolger der unveränderten Baseline c65642fe56015556f696364a724cb5b976a27888. 13 alte Commits via union origin/V1/V2/V3/main erreichbar, Originalkartenblobs in alten Trees vorhanden. Alle fünf lokalen aktuellen Branches PCD-frei. Keine neuen Merge-Commits/Tags/Cherry-Picks/History-Rewrites. Sämtliche neu erzeugten historischen Worktrees entfernt, ursprünglicher V4-Worktree bleibt; keine Branchreferenz gelöscht. Remote-URLs/Remote-Trackingrefs unverändert, branch.V1/V2/V3 Trackingconfig neu durch erlaubte lokale Branchanlage; kein Push/GitHub-/Sichtbarkeitswechsel/Release. Historisches PDF unverändert SHA256 8c3603ec2dac85c5cabcca7ae7e85c8d8c709663fa02fabd09039274a2b35383. Entwicklungsprotokoll einzige fortlaufende Forschung, kein zusätzliches PDF.

Quellen/Stand 14.10.2026, tatsächliche resolve/where-defined/apt-policy/Debimport-/Testresultausgaben und lokale Toolimplementierungen unterscheiden:

| ID | Quelle | Verwendung / Grenze |
|---|---|---|
| D01 | [offizielle rosdep python.yaml](https://raw.githubusercontent.com/ros/rosdistro/master/rosdep/python.yaml) | System-Pythonkeys/Open3D-Noble-null; per-Key lokale Auflösung belegt |
| D02 | [offizieller Humble-Katalog](https://raw.githubusercontent.com/ros/rosdistro/master/humble/distribution.yaml) | ROS-Keys via aktueller Humble-Cache/where-defined |
| D03 | [Ubuntu Jammy python3-open3d](https://packages.ubuntu.com/jammy/python3-open3d) | Systempaket 0.14.1, Python3.10/NumPy-ABI, universe; tatsächliche Debimportprobe ergänzt |
| D04 | [Humble tf2_ros_py-Manifest](https://raw.githubusercontent.com/ros2/geometry2/humble/tf2_ros_py/package.xml) | Python-TF2-Provider, lokal installiertes entsprechendes Manifest gegengeprüft |
| D05 | [REP-149](https://raw.githubusercontent.com/ros-infrastructure/rep/master/rep-0149.rst) | Dependencykategorien/Runtime-/Buildtool-/Testvertrag, kein formales Verbot optionaler Verbesserungen |
| D06 | lokal ros2pkg/verb/create.py und colcon_ros/task/ament_python/build.py, colcon_core/task/python/test/pytest.py | Buildtyp/Setuptools/Testausführung/colcon Exit0 trotz TestFailure; lokale implementierte Werkzeugversionen |
| D07 | lokal SciPy __init__.py, apt-cache policy und importmodule.__file__/__version__ | tatsächliche NumPy-/SciPy-Mischung, erwarteter Range und isolierte Gegenprobe; keine unbekannte Installationsherkunft behauptet |

**Nächster vorgeschlagener Entwicklungsschritt:** AP04 – Build and Installation Portability nach ausdrücklicher neuer Freigabe. Share-Verzeichnisse/Copy-Konfiguration/ressourcenunabhängige Pfade/beschreibbare Ausgaben/Launches ohne Source und reproduzierbarer Clean-Build; offen gebliebenen AP03-Installationsnachweis dabei sauber getrennt nachholen. Kein automatischer Beginn, kein Push.


### 15.12 Commitreferenzen und abschließende Kontrollprüfung

| Ereignis | Branch / Commit | Nachgewiesener Umfang |
|---|---|---|
| historische Kartenbereinigung | V1 / `91ccb1a824e7d2d7163433f13594d6c07855b1c5` | eigener direkter Nachfolger `01348f3285a0e7582f70cc5f2ed3d1bf4b7f904b`; zwei Karten und vier minimale Folge-Dateien, kein Merge |
| historische Kartenbereinigung | V2 / `cc2f5bef269b3dcb1664bc52bba1d9c0be1bd1ca` | eigener direkter Nachfolger `3abd002e8cc9e7a26cacaf43a5c20b1822664f14`; zwei Karten und vier minimale Folge-Dateien, kein Merge |
| historische Kartenbereinigung | V3 / `a914f0e4cd793f1ed7f35501e09a7ca865914b67` | eigener direkter Nachfolger `3752404a08867e9e6f3725300b88e148d4d5be37`; zwei Karten und vier minimale Folge-Dateien, kein Merge |
| historische Kartenbereinigung | main / `51a08ed3da1bd43f06d89c6a84bbbd540aaf5861` | eigener direkter Nachfolger `c65642fe56015556f696364a724cb5b976a27888`; zwei Karten und vier minimale Folge-Dateien, kein Merge |
| V4-010 Dokumentation | V4 / `b8967211a2a6696f3bfebdd32e8793a315d6eb86` | nur zentrales Protokoll; unmittelbarer Vorgänger d2e05e6 |
| V4-011 AP03 Implementierung | V4 / `d177d3052d9554b3a2a9a160a7a79ddb52c94e6f` | genau acht Manifest-/Dokumentationsdateien; unmittelbarer Vorgänger `b8967211a2a6696f3bfebdd32e8793a315d6eb86` |

AP03-Implementierungscommit erfolgreich erstellt, danach Arbeitsbaum/Index sauber. Abschließender separater Protokollcommit dokumentiert diese entstandenen SHAs und Kontrollprüfung; seine eigene SHA ist aus `git log -1 --format=%H --grep='docs(deps): record AP03 verification and commit references'` auflösbar. Keine selbstreferenzielle SHA oder amend erforderlich.

Finale Kontrollprüfung mit /usr/bin/python3 -B: 26 unveränderte Pythondateien syntaktisch gültig, beide Manifeste/catkin_pkg/0 Warnungen und finaler Share-Manifestvergleich erfolgreich. Alle nicht freigegebenen ursprünglichen 62 Dateipfade bytegleich; kein neuer Repositorypfad/keine PCDs. Frühere zehn V4-Ereignisblöcke bytegleich erhalten, 15 Hauptabschnitte, Markdown-Tabellenspalten konsistent. Keine neue Skip-Anweisung in aktueller Installations-/Paketdokumentation; historische eingefrorene Aussagen im Protokoll/V2-Bericht nicht entfernt. Beide LICENSE-Originale/PDF unverändert. Fünf aktuelle lokale Branch-Trees PCD-frei, 13 historische Commits weiterhin existierend, alte Branch-Tips direkte Vorfahren ihrer vier Löschcommits. Ursprüngliche Remote-Trackingrefs und alle früheren Gitconfig-Abschnitte unverändert; ausschließlich die freigegebenen neuen branch.V1/V2/V3-Trackingabschnitte hinzugekommen. Nur ursprünglicher V4-Worktree vorhanden. `git diff --check`, Index-Whitelist, Commit-Parent-/Dateiumfang-/Vorfahrprüfungen erfolgreich. Abschließende `git status`, `git branch -avv`, `git log --all --graph --oneline --decorate` bestätigen dieselben Branchrelationen und sauberen lokalen Endzustand.

**Unverändert offene Abnahme:** AP03 IN PROGRESS für echten Installations-/Check-Nachweis, keine systemweite Installation. Copy-Build/Funktionstests und Key-Auflösung VERIFIED; Gesamtsuite bekannte zwei Lintfehler/zwei Skips. Kein Push/keine Veröffentlichung/Sichtbarkeitsänderung/History-Umschreibung/Hardwarebewegung. AP04 nur vorgeschlagen, nächste Nutzerfreigabe abwarten.


## 16. AP03/AP04/AP06 – Isolierte Humble-Abnahme und Portabilität

### 16.1 V4-012 – Tatsächliche Dependencies

Getesteter Eingang e204fee; 16 vorherige Textchunks vollständig gelesen, ältere Einträge erhalten. Neues Ziel ist die tatsächliche technische Installation/Portabilität/Qualität; Rechte-/API-/CI-/Multi-Distro-Arbeit bleibt separat.

```bash
docker pull ros:humble-ros-base
# gestartet mit gepinntem Digest, ro Quellmount, getrennten temporären tools/results:
source /opt/ros/humble/setup.bash
apt-get update
apt-get install -y --no-install-recommends python3-colcon-common-extensions python3-rosdep
rosdep update --rosdistro humble
rosdep install --from-paths /r3d-source/r3d_planner /r3d-source/r3d_preprocessor --ignore-src --rosdistro humble --os=ubuntu:jammy -y
rosdep check --from-paths /r3d-source/r3d_planner /r3d-source/r3d_preprocessor --ignore-src --rosdistro humble --os=ubuntu:jammy
# alle diese Apt-/rosdep-Befehle ausschließlich im Container, keine Hostinstallation
```

Relevante tatsächliche Ausgabe, finale Exitcodes 0:

```text
#All required rosdeps installed successfully
All system dependencies have been satisfied
BOOTSTRAP_INSTALL_AND_CHECK_PASS
```

Die erste erfolgreiche echte Installation ergänzt unter anderem python3-open3d, ros-humble-nav2-msgs, python3-scipy und python3-networkx samt Apt-Transitiven; übrige ROS/Testwerkzeuge bereits im Image bzw. vorherigem Container-Toolbootstrap. Zweiter idempotenter Ablauf ebenfalls erfolgreich, nicht als erneute frische Erstinstallation ausgegeben. Individuelle 26 Keyauflösungen separat bestanden. Vorhandene neun Host-PYC nie entfernt; temporäre Workspacekopien ohne Altcache. Hostdpkg/Interpreter/Remotes unverändert. Keine globale pip-/Conda-Mischung, keine zusätzliche Python-Umgebung als Benutzerpflicht.

| Bibliothek | Tatsächliche Container-Version | Importpfad |
|---|---|---|
| NumPy | 1.21.5 | /usr/lib/python3/dist-packages/numpy |
| SciPy | 1.8.0 | /usr/lib/python3/dist-packages/scipy |
| Open3D | 0.14.1 | /usr/lib/python3/dist-packages/open3d |
| NetworkX | 2.4 | /usr/lib/python3/dist-packages/networkx |
| PyYAML | 5.4.1 | /usr/lib/python3/dist-packages/yaml |
| benötigte ROS-/Launch-/TF2-/Messages | Humble-Apt-Pakete | /opt/ros/humble (Python3.10) |

Warnungen: NetworkX2.4 np.int-Deprecations, keine SciPy-Kompatibilitätswarnung. Erster Helper-nounset-/catkin-Metadatenfehler separat von echten rosdep-Exit0-Ergebnissen dokumentiert. Das Containerimage und Workspacewerkzeuge allein ersetzen keinen späteren Projektbuild/Funktionstest. Noble-Open3D bleibt AP09-Problem, keine Jazzy-Unterstützung.


### 16.2 V4-013 – Reguläre Package-Share-Konfiguration

Priorität unverändert: R3D_CONFIG_DIR → live Source/Symlink, wenn direkt aus Source importiert → normale installierte share/r3d_planner/config/planner_config.yaml. Robotpfad relativ zur tatsächlich gewählten YAML, Overridefehler führen nicht zu Defaultfallback. Ohne nutzerseitige PCDs meldet die erkannte installierte YAML weiterhin maps.<gewählter Pfad>: configure; keine Standardkarte. 40 bestehende passende Fälle PASS (Exit0), drei ROS-Ausführungsfälle später in voller Suite. Bestehender Ablehnungstest auf neuen Share-/Overridevertrag migriert, übrige Bestandsfälle erhalten. Anfangsfixture-Fehler explizit dokumentiert. Aktuelle README/INSTALL/CONFIGURATION/ARCHITECTURE/KNOWN_ISSUES aktualisiert, historische V3-/PDFberichte unverändert. Keine Version/License/Dependency/ROS-Namensänderung.


### 16.3 V4-014 – PCD-Ausgabevertrag

Neuer optionaler ROS-Parameter output_dir im Analyzer, zentrale Zuordnung preprocessing.output_dir. Ohne Feld/bei leerem String nutzerbezogenes XDG_DATA_HOME/r3d_preprocessor (nur absoluter XDG-Wert) oder ~/.local/share/r3d_preprocessor. Nichtleeres YAML output_dir relativ zur tatsächlichen YAML, absolute/~ möglich; Directory-file/Typ-/Whitespacefehler klar abweisen. Übriges striktes Schema unverändert, vorhandene gültige alte YAML ohne Feld akzeptiert. Die Filenamekonvention <stem>_analysed<pcd-suffix> bleibt erhalten; map_name muss den neuen Output manuell wählen.

Kein Outputbesitz aus Inputpfad abgeleitet: tempfile ausschließlich im gewählten Ziel, Open3D schreibt dort, os.link veröffentlicht atomar ohne replace. Existierende Datei oder (auch dangling) Symlink bleibt unverändert, Tempdatei nach Erfolg/Fehler entfernt. Fehlendes/ungültiges Input, unbeschreibbare Ausgabe, Open3D-false/Exception liefern sichtbare Fehlermeldung und Analyzer-main Exit1; Erfolg Exit0. Kein Package-Share als impliziter Writeort. Explizite Nutzerwahl kann natürlich ein beliebiges eigenes beschreibbares Verzeichnis bestimmen. Keine neuen Planungs-/Klassifikationsberechnungen.

Unprivilegierter echter I/O-Nachweis (kein root-Rechte-Pseudobeweis): 10 Outputfälle PASS/0 FAIL/0 SKIP, 40 bestehende Configfälle PASS/3 ROSfälle bewusst später; Voxel-/Floor-/Clearance-/Stairfunktion-ASTs identisch. Root würde den reinen DAC-Test skippen; finale Gesamtsuite wird deshalb als regulärer User ausgeführt, kein Skip-PASS. Die Dateioutput-Tests sind neue AP04-Regressionen, nicht nachträglich der Baseline zugerechnet. Lizenzentscheidung/SPDX-/Fremdnotices unverändert; neue eigene Helper-/Testdateien tragen passenden Apache-/SPDX-Hinweis.


### 16.4 V4-015 – Qualitätskorrekturen

Alle 22 betroffenen Pythonpfade wurden vor Anwendung in Containerkopien geprüft; Flake8-Grenze99/ROS-Lintregeln unverändert. Kein flake8-disable/noqa-Pauschalfix. AST-normierte Ausnahmen: local_filter import math, Preprocessor setup import os, alternativer Publisher import struct (unbenutzte Standardbibliothek); PathFollower tote except-e-Bindung; Analyzer konstantes fstring-Präfix; zwei Copyright-skipdecorators. Restliche ASTs unverändert, Stringinhalte/Parameterwerte/Rechnungen/ROS-Namen erhalten. Neue Daten-/Ausgabefunktionen werden nur formatiert, nicht algorithmisch umgebaut.

18 frühere eigene Pythondateien erhalten einen zusätzlichen traditionellen Apache-2.0-Header, ihre alten Copyright-/SPDX-Zeilen bleiben. Zwei neue eigene Outputdateien ordnen ihre unveränderten SPDX-Zeilen nach dem vollständigen Licenseblock an. Sechs OSRF-Lizenz-/Copyrightblöcke byteidentisch, nur der obsolete Skipcode der zwei Copyrighttests entfernt. Leere Pythonmarker bleiben leer; keine Attribution unbekannter YAML/TXT/PYC. Root-/Paket-LICENSE und Manifestversion0.0.1/Apache-2.0 erhalten. Echter ament_copyright-Test passt, keine selbstgeschriebene Ersatzprüfung.

Temporäre finale Lintresultate: Planner3PASS/43deselected, Preprocessor3PASS/10deselected, beide Exit0; keine SKIPs. Vorherige formatterbedingte 16/4 Restbefunde/two-license-unknowns transparent korrigiert. Verbleibende externe ament_flake8 SelectableGroups-/optparse-Warnungen ändern Teststatus nicht. Die vollständige Suite wurde anschließend unter V4-016 ohne Ausklammerung erfolgreich ausgeführt.


### 16.5 Konsolidierte Testnachweise und relevante Ausgaben

Datum 14. Oktober 2026. C1 = r3d-v4-humble-completion-20261014; C2 = r3d-v4-humble-sourcefree-20261014. Beide aus ros:humble-ros-base@sha256:860e53793ccf575e5369b5e9a19939de2bfcfb46a299954d06f54f2af54fed19, Ubuntu22.04.5/Python3.10.12/Humble. Imagesnapshot und Apt-/rosdep-Indexstand sind getrennt: Aptquellen wurden live aktualisiert, keine Lockfile- oder dauerhafte Bitreproduzierbarkeitszusage. Ein späterer Lauf muss seine Versionen erneut erfassen.

C1-Sourcebind readonly; Builds in getrennten Containerverzeichnissen. C2 hat nur fertigen Installbaum readonly unter /work/final2/install, zwei Testdateien readonly, zwei Manifestkopien readonly, temporäre Harnessscripts readonly und ein Ergebnisverzeichnis rw. Kein ursprünglicher Gitcheckout oder R3D-Quellbaum dort verfügbar. Kein privileged/host-network, keine sensitiven Mounts. FastDDS, ROS_LOCALHOST_ONLY=1, getrennte ROS_DOMAIN_ID201/203, PYTHONNOUSERSITE=1, unprivilegierter User1000. Nicht als allgemeine Prefix-Relokation oder jeder-OS-Installation ausgeben.

Commitcodes: A=7a476588ba3e50550074c14920b95d3658e45a03; B=c702da4ac241f3173d3732da3bdd1a754a04d949; C=370cf5f9246791c570600fffceab637c3c4b564b; D=bb578b36fc6ac72dddb043f35a474fe15c25da30; E=der diese Tabelle/test_installation.py enthaltende eindeutige Commit `test(install): add clean installation regression coverage`, Parent D. `git log --format='%H %s'` liefert seine SHA ohne selbstreferenziellen Committext. Früher dokumentierte IDs T01-T64 unverändert; folgende IDs sind neue Nachweise und keine Baselineleistungen.

| Test-ID | Arbeitspaket | Prüfung | Testumgebung | Befehl | Ergebnis | Status | Commit |
|---|---|---|---|---|---|---|---|
| T65 | AP03 | 26 externe Keys individuell | C1 Humble/Jammy | `rosdep resolve --rosdistro humble --os=ubuntu:jammy KEY` | 26 Exit0; kein skip | VERIFIED | A/V4-012 |
| T66 | AP03 | Reale Dependencyinstallation | C1 frischer Apt-Container | `rosdep install --from-paths /r3d-source/r3d_planner /r3d-source/r3d_preprocessor --ignore-src --rosdistro humble --os=ubuntu:jammy -y` | Exit0, tatsächlich installierte Apt-Pakete | VERIFIED | A/V4-012 |
| T67 | AP03 | Installierte Dependencies checken | C1 | `rosdep check --from-paths /r3d-source/r3d_planner /r3d-source/r3d_preprocessor --ignore-src --rosdistro humble --os=ubuntu:jammy` | Exit0: All system dependencies have been satisfied | VERIFIED | A/V4-012 |
| T68 | AP03 | Systemversionen/Imports/Pythonpfade | C1/C2 Python3.10.12 | `python3 -c "import numpy, scipy, open3d, networkx, yaml"; ROS-/Projekt-Importprüfungen` | Apt1.21.5/1.8.0/0.14.1/2.4/5.4.1; keine SciPy-Kompatibilitätswarnung | VERIFIED | A/E |
| T69 | AP04 | Share-/Override-/strikte Configregression | C1 temporäre Paketkopie | `python3 -m pytest -p no:cacheprovider --basetemp=/work/config-pytest-final test/test_configuration.py -k "not effective_ros_parameters_and_odometry and not preprocessor_real_launch and not real_launch_restart_and_all_components" -q` | 40PASS; drei Runtimefälle später in Vollsuite | VERIFIED | B/V4-013 |
| T70 | AP04/AP06 | Exklusiver readonly-Input/Output/Fehlpfad | C1 UID1000 | `python3 -m pytest -p no:cacheprovider --basetemp=/work/tests-user/output test/test_output.py -q` | 10PASS/0FAIL/0SKIP; echte Open3D-Rücklesung/Schreibrechte | VERIFIED | C/V4-014 |
| T71 | AP04 | Clean-Copy-Build1 | C1 /work/final2 UID1000 | `colcon --log-base log-build build --packages-select r3d_preprocessor r3d_planner --event-handlers console_cohesion+` | Exit0, zwei Pakete, ohne symlink/Altinstall | VERIFIED | E/V4-016 |
| T72 | AP06 | Vollsuite1 | C1 /work/final2 UID1000 | `colcon --log-base log-test test --packages-select r3d_preprocessor r3d_planner --event-handlers console_cohesion+; colcon test-result --verbose` | Beide Exit0; 86PASS/0FAIL/0ERROR/0SKIP | VERIFIED | D/E |
| T73 | AP04/AP06 | Clean-Copy-Build2/Vollsuite2 | C1 unabhängiger leerer /work/final3 UID1000 | `Identische build/test/test-result-Befehle im zweiten Workspace` | Alle Exit0; erneut86PASS/0FAIL/0ERROR/0SKIP | VERIFIED | E/V4-016 |
| T74 | AP04 | Ressourcen/Versions-/Lizenz-/Scriptinventar | C1 beide Copy-Workspaces | `test_installed_artifacts_and_entry_points; get_package_share_directory` | 2 Manifeste/2 LICENSE/2 Marker/7 Scripts/4 Launches/3 YAMLs/0PCD; 0.0.1 | VERIFIED | E/V4-016 |
| T75 | AP04 | Alle installierten Launchfiles | C1/C2 synthetischer Override | `ros2 launch r3d_planner LAUNCHFILE --show-args (vier Dateien)` | 4xExit0; nur Discovery/Generierung, Follower nicht gestartet | VERIFIED | E/V4-016 |
| T76 | AP03 | Reale Installation/check reproduziert | C2 neues Imagefilesystem, nur Manifestkopien | `rosdep install/check --from-paths /dependency-manifests --ignore-src --rosdistro humble --os=ubuntu:jammy (install zusätzlich -y)` | Beide Exit0, keine skip/simulate; Imports erfolgreich | VERIFIED | E/V4-016 |
| T77 | AP04/AP06 | Source-freie readonly-Installation | C2 ohne Source-/Workspace-Mount UID1000 | `python3 -m pytest -p no:cacheprovider --basetemp=/work/runtime-user/pytest --junitxml=/runtime-results/pytest.xml /runtime-tests -q` | Exit0; 37PASS/0FAIL/0SKIP; Sourcepfade fehlen, Module aus Install | VERIFIED | E/V4-016 |
| T78 | AP04 | Map-/Robot-/Output-/Overridepfade | C1/C2 Installedtests | `test_installation.py Konfigurations-/Pfadgruppen` | Standardshare/Override/relativ/absolut/~, Legacy-YAML, invalid types/missing override geprüft | VERIFIED | B/C/E |
| T79 | AP04 | Sieben installierte Nodes initialisieren | C1/C2 neuer subprocess | `test_installed_nodes_initialize_with_isolated_inputs` | 7 Konstruktoren/Destroy, synthetic inputs, Commandtopic isoliert; kein Control-loop | VERIFIED | E/V4-016 |
| T80 | AP04 | Installiertes Analyzer-Script funktional | C1/C2 readonly Inputs | `test_installation.py Analyzer-readonly/collision- und invalid-PCD-Fälle` | Success0; ungültige PCD/collision1; Input/Outputdaten erhalten | VERIFIED | C/E |
| T81 | AP04 | Wiederholte Ressourceninhalte vergleichen | C1 final2 vs final3 | `SHA256 plus exakter Vergleich installierter .py und nur Prefixnormalisierung package.sh` | 31/33 Sharebytes gleich; 2 generierte Prefixhooks normiert gleich; 20 Pythondateien gleich (18 Paketmodule/Launches plus2 generierte Helper) | VERIFIED (keine Bitreproduzierbarkeitsbehauptung) | E/V4-016 |
| T82 | AP01/AP02/AP06 | Geschützte Texte/AST/Metadaten | Repo plus Containerkopien | `Manifest-/LICENSE-/PDF-SHA; 6 OSRF-Blockvergleiche; AST-Normalvergleich; git diff --check` | Alle invarianten Checks; sechs Lints aktiv, keine Lizenz-/Versionsänderung | VERIFIED | D/E |
| T83 | AP06 | Unveränderter Eingang frisch reproduziert | C1 /work/baseline | `colcon test; colcon test-result --verbose` | 45PASS/2Flake8FAIL/2CopyrightSKIP; test-result1 (Ausgangspunkt) | FAILED (historischer Eingang) | A/V4-012 |
| T84 | AP06 | Neuer Node-Testhelper erster Vollversuch | C1 /work/final1 | `colcon test; colcon test-result --verbose` | 85PASS/1FAIL/0SKIP, result1; fehlender expliziter rclpy.node-Import im Test korrigiert | FAILED (danach T72/T73/T77 VERIFIED) | E/V4-016 |
| T85 | AP09/AP07 | Jazzy/andere Plattformen/CI/Coverage/Hardware | Nicht ausgeführt | `Keine entsprechenden Befehle/Hardwaretests` | Keine Freigabe/kein Nachweis; externe Warnungen bleiben | NOT VERIFIED | Kein Implementierungscommit |
| T86 | AP08/AP10 | Temporäre Container aufräumen | Dockerhost, nur codex.task=r3d-v4-completion | `docker stop und docker rm mit den zwei exakten eigenen Namen` | Exit0; keine eigenen Container übrig, keine Images gelöscht/Hostpakete verändert | VERIFIED | E/V4-016 |

Reproduzierbare tatsächliche Kommandos für beide leeren Copy-Workspaces (WORKSPACE jeweils /work/final2 oder /work/final3; keine Überlagerung eines alten R3D-Installbaums):

```bash
# als r3dtest UID1000 innerhalb C1, aus jeweils neu kopierten src/Paketen:
source /opt/ros/humble/setup.bash
cd /work/final2  # zweiter erfolgreicher Lauf: /work/final3
export PYTHONNOUSERSITE=1
colcon list --names-only
colcon --log-base log-build build --packages-select r3d_preprocessor r3d_planner --event-handlers console_cohesion+
source install/setup.bash
colcon --log-base log-test test --packages-select r3d_preprocessor r3d_planner --event-handlers console_cohesion+
colcon test-result --verbose
```

Relevante unveränderte Ausgabe der tatsächlichen Ergebnisse:

**final2:** list/build/test/test-result jeweils Exit0.

```text
r3d_planner
r3d_preprocessor
Finished <<< r3d_preprocessor [0.28s]
Finished <<< r3d_planner [0.28s]
Summary: 2 packages finished [0.63s]
======================== 13 passed, 2 warnings in 0.38s ========================
Finished <<< r3d_preprocessor [0.60s]
======================= 73 passed, 4 warnings in 40.47s ========================
Finished <<< r3d_planner [40.8s]
Summary: 2 packages finished [41.5s]
Summary: 86 tests, 0 errors, 0 failures, 0 skipped
```

**final3:** list/build/test/test-result jeweils Exit0.

```text
r3d_planner
r3d_preprocessor
Finished <<< r3d_preprocessor [0.29s]
Finished <<< r3d_planner [0.29s]
Summary: 2 packages finished [0.64s]
======================== 13 passed, 2 warnings in 0.40s ========================
Finished <<< r3d_preprocessor [0.62s]
======================= 73 passed, 4 warnings in 40.91s ========================
Finished <<< r3d_planner [41.3s]
Summary: 2 packages finished [42.0s]
Summary: 86 tests, 0 errors, 0 failures, 0 skipped
```

C2 führte eine separate echte rosdep install/check-Prüfung aus (nicht von C1-Dpkg übernommen):

```bash
# ausschließlich innerhalb C2 nach ROS/workspace-tool-Setup:
rosdep update --rosdistro humble
rosdep install --from-paths /dependency-manifests --ignore-src --rosdistro humble --os=ubuntu:jammy -y
rosdep check --from-paths /dependency-manifests --ignore-src --rosdistro humble --os=ubuntu:jammy
```

Relevante tatsächliche Ausgabe, finaler Bootstrap Exit0:

```text
#All required rosdeps installed successfully
All system dependencies have been satisfied
BOOTSTRAP_INSTALL_AND_CHECK_PASS
```

Source-freier Testaufruf als UID1000 nach Source von ROS und dem readonly-Installbaum:

```bash
source /opt/ros/humble/setup.bash
source /work/final2/install/setup.bash
export PYTHONNOUSERSITE=1 ROS_LOG_DIR=/work/runtime-user/ros-log
cd /work/runtime-user
python3 -m pytest -p no:cacheprovider --basetemp=/work/runtime-user/pytest --junitxml=/runtime-results/pytest.xml /runtime-tests -q
```

Relevante tatsächliche Ausgabe, Exit0:

```text
.....................................                                    [100%]
37 passed in 3.53s
```

Fehlversuche werden erhalten: Bootstrap-nounset-/Debian-Metadatendiagnosefehler (16.1); ursprüngliche 45PASS/2FAIL/2SKIP (T83); erste Formatierung mit Restbefunden (16.4); neuer Nodehelper-Importfehler 85PASS/1FAIL/0SKIP (T84). Aus diesen Fehlern wurden keine ungeprüften Produktionsbugs oder rosdep-Keyfehler abgeleitet. Zwei erfolgreiche Vollsuiten danach und Source-free-Lauf enthalten keine ausgeschlossenen Gruppen/Skips. colcon test Exit0 des ersten Fehlversuchs war ausdrücklich kein Gesamt-PASS.

Die vollständigen technischen Rohlogs/xUnit/Versions-/SHA-/Isolationsdaten wurden vor Cleanup unter /tmp/r3d-v4-completion gesichert; das ist temporärer Testoutput, kein neuer Forschungsbericht oder Langzeitarchiv. Dauerhafte relevante Kommandos/Ergebnisse/Grenzen stehen hier. Testcode wird in den Paketen versioniert. Die beiden selbst angelegten Container wurden nach Sicherung gestoppt/entfernt; ausschließlich das neu gezogene offizielle Image blieb im Cache, vorhandene Images unberührt. Kein Host-Apt/pip/Conda-/ROS-/Treiber-/Daemonkonfigurationseingriff.

### 16.6 Abnahme, bestehende Vorleistungen und offene Folgearbeit

| Arbeitspaket | Aktueller Status | Erfüllter Umfang / verbleibende Grenze |
|---|---|---|
| AP01 | technisch VERIFIED; rechtliches Gesamtgate BLOCKED | Gewählte Apache-2.0/Metadaten/Lizenzmitnahme erhalten; Verträge/historische Gitdaten/konkrete Bundlefreigabe separat |
| AP02 | VERIFIED | Zwei unveränderte Manifeste/Setupmetadaten, Namen/0.0.1/ament_python erhalten |
| AP03 | VERIFIED für Humble/Jammy | Direkte Deklarationen/26Keys, tatsächliches install/check, Imports und konsistente Apt-Versionen belegt; Host nicht repariert, andere Ziele offen |
| AP04 | VERIFIED für ursprünglichen beauftragten Umfang | Zwei Clean-Copy-Builds, Share/Override/Robot/Launch/Entry-Points, sourcefreier readonly-Installbaum und separate exklusive Ausgabe; keine beliebige Installprefix-Relokation |
| AP05 | NOT STARTED | Namespaces/Remapping/TF/PointCloud2/Quaternionverträge benötigen neuen Auftrag |
| AP06 | VERIFIED für bearbeiteten Umfang | 43 vorhandene Funktionen plus37 neue Regressionen und6 Lints, zweimal86PASS/0FAIL/0SKIP; Coverage/umfassende API-/Algorithmus-/Hardwaretests nicht belegt |
| AP07 | NOT STARTED | Kein CI-Lauf oder Pipeline implementiert; lokale Containerprüfung ist keine CI |
| AP08 | IN PROGRESS | Vorhandene Anleitungen/Protokoll bisV4-016 aktualisiert; Policies/weitere Wartungsdokumentation offen |
| AP09 | NOT STARTED | Humbleprüfung, keine Jazzy-/anderePlattform-Prüfung; Noble-Open3D-Hürde bleibt |
| AP10 | IN PROGRESS | Technische Installationsgates geschlossen; Index/Bloom/Buildfarm weiterhin NOT READY |

Bereits vor diesem Auftrag vorhanden und nicht als neue Forschungsergebnisse ausgeben: PCD-Laden/Voxelisierung/Boden-/Clearance-/Hindernis-/Stairklassifikation/Export, NetworkX-Graph/A*, ComputePathToPose, RViz/Filter/Follower, Odometry-/TF-Verarbeitung, zentrale strikte YAML/Robotprofil, vier Launches/sieben Entry-Points, Lizenz-/Metadaten-/Dependencykorrekturen bis V4-011 und43 Funktionsregressionen. Neu im aktuellen Auftrag: reale isolierte Dependencyverifikation, normale Share-Defaults, separater exklusiver Outputpfad, Lint-/Headerkompatibilität mit aktivem Checker,37 Output-/Installed-Regressionen und tatsächliche Clean-/Source-free-Abnahme. AST-/Bestandstests stützen den Erhalt der Algorithmen; vollständige Algorithmus-/Fahrzeug-/GUI-Regression ist nicht bewiesen.

Verbleibende Release-Gates: vollständige rechtliche Rechte-/Distributions-/historische Datenprüfung, geeigneter autorisierter öffentlicher V4-Ref und Namens-/Indexreview, freigegebene Releaseversion/-politik/Changelogs und konkrete Bloom-/Releaseorganisation. Lokale Humbleergebnisse sind keine externe Indexregistrierung/Buildfarmabnahme. CI/QualityLevel/Multi-Distribution sind zusätzliche Projektqualität und keine erfundenen pauschalen Indexpflichten. ROS Index/Bloom/Buildfarm bleiben NOT READY.

Nächster sinnvoller Schritt ist ausschließlich nach ausdrücklicher neuer Freigabe AP05 – ROS Interfaces and Configuration. Schwerpunkt: dokumentierte bestehende Grenzen von absoluten Topics/Namespaces/Remapping, TF-Verträgen, gepackter PointCloud2-Annahme und nichtnormalisierten Quaternion-Markern. Keine neue SLAM-/Nav2-/Algorithmusarbeit begonnen. AP07/Releaseautomatisierung erst nach stabilen Verträgen; AP09-Plattformdependencies getrennt klären.

Abschlussgrenzen: nur V4; V1/V2/V3/main und Remote-Tracking-Refs unverändert; Baseline c65642fe56015556f696364a724cb5b976a27888 bleibt Vorfahr. Historisches PDF SHA256 8c3603ec2dac85c5cabcca7ae7e85c8d8c709663fa02fabd09039274a2b35383 unverändert; Root-/beide Paket-LICENSE SHA256 cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30 unverändert. Sechs Fremdnoticeblöcke erhalten, neun getrackte alte PYC nicht bereinigt. Keine History-Rewrites, Remote-/Sichtbarkeits-/öffentliche Repositoryänderung, kein Push, keine Veröffentlichung und keine realen Roboterbewegungen. Kein R3D_null untersucht/geändert.


## 17. AP05 – Schnittstellenanalyse und Migration (ab V4-017)

### 17.1 Verifizierter Eingang und Anforderungen

Datum14.10.2026, Eingang22be983. AP01 technisch/02/03/04 und der bisherige AP06-Umfang vorhanden, keine neue Ausführung daraus ableiten. Historische Vorleistungen bleiben A*, Graph-/PCD-/Voxel-/Clearance-/Stairfunktion, ROS-Nodes, vier Launches, zentrale YAML, Standard-Odometry/TF,86Bestandstestfälle. Neue Aufgabe ist Schnittstellenfinalisierung plus spätere Tests/CI/Dokumentation/Distribution/Releasevorbereitung in festgelegter Reihenfolge. Die neuen Phasen sind ausdrücklich beauftragt; für inkompatible Verträge gilt weiterhin separate Freigabe.

Offizielle Quellen neu gelesen: [Humble ComputePathToPose](https://raw.githubusercontent.com/ros-navigation/navigation2/humble/nav2_msgs/action/ComputePathToPose.action), [Humble sensor_msgs_py](https://raw.githubusercontent.com/ros2/common_interfaces/humble/sensor_msgs_py/sensor_msgs_py/point_cloud2.py), [Quaterniondefinition](https://raw.githubusercontent.com/ros2/common_interfaces/humble/geometry_msgs/msg/Quaternion.msg). Inference: Action-Server/-Client sind im Rootnamespace passend, aber bei Namespacebetrieb serverrelativ/clientabsolut inkonsistent. sensor_msgs_py stellt Feld-Dtypebau bereit; sein Humble read_points verarbeitet row_step nicht explizit und byteswap ist inplace, deshalb dürfen Rowpadding/readonly Daten nicht ungeprüft durch diesen Helfer geleitet werden. Kein fremder Quelltext kopiert, nur API/Verhalten untersucht.

### 17.2 Tatsächliche ROS-Schnittstellen am Eingang

| Package / Executable | Node | Publikationen / Subscriptionen | Service / Action | TF / QoS / Launch |
|---|---|---|---|---|
| r3d_planner / pcd_path_planner | global_graph_planner | /global_path Path, /planned_path Marker; robot.odometry.topic Odometry | relativer Server compute_path_to_pose, Nav2 ComputePathToPose | map<-odom zum Odometry-Stempel, kein Broadcaster; Path/Marker reliable volatile keep-last10, Odometry SensorDataQoS; planner.launch.py |
| r3d_planner / local_filter | obstacle_cliff_filter | Sensorcloud input konfiguriert; /local/filtered_obstacles und /local/cliff_virtual_wall PointCloud2, /stair_detect PointStamped | keine | Keine TF, Verarbeitung im incoming sensor frame; alle depth10 reliable volatile; optional in planner.launch.py |
| r3d_planner / rviz_interface | r3d_rviz_interface | /clicked_point, /initialpose, /goal_pose Subscriptions | relativer Trigger-Service recalibrate_pose; absoluter Client /compute_path_to_pose | optional static map->odom Kalibrierung, externe Lokalisierung bei publish_map_odom=false; Subs depth10 reliable volatile; optional planner.launch.py |
| r3d_planner / path_follower | r3d_path_follower | /global_path Path, /local/filtered_obstacles PointCloud2, configured Odometry; configured cmd_vel Twist | keine | map<-odom zum Posezeitstempel, kein Broadcaster; Cloud/Path/Twist depth10 reliable volatile, Odometry SensorDataQoS; nur follower.launch.py |
| r3d_planner / path_test | r3d_path_test | keine normalen Topics | keine | Test static odom->base_link Identität; keine Launchintegration; nicht parallel zum echten Odometry-TF-Owner starten |
| r3d_preprocessor / pcd_server | pcd_publisher | /map_pointcloud PointCloud2 | keine | configured map_frame als Label ohne Transformation; reliable transient-local keep-last1; map.launch.py |
| r3d_preprocessor / pcd_analyser | pcd_to_graph_node | keine | keine | Offline-PCD/read-only Input, separate exklusive Dateioutput; kein TF/QoS; preprocessor.launch.py |
| r3d_preprocessor / kein Console-Entry-Point | pcd_publisher (alternatives Modul) | /map_pointcloud XYZ-only | keine | hardcoded map frame, reliable transient-local keep-last1; nicht installiert als Executable, Namenskollision falls manuell parallel gestartet |

QoS-Defaults für depth10: KEEP_LAST/RELIABLE/VOLATILE, Deadline/Lifespan Default unbeschränkt, Liveliness system-default und Lease default. SensorDataQoS: KEEP_LAST depth5/BEST_EFFORT/VOLATILE. Action/Service verwenden rclpy-Defaults; kein benutzerdefiniertes Deadline/Livelinessprotokoll. TF-Publisher/Listenerbibliothek regelt /tf bzw./tf_static selbst, nicht neu konfiguriert. Keine eigenen Message-/Service-/Actiontypen am Eingang.

Vollständiger statischer Parameter-/Schnittstellenstellenindex (Literal-/Dictionarydefaultdeklarationen, keine Ausführung):

**r3d_planner/r3d_planner/odometry.py**

- Zeile57: `Parameterdefaults: {'odometry_topic': '/lidar_odometry', 'odom_frame': 'odom', 'base_frame': 'base_link', 'map_frame': 'map', 'odometry_timeout_sec': 1.0}`
- Zeile61: `node.declare_parameter(key, value)`
- Zeile70: `node.create_subscription(Odometry, self.topic, self.callback, qos_profile_sensor_data)`

**r3d_planner/r3d_planner/r3d_local_filter.py**

- Zeile59: `Parameterdefaults: {'pointcloud_topic': '/hesai_ros_driver/hesai/lidar_points', 'min_height': 0.05, 'max_height': 1.0, 'max_step_height': 0.22, 'min_step_height': 0.06, 'cliff_width': 0.4, 'stair_roi_x_min': 0.7, 'stair_roi_x_max': 1.1, 'stair_roi_width': 0.5, 'min_reliable_distance': 0.65, 'stair_min_points': 50, 'cliff_roi_x_min': 0.7, 'cliff_roi_x_max': 1.2, 'cliff_min_ground_points': 30, 'cliff_wall_points': 20, 'cliff_wall_height': 0.5}`
- Zeile68: `self.declare_parameter(key, value)`
- Zeile70: `self.create_subscription(PointCloud2, self.get_parameter('pointcloud_topic').value, self.pc_callback, 10)`
- Zeile73: `self.create_publisher(PointCloud2, '/local/filtered_obstacles', 10)`
- Zeile74: `self.create_publisher(PointCloud2, '/local/cliff_virtual_wall', 10)`
- Zeile77: `self.create_publisher(PointStamped, '/stair_detect', 10)`

**r3d_planner/r3d_planner/r3d_path_follower.py**

- Zeile41: `Parameterdefaults: {'lookahead_distance': 0.5, 'max_linear_speed': 0.35, 'max_angular_speed': 0.6, 'stop_distance': 0.6, 'goal_tolerance': 0.2, 'control_period_sec': 0.1, 'obstacle_x_min': 0.1, 'obstacle_half_width': 0.3, 'max_angular_speed_narrow': 0.2, 'angle_threshold': 0.5, 'steering_gain': 1.5, 'narrow_speed_factor': 0.4, 'turning_speed_factor': 0.3, 'cmd_vel_topic': '/cmd_vel'}`
- Zeile49: `self.declare_parameter(key, value)`
- Zeile58: `self.create_publisher(Twist, self.cmd_vel_topic, 10)`
- Zeile60: `self.create_subscription(Path, '/global_path', self.path_callback, 10)`
- Zeile63: `self.create_subscription(PointCloud2, '/local/filtered_obstacles', self.obstacle_callback, 10)`

**r3d_planner/r3d_planner/r3d_pcd_path.py**

- Zeile56: `self.declare_parameter('map_dir', default_dir)`
- Zeile57: `self.declare_parameter('map_name', 'map_analysed.pcd')`
- Zeile61: `self.declare_parameter('voxel_size_cm', 5.0)`
- Zeile62: `self.declare_parameter('min_step_height_cm', 5.0)`
- Zeile63: `self.declare_parameter('max_step_height_cm', 25.0)`
- Zeile68: `self.declare_parameter(key, value)`
- Zeile91: `self.create_publisher(Marker, '/planned_path', 10)`
- Zeile93: `self.create_publisher(Path, '/global_path', 10)`

**r3d_planner/r3d_planner/r3d_rviz_interface.py**

- Zeile42: `self.declare_parameter('match_radius', 0.8)`
- Zeile43: `self.declare_parameter('publish_map_odom', True)`
- Zeile44: `self.declare_parameter('map_frame', 'map')`
- Zeile45: `self.declare_parameter('odom_frame', 'odom')`
- Zeile51: `self.create_subscription(PointStamped, '/clicked_point', self.point_cb, 10)`
- Zeile53: `self.create_subscription(PoseWithCovarianceStamped, '/initialpose', self.initial_pose_cb, 10)`
- Zeile55: `self.create_subscription(PoseStamped, '/goal_pose', self.goal_pose_cb, 10)`
- Zeile59: `self.create_service(Trigger, 'recalibrate_pose', self.recalibrate_callback)`

**r3d_preprocessor/r3d_preprocessor/r3d_pcd_analyser.py**

- Zeile329: `self.declare_parameter('pcd_path', 'environment.pcd')`
- Zeile330: `self.declare_parameter('output_dir', '')`
- Zeile331: `self.declare_parameter('voxel_size_cm', 5.0)`
- Zeile332: `self.declare_parameter('max_step_height_cm', 25.0)`
- Zeile334: `self.declare_parameter('min_points_per_sqm', 10.0)`
- Zeile335: `self.declare_parameter('min_points_per_voxel', 3)`
- Zeile336: `self.declare_parameter('floor_height_tolerance', 0.02)`
- Zeile337: `self.declare_parameter('ground_fill', True)`
- Zeile339: `self.declare_parameter('robot_base_clearance_cm', 10.0)`
- Zeile340: `self.declare_parameter('robot_narrow_radius_cm', 30.0)`
- Zeile341: `self.declare_parameter('min_step_height_cm', 5.0)`
- Zeile342: `self.declare_parameter('robot_radius_cm', 40.0)`
- Zeile343: `self.declare_parameter('robot_height_cm', 80.0)`
- Zeile344: `self.declare_parameter('analysis_grid_size_cm', 20.0)`
- Zeile345: `self.declare_parameter('cluster_gap_threshold_cm', 20.0)`
- Zeile346: `self.declare_parameter('fill_plane_iterations', 2)`
- Zeile347: `self.declare_parameter('fill_plane_search_radius', 2)`
- Zeile348: `self.declare_parameter('fill_plane_min_neighbors', 4)`

**r3d_preprocessor/r3d_preprocessor/r3d_pcd_publisher.py**

- Zeile40: `self.declare_parameter('pcd_path', 'environment.pcd')`
- Zeile41: `self.declare_parameter('map_frame', 'map')`
- Zeile47: `self.create_publisher(PointCloud2, '/map_pointcloud', qos_profile)`

**r3d_preprocessor/r3d_preprocessor/r3d_pcd_voxel_publisher.py**

- Zeile40: `self.declare_parameter('pcd_path', 'environment.pcd')`
- Zeile47: `self.create_publisher(PointCloud2, '/map_pointcloud', qos_profile)`

Die vier bestehenden Launchfiles führen jeweils description(mode) aus; configured_nodes lädt strikte YAML/Robotprofile und gibt Dictionaries als ROS-Parameter weiter. Keine Launchargumente für Namespace/Remapping am Eingang. Preprocessor-/Map-/Follower-Modus separiert; optionale LiveFilter/RViz-Komponenten bleiben unabhängig. Vollständige Einheiten/Bounds und Output-/Map-/Robotprofile stehen bereits in docs/CONFIGURATION.md; obiger Index benennt zusätzliche Standalone-/Odometrydefaults. Node-Namen werden nicht durch Executable-Namen ersetzt.

### 17.3 Vertragsbefunde und Veränderungsgrenzen

| ID | Befund / tatsächliche Evidenz | Einordnung | Externe Auswirkung / geplante Behandlung |
|---|---|---|---|
| I01 | Planner execute_callback setzt narrow z=1,w=1; Follower control_loop liest z>0.5 | konkrete Quaternion-/Pose-Semantikverletzung | Generische Poseconsumer und Legacy-narrowdecoder betroffen; nur nach17.4-Freigabe migrieren |
| I02 | LocalFilter pc_callback interpretiert jedes Byte als gepacktes12-byteXYZ; row_step/fields/endian ignoriert | konkrete PointCloud2-Datenvertragsverletzung | Gültige XYZI/RGB/Padding/Organizedwolken falsch; feldbasierter stride-/endianbewusster Decoder, XYZ finite, Inputbytes nicht ändern |
| I03 | LocalFilter benutzt ausdrücklich sensorbezogene YAML-Schwellen und Header, Follower interpretiert X/Y für Vorwärtsfahrt ohne Frameprüfung | definierter Filtervertrag, aber ungesicherter Follower-Framevertrag | Filter nicht still auf Baseframe ändern; Follower-Cloud bei Sensorstempel nach base_frame transformieren, bei fehlender TF stoppen; Freigabe17.4 |
| I04 | Server compute_path_to_pose relativ; Client /compute_path_to_pose absolut, viele Topics absolut | Root gültig; namespacefähige Komposition fehlt, Namen allein kein ROS-Verbot | Optionaler Launchnamespace plus konsistente explizite Remaps, Rootdefaults erhalten; keine stillen Umbenennungen |
| I05 | Action hat keinen Cancelcallback; synchroner Execute im Singlethreadexecutor, planner_id ignoriert; positionsfinite/startorient nicht geprüft; planning_time nie gesetzt | konkrete Action-/Validierungsgrenzen | Humble besitzt kein error_code/Feedbackpayload; Status/result/cancel/finite/plannerID tests nötig, kein Lifecycle-/Pluginredesign |
| I06 | Cloudinput Reliable depth10 trotz möglicher BestEffortsensoren; Odometry SensorData und MapTL bereits sinnvoll | QoS-Interoperabilitätsverbesserung, kein einheitlicher QoS-Zwang | Sensorinput BestEffort empfängt beide Publisherarten; Änderungen der Nutzeranforderungen konkret dokumentieren/testen |
| I07 | Follower cached obstacle_in_front ohne Alter/Ersteingang, verwertet Header/TF nicht | ungesicherter Kommunikations-/Frischevertrag | Neue fail-closed-Datenvalidierung ist Verhaltensänderung, gesonderte17.4-Freigabe; kein Sicherheitszertifikat |
| I08 | min_reliable_distance0.65 im Filter versus stop_distance0.6 beim Follower | konkrete Integrationsgrenze, nicht universelle Controllerlösung | In identisch ausgerichteten/gleichursprünglichen Frames liegen Filterpoints außerhalb Stopzone; Defaulttuning nicht blind ändern, Grenzen und Kalibrierung dokumentieren |
| I09 | RVizpunkt/Posenheader/-quaternion nicht geprüft, wait_for_server unbeschränkt | konkrete Frame-/Validierungs-/Blockierungsgrenze | Ungültige/fremdframe/geometrisch ungültige Eingaben klar ablehnen, Wartezeit begrenzen; keine konkurrierende map->odom-Publikation |
| I10 | Cliff/Stair publiziert, Follower konsumiert beide nicht; planarXY und narrowdecode | vorhandener Funktionsumfang und externe Sicherheitsintegration | Dokumentierte Grenze, kein vollständiger neuer 3DController/Cliffintegration |

TF-Eigentümer: map->odom ausschließlich globale Lokalisierung oder ausdrücklich eingeschaltete Legacy-RVizkalibrierung; odom->base_link ausschließlich externe Odometryquelle. Planner/Follower lesen nur. Posezeitstempel ist maßgeblich; fehlende/extrapolierte/ungültige TF darf nicht als Identität ersetzt werden. Sensorachsen/-ursprung bleiben eigener dokumentierter Vertrag, nicht aus Framezeichenketten erschlossen.

### 17.4 Konkrete Migrationsstrategie – noch nicht freigegeben

**Entscheidung M01 (Quaternion/narrow):** Statt einer Flag-Normalisierung wird die bestehende geometrische Path-Ausgabe auf echte, normierte Orientierungen entlang der Pfadtangente umgestellt (Endpunkt letzter gültiger Tangentenheading; Einpunktpfad validierte Zielorientierung). Positionen/Graphfarben/Kosten/A* bleiben erhalten. Der Typ nav_msgs/Path und /global_path sowie ComputePathToPose bleiben erhalten; ihre Orientierungssemantik ändert sich ausdrücklich. Alte Consumer dürfen z>0.5 danach nicht als narrow lesen.

Ergänzung eines kleinen ROS-Interfacepakets r3d_interfaces (0.0.1/Apache-2.0, rosidl/ament_cmake ausschließlich für die Nachrichtengenerierung), Nachricht PathWithMetadata:

```text
nav_msgs/Path path
bool[] narrow
```

Neues /global_path_metadata publiziert den kompletten geometrischen Path und genau ein narrow-Bool pro Pose atomar in derselben Nachricht. Dadurch keine stamp-only-Zuordnung zweier getrennt transportierter Arraytopics, kein Flagverlust/race beim Pairing; Pathheader/Koordinaten sind identisch mit Actionresult und Standard-Pathausgabe. Metadatentransport reliable/transient-local/keep-last1 (Publisher und Follower): später Follower bekommt letzten kompletten Pfad inklusive Flags. Standard-/global_path behält seinen bisherigen QoS. Follower verwendet ausschließlich die angereicherte Nachricht; prüft Länge, Frames, finite Geometrie und Quaternionen. Fehlende/inkonsistente Metadaten führen zu Stop, kein interpretierter Legacyfallback. Neuplanung ersetzt Path+Flags gemeinsam. Empty-Path löscht beides gemeinsam.

Rollout: neues Interfacepaket, Planner und Follower gemeinsam bauen/installieren; bestehenden `path_follower` nicht mit einem Legacyplanner mischen. Generic Pathconsumer behalten Topic/Typ und erhalten geometrisch gültige Posen. Eigene/externe Legacy-narrowdecoder auf PathWithMetadata migrieren. In lokalen V4-Entwicklungsdocs Breaking-Change/Migrationsanweisung und paketweisen unreleased Changelog festhalten; keine Releaseversion/Tag/Push auswählen. Keine alten Invalidquaternionen als dauerhaften Parallelkanal ausgeben, keine narrowkodierung in Position/Covariance/anderen geometrischen Standardfeldern.

**Entscheidung M02 (Followerdaten):** Fehlende, ungültige, future-datierte oder ältere-als-Timeout Hindernisdaten sollen in der vorgeschlagenen strikten V4-Betriebsart Null-Twist auslösen. Vorgeschlagener neuer Parameter obstacle_timeout_sec=1.0s, zentral validiert und dokumentiert. Hindernisse anhand ihres Messstempels nach robot.base_frame transformieren; keine gültige TF/ungültige Transformation -> Eingabe ungültig/Stop. Nur neue gültige zeitaktuelle Wolke kann Freigabe liefern; leere aber gültige Wolke ist ein legitimer clear-Befund. Frische Pose/Pfad/Metadaten weiter nötig. Controllerberechnungen/Geschwindigkeitswerte bleiben erhalten, keine Cliff/Stairintegration oder komplette neue Bewegungssteuerung. Dies ändert bisherige Weiterfahrt ohne Hinderniseingang und muss vor Umsetzung separat genehmigt werden.

Alternativen/Tradeoffs: (a) getrennter typisierter Header+Boolarray-Kanal spart doppelte Pfadpositionen, benötigt aber exaktes Pairing/Cache/Timeout und bringt zusätzliche Fehlzustände; (b) JSON/String vermeidet Interfacepaket, verliert aber rosidl-Typprüfung/Discovery und erschwert publicAPI; (c) lokal erneutes Map-KDTree-Matching vermeidet neuen Transport, bindet Follower an Graphkarten/Regenerationsparameter und kann Wegpunktzuordnung verlieren. Empfohlen M01 mit atomarer typisierter Nachricht trotz zusätzlichem kleinen Package und transportiertem Path; größere Scopeänderung sichtbar und nicht bereits implementiert.

Freigabequelle ist ausdrücklich der aktuelle Nutzerauftrag, Abschnitt6 („Solche nicht rückwärtskompatiblen Änderungen benötigen eine gesonderte Freigabe“), Abschnitt10 und38. Die allgemeine AP05-Freigabe ersetzt diese konkrete Migrationsfreigabe nicht. Unabhängige PointCloud2-Dekoderkorrektur I02 erfordert kein Legacytopic-/narrow-/Followerstop-Defaultbruch und kann separat geprüft werden. PhasenAP06..AP10 folgen auf die abschließend freigegebene/abgenommene AP05-Schnittstellenbasis; nicht als abgeschlossen erklären, solange M01/M02 offen sind.


### 17.5 Tatsächliche aktuelle Nachweise und Freigabegrenze

Datum14.10.2026. Neue Ergebnisse beziehen sich auf den jetzigen PointCloud2-/Testhelperstand, nicht auf die unimplementierte gesamte Migrationsstrategie. C1=r3d-v4-interface-humble-20261014, C2=r3d-v4-interface-sourcefree-20261014. Beide offizielles Humbleimage mit dem bereits dokumentierten Digest860e5379..., Ubuntu22.04.5/Python3.10.12, native Aptversionen NumPy1.21.5/SciPy1.8.0/Open3D0.14.1/NetworkX2.4, kein User-Site/Conda. C1 Source readonly, neue Workspaces getrennt; C2 nur readonly-Install/Testfiles/Manifestkopien/Harness und getrennte Ergebnisausgabe, kein Sourcecheckout. FastDDS/localhost/Domain213,215 bzw.214; Tests UID1000. Kein hardwarebezogener Follower-spin oder produktives cmd_vel.

| Test-ID | AP | Prüfung | Kommando / Umgebung | Ergebnis | Status |
|---|---|---|---|---|---|
| T87 | AP05 | Git/Inventar/Schema | ASTindex und tatsächlicher Containerimport ComputePathToPose.Result.get_fields_and_field_types()/ActionServer-signature | Names/Params/QoS inventarisiert; Humble path+planning_time, leerer Feedbackpayload, keine error_code; Quaterniondefaultw1 | VERIFIED Analyse |
| T88 | AP03/AP05 | Echte aktuelle Installation/check | rosdep install/check --from-paths /r3d-source/r3d_planner /r3d-source/r3d_preprocessor --ignore-src --rosdistro humble --os=ubuntu:jammy (install -y); C2 entsprechend /dependency-manifests | Je Exit0 ohne skip/simulate, Imports erfolgreich; keine NumPy/SciPy-Kompatibilitätswarnung | VERIFIED Humble |
| T89 | AP05/AP06 | Cloudlayouts/Outputs | test_pointcloud.py, actual installed Humblemodule | 83PASS, 64Kombinationen plus malformed/finite/empty/mixed/anonymous/array/nodefälle | VERIFIED |
| T90 | AP05 | Performance/Allocation | 100000finiteXYZ,15Trials; tracemalloc/timing im isolierten Prozess | packed0.528ms, organizedRGB+padding0.569ms; ca1.61MBtracedpeak ohne Input; kein universeller Benchmark | VERIFIED spezifische Messung |
| T91 | AP06 | Testhelpertransient/permanent | Zwei test_parameter_query_readiness_preserves_failures-Fälle, echter Launchtest weiterhin aktiviert | Wiederholung nur bei CLIexit!=0; dauerhaft3Fehler führen Assertion mit stdout/stderr; Params unverändert geprüft | VERIFIED |
| T92 | AP04/AP06 | FreshCopy1 | /work/cloud6: colcon build; colcon test; colcon test-result --verbose | Je Exit0;171PASS/0FAIL/0ERROR/0SKIP;6Lints aktiv | VERIFIED |
| T93 | AP04/AP06 | FreshCopy2 | /work/cloud7 gleiche Befehle, neuer Workspace/Domain | Je Exit0;erneut171PASS/0FAIL/0ERROR/0SKIP | VERIFIED |
| T94 | AP04/AP06 | Sourcefrei/readonly | C2 pytest /runtime-tests, install=/work/cloud6/install readonly | Exit0;120PASS/0FAIL/0SKIP, Module aus Install, Sourcecheckout fehlt, kein installiertesPCD | VERIFIED Teilumfang |
| T95 | AP01/AP02/AP08 | Geschützte Inhalte/Codeidentität | Ref-/SHA-/Eventvergleich, module/testcopy bytevergleich, git diff --check | Baseline/PDF/LICENSE/Manifeste/Version/Fremdnotice/alteEreignisse unverändert; finale Produktions-/Testkopien identisch | VERIFIED |
| T96 | AP05/AP07..10 | Migrations-/Phasengate | Kein entsprechender Implementierungs-/CI-/Releasebefehl | M01/M02 angefragt, keine Antwort als Zustimmung gewertet; spätere Phasen noch nicht ausgeführt | BLOCKED Entscheidung / NOT VERIFIED spätere Phasen |

Aktuelle erfolgreiche Hauptbefehle in beiden neuen Workspaces, als unprivilegierter User und ohne --symlink-install/alte R3D-Overlays:

```bash
source /opt/ros/humble/setup.bash
cd /work/cloud6  # zweiter Lauf: /work/cloud7
export PYTHONNOUSERSITE=1
colcon --log-base log-build build --packages-select r3d_preprocessor r3d_planner --event-handlers console_cohesion+
source install/setup.bash
colcon --log-base log-test test --packages-select r3d_preprocessor r3d_planner --event-handlers console_cohesion+
colcon test-result --verbose
```

Tatsächliche Ausgabe jeweils, test-result Exit0:

```text
Summary: 171 tests, 0 errors, 0 failures, 0 skipped
```

Source-frei C2 als UID1000:

```bash
source /opt/ros/humble/setup.bash
source /work/cloud6/install/setup.bash
cd /work/runtime-user
python3 -m pytest -p no:cacheprovider --basetemp=/work/runtime-user/pytest --junitxml=/results/pytest.xml /runtime-tests -q
```

Tatsächliche Ausgabe, Exit0:

```text
........................................................................ [ 60%]
................................................                         [100%]
120 passed in 3.59s
```

Frühere Fehlläufe cloud1..4 sind in V4-018/019 offen ausgewiesen; keine FAIL-als-PASS-Wertung. cloud5 bestand169Fälle vor Testhelperergänzung, cloud6/7 nun171. NetworkX-/ament-Deprecations bleiben, kein globales Ignorieren. Die Source-freien120Fälle umfassen27Installation+10Output+83Cloud, nicht die43anderen Funktionstests oder die2reinen Testhelperfälle. Rohlogs/xUnit/Benchmark/Isolations-/Bytevergleiche temporär unter /tmp/r3d-v4-finalization, dauerhaft relevante Ergebnisse hier; kein neuer Forschungsbericht.

Fokussierte Commits: Inventar/Migrationsvorschlag60bbe44622deb7f3671b52403a435f648852d23d; begrenzter Testhelper add819661cc2405823b0c8f31b1ea7b1e7efe9e8; PointCloud2 plus aktuelle Dokumentation im eindeutigen `fix(ros): decode PointCloud2 fields and row padding`-Commit (Parent add8196). Commitorder der unabhängigen Helper-/Cloudkorrektur ist nicht die Reihenfolge der V4-IDs; V4-018 wurde vor Codeänderung angelegt, V4-019 dokumentiert den während seiner Abnahme gefundenen Testwerkzeugbedarf. Jeder Implementationcommit enthält das Protokoll.

**Freigabegrenze:** Die angefragten M01/M02-Verträge sind weiterhin nicht implementiert; kein neues Interfacepaket oder Metadatatopic angelegt, keine Quaternion-/Followerframe-/Hindernistimeout-/Namespace-/QoS-/Actionmigration durchgeführt. AP05 IN PROGRESS, Cloud-/Queryteil VERIFIED; erweiterter AP06-Gesamtumfang IN PROGRESS. AP07/AP09 NOT STARTED; AP08/AP10 begleiten als IN PROGRESS, keine spätere Phase vor der stabilisierten/freigegebenen AP05-Basis abgeschlossen. ROS Index/Bloom/Buildfarm weiterhin NOT READY; rechtliches Gesamtgate unverändert. Der Gesamtauftrag AP05..AP10 ist ausdrücklich noch nicht abgeschlossen und wird nach gesonderter Migrationsentscheidung fortgesetzt.

Es wurden ausschließlich zwei eigene Testcontainer gestoppt/entfernt; bestehende Dockerimages/Hostpakete/Conda/ROS-/NVIDIA-/Daemonkonfiguration unberührt. V1/V2/V3/main/Remote-Trackingrefs/Gitconfig/PDF/Lizenztexte/historischeV4-001..016 unverändert, keine Historienumschreibung/externenRepositoryänderung/Push/Release/Hardwarebewegung. Kein R3D_null untersucht/geändert.


## 18. Fortsetzung am 15. Oktober 2026 – M01 und weitere freigegebene Phasen

### 18.1 Freigabe und Phasenabgrenzung

Der Nutzer hat M01 zweimal ausdrücklich bestätigt: nur M01 freigeben, M02 zurückstellen; anschließend PathWithMetadata/standardkonformen Path/eindeutige Paarung und vollständige Build-/rosdep-/Install-/Testintegration konkret beauftragt. M01 wird unter V4-020 implementiert, neue Schnittstelle ist eine freigegebene inkompatible Narrow-Decoder-Migration. Vorschlag17.4 bleibt historisch nachvollziehbar. M02 hat keine Implementierungsfreigabe: nicht als implizite Folge von M01 einschleusen. Weitere ursprüngliche AP05..AP10-Aufgaben bleiben beauftragt; zurückgestellte M02-Gesamtqualität am Ende offen ausweisen, nicht als Grund für unnötiges Stoppen aller unabhängigen Phasen behandeln.

### 18.2 M02-Vorschlag – optionaler Filter, Timeout, TF und Stopzustände

**Status: Analyse abgeschlossen, Vorschlag, keine Umsetzung.** Evidenz: configured_nodes in launching.py startet local_filter ausschließlich bei components.live_filter.enabled. planner.launch.py startet niemals path_follower; follower.launch.py ist separat. Offlineplanung funktioniert ohne Filter/Hardware. Beim heutigen Follower startet obstacle_in_front=false; vorhandene Wolken können Stop setzen, fehlen/veralten sie, besteht keine vollständige Frischeüberwachung. Genau dieser Default bleibt auf Nutzerwunsch bestehen, einschließlich fehlender Sensor->Base-Transformation. M01-Metadatenvalidierung ist davon unabhängig.

Eine global verpflichtende Hindernisquelle würde bei live_filter=false und fehlendem externen Publisher jede Followerfahrt verhindern. Ein automatisches Aktivieren des Filters wäre ein versteckter Konfigurationsbruch; ein automatisches Deaktivieren der Überwachung beim Ausbleiben von Clouds würde die gewünschte Pflicht umgehen. Auch live_filter=true beweist keinen laufenden Sensor/keine geeignete Cloud. Umgekehrt kann live_filter=false mit einem externen geprüften Hindernispublisher sinnvoll sein. Deshalb keine Regel „Pfadplanung benötigt stets local_filter“, keine Ableitung von Sicherheit aus der bloßen Node-/Publisherexistenz.

Vorgeschlagene zukünftige Konfiguration (keine aktuell akzeptierte YAML, noch nicht einfügen):

```yaml
path_follower:
  # existing keys retained
  obstacle_monitor:
    enabled: false
    topic: /local/filtered_obstacles
    timeout_sec: 1.0
    tf_timeout_sec: 0.1
    max_future_skew_sec: 0.0
```

- enabled=false erhält ausschließlich den bisherigen Kommunikationsvertrag: empfangene Hindernisse wirken weiter, aber kein behaupteter Frische-/TFschutz. Deaktivierte Überwachung bedeutet keine Sicherheitsfreigabe.
- enabled=true verlangt zum Fahren aktuelle gültige Hindernisdaten unabhängig davon, ob sie vom optionalen lokalen Filter oder einem externen Node stammen. Kein gültiger Ersteingang -> WAITING und Null-Twist; keine automatische Abschaltung des Monitors.
- Follower liest base_frame aus dem bereits gewählten Robotprofil, kein zweites konkurrierendes Framefeld. Bei anderem Cloudframe exakt nach base_frame am Messstempel transformieren; alle numerischen TFwerte/Quaternionen prüfen, normieren und Transformationsrichtung beachten. Bei fehlender/extrapolierter/ungültiger TF kein Identitätsfallback und keine Verwendung einer anderen/latest-Zeit. Statische TF darf legitimerweise Stempel0 haben; nicht pauschal als veraltet verwerfen. Dynamische TF am Messstempel durch TF2 validieren.
- timeout_sec>0 prüft Messalter mit ROSclock; zulässiger Future-Skew explizit begrenzt. Zusätzlich begrenzte Empfangsfrische verhindert endloses Replaying alter Nachrichten. Clockrücksprung/ungültige Clock -> warten/stoppen bis gültige neue Daten. Externer Base-Command-Watchdog bleibt nötig: ein blockierter Executor oder pausierter ROS-Timer kann keine regelmäßigen Nullbefehle garantieren.
- Gültige leere XYZ-Wolke ist ein definierter clear-Befund des gewählten Producers; malformed/fehlendeXYZ/nonfinite-only-Daten dürfen nicht still als freier Raum interpretiert werden. Ob eine echte Inputwolke ausschließlich ungültigePunkte enthielt, muss vor dem Wegfiltern erkennbar bleiben. Eigener Dateninvalidstatus statt bloßes bool obstacle_in_front.

| Zustand bei aktiviertem Monitor | Auslöser | Cmd-Verhalten / Wiederanlauf |
|---|---|---|
| WAITING | Noch kein gültiger Cloud-/TF-/Clockeingang | Null-Twist; nur gültiger aktueller Eingang hebt Sperre auf |
| CLEAR | Aktuelle gültige Wolke, richtige TF, kein StopROI-Hindernis | Weiterhin nur bei gültigem Path+Metadaten und frischer Pose fahren |
| BLOCKED | Aktuelles Hindernis im konfigurierten StopROI | Null-Twist; nächster gültiger freier Befund erforderlich |
| STALE / FUTURE / CLOCK_ERROR | Alter/Futuregrenze/Clockvertrag verletzt | Null-Twist; keine automatische Monitorabschaltung |
| TF_ERROR / INVALID_DATA | Fehlende/ungültige Transformation oder Cloud | Null-Twist; nur neuer gültiger Eingang statt altem clearcache |
| DISABLED | enabled=false ausdrücklich gewählt | Bisherige Hindernislogik ohne behaupteten Monitorvertrag |

LocalFilter=false plus enabled=true bleibt erlaubt, braucht aber externen Publisher und passende TF; ohne diese Eingänge WAITING/Stop. Optionalfilterflag wird nicht still überschrieben. LocalFilter=true plus enabled=true braucht denselben Eingangs-/Frischenachweis. Motionfreigabe/Diagnose beschreibt die Ursache, nicht nur „kein Pfad“; keine zusätzliche öffentliche Statusschnittstelle vor einer begründeten Schemaentscheidung einführen.

**Integrationsgrenzen:** Filter min_reliable_distance0.65 und Follower stop_distance0.6 überlappen bei identischem Ursprung/Achsen nicht sinnvoll; Sensoroffset/TF verschieben die Zone zusätzlich. Frische leere Filterausgabe beweist deshalb keine vollständige Nahbereichsbeobachtung. Grenzen/Kalibrierung müssen vor Motionfreigabe abgestimmt und synthetisch geprüft werden; keine Zahlen automatisch „reparieren“. Cliff/Stair-Ausgaben sind weiterhin keine internen Followerstopquellen. M02 wäre Datenvertragsverbesserung, keine zertifizierte Kollisions-/Cliff-/Robotersteuerung.

Erforderliche zukünftige Regressionen vor M02-Abnahme: enabled=false Legacyverhalten; enabled=true ohneFilter/ohneexternenPublisher WAITING; externesCloudangebot bei Filterfalse; echte statische/dynamische TF am Cloudstempel; falscheRichtung/fehlende/veraltete/nichtfiniteTF; stale/future/Clockjump; invalid versus echte leere Wolke; Hindernis/clear/erneutstale; Pose-/Path-/Metadatenverlust; Zielerreichung; Cmd ausschließlich isoliertes Testtopic. Neue Parameter zentral strikt validieren und proMode dokumentieren, keine Hardware. Die Umsetzung wartet ausdrücklich auf weitere Nutzerfreigabe; diese Analyse beantragt keinen Push/Release.


### 18.3 M01-Abnahme und neue Paketintegration

M01 freigegeben/implementiert unter V4-020; M02 nur untersucht unter V4-021. Drei ROSpakete mitVersion0.0.1/Apache-2.0: r3d_interfaces ament_cmake/rosidl sowie zwei bestehende ament_python-Pakete. rosidl_default_generators/build, rosidl_default_runtime/export und nav_msgs/depend plus ament_lint_auto/common(test) deklariert; r3d_planner exec_depend r3d_interfaces. BUILD_TESTING und ament_package im neuen CMakeprojekt; generierte Header/Python/Typesupport und Msgdefinition durch rosidl installiert, LICENSE explizit. Keine manuelle Workspacepfadkopplung oder pip-Pflicht. Offizielle Quelle: [Humble Custom Interfaces](https://raw.githubusercontent.com/ros2/ros2_documentation/humble/source/Tutorials/Beginner-Client-Libraries/Custom-ROS2-Interfaces.rst).

Befehle im isolierten Container mit readonly-Source, UID1000, Domain221/localhost/FastDDS: rosdep install/check --from-paths /r3d-source --ignore-src --rosdistro humble --os=ubuntu:jammy (install zusätzlich -y); normaler colcon build --packages-up-to r3d_planner, source install/setup.bash, colcon test --packages-up-to r3d_planner, colcon test-result --verbose. Je Exit0. Tatsächliche Ausgabe:

```text
Summary: 191 tests, 0 errors, 0 failures, 0 skipped
```

Python-xUnit186, zusätzliche5CMakeprüfungen werden von colcon gezählt; Testhelper darf Pythonzahl nicht mit Gesamtsuite gleichsetzen. Keine neuen Fehler/Skips in dieser M01-Abnahme. Generierte Nachricht/Schema, Qos/Paarung/Migration15neuePythonfälle; neue CMake-/License-/XML-/Stylechecks5. Rohlogs temporär /tmp/r3d-v4-release, dauerhafte relevante Resultate hier. Aktuelle README/INSTALL/PaketREADME/Config-/Architektur-/KnownIssues beschreiben die Migration. Weitere AP05-Korrekturen werden separat getestet; dieser Erfolg gilt nicht vorab für spätere Änderungen oder spätere Source-freie/CI-/Multi-Distro-Abnahmen.


### 18.4 Tatsächliche Action-Abnahme (V4-022)

Normale colcon build/test --packages-up-to r3d_planner in /work/action1, anschließend colcon test-result --verbose; jeweils Exit0, Domain222/localhost/FastDDS/UID1000, readonlySource und keineHardware. Tatsächliche Ausgabe:

```text
Summary: 205 tests, 0 errors, 0 failures, 0 skipped
```

14neue Actionfälle zusätzlich zu191M01-Gesamtfällen. Schema-Humble path+planning_time, keine erfundenen Error-/Feedbackfelder. Ungültige Frames/finitePoses/Quaternionen/fehlendeoderstalePose/TF/unreachable/emptyPath ergebenAbort. Realer CancellationService während laufendemExecute erreichtCanceled. Modifizierter Testsearch simuliert längere Laufzeit; echte A*-Cancelbedingung separat geprüft. Keine Kollisions-/Robotersicherheits-/Echtzeit-/Plugin-/Lifecyclezusage. Alle bereits im Eintrag genannten Grenzen bleiben dokumentiert. M02 nicht umgesetzt.


### 18.5 Komposition und freigegebene AP05-/AP06-Grenze

V4-023 finale Befehle: normaler colcon build/test --packages-up-to r3d_planner und colcon test-result --verbose in /work/compose4, jeweils0. Tatsächliche Ausgabe:

```text
Summary: 225 tests, 0 errors, 0 failures, 0 skipped
```

Rootnames/absoluteRobotTopics bleiben, neue opt-inNamespacekomposition und relativeProfile/ROSRemapping nativ geprüft. Namespace ist keine automatische TF-Frameisolation. RViz/TF/SensorQoS-Verträge belegt, alte Filtergeometrie und FollowerObstaclepolicy erhalten. M02 bleibt ausdrücklich zurückgestellt: keine Hindernisfrische/TF-Stoppolicy, kein Safety-Nachweis. Die freigegebene aktuelle Schnittstellenbasis ist für CI stabilisiert; ursprüngliches vollständiges AP05-Sicherheits-/Followerziel nicht künstlich VERIFIED setzen. AP06 implementierter Umfang verifiziert, endgültiger Copy-/Sourcefree-/CI-Lauf nach neuen CI-/Dokumentänderungen folgt. Weitere unabhängige AP07..AP10-Arbeit bleibt beauftragt und wird ohne erneute allgemeine Freigabefrage fortgesetzt.


### 18.6 AP07 lokale Pipeline und fehlende Remoteabnahme

Offizielle Checkoutquellen geprüft15.10.2026: [Releasev7.0.1](https://github.com/actions/checkout/releases/tag/v7.0.1), [vollständiger Commit3d3c42e5aac5ba805825da76410c181273ba90b1](https://github.com/actions/checkout/commit/3d3c42e5aac5ba805825da76410c181273ba90b1), [Actiondefinition](https://raw.githubusercontent.com/actions/checkout/v7.0.1/action.yml). Workflow pinnt exakt diesen Stand/Node24, read-onlycontents, persist-credentialsfalse; keine externen Schreibaktionen. Shell/Python/Workflowstrukturen tatsächlich geprüft. Kein spezifischerWorkflowlinter oder GitHubActioncheckout lokal vorgetäuscht.

Exakter lokaler Befehl bash scripts/ci/run_humble.sh, Exit0. Tatsächliche Ausgaben:

```text
METADATA_XML_YAML_SYNTAX_DOC_STRUCTURE_PASS
Summary: 225 tests, 0 errors, 0 failures, 0 skipped
169 passed, 2 warnings in 5.77s
CI_LOCAL_BUILD_AND_SOURCEFREE_PASS
```

Zwei getrennte frische Containersysteme, tatsächliche Apt-/rosdepinstallation/check. Runtime hat keinen Source-/Buildbaum, alle3installiertenPakete und generierteNachricht funktionieren. DockercontainerExitcodes zusätzlich explizit geprüft, damit dockerstart/tee keine Containerfehler als Erfolg verdecken. Trap entfernt nur zurückgelieferte eigeneContainerIDs; keineImages/Dockerdaemon-/Hostpackageänderung. LogsArtifacts temporär, kein weiterer Forschungsbericht. Pipeline enthält wederCoverage nochMultiDistro/Hardware, behauptet keinenREP2004QualityLevel. AP07 bleibt wegen ursprünglichem tatsächlichem Remoteabnahmekriterium IN PROGRESS: IMPLEMENTED / NOT REMOTELY VERIFIED. Weitere AP08..AP10-Arbeit ist unabhängig freigegeben und folgt; keinPush zur Erfüllung des Remote-Kriteriums erzwingen.


### 18.7 AP08 – Dokumentationsabnahme

Nutzungsanleitungen, Architektur, Topics/Actions/TF/QoS/Konfiguration/M01-Migration und bekannte Grenzen abgeglichen; CONTRIBUTING und MAINTENANCE trennen Beiträge, vorhandenen Devstand0.0.1, ungarantierteAPI/ABI/Support, Projekt-EOL-Entscheidung und spätere Releases. Drei Forthcoming-Changelogs werden installiert, keine Releaseversion/keinTag gewählt. Nach tatsächlicher Änderung neuer `/work/maintenance1` normalerCopybuild plus Vollsuite225PASS/0FAIL/0SKIP, docutils+Installbytevergleich+MetadatencheckPASS. Alte wissenschaftliche Vorleistungen bleiben im zentralen Protokoll; keine zusätzliche Forschungsberichtdatei angelegt. Umfang AP08 aktuell VERIFIED, Distributions-/Releaseergebnisse werden fortgeschrieben.


### 18.8 AP09 – aktuelle Distributionsmatrix und belegte Grenzen

Stichtag15.10.2026. Offizieller [ROS-Releaseindex](https://raw.githubusercontent.com/ros2/ros2_documentation/rolling/source/Releases.rst) nennt HumbleEOLMai2027, JazzyMai2029, KiltedDezember2026 und aktuelle stabile LyricalMai2031. Lyrical erschien22.05.2026, Rolling bleibt Entwicklungslinie. [REP2000](https://raw.githubusercontent.com/ros-infrastructure/rep/master/rep-2000.rst) nennt beiKilted nochNovember2026 und beschreibtRollingplattform nurStandMai2025; Quellen widersprechen sich beimKiltedmonat. Kein neuesProjekt-Supportversprechen daraus ableiten. Plattformen der tatsächlich gepinnten offiziellen [Dockerimages](https://raw.githubusercontent.com/docker-library/official-images/master/library/ros) und reale /etc/os-release-/Pythonabfragen sind unten getrennt erfasst; dessenRollingimage nutzt inzwischenResolute.

| ROS | Ubuntu / Python (tatsächlich oder Quellenumfang) | rosdep | Build | Tests | Installation | Gesamtstatus |
|---|---|---|---|---|---|---|
| Humble | 22.04.5 /3.10.12 amd64, nativ imContainer |32Keys einzelnPASS, install/checkPASS |3PaketeCopyPASS |225PASS/0FAIL/0SKIP |169SourcefreieFällePASS, readonly |VERIFIED im definierten Umfang, finalerLauf bestanden18.10 |
| Jazzy |24.04.5 /3.12.3 amd64, nativ imContainer |Gesamtinstall/checkExit1, Open3Dnotavailable |NurInterfacepaketPASS; Planner/Preproc nichtgebaut |5Interfacechecks+CDRPASS; keinePlanner-Vollsuite |Interfaceinstalliert; keineSourcefreieGesamtabnahme |BLOCKED fürGesamtpaketsatz; InterfacePARTIALnachgewiesen |
| Kilted |Noble24.04 /Python3.12 lautREP; keinContainerlauf |SystemregelNoble:blockiertOpen3D |NOT TESTED |NOT TESTED |NOT TESTED |BLOCKED Dependencyregel / API NOT TESTED |
| Lyrical |26.04.1 /3.14.4 amd64, nativ imContainer |install/checkExit0 ohneSkip/Pip |3PaketeCopyPASS |colcon testExit5; nur5CMakePASS, direktePython218PASS/2LintFAIL/0SKIP |3PaketeInstall/Imports/CDRPASS; keinSourcefrei-Lauf |PARTIAL; keineSupport-/Gesamttestfreigabe |
| Rolling |aktuellesoffiziellesImageResolute; Python hierNOT DETERMINABLE mangelsLauf |WildcardregelOpen3DaufApt; echteInstallationNOT TESTED |NOT TESTED |NOT TESTED |NOT TESTED |NOT TESTED, optionalesEntwicklungsziel |

Eigene temporäre Jazzy-/Lyricalcontainer: `e1af4a3c358a886fe83f66a5401a378c311596b83af7cb8a92c3a023ce5cc7ec` / `49f933375b81d7322586d5740863ec573bccd3558e529c2f32af8b656780bc47`, labelcodex.task=r3d-v4-release, SourceRO, lokaleisolierteDomains229/230, keinHostnetz/Privileged/Hardware. Images `ros:jazzy-ros-base@sha256:066420e07f60aa18262f2479981def87ebcfcec42eefb0c0c57c4a46098348ca` und `ros:lyrical-ros-base@sha256:f79cd486fa218596747c45d00ca42101b0303fc6d94ed5adb72145cd6f54b86c`. BenutzerUID1000 beiBuild/Tests, Apt/rosdep nurContainer. KeinePython3.14-Host-Conda mitLyricaltest verwechseln. RohdatenProbe-/Interface-/Build-/Pytestjson+xUnit temporär/tmp/r3d-v4-release; relevanteErgebnisse dauerhaft hier.

Tatsächlich ausgeführt jeContainer: `rosdep update --rosdistro <jazzy|lyrical>`, `rosdep install --from-paths /r3d-source --ignore-src --rosdistro <distro> -y`, `rosdep check --from-paths /r3d-source --ignore-src --rosdistro <distro>`, `rosdep resolve python3-open3d --rosdistro <distro>`, `apt-cache policy python3-open3d python3-numpy python3-scipy python3-networkx`. Jazzy zusätzlich nurInterfaceDependenciesund `colcon build/test --packages-select r3d_interfaces; colcon test-result --verbose`, jeweils0. Separat offizielleAptpakete nav2_msgs/sensor_msgs_py/SciPy/NetworkX fürAPIanalyse installiert, dadurchGesamtrosdepblocker nichtgelöst. Lyrical regulär `colcon build/test --packages-up-to r3d_planner; colcon test-result --verbose`; build0/test5/result0. **Ein Exit0 von test-result mit nur5CMakefällen ist hier ausdrücklich kein bestandener Gesamttest.** DirektePython-Diagnose ausje `/work/lyrical_full1/src/<paket>`: `python3 -m pytest -p no:cacheprovider --basetemp=<eigenerTemp> --junitxml=<eigeneXML> test -q`, beideExit1 durchFlake8. ErsterDiagnoseversuch falscherCWD korrigiert; keine Tests entfernt/geskippt oderLintregelnabgeschwächt.

**Dependencybefund:** Aktuelle offizielle [rosdep-Regel](https://raw.githubusercontent.com/ros/rosdistro/master/rosdep/python.yaml) enthält fürOpen3D explizitnoble:null, sonstUbuntu-WildcardApt. JazzyApt zeigt `python3-open3d Candidate:(none)` in denkonfiguriertenoffiziellenNoblequellen. Lyrical installiert dagegenAptOpen3D0.19.0-5build4, NumPy2.3.5, SciPy1.16.3, NetworkX3.2.1; alleImportsPASS. Jazzyseparat NumPy1.26.4/SciPy1.11.4/NetworkX2.8.8, keinOpen3D. [PyPI-Metadaten](https://pypi.org/pypi/open3d/json) belegen einePip-Veröffentlichung, keine hiergetestetePip-Lösung. Pipkeys sind laut [rosdistroReview](https://raw.githubusercontent.com/ros/rosdistro/master/REVIEW_GUIDELINES.md) keinWeg zumoffiziellenBinärrelease. LokalerSourcebuild/Vendorisierung könntenNoble untersuchen, brauchen Packaging-/Lizenz-/Transitivitätsprüfung undgesonderteStrategieentscheidung; nichtimplementiert. Lyrical beseitigt konkret dessenSystemdependencyhürde, beweist aberkeineGesamtportierung. KeineVersionspins/Manifests/Repos zurUmgehung geändert.

**APIvergleich:** TatsächlicheImports/Signaturen in beidenneuenTargets bestätigen ActionServer/cancel_callback/callback_group, MultiThreadedExecutor, LaunchNode namespace/remappings, TF2 lookup_transform mitTime/Duration und sensor_msgs_py.read_points. Letzteres bietetstrukturierteArrays/reshape_organized_cloud; eigenerfeldbewussterDecoder bleibtunverändert undbestehtLyrical-Funktionstests. [JazzyComputePathToPose](https://raw.githubusercontent.com/ros-navigation/navigation2/jazzy/nav2_msgs/action/ComputePathToPose.action) ergänzt gegenüberHumble error_code/error_msg. [Lyrical](https://raw.githubusercontent.com/ros-navigation/navigation2/lyrical/nav2_msgs/action/ComputePathToPose.action) ergänzt außerdemviapoints. Der aktuelleHumble-Vertrag fülltdieseZusatzfelder nichtgezielt; Viapoints werdennichtverarbeitet. Zielplattformvertrag mussFehlerzuordnung undViapoint-Annahme/Ablehnung gesondertfestlegen/testen. KeinevolleNav2-Kompatibilität ausbestandenenEinzelfällen ableiten. Lyrical result_timeout-Default10stattJazzy900Sekunden: bestehenderClient fragtsofortResultan, längereRetrieval-/Concurrencygrenzen nichtabgenommen.

**Build-/Testhürden Lyrical:** CMake3.8-Minimum wirdnochgebaut, neueCMakewarnt zurkünftigenEntfernung vonKompatibilität<3.10. Setuptools meldet `Unknown distribution option: tests_require`; installierterColconpytest-Matcher prüfttestDependencies ausSetuptools, findetkeinpytestundwähltsetup.py-test-Fallback (NO TESTS RAN). Manifestpytestistvorhanden, dasistkeinfehlendesAptpaket. NeuereFlake8plugins verlangenzusätzlicheImport-/Quote-/Classnewline-Regeln:57Preproc/95Planner-Befunde, beidePEP257/CopyrightPASS. 218direktePythonfällebelegenbegrenzteFunktionsverträglichkeit, keineColcon-/Gesamt-/Fehlercode-/Viapoint-/SourcefreieAbnahme. Zukunft: pytest-Metadatenkompatibilität (z.B. geprüfte extras_require-Testgruppe), Lintregeln überTargets abstimmen, Actionzusatzfelder explizitabgrenzen, dannvollenBuild+colcon+Sourcefreiheitwiederholen. KeineumfangreichePortierung oderDependenciesmigration in diesemAuftrag stillimplementiert.


### 18.9 AP10 – Release-Readiness am 15. Oktober 2026

Die Prüfung unterscheidet Source-Registrierung, Dependency-Auflösung, Release-Erzeugung und tatsächlich bereitgestellte Binärpakete. Ein bestandener lokaler Build ersetzt keinen dieser externen Schritte. Die Paketversion **0.0.1** ist konsistent und bleibt unverändert; **V4 ist ein Branchname, keine Version 4.0.0**. Die drei installierten Forthcoming-Changelogs sind vorbereitet, enthalten aber keine autorisierte endgültige Releaseversion oder ein Release-Datum.

Die offiziellen [Index-Anforderungen](https://raw.githubusercontent.com/ros2/ros2_documentation/humble/source/How-To-Guides/Releasing/Index-Your-Packages.rst) verlangen öffentlich verfügbaren Source, passende Namen, Lizenz und einen zielbezogenen Source-Eintrag zur externen Prüfung. Die drei Paketnamen erfüllen die lexikalischen Regeln aus [REP-144](https://raw.githubusercontent.com/ros-infrastructure/rep/master/rep-0144.rst); Format-3-Manifeste mit Maintainer, Beschreibung, Version, Dependencies und Buildtyp sind vorhanden und validiert ([REP-149](https://raw.githubusercontent.com/ros-infrastructure/rep/master/rep-0149.rst)). Die ROS-Index-Anleitung empfiehlt auch Rolling; diese Empfehlung macht erfolgreiche Rolling-Tests nicht automatisch zur Voraussetzung jeder einzelnen stabilen Source-Registrierung. Repo-ID und Source-Branch bleiben später ausdrücklich auszuwählen; eine URL-Vorlage ist keine ausgeführte Registrierung.

Am Stichtag wurden die offiziellen distribution.yaml-Dateien für [Humble](https://raw.githubusercontent.com/ros/rosdistro/master/humble/distribution.yaml), [Jazzy](https://raw.githubusercontent.com/ros/rosdistro/master/jazzy/distribution.yaml), [Kilted](https://raw.githubusercontent.com/ros/rosdistro/master/kilted/distribution.yaml), [Lyrical](https://raw.githubusercontent.com/ros/rosdistro/master/lyrical/distribution.yaml) und [Rolling](https://raw.githubusercontent.com/ros/rosdistro/master/rolling/distribution.yaml) gelesen und geparst: kein R3D-Repositoryname, keine drei R3D-Paketnamen in Release-Paketlisten und keine R3D-Planner-Source-URL gefunden. Das belegt den Umfang dieser aktuellen Datenbankprüfung, keine weltweite Namensreservierung und keine Abwesenheit beliebiger noch nicht indexierter Projekte. Externe Namens-/Source-Review steht aus. Es wurde kein Fork, Issue oder Pull Request angelegt und kein Git-Remote aktualisiert.

| Bereich | Erforderliche Bedingung / Art | Aktueller Zustand | Nachweis | Blocker | Nächste Maßnahme |
|---|---|---|---|---|---|
| Source-Veröffentlichung | Autorisierter, rechtlich freigegebener öffentlicher Stand | **NOT READY** | V4 lokal; keine Veröffentlichung in diesem Auftrag | Offene Rechte-/Artefaktfragen, keine Pushfreigabe | Rechte und konkreten Publikationsumfang entscheiden; später separat autorisieren |
| ROS Index / Source | Öffentlich prüfbarer Source-Ref, passende Metadaten/Namen/Lizenz; externe Review | **NOT READY** | Drei gültige Manifeste; vorhandene Lizenztexte; Datenbankprüfung ohne Treffer | Der geprüfte V4-Stand ist nicht veröffentlicht; Rechtsgate und Review offen | Freigegebenen Source-Ref bereitstellen, Ziel/Repo-ID festlegen, erst anschließend Source-PR |
| Humble-rosdep | Alle externen Zielschlüssel und gemeinsam bereitgestellte interne Pakete | **READY für lokalen Humble/Jammy-Sourcebuild** | 32 externe Keys einzeln aufgelöst; echte Installation/check; drei Pakete gemeinsam gebaut | Kein lokaler Keyblocker; veröffentlichte interne Pakete für Binärrelease fehlen | Bei späterem Release alle drei Pakete und Abhängigkeitsreihenfolge berücksichtigen |
| Jazzy/Kilted-rosdep | Reguläre Systempakete auf Noble | **BLOCKED** | Jazzy install/check Exit1, Open3D-Regel noble:null und kein Apt-Kandidat | Open3D im untersuchten offiziellen Noble-Paketsatz | Geeignete offizielle System-/Vendor-Strategie gesondert bewerten; kein Pip-Ersatzrelease |
| Lyrical-rosdep | Reguläre Systempakete auf Resolute | **READY für geprüfte Dependency-Installation** | Echte Installation/check Exit0 | Kein Dependencyblocker; Tests/API-Vertrag separat offen | Testintegration, Lints und neuen Actionumfang klären |
| Bloom | Freigegebene Version/Ref, geeignete Changelogs und Releaseorganisation/Track | **NOT READY** | Devversion und Forthcoming vorhanden; keine Releasekonfiguration | Rechts-/Public-Ref-Gate; Version/Datum/Ziel/Release-Repo/-Team/-Track nicht festgelegt | Organisatorische Entscheidungen, dann später autorisierter Bloom-Schritt |
| ROS Buildfarm | Akzeptierter Releaseeintrag, Ziel-Dependencies, tatsächlich erfolgreiche Jobs | **NOT READY** | Lokale Humble-Installation und Tests vorhanden | Kein Releaseeintrag/-Job; externe Abnahme fehlt; neue Targets zusätzlich offen | Nach Releasevorbereitung offizielle Jobs ausführen lassen und Ergebnisse prüfen |
| Debian-Binärpakete | Konkrete erzeugte Pakete, installierte Ressourcen und notwendige Begleittexte | **NOT VERIFIED / NOT READY für Lieferung** | Source-/Python-/ROS-Installressourcen geprüft | Kein Debian-Artefakt gebaut/abgenommen; konkrete native/transitive Bundlepflichten offen | Tatsächliche Debian-Artefakte, Inhalte und Rechte prüfen |
| Humble-Kompatibilität | Definierte Build-/Interface-/Installregression | **READY im geprüften technischen Umfang** | 225 vollständige Tests und169 Source-freie Tests; Schlusslauf18.10 | Keine Hardware-/Coverage-/Sicherheitsgarantie | Bekannte Einsatzgrenzen dokumentiert halten |
| Neue ROS-Targets | Eigener Build-, Test-, Install- und API-Nachweis | **PARTIAL / BLOCKED** | Matrix18.8 | Noble-Open3D; Lyrical-Testintegration/Lints und Actionzusatzvertrag | Ziel priorisieren, konkrete Korrekturen und vollständige Abnahme planen |
| Lizenzierung | Tatsächliche Distributionsrechte und passende Pflichttexte | **Technisch VERIFIED; Rechtsgesamtgate BLOCKED** | Root-/drei Paket-LICENSEs; SPDX; erhaltene OSRF-Notices;11.21 | Vertragsbefugnisse, historische Karten-Gitobjekte, konkrete Bundle-/Dateirechte | Individuelle Rechtsfragen und echten Artefaktumfang klären |
| Wartungsdokumentation | Zutreffende Nutzung, Änderungen und tatsächliche Zusagen | **READY für dokumentierten Devumfang** | README/INSTALL/Architektur/Config/KnownIssues, CONTRIBUTING/MAINTENANCE, drei Changelogs | Keine beschlossene langfristige Support-/stabile API-/ABI-Zusage | Solche Zusagen vor einem entsprechenden öffentlichen Versprechen festlegen |
| CI/CD | Projektkriterium: tatsächlicher Remote-Lauf zusätzlich zur Implementierung | **IMPLEMENTED / NOT REMOTELY VERIFIED** | Gleicher lokaler Dockerbefehl; zwei getrennte Container | V4 darf nicht gepusht werden; kein GitHub-Lauf | Erst nach späterer ausdrücklicher Freigabe Remoteprüfung, kein ungefragter Push |

**Bloom/Buildfarm-Vorbereitung:** Die offizielle [Erstrelease-Anleitung](https://raw.githubusercontent.com/ros2/ros2_documentation/humble/source/How-To-Guides/Releasing/First-Time-Release.rst) trennt Changelog, Versionsentscheidung und Bloom. Ein separates [Release-Repository und Release-Team](https://raw.githubusercontent.com/ros2/ros2_documentation/humble/source/How-To-Guides/Releasing/Release-Team-Repository.rst) sowie ein [distributionsbezogener Track](https://raw.githubusercontent.com/ros2/ros2_documentation/humble/source/How-To-Guides/Releasing/Release-Track.rst) sind spätere Organisationsschritte. Rolling verlangt in der gelesenen Anleitung ros2-gbp; für stabile Distributionen wird es empfohlen. Hier wurde nichts davon angelegt, kein Token angefordert und kein Releasebefehl ausgeführt. Nach einem später autorisierten Release müssen Jobresultate und die tatsächliche Synchronisierung/Installation der Debian-Pakete gesondert kontrolliert werden.

**Rechtliche Grenzen:** Die vorhandene Apache-2.0-Entscheidung wird nicht neu eröffnet. Arbeitgeber-/Vertragsbefugnisse, unklare Ressourcen-/Bytecode-Provenienz, historische Karten in Gitobjekten und Rechte/Pflichttexte eines konkreten Binärbundles bleiben aus11.21 offen. Eine bloß extern installierte Library ist nicht automatisch Teil eines eigenen Sourcepakets. Die LiDAR-Modification-Notice wurde nur dokumentarisch ausgearbeitet; externe Übernahme und konkrete Deployment-/Bundle-SHAs sind weiterhin nicht verifiziert. Kein externes LiDAR-Repository wurde hier geändert. Der datenfreie aktuelle Tree beweist keine datenfreie Git-Historie.

**Abgrenzung von Anforderungen:** Geklärte Rechte, gültige Paketmetadaten, öffentlicher prüfbarer Source und externe Review sind Source-/Indexgrundlagen. Zielauflösbare Dependencies, passende installierte Inhalte und tatsächliche Release-/Buildfarm-/Debianergebnisse betreffen die Binärveröffentlichung. M02, mehr Algorithmusabdeckung, Remote-CI und Unterstützung zusätzlicher Distributionen sind konkrete Projektziele bzw. Qualitätsnachweise, keine erfundenen allgemeinen ROS-Index-Pflichtdateien. CONTRIBUTING und Wartungshinweise sind nützlich; dedizierte SECURITY-/Issue-/PR-Templates oder eine QUALITY_DECLARATION sind nicht pauschal Voraussetzung jeder Registrierung. [REP-2004](https://raw.githubusercontent.com/ros-infrastructure/rep/master/rep-2004.rst) dient hier zur Einordnung von Versionpolitik, Change-Control, API/ABI, Dokumentation, Tests/Coverage, Dependencies, Plattformen und Security. Ein Quality Level wird nicht beansprucht: insbesondere fehlen vollständige Coverage-, stabile API-/ABI-, Remote-CI- und umfassende Plattform-/Sicherheitsnachweise.

**Nächste abhängige Schritte:** Zuerst offene Rechte und Publikationsumfang entscheiden. Parallel kann M02 nach separater Freigabe mit dem Vorschlag18.2 bearbeitet werden. Danach den zugesagten Zielvertrag, insbesondere eine neuere ROS-Zielplattform und deren Dependency-/Action-/Teststrategie, festlegen und vollständig prüfen. Anschließend endgültige Releaseversion/Changelog, öffentlichen Source-Ref und autorisierten Remote-CI-Lauf vorbereiten. Erst danach externe Source-Review, Releaseorganisation/Bloom und tatsächliche Farm-/Debianabnahme. Kosmetik oder zusätzliche Templates schließen keine grundlegenden Gates.


### 18.10 Abschließende Regression und Schutzprüfung – V4-028

Nach allen Änderungen an Produktion, Paketintegration und Installationsregeln wurde erneut exakt `bash scripts/ci/run_humble.sh` ausgeführt, Prozess-Exit0. Build und Runtime installierten/checkten ihre Dependencies tatsächlich und ohne Skipkeys; beide rosdep-Checks meldeten „All system dependencies have been satisfied“. Tatsächliche Schlussausgaben:

```text
METADATA_XML_YAML_SYNTAX_DOC_STRUCTURE_PASS
Summary: 225 tests, 0 errors, 0 failures, 0 skipped
169 passed, 2 warnings in 5.83s
CI_LOCAL_BUILD_AND_SOURCEFREE_PASS
```

Das sind zwei getrennte frische Humble/Jammy-Containersysteme mit UID1000, FastDDS, Domains231/232 und lokaler ROS-Kommunikation. Die Runtime erhält ausschließlich die schreibgeschützte Installation am ursprünglichen Buildprefix, sechs Testdateien, drei Manifestkopien und den Helper; Source- und Buildtree sind nicht gemountet und werden ausdrücklich als abwesend geprüft. Der Container-Exitcode wird zusätzlich kontrolliert, damit docker start/tee keinen Fehler verdeckt. Die erste Pipelineprüfung und AP08-Copyprüfung sind separate frühere Nachweise. Der Schlusslauf ist kein GitHub-Actions- oder Buildfarm-Lauf.

Die Artefaktprüfung vergleicht16 aktuelle Pythonmoduldateien und sechs Runtime-Testdateien byteweise sowie installierte Manifeste, vier Lizenztexte einschließlich Rootvergleich, Changelogs, Interface-README/-Schema, YAML und vier Launchdateien mit dem Repository. Alle Vergleiche bestehen; die Installation enthält keine PCDs. Metadaten/XML/YAML/Python/Markdownstruktur wurden erneut erfolgreich geprüft. Der Check ist strukturell, keine vollständige manuelle Prüfung jedes externen Dokumentationslinks. Deprecation-Warnungen aus NetworkX/ament bleiben sichtbar; kein NumPy/SciPy-Mischversionsfehler in der Humble-Aptumgebung. Die zwei Runtime-Warnungen sind keine ausgeblendeten Failures.

Baseline und Eingang bleiben Vorfahren von V4. Alle übrigen lokalen Branches/Remote-Tracking-Refs, Tags und die Git-Konfiguration sind unverändert. Das historische PDF hat weiterhin SHA-256 `8c3603ec2dac85c5cabcca7ae7e85c8d8c709663fa02fabd09039274a2b35383`; Root-/ursprüngliche Paket-LICENSEs bleiben bytegleich, das neue Interfacepaket trägt denselben Text. V4-001..019 und die gesamten22 Lizenz-Unterkapitel sind identisch mit dem Eingang. Die sechs OSRF-Noticeblöcke und neun alten versionierten PYC-Dateien bleiben unverändert. Fünf lokale aktuelle Branch-Trees sind PCD-frei; historische Gitobjekte sind nicht umgeschrieben.

AST-/Byteprüfungen bestätigen erhaltene Preprocessing-, Graph-, A*-Berechnungen und Filtergeometrie. Beim A* ist ausschließlich der optionale kooperative Cancelcheck hinzugekommen. Follower-Obstaclecallback bleibt unverändert; in der Kontrollberechnung sind ausschließlich die freigegebene Flagquelle und das gemeinsame Leeren der Arrays geändert. Kein M02-Monitorparameter und keine Sensor→Base-Stopüberwachung wurden implementiert.

Die drei eigenen Analysecontainer wurden anhand exakter IDs und Aufgabenlabel kontrolliert, dann gestoppt/entfernt. Zuvor wurden readonly-Source, kein privilegierter Modus, kein Hostnetz und keine Hardware-Gerätefreigabe verifiziert. CI-Container wurden durch die eigene ID-basierte Trap entfernt. Keine fremden Container oder Images wurden gelöscht; Host-Apt/Pip/Conda und externe Projekte bleiben unangetastet. Im Repository sind85 Dateien versioniert. Rohlogs/xUnit/Hashvergleiche liegen temporär unter `/tmp/r3d-v4-release` und `/tmp/r3d-ci.5ynwiewN`; dauerhafte relevante Befunde und Exits stehen hier. Abschließende reine Git-/Schutzkontrolle nach dem Protokollcommit gehört zur Abnahme; dessen SHA wird über den eindeutigen Subject aufgelöst.

### 18.11 Konsolidierter M01-Vertrag und verbleibender M02-Vorschlag

**M01 ist implementiert.** `r3d_interfaces/msg/PathWithMetadata` enthält `nav_msgs/Path path` und `bool[] narrow`. `narrow[i]` gehört ausschließlich zu `path.poses[i]` derselben Nachricht; die Längen müssen übereinstimmen. Pfad- und Pose-Header stimmen einschließlich Frame und Zeitstempel überein. Positionen sind endlich, Quaternionen normiert. Die Orientierung beschreibt die XY-Pfadrichtung; bei fehlender horizontaler Richtung wird eine gültig normalisierte Zielorientierung verwendet. Graphpositionen und Klassifikationen werden dadurch nicht geändert.

Der Planner stellt denselben geometrischen Path auf `/global_path`, innerhalb `/global_path_metadata` und als erfolgreiches Actionresult bereit. `/global_path` bleibt `nav_msgs/Path`; generische ROS-Verbraucher brauchen das Metadatenpaket nicht zum Lesen dieses Topics. Eine Lieferung über mehrere Topics ist jedoch nicht atomar: Reihenfolge und Beobachtungszeit können sich unterscheiden. Deshalb koppelt der Follower keine zwei Topics über Zeitstempel, sondern übernimmt ausschließlich die vollständige Metadatennachricht. Das verhindert eine Zuordnung alter Flags zu einem neueren Pfad auch bei gleichen oder zurückgesetzten ROS-Zeitstempeln. Die Nachricht definiert keine globale Goal-ID oder Multi-Planner-Arbitration.

Metadaten nutzen reliable/transient-local/depth1; der Follower verwendet ein kompatibles Profil. Ein nachträglich startender Follower erhält den zuletzt vom noch vorhandenen Publisher gehaltenen Pfad mit Flags. Das ist kein Hindernisfrische- oder Bewegungsfreigabenachweis. Ungültige Metadaten löschen Pfad und Flags gemeinsam; die bestehende Kontrollschleife erzeugt dann Nullbefehle. Ein neuer gültiger Pfad ersetzt beide Arrays gemeinsam in der serialisierten Callback-Ausführung. Zielerreichung löscht beide. Die Engstellengeschwindigkeit liest den zugehörigen Flagindex, keine Quaternion. Die 15 Metadatenregressionen prüfen unter anderem CDR, Längen/Header/Frame/Geometrie, Ersetzung/Verwerfen, Engstellengeschwindigkeit, Late-Join und tatsächliche Gleichheit von Standard-Path, Metadaten-Path und Actionresult.

Die Migration erfordert gemeinsam aktualisierte Planner, Follower und Interfaceinstallation. Externe alte Narrow-Decoder müssen auf das neue Topic wechseln; es gibt keinen Legacy-Decoder oder eine zweite versteckte Flagkodierung. Die bisherigen Standardtopicnamen bleiben am Root erhalten; opt-in Namespace und explizites ROS-Remapping sind geprüft. Ein Namespace präfigiert keine TF-Frame-IDs.

**M02 bleibt unimplementiert.** Eine obligatorische Hindernisquelle würde bei ausgeschaltetem lokalen Filter ohne externen Producer den Follower dauerhaft stoppen. Der Vorschlag in18.2 trennt daher die optionalen Filter- und Monitor-Schalter. Bei aktiviertem Monitor wird nur mit aktuellem gültigem Eingang und passender TF am Messstempel gefahren; fehlen Daten, sind sie zu alt, ungültig oder nicht transformierbar, ist ein Null-Twist vorgesehen. Deaktivierter Monitor erhält das bisherige Verhalten. Timeout, zulässige Zeitabweichung, TF-Wartezeit, Start-/Fehler-/Wiederanlaufzustände und synthetische Tests sind vorgeschlagen, noch keine akzeptierten Konfigurationsfelder. Die bestehende Hinderniscallback-Logik bleibt byte-/AST-semantisch erhalten. Radiuslücke0.65m Filter gegenüber0.6m Follower, Sensorversatz und fehlende Cliff/Stair-Verbraucher bleiben ausdrücklich offen. Der Vorschlag ist keine Sicherheitszertifizierung und wartet auf gesonderte Freigabe.

### 18.12 Wissenschaftliche Abschlussbewertung und Vorher/Nachher

Vergleichsreferenz bleibt **c65642fe56015556f696364a724cb5b976a27888**. PCD-Verarbeitung, Voxelisierung, Boden-/Clearance-/Treppenanalyse, RGB-Ausgabe, Graphrekonstruktion und A*, Odometry/TF, RViz, lokaler Filter, Follower, strikte zentrale YAML, Robotprofile und vier Launchdateien waren vorher vorhanden. Das sind keine im Forschungsprojekt neu entwickelten Navigationsalgorithmen. Der historische Baselinebericht enthält20 parametrische Funktionstestfälle und Lintertemplates. Frühere V4-Schritte erweiterten diese Grundlage auf86 und anschließend171 Fälle; diese Stände bleiben datierte Vorleistungen der jeweiligen Schritte.

Der konkrete Eingang dieser Fortsetzung war **11d594a**, bereits171 vollständige und120 Source-freie Tests. Neu hinzugekommen sind49 Pythonfälle (15 Metadaten,14 Action,20 Komposition) sowie5 CMake-Paketprüfungen. Damit umfasst die aktuelle Humble-Suite225 Tests; der Source-freie Teil169. Die ursprünglichen171 Fälle wurden nicht gelöscht oder übersprungen; die Root-Graph-Erwartung des bestehenden Launchtests wurde begründet auf den Root-Namespace beschränkt, damit neue Namespace-Tests keine falschen Mehrnode-Befunde erzeugen. Die Zahlen zählen parametrische Fälle und Lints, keine Prozentabdeckung. Sie begründen weder eine vollständige Algorithmusprüfung noch ein REP-2004-Quality-Level.

| Technischer Bereich | Historische Baseline | Implementierte V4-Verbesserung | Messbarer Nachweis / Grenze | Status |
|---|---|---|---|---|
| Lizenzierung | Keine vollständige Projektlizenzdatei, Manifest-TODO und ungeklärte Karten | Autorisierte Apache-Texte/Header/Metadaten; aktive Karten entfernt; Fremdnotices erhalten | Lizenzmitnahme/Hashes; Rechts-/Git-Historien-/Bundlefragen bleiben | Technisch VERIFIED, Rechtsgesamtgate BLOCKED |
| Paketmetadaten | Zwei Manifeste, Version/Description widersprüchlich | Konsistentes0.0.1 und zweckgebundene Metadaten; zusätzliches Interfacepaket | Drei validierte Manifeste; keine neue Releaseversion | VERIFIED technisch |
| Dependencies | Unvollständige direkte Deklarationen und Skip-Anleitung | Direkte rosdep-Keys, interne Pakete und Test-/rosidl-Abhängigkeiten |32 externe Humble-Keys; tatsächliche Installation/check | VERIFIED Humble; andere Ziele getrennt |
| Installation / Daten | Copy-Konfiguration abgewiesen; Sourcekarten und Ausgabe neben Input | Normale Share-Auflösung, externer Override, getrennte exklusive Ausgabe, eigene Karten | Normale kopierte Installation und Source-freier readonly-Test, keine PCDs gebündelt | VERIFIED im geprüften Umfang |
| ROS-Nachrichten | Engstellenflag als ungültige Quaternion | Gültiger Standard-Path und atomarer typisierter Pfad mit Flags |15 Metadatenfälle und native Gleichheits-/Geschwindigkeits-/Late-Join-Tests | M01 VERIFIED |
| PointCloud2 | Gepacktes XYZ vorausgesetzt | Feld-/Stride-/Endian-bewusster gemeinsamer Decoder |83 Cloudfälle; Input bleibt unverändert; Sensorachsen bleiben Integrationsvertrag | VERIFIED Decoder |
| Action | Begrenzte Validierung, Cancel-/Zeitsemantik unvollständig | Endliche gültige Posen, Fehler/Cancel und monotone Planungsdauer |14 neue echte ROS-Actionfälle; bestehende A*-Berechnung erhalten | VERIFIED Humble-Vertrag; keine volle Nav2-Zusage |
| TF / RViz | Odometry-/TF-Basis bereits vorhanden | Weitere ungültige TF-/RViz-Werte abgewiesen; begrenzte Serverwartezeit | Synthetische native TF-/RViz-Regression; kein neuer Sensor→Base-Monitor | Implementierter Umfang VERIFIED |
| Namespace / QoS | Teilweise absolut gekoppelte Namen und inkompatibles Sensorangebot möglich | Opt-in Namespace/relative Profile/Remaps; SensorData-Eingangsprofil |20 neue Kompositionsfälle insgesamt; alte Rootnamen erhalten | VERIFIED im getesteten Umfang |
| Follower | Engstellenfahrt und einfache Hindernisprüfung vorhanden | Metadateneingang validiert und eindeutig zugeordnet | Isoliertes Kommandotopic; keine Hardware; M02 unverändert | M01 VERIFIED, Überwachung zurückgestellt |
| Tests / Qualität | Funktionstests und Lintertemplates vorhanden | Gezielte Regressionen und aktive Python-/CMake-Lints |225 vollständige /169 Source-freie Humblefälle; keine Coveragequote | VERIFIED Umfang |
| CI | Keine Pipeline | Gleicher gepinnter Zwei-Container-Befehl lokal und im Workflow | Lokal tatsächlich reproduziert; kein GitHub-Remote-Lauf | IMPLEMENTED / NOT REMOTELY VERIFIED |
| Dokumentation / Wartung | Umfangreiche vorhandene Anleitungen | Aktuelle Verträge, Migration, Contributor-/Wartungsgrenzen und drei installierte Changelogs | Struktur-/Link-/Metadaten-/RST-/Installprüfungen; keine Support-SLA erfunden | VERIFIED aktueller Devumfang |
| Distributionen | Humble als historisches Ziel | Reale Humble-, Jazzy- und Lyrical-Prüfung, aktuelle Quellenmatrix | Jazzy Open3D blockiert; Lyrical Build/218 Pythonfälle PASS,2 LintFAIL und Colcon-Problem | PARTIAL für neue Targets |
| Releasevorbereitung | Kein hier belegter Releaseabschluss | Separate Index/rosdep/Bloom/Farm/Debian-Checkliste | Öffentlicher V4-Ref, Rechte, endgültige Version und externe Abnahme offen | NOT READY |

Die nachgewiesene Verbesserung liegt in überprüfbaren ROS-Verträgen, installierbaren Ressourcen, vollständigerer Dependency-Deklaration und wiederholbarer lokaler Qualitätssicherung. Reproduzierbarkeit ist auf die protokollierten Images, Plattformen und konkreten Aptstände begrenzt: Die Basisimages sind gepinnt, Apt-/rosdep-Repositories sind keine eingefrorenen Zeitsnapshots. Ein späterer Lauf kann andere kompatible Updates erhalten. Mehr Tests sind ein überprüfbarer Umfangszuwachs, kein allgemeines Qualitäts- oder Sicherheitsmaß.

Interoperabilität ist unter Humble durch Standardgeometrie, typisierte Metadaten, Remapping/Namespace und Sensor-QoS konkret verbessert. Die Source-freie Prüfung beseitigt belegte Checkout-Abhängigkeiten, beweist aber keinen beliebigen Umzug des Installationsprefixes, keine Debian-Lieferung und keine Hardwareintegration. Moderne Abhängigkeiten sind nicht pauschal problematisch: Lyrical kann sie regulär installieren; dessen konkrete Test-/Lint-/Actionvertragsgrenzen bleiben trotzdem offen. Die rechtliche Bewertung ist technisch nicht entscheidbar. Öffentliche Releasefähigkeit bleibt durch die benannten Gates eingeschränkt.

Die beauftragte M01-Implementierung und der M02-Analyseauftrag sind erfüllt. Der ursprüngliche Gesamtumfang AP05–AP10 wird wegen zurückgestelltem M02, fehlendem autorisiertem Remote-CI-Lauf, nicht vollständig abgenommenen neuen Distributionen und offenen Rechte-/Releasegates **nicht als vollständig technisch abgeschlossen** ausgegeben. Weitere Entscheidungen und Arbeiten bleiben nachvollziehbar abgegrenzt; aus diesem Bericht folgt keine neue Implementierungs-, Push- oder Motionfreigabe.


### 18.13 Test-, Commit- und Arbeitspaketübersicht

| ID | Bereich / tatsächlicher Befehl | Ergebnis | Status / Grenze |
|---|---|---|---|
| T97 | Eingang, Git-/Datei-/Manifestinventar, geschützte Hashes | V4 bei11d594a sauber,67 Dateien; Baseline vorhanden; Schutzsnapshot | VERIFIED Eingang |
| T98 | M01 `/work/m01_2`: rosdep install/check, normaler colcon build/test/test-result |191PASS/0FAIL/0SKIP;15 neue Pythonfälle+5 CMakechecks | VERIFIED M01; spätere Änderungen separat |
| T99 | Optionalfilter-/Followeranalyse, konkreter Monitorvorschlag18.2 und Codevergleich | Kein M02-Timeout oder Sensor→Base-Monitor implementiert | VERIFIED Analyse; Implementierung zurückgestellt |
| T100 | `/work/action1`: colcon build/test/test-result und echte ROS-Actionclients |205PASS/0FAIL/0SKIP;14 neue Actionfälle | VERIFIED Humble-Vertrag |
| T101 | `/work/compose4`: colcon build/test/test-result, echte Namespaces/Remaps/QoS/TF/RViz |225PASS/0FAIL/0SKIP;20 neue Kompositionsfälle | VERIFIED; vorangegangene Harness-/Lintfehler inV4-023 ausgewiesen |
| T102 | Erster exakter lokaler `bash scripts/ci/run_humble.sh` |225 volle+169 Source-freie Fälle PASS, Exit0 | Lokale Reproduktion VERIFIED; kein Remote-Lauf |
| T103 | AP08 `/work/maintenance1`: normaler Copybuild/Tests, Sharevergleich und docutils |225PASS/0FAIL/0SKIP; drei installierte Changelogs/RST PASS | VERIFIED Install-/Dokumentumfang |
| T104 | Native Jazzy-rosdep und Interfacepaket-Build/Test/CDR |Gesamtinstall/check1, Open3D fehlt; Interface5PASS+CDR | BLOCKED Gesamtpaketsatz; Interface geprüft |
| T105 | Native Lyrical-rosdep/build/colcon test/test-result |Install/check/build0; test5, nur5CMakefällePASS/result0 | FAILED vollständige Colcon-Abnahme; kein falscher GesamtPASS |
| T106 | Lyrical pytest aus jeweils eigenem Paketverzeichnis |218PASS/2Flake8FAIL/0ERROR/0SKIP; CDR PASS | PARTIAL; erster falscher Harness-CWD getrennt korrigiert |
| T107 | Fünf offizielle distribution.yaml geparst; aktuelle offizielle Index-/Releasequellen |Kein R3D-Treffer im beschriebenen Umfang; Readiness getrennt dokumentiert | VERIFIED Analyse; keine externe Review/Registrierung |
| T108 | Abschließender exakter lokaler CI-Befehl nach allen Code-/Installänderungen |225 volle+169 Source-freie PASS,0FAIL/0ERROR/0SKIP, Exit0 | VERIFIED Humble-Schlussumfang |
| T109 | Install-/Sourcebytes, Schema/YAML/Launch/Lizenzen; Git-/AST-/Event-/PDFvergleich |22Pythonvergleiche und Sharevergleiche PASS;85 versionierte Dateien | VERIFIED Schutz-/Identitätsumfang; keine Relokationsgarantie |
| T110 | Eigene drei Analysecontainer perexakterID/Label stoppen/entfernen; CI-Trap |Keine eigenen Analysecontainer übrig; keineImages gelöscht; Isolation geprüft | VERIFIED Cleanup |
| T111 | Finaler struktureller Check `PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B scripts/ci/check.py .`, `git diff --check` |Exit0, Struktur/Metadaten/Links PASS | VERIFIED lokal; kein umfassender externer Link-/Rechtscheck |

| Ereignis | Commit-SHA | Inhalt |
|---|---|---|
| V4-020/021 |410ed3aa2de53cccfa55935468d3283c887385b4 | M01 implementieren; M02 ausschließlich analysieren |
| V4-022 |35f547f6cbb681f1acb727af250a8b1dad34136c | Humble-Actionvalidierung und kooperative Cancellation |
| V4-023 |45d14766b0bd885182cf81284c99ef31b82d1d23 | Namespace/Remapping, RViz/TF-Eingänge, Sensor-QoS |
| V4-024 |2dd10975faa726c994cd75ed43c0a97eec61ab2f | Humble-CI und Source-freie lokale Reproduktion |
| V4-025 |be44bf4a9fe8a9a9fe86ead03552850b3017903f | Nutzer-/Wartungsdokumentation und installierte Changelogs |
| V4-026 |b91cdb909491aa511dde221cba156e4585aed400 | Tatsächliche Jazzy-/Lyrical-Untersuchung |
| V4-027 |aae71c37f4bb663ec408ca0f4487a5c747cda327 | Getrennte Release-Readiness und externe Gates |
| V4-028 | Subject `docs(v4): record final regression and research assessment`, Parent aae71c3 | Dieser Protokollabschluss; vollständige SHA über `git log -1 --format=%H --fixed-strings --grep='docs(v4): record final regression and research assessment'` bestimmbar |

| Arbeitspaket | Aktueller Abschlussumfang | Verbleibende Grenze |
|---|---|---|
| AP01 | Technische Lizenzimplementierung VERIFIED | Rechtsgesamtgate BLOCKED, keine erneute Lizenzwahl |
| AP02 | Drei konsistente Manifeste/0.0.1 und vorhandene Metadaten VERIFIED | Endgültige Releaseversion bleibt Entscheidung |
| AP03 | Humble32 Keys/Installation/check VERIFIED | Noble-Open3D; neuer Zielumfang separat |
| AP04 | Humble-Copy-/Sourcefrei-/Ressourcen-/Outputumfang VERIFIED | Keine beliebige Relokation/Debian-/Mehrplattformabnahme |
| AP05 | M01 und übrige implementierte ROS-Korrekturen VERIFIED | Gesamtumfang IN PROGRESS: M02 ausdrücklich zurückgestellt, Integrationsgrenzen bleiben |
| AP06 | Aktuelle Humble225/169 Regressionen VERIFIED | Keine umfassende Coverage-/Hardware-/M02- oder neuere Zielabnahme |
| AP07 | IMPLEMENTED; lokale Reproduktion VERIFIED | IN PROGRESS / NOT REMOTELY VERIFIED |
| AP08 | Aktuelle Nutzer-/Wartungs-/Protokolldokumentation VERIFIED | Keine erfundene SLA/API-/ABI-Stabilitätszusage |
| AP09 | Untersuchungsauftrag mit realen Nachweisen dokumentiert | Neue Ziele PARTIAL/BLOCKED, keine pauschale Supportfreigabe |
| AP10 | Aktuelle Checkliste/Analyse VERIFIED | IN PROGRESS; Index/Bloom/Farm NOT READY, keine Veröffentlichung |

Die nächste technische Entscheidung ist eine gesonderte M02-Freigabe auf Basis18.2 oder eine ausdrücklich andere Priorität. Rechtsklärung, Publikationsumfang und Ziel-/Releaseentscheidungen können davon getrennt vorbereitet werden. Ohne diese Entscheidungen werden weder Hindernisüberwachung noch neue Dependenciestrategie, Push, Release oder Hardwaretest automatisch ausgeführt.


## 19. M02 – freigegebene Implementierung ab15. Oktober 2026

### 19.1 Verifizierter Eingang und bestehende Architektur

Nutzerauftrag1cfa68bb gibt M02 ausdrücklich frei. EingangV4/04d080b ist sauber, Baseline und alle bisherigen Commits sind Vorfahren; Remotes/Worktrees unverändert. Keine AGENTS.md im relevanten gefundenen Umfang. Die komplette bisherige Entwicklung einschließlich17.4/18.2, M01-Vertrag, TF/QoS und früheren Tests ist Ausgangspunkt; alte Ereignisse und Lizenzanalyse bleiben unverändert. Neue IDs beginnen beiV4-029.

Follower empfängt PointCloud2 auf /local/filtered_obstacles, bisher reliable/volatile/depth10. Filterausgaben behalten Sensorheader, Follower wertet XYZ bisher unmittelbar anhand x_min<x<stop_distance und |y|<half_width aus, ohne TF/Messalter. obstacle_in_front startetfalse; leere gültige Wolke setztfalse. Kontrollperiode0.1s, Null-Twist bei fehlendem Pfad, Hindernis, fehlender/frischer globaler Pose oder Zielerreichung. M01-Pfade/Flags werden gemeinsam ersetzt; ungültige Metadaten löschen beide. Planner startet optional Filter/RViz, niemals den Follower; follower.launch.py startet ihn separat mit zentraler YAML/Robotprofil und R3D_CONFIG_DIR-Unterstützung. Externe geeignete Clouds waren bereits prinzipiell möglich; Best-Effort war amFollower bisher nicht kompatibel, obwohl Filtereingang schonSensorDataQoS nutzte.

### 19.2 Entscheidung vor Implementierung

Die Freigabe ergänzt den vorgeschlagenen Monitor, ohne den optionalen Filter zu erzwingen. Gruppe obstacle_monitoring (statt des noch nie implementierten Vorschlagsnamens obstacle_monitor) enthält enabled=false, timeout_sec=1.0, require_transform=true, topic=/local/filtered_obstacles. Kein bisher unterstützter YAML-Schlüssel wird umbenannt. Fehlende Gruppe verwendet Defaults; gelieferte Gruppe wird strikt validiert. require_transform=false bedeutet nurBaseframe akzeptieren, niemals fremde Koordinaten alsBase interpretieren. TFlookup zumMessstempel ohneWarten verhindert dasBlockieren desSingleThread-Executors; fehlendeTF stoppt, nächster neuer gültiger Eingang kann erholen. Die bisher nurvorgeschlagene TFwartezeit wird nicht alsunnötiger neuerParameter eingeführt. Futurestempel werdenohneToleranz abgewiesen.

Aktivierter Monitor verwendet zusätzlich zurROS-Messzeit eine monotoneEmpfangszeit und einenSteady-Controltimer, damit Pause/VerlangsamungvonSimzeit dieEmpfangsgrenze nichtaufhebt. Ein identischer erneut gesendeteralterMessstempel wirdnicht durchEmpfangszeit verjüngt. Zeitbasiswechsel und Rücksprünge invalidierenCaches; großeVorwärtssprünge relativzurSteadyzeit ebenfalls. Grenzen exakt:Alter<=Timeout istgültig, >Timeout stoppt. Überwachung deaktiviert erhält vorhandeneHindernis-/Pose-/Pfad-/Zielbedingungen unddenbisherigenROStimer.

BeimMonitor direkteungültigeClouds sofort verwerfen undNullbefehle auslösen; echteleereWolke mitgültigenXYZ/Layout/Header/TF kannfreigeben. BestehenderDecoder wirdweiterverwendet, Inputbytes bleibengleich. Nonfinite-onlyOriginalcloud darf derinterneFilter nichtalsfrischenleerenClearbefund weiterreichen; gezielteKorrektur vorAusgabeberechnung vorsehen, ohneFiltergeometrie/Schwellen neuabzustimmen. SensorblindeZone0.65m versusFollowerstop0.6m undCliff/Stair-Verbraucher bleibenexpliziteEinsatzgrenzen.


### 19.3 Verbindliche Zielentscheidung während M02

Der Nutzer beschränkt Entwicklung und Veröffentlichungsvorbereitung ausdrücklich auf **ROS2 Humble / Ubuntu22.04 Jammy / Python3.10**. Bereits geprüfte Systemabhängigkeiten bleiben der Zielvertrag. Jazzy, Lyrical und Rolling werden auf spätere Phasen verschoben; bekannte Befunde18.8 bleiben historische Recherche, keine aktuell zu schließenden Gates. Ein fehlender Multi-Distribution-Nachweis blockiert den angestrebten Humble-Release nicht.

AP07 bleibt eine Humble-Pipeline; lokale neue M02-Abnahme folgt, Remote-CI ohnePush weiterhinNOTREMOTELYVERIFIED. AP08 nennt nurHumble alsaktuellesZiel. AP09 ist fürdieseneingeschränktenUmfang zuverifizieren; keinePortierungsarbeiten/Dependency-Migration. AP10 bewertet Sourceindex/Bloom/Buildfarm aufHumble; Rechte, öffentlicherSourceRef, autorisierteReleaseversion undexterneAbnahme bleibeneigenständigeGates. M02/HumbleRegression/lokaleCI werdenfortgesetzt; keinandererBranch/Push/Release.


### 19.4 Kernabnahme V4-029 und Zielentscheidung V4-030

Neue62 Unit-/Konfigurationsfälle plus225Bestandsfälle bestehen imfrischen /work/core4:287PASS/0FAIL/0SKIP, build/test/test-result0. Der reine Validierungshelfer und die imROSbaum deklarierten readonlyParameter sindabgenommen; dieaktiveFollower-Stopintegration folgtV4-031. NochkeinSourcefreierM02-/Twist-/Gesamtimplementierungsnachweis. Zeitsprünge/Replay/TFwerdenmitkontrolliertenZeiten getestet; alteYAMLohneGruppe bleibtgültig. KeinJazzy/Lyrical/Rolling-Container oderPortierungsversuchdiesesAuftrags.

OffizielleHumblequellen: [Clock/JumpThreshold](https://raw.githubusercontent.com/ros2/rclpy/humble/rclpy/rclpy/clock.py), [NodeTimer/Parameter](https://raw.githubusercontent.com/ros2/rclpy/humble/rclpy/rclpy/node.py), [TFbufferlookup](https://raw.githubusercontent.com/ros2/geometry2/humble/tf2_ros_py/tf2_ros/buffer.py); Signaturen zusätzlich tatsächlich installiert geprüft. LookupTime0 würde latest bedeuten, deshalb werdenNull-Messstempelabgewiesen undMesszeitübergeben. Timer mitSteadyClock undJumpCallback sindinHumblevorhanden. JumpCallback bleibtkurz/nichtblockierend. [DDS-Domainbereiche](https://raw.githubusercontent.com/ros2/ros2_documentation/humble/source/Concepts/Intermediate/About-Domain-ID.rst) erklären deninitialenHarnessfehler241 außerhalb0..232; finaleKern-Domain91 liegtimsicherenBereich. KeineNetz-/Middleware-Hostkonfiguration geändert.
