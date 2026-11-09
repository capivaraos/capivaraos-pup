# capivaraos-wallpapers (pup) — wallpapers da marca, empacotados à parte.
#
# POR QUE ESTE PACOTE EXISTE (ver PROD-187 / PROD-188 no Jira)
# ============================================================
# Ate a 2.0.0 os wallpapers moravam dentro do capivaraos-branding e respondiam
# pela maior parte do peso dele. Como o RPM e republicado inteiro a cada
# mudanca, qualquer correcao de tema obrigava o usuario a rebaixar tudo de novo.
#
# Separando, o branding fica pequeno e os wallpapers sao publicados uma vez so.
# Para isso funcionar, a Version deste pacote e INDEPENDENTE da do branding:
#
#   /!\  NAO acompanhe a Version do capivaraos-branding aqui.
#        Se as duas subirem juntas, o usuario rebaixa as imagens de novo e todo
#        o ganho evapora. So suba a Version DESTE pacote quando uma imagem mudar
#        de verdade. Um subpacote (%%package) do branding NAO serviria: subpacote
#        herda Version-Release do principal, que e justamente o que evitamos.
#
# O capivaraos-branding declara "Requires: capivaraos-wallpapers >= 2.0.0" e
# aponta o wallpaper padrao (DEFAULT_WP) para um caminho servido por aqui. Os
# dois caminham juntos na mesma transacao do dnf.

Name:           capivaraos-wallpapers
Version:        2.0.0
# Release independente do branding. Ver o aviso acima antes de mexer.
Release:        1%{?dist}.pup
Summary:        Wallpapers da marca CapivaraOS Pup

License:        LicenseRef-CapivaraOS-Trademark
URL:            https://capivaraos.org
BuildArch:      noarch

Source0:        %{name}-%{version}.tar.gz

%description
Wallpapers exclusivos da marca CapivaraOS. Vive separado do capivaraos-branding
para que correcoes de tema nao obriguem cada usuario a rebaixar dezenas de
megabytes de imagem que nao mudaram.

%prep
%setup -q

%build
# Nada a construir: as imagens sao instaladas como estao, sem reprocessamento.

%install
set -e
install -d %{buildroot}%{_datadir}/backgrounds/capivaraos
# CapivaraOS_Logo.png e pulado de proposito: apesar de morar nesta pasta, nao e
# papel de parede -- e a arte-mestre da qual os wallpapers sao derivados. Quando
# era instalada, aparecia no seletor como opcao e saia gigante e cortada.
# Continua indo no capivaraos-branding como FONTE de pixmaps/plymouth.
for WP in backgrounds/*.png; do
    [ "$(basename "$WP")" = "CapivaraOS_Logo.png" ] && continue
    install -m 0644 "$WP" %{buildroot}%{_datadir}/backgrounds/capivaraos/
done

%files
%{_datadir}/backgrounds/capivaraos/

%changelog
* Mon Nov 09 2026 CapivaraOS <contato@capivaraos.org> - 2.0.0-1.pup
- Pacote novo: wallpapers da marca, antes entregues pelo capivaraos-branding
  (PROD-187). Mesmos wallpapers, mesmos caminhos, imagens inalteradas.
