#!/bin/bash
# Empacota os assets de branding/ num tarball e constroi o RPM
# capivaraos-branding com rpmbuild.
#
# Uso:
#   dnf install -y rpm-build ImageMagick
#   ./build-rpm.sh
#
# O RPM resultante fica em ~/rpmbuild/RPMS/noarch/capivaraos-branding-*.rpm

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
# VERSION sai do proprio .spec -- NAO cravar aqui. Ate 2026-07-21 este valor
# era fixo, e ao subir a Version: do spec sem lembrar de mexer neste arquivo o
# tarball era gravado com o nome ANTIGO. O rpmbuild entao pegava, em silencio,
# um capivaraos-branding-<nova versao>.tar.gz VELHO que estivesse sobrando em
# ~/rpmbuild/SOURCES (o diretorio e compartilhado pelas tres spins) e buildava
# o RPM com os assets errados, sem nenhum erro. Aconteceu de verdade no
# rebrand da Pup 1.1.0, que puxou sources da Marsh 1.1.0 de um mes antes.
VERSION="$(rpmspec -q --qf '%{version}\n' "${SCRIPT_DIR}/capivaraos-branding.spec" 2>/dev/null | head -1)"
[ -n "$VERSION" ] || { echo "ERRO: nao consegui ler Version: do spec" >&2; exit 1; }
NAME="capivaraos-branding"
WORKDIR="$(mktemp -d)"
SRCDIR="${WORKDIR}/${NAME}-${VERSION}"

mkdir -p "$SRCDIR"
cp -r "${PROJECT_DIR}/branding/backgrounds" "$SRCDIR/"
cp -r "${PROJECT_DIR}/branding/icons" "$SRCDIR/"
cp -r "${PROJECT_DIR}/branding/skel" "$SRCDIR/"
cp -r "${PROJECT_DIR}/branding/update-notify" "$SRCDIR/"

mkdir -p "$HOME/rpmbuild/SOURCES" "$HOME/rpmbuild/SPECS"
# Remove um tarball homonimo de build anterior antes de gravar o novo.
rm -f "$HOME/rpmbuild/SOURCES/${NAME}-${VERSION}.tar.gz"
tar -C "$WORKDIR" -czf "$HOME/rpmbuild/SOURCES/${NAME}-${VERSION}.tar.gz" "${NAME}-${VERSION}"
cp "${SCRIPT_DIR}/capivaraos-branding.spec" "$HOME/rpmbuild/SPECS/"

rm -rf "$WORKDIR"

rpmbuild -bb "$HOME/rpmbuild/SPECS/capivaraos-branding.spec"

echo
echo "RPM gerado em: $HOME/rpmbuild/RPMS/noarch/"
ls -1 "$HOME/rpmbuild/RPMS/noarch/" | grep "^${NAME}"
