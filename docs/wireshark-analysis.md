# DDS / RTPS traffic analysis

Capture only this project's local Docker bridge traffic. This procedure performs
no scanning and needs no capture capability inside the application containers.

## Find the capture interface

On native Linux, inspect `docker network inspect secure_ros2_lab` after starting
the lab. Record its network ID, subnet, container addresses and any configured
bridge interface. Run `ip -brief link` and `dumpcap -D` on the Docker host; identify
the bridge corresponding to that network (Docker often derives a bridge name
from the network ID, but do not assume an interface name). Wireshark's capture
interface list shows traffic activity and addresses. Capture on the actual
bridge or its associated veth interface and confirm that packets correspond to
the addresses shown in the network inspection.

Docker Desktop's Linux engine runs inside a VM. A Windows Ethernet interface
usually cannot observe traffic entirely between containers on its internal
bridge. WSL2 distributions, Windows, and the Docker engine may have different
network namespaces. If the interface is absent from your Wireshark/dumpcap list,
do not assume there is no DDS traffic. Use native Linux for this exercise or a
capture mechanism supported by your Docker Desktop/WSL deployment, running in
the engine's network namespace with only capture access. Do not switch the
application services to host networking or grant them NET_ADMIN to obtain evidence.
No packet capture was performed on the originating Windows host.

## Capture unsecured traffic

1. Run `make insecure-up` and note the network/container addresses.
2. Start Wireshark on the confirmed local bridge interface. Capture long enough
   for discovery and repeated camera, navigation and attacker messages.
3. Use the display filter `rtps`, the Wireshark RTPS protocol dissector name.
   If packets are not recognized, confirm interface/address selection and
   inspect UDP packets before using Decode As RTPS. Do not infer encryption
   from absent decoded packets.
4. Inspect RTPS discovery and DATA submessages. DDS payloads use serialized CDR
   representations; they are not necessarily plain English. Strings may be
   readable, but numeric Twist fields require type-aware decoding or careful
   inspection of serialization. Topic names may appear in discovery traffic.
5. Save a local capture and screenshot of relevant decoded packets. Run `make down`.

## Capture secured traffic

1. Run `make secure-setup` once, then `make secure-up`.
2. Rediscover the current bridge interface and container addresses: recreated
   networks may have new IDs and interfaces.
3. Capture both startup and steady-state traffic using the same procedure and
   `rtps` display filter. Review protected/security submessages and identity
   exchange where the installed Wireshark dissector supports them.
4. Compare application data inspection against the unsecured capture. Protected
   message contents should no longer be inspectable in the same way. Discovery
   metadata and traffic timing can remain visible. Not all UDP traffic is
   expected to disappear or become unreadable.
5. Save actual packet evidence and the motor/attacker logs. Confirm legitimate
   delivery, status delivery and denied command delivery separately from capture.
6. Run `make down` when done.

RTPS display decoding alone does not prove every topic is encrypted. Check the
generated governance `data_protection_kind`, signed policy deployment, and the
actual application DATA paths. Setup rejects governance without encryption or
access checks. Never label an unsecured payload screenshot as secured evidence.

## Evidence checklist

Record OS, Docker engine location, capture interface, image digest, middleware
version (`ros2 pkg xml rmw_fastrtps_cpp` inside a service), run time, topic, and
relevant packet numbers. Keep packet files local and ignored by Git. Screenshots
should show the mode and observation without private credentials.

Reference: [Wireshark RTPS display filter fields](https://www.wireshark.org/docs/dfref/r/rtps.html).
