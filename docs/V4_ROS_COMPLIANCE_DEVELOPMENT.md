# R3D-Planner V4
# ROS 2 Compliance Development

Stand: 13. Oktober 2026. Dieses Dokument ist das einzige zentrale Entwicklungsprotokoll für V4. Es trennt den historischen Bestand, geplante Maßnahmen, tatsächlich durchgeführte Änderungen und deren Nachweise. Die Erstinitialisierung verändert ausschließlich dieses Dokument und legt den Branch V4 an. Sie enthält keine Implementierung der Arbeitspakete AP01 bis AP10.

## 1. Zielsetzung

V4 soll die bestehende funktionale R3D-Planner-Implementierung für eine nachvollziehbare öffentliche Bereitstellung im ROS-2-Ökosystem vorbereiten. Gegenstand sind Paketmetadaten, Dependency-Deklarationen und rosdep, Lizenz- und Datenrechte, installationsunabhängige Ressourcen, öffentliche ROS-Verträge, Tests, CI/CD, Nutzungsdokumentation und Releasevorbereitung. Beide Pakete behalten `ament_python` und setuptools. Eine CMake-Konvertierung ist ohne konkreten technischen Bedarf nicht vorgesehen.

PCD-Verarbeitung, Traversierbarkeitsanalyse, Graphrekonstruktion, A*, Navigationseinstiegspunkte und die V3-Integration sind Vorleistungen. V4 werden ausschließlich begründete und nachgewiesene Änderungen nach dem Baseline-Commit zugerechnet. Neue SLAM-/Mappingverfahren, der Ersatz des Planners, ein vollständiges Nav2-Redesign und neue Hardwaretreiber sind keine primären Ziele.

Die Initialisierung ist noch keine Freigabe für Codeänderungen. Gemäß Abschnitt 11 des Auftrags muss der initiale Plan zunächst vorgelegt werden; der Beginn des ersten Implementierungsarbeitspakets benötigt eine ausdrückliche Freigabe. Pushes, Releases und Pull Requests sind nicht beauftragt.

**Nutzerentscheidung vom 13. Oktober 2026:** „Überspringe die Lizenzierung vorerst, hierzu muss ich erst noch recherchieren“. AP01 wird deshalb zurückgestellt und als `BLOCKED` geführt. Diese Entscheidung erlaubt keine Annahme einer Projektlizenz und beseitigt keine Veröffentlichungshindernisse. Unabhängige technische Arbeiten können nach Planfreigabe beginnen. Es wird keine Lizenz ausgewählt, angewendet oder stillschweigend aus `setup.py` übernommen.

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
| Geplante Änderung | Nach Nutzerrecherche Rechtekette und Entscheidung dokumentieren; erst auf autorisierter Grundlage Lizenztext/Deklarationen/Notices und Kartenverteilung umsetzen |
| Priorität | P0 |
| Abhängigkeiten | Verbindliche Rechte-/Lizenzauskunft des Nutzers; Rückstellung am 13.10.2026 ausdrücklich angeordnet |
| Abschlusskriterien | Rechte und Distributionsumfang nachvollziehbar; autorisierte Lizenzentscheidung; konsistente Dateien/Metadaten, mitzugebende Notices geklärt; keine unbelegten Bibliotheks-Kompatibilitätsbehauptungen |
| Aktueller Status | **BLOCKED** - Nutzer recherchiert; vorerst keine Lizenzarbeit; technische APs separat möglich |

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
| Aktueller Status | **IN PROGRESS** - ausschließlich zentrale Initialdokumentation; öffentliche Anleitungen noch unverändert |

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
| Aktueller Status | **IN PROGRESS** - ausschließlich Kriterien-/Blockeraufnahme, keine Releasewerkzeuge ausgeführt |

### 4.12 Abhängigkeitsgerechte Reihenfolge und nächste Freigabe

AP01 bleibt auf Nutzerwunsch zurückgestellt. Als erster separat freizugebender Schritt wird der nichtrechtliche Teil von **AP02** vorgeschlagen: Paketbeschreibungen, sinnvolle URLs und Versionskonsistenz prüfen/korrigieren; Lizenzangaben nicht auswählen oder ändern. Danach folgen **AP03 → AP04 → AP05**, jeweils mit passenden **AP06**-Regressionen und fortlaufender **AP08**-Dokumentation. **AP07** automatisiert erst die stabilisierten Schritte. **AP09** prüft die gewählten Zielumgebungen; **AP10** schließt die Releasevorbereitung erst nach Beseitigung der technischen und rechtlichen Blocker ab.

AP06/AP08 sind keine erst am Ende beginnenden Phasen. AP01 kann später wiederaufgenommen werden und sperrt weiterhin den öffentlichen Releaseabschluss sowie die ungeklärte Mitlieferung von Kartendaten. CI und weitere Distributionen werden nicht vorgezogen, um ungelöste Dependencies oder Installationsverhalten zu verdecken.

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

Die temporären Prüfhilfen liegen außerhalb des Repositorys und sind keine zusätzlichen Entwicklungsberichte. Im Repository entsteht genau ein neues Entwicklungsdokument. Neue Testergebnisse müssen künftig mit vollständigem Befehl, Umgebung, Commit, Exitcode und relevanten Resultaten hier ergänzt werden; Fehler und nicht ausführbare Prüfungen werden ausdrücklich protokolliert.

## 7. Probleme und offene Entscheidungen

| ID | Beschreibung | Auswirkung | Erforderliche Entscheidung | Vorgeschlagene Lösung | Aktueller Status |
| --- | --- | --- | --- | --- | --- |
| O01 | Projektlizenz und Code-Rechtekette ungeklärt | Source-/Binärveröffentlichung nicht freigabefähig | Nutzer recherchiert autorisierte Rechte-/Lizenzgrundlage | AP01 zurückstellen, danach Entscheidung und Nachweise hier erfassen; nichts aus Setup ableiten | BLOCKED - vom Nutzer am 13.10.2026 zurückgestellt |
| O02 | Herkunft/Rechte der zwei PCD-Karten ungeklärt | Gebündelte Datendistribution offen; keine ungeprüfte Installationsmitnahme | Dürfen Daten verteilt werden; wenn ja unter welchen Bedingungen? | Bis Klärung keine neue Datenverteilung; Portabilität später mit synthetischen Fixtures und Nutzerpfaden prüfen | BLOCKED - Teil der zurückgestellten Rechteklärung |
| O03 | Initialer Plan muss vor Implementierung geprüft werden | Noch keine Code-/Metadatenarbeit autorisiert | Freigabe des ersten nichtrechtlichen AP02-Schritts | Dieses initiale Dokument und die Reihenfolge vorlegen, ausdrückliche Zustimmung abwarten | NOT STARTED - Freigabe ausstehend |
| O04 | 0.0.0 vs 0.0.1, keine Versionspolitik | Unklare Releaseidentität | Konsistente Paketversion und spätere Stabilitätszusagen | AP02 vereinheitlicht nach abgestimmter Entscheidung; Branch V4 nicht zu SemVer 4.0 erklären | NOT STARTED |
| O05 | Aktiver Conda-Python 3.14.6 neben System-Python 3.10.12 | Mögliche nichtrepräsentative ROS-/Packaging-Tests | Reproduzierbare isolierte Humble-Testumgebung wählen | Explizites System-Python/saubere Umgebung; keine globale Apt-/pip-/Conda-Reparatur ohne Erklärung | NOT STARTED |
| O06 | Aktuelle System-/ROS-Keys und Python-TF2-Provider unvalidiert | rosdep-/Buildfarm-Nachweis fehlt | Geeignete verfügbare Dependencies für Humble/Jammy | AP03 resolve/check plus vollständige Installation in isolierter Umgebung; keine Skip-Endlösung | NOT STARTED |
| O07 | Config-/Karten-/Ausgabepolitik auf Sourceentwicklung zugeschnitten | Copy-Installation bricht oder erwartet Sourcepfade | Default-Ressourcen, Nutzeroverride und beschreibbare Ausgaben festlegen | AP04 minimalen Vertrag entwerfen und vorhandene Validierung beibehalten; Datenrechte getrennt | NOT STARTED |
| O08 | Narrow-Flag in Orientierung, Namespaces/Clouds/Actiongrenzen | Öffentliche API-Korrekturen können bestehende Verbraucher beeinflussen | Neuer Metadaten-/Kompatibilitätsvertrag je Änderung | AP05 kleinere Änderungen; alle internen Verbraucher und Nutzeranleitungen gemeinsam anpassen; Regressionen | NOT STARTED |
| O09 | Filter/Follower-Systemgrenzen und Kalibrierungsannahmen | Keine generische sichere Navigation aus Detektionscode ableitbar | Gewünschten unterstützten Systemvertrag abgrenzen | Konkrete Sourcebefunde und synthetische No-Motion-Prüfungen priorisieren; keine neue Navigation pauschal beauftragen | NOT STARTED |
| O10 | Historisches PDF weiterhin unversioniert | Spätere frische Clones enthalten die Baseline-Dokumentation nicht | Soll das unveränderte PDF später versioniert oder anderweitig dauerhaft referenziert werden? | Bestehende Datei zunächst unverändert erhalten; später separate bewusste Dokumentationsentscheidung | NOT STARTED |
| O11 | CI-Fernlauf, weitere Distributionen und Pflegezuständigkeiten unbestätigt | Kein neuer CI-/Support-/Releaseerfolg behauptbar | Zielmatrix, Maintainerzusagen und spätere Veröffentlichung autorisieren | Erst Humble; weitere Ziele nach Prüfung; kein ungefragter Push für CI | NOT STARTED |
| O12 | Lizenzinformationen externer Bibliotheken nicht im Projekt enthalten | Gesamtverteilbarkeit/Notices nicht abschließend bestimmt | Spätere Prüfung konkreter Bibliotheks-/Paketversionen und Distribution | Zu AP01 zurückstellen; Libraries werden nicht allein aufgrund allgemeiner Bekanntheit lizenzrechtlich bewertet | BLOCKED - rechtliche Recherche zurückgestellt |

Die technische Vorbereitung darf die zurückgestellte Lizenzentscheidung nicht ersetzen. O01/O02/O12 blockieren den öffentlichen Abschluss, nicht jede unabhängige technische Änderung. Bei neuer Information wird der jeweilige Status mit Datum und Nachweis aktualisiert; frühere Einschränkungen bleiben historisch nachvollziehbar.

## 8. Versionsvergleich: main → V4

Vergleichsreferenz bleibt der festgeschriebene Baseline-Commit, nicht ein später eventuell weiterentwickeltes main. „Unverändert“ bezieht sich auf diesen initialen V4-Stand. Erst ausgeführte Folgeänderungen dürfen diese Spalte erweitern.

| Bereich | Ausgangsstand main | Änderung V4 | Ergebnis | Nachweis |
| --- | --- | --- | --- | --- |
| Entwicklungslinie | main bei `c65642f…`; V1/V2/V3 als Remote-Tracking-Refs | Lokaler Branch V4 unmittelbar von Baseline; ein fokussierter Initial-Dokumentationscommit | Neue getrennte Entwicklungslinie, bestehende Refs unverändert | V4-001, T01/T06, Git-Parent/Refvergleich |
| Forschungsdokumentation | Historischer 33-seitiger Bericht und vorhandene Projektdokumentation | Ein zentrales deutsches V4-Protokoll mit Befunden, APs, Teststatus und Release-Gates | Vorbestand und geplante V4-Leistung trennbar | V4-001/T05; dieses Dokument |
| Historische PDF | Unversionierte konsolidierte Baseline-Dokumentation | Keine Änderung, keine Aufnahme in den Initialisierungscommit | SHA-256 unverändert; weitere Versionierungsentscheidung O10 offen | T02, Abschnitt 2.1 |
| Planung/Preprocessing | Vorhandene PCD-/Voxel-/Traversierbarkeits-/Graph-/A*-Funktionen | Keine | Bestehende Algorithmen erhalten, kein neuer Algorithmusbeitrag | T02; Abschnitt 2.3 |
| Paketmetadaten | Namen/Buildtyp/Maintainer vorhanden; Version/Beschreibung/Lizenz uneinheitlich | Nur Defizite dokumentiert | AP02 noch nicht umgesetzt | B03/AP02 |
| Dependencies | Teildeklaration, fehlende Imports, Skip-Workaround | Nur Abgleich und Planung | Keine Manifest-/Systemänderung, rosdep nicht neu geprüft | T04/T10; B04-B06 |
| Build/Installation | setuptools/ament_python, vorhandene Scripts/Ressourcen; Copy-Config eingeschränkt | Keine | AP04 offen | B07/B08/T11/T15 |
| ROS-Interfaces | Action/Topics/Service, RViz, Filter/Follower; bekannte Semantikgrenzen | Keine | AP05 offen; keine stillen API-Änderungen | B09-B13/T16 |
| Konfiguration/Launch | Zentrale validierte YAML, Robotprofile, vier installierte Launches | Keine | Bestand, nicht neue V4-Funktionalität | Abschnitt 2.3; T02 |
| Odometry/TF | Standardisierte Poseeingabe, Frische/Frames, use_start, Poseverlust-Nullbefehl | Keine | V3-Vorleistung erhalten | Abschnitt 2.3; T02 |
| Tests/Lint | Funktionale Fälle und Linter-Templates bereits vorhanden | Nur Dokument-/Statische Prüfungen der Initialisierung | Keine neuen funktionalen Tests oder Lintkorrekturen | T03/T05; T12-T16 noch nicht ausgeführt |
| Lizenzierung/Datenrechte | Setupstring, TODO-Manifeste, Notices; Rechte ungeklärt | Rückstellung auf ausdrücklichen Nutzerwunsch protokolliert | Weiterhin ungelöster Releaseblocker | AP01/O01/O02/O12 |
| CI/CD | Keine Pipeline | Keine | AP07 offen | T18 |
| Kompatibilität | Humble als Ziel dokumentiert | Lokale OS-/Python-Präsenz erfasst, keine ROS-Ausführung | Kein neues Supportversprechen | T17/O05 |
| Release | Kein hier belegter Index-/Bloom-/Buildfarmabschluss | Kriterien und Blocker getrennt erfasst | NOT READY; keine Veröffentlichung | Abschnitt 9 |

## 9. Veröffentlichungsstatus

| Gegenstand | Status | Begründung und nächster erforderlicher Nachweis |
| --- | --- | --- |
| ROS Index source readiness | **NOT READY** | LICENSE/Manifest-Lizenz ungeklärt; Nutzerrecherche ausstehend. Paketnamen lexikalisch gültig, aktuelle Öffentlichkeit/Namenskollision und externe Reviewentscheidung nicht erneut verifiziert. AP01/AP02/AP10 |
| rosdep readiness | **NOT READY** | Direkte Manifestlücken und dokumentierter Skip-Workaround; vollständige aktuelle Humble-Auflösung/Installation/check nicht ausgeführt. AP03 |
| Bloom readiness | **NOT READY** | Rechte/Metadaten/Dependencies, Versionskonsistenz, Changelogs und installierter Betrieb offen; kein Release-Repository/-Track in dieser Ausführung geprüft/angelegt. AP01-AP04/AP08/AP10 |
| Buildfarm readiness | **NOT READY** | Reproduzierbarer Clean-Copy-Build-/Install-/Testnachweis fehlt, bekannte Installationsgrenzen und Releaseblocker bestehen. Keine Farmjobs ausgeführt. AP03/AP04/AP06/AP10 |
| Tatsächliche offizielle Index-/Binärveröffentlichung | **NOT VERIFIED** | Keine neue rosdistro-/Release-/Buildfarm-Statusabfrage oder externe Bestätigung; historische Abwesenheit nicht als aktuelle Serverprüfung ausgeben |
| ROS 2 Humble / Ubuntu 22.04 / Python 3.10 | **NOT VERIFIED** | Primäres dokumentiertes Ziel; historisch berichtete Tests, aber kein neuer vollständiger Clean-Nachweis für V4 |
| Jazzy / neuere ROS-Distributionen / andere Plattformen | **NOT VERIFIED** | Keine neue Ausführung, keine Supportzusage; weitere Ziele erst nach Auswahl und Prüfung |

`READY` darf erst vergeben werden, wenn die konkret definierten Voraussetzungen für den jeweiligen Bereich nachgewiesen sind. `NOT READY` benennt bekannte Hindernisse, `NOT VERIFIED` fehlende Prüfung. Eine erfolgreich konfigurierte lokale Pipeline ist noch keine externe Veröffentlichung und noch kein erfolgreicher Buildfarm-Lauf.

Die verbleibenden grundlegenden Release-Gates sind: autorisierte Code-/Datenverteilung, zutreffende konsistente Paketmetadaten, vollständige plattformspezifische Dependencies, funktionsfähige installierte Ressourcen und nachvollziehbare Version-/Releasevorbereitung. Die V4-Projektziele zu Schnittstellen-/Test-/CI-Qualität werden zusätzlich verfolgt; fehlende optionale Tools sind keine erfundenen separaten Indexblocker. AP01 bleibt zurückgestellt, bis die Nutzerrecherche eine belastbare Grundlage liefert.

## 10. Abschließende Bewertung

**Vorläufig.** V4 enthält bislang ausschließlich die getrennte Entwicklungslinie und deren initiales Protokoll. Vorhandene Algorithmen, ROS-Schnittstellen, vier Launches, YAML-/Odometry-/TF-Integration und Bestandsprüfungen wurden weder neu implementiert noch verändert. Der initiale Beitrag besteht in Baselineschutz, nachvollziehbarer Anforderungs-/Blockerzuordnung, priorisierter Planung und überprüfbaren Nachweiskriterien.

Die finalen technischen Ergebnisse sind noch offen. Die spätere Bewertung muss jede behauptete Verbesserung auf konkrete V4-Änderungs-IDs, Commits und tatsächlich ausgeführte Prüfungen zurückführen und mit dem Baseline-Commit vergleichen. Historische Testergebnisse, ungeklärte Rechtsfragen und nicht verifizierte Distributionen bleiben entsprechend markiert. Bis zur ausdrücklichen Freigabe des ersten nichtrechtlichen AP02-Schritts werden keine Implementierungsphasen begonnen; die Lizenzierung ist zusätzlich auf Nutzerwunsch vorerst zurückgestellt.
