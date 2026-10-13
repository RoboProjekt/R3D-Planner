# R3D-Planner V4
# ROS 2 Compliance Development

Stand: 13. Oktober 2026; fortgeführt um V4-002/V4-003. Dieses Dokument ist das einzige zentrale Entwicklungsprotokoll für V4. Es trennt den historischen Bestand, geplante Maßnahmen, tatsächlich durchgeführte Änderungen und deren Nachweise. Die Erstinitialisierung verändert ausschließlich dieses Dokument und legt den Branch V4 an. Sie enthält keine Implementierung der Arbeitspakete AP01 bis AP10.

## 1. Zielsetzung

V4 soll die bestehende funktionale R3D-Planner-Implementierung für eine nachvollziehbare öffentliche Bereitstellung im ROS-2-Ökosystem vorbereiten. Gegenstand sind Paketmetadaten, Dependency-Deklarationen und rosdep, Lizenz- und Datenrechte, installationsunabhängige Ressourcen, öffentliche ROS-Verträge, Tests, CI/CD, Nutzungsdokumentation und Releasevorbereitung. Beide Pakete behalten `ament_python` und setuptools. Eine CMake-Konvertierung ist ohne konkreten technischen Bedarf nicht vorgesehen.

PCD-Verarbeitung, Traversierbarkeitsanalyse, Graphrekonstruktion, A*, Navigationseinstiegspunkte und die V3-Integration sind Vorleistungen. V4 werden ausschließlich begründete und nachgewiesene Änderungen nach dem Baseline-Commit zugerechnet. Neue SLAM-/Mappingverfahren, der Ersatz des Planners, ein vollständiges Nav2-Redesign und neue Hardwaretreiber sind keine primären Ziele.

Die Initialisierung ist noch keine Freigabe für Codeänderungen. Gemäß Abschnitt 11 des Auftrags muss der initiale Plan zunächst vorgelegt werden; der Beginn des ersten Implementierungsarbeitspakets benötigt eine ausdrückliche Freigabe. Pushes, Releases und Pull Requests sind nicht beauftragt.

**Nutzerentscheidung vom 13. Oktober 2026:** „Überspringe die Lizenzierung vorerst, hierzu muss ich erst noch recherchieren“. AP01 wird deshalb zurückgestellt und als `BLOCKED` geführt. Diese Entscheidung erlaubt keine Annahme einer Projektlizenz und beseitigt keine Veröffentlichungshindernisse. Unabhängige technische Arbeiten können nach Planfreigabe beginnen. Es wird keine Lizenz ausgewählt, angewendet oder stillschweigend aus `setup.py` übernommen.

**Fortführung am 13. Oktober 2026:** Der folgende Auftrag hebt die Rückstellung ausschließlich für Recherche, Copyright-/Provenienzbewertung und wissenschaftliche Dokumentation auf. Der ergänzte Auftrag enthält die Entwicklererklärung Bastian Aumers und erlaubt ausdrücklich die Analyse der benannten externen LiDAR-Repositories. Verbindliche Lizenzwahl, Lizenz-/Headeranwendung, AP02/AP03-Implementierung und GitHub-/Remoteänderungen bleiben nicht freigegeben. V4-002/V4-003 dokumentieren diese neue Abgrenzung; die frühere Rückstellung bleibt historisch nachvollziehbar.

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
| Geplante Änderung | Lizenzvergleich/Dateiinventur/Dependency-/LiDAR-Provenienz sind nun dokumentiert; Entwicklererklärung aufnehmen; offene Vertrags-/Karten-/Artefaktrechte klären; Entscheidung und technische Anwendung erst nach neuer Freigabe |
| Priorität | P0 |
| Abhängigkeiten | Recherchefortführung am 13.10.2026 ausdrücklich beauftragt; persönliche Entwicklererklärung dokumentiert. Verbindliche Befugnis-/Vertrags-/Datenklärung und Lizenzentscheidung fehlen weiterhin |
| Abschlusskriterien | Rechte und Distributionsumfang nachvollziehbar; autorisierte Lizenzentscheidung; konsistente Dateien/Metadaten, mitzugebende Notices geklärt; keine unbelegten Bibliotheks-Kompatibilitätsbehauptungen |
| Aktueller Status | **BLOCKED** - begrenzte Recherche/Inventur unter V4-002/V4-003 VERIFIED; Rechte-/Entscheidungs-/Implementierungsabnahme offen |

AP01-Teilstände nach V4-002/V4-003: Lizenzvergleich, Source-/Copyright-Inventur und deklarationsbezogener Dependency-/LiDAR-Abgleich **VERIFIED** im jeweils benannten Prüfumfang. Alleinentwicklung ist **dokumentiert**, rechtliche Rechteketten-/Arbeitgeber-/Kartenabnahme und verbindliche Entscheidung bleiben **offen/BLOCKED**. Technische Lizenzanwendung **NOT STARTED**. Details und Soll-Implementierung ausschließlich in Kapitel 11.

### 4.3 AP02 - Paketmetadaten

| Feld | Planung |
| --- | --- |
| Ausgangsstand | Zwei syntaktisch lesbare Format-3-Manifeste; passende Namen, Maintainer, ament_python-Export; Version 0.0.0 vs Setup 0.0.1 |
| Probleme | B03: TODO-Beschreibung, Versionswiderspruch, fehlende empfohlene URLs; rechtliche Angaben ungelöst |
| Geplante Änderung | Zunächst nichtrechtliche Beschreibungen und Repository-/Bugtracker-URLs korrigieren; konsistente nächste Paketversion abstimmen; vorhandene Maintainerdaten nicht erfinden/ersetzen; Lizenzfelder bis AP01 offenhalten |
| Priorität | P0 für Release-Metadaten, P1 für empfohlene Ergänzungen |
| Abhängigkeiten | Freigabe des ersten Implementierungsschritts; Lizenzabschluss hängt von AP01 ab, übrige Korrekturen nicht |
| Abschlusskriterien | Manifest-/Setup-Metadaten konsistent und geprüft; Platzhalter technisch soweit zulässig entfernt; Lizenzrestpunkt ausdrücklich offen, daher vor AP01 keine vollständige Releaseabnahme |
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
| Aktueller Status | **NOT STARTED** |

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
| Aktueller Status | **NOT STARTED** |

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
| Aktueller Status | **IN PROGRESS** - Initialprotokoll plus verifizierte Rechercheintegration/Copyright-/LiDAR-Analyse; öffentliche Anleitungen und technische Implementierung unverändert |

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
| Aktueller Status | **IN PROGRESS** - Kriterien, Lizenz-/Attributionsstrategie und private Entwicklungsabgrenzung dokumentiert; keine Releasewerkzeuge oder Publikationsschritte |

### 4.12 Abhängigkeitsgerechte Reihenfolge und nächste Freigabe

AP01 wurde zunächst zurückgestellt; nun sind ausschließlich Analyse und Dokumentation beauftragt, nicht Lizenzanwendung. Nach dieser Recherchefortführung bleibt als erster separat freizugebender technischer Schritt wird der nichtrechtliche Teil von **AP02** vorgeschlagen: Paketbeschreibungen, sinnvolle URLs und Versionskonsistenz prüfen/korrigieren; Lizenzangaben nicht auswählen oder ändern. Danach folgen **AP03 → AP04 → AP05**, jeweils mit passenden **AP06**-Regressionen und fortlaufender **AP08**-Dokumentation. **AP07** automatisiert erst die stabilisierten Schritte. **AP09** prüft die gewählten Zielumgebungen; **AP10** schließt die Releasevorbereitung erst nach Beseitigung der technischen und rechtlichen Blocker ab.

AP06/AP08 sind keine erst am Ende beginnenden Phasen. Die weiterhin offene Rechte-/Entscheidungs-/Implementierungsabnahme von AP01 sperrt den öffentlichen Releaseabschluss sowie die ungeklärte Mitlieferung von Kartendaten. CI und weitere Distributionen werden nicht vorgezogen, um ungelöste Dependencies oder Installationsverhalten zu verdecken.

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

Die temporären Prüfhilfen liegen außerhalb des Repositorys und sind keine zusätzlichen Entwicklungsberichte. Im Repository entsteht genau ein neues Entwicklungsdokument. Neue Testergebnisse müssen künftig mit vollständigem Befehl, Umgebung, Commit, Exitcode und relevanten Resultaten hier ergänzt werden; Fehler und nicht ausführbare Prüfungen werden ausdrücklich protokolliert.

## 7. Probleme und offene Entscheidungen

| ID | Beschreibung | Auswirkung | Erforderliche Entscheidung | Vorgeschlagene Lösung | Aktueller Status |
| --- | --- | --- | --- | --- | --- |
| O01 | Alleinige R3D-Eigenentwicklung erklärt; Lizenzierungsbefugnis/Verträge weiterhin nicht unabhängig geprüft | Keine rechtliche Gesamtfreigabe | Arbeitgeber-/Vertrags-/Befugnisfragen und endgültige Lizenzwahl klären | Erklärung und Inventar in Kapitel 11; Apache nur Kandidat, keine Anwendung | BLOCKED - Recherche verifiziert, Rechts-/Entscheidungsabnahme offen |
| O02 | Herkunft/Rechte beider PCD-Karten ungeklärt | Datenverteilung weiterhin offen | Berechtigte und konkrete Weitergabebedingungen bestätigen | Technisches Inventar/SHA in 11.12; keine Standardlizenz annehmen | BLOCKED |
| O03 | Initialer Plan muss vor Implementierung geprüft werden | Noch keine Code-/Metadatenarbeit autorisiert | Freigabe des ersten nichtrechtlichen AP02-Schritts | Dieses initiale Dokument und die Reihenfolge vorlegen, ausdrückliche Zustimmung abwarten | NOT STARTED - Freigabe ausstehend |
| O04 | 0.0.0 vs 0.0.1, keine Versionspolitik | Unklare Releaseidentität | Konsistente Paketversion und spätere Stabilitätszusagen | AP02 vereinheitlicht nach abgestimmter Entscheidung; Branch V4 nicht zu SemVer 4.0 erklären | NOT STARTED |
| O05 | Aktiver Conda-Python 3.14.6 neben System-Python 3.10.12 | Mögliche nichtrepräsentative ROS-/Packaging-Tests | Reproduzierbare isolierte Humble-Testumgebung wählen | Explizites System-Python/saubere Umgebung; keine globale Apt-/pip-/Conda-Reparatur ohne Erklärung | NOT STARTED |
| O06 | Aktuelle System-/ROS-Keys und Python-TF2-Provider unvalidiert | rosdep-/Buildfarm-Nachweis fehlt | Geeignete verfügbare Dependencies für Humble/Jammy | AP03 resolve/check plus vollständige Installation in isolierter Umgebung; keine Skip-Endlösung | NOT STARTED |
| O07 | Config-/Karten-/Ausgabepolitik auf Sourceentwicklung zugeschnitten | Copy-Installation bricht oder erwartet Sourcepfade | Default-Ressourcen, Nutzeroverride und beschreibbare Ausgaben festlegen | AP04 minimalen Vertrag entwerfen und vorhandene Validierung beibehalten; Datenrechte getrennt | NOT STARTED |
| O08 | Narrow-Flag in Orientierung, Namespaces/Clouds/Actiongrenzen | Öffentliche API-Korrekturen können bestehende Verbraucher beeinflussen | Neuer Metadaten-/Kompatibilitätsvertrag je Änderung | AP05 kleinere Änderungen; alle internen Verbraucher und Nutzeranleitungen gemeinsam anpassen; Regressionen | NOT STARTED |
| O09 | Filter/Follower-Systemgrenzen und Kalibrierungsannahmen | Keine generische sichere Navigation aus Detektionscode ableitbar | Gewünschten unterstützten Systemvertrag abgrenzen | Konkrete Sourcebefunde und synthetische No-Motion-Prüfungen priorisieren; keine neue Navigation pauschal beauftragen | NOT STARTED |
| O10 | Historisches PDF weiterhin unversioniert | Spätere frische Clones enthalten die Baseline-Dokumentation nicht | Soll das unveränderte PDF später versioniert oder anderweitig dauerhaft referenziert werden? | Bestehende Datei zunächst unverändert erhalten; später separate bewusste Dokumentationsentscheidung | NOT STARTED |
| O11 | CI-Fernlauf, weitere Distributionen und Pflegezuständigkeiten unbestätigt | Kein neuer CI-/Support-/Releaseerfolg behauptbar | Zielmatrix, Maintainerzusagen und spätere Veröffentlichung autorisieren | Erst Humble; weitere Ziele nach Prüfung; kein ungefragter Push für CI | NOT STARTED |
| O12 | Direkte Dependency-Lizenzdeklarationen und zusätzliche NumPy-/LiDAR-Bedingungen untersucht | Vollständige Binär-/transitive Verteilbarkeit noch offen | Tatsächliche Artefakt-/Versions-/Bundle-Strategie und Pflichttexte klären | 11.11/11.13 trennen Hauptlizenzen, Sourceübernahme und Binärdistribution; keine pauschale Freigabe | BLOCKED - begrenzte Deklarationsprüfung VERIFIED, Gesamtaudit offen |

| O13 | V4 soll nicht öffentlich gepusht werden; origin zeigt weiterhin auf public | Kein konfigurierter privater Pushschutz | Option A/B und konkrete spätere Repository-/Remote-/Pushfreigabe | Empfehlung B, nur nicht ausgeführte Vorlage in Abschnitt 12; aktuelle Remotes unverändert | NOT STARTED - Entscheidung ausstehend |
| O14 | LiDAR-Serverstand/Git-Ableitung belegt, tatsächlicher Deploymentstand fehlt | Keine Aussage über exakt eingesetzte Odometrie-/Submodul-/Systembinaries | Deployment-SHAs und Paket-/Artifactumfang belegen | R14/R15; analysierten Tip nicht mit Runtime gleichsetzen | NOT STARTED |
| O15 | Externe Root-BSD-2 und PCL-BSD-3 sowie unbenannte Copyright-2026-Header | Persönliche Änderungsattribution und Binärmitnahme nicht vollständig angewandt | Spätere genaue Notice-/Datei-/Distributionsfreigabe | Modification-Notice-Konzept in 11.15; Originaltexte erhalten | BLOCKED - keine technische Anwendung freigegeben |

Die nun erlaubte Recherche und dokumentierte Entwicklererklärung ersetzen keine verbindliche Lizenzentscheidung oder Vertrags-/Datenrechteklärung. O01/O02/O12 blockieren den öffentlichen Abschluss, nicht jede unabhängige technische Änderung. Bei neuer Information wird der jeweilige Status mit Datum und Nachweis aktualisiert; frühere Einschränkungen bleiben historisch nachvollziehbar.

## 8. Versionsvergleich: main → V4

Vergleichsreferenz bleibt der festgeschriebene Baseline-Commit, nicht ein später eventuell weiterentwickeltes main. „Unverändert“ bezieht sich auf diesen initialen V4-Stand. Erst ausgeführte Folgeänderungen dürfen diese Spalte erweitern.

| Bereich | Ausgangsstand main | Änderung V4 | Ergebnis | Nachweis |
| --- | --- | --- | --- | --- |
| Entwicklungslinie | main bei `c65642f…`; V1/V2/V3 als Remote-Tracking-Refs | Lokaler Branch V4 unmittelbar von Baseline; ein fokussierter Initial-Dokumentationscommit | Neue getrennte Entwicklungslinie, bestehende Refs unverändert | V4-001, T01/T06, Git-Parent/Refvergleich |
| Forschungsdokumentation | Historischer Bericht und Bestandsdokumentation | Zentrales Initialprotokoll plus Lizenz-/Copyright-/LiDAR-Analyse mit 22 Unterkapiteln, Matrix, Inventar und Notice-Entwurf | Wissenschaftliche Dokumentation erweitert; kein neuer Algorithmusbeitrag | V4-001 bis V4-003; T19-T26 |
| Historische PDF | Unversionierte konsolidierte Baseline-Dokumentation | Keine Änderung, keine Aufnahme in den Initialisierungscommit | SHA-256 unverändert; weitere Versionierungsentscheidung O10 offen | T02, Abschnitt 2.1 |
| Planung/Preprocessing | Vorhandene PCD-/Voxel-/Traversierbarkeits-/Graph-/A*-Funktionen | Keine | Bestehende Algorithmen erhalten, kein neuer Algorithmusbeitrag | T02; Abschnitt 2.3 |
| Paketmetadaten | Namen/Buildtyp/Maintainer vorhanden; Version/Beschreibung/Lizenz uneinheitlich | Nur Defizite dokumentiert | AP02 noch nicht umgesetzt | B03/AP02 |
| Dependencies | Teildeklaration, fehlende Imports, Skip-Workaround | Nur Abgleich und Planung | Keine Manifest-/Systemänderung, rosdep nicht neu geprüft | T04/T10; B04-B06 |
| Build/Installation | setuptools/ament_python, vorhandene Scripts/Ressourcen; Copy-Config eingeschränkt | Keine | AP04 offen | B07/B08/T11/T15 |
| ROS-Interfaces | Action/Topics/Service, RViz, Filter/Follower; bekannte Semantikgrenzen | Keine | AP05 offen; keine stillen API-Änderungen | B09-B13/T16 |
| Konfiguration/Launch | Zentrale validierte YAML, Robotprofile, vier installierte Launches | Keine | Bestand, nicht neue V4-Funktionalität | Abschnitt 2.3; T02 |
| Odometry/TF | Standardisierte Poseeingabe, Frische/Frames, use_start, Poseverlust-Nullbefehl | Keine | V3-Vorleistung erhalten | Abschnitt 2.3; T02 |
| Tests/Lint | Funktionale Fälle und Linter-Templates bereits vorhanden | Nur Dokument-/Statische Prüfungen der Initialisierung | Keine neuen funktionalen Tests oder Lintkorrekturen | T03/T05; T12-T16 noch nicht ausgeführt |
| Lizenzierung/Datenrechte | Setupstring, TODO-Manifeste, Fremdnotices; Rechte ungeklärt | Vier Kandidaten verglichen, Entwicklererklärung dokumentiert, direkte Lizenzen/Artefaktgrenzen erfasst | Apache-2.0 nur bevorzugt; Vertrags-/Karten-/Entscheidungs-/Anwendungsabnahme bleibt offen | AP01, 11.18-11.21, T19-T24 |
| CI/CD | Keine Pipeline | Keine | AP07 offen | T18 |
| Kompatibilität | Humble als Ziel dokumentiert | Lokale OS-/Python-Präsenz erfasst, keine ROS-Ausführung | Kein neues Supportversprechen | T17/O05 |
| Release | Kein hier belegter Index-/Bloom-/Buildfarmabschluss | Kriterien, private V4-Abgrenzung und noch offene Lizenz-/Artefakt-Gates präzisiert | NOT READY; keine Veröffentlichung | Abschnitt 9/12; AP10 |
| Externe LiDAR-Software | Nicht als Implementation in den R3D-Paketen enthalten; Standard-Odometry-/TF-Vertrag vorhanden | Herkunft und drei ältere externe Änderungen analysiert, keine Dateien integriert | Externer Vorbestand, neue V4-Dokumentation; BSD-2/PCL-BSD-3-Bedingungen getrennt | V4-003, 11.13-11.15 |
| Copyright-Attribution | 18 eigene Namensheader plus sechs OSRF-Templates | Alleinentwicklererklärung dokumentiert, vollständiges Dateiinventar und zukünftige SPDX-Form vorbereitet | Keine Headeränderung oder neue Rechteübertragung | 11.9-11.12, T20 |
| GitHub-/Remoteverwaltung | origin public, V4 lokal ohne Upstream | Optionen und Pushschutz nur als Vorschlag dokumentiert | Keine Sichtbarkeits-/Remoteänderung; kein Push | Abschnitt 12/T25 |

## 9. Veröffentlichungsstatus

| Gegenstand | Status | Begründung und nächster erforderlicher Nachweis |
| --- | --- | --- |
| ROS Index source readiness | **NOT READY** | LICENSE/Manifest-Lizenz ungeklärt; Vergleich/Erklärung dokumentiert, verbindliche Entscheidung und Anwendung fehlen. Öffentlichkeit jetzt als public geprüft; Namenskollision und externe Reviewentscheidung weiterhin nicht verifiziert. AP01/AP02/AP10 |
| rosdep readiness | **NOT READY** | Direkte Manifestlücken und dokumentierter Skip-Workaround; vollständige aktuelle Humble-Auflösung/Installation/check nicht ausgeführt. AP03 |
| Bloom readiness | **NOT READY** | Rechte/Metadaten/Dependencies, Versionskonsistenz, Changelogs und installierter Betrieb offen; kein Release-Repository/-Track in dieser Ausführung geprüft/angelegt. AP01-AP04/AP08/AP10 |
| Buildfarm readiness | **NOT READY** | Reproduzierbarer Clean-Copy-Build-/Install-/Testnachweis fehlt, bekannte Installationsgrenzen und Releaseblocker bestehen. Keine Farmjobs ausgeführt. AP03/AP04/AP06/AP10 |
| Tatsächliche offizielle Index-/Binärveröffentlichung | **NOT VERIFIED** | Keine neue rosdistro-/Release-/Buildfarm-Statusabfrage oder externe Bestätigung; historische Abwesenheit nicht als aktuelle Serverprüfung ausgeben |
| ROS 2 Humble / Ubuntu 22.04 / Python 3.10 | **NOT VERIFIED** | Primäres dokumentiertes Ziel; historisch berichtete Tests, aber kein neuer vollständiger Clean-Nachweis für V4 |
| Jazzy / neuere ROS-Distributionen / andere Plattformen | **NOT VERIFIED** | Keine neue Ausführung, keine Supportzusage; weitere Ziele erst nach Auswahl und Prüfung |

`READY` darf erst vergeben werden, wenn die konkret definierten Voraussetzungen für den jeweiligen Bereich nachgewiesen sind. `NOT READY` benennt bekannte Hindernisse, `NOT VERIFIED` fehlende Prüfung. Eine erfolgreich konfigurierte lokale Pipeline ist noch keine externe Veröffentlichung und noch kein erfolgreicher Buildfarm-Lauf.

Die verbleibenden grundlegenden Release-Gates sind: autorisierte Code-/Datenverteilung, zutreffende konsistente Paketmetadaten, vollständige plattformspezifische Dependencies, funktionsfähige installierte Ressourcen und nachvollziehbare Version-/Releasevorbereitung. Die vorgesehene Attribution/BSD-Erhaltung und unverbindliche Apache-Präferenz beseitigen diese Gates nicht. V4 bleibt ausschließlich lokal, bis ein privater Workflow ausdrücklich freigegeben ist. Die V4-Projektziele zu Schnittstellen-/Test-/CI-Qualität werden zusätzlich verfolgt; fehlende optionale Tools sind keine erfundenen separaten Indexblocker. AP01 bleibt BLOCKED trotz nun verifizierter begrenzter Recherche; Vertrags-/Karten-/Befugnisnachweise, endgültige Entscheidung und technische Anwendung fehlen.

## 10. Abschließende Bewertung

**Vorläufig.** V4 enthält bislang die getrennte Entwicklungslinie, das zentrale Initialprotokoll und die fortgeführte Lizenz-/Copyright-/Dependency-/LiDAR-Provenienzrecherche. Die neue wissenschaftliche Leistung ist die nachvollziehbare Quellen-/Diffbewertung, Entwicklerattribution, Entscheidungsmatrix, Dateiinventur und Vorbereitung einer Modification Notice. Sie ist weder Lizenzimplementierung noch neue LiDAR-/Planner-/Preprocessor-Funktionalität. Die untersuchten externen Änderungen vom 16.09.2026 bleiben Vorbestand.

Apache-2.0 ist unter der offengelegten Präferenzordnung ein bevorzugter Kandidat für autorisierte eigene R3D-Anteile. Originale externe BSD-/sonstige Bedingungen und OSRF-Testtemplates bleiben separat. Alleinentwicklung der eigenen Komponenten ist als Entwicklererklärung dokumentiert, Arbeitgeber-/Vertrags-/Kartenrechte und konkrete Gesamtartefakte bleiben offen. AP01 BLOCKED, AP08/AP10 IN PROGRESS; AP02/AP03 technisch NOT STARTED.

Vorhandene Algorithmen, ROS-Verträge, vier Launches, YAML-/Odometry-/TF-Integration, Lizenzfelder, Sourceheader und Karten sind unverändert. Die späteren technischen Ergebnisse sind noch offen und müssen an der festgeschriebenen Baseline mit tatsächlich ausgeführten Prüfungen gemessen werden. Weitere Implementierung, Lizenzanwendung und private/öffentliche Übertragung warten auf einen neuen ausdrücklichen Auftrag. Der aktuelle Dokumentationscommit ist keine Veröffentlichung.

## 11. Open-Source-Lizenzanalyse und Copyright-Strategie

### 11.1 Zielsetzung

Die Untersuchung bereitet eine autorisierte Lizenzwahl für `r3d_planner` und `r3d_preprocessor` vor. Sie ist eine Forschungs- und Dokumentationsleistung nach der technischen Baseline, keine bereits umgesetzte Open-Source-Freigabe. Verglichen werden Apache-2.0, MIT, BSD-2-Clause und BSD-3-Clause. Die bereitgestellte Recherche favorisiert Apache-2.0; diese Präferenz wird anhand der Lizenztexte, ROS-Dokumentation und konkreter Projektbefunde geprüft.

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

Quellen: [Q09-Q18]. Ein Copyright-Hinweis erzeugt keine Urheberschaft und überträgt keine Rechte. Auch ein persönlicher Hinweis bei tatsächlicher Urheberschaft beweist keine ausschließliche Lizenzierungsbefugnis. Vorhandene Fremdhinweise bleiben bestehen. Es wird kein neuer personenbezogener Header eingefügt und kein unbekannter Autor ergänzt.

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

Die Tabelle beschreibt die Texte [Q01-Q04], nicht die bereits geltende Projektlizenz. „Keine ausdrückliche Klausel“ ist keine Aussage über eine mögliche konkludente Rechtslage im Einzelfall.

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

Die Header-/Templateprüfung war lesend. Namen, Jahreszahlen und bestehende Notices wurden nicht ergänzt oder umgeschrieben. Der persönliche Name ist für nachgewiesene eigene Beiträge grundsätzlich als gewünschte Urheberbezeichnung plausibel; eine zentrale exklusive Rechteinhaberschaft des gesamten Repositorys ist nicht nachgewiesen. Für den eigenen R3D-Funktionscode liegt nun die Erklärung alleiniger Entwicklung vor (11.10). Bekannte Fremdtemplates bleiben davon ausgenommen; Arbeitgeber-/Vertragsrechte und Lizenzierungsbefugnis sind weiterhin nicht unabhängig geprüft.

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

**Gewünschte spätere Form für tatsächlich eigene Beiträge, nur als Dokumentationsbeispiel:**

```text
SPDX-FileCopyrightText: 2026 Bastian Aumer
```

**Nur nach gesonderter Apache-2.0-Freigabe für die betreffenden eigenen Dateien:**

```text
SPDX-License-Identifier: Apache-2.0
```

Beide Zeilen sind ausschließlich Vorschläge innerhalb dieses Protokolls. Kein Sourceheader wurde geändert. Erforderliche Fremdhinweise und vorhandene BSD-Lizenzangaben externer Dateien dürfen nicht durch diese Beispiele ersetzt werden.

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
| r3d_preprocessor | Workspace-interner Analyzer/Publisher im Plannerlaunch | Eigene Projektlizenz noch ungeklärt | Offen | Projektmanifeste und Setup | Workspace-intern | Kein fremder MIT-/BSD-Grant daraus ableiten | Dokumentiert; Rechte/Grant offen |

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

**Ergebnis:** Direkte Bibliotheks-Hauptdeklarationen sind nachvollziehbar erfasst. Eine vollständige transitive SBOM, binäre Lizenzprüfung oder pauschale Kompatibilitätsfreigabe ist nicht erbracht. Es wurde nichts installiert, deinstalliert, aktualisiert oder in package.xml korrigiert; AP03 bleibt NOT STARTED.

### 11.12 Lizenzinventar

Die Inventur umfasst alle 60 zum Eingang versionierten Dateien: die 59 Baseline-Dateien plus das bestehende zentrale V4-Protokoll. Damit sind alle 26 Python-Dateien einzeln erfasst. Die unversionierte historische PDF und das externe Recherche-PDF werden anschließend separat aufgeführt. „Eigenanteil laut Erklärung“ ist eine dokumentierte Zuordnung, keine unabhängige Rechtsprüfung. Für normale Projekttexte ohne ausdrücklichen Hinweis wird keine Lizenz erfunden.

| Dateipfad | Vorhandener Copyright-Hinweis | Vorhandener Lizenzhinweis | Erkennbare Herkunft | Eigenentwicklung / Fremdcode | Möglicher Änderungsbedarf, noch nicht umgesetzt |
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

Auch Dokumentation, Konfiguration und generierte Binärdateien sind im künftigen Distributionsumfang bewusst abzugrenzen. Beide PCDs bleiben unverändert im lokalen Repository; keine Entfernung, Neulizenzierung, zusätzliche Installation oder private/öffentliche Übertragung erfolgt. Eine spätere Lizenzentscheidung muss Code und Daten ausdrücklich unterscheiden.

### 11.13 LiDAR-SLAM-Herkunft

#### 11.13.1 Git-Nachweise und untersuchte Revisionen

Die beiden ausdrücklich benannten öffentlichen Repositories wurden lesend über GitHub sowie in temporären Bare-Objektkopien ohne Checkout/Build untersucht. An den externen Originalrepositorys wurde nichts geändert. Im R3D-Repository betrifft die aktuelle Änderung ausschließlich dieses zentrale Protokoll; Quellcode, vorhandene Branchzuordnungen und Remotes bleiben unverändert. Der R3D-Quellbaum enthält keinen lidar_odom-/lidar_slam_ros2-Implementationstree und kein entsprechendes Submodul. Die externe LiDAR-Software wird deshalb nicht als Bestandteil der beiden R3D-Pakete dargestellt.

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

### 11.15 Modification-Notice-Konzept

Die folgende Notice ist ein **vorbereiteter Dokumentationsentwurf innerhalb dieses Protokolls**, keine angewendete Attribution und keine erzeugte Release-Datei. Original-/Modified-Revision bezeichnen die analysierte Git-Ableitung, nicht einen bestätigten Roboterstand. Die persönliche Änderungszuordnung folgt der Entwicklererklärung zusammen mit den Git-Autorinformationen. Vollständige Drittrechte-/Binärmitnahme bleibt offen.

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
This draft does not replace LICENSE, file headers or third-party notices.
Full binary-distribution compliance: NOT VERIFIED.

Additional Third-Party Component:
ndt_omp_ros2, revision 497411279593eb261a3e3d04cdcbb4717af33ca3
Root license: BSD-2-Clause
Copyright (c) 2019, k.koide
PCL-derived headers: BSD-3-Clause; retain their file-specific notices.
```

Die Formulierung „must be retained“ ist bewusst eine Anforderung an die spätere Distribution; eine ungeprüfte Behauptung, bereits jedes Binärpaket enthalte alle Texte, wäre unzutreffend. Originaltexte/Disclaimer werden durch diese Notice nicht ersetzt. Bei späterer Umsetzung sind betroffene eigene Bearbeitungen, unveränderte fremde Source und vollständige Pflichttexte getrennt zu behandeln. Fehlende Felder bleiben NOT VERIFIED, statt Urheber, Laufzeitstand oder Rechtevereinbarungen zu erfinden.

### 11.16 Patentregelungen

**Lizenztext:** Apache-2.0 Abschnitt 3 betrifft die vom jeweiligen Contributor lizenzierbaren Ansprüche, die sein Beitrag allein oder zusammen mit dem damaligen Werk notwendigerweise verletzt. Für den dort beschriebenen Patentprozess gegen Werk/Contribution endet der entsprechende Patentgrant. Er ist keine Versicherung gegen Patente außenstehender Dritter [Q01]. Die ASF-FAQ erläutert die Begrenzung auf kontrollierte Ansprüche und den Beitragskontext [Q06].

**Bewertung:** Eine ausdrückliche Regel ist für den gewünschten professionellen Weiterverwendungskontext ein begründeter Vorteil. Ihre tatsächliche Wirkung hängt von Contributors und deren Befugnissen ab. Weder eine Patentlandschaft noch Arbeitgeberpatente wurden untersucht. Das Ergebnis ist daher eine Lizenzpräferenz, kein Patentfreigabenachweis. Fehlende ausdrückliche MIT-/BSD-Klauseln werden nicht mit einem nachgewiesenen Verzicht auf sämtliche denkbaren Patentrechte gleichgesetzt.

### 11.17 ROS-2-Release-Anforderungen

Die ROS-2-Dokumentation empfiehlt Apache-2.0 für neue Projekte, auch im Vergleich zur früheren BSD-Empfehlung. Für übernommenen Code fordert der Migrationsleitfaden den Erhalt bestehender Beiträge/Lizenzen und verweist bei einer Änderung auf erforderliche Contributor-Erlaubnisse. Dies stützt eine Präferenz, keine verbindliche Apache-Pflicht für jedes ROS-Paket [Q22].

Die rosdistro-Kriterien betreffen OSI-Lizenztext, zutreffende package.xml-Deklaration und öffentlich zugängliche Quellen für die Aufnahme. Eine private Entwicklungsphase ist damit vereinbar; sie ist noch kein öffentlich registrierbarer V4-Source-Stand [Q07]. REP-149 erlaubt mehrere License-Tags, wenn das Paket unterschiedliche lizenzierte Sourcebestandteile enthält. Externe Bibliotheksimporte werden nicht pauschal als weitere Lizenz des eigenen Sourcecodes in jedes Manifest kopiert [Q08].

Künftige SPDX-Angaben müssen mit dem autorisierten Lizenz- und Distributionsumfang übereinstimmen. Setup und XML werden in dieser Aufgabe nicht angeglichen. Unabhängige rosdep-/Build-/Installationsprobleme bleiben bestehen; AP03 beginnt nicht.


ROS Index und Bloom-/Buildfarm-Eignung hängen auch bei einer passenden Lizenz von den bereits dokumentierten technischen Voraussetzungen ab. Die externe LiDAR-Komponente wird nicht allein durch ihren BSD-Text als releasefähig erklärt. Keine Release-Dateien oder LICENSE-Dateien entstehen in dieser Analyse.

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
| Rechtliche Unsicherheit / U | Rechte/Karten/Verträge offen | Rechte/Karten/Verträge offen | Rechte/Karten/Verträge offen | Rechte/Karten/Verträge offen | Unverzichtbares Gate, aktuell kein finaler Sieger |

**Sensitivität:** Würde das Projekt ausschließlich minimale Text-/Pflegepflichten bevorzugen und keine ausdrückliche Patentregelung verlangen, könnten MIT oder BSD-2-Clause vorrangig sein. BSD-3-Clause wäre bei gewünschter expliziter Non-Endorsement-Bedingung nachvollziehbar. Unter der hier gewählten Präferenzordnung ist Apache-2.0 der bevorzugte Kandidat. Die Matrix macht diese Abhängigkeit sichtbar, statt die Präferenz als Rechtszwang darzustellen.

### 11.19 Lizenzempfehlung

**Unverbindliche Empfehlung: Apache-2.0 für die autorisierbaren eigenen Softwarebestandteile beider Pakete.** Ausschlaggebend sind die belegte ROS-Neuprojektempfehlung und der ausdrückliche begrenzte Patentgrant. Die zusätzliche Hinweis-/Änderungspflege wird unter den offengelegten Projektpräferenzen als tragbarer Aufwand bewertet. Eine statistische Behauptung über Verbreitung im gesamten professionellen Robotikmarkt wird mangels entsprechender Untersuchung nicht als eigenständiger Nachweis verwendet [Q01/Q22].

Die Empfehlung ist bedingt: Fremdtemplates behalten ihre Hinweise; Code- und Kartenrechte, konkrete Binärpakete und Contributor-Befugnisse müssen geklärt werden. Das bereits vorhandene Apache-Setupfeld ist ein technischer Bestandsbefund, nicht die Autorisierung dieser Empfehlung. MIT und beide BSD-Varianten bleiben ernsthafte Alternativen. Eine verbindliche Entscheidung, Rechtsfreigabe oder Lizenzimplementierung wurde nicht getroffen.


Die vom Entwickler vorgesehene Aufteilung ist technisch und nach den gelesenen Lizenzbedingungen **grundsätzlich plausibel**, sofern Befugnisse und tatsächlicher Distributionsumfang geklärt sind. Sie ist keine bereits getroffene oder umgesetzte Gesamtentscheidung:

| Bestandteil | Vorgesehene Strategie | Grenze / Voraussetzung |
| --- | --- | --- |
| Eigener r3d_planner-Code | Apache-2.0 als bevorzugter Kandidat, persönliche Attribution Bastian Aumer | Erklärung dokumentiert; Vertrags-/Arbeitgeberbefugnis und technische Anwendung offen |
| Eigener r3d_preprocessor-Code | Gleicher bevorzugter Kandidat, persönliche Attribution Bastian Aumer | Keine automatische Erstreckung auf Karten/Fremdtemplates |
| ROS-Testtemplates | Bestehende Apache-2.0-/OSRF-Hinweise vollständig erhalten | Eigene Attribution nicht an Stelle fremder Namen einsetzen |
| Ursprünglicher LiDAR-SLAM-Code | Originale BSD-2-Clause und Copyright Ryohei Sasaki erhalten | PCL-/NDT-Dateien mit eigenen Bedingungen zusätzlich beachten |
| Eigene LiDAR-Bearbeitungen | Bastian Aumer separat attributieren; vorhandene BSD-2-Clause-Deklaration nicht stillschweigend durch R3D-Apache ersetzen | Präziser Änderungs-/Dateiumfang und Freigabe erforderlich |
| Externe ROS-/Python-Bibliotheken | Jeweilige Originallizenzen/Notices beachten | Imports vs mitgelieferte Binaries/Source unterscheiden |
| PCD-Karten und weitere Daten | Gesonderte Rechte-/Lizenzentscheidung | Herkunft/Freigaben fehlen; keine Standard-MIT-/Apache-Lizenz behaupten |

Die zwei R3D-Pakete und das separate LiDAR-Repository müssen daher nicht unter einen künstlich vereinheitlichten Gesamtgrant gestellt werden. Bei einem gemeinsamen Bundle sind dennoch alle tatsächlich enthaltenen Source-/Binärbedingungen einzuhalten. Die neue Entwicklererklärung wird berücksichtigt, ohne unbekannte Arbeitgeber- oder Vertragsrechte wegzudefinieren.

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
| R07 | Wer erzeugte/stellte die rohe und analysierte PCD bereit, mit welchen Aufnahme-/Nutzungsbedingungen? | Datenherkunft, Berechtigte, Bearbeitungs-/Weiterverteilungsfreigabe, gegebenenfalls separate Datenlizenz |
| R08 | Enthalten Karten oder andere Artefakte zusätzliche sensible/vertrauliche Inhalte oder Drittmaterial? | Inhalts-/Vertragsprüfung nach tatsächlicher Herkunft; derzeit nicht bestimmbar |
| R09 | Welche exakten Dependencies/Artefakte werden beim späteren Release tatsächlich mitgeliefert? | Versions-/Plattforminventar, mitzugebende Texte/Notices und gegebenenfalls besondere Binärbedingungen |
| R10 | Gibt es bekannte Patentansprüche oder Rechtebeschränkungen bei Beitragenden/Arbeitgebern? | Gezielte Auskunft; keine allgemeine Patentfreiheit behaupten |
| R11 | Wie werden künftige externe Beiträge und deren Berechtigungsbestätigung behandelt? | Passende Contribution-Regel; CLA/DCO nur bewusst wählen, keine Urheberrechtsübertragung voraussetzen |
| R12 | Soll der persönliche Name nur eigene Beiträge bezeichnen und wie bleiben fremde Attributionen erhalten? | Autorisierte Header-/Attributionsstrategie; keine pauschale exklusive Eigentümerschaft am Gesamtrepository |
| R13 | Welche Lizenz gilt schließlich für Code, Dokumentation und Daten jeweils? | Ausdrückliche Entscheidung nach relevanter Rechteklärung; gesonderte technische Umsetzungsfreigabe |
| R14 | Welche lidar_odom-/NDT-/Systemrevision ist tatsächlich im Zieldeployment eingesetzt? | Dokumentierter Build-/Deploymentstand; Server-Defaulttip allein genügt nicht |
| R15 | Wie werden Root-BSD-2-Clause, PCL-BSD-3-Clause, Eigen-/Runtimebedingungen und Notices bei gemeinsamer Binärverteilung erfüllt? | Konkrete Artefakt-/Packagingprüfung, keine pauschale Library-Kompatibilität |
| R16 | Soll die vorbereitete Modification Notice später im externen Repository oder einem Bundle angewendet werden? | Neue ausdrückliche Freigabe, genaue Dateizuordnung und vollständige Originaltexte |

### 11.21 Vorgesehene Lizenzimplementierung

| Teilaufgabe von AP01 | Aktueller Stand | Status |
| --- | --- | --- |
| Vier Lizenztexte und Primärquellen vergleichen | Vergleich und Korrekturen dokumentiert, IDs und Methodik geprüft | VERIFIED - begrenzte Rechercheabnahme |
| Vorhandene Copyright-/Template-Hinweise untersuchen | Header, sechs Templates und technische Provenienz gelesen/abgeglichen | VERIFIED - keine rechtliche Rechtekettenabnahme |
| Direkte Dependency-Hauptlizenzen erfassen | Quellen und lokale Metadaten erfasst; Binär-/transitive Grenzen benannt | VERIFIED - Deklarationsebene |
| Rechtekette Code / Contributors / Arbeitgeber / Karten | Erklärung liegt vor; Vertrags-/Karten-/Befugnisfragen und R14-R16 offen | BLOCKED |
| Vollständiger konkreter Distributions-/Artefaktaudit | Noch nicht durchgeführt | NOT STARTED |
| Verbindliche Lizenzentscheidung | Nutzerentscheidung nach Rechteklärung fehlt | BLOCKED |
| Technische Lizenzanwendung | Nicht beauftragt; keine Dateien/License-Tags/Header geändert | NOT STARTED |
| AP01 insgesamt | Recherche ist integriert, Voraussetzungen des Gesamtabschlusses fehlen | BLOCKED |

Die Forschungsergebnisse können als verifizierter Vergleich verwendet werden. Das Projekt darf dadurch nicht als bereits „unter Apache-2.0 freigegeben“ beschrieben werden. Weder eine Lizenzdatei noch eine pauschale Kompatibilitätsfreigabe oder ein Release entsteht. Erst eine neue ausdrückliche Entscheidung und Umsetzungsfreigabe erlaubt die technische Anwendung.


#### 11.21.1 Vorgesehene technische Maßnahmen nach späterer Freigabe

Erst nach einer neuen ausdrücklichen Entscheidung wären der autorisierte Lizenztext, zutreffende Manifest-/Setup-Angaben, eigene SPDX-Attribution und Dateilizenzbezüge zu ergänzen. Dabei sind sechs Fremdtemplates, externe BSD-Dateien, eigene Bearbeitungen und Karten getrennt zu behandeln. Gegebenenfalls erforderliche Third-Party-Texte/Notices und eine angewendete Modification Notice müssten im tatsächlichen Source-/Binär-/Installationsumfang nachgewiesen werden. Diese Liste ist geplant, nicht durchgeführt.

**Abgrenzung der abgeschlossenen Recherche:** Vergleich, Primärquellenabgleich, Copyright-/Dateiinventur und Git-basierte LiDAR-Analyse sind für den angegebenen Umfang verifiziert. Persönliche Alleinentwicklung ist dokumentiert, Lizenzstrategie abgeleitet. Verbindliche Entscheidung, Implementierung, konkrete Deploymentrevision und vollständige Binär-/Vertragsabnahme bleiben offen. AP01 bleibt insgesamt BLOCKED; AP08/AP10 IN PROGRESS; AP02/AP03 NOT STARTED.

### 11.22 Quellenverzeichnis

Alle folgenden Quellen wurden am **13. Oktober 2026** gelesen, sofern nicht ausdrücklich ein gescheiterter Webzugriff mit lokalem Ersatz genannt ist. Die Lizenztexte sind maßgeblich; deutsche Zusammenfassungen sind Auswertungen. Versions-Tags sind konkrete Upstream-Referenzen, Humble-/main-Links bewegliche Stände. Die Quellenliste enthält keine erfundenen URLs aus den unauflösbaren Markern der Sekundär-PDF.

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

Entwicklererklärung: ergänzter Nutzerauftrag vom 13.10.2026, dokumentiert in 11.10; kein unabhängiger Rechtsnachweis. GitHub-Sichtbarkeits-/Remotequellen stehen separat in Abschnitt 12. Fremde Repository-AGENTS-Dateien wurden ausschließlich als Sourceinhalt betrachtet; keine dortigen Software-/Buildanweisungen ausgeführt. Der einzige Projekt-Schreibzugriff dieser Aufgabe betrifft dieses zentrale Dokument.

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
