#!/bin/bash
# =============================================================================
# Teste reprodutível do upgrade de versão in-place do CapivaraOS (FEAT-115).
# =============================================================================
# Prova, isolado num contêiner Fedora 44, a LÓGICA da ferramenta capivaraos-upgrade:
#   1. o pacote capivaraos-upgrade constrói e instala /usr/bin/capivaraos-upgrade
#      (puxando capivaraos-repos);
#   2. --help sai 0; opção inválida e destino <= atual saem != 0 (guardas);
#   3. FALHA FECHADA: `check` recusa (exit 1) quando o repo assinado do CapivaraOS
#      NÃO existe para a versão de destino — o comportamento de segurança central;
#   4. LIBERA: com um repo local file:// contendo capivaraos-repos para a versão
#      de destino, `check` aprova o pré-voo (exit 0);
#   5. `download` com pré-voo reprovado ABORTA antes de tocar o dnf (não baixa).
#
# A verificação de ASSINATURA (gpgcheck/repo_gpgcheck) é coberta na validação de
# publicação (publish-repo.sh, com a chave); aqui o repo local é sem assinatura
# de propósito, para isolar a lógica de gate/versionamento da ferramenta. Não
# toca o host.
#
# Requer podman. Uso (a partir da raiz do repo):
#   ./tests/test-upgrade.sh
# =============================================================================
set -euo pipefail
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
command -v podman >/dev/null || { echo "ERRO: podman necessário" >&2; exit 1; }

podman run -i --rm \
    -v "${PROJECT_DIR}/rpm":/src/rpm:ro \
    -v "${PROJECT_DIR}/repo":/src/repo:ro \
    -v "${PROJECT_DIR}/keys":/src/keys:ro \
    -v "${PROJECT_DIR}/upgrade":/src/upgrade:ro \
    --security-opt label=disable \
    registry.fedoraproject.org/fedora:44 bash -s <<'EOS'
set -euo pipefail; export LC_ALL=C
ok(){ echo "  [OK] $*"; }; fail(){ echo "  [FALHA] $*"; exit 1; }
# roda um comando que se ESPERA falhar; ok se exit != 0
expect_fail(){ if "$@" >/tmp/ef.log 2>&1; then fail "esperava falha e passou: $*"; fi; }

dnf install -y --setopt=install_weak_deps=False rpm-build createrepo_c >/dev/null 2>&1
mkdir -p ~/rpmbuild/{SOURCES,SPECS}
CUR="$(rpm -E %fedora)"; TGT=$((CUR + 1))

echo "== 1. build + install do capivaraos-upgrade =="
install -m0644 /src/repo/capivaraos.repo ~/rpmbuild/SOURCES/
install -m0644 /src/keys/RPM-GPG-KEY-capivaraos ~/rpmbuild/SOURCES/
install -m0755 /src/upgrade/bin/capivaraos-upgrade ~/rpmbuild/SOURCES/
cp /src/rpm/capivaraos-repos.spec /src/rpm/capivaraos-upgrade.spec ~/rpmbuild/SPECS/
rpmbuild -bb ~/rpmbuild/SPECS/capivaraos-repos.spec   >/dev/null 2>&1
rpmbuild -bb ~/rpmbuild/SPECS/capivaraos-upgrade.spec >/dev/null 2>&1
REPOS=$(find ~/rpmbuild/RPMS -name 'capivaraos-repos-*.rpm'|head -1)
UPG=$(find ~/rpmbuild/RPMS -name 'capivaraos-upgrade-*.rpm'|head -1)
[ -f "$UPG" ] || fail "não construiu capivaraos-upgrade"
dnf install -y "$REPOS" "$UPG" >/tmp/i.log 2>&1 || { tail -15 /tmp/i.log; fail "install falhou"; }
[ -x /usr/bin/capivaraos-upgrade ] && ok "/usr/bin/capivaraos-upgrade instalado e executável" || fail "binário ausente"
rpm -q --requires capivaraos-upgrade | grep -q '^dnf5' && ok "Requires dnf5" || fail "faltou Requires dnf5"

echo "== 2. guardas de argumento =="
capivaraos-upgrade --help >/tmp/h.log 2>&1 && grep -q 'in-place' /tmp/h.log && ok "--help sai 0" || fail "--help"
expect_fail capivaraos-upgrade --opcao-invalida;             ok "opção inválida recusada"
expect_fail capivaraos-upgrade --to "$CUR";                  ok "destino == atual recusado"
expect_fail capivaraos-upgrade --to abc;                     ok "destino não-numérico recusado"

echo "== 3. FALHA FECHADA: sem repo do CapivaraOS para f$TGT, check recusa =="
# baseurl file:// inexistente -> gate reprova de forma determinística (sem rede/DNS).
cat >/etc/yum.repos.d/capivaraos.repo <<'REPO'
[capivaraos]
name=CapivaraOS teste (ausente) $releasever
baseurl=file:///srv/repo-inexistente/pup/f$releasever/$basearch/stable/
enabled=1
gpgcheck=0
repo_gpgcheck=0
REPO
if capivaraos-upgrade check --to "$TGT" >/tmp/c1.log 2>&1; then
  cat /tmp/c1.log; fail "check deveria ter recusado (repo ausente)"
fi
grep -qi 'AUSENTE' /tmp/c1.log && ok "check reprova o pré-voo (repo CapivaraOS ausente p/ f$TGT)" \
  || { cat /tmp/c1.log; fail "esperava relato de repo AUSENTE"; }

echo "== 4. LIBERA: repo local file:// com capivaraos-repos p/ f$TGT =="
ARCH="$(rpm -E %{_arch})"
REPO_ROOT="/srv/repo/pup/f${TGT}/${ARCH}/stable"
mkdir -p "$REPO_ROOT"; cp "$REPOS" "$REPO_ROOT/"
createrepo_c "$REPO_ROOT" >/dev/null 2>&1
# .repo de teste (sem gpg — a assinatura é coberta na validação de publicação),
# baseurl com $releasever/$basearch resolvendo para o repo local.
cat >/etc/yum.repos.d/capivaraos.repo <<REPO
[capivaraos]
name=CapivaraOS teste \$releasever
baseurl=file:///srv/repo/pup/f\$releasever/\$basearch/stable/
enabled=1
gpgcheck=0
repo_gpgcheck=0
REPO
if capivaraos-upgrade check --to "$TGT" >/tmp/c2.log 2>&1; then
  grep -qi 'Pronto para upgrade' /tmp/c2.log && ok "check aprova com repo presente p/ f$TGT" \
    || { cat /tmp/c2.log; fail "aprovou mas sem a mensagem esperada"; }
else
  cat /tmp/c2.log; fail "check deveria aprovar (repo presente)"
fi

echo "== 5. download aborta quando o pré-voo reprova (não toca o dnf) =="
# Aponta o repo p/ caminho inexistente (enabled=0 não bastaria: --repo força o
# enable). Assim o pré-voo reprova e o download deve abortar ANTES de tocar o dnf.
cat >/etc/yum.repos.d/capivaraos.repo <<'REPO'
[capivaraos]
name=CapivaraOS teste (ausente) $releasever
baseurl=file:///srv/repo-inexistente/pup/f$releasever/$basearch/stable/
enabled=1
gpgcheck=0
repo_gpgcheck=0
REPO
expect_fail capivaraos-upgrade download --to "$TGT" --yes
grep -qi 'pré-voo reprovado\|Upgrade abortado' /tmp/ef.log && ok "download abortou no pré-voo (sem baixar)" \
  || { cat /tmp/ef.log; fail "esperava aborto no pré-voo"; }

echo; echo "== RESULTADO: FEAT-115 OK (build+install + guardas + falha-fechada + libera + aborto seguro) =="
EOS
