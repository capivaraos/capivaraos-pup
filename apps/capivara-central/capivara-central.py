#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# COS Dev Center MÍNIMO — app de onboarding pt-BR do CapivaraOS Pup (Xfce).
#
# UI em GTK4/libadwaita; a lógica de instalação fica no backend.py
# (PyGObject/Gio.Subprocess). Versão enxuta do port do Snout (PROD-122): só os
# 3 cards essenciais — IA local, Ferramentas de dev e GitHub CLI. Sem trilhas de
# linguagem, sem GPU e sem card de upgrade (o "nova versão" no Pup fica com o
# notificador próprio leve, PROD-123).

import os
import sys

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk, GLib  # noqa: E402

# backend.py fica ao lado (em /usr/share/capivara-central pelo RPM, ou no dev).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backend import Backend  # noqa: E402

APP_ID = "org.capivaraos.Central"


class Card:
    """Um card do catálogo = Adw.ActionRow com ícone, descrição, botão de ação e
    (opcional) botão 'Abrir'/status. Dois modos: 'toggle' (vira 'Instalado ✓') e
    'seleção' (mostra 'Instalado: X' e mantém o botão para escolher mais)."""

    def __init__(self, heading, description, icon, action_text, on_activate,
                 open_text=None, on_open=None):
        self.action_text = action_text
        self._done = False
        self.row = Adw.ActionRow(title=heading, subtitle=description)
        self.row.set_subtitle_lines(0)  # deixa a descrição quebrar por completo
        img = Gtk.Image.new_from_icon_name(icon)
        img.add_css_class("dim-label")
        self.row.add_prefix(img)

        self.status = Gtk.Label(visible=False, wrap=True, xalign=1.0)
        self.status.add_css_class("dim-label")
        self.status.add_css_class("caption")

        self.open_btn = None
        if open_text:
            self.open_btn = Gtk.Button(label=open_text, valign=Gtk.Align.CENTER,
                                       visible=False)
            self.open_btn.connect("clicked", lambda *_: on_open())

        self.btn = Gtk.Button(label=action_text, valign=Gtk.Align.CENTER)
        self.btn.add_css_class("suggested-action")
        self.btn.connect("clicked", lambda *_: on_activate())

        self.row.add_suffix(self.status)
        if self.open_btn:
            self.row.add_suffix(self.open_btn)
        self.row.add_suffix(self.btn)

    def set_done(self, done: bool):
        """Modo toggle: instalado → botão 'Instalado ✓' desativado."""
        self._done = done
        if done:
            self.btn.set_label("Instalado ✓")
            self.btn.remove_css_class("suggested-action")
        else:
            self.btn.set_label(self.action_text)
            self.btn.add_css_class("suggested-action")
        if self.open_btn:
            self.open_btn.set_visible(done)

    def set_status(self, text: str):
        """Modo seleção: mostra o que já está instalado, sem travar o botão."""
        if text:
            self.status.set_text("Instalado: " + text)
            self.status.set_visible(True)
        else:
            self.status.set_visible(False)

    def apply_busy(self, busy: bool):
        self.btn.set_sensitive(not busy and not self._done)
        if self.open_btn:
            self.open_btn.set_sensitive(not busy)


class MainWindow(Adw.ApplicationWindow):
    def __init__(self, app, backend):
        super().__init__(application=app, title="COS Dev Center")
        self.set_default_size(760, 640)
        self.set_size_request(420, 480)
        self.backend = backend
        self._progress = None  # Adw.Dialog do log (criado sob demanda)

        self.nav = Adw.NavigationView()
        self.set_content(self.nav)
        self.nav.push(self._welcome_page())

        backend.connect("log-line", self._on_log_line)
        backend.connect("step-changed", self._on_step)
        backend.connect("finished", self._on_finished)
        backend.connect("busy-changed", self._on_busy)

    # ---- Página de boas-vindas -------------------------------------------
    def _welcome_page(self):
        status = Adw.StatusPage(
            icon_name=APP_ID,
            title="Sua estação de dev pronta em minutos",
            description=("O básico já vem instalado. O Dev Center liga os extras "
                         "opcionais — IA local, ferramentas de dev e GitHub — em "
                         "um clique, sem terminal."),
        )
        btn = Gtk.Button(label="Começar", halign=Gtk.Align.CENTER)
        btn.add_css_class("suggested-action")
        btn.add_css_class("pill")
        btn.connect("clicked", lambda *_: self.nav.push(self._catalog_page()))
        status.set_child(btn)

        tv = Adw.ToolbarView()
        tv.add_top_bar(Adw.HeaderBar())
        tv.set_content(status)
        return Adw.NavigationPage(title="Bem-vindo ao CapivaraOS Pup", child=tv)

    # ---- Catálogo --------------------------------------------------------
    def _catalog_page(self):
        page = Adw.PreferencesPage()

        # Grupo: "Instalados" (mini-lançador; escondido se vazio).
        self.grp_installed = Adw.PreferencesGroup(title="Instalados", visible=False)
        self._installed_rows = []
        page.add(self.grp_installed)

        # Grupo: extras (com o aviso de senha como descrição do grupo).
        grp = Adw.PreferencesGroup(
            title="Extras para sua estação",
            description=("Escolha o que instalar. Pediremos sua senha de "
                         "administrador quando for necessário."))

        self.card_ai = Card(
            "IA local",
            ("Rode modelos de IA na sua máquina, sem nuvem: Ollama (motor), "
             "Alpaca (interface) e a extensão Continue no VSCodium. No Fedora 45 "
             "o Ollama inclui a pilha AMD/ROCm (~6 GB); instale no sistema em "
             "disco, não na sessão live."),
            "system-run-symbolic", "Instalar IA local",
            self._install_ai, open_text="Abrir o Alpaca",
            on_open=self.backend.open_ai_local)
        grp.add(self.card_ai.row)

        self.card_tools = Card(
            "Ferramentas de dev",
            ("Complete seu arsenal: VS Code, extensão Cline (IA agentic no "
             "editor), Open WebUI (chat web do Ollama) e Docker CE."),
            "applications-engineering-symbolic", "Escolher ferramentas",
            self._open_tools)
        grp.add(self.card_tools.row)

        self.card_gh = Card(
            "GitHub CLI + pre-commit",
            ("Configure o gh (GitHub pelo terminal) e um template de pre-commit "
             "com verificações de segurança (gitleaks, chaves, ShellCheck)."),
            "software-install-symbolic", "Configurar", self._setup_gh,
            open_text="Entrar no GitHub", on_open=self.backend.open_gh_login)
        grp.add(self.card_gh.row)

        page.add(grp)

        tv = Adw.ToolbarView()
        tv.add_top_bar(Adw.HeaderBar())
        tv.set_content(page)

        # Monta o estado inicial dos cards.
        self.refresh_state()
        return Adw.NavigationPage(title="Extras para sua estação", child=tv)

    # ---- Estado dos cards ------------------------------------------------
    def refresh_state(self):
        b = self.backend
        self.card_ai.set_done(b.is_ai_local_installed())
        self.card_gh.set_done(b.is_gh_ready())
        self.card_tools.set_status(b.installed_dev_tools())
        self._rebuild_installed(b.installed_apps())
        self._on_busy(None, b.busy)

    def _rebuild_installed(self, apps):
        for row in self._installed_rows:
            self.grp_installed.remove(row)
        self._installed_rows = []
        for app in apps:
            row = Adw.ActionRow(title=app["name"])
            row.add_prefix(Gtk.Image.new_from_icon_name(app["icon"]))
            if app["launch"]:
                btn = Gtk.Button(label="Abrir", valign=Gtk.Align.CENTER)
                kind = app["kind"]
                btn.connect("clicked", lambda *_a, k=kind: self.backend.open_app(k))
                row.add_suffix(btn)
            else:
                lbl = Gtk.Label(label="instalado")
                lbl.add_css_class("dim-label")
                row.add_suffix(lbl)
            self.grp_installed.add(row)
            self._installed_rows.append(row)
        self.grp_installed.set_visible(bool(apps))

    def _on_busy(self, _backend, busy):
        for card in (self.card_ai, self.card_tools, self.card_gh):
            card.apply_busy(busy)

    # ---- Ações dos cards -------------------------------------------------
    def _start(self, title, fn):
        """Abre a folha de progresso, limpa o log e dispara a ação."""
        self._open_progress(title)
        fn()

    def _blocked_by_live(self) -> bool:
        """Numa sessão live não há espaço p/ instalar as ferramentas — avisa e
        bloqueia ANTES de baixar (evita falhar no meio com 'disk full'). Retorna
        True se bloqueou."""
        if not self.backend.is_live_session():
            return False
        dialog = Adw.AlertDialog(
            heading="Você está na sessão de demonstração",
            body=("Esta é a sessão live do CapivaraOS — ela roda da memória e tem "
                  "pouco espaço, então baixar estas ferramentas (IA local, Docker, "
                  "Open WebUI…) falharia no meio.\n\nInstale o CapivaraOS no disco "
                  "(ícone “Instalar CapivaraOS” na área de trabalho) e abra o COS "
                  "Dev no sistema instalado para adicioná-las."))
        dialog.add_response("ok", "Entendi")
        dialog.set_default_response("ok")
        dialog.present(self)
        return True

    def _install_ai(self):
        if self._blocked_by_live():
            return
        self._start("Instalando IA local", self.backend.install_ai_local)

    def _setup_gh(self):
        if self._blocked_by_live():
            return
        self._start("Configurando gh + pre-commit", self.backend.setup_gh)

    def _open_tools(self):
        if self._blocked_by_live():
            return
        self._selection_dialog(
            "Ferramentas de dev",
            ("Escolha o que instalar. VS Code e Docker CE são de sistema (pedem "
             "senha); Cline e Open WebUI ficam no seu usuário."),
            [("vscode", "VS Code (editor da Microsoft)"),
             ("cline", "Cline — IA agentic no editor (code/codium)"),
             ("openwebui", "Open WebUI — chat web do Ollama (podman)"),
             ("docker", "Docker CE — containers")],
            "Instalando ferramentas de dev", self.backend.install_dev_tools,
            installed=self.backend.installed_dev_tool_keys())

    # ---- Diálogo de seleção múltipla (ferramentas) -----------------------
    def _selection_dialog(self, title, subtitle, items, progress_title, run,
                          installed=None):
        dialog = Adw.Dialog(title=title)
        dialog.set_content_width(460)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12,
                      margin_top=12, margin_bottom=12,
                      margin_start=12, margin_end=12)
        lbl = Gtk.Label(label=subtitle, wrap=True, xalign=0.0)
        box.append(lbl)

        installed = installed or set()
        checks = {}
        group = Adw.PreferencesGroup()
        for key, label in items:
            row = Adw.ActionRow(title=label)
            chk = Gtk.CheckButton(valign=Gtk.Align.CENTER)
            row.add_prefix(chk)
            if key in installed:
                # Já instalado: pré-marcado e travado (não reinstala).
                chk.set_active(True)
                chk.set_sensitive(False)
                row.set_subtitle("já instalado")
            else:
                row.set_activatable_widget(chk)
            checks[key] = chk
            group.add(row)
        box.append(group)

        install = Gtk.Button(label="Instalar selecionadas", halign=Gtk.Align.END)
        install.add_css_class("suggested-action")
        install.set_sensitive(False)

        # Só contam/instalam os itens NOVOS (não os já instalados).
        def on_toggle(*_a):
            install.set_sensitive(
                any(c.get_active() for k, c in checks.items() if k not in installed))
        for k, c in checks.items():
            if k not in installed:
                c.connect("toggled", on_toggle)

        def on_install(*_a):
            picks = [k for k, c in checks.items()
                     if c.get_active() and k not in installed]
            dialog.close()
            self._open_progress(progress_title)
            run(picks)
        install.connect("clicked", on_install)
        box.append(install)

        tv = Adw.ToolbarView()
        tv.add_top_bar(Adw.HeaderBar())
        tv.set_content(box)
        dialog.set_child(tv)
        dialog.present(self)

    # ---- Folha de progresso (log ao vivo) --------------------------------
    def _open_progress(self, title):
        if self._progress is None:
            self._build_progress()
        self.progress_dialog.set_title(title)
        self.step_label.set_text("Preparando…")
        self.log_buffer.set_text("")
        self.spinner.start()
        self.close_btn.set_label("Instalando…")
        self.close_btn.set_sensitive(False)
        self.progress_dialog.present(self)

    def _build_progress(self):
        self.progress_dialog = Adw.Dialog(title="Progresso")
        self.progress_dialog.set_content_width(640)
        self.progress_dialog.set_content_height(520)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12,
                      margin_top=12, margin_bottom=12,
                      margin_start=12, margin_end=12)

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.spinner = Gtk.Spinner()
        self.step_label = Gtk.Label(label="Preparando…", xalign=0.0, wrap=True)
        self.step_label.add_css_class("title-4")
        header.append(self.spinner)
        header.append(self.step_label)
        box.append(header)

        scroller = Gtk.ScrolledWindow(vexpand=True)
        scroller.add_css_class("card")
        self.log_view = Gtk.TextView(editable=False, monospace=True,
                                     cursor_visible=False)
        self.log_view.set_wrap_mode(Gtk.WrapMode.NONE)
        self.log_buffer = self.log_view.get_buffer()
        scroller.set_child(self.log_view)
        box.append(scroller)

        self.close_btn = Gtk.Button(label="Fechar", halign=Gtk.Align.END)
        self.close_btn.connect("clicked", lambda *_: self.progress_dialog.close())
        box.append(self.close_btn)

        tv = Adw.ToolbarView()
        tv.add_top_bar(Adw.HeaderBar())
        tv.set_content(box)
        self.progress_dialog.set_child(tv)
        self._progress = self.progress_dialog

    # ---- Sinais do backend -----------------------------------------------
    def _on_log_line(self, _backend, line):
        end = self.log_buffer.get_end_iter()
        self.log_buffer.insert(end, line + "\n")
        # Rola para o fim.
        mark = self.log_buffer.create_mark(None, self.log_buffer.get_end_iter(),
                                           False)
        self.log_view.scroll_mark_onscreen(mark)

    def _on_step(self, _backend, step):
        if hasattr(self, "step_label"):
            self.step_label.set_text(step)

    def _on_finished(self, _backend, ok, message):
        if hasattr(self, "log_buffer"):
            end = self.log_buffer.get_end_iter()
            self.log_buffer.insert(end, "\n" + message + "\n")
        if hasattr(self, "spinner"):
            self.spinner.stop()
        if hasattr(self, "close_btn"):
            self.close_btn.set_label("Fechar")
            self.close_btn.set_sensitive(True)
        # Reavalia o estado mesmo em falha parcial.
        self.refresh_state()


class CentralApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id=APP_ID)
        self.backend = Backend()

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = MainWindow(self, self.backend)
        win.present()


def main() -> int:
    # O launcher bash já removeu --autostart; filtra por segurança (dev direto).
    argv = [a for a in sys.argv if a != "--autostart"]
    app = CentralApp()
    return app.run(argv)


if __name__ == "__main__":
    raise SystemExit(main())
