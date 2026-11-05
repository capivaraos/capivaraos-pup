# Upgrade de versão in-place do CapivaraOS — FEAT-115

A ferramenta `capivaraos-upgrade` sobe o CapivaraOS para a próxima versão **sem
formatar**, usando a transação **offline** do dnf5 (`dnf5 system-upgrade`): baixa
tudo com o sistema no ar e aplica no próximo boot, num ambiente isolado. É a
**engine** do "atualizar sem formatar" (FEAT-111); a UX do botão (COS Dev Center /
Discover, FEAT-116) reusa esta mesma ferramenta.

Portada do `herd-upgrade` (Herd, PROD-107), já validado — aqui com os nomes do
desktop (repo `capivaraos`, pacote `capivaraos-repos`, branding `capivaraos-branding`).

## Uso
```
capivaraos-upgrade [check]                 # pré-voo (padrão, seguro — nada muda)
sudo capivaraos-upgrade download [--to N]  # baixa a transação (NÃO reinicia)
sudo capivaraos-upgrade reboot             # aplica: reinicia no modo offline
sudo capivaraos-upgrade run [--to N]       # download + reboot (com confirmação)
capivaraos-upgrade status | log | clean    # atalhos do dnf5 system-upgrade
```
`--to N` / `--releasever N`: versão Fedora de destino. Sem isso, assume a atual+1
(`rpm -E %fedora`), então a mesma ferramenta serve para os saltos futuros.

## Segurança / auditabilidade (marca CapivaraOS)
- **Só verifica por padrão.** Sem argumento, roda `check` e não altera nada.
- **Passos explícitos.** Baixar e reiniciar são comandos separados.
- **Falha fechada.** Se o nosso repo assinado (`capivaraos`) ainda não existir
  para a versão de destino, o upgrade é RECUSADO — senão a máquina subiria a base
  Fedora e deixaria os pacotes do CapivaraOS para trás. (Escape consciente:
  `--allow-missing-repo`.)
- **Confiança pela assinatura.** `gpgcheck` + `repo_gpgcheck` fazem a transação
  offline recusar pacote/metadado não assinado pela nossa chave — mesmo com
  host/CDN comprometido (ver docs/repo/README.md).
- **Snapshot antes.** Em btrfs+snapper (quando presente e configurado), cria
  snapshot automático antes do upgrade. Em LVM, reporta o comando manual. Sem
  storage compatível, avisa para fazer backup. **NOTA Pup:** o instalador do Xfce
  (Anaconda) usa btrfs mas NÃO cria a config `root` do snapper por padrão — o
  CapivaraOS 2.x resolve isso com um oneshot de 1º boot
  (`capivaraos-snapper-setup`), de modo que o snapshot pré-upgrade funcione.

## Rollback
- **snapper/btrfs:** `snapper list` acha o snapshot "pré capivaraos-upgrade …";
  reverter com `snapper undochange <N>..0` ou, para o sistema todo, bootar o
  snapshot e promovê-lo (ver a doc do snapper). O snapshot pré-upgrade é o ponto
  de retorno se o boot novo falhar.
- **LVM:** `sudo lvconvert --merge <snap>` e reiniciar.

## Estado / limitações
- Depende de FEAT-112/113 (repo assinado + pacote `capivaraos-repos`).
- O gate de repo demonstra a recusa correta **enquanto `f<destino>` não estiver
  publicada** — é o comportamento esperado até o repo de produção existir.
- Teste da lógica: `tests/test-upgrade.sh` (podman; build+install, guardas,
  falha-fechada, libera com repo local, aborto seguro no download).
- **Falta p/ Done:** teste cross-release REAL em VM (F45→F46), gated no `pup/f46/`
  publicado (host adiado). **Item aberto do Pup:** decidir se o Pup 2.x adota
  snapper+btrfs no layout padrão de instalação (como o Marsh) para o rollback
  automático valer — senão o upgrade cai no caminho "sem snapshot / faça backup".
