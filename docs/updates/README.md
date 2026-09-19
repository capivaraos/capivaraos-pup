# Updates contínuos da versão corrente — FEAT-114

Como o CapivaraOS instalado recebe **correções e melhorias dentro da versão
atual** (o equivalente ao repo `updates` do Fedora), sem esperar uma ISO nova.
Complementa o upgrade *entre* versões (FEAT-115) e usa a mesma infra assinada
(FEAT-112/113).

## O que é um "update dentro da versão"
Um rebuild de um **pacote próprio** com EVR (Epoch-Version-Release) maior,
publicado no canal `stable` do repo da versão corrente. O `dnf upgrade` (ou o
notificador de atualização leve do Pup, PROD-123) puxa porque o EVR é maior.
Pacotes próprios do desktop (Pup 2.x):

| Pacote | Onde | Build |
|---|---|---|
| `capivaraos-branding` | `rpm/` | `rpm/build-rpm.sh` |
| `capivaraos-repos` | `rpm/` | `rpm/build-rpm-repos.sh` |
| `capivaraos-upgrade` | `rpm/` | `rpm/build-rpm-upgrade.sh` |

> O `capivara-central` (COS Dev Center) entra nesta lista quando a **PROD-117**
> (port GTK4/libadwaita) for feita — hoje o Pup ainda não o empacota.

Backports de pacotes do Fedora ficam **fora de escopo por ora** — herdamos o
`updates` do Fedora para a base.

## Política de versionamento (bump previsível)
- **EVR sempre monotônico.** Toda publicação de um pacote tem EVR estritamente
  maior que o anterior no mesmo canal, senão o `dnf` não vê o update.
- **Correção dentro da versão** → bump do **Release** (ex.: `1.pup` → `2.pup`),
  mantendo o `Version`. **Mudança de conteúdo/feature** → bump do **Version**.
- **Sufixo por spin `.marsh`/`.pup`/`.pup`** no Release: mantém as spins
  distintas no `~/rpmbuild` compartilhado (BUG-30). **Não** é o que ordena o
  update — quem ordena é o Version/Release numérico. Por isso cada spin publica
  no **seu** caminho de repo (`marsh/`, `pup/`, `pup/`), nunca num diretório
  comum (senão o dnf compararia builds de spins diferentes — ver repo/capivaraos.repo).
- **`Version` sai do `.spec`, nunca cravado no build** (`rpmspec -q` — disciplina
  do BUG-30). O `capivaraos-branding` do 2.x hoje usa Release de pré-lançamento
  (`0.NN.alphaNN`); ao estabilizar a versão, o Release passa a bump inteiro.
- **Notas de atualização = `%changelog`** de cada pacote (o Discover/dnf mostram
  ao usuário). Escreva a entrada de changelog junto com o bump.

## Pipeline de publicação
```
build (todos os RPMs próprios)  ->  add ao TESTING  ->  QA em VM  ->  promote p/ STABLE  ->  upload
```
- **`./build-updates.sh`** reconstrói os 4 pacotes próprios (resolvendo a NEVRA
  exata de cada `.spec`) e, com `--stage`, os assina e adiciona ao canal
  `testing` do repo da versão corrente (via `publish-repo.sh add`). Sem `--stage`,
  só builda (útil pra checar que tudo compila; não precisa da chave privada).
- **QA:** um testador habilita o testing (`dnf --enablerepo=capivaraos-testing
  upgrade`) e valida numa VM.
- **Promover:** `./publish-repo.sh promote --rel <N> --arch x86_64` copia o que
  passou p/ `stable` e reindexa.
- **Subir:** `./publish-repo.sh upload --rel <N> --arch x86_64` (rclone; host de
  produção adiado — ver docs/repo/README.md).

## Gate / segurança
- `--stage` (assinar) exige a **chave privada** disponível + `%_gpg_name` em
  `~/.rpmmacros` (ver keys/README.md). Sem isso, falha limpo no `rpmsign`.
- Confiança pela **assinatura** (gpgcheck + repo_gpgcheck): host comprometido não
  empurra update forjado.
- **Guardrail:** nada de publicar no `stable` sem passar pelo `testing`/QA; e não
  embarcar `capivaraos-repos` na ISO antes do repo estar no ar (docs/repo/README.md).
