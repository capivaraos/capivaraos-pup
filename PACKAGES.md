# Seleção de pacotes — CapivaraOS Pup (Fedora 45, Xfce)

Diferente do CapivaraOS Marsh (que parte de um mapeamento Debian -> Fedora),
o Pup é uma spin nova, então este documento registra a *escolha* de pacotes
e o porquê, não um mapeamento de outra distro.

Convenções do kickstart Fedora:
- `@nome` = grupo comps
- `@^nome` = grupo "environment" (define o ambiente todo)
- `-pacote` = remove um pacote que viria por dependência/grupo

Todos os grupos/pacotes abaixo foram conferidos diretamente no comps.xml do
Fedora 44 (repos `fedora`+`updates`) numa máquina de build Fedora 44, via
`dnf group info xfce-desktop-environment` e inspeção do
`comps-Everything.xml`.

## Ambiente gráfico

| Grupo comps | O que traz | Decisão |
|---|---|---|
| `@^xfce-desktop-environment` | Xfce completo (xfwm4, xfce4-panel, xfce4-session, xfdesktop, Thunar, LightDM+lightdm-gtk, NetworkManager-applet, temas Greybird/Adwaita, gvfs, tumbler etc.) | Base do spin. Mantemos o tema Greybird padrão do Fedora Xfce (sem WhiteSur/macOS como na Marsh) — decisão consciente para manter a spin leve e sem dependências de build externas. |
| `@xfce-apps` (opcional, default) | Thunar, xfce4-terminal, Mousepad, Geany, Ristretto, GParted, Catfish, Xarchiver, Galculator, Claws Mail (+plugins), Pidgin, Transmission, Seahorse | Mantido, mas **removemos** Pidgin, Transmission e os plugins extras do Claws Mail (`claws-mail-plugins-*`) — não essenciais para o público-alvo (4GB RAM) e pesam no tamanho da ISO. Claws Mail (sem plugins) fica como cliente de e-mail leve — não incluímos Thunderbird. |
| `@xfce-media` (opcional, default) | Parole, Asunder, Pavucontrol, Pragha, Xfburn | Mantido por completo; adicionamos `vlc` para suporte de codecs mais amplo no dia a dia (sem RPM Fusion habilitado — mesma limitação de codecs da Marsh). |
| `@xfce-office` (opcional) | `libreoffice-calc`, `libreoffice-writer` | Usado **no lugar** do grupo `@libreoffice` completo (que a Marsh usa) — Calc + Writer cobre a maioria dos casos de uso num spin leve, sem Impress/Draw/Base/Math. Adicionamos `libreoffice-langpack-pt-BR` (tradução), sem o pacote de ajuda completo (mais pesado). |
| `@xfce-extra-plugins` | Plugins extras de painel (clima, sensores, bateria, olhinhos animados, whisker menu, dashboard) | **Não incluído** — nenhum é essencial e somam bastante peso/dependências para um conjunto pouco usado por padrão. |

## Excluídos explicitamente (`-pacote`)

| Pacote | Motivo |
|---|---|
| `desktop-backgrounds-compat` | Traz o wallpaper padrão do Fedora; substituído pelo `capivaraos-branding`. |
| `autofs`, `acpid` | Não necessários numa imagem live/desktop padrão (mesma exclusão do `fedora-livecd-xfce.ks` upstream histórico). |
| `gimp-help` | GIMP em si **não é instalado** por padrão nesta spin (mantém a imagem leve); a exclusão do pacote de ajuda é defensiva caso algum grupo o traga transitivamente. |
| `aspell-*` | Dicionários — pesados, pouco usados fora de um editor de texto avançado. |
| `pidgin`, `transmission` | Apps de nicho (chat multiprotocolo, torrent) não essenciais para o público de 4GB RAM. |
| `claws-mail-plugins-*` | Plugins do cliente de e-mail padrão do Xfce, mantemos só o app base. |

## Aplicativos próprios do CapivaraOS (série 2.x)

| Pacote | O que é | Origem |
|---|---|---|
| `capivara-central` | **COS Dev Center** (versão mínima): app de onboarding do 1º boot com os cards de IA local, Ferramentas de dev e GitHub CLI. | Construído neste repo (`apps/capivara-central/`) e servido pelo repo local da build. |
| `cos-config` | **COS Config Center** (0.11.1): central única de configuração do CapivaraOS — 9 módulos (codecs/RPM Fusion/Flathub, limpeza, discos, tamanho dos logs, diagnóstico, teclado, idioma, firewall, acesso remoto e rede). Firewall na zona `public`, portas >1024 fechadas de fábrica. | Pacote próprio (repositório `cos-config`); baixado do canal **testing** assinado do repo da spin (`repo.capivaraos.org/pup/f45/x86_64/testing/`) no passo 3 do `build-all.sh`, com verificação de assinatura (`keys/RPM-GPG-KEY-capivaraos`) — sem assinatura válida a build aborta. Canal na variável `COS_CONFIG_CHANNEL` (padrão `testing`; vira `stable` no lançamento, PROD-165). |

## Idioma / localização

- `langpacks-pt_BR`, `glibc-langpack-pt` — pacotes de idioma pt-BR.
- `glibc-all-langpacks` — já incluso via `fedora-live-base.ks` (upstream), garante todos os locales disponíveis para troca em Configurações.
- `libreoffice-langpack-pt-BR` — tradução do LibreOffice Calc/Writer.

## Utilitários adicionados

`htop`, `fastfetch`, `curl`, `wget`, `zip`, `unzip`, `rsync` — ferramentas de
linha de comando comuns e leves. `cups` + `system-config-printer` —
suporte a impressão (não incluso por padrão no grupo Xfce).

## Fontes

`liberation-fonts`, `dejavu-fonts-all` — fontes essenciais. Não incluímos o
pacote `google-noto-*` completo (usado na Marsh) para manter a instalação
mais leve; o usuário pode instalar fontes adicionais via `dnf` se precisar
de cobertura Unicode mais ampla (CJK, emoji etc.).

## O que NÃO foi portado da Marsh

- **Tema WhiteSur/macOS** (dock + painel global + decoração de janela
  estilo macOS): decisão consciente para manter o Pup leve e sem
  dependência de `git clone` de temas de terceiros durante o build. O Pup
  usa o tema Greybird/Xfwm4 padrão do Fedora Xfce.
- **Thunderbird, GIMP, ferramentas de desenvolvimento**: fora do conjunto
  padrão; instale via `dnf install` se precisar.
- **LibreOffice completo**: só Calc + Writer (`@xfce-office`), não o
  conjunto inteiro (`@libreoffice`).
