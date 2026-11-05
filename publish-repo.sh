#!/bin/bash
# =============================================================================
# publish-repo.sh — pipeline de publicação do repositório assinado do CapivaraOS.
# =============================================================================
# FEAT-112. Assina RPMs, monta o layout por release/canal, gera e ASSINA o índice
# do repositório (repomd.xml -> repomd.xml.asc) e, opcionalmente, sobe para o
# object storage. A confiança vem da assinatura, não do host (ver keys/README.md).
#
# Layout publicado (raiz -> repo.capivaraos.org/pup/):
#   pup/f<rel>/<arch>/testing/     canal de QA (repo enabled=0 no cliente)
#   pup/f<rel>/<arch>/stable/      canal de produção (enabled=1)
#     └── repodata/{repomd.xml,repomd.xml.asc,...}
# (Caminho por spin: este repo publica em pup/ por padrão; Marsh usa marsh/ e
#  Pup usará pup/. Passe --spin para publicar noutra spin. Ver repo/capivaraos.repo.)
#
# HOST DE PRODUÇÃO = GitHub Pages (repo capivaraos/repo, servido em
# repo.capivaraos.org, card-free). Use o comando `pages` para publicar. O `upload`
# (rclone, p/ object storage) fica como alternativa futura, se a banda crescer —
# como o baseurl é o nosso domínio (CNAME), dá pra repointar depois sem tocar
# no pacote.
#
# Fluxo recomendado:
#   build RPM -> add ao TESTING -> QA em VM -> PROMOTE p/ STABLE -> pages (publica)
#
# Uso:
#   # 1) adicionar RPMs ao canal testing (assina + createrepo + assina repomd)
#   ./publish-repo.sh add    --rel 44 --arch x86_64 --channel testing ~/rpmbuild/RPMS/noarch/*.rpm
#   # 2) promover o que passou no QA para stable
#   ./publish-repo.sh promote --rel 44 --arch x86_64
#   # 3) publicar a árvore no GitHub Pages (commit+push no capivaraos/repo)
#   ./publish-repo.sh pages   --rel 44 --arch x86_64
#   #    (alternativa futura: ./publish-repo.sh upload ... -> object storage)
#
# Pré-req: rpm-sign (rpmsign), createrepo_c, gnupg2; git+rsync p/ `pages`
# (rclone p/ `upload`). A chave privada precisa estar disponível ao gpg-agent e o
# %_gpg_name em ~/.rpmmacros (ver keys/README.md). Para o `pages`, o autor do push
# (capivaraos-bot ou comunidade) precisa de acesso de escrita ao capivaraos/repo.
# =============================================================================
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${CAPIVARAOS_REPO_ROOT:-${PROJECT_DIR}/out/repo}"   # raiz local do repo
# Destino do `upload` (alternativa ao `pages`): object storage compatível com S3.
# Configure o remote uma vez com `rclone config` e aponte o domínio
# repo.capivaraos.org para o bucket. BOOTSTRAP alternativo: Fedora Copr, que
# assina e hospeda.
RCLONE_REMOTE="${CAPIVARAOS_RCLONE_REMOTE:-objstore:capivaraos-pup}" # destino do upload
# Repo do GitHub Pages (host de PRODUÇÃO). Override p/ testar num clone/bare local.
PAGES_REPO="${CAPIVARAOS_PAGES_REPO:-https://github.com/capivaraos/repo.git}"
GPG_KEY_NAME="${CAPIVARAOS_GPG_NAME:-CapivaraOS (repo signing key)}"
SPIN="${CAPIVARAOS_SPIN:-pup}"                                 # caminho por spin
# Cache na CDN: RPMs são imutáveis (cache longo); o índice muda a cada publicação
# e NÃO pode ficar velho na borda (cache curto + revalidação). Evita cliente
# baixar repomd antigo apontando p/ pacote que já saiu.
CACHE_RPM="${CAPIVARAOS_CACHE_RPM:-public, max-age=31536000, immutable}"
CACHE_META="${CAPIVARAOS_CACHE_META:-public, max-age=300, must-revalidate}"

die() { echo "ERRO: $*" >&2; exit 1; }

# --- parse comum ------------------------------------------------------------
CMD="${1:-}"; shift || true
REL=""; ARCH="x86_64"; CHANNEL="testing"; RPMS=()
while [ $# -gt 0 ]; do
    case "$1" in
        --rel)     REL="$2"; shift 2;;
        --arch)    ARCH="$2"; shift 2;;
        --channel) CHANNEL="$2"; shift 2;;
        --spin)    SPIN="$2"; shift 2;;
        *)         RPMS+=("$1"); shift;;
    esac
done
[ -n "$REL" ] || die "informe --rel (ex.: 44)"
case "$CHANNEL" in testing|stable) ;; *) die "--channel deve ser testing ou stable";; esac

chan_dir() { echo "${REPO_ROOT}/${SPIN}/f${REL}/${ARCH}/$1"; }

sign_rpms() {
    command -v rpmsign >/dev/null || die "rpmsign ausente (dnf install rpm-sign)"
    grep -q '%_gpg_name' ~/.rpmmacros 2>/dev/null \
        || die "configure %_gpg_name em ~/.rpmmacros (ver keys/README.md)"
    for r in "$@"; do
        echo "  assinando $(basename "$r")"
        rpmsign --addsign "$r" >/dev/null
    done
}

build_index() {
    local dir="$1"
    command -v createrepo_c >/dev/null || die "createrepo_c ausente"
    echo "  createrepo_c $dir"
    createrepo_c --update "$dir"
    # Assina o índice (repo_gpgcheck no cliente valida ISTO).
    echo "  assinando repomd.xml"
    rm -f "${dir}/repodata/repomd.xml.asc"
    gpg --detach-sign --armor -u "$GPG_KEY_NAME" "${dir}/repodata/repomd.xml"
}

case "$CMD" in
    add)
        [ "${#RPMS[@]}" -gt 0 ] || die "passe ao menos um .rpm"
        DIR="$(chan_dir "$CHANNEL")"; mkdir -p "$DIR"
        sign_rpms "${RPMS[@]}"
        for r in "${RPMS[@]}"; do cp -f "$r" "$DIR/"; done
        build_index "$DIR"
        echo "OK: ${#RPMS[@]} pacote(s) em ${CHANNEL} (${DIR})"
        ;;
    promote)
        SRC="$(chan_dir testing)"; DST="$(chan_dir stable)"
        [ -d "$SRC" ] || die "canal testing vazio: $SRC"
        mkdir -p "$DST"
        echo "promovendo testing -> stable (${SPIN}/f${REL}/${ARCH})"
        # Copia os RPMs (já assinados) do testing p/ stable e reindexa o stable.
        find "$SRC" -maxdepth 1 -name '*.rpm' -exec cp -f {} "$DST/" \;
        build_index "$DST"
        echo "OK: stable atualizado (${DST})"
        ;;
    upload)
        command -v rclone >/dev/null || die "rclone ausente (para o upload)"
        BASE="${REPO_ROOT}/${SPIN}/f${REL}/${ARCH}"
        [ -d "$BASE" ] || die "nada para subir em $BASE"
        DEST="${RCLONE_REMOTE}/${SPIN}/f${REL}/${ARCH}"
        echo "upload ${BASE} -> ${DEST}"
        # Ordem importa: sobem-se os RPMs (imutáveis, cache longo) ANTES do índice,
        # senão o repodata poderia, por segundos, apontar p/ um RPM ainda ausente.
        rclone copy --checksum --exclude 'repodata/**' \
            --header-upload "Cache-Control: ${CACHE_RPM}" \
            "$BASE" "$DEST"
        # Índice por último, com cache curto (a borda não pode servir repomd velho).
        for ch in stable testing; do
            [ -d "$BASE/$ch/repodata" ] || continue
            rclone copy --checksum \
                --header-upload "Cache-Control: ${CACHE_META}" \
                "$BASE/$ch/repodata" "$DEST/$ch/repodata"
        done
        echo "OK: upload concluído"
        ;;
    pages)
        # Publica a árvore assinada no GitHub Pages (capivaraos/repo -> repo.capivaraos.org).
        # Clona o repo do Pages, sincroniza SÓ esta spin/release/arch (preserva
        # index.html/CNAME/.nojekyll/chave e as outras spins), commita e faz push.
        # Um único commit é atômico -> cliente sempre vê RPMs + repodata coerentes
        # (não precisa da dança "RPM antes do índice" de object storage com CDN).
        command -v git >/dev/null   || die "git ausente (para o pages)"
        command -v rsync >/dev/null || die "rsync ausente (para o pages)"
        BASE="${REPO_ROOT}/${SPIN}/f${REL}/${ARCH}"
        [ -d "$BASE" ] || die "nada para publicar em $BASE (rode 'add'/'promote' antes)"
        # Guarda: RPM > 100 MB é rejeitado pelo GitHub -> pare com aviso claro.
        big="$(find "$BASE" -name '*.rpm' -size +100M -printf '%f ' 2>/dev/null)"
        [ -z "$big" ] || die "RPM(s) acima de 100 MB (limite do GitHub): $big"
        WORK="$(mktemp -d)"
        echo "clonando ${PAGES_REPO}…"
        git clone --quiet --depth 1 "$PAGES_REPO" "$WORK" || die "falha ao clonar $PAGES_REPO"
        DST="$WORK/${SPIN}/f${REL}/${ARCH}"
        mkdir -p "$DST"
        # --delete: pacotes removidos na rotação somem do Pages; --delete restrito à
        # subárvore desta spin/release/arch, então o resto do site fica intacto.
        rsync -a --delete "$BASE/" "$DST/"
        ( cd "$WORK"
          git add -A
          if git diff --cached --quiet; then
              echo "nada mudou — nenhum commit."; exit 0
          fi
          git -c user.name="CapivaraOS Bot" \
              -c user.email="capivaraos-bot@users.noreply.github.com" \
              commit -q -m "publish: ${SPIN}/f${REL}/${ARCH} ($(date -u +%FT%TZ))"
          git push --quiet )
        rm -rf "$WORK"
        echo "OK: publicado em https://repo.capivaraos.org/${SPIN}/f${REL}/${ARCH}/"
        ;;
    *)
        die "comando inválido. Use: add | promote | pages | upload (ver cabeçalho)"
        ;;
esac
