# R3D-Planner V4
# ROS 2 Compliance Development

Stand: 14. Oktober 2026; fortgeführt bis V4-007 (historische PDF-Baseline versioniert). Dieses Dokument ist das einzige zentrale Entwicklungsprotokoll für V4. Es trennt den historischen Bestand, geplante Maßnahmen, tatsächlich durchgeführte Änderungen und deren Nachweise. Die Erstinitialisierung verändert ausschließlich dieses Dokument und legt den Branch V4 an. Sie enthält keine Implementierung der Arbeitspakete AP01 bis AP10.

## 1. Zielsetzung

V4 soll die bestehende funktionale R3D-Planner-Implementierung für eine nachvollziehbare öffentliche Bereitstellung im ROS-2-Ökosystem vorbereiten. Gegenstand sind Paketmetadaten, Dependency-Deklarationen und rosdep, Lizenz- und Datenrechte, installationsunabhängige Ressourcen, öffentliche ROS-Verträge, Tests, CI/CD, Nutzungsdokumentation und Releasevorbereitung. Beide Pakete behalten `ament_python` und setuptools. Eine CMake-Konvertierung ist ohne konkreten technischen Bedarf nicht vorgesehen.

PCD-Verarbeitung, Traversierbarkeitsanalyse, Graphrekonstruktion, A*, Navigationseinstiegspunkte und die V3-Integration sind Vorleistungen. V4 werden ausschließlich begründete und nachgewiesene Änderungen nach dem Baseline-Commit zugerechnet. Neue SLAM-/Mappingverfahren, der Ersatz des Planners, ein vollständiges Nav2-Redesign und neue Hardwaretreiber sind keine primären Ziele.

Die Initialisierung ist noch keine Freigabe für Codeänderungen. Gemäß Abschnitt 11 des Auftrags muss der initiale Plan zunächst vorgelegt werden; der Beginn des ersten Implementierungsarbeitspakets benötigt eine ausdrückliche Freigabe. Pushes, Releases und Pull Requests sind nicht beauftragt.

**Nutzerentscheidung vom 13. Oktober 2026:** „Überspringe die Lizenzierung vorerst, hierzu muss ich erst noch recherchieren“. AP01 wird deshalb zurückgestellt und als `BLOCKED` geführt. Diese Entscheidung erlaubt keine Annahme einer Projektlizenz und beseitigt keine Veröffentlichungshindernisse. Unabhängige technische Arbeiten können nach Planfreigabe beginnen. Es wird keine Lizenz ausgewählt, angewendet oder stillschweigend aus `setup.py` übernommen.

**Fortführung am 13. Oktober 2026:** Der folgende Auftrag hebt die Rückstellung ausschließlich für Recherche, Copyright-/Provenienzbewertung und wissenschaftliche Dokumentation auf. Der ergänzte Auftrag enthält die Entwicklererklärung Bastian Aumers und erlaubt ausdrücklich die Analyse der benannten externen LiDAR-Repositories. Verbindliche Lizenzwahl, Lizenz-/Headeranwendung, AP02/AP03-Implementierung und GitHub-/Remoteänderungen bleiben nicht freigegeben. V4-002/V4-003 dokumentieren diese neue Abgrenzung; die frühere Rückstellung bleibt historisch nachvollziehbar.

**Verbindliche Fortführung V4-004, 13. Oktober 2026:** Der neue Nutzerauftrag wählt **Apache License 2.0 (Apache-2.0)** für autorisierte eigene Softwarebestandteile von r3d_planner und r3d_preprocessor und gibt die technische Anwendung ausdrücklich frei. Root-LICENSE, zwei Manifest-Lizenzfelder und SPDX-Kommentarheader der 18 bereits zugeordneten eigenen Python-Dateien sind umgesetzt und statisch geprüft. Copyright-Attribution: **2026 Bastian Aumer**, vorhandene eigene Hinweise erhalten. Die früheren Rückstellungen/Recherchegrenzen oben und in V4-001 bis V4-003 beschreiben ihren damaligen Stand und sind durch diese gezielte Freigabe für AP01 überholt.

**Geltungsbereich der Root-LICENSE:** Der unveränderte Apache-Text gilt für die eigenen Softwarebestandteile, für die Bastian Aumer die erforderlichen Rechte besitzt. Die Datei ersetzt keine Bedingungen fremder Software. Die sechs OSRF-Testtemplates behalten ihre eigenen Apache-/Copyright-Hinweise; externe Libraries und LiDAR-Software behalten ihre Originallizenzen. **Die früheren beiden PCD-Karten wurden unter V4-005 aus dem aktiven Tree entfernt; keine Apache-Freigabe für historische Objekte.** Unbekannte Herkunft, Dokumentations-/Ressourcenrechte, ältere Bytecode-Artefakte sowie arbeits-/dienstvertragliche Befugnisse werden nicht durch einen Root-Text oder Manifesttag als geklärt dargestellt. Technische Lizenzimplementierung ist keine vollständige rechtliche Releasefreigabe. AP02/AP03 sind nicht begonnen; kein Push oder Release.

**V4-005, 14. Oktober 2026:** Die beiden alten PCD-Beispielkarten sind aus dem aktiven V4-Tree entfernt; beim Eingang waren beide Löschungen bereits im Working Tree vorhanden. Keine Ersatzkarten. Nutzer konfigurieren eigene PCD-Dateien, shipped maps-Werte sind leer. Die externe Konfiguration über R3D_CONFIG_DIR funktioniert auch ohne den ursprünglichen Source-Checkout. Historische Inventare, ältere V4-Einträge und das unveränderte PDF beschreiben weiterhin korrekt den früheren Kartenbestand. **Die Git-Historie enthält die alten Daten weiterhin**; ein vollständiger Git-Klon ist nicht mit einem datenfreien Tree-/Paketartefakt gleichzusetzen.

**V4-006, 14. Oktober 2026:** Technische AP01-Verifikation **VERIFIED** für Originaltext, 18 eigene SPDX-/Copyrightheader, Apache-Manifeste/Setup, erhaltene sechs Fremdtemplates, dokumentierte LiDAR-Trennung/Notice, datenfreien aktiven Tree und tatsächlich geprüfte Lizenzmitnahme in sdists, Wheels und Copy-colcon-Shares. Je Paket ist eine identische lokale LICENSE-Kopie hinzugefügt; Root-LICENSE unverändert. Keine vollständige rechtliche/transitive/Debian-/Buildfarm-Freigabe. Arbeitspaket AP01 insgesamt bleibt BLOCKED für individuelle Rechts-/Release-Gates, AP04/AP06/AP08/AP10 IN PROGRESS; AP02/AP03 NOT STARTED.

**V4-007, 14. Oktober 2026:** Das zuvor unversionierte historische PDF ist unverändert in Git aufgenommen: 33 Seiten, 298707 Byte, SHA-256 8c3603ec2dac85c5cabcca7ae7e85c8d8c709663fa02fabd09039274a2b35383. Frühere Angaben „unversioniert“ beschreiben den jeweiligen früheren Eingangszustand, keine aktuelle Anweisung. Historischer Inhalt/alte Kartendarstellung und Software-Lizenzgrenzen bleiben unverändert.

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
| Geplante Änderung | Nach gesondertem Auftrag nichtrechtliche Beschreibungen/URLs und Versionskonsistenz korrigieren; Maintainerdaten nicht erfinden/ersetzen; Apache-Lizenzfelder sind bereits durch AP01 gesetzt und keine neue AP02-Leistung |
| Priorität | P0 für Release-Metadaten, P1 für empfohlene Ergänzungen |
| Abhängigkeiten | Freigabe des ersten Implementierungsschritts; Lizenzabschluss hängt von AP01 ab, übrige Korrekturen nicht |
| Abschlusskriterien | Manifest-/Setup-Metadaten konsistent und geprüft; übrige Platzhalter technisch soweit zulässig entfernt; Lizenzdeklarationen aus AP01 erhalten, rechtliche Gesamtfreigabe separat offen |
| Aktueller Status | **NOT STARTED** |

### 4.4 AP03 - Dependencies und rosdep

| Feld | Planung |
| --- | --- |
| Ausgangsstand | ROS-/Science-Deklarationen und Apt-Anleitung vorhanden; direkter Importabgleich initial erstellt; Skip-Workaround dokumentiert |
| Probleme | B04-B06: direkte Dependencies fehlen, Systemschlüssel und Kategorien ungesichert; Python-TF2-Provider prüfen; install_requires ist kein vollständiger ROS-Distributionsvertrag |
| Geplante Änderung | Alle Runtime-/Launch-/Testimporte paketweise zuordnen; validierte System-/ROS-Schlüssel und passende Kategorien verwenden; unbenötigte Einträge nur nach Nachweis entfernen; Skip-Workaround aus finalem Verfahren ablösen |
| Priorität | P0 |
| Abhängigkeiten | Planfreigabe; AP02-Namens-/Metadatenkonsistenz; dokumentierte isolierte Humble-/Jammy-Umgebung ohne globale Reparatur; kein Lizenzentscheid für technische Schlüsselauskunft notwendig |
| Abschlusskriterien | Import-/Manifest-Abgleich vollständig; alle Keys für Humble/Jammy aufgelöst; Dependency-Installation und rosdep check ohne Skip erfolgreich, Befehle/Versionen protokolliert |
| Aktueller Status | **NOT STARTED** |

### 4.5 AP04 - Build und Installationsportabilität

| Feld | Planung |
| --- | --- |
| Ausgangsstand | setuptools, Marker-/Script-/Config-/Launchinstallation vorhanden; Source-/Symlink-Konfiguration wird bevorzugt |
| Probleme | B07/B08: Copy-Config absichtlich abgelehnt, Source-Kartenpfade, Karten nicht installiert, Ausgaben neben Eingabe; Conda-/System-Python-Abgrenzung erforderlich |
| Geplante Änderung | Normale Share-Ressourcenfindung, dokumentierter Override für Nutzerkonfiguration, strikte Validierung erhalten; installierte Eingaben von beschreibbaren Ausgaben trennen; Datenstrategie rechtlich separat klären |
| Priorität | P0 |
| Abhängigkeiten | AP03 für vollständigen Clean-Build; AP01 für öffentliche Mitlieferung der vorhandenen Karten, nicht für synthetische Installationsfixtures; AP06-Regressionen begleitend |
| Abschlusskriterien | Copy-Build/Install ohne Symlink; Tests bei nicht zugänglichem ursprünglichem Source-Checkout; Nodes/Launches/Config/Robotprofile auffindbar; Analyse schreibt ausschließlich in gewählten beschreibbaren Datenpfad; Source-/Override-Verhalten dokumentiert |
| Aktueller Status | **IN PROGRESS** - Nutzerkarten/externes Config-Verzeichnis und temporärer Copy-Build geprüft; vollständige Installations-/Ausgabeportabilität offen |

### 4.6 AP05 - ROS-Schnittstellen und Konfiguration

| Feld | Planung |
| --- | --- |
| Ausgangsstand | Standardnachrichten, Action, Service, Odometry/TF, QoS-Profile, YAML und vier Launches bereits vorhanden |
| Probleme | B09-B13: narrow-Quaternion, absolute/relative Namen, Cloud-Layout/Frameannahmen, Action-/QoS-/Integrationsgrenzen |
| Geplante Änderung | Jeweils eine belegte Vertragsgrenze korrigieren; alten/neuen Vertrag beschreiben; narrow-Metadaten getrennt von Orientierungen führen und alle internen Verbraucher migrieren; Namespaces/Remaps, Cloudfelder/Frames, Result-/Fehler-/Cancel-Verhalten prüfen |
| Priorität | P1; Kopplung an geplante öffentliche API vor Release klären |
| Abhängigkeiten | AP03/AP04 für reproduzierbare Ausführung; AP06 pro Vertragsänderung; AP09 bei distributionsverschiedenen Action-/Python-APIs |
| Abschlusskriterien | Normierte semantisch sinnvolle Orientierungen; erhaltenes Engstellenverhalten; konsistente interne Namen und Namespace-Test; Cloud-Varianten und Frames geprüft; Action-Erfolg/Fehler/Cancel entsprechend dokumentiertem Zielvertrag; keine stille API-Änderung |
| Aktueller Status | **NOT STARTED** |

### 4.7 AP06 - Tests und Qualitätssicherung

| Feld | Planung |
| --- | --- |
| Ausgangsstand | 20 funktionale Fälle, sechs Linter-Templates, strikte Config-/Posevalidierung; historische Ausführung berichtet |
| Probleme | B14: unvollständige Regressionen, skip/Legacy-Lint, Namenskonflikte bei gemeinsamer Pytest-Sammlung; keine neue Baseline-Laufzeitprüfung |
| Geplante Änderung | Bestehende Suite erhalten; gezielte Regressionen für jede V4-Änderung; alten Copy-Install-Ablehnungstest transparent migrieren; Importsammlung und sinnvolle Lints korrigieren; Algorithmusfixtures ergänzen, soweit für Regression nötig |
| Priorität | P1; Voraussetzung für Nachweis jedes technischen Schritts |
| Abhängigkeiten | Begleitet AP02-AP05; vollständige ROS-Läufe nach AP03; Copyright-Lizenzprüfung hängt von AP01 ab; keine Bewegung/hardwareabhängige Prüfung automatisch ausführen |
| Abschlusskriterien | Dokumentierte Auswahl und Abdeckung; neue Regressionen und Bestandsfälle erfolgreich; colcon test und test-result mit ausgewiesenen Skips; bekannte Restfehler nicht verstecken; keine historischen Ergebnisse als V4-Nachweis übernehmen |
| Aktueller Status | **IN PROGRESS** - bestehende 20 plus 23 neue Kartenpfadfälle geprüft; allgemeine Lint-/Coverage-/Regressionstiefe offen |

### 4.8 AP07 - CI/CD

| Feld | Planung |
| --- | --- |
| Ausgangsstand | Manuelle Build-/Testanleitungen, keine Pipeline |
| Probleme | B15: kein unabhängiger reproduzierbarer Build-/Install-/Testnachweis |
| Geplante Änderung | Zunächst Ubuntu 22.04/Humble: rosdep, Copy-Build, Tests, test-result, Lints und installierte Ressourcen prüfen; Code/Workflow ohne unbewiesene weitere Distro-Matrix vorbereiten |
| Priorität | P1 |
| Abhängigkeiten | AP03/AP04 und tragfähige AP06-Tests; Lizenzprüfung als offenes Release-Gate sichtbar halten |
| Abschlusskriterien | Workflow geprüft; tatsächlicher CI-Lauf samt Commit und Ergebnis nachweisbar; Konfigurationsdatei allein ist kein ausgeführter CI-Nachweis; Fernlauf nicht durch ungefragten Push erzwingen |
| Aktueller Status | **NOT STARTED** |

### 4.9 AP08 - Dokumentation und Wartung

| Feld | Planung |
| --- | --- |
| Ausgangsstand | Umfangreiche Bestandsdokumentation; historische PDF unverändert; dieses Protokoll wird initial angelegt |
| Probleme | Veraltete Installations-/Interfaceaussagen, keine festgelegte Versionierungs-/API-/Supportpolitik; Forschungsbeitrag muss vom Vorbestand getrennt bleiben |
| Geplante Änderung | Dieses Dokument kontinuierlich führen; bestehende Installation/Usage/Config bei Änderungen aktualisieren; passende Wartungszusagen im bestehenden Dokumentationsbestand festhalten; erforderliche Release-Metadaten separat, keine zusätzlichen Forschungsberichte |
| Priorität | P1 für korrekte Nutzung; P2/P3 für weitergehende Policies |
| Abhängigkeiten | Begleitet alle APs; Lizenztext nur nach AP01; konkrete Support-/API-Zusagen erst anhand AP06/AP09 |
| Abschlusskriterien | Nachvollziehbare Änderungs-IDs und Commitreferenzen, zutreffende Prüfberichte, reproduzierbare aktualisierte Nutzeranleitungen; dokumentierte Grenzen statt pauschaler Quality-Level-/ABI-Garantie |
| Aktueller Status | **IN PROGRESS** - Protokoll bis V4-006 mit Karten-/Regressions-/Lizenzartefaktnachweisen fortgeführt; laufende Entwicklung und Policies weiter offen |

### 4.10 AP09 - ROS-Distributionskompatibilität

| Feld | Planung |
| --- | --- |
| Ausgangsstand | Humble/Jammy/Python 3.10 als Ziel, generische rclpy-/Launch-/TF-Verwendung; keine belegte Jazzy-/Neuer-Matrix |
| Probleme | B15: tatsächliche saubere Humble-Ausführung nicht neu belegt; Abhängigkeiten und Action-/PointCloud2-APIs können distributionsabhängig sein |
| Geplante Änderung | Zuerst Humble reproduzieren; weitere Ziele ausdrücklich auswählen und getrennt testen; nur nachgewiesene Inkompatibilitäten korrigieren; keine vorsorgliche Portierung |
| Priorität | P1 für Humble; P2 für weitere freigegebene Ziele |
| Abhängigkeiten | AP03-AP06; CI kann später geeignete Matrixnachweise liefern |
| Abschlusskriterien | Zielbezogene Dependency-/Build-/Test-/Installnachweise mit OS/Python/ROS-Versionen; weitere Distributionen erst nach Ausführung als unterstützt bezeichnen |
| Aktueller Status | **NOT STARTED** |

### 4.11 AP10 - ROS Index und Releasevorbereitung

| Feld | Planung |
| --- | --- |
| Ausgangsstand | Source-Pakete und historische Git-Referenzen vorhanden; Index-/Bloom-Kriterien initial getrennt recherchiert; kein hier erzeugtes Release |
| Probleme | B01-B08/B16: ungelöste Rechte/Metadaten/Dependencies/Installation; Releaseversion, Changelogs, Zielbranch, Namenskollisionen und organisatorische Zuständigkeiten offen |
| Geplante Änderung | Readiness zielbezogen aktualisieren; zunächst Source-Registrierung und Binärrelease getrennt vorbereiten; notwendige Paket-Changelogs/Release-Metadaten erst bei passendem Stand; keine PRs/Pushes/Releases ohne neuen Auftrag |
| Priorität | P0 für offene Release-Gates; Umsetzung nach technischen Grundlagen |
| Abhängigkeiten | AP01-AP04 zwingend für belastbaren Abschluss; AP05/AP06 für vorgesehenen Produktvertrag; AP08/AP09 für Ziel-/Wartungszusagen; AP07 als Projektqualitätsnachweis |
| Abschlusskriterien | Geprüfte Checkliste, konsistente Version/Ref, vollständige Dependencies, funktionierender Copy-Install, geklärte Rechte; Veröffentlichung nur nach gesonderter Autorisierung und externer Bestätigung |
| Aktueller Status | **IN PROGRESS** - aktiver Kartenumfang und konkrete Lizenzmitnahme geprüft; historische Git-/Vertrags-/Bundle-/Metadaten-/Dependency-/Release-Gates offen; keine Publikation |

### 4.12 Abhängigkeitsgerechte Reihenfolge und nächste Freigabe

AP01-Lizenzentscheidung und beauftragte technische Lizenzimplementierung sind abgeschlossen. Offene Vertrags-, Karten- und konkrete Distributionsrechte sperren weiterhin die entsprechende Veröffentlichung, nicht jede unabhängige technische Arbeit. Die bereits begründete Apache-Wahl muss dafür nicht erneut recherchiert werden. Bei konkreten entgegenstehenden Hinweisen ist die betroffene Lizenzzuordnung zu stoppen und neu zu beurteilen.

Als nächster **gesondert zu beauftragender** Schritt bleibt AP02 (nichtrechtliche Beschreibungen, URLs, Versionskonsistenz), danach AP03 → AP04 → AP05 mit begleitenden AP06-Regressionen/AP08-Dokumentation. AP04/AP10 müssen auch den tatsächlichen Installations-/Binärumfang einschließlich Pflichttexten prüfen. AP07 folgt stabilen Grundlagen; AP09/AP10 benötigen eigene ausgeführte Nachweise. Keine automatische Aufnahme von AP02/AP03, kein Push und keine Releaseausführung nach diesem Auftrag.

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

## 7. Probleme und offene Entscheidungen

| ID | Beschreibung | Auswirkung | Erforderliche Entscheidung | Vorgeschlagene Lösung | Aktueller Status |
| --- | --- | --- | --- | --- | --- |
| O01 | Apache-2.0 verbindlich gewählt/technisch angewendet; Vertrags-/Befugnislage nicht unabhängig geprüft | Keine vollständige rechtliche Releasefreigabe | Noch offene arbeits-/dienstvertragliche Rechte und Lizenzierungsbefugnis klären | Entscheidung/Dateien aus V4-004 erhalten; konkrete entgegenstehende Hinweise betroffenenbezogen prüfen | BLOCKED nur für Rechtsgesamtgate; Wahl/Implementierung COMPLETED |
| O02 | Alte PCDs aus aktivem V4-Tree entfernt; ursprüngliche Herkunft ungeklärt | Kein aktueller Karten-Mitdistributionsblocker im Tree; historische Gitobjekte/öffentliche Kopien weiterhin betroffen | Releaseumfang Tree-/Artefakt vs vollständige Git-Historie abgrenzen | Keine erneute Karteneinbindung; historische Rechte separat prüfen, keine Rewrites | Tree-Maßnahme VERIFIED; historische Rechte NOT VERIFIED |
| O03 | AP01-Implementierung ausdrücklich freigegeben und durchgeführt; AP02/AP03 nicht beauftragt | Keine automatische weitere Metadaten-/Dependencyarbeit | Nächsten technischen Auftrag bestimmen | Lizenzierung für Eigenanteile technisch abgeschlossen; weitere APs separat | NOT STARTED für AP02/AP03 |
| O04 | 0.0.0 vs 0.0.1, keine Versionspolitik | Unklare Releaseidentität | Konsistente Paketversion und spätere Stabilitätszusagen | AP02 vereinheitlicht nach abgestimmter Entscheidung; Branch V4 nicht zu SemVer 4.0 erklären | NOT STARTED |
| O05 | Aktiver Conda-Python 3.14.6 neben System-Python 3.10.12 | Mögliche nichtrepräsentative ROS-/Packaging-Tests | Reproduzierbare isolierte Humble-Testumgebung wählen | Explizites System-Python/saubere Umgebung; keine globale Apt-/pip-/Conda-Reparatur ohne Erklärung | NOT STARTED |
| O06 | Aktuelle System-/ROS-Keys und Python-TF2-Provider unvalidiert | rosdep-/Buildfarm-Nachweis fehlt | Geeignete verfügbare Dependencies für Humble/Jammy | AP03 resolve/check plus vollständige Installation in isolierter Umgebung; keine Skip-Endlösung | NOT STARTED |
| O07 | Externe Nutzerkarten/R3D_CONFIG_DIR geprüft; Copy-Defaultpolitik und Ausgabe neben Eingabe bestehen | Nutzeroverride funktioniert ohne Source, Defaultportabilität noch offen | Spätere allgemeine Install-/Ausgabepolitik | V4-005 minimaler Kartenvertrag; restliches AP04 separat | IN PROGRESS, begrenzter Teil VERIFIED |
| O08 | Narrow-Flag in Orientierung, Namespaces/Clouds/Actiongrenzen | Öffentliche API-Korrekturen können bestehende Verbraucher beeinflussen | Neuer Metadaten-/Kompatibilitätsvertrag je Änderung | AP05 kleinere Änderungen; alle internen Verbraucher und Nutzeranleitungen gemeinsam anpassen; Regressionen | NOT STARTED |
| O09 | Filter/Follower-Systemgrenzen und Kalibrierungsannahmen | Keine generische sichere Navigation aus Detektionscode ableitbar | Gewünschten unterstützten Systemvertrag abgrenzen | Konkrete Sourcebefunde und synthetische No-Motion-Prüfungen priorisieren; keine neue Navigation pauschal beauftragen | NOT STARTED |
| O10 | Historisches PDF unverändert für Git-Aufnahme freigegeben/geprüft | Referenz nun im V4-Clone verfügbar | Nutzerauftrag zur Versionierung liegt ausdrücklich vor | V4-007, gleicher Referenzhash/33 Seiten; keine inhaltliche Aktualisierung | VERIFIED - dokumentierter Aufnahmeumfang |
| O11 | CI-Fernlauf, weitere Distributionen und Pflegezuständigkeiten unbestätigt | Kein neuer CI-/Support-/Releaseerfolg behauptbar | Zielmatrix, Maintainerzusagen und spätere Veröffentlichung autorisieren | Erst Humble; weitere Ziele nach Prüfung; kein ungefragter Push für CI | NOT STARTED |
| O12 | Originalhinweise/konkrete eigene Paketartefakte kontrolliert; Roottext in sdists/Wheels/Shares vorhanden | Keine Lizenzmitnahmelücke in geprüften Artefakten, Gesamtbundles/transitive Nativebinaries offen | Tatsächlichen künftigen Bundle-/Debianumfang festlegen und prüfen | T42-T47/11.21.5; keine automatische Library-Neulizenzierung | Technischer Paketumfang VERIFIED; rechtliche Gesamtbundlefreigabe BLOCKED/NOT VERIFIED |
| O13 | V4 soll nicht öffentlich gepusht werden; origin zeigt weiterhin auf public | Kein konfigurierter privater Pushschutz | Option A/B und konkrete spätere Repository-/Remote-/Pushfreigabe | Empfehlung B, nur nicht ausgeführte Vorlage in Abschnitt 12; aktuelle Remotes unverändert | NOT STARTED - Entscheidung ausstehend |
| O14 | LiDAR-Serverstand/Git-Ableitung belegt, tatsächlicher Deploymentstand fehlt | Keine Aussage über exakt eingesetzte Odometrie-/Submodul-/Systembinaries | Deployment-SHAs und Paket-/Artifactumfang belegen | R14/R15; analysierten Tip nicht mit Runtime gleichsetzen | NOT STARTED |
| O15 | Externe BSD-/PCL-Bedingungen und persönliche Änderungsattribution getrennt | Externe Anwendung/Binärmitnahme weiterhin offen | Spätere Notice-Übernahme und konkrete Distributionsnachweise | Notice in 11.15 dokumentarisch abgeschlossen; kein externes Repo geändert | Dokumentationsabschluss COMPLETED; externe Anwendung NOT STARTED |

Die verbindliche Lizenzentscheidung und technische Eigenanteil-Implementierung sind unter V4-004 erfolgt. Sie ersetzen keine unabhängige Vertrags-/Datenrechteklärung oder konkrete Binärfreigabe. O01/O02/O12 blockieren den öffentlichen Abschluss, nicht jede unabhängige technische Änderung. Bei neuer Information wird der jeweilige Status mit Datum und Nachweis aktualisiert; frühere Einschränkungen bleiben historisch nachvollziehbar.

## 8. Versionsvergleich: main → V4

Vergleichsreferenz bleibt der festgeschriebene Baseline-Commit, nicht ein später eventuell weiterentwickeltes main. „Unverändert“ bezieht sich auf diesen initialen V4-Stand. Erst ausgeführte Folgeänderungen dürfen diese Spalte erweitern.

| Bereich | Ausgangsstand main | Änderung V4 | Ergebnis | Nachweis |
| --- | --- | --- | --- | --- |
| Entwicklungslinie | main bei `c65642f…`; V1/V2/V3 als Remote-Tracking-Refs | Lokaler Branch V4 unmittelbar von Baseline; ein fokussierter Initial-Dokumentationscommit | Neue getrennte Entwicklungslinie, bestehende Refs unverändert | V4-001, T01/T06, Git-Parent/Refvergleich |
| Forschungsdokumentation | Historischer Bericht und Bestandsdokumentation | Dasselbe zentrale Protokoll mit V4-001..006 und abgegrenzten Original-/Regression-/Artefaktnachweisen | Keine zusätzlichen Forschungsberichte; historische Einträge erhalten | V4-005/V4-006; T37-T48 |
| Historische PDF | Vorhandene unveränderte, zunächst unversionierte Baseline-Dokumentation | Identische Bytes in V4 unter Git aufgenommen | Keine neue technische Funktion; SHA unverändert und historische Kartendarstellung erhalten | V4-007/T49 |
| Planung/Preprocessing | Vorhandene PCD-/Voxel-/Traversierbarkeits-/Graph-/A*-Funktionen | Keine | Bestehende Algorithmen erhalten, kein neuer Algorithmusbeitrag | T02; Abschnitt 2.3 |
| Paketmetadaten | Namen/Buildtyp/Maintainer vorhanden; Version/Beschreibung/Lizenz uneinheitlich | Nur beide license-Felder durch AP01 auf Apache-2.0 gesetzt | AP02 bleibt NOT STARTED; übrige Metadaten unverändert | V4-004/T31/T33; B03/AP02 |
| Dependencies | Teildeklaration, fehlende Imports, Skip-Workaround | Nur Abgleich/Planung; keine Dependencydeklaration geändert | Lizenzfelder geändert, Dependencyteile unverändert; rosdep nicht neu geprüft | T04/T10/T33; B04-B06 |
| Build/Installation | Copy-Config absichtlich abgelehnt, Sourcepfade und fehlende Paketlizenzmitnahme | Nutzerconfig ohne Source getestet; Originaltext in Paketroot/Share/sdist/Wheel vorhanden | Begrenzter Copy-Build belegt, Default-/Ausgabepolitik und rosdep weiterhin offen | V4-005/V4-006; T40/T44-T46 |
| ROS-Interfaces | Action/Topics/Service, RViz, Filter/Follower; bekannte Semantikgrenzen | Keine | AP05 offen; keine stillen API-Änderungen | B09-B13/T16 |
| Konfiguration/Launch | Source-Beispielpfade, zentrale strikte YAML, vier Launches | maps-Defaults leer, Modeeingabe explizit; relative/absolute/~ und externer Nutzerconfig geprüft | ROS-Launchvertrag unverändert, kein Kartenfallback; allgemeines AP04 offen | V4-005/T38-T40 |
| Odometry/TF | Standardisierte Poseeingabe, Frische/Frames, use_start, Poseverlust-Nullbefehl | Keine | V3-Vorleistung erhalten | Abschnitt 2.3; T02 |
| Tests/Lint | Funktionale Fälle und Linter-Templates bereits vorhanden | Nur Dokument-/Statische Prüfungen der Initialisierung | Keine neuen funktionalen Tests oder Lintkorrekturen | T03/T05; T12-T16 noch nicht ausgeführt |
| Lizenzierung/Datenrechte | Keine Root-LICENSE, TODOs und ungeklärte gebündelte PCDs | Apache-Eigenanteile samt Pakettexten geprüft; PCDs aus aktivem Tree/Artefakten entfernt | Technischer AP01-Umfang VERIFIED, historische Git-/Vertrags-/Bundlefragen offen | V4-004..006; T42-T48 |
| CI/CD | Keine Pipeline | Keine | AP07 offen | T18 |
| Kompatibilität | Humble als Ziel dokumentiert | Lokale OS-/Python-Präsenz erfasst, keine ROS-Ausführung | Kein neues Supportversprechen | T17/O05 |
| Release | Kein hier belegter Index-/Bloom-/Buildfarmabschluss | Kriterien, private V4-Abgrenzung und noch offene Lizenz-/Artefakt-Gates präzisiert | NOT READY; keine Veröffentlichung | Abschnitt 9/12; AP10 |
| Externe LiDAR-Software | Separates Repository; Standard-Odometry-/TF-Vertrag | Herkunft und ältere Diffs dokumentiert; Notice im Protokoll abgeschlossen | Kein fremder Code integriert/geändert; Originallizenzen getrennt | V4-003/V4-004; 11.13-11.15 |
| Copyright-Attribution | 18 eigene Namensheader plus sechs OSRF-Templates | Zusätzliche SPDX-Attribution 2026 Bastian Aumer nur für 18 zugeordnete eigene Dateien | Eigene bisherige Hinweise erhalten; sechs Fremdtemplates byteidentisch | V4-004/T30/T34; 11.21.2 |
| GitHub-/Remoteverwaltung | origin public, V4 lokal ohne Upstream | Optionen und Pushschutz nur als Vorschlag dokumentiert | Keine Sichtbarkeits-/Remoteänderung; kein Push | Abschnitt 12/T25 |

## 9. Veröffentlichungsstatus

| Gegenstand | Status | Begründung und nächster erforderlicher Nachweis |
| --- | --- | --- |
| ROS Index source readiness | **NOT READY** | Apache-Text/Metadaten und aktiver datenfreier Tree vorhanden; individuelle Befugnis-/historische Git-Datenrechte, sonstige Herkunft und übrige Metadaten/öffentlicher Release-Ref/Review offen. Keine V4-Veröffentlichung |
| rosdep readiness | **NOT READY** | Direkte Manifestlücken und dokumentierter Skip-Workaround; vollständige aktuelle Humble-Auflösung/Installation/check nicht ausgeführt. AP03 |
| Bloom readiness | **NOT READY** | Rechte/Metadaten/Dependencies, Versionskonsistenz, Changelogs und installierter Betrieb offen; kein Release-Repository/-Track in dieser Ausführung geprüft/angelegt. AP01-AP04/AP08/AP10 |
| Buildfarm readiness | **NOT READY** | Begrenzte Copy-Builds/43 Runtime-/Configfälle und Lizenzmitnahme belegt, aber rosdep/Runtimevollständigkeit, Versions-/Metadaten-/Defaultinstall-/Releasegates offen; kein Debian-/Farmjob |
| Tatsächliche offizielle Index-/Binärveröffentlichung | **NOT VERIFIED** | Keine neue rosdistro-/Release-/Buildfarm-Statusabfrage oder externe Bestätigung; historische Abwesenheit nicht als aktuelle Serverprüfung ausgeben |
| ROS 2 Humble / Ubuntu 22.04 / Python 3.10 | **NOT VERIFIED** | Primäres dokumentiertes Ziel; historisch berichtete Tests, aber kein neuer vollständiger Clean-Nachweis für V4 |
| Jazzy / neuere ROS-Distributionen / andere Plattformen | **NOT VERIFIED** | Keine neue Ausführung, keine Supportzusage; weitere Ziele erst nach Auswahl und Prüfung |

`READY` darf erst vergeben werden, wenn die konkret definierten Voraussetzungen für den jeweiligen Bereich nachgewiesen sind. `NOT READY` benennt bekannte Hindernisse, `NOT VERIFIED` fehlende Prüfung. Eine erfolgreich konfigurierte lokale Pipeline ist noch keine externe Veröffentlichung und noch kein erfolgreicher Buildfarm-Lauf.

Die verbleibenden grundlegenden Release-Gates sind: autorisierte Code-/Datenverteilung, zutreffende konsistente Paketmetadaten, vollständige plattformspezifische Dependencies, funktionsfähige installierte Ressourcen und nachvollziehbare Version-/Releasevorbereitung. Die umgesetzte Eigenanteil-Attribution/Apache-Wahl und erhaltenen Fremdbedingungen beseitigen diese übrigen Gates nicht. V4 bleibt ausschließlich lokal, bis ein privater Workflow ausdrücklich freigegeben ist. Die V4-Projektziele zu Schnittstellen-/Test-/CI-Qualität werden zusätzlich verfolgt; fehlende optionale Tools sind keine erfundenen separaten Indexblocker. AP01 bleibt insgesamt BLOCKED ausschließlich wegen noch offener Rechts-/Distributionsnachweise; endgültige Eigenanteil-Lizenzentscheidung und beauftragte technische Anwendung sind abgeschlossen.

Aktualisierung V4-005: Der aktive Tree-/Paketdatenblocker der zwei Karten entfällt, nicht die Rechtsprüfung historischer Gitobjekte. Begrenzter Copy-Build und externer Nutzerconfig-Test sind neu belegt; allgemeine rosdep-/Installations-/Release-Gates bleiben NOT READY. AP04/AP06 nun IN PROGRESS; AP02/AP03 bleiben NOT STARTED.

## 10. Abschließende Bewertung

Der beauftragte technische AP01-Umfang ist nach V4-006 VERIFIED: Apache-2.0-Entscheidung und Originaltext, 18 zugeordnete eigene Copyright-/SPDX-Header, Manifest-/Setup-Lizenzen, erhaltene Fremdtemplates, getrennte externe LiDAR-Originalbedingungen/Modification Notice, aktive Kartenentfernung und konkret geprüfte Paket-Lizenzmitnahme. Roottext ist unverändert; zwei notwendige identische Paketkopien ermöglichen isoliertes Source-/Wheel-/ROS-Paketieren.

Die bisherigen zwei Karten waren bereits beim Auftragseingang im Working Tree gelöscht und sind nun in normalem V4-Commit entfernt. Nutzer liefern eigene PCDs über die vorhandene Konfiguration; die Algorithmen/ROS-Verträge bleiben erhalten. 40 Configfälle plus drei vorhandene ROS-/Launchfälle bestehen. Copy-Installation ohne Karten und externe Nutzerkonfiguration bei nicht verfügbarem ursprünglichem Sourcepfad sind geprüft; allgemeine Copy-Default-/Ausgabepolitik ist nicht umfassend refaktoriert. Systembuild ohne User-Site ist kein vollständiger Runtime-Dependencynachweis, da dort Open3D/NetworkX fehlen; Runtimefälle benutzen vorhandene User-Site und behalten eine SciPy-/NumPy-Warnung.

**Vollständige rechtliche Releasefreigabe nicht verifiziert:** Verträge/Arbeitgeberbefugnisse, sonstige Dateiprovenienz, historische Karten-Gitobjekte und konkrete transitive/native/zusammen verteilte Binaries bleiben offen. Die Karte ist aus aktuellem Tree/Artefakten, nicht aus Git-Historie, Forks oder Kopien entfernt. AP01 insgesamt daher BLOCKED nur für dieses Rechts-/Releasegesamtgate. AP04/AP06/AP08/AP10 IN PROGRESS, AP02/AP03 NOT STARTED. ROS Index/Bloom/Buildfarm NOT READY; kein neuer Quality Level oder Plattform-Supportanspruch.

Zwei logisch getrennte lokale Commits halten Karten-/Configänderung und Lizenzmitnahme/Verifikation fest. Historische V4-Einträge/Branchreferenzen/PDFs erhalten, keine History-Rewrites, externen Repository-/GitHub-/Remoteänderungen, keine Veröffentlichung und kein Push. Weitere Arbeit wartet auf den nächsten Auftrag.

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
| R07 | Herkunft/Weitergabe der historischen Karten weiterhin unbekannt; keine aktiven V4-PCDs mehr | Kein aktueller Tree-Datenreleaseblocker; historische Objekte, Forks/Kopien und vollständiger Git-Releaseumfang separat prüfen |
| R08 | Historische Kartendaten oder sonstige Artefakte möglicherweise sensibel/vertraulich | PCDs aus aktuellem Tree entfernt; historischer Inhalts-/Vertragsstatus weiterhin nicht bestimmbar |
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
| AP02 / AP03 | Keine allgemeine Metadaten-/Dependencyimplementierung | NOT STARTED |

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

Für den beauftragten eigenen Code sind Auswahl, Attribution, Lizenzdatei und Lizenzfelder umgesetzt und statisch geprüft. Keine weitere allgemeine Lizenzrecherche ist für den nächsten unabhängigen technischen AP vorgesehen. Noch offen sind konkrete arbeits-/dienstvertragliche Rechte, Rechte an historischen Karten-Gitobjekten, unklare Artefaktprovenienz und sämtliche zusätzlichen Texte/Pflichten bei einer vollständigen transitiven/nativen Binärdistribution. Die aktive Karte ist entfernt und eigene sdist-/Wheel-/Copy-Sharetextmitnahme ist unter V4-006 geprüft. Diese Grenzen bleiben AP01-Rechtsgesamtgate/AP10-Releasegate; keine rechtliche Gesamtfreigabe, Patentgarantie oder Veröffentlichung. AP02/AP03 werden erst nach einem neuen Auftrag begonnen.

#### 11.21.5 Abschließende Verifikation und Distributionsgrenzen, 14. Oktober 2026

Die 18 zugeordneten eigenen Python-Dateien einschließlich Launch-/Setup-/Testdatei haben weiterhin exakt die angewandten persönlichen SPDX-Zeilen. Sechs OSRF-Testtemplates behalten Originalcopyright und Apache-Hinweise; ihr Sourcearchiveinhalt wurde byteidentisch geprüft. Leere Python-/ament-Marker, Paketmetadaten, YAML, TXT/Dokumentation und neun ältere PYC bekommen keine neue unbelegte Autorzuordnung. PYC-Provenienz ist im Repository nicht unabhängig geklärt; die konkret erzeugten sdists/Wheels enthalten jedoch keine PYC. `r3d_planner/points.txt` enthält weiterhin ortsspezifische CLI-Koordinaten/Bezeichnungen; Daten-/Vertragsprovenienz nicht verifiziert, daraus allein kein nachgewiesener Copyright- oder Lizenzverstoß. Keine anderen mitgelieferten PCD-Beispieldaten identifiziert. Temporäre Synthesefälle sind Testfixtures, keine veröffentlichte Standardkarte.

Roottext und zwei paketlokale LICENSEs entsprechen dem erneut abgerufenen offiziellen ASF-TXT. Lizenztexte/Originalheader in fremden Templates sind erhalten. Für die im R3D-Tree enthaltenen Fremdtemplates ist keine separate upstream NOTICE-Datei identifiziert; daraus wird keine Aussage über sämtliche externen ROS-/Native-Binaries abgeleitet. Die bedingten Noticepflichten aus 11.8/11.21.3 gelten nach tatsächlichem Distributionsumfang. Die getrennte LiDAR-Dokumentationsnotice ersetzt weder BSD-Texte noch PCL/NDT-Dateihinweise; tatsächliche externe Deployment-/Bundlemitnahme bleibt NOT VERIFIED.

| Distributionsweg | Aktueller Nachweis | Rechts-/Technikgrenze |
| --- | --- | --- |
| Aktueller Source-Tree/Sourcearchive | Keine PCDs, Root-/Paket-Lizenztexte und Originaltemplates erhalten; zwei konkrete sdists geprüft | Vollständiger Git-Klon enthält historische Kartenobjekte; individuelle Befugnisse/sonstige Provenienz offen |
| ROS-Index-Registrierung | Lizenzfelder/Text und datenfreier aktiver Tree vorhanden | Public-V4-Ref nicht übertragen; übrige Metadaten/Namens-/Review-/Rechteprüfung offen |
| Installation über rosdep | Lizenzwahl verändert weder Keys noch installierte Dependencies | AP03 nicht begonnen; keine rosdep-Auflösung/Installation/Gesamtlizenzfreigabe |
| Wheels / colcon-Copy-Shares | Beide Wheels mit .dist-info- und Share-LICENSE; zwei Shares aus isolierten sdists; 0 PCDs | Konkrete temporäre Artefakte, keine transitive Librarymitlieferung bzw. allgemeine Copy-Defaultabnahme |
| Debian/Bloom/Buildfarm | Paketlokale Originaltexte und data_files schaffen technische Voraussetzung | Kein Debianpaket/Farmjob erzeugt; Versionen/Dependencies/Installverträge/sonstige Rechte weiterhin offen |
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
