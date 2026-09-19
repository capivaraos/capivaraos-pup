#!/bin/bash
# Empacota o app apps/capivara-central num tarball e constroi o RPM
# capivara-central com rpmbuild.
#
# Uso:
#   dnf install -y rpm-build
#   ./build-rpm.sh
#
# O RPM resultante fica em ~/rpmbuild/RPMS/noarch/capivara-central-*.rpm

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(dirname "$SCRIPT_DIR")"                 # apps/capivara-central
PROJECT_DIR="$(dirname "$(dirname "$APP_DIR")")"   # raiz do repo

# VERSION sai do proprio .spec (mesma disciplina do branding: ~/rpmbuild/SOURCES
# e compartilhado, entao um tarball homonimo velho entraria em silencio).
VERSION="$(rpmspec -q --qf '%{version}\n' "${SCRIPT_DIR}/capivara-central.spec" 2>/dev/null | head -1)"
[ -n "$VERSION" ] || { echo "ERRO: nao consegui ler Version: do spec" >&2; exit 1; }
NAME="capivara-central"
WORKDIR="$(mktemp -d)"
SRCDIR="${WORKDIR}/${NAME}-${VERSION}"

mkdir -p "$SRCDIR"
# Codigo + assets do app.
cp -a "${APP_DIR}/capivara-central.py" \
      "${APP_DIR}/backend.py" \
      "${APP_DIR}/capivara-central" \
      "${APP_DIR}/README.md" \
      "$SRCDIR/"
cp -a "${APP_DIR}/data"    "$SRCDIR/"
cp -a "${APP_DIR}/libexec" "$SRCDIR/"
# LICENSE vem da raiz do repo (GPLv3 unico do projeto).
cp -a "${PROJECT_DIR}/LICENSE" "$SRCDIR/"

mkdir -p "$HOME/rpmbuild/SOURCES" "$HOME/rpmbuild/SPECS"
rm -f "$HOME/rpmbuild/SOURCES/${NAME}-${VERSION}.tar.gz"
tar -C "$WORKDIR" -czf "$HOME/rpmbuild/SOURCES/${NAME}-${VERSION}.tar.gz" "${NAME}-${VERSION}"
cp "${SCRIPT_DIR}/capivara-central.spec" "$HOME/rpmbuild/SPECS/"

rm -rf "$WORKDIR"

rpmbuild -bb "$HOME/rpmbuild/SPECS/capivara-central.spec"

echo
echo "RPM gerado em: $HOME/rpmbuild/RPMS/noarch/"
ls -1 "$HOME/rpmbuild/RPMS/noarch/" | grep "^${NAME}"
