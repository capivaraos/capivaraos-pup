# capivaraos-repos — configuração do repositório de updates do CapivaraOS (desktop)
#
# Entrega, ao sistema INSTALADO, o apontamento para o repositório de atualizações
# assinado do CapivaraOS desktop + a chave GPG pública que valida pacotes e
# metadados (FEAT-113). É o pacote que dá ao sistema instalado um caminho de
# update de primeira classe: sem ele, um CapivaraOS instalado recebe updates do
# Fedora mas NUNCA os nossos (os RPMs próprios só existiam offline dentro da ISO).
#
# Só arquivos de config + chave (sem scriptlets que toquem arquivos de
# terceiros). O %post apenas importa a chave pública no chaveiro do rpm, para o
# gpgcheck funcionar de imediato, sem o prompt de "importar chave?".
#
# GUARDRAIL DE PUBLICAÇÃO: NÃO embarcar este pacote no %packages da ISO antes de
# repo.capivaraos.org/pup/ estar NO AR — senão todo `dnf` no sistema instalado
# (e na sessão live) avisa "repo inacessível". Ver docs/repo/README.md.

Name:           capivaraos-repos
Version:        1.0.0
# Sufixo ".pup": mesma convenção do capivaraos-branding — evita colisão de
# NEVRA no ~/rpmbuild compartilhado entre as spins (ver BUG-30). Também casa com
# o caminho por spin (pup/) do repositório.
Release:        1%{?dist}.pup
Summary:        Repositório de atualizações assinado do CapivaraOS (desktop, Community)

# Só config nossa (.repo) + a nossa chave pública. GPLv3 cobre a config; a chave
# é material criptográfico do projeto (sem licença de software).
License:        GPL-3.0-or-later
URL:            https://capivaraos.org
BuildArch:      noarch

# Arquivos soltos (não um tarball): o .repo e a chave pública são copiados para
# ~/rpmbuild/SOURCES pelo build-rpm-repos.sh.
Source0:        capivaraos.repo
Source1:        RPM-GPG-KEY-capivaraos

# Nome canônico "*-release" que outros pacotes/documentação podem exigir.
Provides:       capivaraos-release = %{version}-%{release}

%description
Configuração do repositório de atualizações assinado do CapivaraOS desktop
(Community): instala /etc/yum.repos.d/capivaraos.repo (canais stable e testing)
e a chave GPG pública em /etc/pki/rpm-gpg/, importando-a no chaveiro do rpm. A
partir daí um CapivaraOS instalado recebe automaticamente os pacotes próprios do
projeto (capivaraos-branding, COS Dev Center, temas e correções de segurança),
com verificação de assinatura de pacote e de metadados (gpgcheck + repo_gpgcheck).
A chave privada de assinatura permanece offline; só a pública é distribuída aqui.

# Sem %prep/%build: os sources são arquivos soltos, não há o que extrair/compilar.

%install
install -D -m 0644 %{SOURCE0} \
    %{buildroot}%{_sysconfdir}/yum.repos.d/capivaraos.repo
install -D -m 0644 %{SOURCE1} \
    %{buildroot}%{_sysconfdir}/pki/rpm-gpg/RPM-GPG-KEY-capivaraos

%post
# Importa a chave pública no chaveiro do rpm para o gpgcheck funcionar sem o
# prompt interativo "importar esta chave GPG?" no primeiro update. Idempotente
# (reimportar a mesma chave é no-op). Funciona OFFLINE (a chave está no disco),
# então roda bem também no %post do install via ISO.
if [ -x /usr/bin/rpmkeys ]; then
    rpmkeys --import %{_sysconfdir}/pki/rpm-gpg/RPM-GPG-KEY-capivaraos \
        >/dev/null 2>&1 || true
fi

%files
%config(noreplace) %{_sysconfdir}/yum.repos.d/capivaraos.repo
%{_sysconfdir}/pki/rpm-gpg/RPM-GPG-KEY-capivaraos

%changelog
* Fri Sep 18 2026 CapivaraOS <capivaraos-bot@users.noreply.github.com> - 1.0.0-1.pup
- Port do pacote de configuração de repositório para o Pup 2.x (PROD-116):
  mesma base do Marsh (FEAT-111/113), só o caminho por spin muda para pup/
  (baseurl pup/f$releasever/) e o Release para .pup. Instala o
  capivaraos.repo (canais stable + testing, gpgcheck + repo_gpgcheck) e a MESMA
  chave GPG pública do desktop em /etc/pki/rpm-gpg/, importada no chaveiro do rpm
  no %post. baseurl usa $releasever (base Fedora, via system-release(releasever))
  → acompanha sozinho o system-upgrade F45->F46. ATENÇÃO: não embarcar numa ISO
  antes de repo.capivaraos.org/pup/ estar no ar. Ver docs/repo/README.md.
