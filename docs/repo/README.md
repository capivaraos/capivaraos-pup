# Repositório de atualizações do CapivaraOS (desktop) — FEAT-111 / FEAT-112

Infra do repo RPM assinado que dá ao CapivaraOS instalado um caminho de
atualização de primeira classe: updates contínuos da versão corrente + upgrade
de versão sem formatar (ver o épico FEAT-111). A fundação (assinatura + layout +
pipeline) é a **mesma** já validada no Herd; aqui é a variante **desktop**, com
**chave própria** (separada da do Herd).

## Peças
- `keys/gen-signing-key.sh` + `keys/README.md` — cerimônia offline da chave.
- `repo/capivaraos.repo` — os canais `stable` (on) e `testing` (off) que o
  cliente recebe. baseurl por `$releasever` (acompanha F44→F45 sozinho).
- `rpm/capivaraos-repos.spec` + `rpm/build-rpm-repos.sh` — o pacote
  `capivaraos-repos` (.repo + chave pública) que vai embarcado na ISO.
- `publish-repo.sh` — assina RPMs, `createrepo_c`, assina `repomd.xml`, e sobe
  para o host (rclone).

## Modelo de confiança
A integridade vem da **assinatura**, não do host. `gpgcheck=1` + `repo_gpgcheck=1`
fazem um host/CDN comprometido não conseguir empurrar update malicioso. A chave
privada fica **offline** (HSM/cofre); só a pública viaja no `capivaraos-repos`.

## Layout publicado
```
repo.capivaraos.org/
  pup/f<rel>/<arch>/stable/     (enabled=1)
  pup/f<rel>/<arch>/testing/    (enabled=0; QA)
      └── repodata/{repomd.xml, repomd.xml.asc, ...}
```
**Caminho por spin** (`pup/`): as 3 spins desktop compartilham esta base mas
têm caminhos separados (marsh/pup/pup) porque `capivaraos-branding` tem Release
por spin — juntá-las faria o dnf "atualizar" uma spin com o build de outra
(armadilha de NEVRA, BUG-30). Este é o repo do PUP (publica em `pup/`);
Marsh e Pup usam `marsh/`/`pup/`.

## Fluxo
```
build RPM  ->  add ao TESTING  ->  QA em VM  ->  PROMOTE p/ STABLE  ->  upload
```
Dev/local (sem host): `publish-repo.sh add/promote` gravam em `out/repo/`
(gitignored); testa-se por `file://` ou `python -m http.server`. Teste "online"
grátis = **Copr** (bootstrap).

## Host de produção
**GitHub Pages** (repo `capivaraos/repo`), servido em `repo.capivaraos.org` — o
comando `pages` publica aí. Object storage com CDN fica como alternativa futura,
pelo comando `upload`. Como o baseurl aponta pro nosso domínio, o host é
repointável depois sem tocar no pacote: a confiança vem da assinatura, não do
host.

## GUARDRAILS
1. **Chave primeiro.** O build do `capivaraos-repos` FALHA sem
   `keys/RPM-GPG-KEY-capivaraos` — de propósito (não empacotamos placeholder).
2. **Não cortar ISO com o pacote antes do repo estar no ar.** Enquanto
   `repo.capivaraos.org/pup/` não existir, NÃO adicionar `capivaraos-repos` ao
   `%packages` do kickstart — senão todo `dnf` no sistema instalado/live avisa
   "repo inacessível". A linha do %packages entra junto com a publicação do repo.
3. **Nada de material privado no git** (`.gitignore` bloqueia `*PRIVATE*`).
