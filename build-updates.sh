#!/bin/bash
# =============================================================================
# build-updates.sh — pipeline de updates contínuos do CapivaraOS (FEAT-114).
# =============================================================================
# Reconstrói os RPMs PRÓPRIOS do desktop (branding, COS Dev Center, repos e
# upgrade) e, opcionalmente, os assina e adiciona ao canal `testing` do repo
# assinado da versão corrente (via publish-repo.sh). Fluxo completo:
#
#   ./build-updates.sh                 # só builda os 4 (não precisa da chave)
#   ./build-updates.sh --stage         # builda + assina + add ao testing
#   ./publish-repo.sh promote --rel N  # depois do QA, promove testing -> stable
#   ./publish-repo.sh upload  --rel N  # sobe para o host
#
# --rel N     versão Fedora do repo de destino (padrão: rpm -E %fedora, a atual)
# --stage     assina e adiciona ao testing (exige a chave privada; ver keys/README.md)
#
# A NEVRA exata de cada pacote sai do próprio .spec (rpmspec -q) — mesma
# disciplina do build-all.sh, para não pegar um RPM velho homônimo de outra spin
# no ~/rpmbuild compartilhado (BUG-30).
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REL="$(rpm -E %fedora)"
STAGE=0
CHANNEL=testing

while [ $# -gt 0 ]; do
    case "$1" in
        --rel)     REL="$2"; shift 2;;
        --channel) CHANNEL="$2"; shift 2;;
        --stage)   STAGE=1; shift;;
        -h|--help) sed -n '2,25p' "$0"; exit 0;;
        *) echo "opção desconhecida: $1" >&2; exit 2;;
    esac
done

# Pares (spec | script de build) dos pacotes próprios do desktop.
SPECS=(
    "${SCRIPT_DIR}/rpm/capivaraos-branding.spec|${SCRIPT_DIR}/rpm/build-rpm.sh"
    "${SCRIPT_DIR}/apps/capivara-central/rpm/capivara-central.spec|${SCRIPT_DIR}/apps/capivara-central/rpm/build-rpm.sh"
    "${SCRIPT_DIR}/rpm/capivaraos-repos.spec|${SCRIPT_DIR}/rpm/build-rpm-repos.sh"
    "${SCRIPT_DIR}/rpm/capivaraos-upgrade.spec|${SCRIPT_DIR}/rpm/build-rpm-upgrade.sh"
)

echo "==> Reconstruindo os pacotes próprios do desktop (updates da versão corrente)…"
for pair in "${SPECS[@]}"; do
    build="${pair#*|}"
    echo "--- ${build} ---"
    "$build"
done

echo
echo "==> Coletando a NEVRA exata de cada pacote…"
RPMS=()
for pair in "${SPECS[@]}"; do
    spec="${pair%%|*}"
    nevra="$(rpmspec -q --qf '%{name}-%{version}-%{release}.%{arch}\n' "$spec" 2>/dev/null | head -1)"
    [ -n "$nevra" ] || { echo "ERRO: não li a NEVRA de ${spec}" >&2; exit 1; }
    rpm_file="$HOME/rpmbuild/RPMS/noarch/${nevra}.rpm"
    [ -f "$rpm_file" ] || { echo "ERRO: RPM esperado não encontrado: ${rpm_file}" >&2; exit 1; }
    echo "    ${nevra}.rpm"
    RPMS+=("$rpm_file")
done

if [ "$STAGE" -eq 0 ]; then
    echo
    echo "==> OK: ${#RPMS[@]} pacote(s) construído(s). Para publicar no canal ${CHANNEL}:"
    echo "      ./build-updates.sh --rel ${REL} --stage      (assina + add; requer a chave)"
    echo "    ou diretamente: ./publish-repo.sh add --rel ${REL} --channel ${CHANNEL} <rpms>"
    exit 0
fi

echo
echo "==> Estagiando no canal ${CHANNEL} (f${REL}) — assina + createrepo + assina repomd…"
"${SCRIPT_DIR}/publish-repo.sh" add --rel "$REL" --channel "$CHANNEL" "${RPMS[@]}"
echo
echo "==> Feito. Próximos passos após o QA em VM:"
echo "      ./publish-repo.sh promote --rel ${REL} --arch x86_64"
echo "      ./publish-repo.sh upload  --rel ${REL} --arch x86_64"
