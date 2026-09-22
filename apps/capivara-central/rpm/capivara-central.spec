Name:           capivara-central
Version:        0.2.0
Release:        7%{?dist}.pup
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
* Tue Sep 22 2026 CapivaraOS Bot <capivaraos-bot@users.noreply.github.com> - 0.2.0-7.pup
- Editor da estação = VSCodium (decisão do dono). O card "Ferramentas de dev"
  passa a oferecer VSCodium (FOSS, Open VSX) como editor RECOMENDADO — a IA no
  editor (Cline/Continue) instala limpo nele, sem a verificação de assinatura do
  VS Code. VS Code segue como opção. install-devtools-system ganha install_vscodium
  (repo download.vscodium.com, pacote 'codium', gpgkey verificada). Backend/UI:
  vscodium em DEV_TOOLS, installed_dev_tool_keys/installed_dev_tools/installed_apps/
  open_app; Cline já tenta o codium primeiro (0.2.0-6). Ação polkit atualizada.

* Tue Sep 22 2026 CapivaraOS Bot <capivaraos-bot@users.noreply.github.com> - 0.2.0-6.pup
- setup-devtools/Cline: corrige a lógica de mensagem — não diz mais "nenhum
  editor encontrado" quando o editor existe mas a instalação falhou. Tenta o
  VSCodium primeiro (Open VSX, sem verificação de assinatura) e, se o VS Code
  recusar o Cline por assinatura (comum em instalação nova/VM via CLI), dá aviso
  ACIONÁVEL (instalar pela aba Extensões do VS Code, ou usar o VSCodium). Card
  segue best-effort (Cline é por-usuário, não derruba os demais itens).

* Tue Sep 22 2026 CapivaraOS Bot <capivaraos-bot@users.noreply.github.com> - 0.2.0-5.pup
- Sessao LIVE: os cards (IA local, Ferramentas de dev, gh) agora DETECTAM a
  sessao de demonstracao (raiz overlay em RAM / /run/initramfs/live) e BLOQUEIAM
  cedo com um dialogo claro ("instale no disco primeiro"), em vez de baixar 1 GB
  e falhar no meio com "Failed writing to disk"/ENOSPC. Backend: is_live_session().
  No sistema instalado em disco nada muda (instala normal).

* Tue Sep 22 2026 CapivaraOS Bot <capivaraos-bot@users.noreply.github.com> - 0.2.0-4.pup
- Card "Ferramentas de dev": o diálogo agora PRÉ-MARCA e TRAVA os itens já
  instalados (mostra "já instalado") e só instala/habilita o botão para os NOVOS
  — evita reinstalar. Backend expõe installed_dev_tool_keys(). (Melhoria vinda do
  chat de outra spin; no Pup só há este diálogo, pois "Trilhas de linguagem" não
  existe na versão mínima.)

* Mon Sep 21 2026 CapivaraOS Bot <capivaraos-bot@users.noreply.github.com> - 0.2.0-3.pup
- Ícone do app: corrige os "quadradinhos" (restos do xadrez do JPEG de origem)
  que sobravam nos cantos arredondados — máscara com cantos mais internos (raio
  150, bounds 90,84→946,952) para o arco cair no branco da tile, sem xadrez.
  Verificado nos tamanhos pequenos (48/64px). Master brand-assets/cos-dev-icon.png
  atualizado (reaproveitar no Marsh/Snout 2.x).
- Ferramentas de dev/Docker: corrige a falha real no F45 (rc=1). O repo do Docker
  NÃO tem pacotes p/ Fedora 45 ainda (/linux/fedora/45/ = 404; F44/F43 = 200) e o
  Fedora não empacota docker-ce. Agora o install-docker descobre a versão de
  Fedora mais recente já publicada pelo Docker e fixa o baseurl nela (pacotes do
  F-anterior funcionam); se nenhuma responder, avisa e segue (não derruba o card —
  é indisponibilidade upstream). Revisar no GA do F45.

* Sun Sep 20 2026 CapivaraOS Bot <capivaraos-bot@users.noreply.github.com> - 0.2.0-2.pup
- Novo ícone do app "cos dev by CapivaraOS" (fundo transparente) nos 5 tamanhos;
  origem canônica em brand-assets/cos-dev-icon.png (reutilizar no Marsh/Snout 2.x).
- Card "IA local": avisa que no Fedora 45 o Ollama inclui a pilha AMD/ROCm
  (~6 GB) e recomenda instalar no sistema em disco (não na sessão live).
- install-ai-system: comentário corrigido p/ a realidade do F45 (ollama puxa ROCm).
- setup-devtools: não imprime mais ">>> concluídas" quando algum item falha
  (mensagem honesta + dica de que itens grandes instalam melhor em disco). O
  rc=1 vinha do passo de sistema (VS Code/Docker) — típico em sessão live sem
  espaço.

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
