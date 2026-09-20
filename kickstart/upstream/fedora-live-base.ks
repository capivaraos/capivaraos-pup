# Vendorizado de fedora-kickstarts: fedora-live-base.ks
# Fonte original: https://forge.fedoraproject.org/releng/spin-kickstarts
# (histórico anterior à migração para kiwi, commit d93b2ac)
#
# Defines the basics for all kickstarts in the fedora-live branch
# Does not include package selection (other then mandatory)
# Does not include localization packages or configuration
#
# Does includes "default" language configuration (kickstarts including
# this template can override these settings)
#
# NOTA CapivaraOS: lang/keyboard/timezone são sobrescritos em
# capivaraos-marsh.ks (pt_BR.UTF-8 / br-abnt2 / America/Sao_Paulo).

lang en_US.UTF-8
keyboard us
timezone US/Eastern
selinux --enforcing
firewall --enabled --service=mdns
xconfig --startxonboot
zerombr
# NOTA CapivaraOS: tamanho do filesystem de TRABALHO (vira squashfs comprimido
# depois — NÃO afeta o tamanho da ISO final). Era 8192 (8 GiB) na série 1.x e
# CABIA; na série 2.x (Fedora 45) o conjunto passou de 8 GiB e o compose
# falhava com "precisa de NNN MB a mais no /" (PayloadInstallationError). O que
# cresceu: o COS Dev mínimo puxa gtk4+libadwaita+podman+flatpak e o
# btrfs-assistant (snapshots) arrasta a pilha Qt6 inteira no Xfce (o Marsh já
# tem Qt "de graça" por ser KDE). Subimos para 16384 (16 GiB), igual ao Snout,
# com folga sobre o pico observado (~8,5 GiB instalados). A ISO final segue leve.
clearpart --all
part / --size 16384 --fstype ext4
services --enabled=NetworkManager,ModemManager --disabled=sshd
network --bootproto=dhcp --device=link --activate
# NOTA CapivaraOS: "rootpw --lock --iscrypted locked" (original upstream) faz o
# anaconda montar o hash "!locked" e passá-lo para "chpasswd -e", que o
# chpasswd/libxcrypt do Fedora 44 rejeita por não ser um hash válido
# (AnacondaError: Unable to set password for new user: status=1). "rootpw
# --lock" (sem senha) produz "!" (placeholder padrão de conta bloqueada do
# /etc/shadow), que o chpasswd -e aceita sem problema.
rootpw --lock
shutdown

# NOTA CapivaraOS: caminho relativo ao cwd do anaconda (kickstart/), não a
# este arquivo — ver nota em fedora-live-kde-base.ks.
%include upstream/fedora-repo.ks

%packages
# Explicitly specified here:
# <notting> walters: because otherwise dependency loops cause yum issues.
kernel
kernel-modules
kernel-modules-extra

# The point of a live image is to install
anaconda-install-env-deps
anaconda-live
@anaconda-tools
# Anaconda has a weak dep on this and we don't want it on livecds, see
# https://fedoraproject.org/wiki/Changes/RemoveDeviceMapperMultipathFromWorkstationLiveCD
-fcoe-utils
-device-mapper-multipath
-sdubby

# Need aajohan-comfortaa-fonts for the SVG rnotes images
aajohan-comfortaa-fonts

# Without this, initramfs generation during live image creation fails: #1242586
dracut-live

# anaconda needs the locales available to run for different locales
glibc-all-langpacks

# provide the livesys scripts
livesys-scripts
%end

%post
# Enable livesys services
systemctl enable livesys.service
systemctl enable livesys-late.service

# enable tmpfs for /tmp
systemctl enable tmp.mount

# make it so that we don't do writing to the overlay for things which
# are just tmpdirs/caches
# note https://bugzilla.redhat.com/show_bug.cgi?id=1135475
cat >> /etc/fstab << EOF
vartmp   /var/tmp    tmpfs   defaults   0  0
EOF

# work around for poor key import UI in PackageKit
rm -f /var/lib/rpm/__db*
echo "Packages within this LiveCD"
rpm -qa --qf '%{size}\t%{name}-%{version}-%{release}.%{arch}\n' |sort -rn
# Note that running rpm recreates the rpm db files which aren't needed or wanted
rm -f /var/lib/rpm/__db*

# go ahead and pre-make the man -k cache (#455968)
/usr/bin/mandb

# make sure there aren't core files lying around
rm -f /core*

# remove random seed, the newly installed instance should make it's own
rm -f /var/lib/systemd/random-seed

# convince readahead not to collect
# FIXME: for systemd

echo 'File created by kickstart. See systemd-update-done.service(8).' \
    | tee /etc/.updated >/var/.updated

# Drop the rescue kernel and initramfs, we don't need them on the live media itself.
# See bug 1317709
rm -f /boot/*-rescue*

# Disable network service here, as doing it in the services line
# fails due to RHBZ #1369794
systemctl disable network

# Remove machine-id on pre generated images
rm -f /etc/machine-id
touch /etc/machine-id

%end
