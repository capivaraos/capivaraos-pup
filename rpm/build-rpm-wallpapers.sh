#!/bin/bash
# Empacota branding/backgrounds/ num tarball e constroi o RPM
# capivaraos-wallpapers com rpmbuild.
#
# Uso:
#   dnf install -y rpm-build
#   ./build-rpm-wallpapers.sh
#
# O RPM resultante fica em ~/rpmbuild/RPMS/noarch/capivaraos-wallpapers-*.rpm
#
# Este pacote existe para que os 76 MB de wallpaper NAO sejam republicados a
# cada correcao do capivaraos-branding (PROD-187/PROD-188). A Version dele e
# INDEPENDENTE da do branding -- ver o aviso no topo do .spec antes de mexer.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
# VERSION sai do proprio .spec -- NAO cravar aqui. Mesma armadilha do BUG-30
# descrita em build-rpm.sh: ~/rpmbuild/SOURCES e compartilhado pelas tres spins,
# e um tarball homonimo velho entra calado, gerando um RPM com os assets de
# OUTRA spin sem nenhum erro.
VERSION="$(rpmspec -q --qf '%{version}\n' "${SCRIPT_DIR}/capivaraos-wallpapers.spec" 2>/dev/null | head -1)"
[ -n "$VERSION" ] || { echo "ERRO: nao consegui ler Version: do spec" >&2; exit 1; }
NAME="capivaraos-wallpapers"
WORKDIR="$(mktemp -d)"
SRCDIR="${WORKDIR}/${NAME}-${VERSION}"

mkdir -p "$SRCDIR"
cp -r "${PROJECT_DIR}/branding/backgrounds" "$SRCDIR/"

mkdir -p "$HOME/rpmbuild/SOURCES" "$HOME/rpmbuild/SPECS"
# Remove um tarball homonimo de build anterior antes de gravar o novo (BUG-30).
rm -f "$HOME/rpmbuild/SOURCES/${NAME}-${VERSION}.tar.gz"
tar -C "$WORKDIR" -czf "$HOME/rpmbuild/SOURCES/${NAME}-${VERSION}.tar.gz" "${NAME}-${VERSION}"
cp "${SCRIPT_DIR}/capivaraos-wallpapers.spec" "$HOME/rpmbuild/SPECS/"

rm -rf "$WORKDIR"

rpmbuild -bb "$HOME/rpmbuild/SPECS/capivaraos-wallpapers.spec"

echo
echo "RPM gerado em: $HOME/rpmbuild/RPMS/noarch/"
ls -1 "$HOME/rpmbuild/RPMS/noarch/" | grep "^${NAME}"
