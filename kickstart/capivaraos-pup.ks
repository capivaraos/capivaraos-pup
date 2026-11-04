#version=DEVEL
# =============================================================================
# CapivaraOS Pup - Fedora 45 (Xfce) - kickstart principal
# =============================================================================
#
# Spin leve do CapivaraOS, baseado no ambiente Xfce oficial do Fedora,
# pensado para computadores com ao menos 4GB de RAM. Usa as mesmas
# ferramentas de build do CapivaraOS Marsh (KDE): `kickstart` +
# `livemedia-creator` (lorax) para a imagem, e Anaconda como instalador.
# Ver ../capivaraos-marsh-fedora/ para a spin KDE "completa" (tema macOS/
# WhiteSur) que serviu de referência de estrutura para este projeto.
#
# Uso (ver README.md para detalhes; ./build-all.sh automatiza tudo isto):
#   cd kickstart && python3 ks-flatten.py capivaraos-pup.ks > /var/tmp/capivaraos-pup-flat.ks
#   livemedia-creator --ks=/var/tmp/capivaraos-pup-flat.ks \
#       --no-virt --resultdir=/var/tmp/capivaraos-pup-result \
#       --project="CapivaraOS Pup" --make-iso --iso-only \
#       --iso-name=CapivaraOS-Pup-2.0.0-x86_64.iso \
#       --volid="CapivaraOS Pup 2.0.0" --variant="CapivaraOS Pup" \
#       --releasever=45
#
# NOTA: o anaconda resolve "%include caminho.ks" em relação ao seu próprio
# cwd (não ao diretório deste arquivo), por isso o ks-flatten.py acima é
# necessário — ver kickstart/ks-flatten.py.

%include upstream/fedora-live-xfce-base.ks

# ── Repositório local com o RPM capivaraos-branding ─────────────────────────
# Gerado por ../build-all.sh (rpm/build-rpm.sh + createrepo_c) em
# /var/tmp/capivaraos-pup-repo. Ajuste o caminho se mover o repositório
# local. Nome de diretório distinto do usado pela spin KDE
# (/var/tmp/capivaraos-repo, ver ../capivaraos-marsh-fedora) para permitir
# buildar as duas spins na mesma máquina sem um repo local sobrescrever o
# outro.
repo --name=capivaraos-local --baseurl=file:///var/tmp/capivaraos-pup-repo

# ── IDIOMA / TECLADO / FUSO ──────────────────────────────────────────────────
# Mesma convenção do CapivaraOS Marsh: pt_BR.UTF-8 / teclado ABNT2 / horário
# de Brasília. glibc-all-langpacks (incluso via fedora-live-base) já traz
# todos os locales prontos.
lang pt_BR.UTF-8
keyboard --xlayouts='br-abnt2' --vckeymap=br-abnt2
timezone America/Sao_Paulo --utc
network --hostname=capivaraos

# NOTA: tamanho do filesystem de trabalho ("part /") definido em
# upstream/fedora-live-base.ks (16384 = 16 GiB na série 2.x; era 8 GiB no 1.x e
# estourou com COS Dev + btrfs-assistant/Qt6) — não redeclarado aqui para
# evitar duas diretivas "part /" conflitantes no kickstart achatado.

# =============================================================================
# PACOTES
# =============================================================================
%packages

# ── Identidade visual: usamos nosso próprio pacote de branding (wallpapers,
# Plymouth, fundo do LightDM, os-release, ícones, avatar padrão) em vez do
# wallpaper genérico do Fedora. Ver rpm/capivaraos-branding.spec.
capivaraos-branding

# Tema Plymouth do CapivaraOS (capivaraos.script) é um tema "script": precisa
# do plugin script.so do plymouth para ser renderizado. Sem este pacote,
# /usr/lib64/plymouth/script.so não existe e o plymouthd cai no tema padrão
# do Fedora (mesmo bug observado na spin KDE antes de adicionar este
# pacote — ver capivaraos-marsh.ks), mesmo com plymouthd.conf apontando
# Theme=capivaraos corretamente.
plymouth-plugin-script

# ===== SISTEMA BASE (idioma) =====
langpacks-pt_BR
glibc-langpack-pt

# ===== OFFICE: tradução pt-BR do LibreOffice (Calc/Writer, via
# @xfce-office) ===== Mantemos apenas o pacote de idioma, sem o help
# completo (mais pesado), para um conjunto leve.
libreoffice-langpack-pt-BR

# ===== MIDIA =====
# VLC além do Parole (padrão do @xfce-media): suporte de codecs mais amplo
# para vídeos do dia a dia. GIMP fica de fora por padrão (mantém a imagem
# leve); instale via dnf se precisar de edição de imagens avançada.
vlc

# ===== UTILITARIOS =====
htop
fastfetch
curl
wget
zip
unzip
rsync
# gparted, mousepad, ristretto, geany, xarchiver já inclusos via @xfce-apps

# ===== FONTES =====
liberation-fonts
dejavu-fonts-all

# ===== WALLPAPERS PADRÃO DO XFCE =====
# Além dos wallpapers da marca (pacote capivaraos-branding), embarcamos o
# conjunto padrão do Xfce para o usuário poder escolher no seletor de fundo.
f45-backgrounds-xfce

# ===== COS DEV CENTER (mínimo) =====
# App de onboarding do 1o boot (Xfce/GTK), versão enxuta (PROD-122): cards de
# IA local, ferramentas de dev e GitHub CLI. Vem do repo local desta spin.
capivara-central
# -- COS Config Center: central de configuracao (codecs, firewall, discos, rede,
# idioma...). Pacote ja assinado, baixado do nosso repositorio pelo build-all.sh
# para o repo local capivaraos-local.
cos-config

# ===== UPDATE IN-PLACE (repo assinado + upgrade de versao) =====
# capivaraos-repos: instala o repositorio de updates assinado (repo.capivaraos.org)
# + a chave GPG do projeto, habilitando o "atualize sem formatar" via dnf/GNOME
# Software. capivaraos-upgrade: ferramenta de upgrade de versao (2.x -> ...) com
# snapshot pre-upgrade. Ambos buildados localmente pelo build-all.sh; o
# capivaraos-upgrade depende de capivaraos-repos. (FEAT-111, PROD-116/117.)
capivaraos-repos
capivaraos-upgrade

# ===== SNAPSHOTS ("atualize sem medo") =====
# Btrfs é o padrão do instalador; snapper dá os snapshots pré/pós. A config
# "root" do snapper é criada no 1o boot pelo capivaraos-snapper-setup.service
# (do capivaraos-branding) — sem ela o capivaraos-upgrade não tira snapshot
# automático antes do upgrade in-place (PROD-121). btrfs-assistant = GUI leve.
snapper
btrfs-assistant

%end

# =============================================================================
# Post-scripts específicos do CapivaraOS
# =============================================================================
%include capivaraos-post-branding.ks
