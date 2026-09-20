# capivaraos-branding — identidade visual do CapivaraOS Pup (Fedora, Xfce)
#
# Equivalente, para a spin Xfce, ao rpm/capivaraos-branding.spec da spin KDE
# (../capivaraos-marsh-fedora/rpm/capivaraos-branding.spec): wallpapers,
# ícones "Sobre o Sistema", tema Plymouth de boot, fundo do LightDM,
# /etc/os-release, /etc/issue, avatar padrão, wallpaper padrão do Xfce.
#
# Diferenças principais em relação à versão KDE (por ser uma spin leve, sem
# tema de terceiros tipo WhiteSur):
#   - Sem pacotes de wallpaper "estilo Plasma" (o Xfce não tem esse
#     mecanismo; os arquivos em /usr/share/backgrounds/capivaraos/ já
#     aparecem no seletor de wallpaper do xfdesktop).
#   - Tela de login: LightDM (lightdm-gtk-greeter), não SDDM.
#   - Mantém o tema GTK/ícones padrão do Fedora Xfce (Greybird/Adwaita) —
#     sem decoração de terceiros.

Name:           capivaraos-branding
Version:        2.0.0
# Sufixo ".pup": as tres spins constroem um pacote com este MESMO Name e
# compartilham ~/rpmbuild, entao sem ele duas spins na mesma Version-Release
# geram nomes de arquivo identicos -- ja causou dois incidentes (dnf instalou
# o RPM do Pup no lugar do Snout em junho; build do Pup consumiu sources da
# Marsh em 21/07, BUG-30). Com o sufixo a colisao e impossivel por construcao.
#
# Serie 2.x (Fedora 45): pre-releases no padrao Fedora
# "0.N.alphaN.<dist>.pup" (0.1.alpha1, 0.2.alpha2, ...). O
# "2.0.0-1.<dist>.pup" fica RESERVADO para o LANCAMENTO PUBLICO conjunto das
# 3 spins (ver PROD-61). NEVRA 2.0.0-0.1.alpha1 < 2.0.0-1, entao o dnf nunca
# atualiza "pra tras". Builds de dev saem rotulados "preview".
Release:        0.5.alpha5%{?dist}.pup
Summary:        Identidade visual, wallpapers e branding padrão do CapivaraOS Pup 2.0.0 (preview)

License:        GPL-3.0-or-later AND LicenseRef-CapivaraOS-Trademark
URL:            https://capivaraos.org
BuildArch:      noarch

Source0:        %{name}-%{version}.tar.gz

BuildRequires:  ImageMagick
# /usr/bin/convert ou /usr/bin/magick
Requires:       plymouth
Requires:       lightdm-gtk
# libnotify: notify-send do aviso leve de nova versao (capivaraos-update-notify,
# PROD-123). O timer/servico de usuario ficam neste pacote.
Requires:       libnotify

# NOTA CapivaraOS: NÃO declaramos "Conflicts: desktop-backgrounds-compat"
# aqui. Esse pacote é Requires obrigatório de xfdesktop e de lightdm-gtk no
# Fedora 44 (confirmado em build real) — conflitar com ele tornaria o
# próprio ambiente Xfce não instalável junto com este pacote. Convivemos
# com ele instalado (só os wallpapers padrão do Fedora) e sobrescrevemos
# qual wallpaper fica ativo via %posttrans/skel, sem remover o pacote.

%description
Pacote de identidade visual do CapivaraOS Pup 2.0.0 (preview): o conjunto de
wallpapers da marca do CapivaraOS 2.x (moonlight/sunset/dev/comics/abstract),
compartilhado com as demais spins (Marsh e Snout), padrão "Luar" (moonlight);
conjunto de ícones "capivaraos-logo" e "capivaraos-full-logo", tema Plymouth de
boot, tela de login LightDM, /etc/os-release, /etc/issue e wallpaper padrão do
Xfce. Os wallpapers padrão adicionais continuam vindo do pacote f45-backgrounds-xfce
da base.

%prep
%setup -q

%build
set -e
CONVERT=convert
command -v convert >/dev/null 2>&1 || CONVERT=magick

# ── 1. Ícones hicolor "capivaraos-logo" (apenas a capivara, sem texto) ──────
mkdir -p build/icons
for SIZE in 16 22 24 32 48 64 96 128 256 512; do
    mkdir -p "build/icons/hicolor/${SIZE}x${SIZE}/apps"
    "$CONVERT" icons/capivaraos-logo.png -resize "${SIZE}x${SIZE}" \
        "build/icons/hicolor/${SIZE}x${SIZE}/apps/capivaraos-logo.png"
done

# ── 2. Ícones hicolor "capivaraos-full-logo" (capivara + texto "CapivaraOS") ─
for SIZE in 16 22 24 32 48 64 96 128 256 512; do
    mkdir -p "build/icons/hicolor/${SIZE}x${SIZE}/apps"
    "$CONVERT" backgrounds/CapivaraOS_Logo.png -background none -gravity center \
        -extent 1536x1536 -resize "${SIZE}x${SIZE}" \
        "build/icons/hicolor/${SIZE}x${SIZE}/apps/capivaraos-full-logo.png"
done

# ── 3. Ícone branco para a área de trabalho ("Instalar CapivaraOS" etc) ─────
mkdir -p build/pixmaps
"$CONVERT" icons/capivaraos-logo.png -fill white -colorize 100% \
    -resize 256x256 build/pixmaps/capivaraos-white.png

# ── 4. Avatar padrão (.face): só a capivara, fundo branco quadrado ──────────
# Vem de icons/capivaraos-logo.png (canvas quadrado, capivara sem texto), não
# de um -crop sobre a logo-mestre -- ver a nota em 4b sobre coordenadas fixas.
"$CONVERT" icons/capivaraos-logo.png -background white -flatten \
    -resize 256x256 build/pixmaps/capivaraos-face.png

# ── 4b. Logo quadrada (capivara, sem texto, fundo transparente) para o
# branding do Cockpit/Anaconda WebUI (instalador gráfico da ISO live) ───────
# O Cockpit (usado pelo instalador "Anaconda WebUI" do Fedora 44) escolhe a
# pasta /usr/share/cockpit/branding/<ID> com base no ID= do /etc/os-release,
# caindo para ID_LIKE= (no nosso caso "fedora") se não existir uma pasta com
# o próprio ID. Sem este pacote, o instalador mostra a logo do Fedora.
#
# Usa um recorte da CABEÇA da capivara (não o corpo inteiro, que é uma
# silhueta larga ~2.5:1) -- dentro da caixa quadrada pequena do CSS
# (".logo", 2rem x 2rem) uma silhueta larga "achata" para uma faixa fina,
# ficando minúscula independente do quanto se reduza o padding. Um recorte
# já aproximadamente quadrado da cabeça preenche a caixa corretamente.
mkdir -p build/cockpit
# A cabeça vem de icons/capivaraos-head.png (460x460, canvas quadrado, fundo
# transparente), um asset versionado -- e NÃO de um -crop com coordenadas
# fixas sobre a logo-mestre. Até a 1.0.0 isto era
# "-crop 360x300+480+90 backgrounds/CapivaraOS_Logo.png", calibrado para a
# logo antiga (capivara sentada, cabeça no centro-topo); na logo nova
# (capivara andando, cabeça à esquerda) essas mesmas coordenadas recortam o
# lombo do animal. Um recorte por coordenadas quebra em silêncio a cada troca
# de arte, então a cabeça agora é um arquivo próprio.
"$CONVERT" icons/capivaraos-head.png \
    -resize 256x256 build/cockpit/logo.png
"$CONVERT" build/cockpit/logo.png -resize 32x32 build/cockpit/favicon.ico

# ── 5. Logo BRANCA para o splash do Plymouth (boot/desligamento) ────────────
mkdir -p build/plymouth
"$CONVERT" backgrounds/CapivaraOS_Logo.png -fill white -colorize 100% \
    -resize 320x320 build/plymouth/logo.png

# Spinner branco (arco girando) exibido logo abaixo da logo no splash.
mkdir -p build/plymouth/spinner
"$CONVERT" -size 64x64 xc:none -stroke white -strokewidth 5 \
    -fill none -draw "stroke-linecap round arc 12,12 52,52 0,300" \
    build/plymouth/spinner-base.png
for i in $(seq 0 29); do
    ANG=$(( i * 12 ))
    "$CONVERT" build/plymouth/spinner-base.png -background none \
        -distort SRT ${ANG} +repage "build/plymouth/spinner/${i}.png"
done

%install
set -e
DEFAULT_WP=%{_datadir}/backgrounds/capivaraos/capivaraos-wp-moonlight.png

# ── Wallpapers da marca 2.x ─────────────────────────────────────────────────
install -d %{buildroot}%{_datadir}/backgrounds/capivaraos
# NAO instalamos backgrounds/CapivaraOS_Logo.png: apesar de morar nesta pasta,
# ela nao e um wallpaper -- e a arte-mestre (1536x1024) da qual os wallpapers
# sao derivados. Instalada aqui, aparecia no seletor de papel de parede como
# uma opcao escolhivel e, ao ser aplicada, saia com a logo gigante e cortada
# pelo painel (visto na Pup 1.1.2 em 2026-07-21).
for WP in backgrounds/*.png; do
    [ "$(basename "$WP")" = "CapivaraOS_Logo.png" ] && continue
    install -m 0644 "$WP" %{buildroot}%{_datadir}/backgrounds/capivaraos/
done

# ── Pixmaps ──────────────────────────────────────────────────────────────────
install -d %{buildroot}%{_datadir}/pixmaps
install -m 0644 icons/capivaraos.png %{buildroot}%{_datadir}/pixmaps/capivaraos.png
install -m 0644 icons/capivaraos-logo.png %{buildroot}%{_datadir}/pixmaps/capivaraos-logo.png
install -m 0644 build/pixmaps/capivaraos-white.png %{buildroot}%{_datadir}/pixmaps/capivaraos-white.png

# ── Icones hicolor ───────────────────────────────────────────────────────────
for SIZE in 16 22 24 32 48 64 96 128 256 512; do
    install -d %{buildroot}%{_datadir}/icons/hicolor/${SIZE}x${SIZE}/apps
    install -m 0644 "build/icons/hicolor/${SIZE}x${SIZE}/apps/capivaraos-logo.png" \
        %{buildroot}%{_datadir}/icons/hicolor/${SIZE}x${SIZE}/apps/
    install -m 0644 "build/icons/hicolor/${SIZE}x${SIZE}/apps/capivaraos-full-logo.png" \
        %{buildroot}%{_datadir}/icons/hicolor/${SIZE}x${SIZE}/apps/
done

# ── Tema Plymouth ────────────────────────────────────────────────────────────
install -d %{buildroot}%{_datadir}/plymouth/themes/capivaraos
install -m 0644 build/plymouth/logo.png \
    %{buildroot}%{_datadir}/plymouth/themes/capivaraos/logo.png

install -d %{buildroot}%{_datadir}/plymouth/themes/capivaraos/spinner
install -m 0644 build/plymouth/spinner/*.png \
    %{buildroot}%{_datadir}/plymouth/themes/capivaraos/spinner/

cat > %{buildroot}%{_datadir}/plymouth/themes/capivaraos/capivaraos.plymouth << 'EOF'
[Plymouth Theme]
Name=CapivaraOS
Description=CapivaraOS boot splash
ModuleName=script

[script]
ImageDir=/usr/share/plymouth/themes/capivaraos
ScriptFile=/usr/share/plymouth/themes/capivaraos/capivaraos.script
EOF

cat > %{buildroot}%{_datadir}/plymouth/themes/capivaraos/capivaraos.script << 'EOF'
Window.SetBackgroundTopColor(0.07, 0.09, 0.13);
Window.SetBackgroundBottomColor(0.07, 0.09, 0.13);

# ── Logo branca (acima do spinner) ──────────────────────────────────────────
logo.image = Image("logo.png");
logo.sprite = Sprite(logo.image);
logo.x = Window.GetWidth() / 2 - logo.image.GetWidth() / 2;
logo.y = Window.GetHeight() / 2 - logo.image.GetHeight() / 2 - 80;
logo.sprite.SetPosition(logo.x, logo.y, 1);

# ── Spinner (arco branco girando, logo abaixo da logo) ──────────────────────
spinner_frame_count = 30;
for (i = 0; i < spinner_frame_count; i++)
    spinner_image[i] = Image("spinner/" + i + ".png");

spinner.sprite = Sprite();
spinner.cx = Window.GetWidth() / 2;
spinner.cy = logo.y + logo.image.GetHeight() + 50;
spinner.frame = 0;

# ── Mensagem (abaixo do spinner) ────────────────────────────────────────────
is_updates = (Plymouth.GetMode() == "updates" || Plymouth.GetMode() == "system-upgrade");

if (Plymouth.GetMode() == "shutdown" || Plymouth.GetMode() == "reboot") {
    message_text = "Encerrando o CapivaraOS";
} else if (is_updates) {
    message_text = "Instalando atualizações";
} else {
    message_text = "Inicializando o CapivaraOS";
}

message.image = Image.Text(message_text, 1, 1, 1, 1, "Sans 14");
message.sprite = Sprite(message.image);
message.sprite.SetPosition(Window.GetWidth() / 2 - message.image.GetWidth() / 2,
                            spinner.cy + 70, 1);

if (is_updates) {
    warning.image = Image.Text("Não desligue o computador", 0.8, 0.8, 0.8, 1, "Sans 11");
    warning.sprite = Sprite(warning.image);
    warning.sprite.SetPosition(Window.GetWidth() / 2 - warning.image.GetWidth() / 2,
                                spinner.cy + 95, 1);

    fun system_update_callback(progress) {
        percent.image = Image.Text(Math.Int(progress) + "%", 1, 1, 1, 1, "Sans 11");
        if (percent.sprite)
            percent.sprite.SetImage(percent.image);
        else
            percent.sprite = Sprite(percent.image);
        percent.sprite.SetPosition(Window.GetWidth() / 2 - percent.image.GetWidth() / 2,
                                    spinner.cy + 118, 1);
    }
    Plymouth.SetSystemUpdateFunction(system_update_callback);
}

fun refresh_callback() {
    spinner.frame++;
    if (spinner.frame >= spinner_frame_count * 3)
        spinner.frame = 0;
    idx = Math.Int(spinner.frame / 3);
    img = spinner_image[idx];
    spinner.sprite.SetImage(img);
    spinner.sprite.SetX(spinner.cx - img.GetWidth() / 2);
    spinner.sprite.SetY(spinner.cy - img.GetHeight() / 2);
}
Plymouth.SetRefreshFunction(refresh_callback);
EOF

# NOTA CapivaraOS: /etc/os-release e /etc/issue/.issue.net NAO sao gerados
# aqui (em %{buildroot}). Esses caminhos pertencem a fedora-release-common e
# tê-los em %files causa "conflito de arquivo" no dnf durante a transação de
# instalação. Em vez disso, são escritos no sistema instalado em
# %posttrans (ver abaixo), que roda depois de toda a transação e garante que
# nosso conteúdo prevaleça.

# ── /etc/skel: wallpaper padrão do Xfce ─────────────────────────────────────
install -d %{buildroot}%{_sysconfdir}/skel/.config/xfce4/xfconf/xfce-perchannel-xml
install -m 0644 skel/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml \
    %{buildroot}%{_sysconfdir}/skel/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml

# ── Avatar padrão (.face) para novos usuários ────────────────────────────────
install -m 0644 build/pixmaps/capivaraos-face.png %{buildroot}%{_sysconfdir}/skel/.face
ln -sf .face %{buildroot}%{_sysconfdir}/skel/.face.icon

# ── Branding do Cockpit (Anaconda WebUI) ────────────────────────────────────
install -d %{buildroot}%{_datadir}/cockpit/branding/capivaraos
install -m 0644 build/cockpit/logo.png %{buildroot}%{_datadir}/cockpit/branding/capivaraos/logo.png
install -m 0644 build/cockpit/logo.png %{buildroot}%{_datadir}/cockpit/branding/capivaraos/apple-touch-icon.png
install -m 0644 build/cockpit/favicon.ico %{buildroot}%{_datadir}/cockpit/branding/capivaraos/favicon.ico
cat > %{buildroot}%{_datadir}/cockpit/branding/capivaraos/branding.css << 'EOF'
/* SPDX-License-Identifier: LGPL-2.1-or-later */
#badge {
    inline-size: 225px;
    block-size: 80px;
    background-image: url("logo.png");
    background-size: contain;
    background-repeat: no-repeat;
}

#brand::before {
    content: "${NAME} <b>${VARIANT}</b>";
}

.anaconda {
    /* Paleta da marca CapivaraOS (verde) */
    --brand-default-light: #66bb6a;
    --brand-default: #2e7d32;
    --brand-default-dark: #1b5e20;

    .logo {
        background-image: url("logo.png");
        /* O padrão do Cockpit (index.css) é 2rem x 2rem -- aumentamos para
           ficar visualmente do mesmo tamanho do texto do título ao lado
           (pedido explícito: logo pequena demais comparada à fonte). */
        width: 2.5rem;
        height: 2.5rem;
    }
}

:not(.pf-v6-theme-dark) .anaconda {
    --pf-t--global--color--brand--default: var(--brand-default);
    --pf-t--global--color--brand--hover: var(--brand-default-dark);
}

.pf-v6-theme-dark .anaconda {
    --pf-t--global--color--brand--default: var(--brand-default-light);
    --pf-t--global--color--brand--hover: var(--brand-default);
}
EOF

# ── Script de aplicação do wallpaper no primeiro login (xfdesktop cria as
# propriedades "backdrop/screen0/monitor<NOME-REAL>/..." em tempo de
# execução, com o nome real do monitor detectado via RandR — que não
# conhecemos em tempo de build. O xfce4-desktop.xml em /etc/skel cobre o
# caso comum "monitor0", e este script cobre qualquer outro nome de monitor
# sobrescrevendo TODAS as propriedades "image-path"/"last-image" já criadas
# pelo xfdesktop, análogo ao capivaraos-set-wallpaper da spin KDE) ──────────
install -d %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/capivaraos-set-wallpaper << EOF
#!/bin/bash
# Log próprio para depuração (visível mesmo sem journal de sessão gráfica).
LOG="\$HOME/.config/.capivaraos-wallpaper.log"
MARKER="\$HOME/.config/.capivaraos-wallpaper-applied"
mkdir -p "\$HOME/.config"
exec >>"\$LOG" 2>&1
echo "== \$(date) =="
[ -f "\$MARKER" ] && { echo "marcador já existe, saindo"; exit 0; }

WP="${DEFAULT_WP}"
STYLE=3
# Estilo 3 = "Esticado" (Stretched). Pedido explícito: o estilo anterior
# (5 = "Ampliado"/Zoomed) cortava a imagem; Esticado preenche a tela sem
# recortar.

for i in \$(seq 1 40); do
    pgrep -x xfdesktop >/dev/null 2>&1 && break
    sleep 1
done
echo "xfdesktop pgrep: \$(pgrep -x xfdesktop || echo 'NAO ENCONTRADO')"
sleep 3

if ! command -v xfconf-query >/dev/null 2>&1; then
    echo "xfconf-query nao encontrado, abortando"
    exit 1
fi

# Sem esta propriedade, o xfdesktop roda sua rotina de "migração" de config
# no primeiro start de um perfil e SOBRESCREVE last-image/image-path com o
# padrão compilado do Fedora. Já vem definida em /etc/skel; isto é só uma
# segunda camada de segurança caso o skel não tenha sido aplicado.
xfconf-query -c xfce4-desktop -p /last-settings-migration-version -n -t uint -s 1 2>>"\$LOG" || \\
xfconf-query -c xfce4-desktop -p /last-settings-migration-version -s 1 2>>"\$LOG"

# BUG CORRIGIDO: o nome do "monitor" usado pelo xfdesktop para renderizar de
# fato varia MUITO por ambiente -- nome numerico "0" em alguns, "Virtual-1" em
# GNOME Boxes/QXL, "eDP-1"/"HDMI-1" em hardware real. Detectamos os monitores
# conectados via /sys/class/drm (sysfs), que NAO depende do xrandr -- o xrandr
# nao esta instalado na imagem (causa raiz do BUG-35: sem ele a versao anterior
# nunca descobria o monitor ativo) e, mesmo instalado, nao funciona cedo no
# login. Tratamos: os monitores que ja existem no xfconf + os do sysfs + "0"
# como fallback. (O fallback e "0", NAO "monitor0": o prefixo 'monitor' e
# concatenado abaixo; a versao anterior usava "monitor0" aqui e gerava o no
# lixo 'monitormonitor0'.)
EXISTING_MONITORS="\$(xfconf-query -c xfce4-desktop -l 2>/dev/null | sed -n 's#^/backdrop/screen0/monitor\\([^/]*\\)/.*#\\1#p' | sort -u)"
DRM_MONITORS=""
for st in /sys/class/drm/*/status; do
    [ -f "\$st" ] || continue
    [ "\$(cat "\$st" 2>/dev/null)" = "connected" ] || continue
    # basename do diretorio e "cardN-<CONNECTOR>", ex.: card0-Virtual-1;
    # removemos o prefixo "cardN-" para ficar com o nome do connector.
    conn="\$(basename "\$(dirname "\$st")")"
    DRM_MONITORS="\$DRM_MONITORS \${conn#*-}"
done
ALL_MONITORS="\$(printf '%s\\n%s\\n0\\n' "\$EXISTING_MONITORS" "\$DRM_MONITORS" | tr ' ' '\\n' | sort -u | grep -v '^\$')"
echo "monitores conhecidos (xfconf): \${EXISTING_MONITORS:-<nenhum>}"
echo "monitores sysfs (drm): \${DRM_MONITORS:-<nenhum>}"
echo "monitores a tratar: \${ALL_MONITORS:-<nenhum>}"

NEED_RESTART=0
for MON in \$ALL_MONITORS; do
    [ -z "\$MON" ] && continue

    # Corrige qualquer last-image/image-path JÁ EXISTENTE (com ou sem
    # "workspace0") que não seja a nossa.
    for SUFFIX in workspace0/last-image workspace0/image-path last-image image-path; do
        PROP="/backdrop/screen0/monitor\${MON}/\${SUFFIX}"
        CUR="\$(xfconf-query -c xfce4-desktop -p "\$PROP" 2>/dev/null)"
        if [ -n "\$CUR" ] && [ "\$CUR" != "\$WP" ]; then
            echo "corrigindo \$PROP (era: \$CUR)"
            xfconf-query -c xfce4-desktop -p "\$PROP" -s "\$WP" 2>>"\$LOG"
            NEED_RESTART=1
        fi
    done

    # Garante que workspace0/last-image e workspace0/image-path existam
    # mesmo que o xfdesktop ainda não os tenha criado para este monitor.
    for SUFFIX in workspace0/last-image workspace0/image-path; do
        PROP="/backdrop/screen0/monitor\${MON}/\${SUFFIX}"
        CUR="\$(xfconf-query -c xfce4-desktop -p "\$PROP" 2>/dev/null)"
        if [ -z "\$CUR" ]; then
            xfconf-query -c xfce4-desktop -p "\$PROP" -n -t string -s "\$WP" 2>>"\$LOG"
            NEED_RESTART=1
        fi
    done

    # Força o estilo "Esticado" em todo monitor que estamos gerenciando.
    STYLE_PROP="/backdrop/screen0/monitor\${MON}/workspace0/image-style"
    CUR_STYLE="\$(xfconf-query -c xfce4-desktop -p "\$STYLE_PROP" 2>/dev/null)"
    if [ "\$CUR_STYLE" != "\$STYLE" ]; then
        echo "corrigindo estilo de \$STYLE_PROP (era: \${CUR_STYLE:-<nao definido>})"
        xfconf-query -c xfce4-desktop -p "\$STYLE_PROP" -n -t int -s "\$STYLE" 2>>"\$LOG" || \\
        xfconf-query -c xfce4-desktop -p "\$STYLE_PROP" -s "\$STYLE" 2>>"\$LOG"
        NEED_RESTART=1
    fi
done

if [ "\$NEED_RESTART" = "1" ]; then
    # "xfdesktop --reload" e SIGHUP nem sempre forçam o xfdesktop a reler o
    # backdrop visualmente. Matamos e religamos o processo -- ele relê os
    # valores (já corretos) do xfconf ao subir de novo. Só chega aqui se
    # algo realmente precisava ser corrigido, então o "flash" preto só
    # ocorre quando há mudança de fato.
    echo "reiniciando xfdesktop para aplicar o wallpaper"
    pkill -x xfdesktop >/dev/null 2>&1 || true
    for i in \$(seq 1 10); do
        pgrep -x xfdesktop >/dev/null 2>&1 || break
        sleep 0.5
    done
    setsid xfdesktop >/dev/null 2>&1 &
    disown
    sleep 1
    echo "xfdesktop pgrep pos-restart: \$(pgrep -x xfdesktop || echo 'NAO ENCONTRADO')"
else
    echo "já estava tudo correto, nada a fazer"
fi

echo "concluido"
touch "\$MARKER"
EOF
chmod 0755 %{buildroot}%{_bindir}/capivaraos-set-wallpaper

install -d %{buildroot}%{_sysconfdir}/xdg/autostart
cat > %{buildroot}%{_sysconfdir}/xdg/autostart/capivaraos-wallpaper.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=CapivaraOS Wallpaper
Exec=/usr/bin/capivaraos-set-wallpaper
NoDisplay=true
X-GNOME-Autostart-Phase=Applications
OnlyShowIn=XFCE;
EOF

# ── Wallpaper no PRIMEIRO frame, sem flash (BUG-35) ─────────────────────────
# O autostart acima corrige o wallpaper DEPOIS que o xfdesktop já desenhou (com
# o image-style do monitor real ainda "Nenhuma", ele nao desenha imagem nenhuma
# no 1o frame -> aparece fundo liso por ~3s ate o script setar e reiniciar).
# Este hook roda no INICIO da sessao XFCE, ANTES do xfce4-session lancar o
# xfdesktop (o startxfce4 fonteia /etc/xdg/xfce4/xinitrc.d/* antes de subir a
# sessao). Ele grava o xfce4-desktop.xml do usuario com o NOME REAL do(s)
# monitor(es) detectado(s) via sysfs, ja com image-style=3 (Esticado) e o nosso
# last-image -> o xfdesktop ja nasce mostrando o fundo certo, sem flash nem
# restart, e sem depender do xfconfd/D-Bus ainda estarem no ar (escrevemos o
# arquivo direto, antes do xfconfd subir e le-lo).
install -d %{buildroot}%{_sysconfdir}/xdg/xfce4/xinitrc.d
cat > %{buildroot}%{_sysconfdir}/xdg/xfce4/xinitrc.d/50-capivaraos-wallpaper.sh << 'EOF'
#!/bin/sh
# Gera o backdrop do xfdesktop para os monitores conectados ANTES do xfdesktop
# subir, para o wallpaper CapivaraOS aparecer ja no primeiro frame. Ver
# capivaraos-branding.spec (BUG-35).
WP=/usr/share/backgrounds/capivaraos/capivaraos-wp-moonlight.png
CFG="$HOME/.config/xfce4/xfconf/xfce-perchannel-xml"
XML="$CFG/xfce4-desktop.xml"

# Nao mexer se o usuario ja tem o wallpaper aplicado (respeita escolha futura).
[ -f "$HOME/.config/.capivaraos-wallpaper-applied" ] && exit 0
[ -f "$WP" ] || exit 0

mkdir -p "$CFG"
{
  echo '<?xml version="1.0" encoding="UTF-8"?>'
  echo ''
  echo '<channel name="xfce4-desktop" version="1.0">'
  echo '  <property name="last-settings-migration-version" type="uint" value="1"/>'
  echo '  <property name="backdrop" type="empty">'
  echo '    <property name="screen0" type="empty">'
  _any=0
  for st in /sys/class/drm/*/status; do
    [ "$(cat "$st" 2>/dev/null)" = connected ] || continue
    conn=$(basename "$(dirname "$st")")
    mon=${conn#*-}
    _any=1
    echo "      <property name=\"monitor${mon}\" type=\"empty\">"
    echo '        <property name="workspace0" type="empty">'
    echo '          <property name="color-style" type="int" value="0"/>'
    echo '          <property name="image-style" type="int" value="3"/>'
    echo "          <property name=\"last-image\" type=\"string\" value=\"${WP}\"/>"
    echo "          <property name=\"image-path\" type=\"string\" value=\"${WP}\"/>"
    echo '        </property>'
    echo '      </property>'
  done
  # Fallback: se nada foi detectado no sysfs, ao menos cobre "monitor0".
  if [ "$_any" = 0 ]; then
    echo '      <property name="monitor0" type="empty">'
    echo '        <property name="workspace0" type="empty">'
    echo '          <property name="color-style" type="int" value="0"/>'
    echo '          <property name="image-style" type="int" value="3"/>'
    echo "          <property name=\"last-image\" type=\"string\" value=\"${WP}\"/>"
    echo "          <property name=\"image-path\" type=\"string\" value=\"${WP}\"/>"
    echo '        </property>'
    echo '      </property>'
  fi
  echo '    </property>'
  echo '  </property>'
  echo '</channel>'
} > "$XML"
EOF
chmod 0755 %{buildroot}%{_sysconfdir}/xdg/xfce4/xinitrc.d/50-capivaraos-wallpaper.sh

# ── Perfil do Anaconda: faz o instalador reconhecer o CapivaraOS (BUG-38) ────
# O Anaconda casa o perfil de instalacao pelo os_id do /etc/os-release. Como o
# nosso ID e "capivaraos" (nao "fedora"), NENHUM perfil casava e o instalador
# caia no default de /etc/anaconda/anaconda.conf, que define efi_dir=default.
# Em UEFI isso faz o gen_grub_cfgstub tentar gravar o stub em
# /boot/efi/EFI/default (inexistente -- shim/grub2-efi instalam em /EFI/fedora)
# -> "gen_grub_cfgstub script failed" e a instalacao FALHA no passo do
# bootloader. So aparece em UEFI real; em VM no modo BIOS/legacy o caminho EFI
# nem roda (por isso nao pegamos antes). Herdando base_profile=fedora, o
# CapivaraOS reusa efi_dir=fedora, esquema BTRFS e demais ajustes do Fedora.
install -d %{buildroot}%{_sysconfdir}/anaconda/profile.d
cat > %{buildroot}%{_sysconfdir}/anaconda/profile.d/capivaraos.conf << 'EOF'
[Profile]
profile_id = capivaraos
base_profile = fedora

[Profile Detection]
os_id = capivaraos
EOF

# ── Snapshots pré-upgrade: config 'root' do snapper criada no 1o boot ────────
# O capivaraos-upgrade (PROD-121) só tira snapshot automático antes do upgrade
# in-place se a raiz for btrfs E existir uma config 'root' do snapper. O pacote
# snapper (ver %packages do kickstart) não cria essa config sozinho, e o
# instalador do Xfce (Anaconda) não a configura. Então um oneshot de 1o boot a
# cria no sistema INSTALADO (na live a raiz não é btrfs -> o script sai sem
# fazer nada). ConditionPathExists=!... faz o systemd pular depois de criada.
install -d %{buildroot}%{_libexecdir}/capivaraos
cat > %{buildroot}%{_libexecdir}/capivaraos/snapper-firstboot << 'EOF'
#!/bin/bash
# Cria a config 'root' do snapper se a raiz for btrfs e ainda não existir.
# Idempotente; pensado para rodar uma vez no 1o boot do sistema instalado.
set -e
[ "$(findmnt -no FSTYPE /)" = btrfs ] || exit 0
command -v snapper >/dev/null 2>&1 || exit 0
snapper list-configs 2>/dev/null | grep -qw root && exit 0
snapper -c root create-config /
# Limites conservadores: sem timeline automática (não encher o disco); mantém
# os snapshots numerados (os pré/pós de transação e o do capivaraos-upgrade).
snapper -c root set-config TIMELINE_CREATE=no NUMBER_CLEANUP=yes NUMBER_LIMIT=10 NUMBER_LIMIT_IMPORTANT=10 || true
systemctl enable --now snapper-cleanup.timer >/dev/null 2>&1 || true
EOF
chmod 0755 %{buildroot}%{_libexecdir}/capivaraos/snapper-firstboot

install -d %{buildroot}%{_unitdir}
cat > %{buildroot}%{_unitdir}/capivaraos-snapper-setup.service << 'EOF'
[Unit]
Description=CapivaraOS: cria a configuracao snapper 'root' no 1o boot (btrfs)
Documentation=https://capivaraos.org
# Pula assim que a config existir (nada de stamp); e so em raiz btrfs.
ConditionPathExists=!/etc/snapper/configs/root
After=local-fs.target
Before=multi-user.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/libexec/capivaraos/snapper-firstboot

[Install]
WantedBy=multi-user.target
EOF

# ── Aviso leve de "nova versao" (PROD-123): script + timer/servico de usuario ─
# O Xfce nao tem GNOME Software; este e o nosso aviso proprio e leve. Roda por um
# timer de USUARIO (systemd --user), sem daemon persistente. E no-op enquanto o
# capivaraos-upgrade nao estiver instalado (pre-lancamento).
install -Dm0755 update-notify/update-notify \
    %{buildroot}%{_libexecdir}/capivaraos/update-notify
install -Dm0644 update-notify/capivaraos-update-notify.service \
    %{buildroot}%{_userunitdir}/capivaraos-update-notify.service
install -Dm0644 update-notify/capivaraos-update-notify.timer \
    %{buildroot}%{_userunitdir}/capivaraos-update-notify.timer

%post
# Splash de boot CapivaraOS
plymouth-set-default-theme capivaraos >/dev/null 2>&1 || true

# ── Tela de login LightDM (lightdm-gtk-greeter) com wallpaper CapivaraOS ────
# user-background=false: sem isso, o greeter mostra o fundo de tela do
# ÚLTIMO usuário logado em vez do nosso, já que essa opção fica "true" por
# padrão no lightdm-gtk-greeter. lightdm-gtk-greeter não tem um mecanismo de
# "*.conf.d"/"theme.conf.user" como o SDDM da spin KDE — editamos direto o
# /etc/lightdm/lightdm-gtk-greeter.conf (arquivo %config do pacote
# lightdm-gtk; o dnf preserva edições locais em atualizações futuras do
# pacote, marcado noreplace).
install -d %{_sysconfdir}/lightdm
if [ -f %{_sysconfdir}/lightdm/lightdm-gtk-greeter.conf ]; then
    sed -i \
        -e '/^background=/d' \
        -e '/^user-background=/d' \
        -e '/^\[greeter\]/a background=%{_datadir}/backgrounds/capivaraos/capivaraos-wp-moonlight.png\nuser-background=false' \
        %{_sysconfdir}/lightdm/lightdm-gtk-greeter.conf
else
    cat > %{_sysconfdir}/lightdm/lightdm-gtk-greeter.conf << EOF
[greeter]
background=%{_datadir}/backgrounds/capivaraos/capivaraos-wp-moonlight.png
user-background=false
EOF
fi

# GRUB_DISTRIBUTOR -> "CapivaraOS"
if [ -f %{_sysconfdir}/default/grub ]; then
    if grep -q '^GRUB_DISTRIBUTOR=' %{_sysconfdir}/default/grub; then
        sed -i 's/^GRUB_DISTRIBUTOR=.*/GRUB_DISTRIBUTOR="CapivaraOS"/' %{_sysconfdir}/default/grub
    else
        echo 'GRUB_DISTRIBUTOR="CapivaraOS"' >> %{_sysconfdir}/default/grub
    fi
fi

gtk-update-icon-cache -f %{_datadir}/icons/hicolor >/dev/null 2>&1 || true

%postun
if [ "$1" -eq 0 ]; then
    gtk-update-icon-cache -f %{_datadir}/icons/hicolor >/dev/null 2>&1 || true
fi

%posttrans
# Tema padrao do Plymouth (boot/desligamento): escrito direto aqui (ver
# justificativa detalhada no spec da spin KDE, idêntica para esta spin).
install -d %{_sysconfdir}/plymouth
cat > %{_sysconfdir}/plymouth/plymouthd.conf << 'EOF'
[Daemon]
Theme=capivaraos
EOF
plymouth-set-default-theme capivaraos >/dev/null 2>&1 || true

# Habilita o oneshot que cria a config 'root' do snapper no 1o boot (PROD-121).
# %posttrans roda com systemd/snapper ja instalados; o enable offline apenas cria
# o symlink WantedBy — o servico so age no 1o boot do sistema instalado (btrfs).
systemctl enable capivaraos-snapper-setup.service >/dev/null 2>&1 || true

# Habilita, para todos os usuarios, o timer do aviso leve de nova versao
# (PROD-123). --global cria o symlink em /etc/systemd/user; o servico so age
# quando ha nova versao E o capivaraos-upgrade esta presente (no-op ate la).
systemctl --global enable capivaraos-update-notify.timer >/dev/null 2>&1 || true

# ── Wallpaper padrão do xfdesktop (BUG-35) ───────────────────────────────────
# ATÉ a série 1.x, gravávamos o nosso PNG por cima dos defaults do Xfce
# (/usr/share/backgrounds/xfce/xfce-verticals|stripes|teal.png) como rede de
# segurança contra o fallback do xfdesktop no 1º login. Na série 2.x isso foi
# REMOVIDO: o dono quer os wallpapers padrão do Xfce disponíveis no seletor
# (pacote f45-backgrounds-xfce entra no %packages), então NÃO os sobrescrevemos. O
# padrão "Luar" continua garantido pela config de backdrop — /etc/skel
# (xfce4-desktop.xml, monitor0) + o xinitrc.d 50-capivaraos-wallpaper.sh, que
# grava o backdrop do(s) monitor(es) REAIS (via sysfs) ANTES do xfdesktop subir
# — que é a correção definitiva do BUG-35 (o clobber era só um extra).

# /etc/os-release, /etc/issue, /etc/issue.net (fedora-release-common):
# escritos aqui (em vez de %files) para evitar conflito de arquivo no dnf.
cat > %{_sysconfdir}/os-release << 'EOF'
NAME="CapivaraOS"
VERSION="Pup 2.0.0 (alpha5, preview)"
RELEASE_TYPE=stable
ID=capivaraos
ID_LIKE=fedora
VERSION_ID=45
VERSION_CODENAME=pup
PLATFORM_ID="platform:f45"
PRETTY_NAME="CapivaraOS Pup 2.0.0 (alpha5, preview)"
ANSI_COLOR="0;32"
LOGO=capivaraos-full-logo
CPE_NAME="cpe:/o:capivaraos:capivaraos:45"
DEFAULT_HOSTNAME=capivaraos
HOME_URL="https://capivaraos.org"
DOCUMENTATION_URL="https://capivaraos.org"
SUPPORT_URL="https://capivaraos.org"
BUG_REPORT_URL="https://capivaraos.org"
REDHAT_BUGZILLA_PRODUCT="Fedora"
REDHAT_BUGZILLA_PRODUCT_VERSION=45
REDHAT_SUPPORT_PRODUCT="Fedora"
REDHAT_SUPPORT_PRODUCT_VERSION=45
VARIANT="Pup 2.0.0 (alpha5, preview)"
VARIANT_ID=pup
EOF

cat > %{_sysconfdir}/issue << 'EOF'
CapivaraOS Pup 2.0.0 (alpha5, preview) \n \l

EOF

cat > %{_sysconfdir}/issue.net << 'EOF'
CapivaraOS Pup 2.0.0 (alpha5, preview)
EOF

# ── Reaplica os-release apos qualquer atualizacao futura do sistema ────────
# Ver justificativa detalhada no spec da spin KDE (mesmo mecanismo: garante
# que o titulo GRUB/BLS de kernels novos nao volte a "Fedora Linux").
#
# ATENCAO -- NAO troque o prefixo abaixo por um caminho de arquivo exato
# (ex.: /etc/os-release). Verificado empiricamente em container fedora:44
# (2026-07-17, spin Marsh): o %transfiletriggerin casa APENAS com prefixos de
# DIRETORIO e NUNCA com caminhos de arquivo exatos. Ate a 1.0.0 este gatilho
# era "-- %{_sysconfdir}/os-release" -- codigo morto: nunca disparou uma
# unica vez, e o bug que ele deveria corrigir seguia acontecendo em silencio.
#
# Por isso vigiamos o diretorio /usr/lib (dirname do arquivo que importa:
# /usr/lib/os-release, que pertence ao fedora-release-identity-basic; o
# /etc/os-release e apenas um symlink para ele). Esse prefixo dispara em
# quase toda transacao, entao a guarda logo abaixo faz o caso comum sair de
# imediato; so pagamos o kernel-install quando o os-release foi revertido.
%transfiletriggerin -- %{_prefix}/lib
# Caso comum: nosso os-release intacto, nada a fazer.
grep -q '^NAME="CapivaraOS"' %{_prefix}/lib/os-release 2>/dev/null && exit 0
cat > %{_sysconfdir}/os-release << 'EOF'
NAME="CapivaraOS"
VERSION="Pup 2.0.0 (alpha5, preview)"
RELEASE_TYPE=stable
ID=capivaraos
ID_LIKE=fedora
VERSION_ID=45
VERSION_CODENAME=pup
PLATFORM_ID="platform:f45"
PRETTY_NAME="CapivaraOS Pup 2.0.0 (alpha5, preview)"
ANSI_COLOR="0;32"
LOGO=capivaraos-full-logo
CPE_NAME="cpe:/o:capivaraos:capivaraos:45"
DEFAULT_HOSTNAME=capivaraos
HOME_URL="https://capivaraos.org"
DOCUMENTATION_URL="https://capivaraos.org"
SUPPORT_URL="https://capivaraos.org"
BUG_REPORT_URL="https://capivaraos.org"
REDHAT_BUGZILLA_PRODUCT="Fedora"
REDHAT_BUGZILLA_PRODUCT_VERSION=45
REDHAT_SUPPORT_PRODUCT="Fedora"
REDHAT_SUPPORT_PRODUCT_VERSION=45
VARIANT="Pup 2.0.0 (alpha5, preview)"
VARIANT_ID=pup
EOF

cat > %{_sysconfdir}/issue << 'EOF'
CapivaraOS Pup 2.0.0 (alpha5, preview) \n \l

EOF

cat > %{_sysconfdir}/issue.net << 'EOF'
CapivaraOS Pup 2.0.0 (alpha5, preview)
EOF

for kver in $(ls /lib/modules 2>/dev/null); do
    [ -f "/lib/modules/${kver}/vmlinuz" ] && \
        kernel-install add "${kver}" "/lib/modules/${kver}/vmlinuz" >/dev/null 2>&1 || true
done

%files
%{_datadir}/backgrounds/capivaraos/
%{_datadir}/pixmaps/capivaraos.png
%{_datadir}/pixmaps/capivaraos-logo.png
%{_datadir}/pixmaps/capivaraos-white.png
%{_datadir}/icons/hicolor/*/apps/capivaraos-logo.png
%{_datadir}/icons/hicolor/*/apps/capivaraos-full-logo.png
%{_datadir}/plymouth/themes/capivaraos/
%{_bindir}/capivaraos-set-wallpaper
%{_sysconfdir}/xdg/autostart/capivaraos-wallpaper.desktop
%{_sysconfdir}/xdg/xfce4/xinitrc.d/50-capivaraos-wallpaper.sh
%{_sysconfdir}/anaconda/profile.d/capivaraos.conf
%{_sysconfdir}/skel/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml
%{_sysconfdir}/skel/.face
%{_sysconfdir}/skel/.face.icon
%{_datadir}/cockpit/branding/capivaraos/
%{_libexecdir}/capivaraos/snapper-firstboot
%{_unitdir}/capivaraos-snapper-setup.service
%{_libexecdir}/capivaraos/update-notify
%{_userunitdir}/capivaraos-update-notify.service
%{_userunitdir}/capivaraos-update-notify.timer

%changelog
* Sun Sep 20 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.5.alpha5
- Novo wallpaper da marca "serie2" (capivaraos-wp-serie2.png, 3840x2160, 8-bit)
  somado ao conjunto — o hero verde da Série 2. Também vai p/ Marsh/Snout 2.x.
- Wallpapers PADRÃO do Xfce agora disponíveis no seletor: pacote f45-backgrounds-xfce
  no %packages do kickstart e REMOVIDO o clobber do %posttrans que sobrescrevia os
  3 defaults do Xfce (xfce-verticals/stripes/teal) com o nosso PNG. O padrão
  "Luar" segue garantido por /etc/skel + o xinitrc.d 50-capivaraos-wallpaper.sh
  (correção definitiva do BUG-35; o clobber era só rede de segurança extra).

* Sat Sep 19 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.4.alpha4
- Notificador de atualizacao leve no Xfce (PROD-123): como o Xfce nao tem GNOME
  Software, este e o aviso proprio de "nova versao". Sem daemon: um timer de
  USUARIO (systemd --user, ~3min apos login + 1x/dia) roda
  /usr/libexec/capivaraos/update-notify, que faz `capivaraos-upgrade check`
  (read-only) e, havendo nova versao, mostra UMA notificacao (notify-send) com o
  botao "Atualizar agora" -> abre `sudo capivaraos-upgrade run` num xfce4-terminal.
  No-op silencioso enquanto o capivaraos-upgrade/repo assinado nao estiverem
  presentes (guardrail FEAT-111 intacto). Timer habilitado p/ todos por
  `systemctl --global enable`. Requires: libnotify.

* Sat Sep 19 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.3.alpha3
- COS Dev Center MÍNIMO no Pup (PROD-122): a ISO passa a incluir o app
  capivara-central (pacote próprio, versão enxuta — 3 cards: IA local, dev, gh).
  Entra pelo %packages do kickstart e pelo repo local do build-all (2 RPMs).
  Esta build de branding só bumpa o rótulo preview (alpha2 -> alpha3) p/ marcar a
  ISO "tudo junto" (rebase + wallpapers + in-place/snapper + COS Dev). O botão de
  "nova versão" no Xfce fica com o notificador próprio leve (PROD-123).

* Sat Sep 19 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.2.alpha2
- Atualizacao in-place (FEAT-111 / PROD-121): porta o motor do repo assinado +
  dnf5 system-upgrade (capivaraos-upgrade, capivaraos-repos, build/publish/tests,
  chave GPG publica, docs) do capivaraos-snout-next/marsh-next, adaptado ao Pup
  (baseurl pup/, Release .pup, publish-repo SPIN=pup). O botao "nova versao" no
  Xfce fica com um notificador proprio leve (PROD-123).
- Snapshots "atualize sem medo" (PROD-121): o Pup 2.x cria a config 'root' do
  snapper no 1o boot (oneshot capivaraos-snapper-setup.service +
  /usr/libexec/capivaraos/snapper-firstboot), em raiz btrfs. Sem isso o
  capivaraos-upgrade nao tira snapshot automatico antes do upgrade in-place.
  Na sessao live e no-op. Pacotes snapper + btrfs-assistant entram pelo
  %packages do kickstart. Falta validar em VM instalada.

* Sat Sep 19 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.1.alpha1
- Primeira build da serie 2.x do Pup: rebase para Fedora 45 (base do 2.0) — PROD-119.
  O F45 Beta saiu (2026-09-18). Repo novo capivaraos-pup-next (clonado do
  capivaraos-pup-fedora p/ preservar a base Xfce), branch rebase-f45. Repoint do
  compose: build-all.sh --releasever=45, base do kickstart f44 -> f45
  (fedora-45/updates-released-f45), trava de updates em 45. os-release/issue ->
  Fedora 45 + "Pup 2.0.0 (alpha1, preview)". Pup CONTINUA Xfce (leve).
  Versionamento pre-release "0.N.alphaN.pup"; "2.0.0-1.pup" reservado p/ o
  lancamento publico conjunto das 3 spins (PROD-61). SMOKE BUILD p/ levantar
  quebras (Xfce/LightDM no F45, Anaconda 45) — NAO cortar ISO publica do F45 antes do GA.
- Wallpapers da marca 2.x (PROD-120): adota o conjunto da marca compartilhado
  com Marsh/Snout (moonlight/sunset/dev/comics/abstract-1..4), padrao "Luar"
  (moonlight) no desktop e no LightDM. REMOVE o conjunto proprio do 1.x (fotos
  de capivaras CC BY-SA do Wikimedia + variantes de cor solida + CREDITOS.txt +
  os scripts regen-*-wallpapers.sh); tags CC-BY-SA saem da License. Os
  wallpapers padrao extras seguem vindo do f45-backgrounds-xfce da base.

* Mon Aug 17 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.1.8-1
- Corrige a FALHA de instalacao em UEFI no passo do bootloader (BUG-38):
  "org.fedoraproject.Anaconda.BootloaderInstallationError: gen_grub_cfgstub
  script failed". Causa raiz: o Anaconda casa o perfil pelo os_id do os-release;
  com ID=capivaraos nenhum perfil casava e ele caia no default (efi_dir=default),
  entao o gen_grub_cfgstub tentava gravar em /boot/efi/EFI/default (inexistente:
  shim/grub2-efi vivem em /EFI/fedora). So afetava UEFI real (VMs em BIOS/legacy
  passavam). Fix: empacota /etc/anaconda/profile.d/capivaraos.conf herdando
  base_profile=fedora (reusa efi_dir=fedora, esquema BTRFS etc.).
* Sat Aug 15 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.1.7-1
- Release publica 1.1.7 (numero unico entre as spins: 1.1.3 e do Marsh,
  1.1.4-1.1.6 do Snout; 1.1.2 -> 1.1.7).
- Wallpaper CapivaraOS agora aplica AUTOMATICAMENTE no 1o login (live e
  instalado), sem precisar trocar na mao (BUG-35). O capivaraos-set-wallpaper
  passa a detectar o monitor via /sys/class/drm (o xrandr nao esta na imagem,
  causa raiz do bug) e corrige o no lixo "monitormonitor0"; o %posttrans grava
  o nosso PNG sobre os defaults do xfdesktop; um hook em xinitrc.d pre-configura
  o backdrop no inicio da sessao.
- CONHECIDO (deferido): no 1o boot ainda ha ~3s com o fundo antigo antes de
  virar o nosso (flash cosmetico). O wallpaper aplica de forma confiavel; falta
  so eliminar essa janela inicial -- rastreado para correcao definitiva futura.
- Consolida tambem a reconciliacao de licenca/marca (LEG-4) e ajustes
  acumulados desde a 1.1.2 (ver entradas abaixo).
* Sat Aug 15 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.1.2-4
- Wallpaper CapivaraOS agora aparece ja no PRIMEIRO frame, sem o flash de ~3s
  de fundo liso (BUG-35). O -3 fazia o wallpaper aplicar, mas so depois do
  script rodar (o image-style do monitor real nascia "Nenhuma", entao o
  xfdesktop nao desenhava imagem ate o script setar e reiniciar). Novo hook
  /etc/xdg/xfce4/xinitrc.d/50-capivaraos-wallpaper.sh gera o xfce4-desktop.xml
  do usuario com o nome real do(s) monitor(es) (via sysfs) ANTES do xfdesktop
  subir -> primeiro frame ja nasce com image-style=3 e o nosso last-image, sem
  flash nem restart, sem depender de xrandr/xfconfd em runtime.
* Sat Aug 15 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.1.2-3
- Wallpaper do CapivaraOS agora aparece ja no PRIMEIRO login (live e instalado)
  -- BUG-35. Causa raiz: sem config de backdrop para o nome real do monitor, o
  xfdesktop caia no arquivo default compilado (xfce-verticals/stripes/teal.png),
  que nem existiam como .png -> aparecia o fundo do Fedora ate o usuario trocar
  na mao uma vez. Correcoes:
  . %posttrans grava o nosso PNG por cima desses tres arquivos default do
    xfdesktop (nao existem/nao sao de nenhum pacote -> sem conflito de dnf).
    Assim o 1o boot ja nasce com o fundo certo, sem depender de runtime.
  . capivaraos-set-wallpaper: detecta monitores via /sys/class/drm (sysfs) em
    vez de xrandr, que NAO esta instalado na imagem -- por isso o script nunca
    descobria o monitor ativo. Corrige tambem o no lixo "monitormonitor0"
    (fallback era "monitor0", concatenado depois de "monitor"; agora e "0").
* Fri Aug 14 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.1.2-2
- Reconciliacao de licenca/marca (LEG-4): corrige o metadado License: do RPM.
  Antes "CC-BY-SA-4.0 AND MIT" -- (a) marcava MIT sem nada MIT no pacote (codigo
  e config do projeto sao GPLv3, como o LICENSE de topo), (b) varria a identidade
  visual sob CC-BY-SA (contradiz a marca) e (c) omitia CC-BY-SA-3.0 de uma das
  fotos embarcadas. Agora: GPL-3.0-or-later AND LicenseRef-CapivaraOS-Trademark
  AND CC-BY-SA-3.0 AND CC-BY-SA-4.0. Correcao de metadado apenas; a atribuicao
  exigida (CREDITOS.txt + creditos gravados nas imagens) ja estava correta (LEG-3).
- Adiciona TRADEMARK.md: nome/logo CapivaraOS sao marca do projeto (direitos
  reservados); codigo GPLv3; wallpapers fotograficos de terceiros CC BY-SA
  creditados em backgrounds/CREDITOS.txt.

* Tue Jul 21 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.1.2-1
- A arte-mestre backgrounds/CapivaraOS_Logo.png deixa de ser instalada como
  papel de parede. Ela mora na pasta backgrounds/ apenas por ser a FONTE da
  qual os wallpapers sao derivados, mas o %install usava um glob "*.png" e a
  levava junto -- ela aparecia no seletor do xfdesktop como uma opcao
  escolhivel e, aplicada, saia com a logo gigante e cortada pelo painel
  (visto em captura da 1.1.1). Agora o loop de instalacao a pula.

* Tue Jul 21 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.1.1-1
- Zona segura nos wallpapers de foto: a logo e o credito de autoria sairam de
  40px/24px das laterais para 250px. Numa tela 4:3 exibindo um wallpaper 16:9
  em "Ampliado"/zoom, o corte e de 240px de CADA lado -- logo e credito caiam
  inteiros na faixa cortada. Confirmado em VM 4:3, onde o credito aparecia
  truncado como "...ann - CC BY-SA 4.0". As fotos sao CC BY-SA e a licenca
  EXIGE atribuicao, entao um credito cortado e um problema de licenciamento,
  nao so de layout. O estilo padrao da spin continua "Esticado" (que nao
  corta); a zona segura protege tambem quem trocar o estilo pelo seletor.
- Sufixo ".pup" no Release: as tres spins constroem um pacote com o mesmo Name
  e compartilham ~/rpmbuild, entao versoes iguais entre spins geravam nomes de
  arquivo identicos. Com o sufixo a colisao e impossivel por construcao, em
  vez de depender de escolher versoes livres na mao.
- Versao 1.1.0 -> 1.1.1 tambem resolve a duplicata com a Marsh 1.1.0.

* Tue Jul 21 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.1.0-1
- Rebrand: nova logo do CapivaraOS (capivara andando) em todo o branding.
  A logo anterior (capivara sentada) era derivada de um desenho de banco de
  imagens e apresentava risco de similaridade substancial; a nova arte e
  original. Ver DOC-6.
  . backgrounds/CapivaraOS_Logo.png trocada pela arte nova (mesmo canvas
    1536x1024), e icons/capivaraos-logo.png pela capivara sem texto.
  . 7 wallpapers de cor solida e o icone quadrado icons/capivaraos.png
    regerados por branding/regen-solid-wallpapers.sh (script novo aqui,
    trazido da spin Marsh -- offline, nao precisa de rede).
  . 6 wallpapers fotograficos regerados por regen-photo-wallpapers.sh, para
    que a marca d'agua e os creditos saiam com a logo nova.
- Assets derivados deixam de sair de -crop com coordenadas fixas sobre a
  logo-mestre e passam a vir de arquivos versionados:
  . logo do Cockpit/Anaconda WebUI: agora icons/capivaraos-head.png (asset
    novo). O recorte antigo, "-crop 360x300+480+90", fora calibrado para a
    capivara sentada; com a logo nova ele recortava o LOMBO do animal, sem
    falhar o build -- o instalador sairia com uma mancha marrom no lugar da
    logo.
  . avatar padrao (.face): agora icons/capivaraos-logo.png achatada sobre
    branco, no lugar de "-crop 1536x600+0+0".
- Corrige o file trigger de os-release, que era codigo morto: o gatilho era
  "%transfiletriggerin -- /etc/os-release", um caminho de ARQUIVO exato, e o
  %transfiletriggerin casa apenas com prefixos de DIRETORIO. Ele nunca
  disparou uma unica vez desde a 1.0.0. Agora vigia /usr/lib (com guarda de
  saida rapida), como na spin Marsh. Sem isso, uma atualizacao futura do
  fedora-release reverteria o os-release e o titulo GRUB/BLS de kernels
  novos voltaria a "Fedora Linux".

* Fri Jun 19 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.0.0-6
- Corrige causa raiz REAL do wallpaper Xfce nao aplicar por padrao: o nome
  do "monitor" usado pelo xfdesktop pra renderizar varia por ambiente
  ("monitor0" em alguns, "monitorVirtual-1" em GNOME Boxes/QXL, confirmado
  em teste real). O script anterior so verificava/corrigia "monitor0" e,
  como esse (nao usado para renderizacao) ja estava certo, pulava a
  correcao do monitor de fato ativo. Agora trata TODOS os monitores
  conhecidos (existentes no xfconf + detectados via xrandr + monitor0
  como fallback).
- Estilo padrao do wallpaper trocado de "Ampliado"/Zoomed (5, cortava a
  imagem) para "Esticado"/Stretched (3), a pedido.

* Fri Jun 19 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.0.0-5
- Corrige causa raiz do wallpaper Xfce: adiciona
  last-settings-migration-version=1 ao /etc/skel/.config/xfce4/.../
  xfce4-desktop.xml. Sem essa propriedade, o xfdesktop roda uma rotina de
  "migracao" no primeiro start de cada novo perfil (live ISO a cada boot,
  E o primeiro login real apos instalar) que sobrescreve last-image/
  image-path com o padrao compilado do Fedora -- confirmado via pesquisa
  (forums.xfce.org) e por teste real (o roxo aparecia certo no LightDM,
  mas era resetado assim que o xfdesktop subia pela primeira vez para o
  usuario). Script de runtime agora so reinicia o xfdesktop (causando o
  "flash" preto reportado) quando o valor atual realmente esta errado.
- Logo do Cockpit/Anaconda WebUI: troca o recorte do corpo inteiro da
  capivara (silhueta larga ~2.5:1, que "achatava" dentro da caixa quadrada
  pequena do CSS) por um recorte da cabeça (proporcao ~quadrada, preenche
  a caixa corretamente) e aumenta a caixa de 2rem para 2.5rem via
  branding.css (pedido: logo do mesmo tamanho do texto do titulo ao lado).

* Fri Jun 19 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.0.0-4
- Adiciona branding do Cockpit/Anaconda WebUI
  (/usr/share/cockpit/branding/capivaraos/): o instalador grafico da ISO
  live (tela "Instalacao CapivaraOS") roda sobre Cockpit, que escolhe a
  pasta de branding pelo ID= do os-release, caindo para ID_LIKE=fedora
  (logo do Fedora) quando nao existe uma pasta com o ID da propria
  distro. Confirmado via strings do binario cockpit-ws
  ("/usr/share/cockpit/branding/%s" + leitura de ID_LIKE do os-release).

* Fri Jun 19 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.0.0-3
- Converte os 7 wallpapers de cor solida (reaproveitados da Marsh) de
  PNG 16-bit/canal para 8-bit/canal. Causa raiz real do wallpaper nao
  aparecer: confirmado em teste real (GNOME Boxes) que o xfdesktop
  carrega normalmente PNGs 8-bit (os fotograficos funcionavam) mas falha
  silenciosamente com PNG 16-bit (mantem a ultima imagem valida na tela,
  sem erro visivel) -- os 16-bit nunca tinham sido testados no Xfce, só
  no Plasma da spin Marsh, que tolera o formato.

* Fri Jun 19 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.0.0-2
- Wallpaper padrao trocado para o roxo com logo branca
  (capivaraos-desktop-roxo-branco.png), conforme pedido
- Corrige aplicacao do wallpaper: "xfdesktop --reload"/SIGHUP nao forcavam
  releitura visual do backdrop em teste real (GNOME Boxes/QXL); agora o
  processo xfdesktop e reiniciado para reler o xfconf
- Script de aplicacao do wallpaper agora descobre o nome real do monitor
  via xrandr, alem do fallback "monitor0" (confirmado como o nome usado
  neste ambiente de teste)

* Fri Jun 19 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.0.0-1
- Versao inicial do CapivaraOS Pup (Fedora 44, Xfce)
