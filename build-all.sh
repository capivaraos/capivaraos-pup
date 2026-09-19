#!/bin/bash
# Build completo do CapivaraOS Pup (Fedora 45 Xfce): instala dependências,
# gera o RPM capivaraos-branding, monta um repositório local com ele e
# constrói a ISO live com livemedia-creator.
#
# Requer privilégios de root (dnf install + livemedia-creator --no-virt) e
# acesso à rede (pacotes do Fedora). Recomenda-se rodar num terminal
# interativo (a senha do sudo será solicitada e o build pode levar bastante
# tempo).
#
# Uso:
#   ./build-all.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR=/var/tmp/capivaraos-pup-repo
RESULT_DIR=/var/tmp/capivaraos-pup-result
ISO_NAME=CapivaraOS-Pup-2.0.0-alpha1-x86_64.iso

echo "==> 1/4: Instalando dependências (lorax, rpm-build, ImageMagick, git, createrepo_c)..."
sudo dnf install -y lorax rpm-build ImageMagick git createrepo_c

echo "==> 2/4: Construindo RPM capivaraos-branding..."
"$SCRIPT_DIR/rpm/build-rpm.sh"

echo "==> 3/4: Criando repositório local em ${REPO_DIR}..."
# BUG CORRIGIDO (2026-06-25): ~/rpmbuild/RPMS/noarch/ acumula RPMs
# "capivaraos-branding" de TODAS as spins buildadas na mesma máquina (Marsh,
# Pup, Snout). Um filtro só por "${PKG_VERSION}-*.rpm" não basta -- Pup e
# Snout usam a MESMA Version (1.0.0), e em um build real o dnf instalou
# silenciosamente o RPM do Pup no lugar do Snout (Release mais alto "ganha"
# na comparação de NEVRA, mesmo em pacotes de spins diferentes). Agora
# resolvemos a NEVRA EXATA deste spec (Version E Release) via "rpmspec -q",
# garantindo que copiamos só o RPM desta spin.
NEVRA=$(rpmspec -q --qf '%{name}-%{version}-%{release}.%{arch}\n' "$SCRIPT_DIR/rpm/capivaraos-branding.spec" | head -1)
RPM_FILE="$HOME/rpmbuild/RPMS/noarch/${NEVRA}.rpm"
[ -f "$RPM_FILE" ] || { echo "ERRO: RPM esperado não encontrado: ${RPM_FILE}" >&2; exit 1; }
sudo rm -rf "$REPO_DIR"
mkdir -p "$REPO_DIR"
cp -v "$RPM_FILE" "$REPO_DIR/"
createrepo_c "$REPO_DIR"

echo "==> 4/4: Gerando ISO com livemedia-creator (pode levar bastante tempo)..."
sudo rm -rf "$RESULT_DIR"

# O anaconda (rodando via --no-virt/unshare) resolve "%include caminho.ks"
# em relação ao seu próprio cwd, que não é o diretório deste projeto — por
# isso "achatamos" o kickstart num único arquivo sem %include antes de
# chamar o livemedia-creator. Ver kickstart/ks-flatten.py.
FLAT_KS=/var/tmp/capivaraos-pup-flat.ks
sudo rm -f "$FLAT_KS"
( cd "$SCRIPT_DIR/kickstart" && python3 ks-flatten.py capivaraos-pup.ks > "$FLAT_KS" )

LIVEMEDIA_LOG="$SCRIPT_DIR/livemedia.log"

sudo livemedia-creator --ks="$FLAT_KS" \
    --no-virt --resultdir="$RESULT_DIR" \
    --logfile="$LIVEMEDIA_LOG" \
    --project="CapivaraOS Pup" --make-iso --iso-only \
    --iso-name="$ISO_NAME" \
    --volid="CapivaraOS Pup 2.0.0 alpha1" --variant="CapivaraOS Pup" \
    --releasever=45

# ── Trava contra ISO sem os updates do Fedora (BUG-29) ─────────────────────
# As ISOs 1.1.2/1.1.3 da spin Marsh saíram só com o Fedora 44 GA porque o repo
# de updates não foi aplicado na composição — o nome "updates" é reservado
# pelo Anaconda e o repo era ignorado em silêncio (ver
# kickstart/upstream/fedora-repo.ks). Sem esta trava, uma ISO desatualizada
# passa batido até o usuário ver ~1000 pacotes de update no primeiro boot.
# Comparamos o kernel que entrou na ISO com o mais novo do repo de updates.
echo
echo "==> Verificando se a ISO recebeu os updates do Fedora..."
ISO_KERNEL=$(grep -o "vmlinuz-[0-9][^ ']*" "$LIVEMEDIA_LOG" 2>/dev/null \
    | sed 's/vmlinuz-//; s/\.x86_64$//' | sort -V | tail -1)
_TMPREPO=$(mktemp -d)
cat > "$_TMPREPO/ucheck.repo" <<EOF
[ucheck]
name=ucheck
mirrorlist=https://mirrors.fedoraproject.org/mirrorlist?repo=updates-released-f45&arch=x86_64
enabled=1
EOF
LATEST_KERNEL=$(dnf -q --setopt=reposdir="$_TMPREPO" --disablerepo='*' --enablerepo=ucheck \
    --releasever=45 repoquery --qf '%{version}-%{release}\n' kernel-core 2>/dev/null \
    | sort -V | tail -1)
rm -rf "$_TMPREPO"

if [ -z "$ISO_KERNEL" ]; then
    echo "AVISO: não consegui extrair o kernel da ISO de ${LIVEMEDIA_LOG}; trava pulada." >&2
elif [ -z "$LATEST_KERNEL" ]; then
    echo "AVISO: não consegui consultar o repo updates (rede?); trava pulada." >&2
elif [ "$ISO_KERNEL" != "$LATEST_KERNEL" ]; then
    echo "ERRO: a ISO saiu com kernel ${ISO_KERNEL}, mas o repo updates tem ${LATEST_KERNEL}." >&2
    echo "      O repo de updates NÃO foi aplicado — a ISO está DESATUALIZADA (BUG-29)." >&2
    exit 1
else
    echo "==> OK: ISO com kernel ${ISO_KERNEL} (bate com o repo updates)."
fi

echo
echo "==> Concluído! ISO em: ${RESULT_DIR}/${ISO_NAME}"
