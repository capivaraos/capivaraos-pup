# capivaraos-upgrade — upgrade de versão in-place do CapivaraOS (FEAT-115)
#
# Entrega a ferramenta `capivaraos-upgrade`, um invólucro auditável do
# `dnf5 system-upgrade` (transação offline no reboot): pré-voo com FALHA FECHADA
# (recusa se o nosso repo assinado ainda não existir para a versão de destino),
# download e reboot como passos SEPARADOS e explícitos, e snapshot pré-upgrade
# quando o storage suporta (snapper/btrfs — padrão no Marsh 2.x).
#
# É a ENGINE do "atualizar sem formatar" (FEAT-111). Com FEAT-112/113 (repo
# assinado + pacote capivaraos-repos), dá ao CapivaraOS instalado o caminho de
# subir de versão. A UX do botão (COS Dev Center / Discover) é o FEAT-116 e reusa
# esta mesma ferramenta.
#
# O subcomando `system-upgrade` é embutido no core do dnf5 no Fedora 44+ (não há
# pacote de plugin separado) — por isso a dependência é só `dnf5`.

Name:           capivaraos-upgrade
Version:        1.0.0
# Sufixo ".pup": convenção das outras spins (evita colisão de NEVRA em
# ~/rpmbuild compartilhado — BUG-30).
Release:        2%{?dist}.pup
Summary:        Upgrade de versão in-place (dnf5 system-upgrade) do CapivaraOS

License:        GPL-3.0-or-later
URL:            https://capivaraos.org
BuildArch:      noarch

Source0:        capivaraos-upgrade

# O comando system-upgrade é embutido no core do dnf5 (Fedora 44+).
Requires:       dnf5
# Garante que o .repo assinado e a chave GPG estejam presentes: sem eles o
# pré-voo não tem como confirmar o repositório do CapivaraOS na versão de destino.
Requires:       capivaraos-repos

Provides:       system-version-upgrade = %{version}-%{release}

%description
Ferramenta `capivaraos-upgrade`: sobe o CapivaraOS para a próxima versão SEM
formatar, usando a transação offline do dnf5 (`dnf5 system-upgrade`). Segue a
marca de auditabilidade: por padrão só faz verificação (pré-voo); baixar e
reiniciar são passos explícitos e separados; o pré-voo FALHA FECHADA se o
repositório assinado do CapivaraOS ainda não existir para a versão de destino
(para não deixar os pacotes próprios para trás); e cria snapshot antes do
upgrade quando o storage é compatível (snapper/btrfs). A confiança vem da
assinatura GPG do repositório (gpgcheck + repo_gpgcheck): a transação recusa
pacote ou metadado não assinado pela nossa chave.

%install
install -D -m 0755 %{SOURCE0} %{buildroot}%{_bindir}/capivaraos-upgrade

%files
%{_bindir}/capivaraos-upgrade

%changelog
* Wed Sep 30 2026 CapivaraOS <capivaraos-bot@users.noreply.github.com> - 1.0.0-2.pup
- Sub-versão de validação da UX de atualização (FEAT-143): sem mudança funcional.
  Usada para confirmar, numa VM real, que os nossos updates aparecem no updater
  padrão do Fedora Xfce (dnfdragora / dnfdragora-updater), via dnf/PackageKit.

* Fri Sep 18 2026 CapivaraOS <capivaraos-bot@users.noreply.github.com> - 1.0.0-1.pup
- Port da engine de upgrade in-place para o Pup 2.x (PROD-116): a ferramenta
  `capivaraos-upgrade` é idêntica à do Marsh (FEAT-111/115) — usa nomes genéricos
  (repo `capivaraos`, pacote `capivaraos-branding`), então só muda o Release para
  .pup. Invólucro auditável do dnf5 system-upgrade (download + reboot offline).
  Pré-voo com falha fechada quando o repo assinado do CapivaraOS não existe na
  versão de destino; destino derivado de `rpm -E %%fedora` (atual+1) ou --to N;
  snapshot pré-upgrade via snapper quando disponível (LVM é reportado). Requires
  dnf5 + capivaraos-repos. No Pup a UX do botão fica com um notificador próprio
  leve (PROD-123), integrando com o COS Dev mínimo (PROD-122); o card = FEAT-116.
