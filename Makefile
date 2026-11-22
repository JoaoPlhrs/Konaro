# Konaro OS — atalhos. Os scripts em scripts/ são a fonte da verdade.
.PHONY: help lint packages iso iso-clean builder builder-iso test-bios test-uefi

ISO ?= $(firstword $(wildcard build/iso/*.iso))

help:
	@echo "make lint         verificações estáticas"
	@echo "make packages     constrói os .deb próprios (Debian 13)"
	@echo "make iso          gera a ISO (root, Debian 13)"
	@echo "make iso-clean    gera a ISO do zero"
	@echo "make builder      cria o chroot Debian 13 (hosts não-Debian, root)"
	@echo "make builder-iso  gera a ISO dentro do chroot (root)"
	@echo "make test-bios    inicia a ISO no QEMU (BIOS)"
	@echo "make test-uefi    inicia a ISO no QEMU (UEFI)"

lint:
	./scripts/lint.sh
packages:
	./scripts/build-packages.sh
iso:
	./scripts/build-iso.sh
iso-clean:
	./scripts/build-iso.sh --clean
builder:
	./scripts/builder-chroot.sh setup
builder-iso:
	./scripts/builder-chroot.sh build-iso
test-bios:
	./scripts/test-vm.sh $(ISO)
test-uefi:
	./scripts/test-vm.sh --uefi $(ISO)
