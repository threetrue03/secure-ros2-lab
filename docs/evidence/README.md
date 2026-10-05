# Evidence to collect after running the lab

No screenshots, logs from live DDS, or packet captures are supplied as simulated
evidence. Save screenshots only after reproducing each observation. Runtime logs
from `make integration-test` go to ignored `artifacts/`.

| Suggested filename | Show |
|---|---|
| 01-insecure-ros-graph.png | Actual `ros2 node list` from the lab attacker container |
| 02-insecure-topic-list.png | Actual topic list and cmd_vel endpoint count |
| 03-insecure-attacker-publish.png | Attacker attempt and publish API logs |
| 04-insecure-motor-result.png | Motor receiving both recognizable command patterns |
| 05-insecure-wireshark.png | Unsecured serialized DDS DATA on the verified bridge |
| 06-secure-legitimate-communication.png | Legitimate commands and permitted status reaching motor |
| 07-secure-attacker-denied.png | Actual middleware behavior and absence of conflicting motor commands |
| 08-secure-wireshark.png | Actual protected data traffic, with context |
| 09-sbom-generation.png | Successful command and nonempty CycloneDX file |
| 10-trivy-scan.png | Actual scan summary, including failures/findings |

Include run time, image digest, host/engine topology and middleware versions in
your evidence notes. Never show key contents or fabricated denial messages.
After every experiment stop the containers with `make down`. `make clean`
deletes generated credentials and reports; preserve wanted evidence separately.
