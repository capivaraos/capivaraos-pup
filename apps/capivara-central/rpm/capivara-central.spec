Name:           capivara-central
Version:        0.2.0
Release:        1%{?dist}.pup
Summary:        COS Dev Center (mínimo) — onboarding do CapivaraOS Pup

# App próprio (GPLv3); o ícone "COS Dev" (tile CapivaraOS) é marca reservada.
License:        GPL-3.0-or-later AND LicenseRef-CapivaraOS-Trademark
URL:            https://capivaraos.org
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch

# UI em GTK4/libadwaita com backend PyGObject; instalações privilegiadas via
# polkit. Versão MÍNIMA do port do Snout (PROD-122): só 3 cards no Pup (leve).
Requires:       python3-gobject
Requires:       gtk4
Requires:       libadwaita
Requires:       polkit
Requires:       flatpak
# git: template global de hooks do card "GitHub CLI + pre-commit".
Requires:       git
# podman: Open WebUI roda em container rootless (card "Ferramentas de dev").
Requires:       podman
# xfce4-terminal: terminal padrão do Pup (Xfce) para o login interativo do gh.
Requires:       xfce4-terminal

%description
COS Dev Center é o app de onboarding em português do CapivaraOS Pup. Versão
mínima e leve: no primeiro boot, oferece instalar em um clique só os extras
essenciais da estação de desenvolvimento — IA local (Ollama + Alpaca +
extensão Continue), ferramentas de dev e gh + pre-commit. Interface em
GTK4/libadwaita; as etapas que exigem administrador são autenticadas por
polkit. O app nunca roda como root.

%prep
%autosetup -n %{name}-%{version}

%build
# Nada a compilar: aplicação Python/GTK.

%install
# --- Código da aplicação (Python) ---
install -d %{buildroot}%{_datadir}/%{name}
install -m0644 capivara-central.py %{buildroot}%{_datadir}/%{name}/capivara-central.py
install -m0644 backend.py          %{buildroot}%{_datadir}/%{name}/backend.py

# --- Launcher em /usr/bin ---
install -Dm0755 capivara-central %{buildroot}%{_bindir}/capivara-central

# --- Helpers privilegiados/orquestrador em /usr/libexec ---
install -Dm0755 libexec/setup-ai                %{buildroot}%{_libexecdir}/%{name}/setup-ai
install -Dm0755 libexec/install-ai-system       %{buildroot}%{_libexecdir}/%{name}/install-ai-system
install -Dm0755 libexec/setup-devtools          %{buildroot}%{_libexecdir}/%{name}/setup-devtools
install -Dm0755 libexec/install-devtools-system %{buildroot}%{_libexecdir}/%{name}/install-devtools-system
install -Dm0755 libexec/setup-gh                %{buildroot}%{_libexecdir}/%{name}/setup-gh
install -Dm0755 libexec/install-gh-system       %{buildroot}%{_libexecdir}/%{name}/install-gh-system

# --- polkit action ---
install -Dm0644 data/org.capivaraos.central.policy \
    %{buildroot}%{_datadir}/polkit-1/actions/org.capivaraos.central.policy

# --- .desktop + ícone ---
install -Dm0644 data/org.capivaraos.Central.desktop \
    %{buildroot}%{_datadir}/applications/org.capivaraos.Central.desktop
for S in 48 64 128 256 512; do
    install -Dm0644 data/org.capivaraos.Central-${S}.png \
        %{buildroot}%{_datadir}/icons/hicolor/${S}x${S}/apps/org.capivaraos.Central.png
done

# --- Autostart de 1º boot (via /etc/skel; abre uma vez no 1º login) ---
install -Dm0644 data/org.capivaraos.Central-autostart.desktop \
    %{buildroot}%{_sysconfdir}/skel/.config/autostart/org.capivaraos.Central.desktop

%files
%license LICENSE
%doc README.md
%{_datadir}/%{name}/
%{_bindir}/capivara-central
%{_libexecdir}/%{name}/
%{_datadir}/polkit-1/actions/org.capivaraos.central.policy
%{_datadir}/applications/org.capivaraos.Central.desktop
%{_datadir}/icons/hicolor/*/apps/org.capivaraos.Central.png
%{_sysconfdir}/skel/.config/autostart/org.capivaraos.Central.desktop

%changelog
* Sat Sep 19 2026 CapivaraOS Bot <capivaraos-bot@users.noreply.github.com> - 0.2.0-1.pup
- COS Dev Center MÍNIMO para o Pup (Xfce) — PROD-122. Versão enxuta do port do
  Snout (PROD-117): mantém só os 3 cards essenciais — IA local, Ferramentas de
  dev e GitHub CLI + pre-commit — e remove Trilhas de linguagem, Ligar GPU e o
  card "Atualizar o CapivaraOS" (o "nova versão" no Pup fica com o notificador
  próprio leve, PROD-123). Reaproveita a UI GTK4/libadwaita e os helpers shell
  (setup-ai/devtools/gh + install-*-system) e a polkit action, só dos 3 cards.
  Terminal do "Entrar no GitHub" = xfce4-terminal (fallback xterm). Autostart e
  .desktop ajustados para XFCE (OnlyShowIn=XFCE). Requires enxuto (sem ptyxis/
  curl): python3-gobject, gtk4, libadwaita, polkit, flatpak, git, podman,
  xfce4-terminal.
