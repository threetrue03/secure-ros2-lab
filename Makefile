SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
export LAB_UID := $(shell id -u)
export LAB_GID := $(shell id -g)
IMAGE ?= secure-ros2-lab:jazzy
I := docker compose -f compose.insecure.yaml
S := docker compose -f compose.secure.yaml
.PHONY: help build normal-up insecure-up insecure-logs down secure-setup secure-up secure-logs sbom scan test integration-test clean
help:
	@echo 'build             Build the ROS Jazzy image'
	@echo 'normal-up         Start only the synthetic robot (security disabled)'
	@echo 'insecure-up       Start robot and controlled unauthorized publisher'
	@echo 'insecure-logs     Follow unsecured service logs'
	@echo 'down              Stop all lab services and remove its network'
	@echo 'secure-setup      Generate local credentials (requires empty runtime)'
	@echo 'secure-up         Start all participants with enforced SROS2'
	@echo 'secure-logs       Follow secured service logs'
	@echo 'sbom              Generate CycloneDX JSON using host Trivy'
	@echo 'scan              Scan image using host Trivy; fail on HIGH/CRITICAL'
	@echo 'test              Run repository validation and ROS package tests'
	@echo 'integration-test  Verify both modes with motor logs; always clean up'
	@echo 'clean             Stop lab and delete generated runtime and reports'
build:
	docker build -t $(IMAGE) .
normal-up: down
	$(I) up -d camera perception navigation motor
insecure-up: down
	$(I) --profile attack up -d camera perception navigation motor attacker
insecure-logs:
	$(I) --profile attack logs -f
down:
	$(I) --profile attack down --remove-orphans
	$(S) --profile attack --profile setup down --remove-orphans
secure-setup:
	mkdir -p security/runtime
	$(S) --profile setup run --rm --user "$$(id -u):$$(id -g)" security-setup
secure-up: down
	test -f security/runtime/.ready || { echo 'Run make secure-setup successfully first.' >&2; exit 1; }
	$(S) --profile attack up -d camera perception navigation motor attacker
secure-logs:
	$(S) --profile attack logs -f
sbom:
	bash scripts/generate_sbom.sh $(IMAGE)
scan:
	bash scripts/scan_image.sh $(IMAGE)
test:
	docker run --rm --network none $(IMAGE) bash -c 'python3 /opt/lab/scripts/validate_repo.py --image && python3 -m unittest discover -s /opt/lab/tests -p test_credentials.py -v && cd /opt/lab/ros2_ws && colcon test --event-handlers console_direct+ && colcon test-result --verbose'
integration-test:
	python3 scripts/integration_test.py
clean: down
	python3 scripts/clean.py
