# =============================================================================
# CapivaraOS Pup — pós-instalação: ajustes finos de branding
# =============================================================================
#
# A maior parte do branding (wallpapers, ícones "Sobre o Sistema", tema
# Plymouth, fundo do LightDM, /etc/os-release, /etc/issue, avatar padrão,
# wallpaper padrão do Xfce) já é instalada pelo pacote `capivaraos-branding`
# (ver ../rpm/capivaraos-branding.spec). Este post-script cobre apenas o que
# não cabe num pacote RPM: regeneração da initramfs com o tema Plymouth,
# idioma de fallback e o atalho "Instalar CapivaraOS" na área de trabalho da
# sessão live.

%post
# ── Regera a initramfs com o tema Plymouth do CapivaraOS ────────────────────
# O kernel-core gera /boot/initramfs-*.img durante a transação de pacotes do
# dnf (no scriptlet do próprio kernel), que roda ANTES do %posttrans do
# pacote capivaraos-branding (que escreve /etc/plymouth/plymouthd.conf com
# Theme=capivaraos). Sem regenerar aqui, a initramfs da ISO live continua
# com o tema padrão do Plymouth. Este %post roda depois de toda a transação
# de pacotes, garantindo que o dracut leia o plymouthd.conf já atualizado.
#
# --no-hostonly (e --no-hostonly-cmdline) é OBRIGATÓRIO (BUG-40, comprovado
# 2026-08-17). O padrão do dracut no Fedora é hostonly="yes"; como este %post
# roda no BUILD (o dracut enxerga o hardware da MÁQUINA DE BUILD), sem estes
# flags o initramfs sai só com os drivers do build. Isso NÃO afeta o live boot
# (roda do USB, drivers genéricos), mas o SISTEMA INSTALADO herda esse mesmo
# initramfs e, num hardware com storage diferente do build, NÃO acha o disco
# raiz -> dracut-initqueue timeout -> "Not all disks have been found" ->
# emergency mode. Caso real: Positivo NTB Q232A (eMMC/Bay Trail): o initramfs
# hostonly tinha nvme (do build) mas NÃO tinha sdhci-acpi/sdhci-pci/mmc_block
# (do eMMC do alvo). Genérico (--no-hostonly) inclui todos -> boota em qualquer
# hardware. Depois de instalado, updates de kernel regeneram hostonly no
# proprio alvo (correto). NÃO reverter para hostonly.
for kver in $(ls /lib/modules); do
    dracut -f --no-hostonly --no-hostonly-cmdline "/boot/initramfs-${kver}.img" "${kver}"
done

# ── Remove o /etc/kernel/cmdline "fantasma" da imagem live (PROD-133) ───────
# BLOCKER do 2.0. Este %post roda no BUILD; o instalador live do Fedora (liveimg)
# COPIA o rootfs da live para o alvo, arrastando junto o /etc/kernel/cmdline que
# nasce aqui no build — com o UUID de raiz do AMBIENTE DE BUILD (inexistente no
# disco do usuario) e SEM rootflags=subvol=root (a raiz e btrfs num subvolume).
# O Anaconda reescreve as entradas BLS do install corretamente (por isso o kernel
# do install boota), mas NAO corrige esse arquivo. Resultado: o kernel-install usa
# esse /etc/kernel/cmdline como molde da linha `options` de TODO kernel novo -> o
# 1o update de kernel gera uma entrada BLS com root inexistente e sem subvol ->
# nao acha /sbin/init -> dracut emergency mode (root vem locked, sem shell de
# resgate). Caso real: VM (Boxes) da comunidade, update 7.2.7 -> 7.2.8, 2026-09-28.
#
# Fix: eliminamos o arquivo (e a variante /usr/lib/kernel/cmdline, por seguranca).
# Sem ele, na proxima atualizacao de kernel o kernel-install deriva a cmdline do
# /proc/cmdline REAL do sistema JA INSTALADO -- que traz root=UUID=<real> ro
# rootflags=subvol=root rhgb quiet corretos, para qualquer layout (btrfs/LUKS/...).
# Ordem de precedencia do kernel-install (man kernel-install): /etc/kernel/cmdline,
# senao /usr/lib/kernel/cmdline, senao /proc/cmdline (sem BOOT_IMAGE=/initrd=).
# E o comportamento do Fedora live padrao, que nao embarca esse arquivo.
# VALIDAR sempre num install limpo: instalar em VM -> rodar 1 update de kernel ->
# conferir a entrada nova (root+rootflags) e o boot. Espelhado do Marsh (commit 0bbc113).
rm -f /etc/kernel/cmdline /usr/lib/kernel/cmdline

# ── Idioma: pt_BR com fallback para en_US ───────────────────────────────────
# A diretiva "lang pt_BR.UTF-8" do kickstart já grava LANG=pt_BR.UTF-8 em
# /etc/locale.conf; adicionamos LANGUAGE para que traduções ausentes em
# pt_BR caiam para en_US em vez de en_US "puro" sem fallback.
if [ -f /etc/locale.conf ]; then
    sed -i '/^LANGUAGE=/d' /etc/locale.conf
fi
echo 'LANGUAGE=pt_BR:en_US' >> /etc/locale.conf

# ── Ícone "Instalar CapivaraOS" — APENAS na sessão live ─────────────────────
# O instalador é fornecido pelo Anaconda live via
# /usr/share/applications/liveinst.desktop (NoDisplay=true). Em sessões
# live, o script livesys-xfce (pacote livesys-scripts,
# /usr/libexec/livesys/sessions.d/livesys-xfce) copia esse liveinst.desktop
# para a área de trabalho do usuário "liveuser" (e só lá — ele NÃO roda no
# sistema já instalado), define NoDisplay=false e marca como executável.
# Aqui apenas renomeamos/reidentificamos o liveinst.desktop com o nome e o
# ícone do CapivaraOS antes disso acontecer, mantendo NoDisplay=true (o
# livesys-xfce faz o sed para NoDisplay=false ao copiá-lo para a área de
# trabalho live).
if [ -f /usr/share/applications/liveinst.desktop ]; then
    sed -i \
        -e '/^Name\[/d' \
        -e '/^GenericName\[/d' \
        -e '/^Comment\[/d' \
        -e 's/^Name=.*/Name=Instalar CapivaraOS/' \
        -e 's/^GenericName=.*/GenericName=Instalar CapivaraOS/' \
        -e 's/^Comment=.*/Comment=Instala o CapivaraOS permanentemente no computador/' \
        -e 's#^Icon=.*#Icon=/usr/share/pixmaps/capivaraos-white.png#' \
        /usr/share/applications/liveinst.desktop
    grep -q '^Name=Instalar CapivaraOS' /usr/share/applications/liveinst.desktop || \
        echo 'Name=Instalar CapivaraOS' >> /usr/share/applications/liveinst.desktop
    grep -q '^Icon=/usr/share/pixmaps/capivaraos-white.png' /usr/share/applications/liveinst.desktop || \
        echo 'Icon=/usr/share/pixmaps/capivaraos-white.png' >> /usr/share/applications/liveinst.desktop
fi

%end
