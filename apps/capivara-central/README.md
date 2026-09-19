# COS Dev Center (`capivara-central`) — Pup (mínimo)

App de onboarding em português do CapivaraOS **Pup** (Xfce). No primeiro boot,
liga em um clique os extras opcionais da estação de desenvolvimento. Versão
**mínima e leve** — o Pup mantém só os cards essenciais (PROD-122).

- **UI:** GTK4/libadwaita. Versão enxuta do port do Snout (PROD-117) — mesmos
  fluxo e widgets, só os 3 cards essenciais.
- **Backend:** `backend.py` (PyGObject/`Gio.Subprocess`). Orquestra os helpers
  em `libexec/`; a parte que precisa de root é elevada por `pkexec` DENTRO do
  helper (polkit `org.capivaraos.central.*`). O app nunca roda como root.
- **Entrada:** launcher `capivara-central` (usa `/usr/bin/python3`, NÃO o do PATH
  — ver BUG-44) → `capivara-central.py` (Adw.Application).

## Cards (mínimo do Pup)
IA local (Ollama + Alpaca + Continue), Ferramentas de dev (VS Code/Cline/Open
WebUI/Docker CE) e GitHub CLI + pre-commit. Ficam de fora (ao contrário do
Snout): Trilhas de linguagem, Ligar GPU e "Atualizar o CapivaraOS" — no Pup o
aviso de nova versão fica com o notificador próprio leve (PROD-123).

## Build
`./rpm/build-rpm.sh` → `~/rpmbuild/RPMS/noarch/capivara-central-*.pup.rpm`.
O `build-all.sh` da raiz constrói branding + central e monta a ISO.
