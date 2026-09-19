# CapivaraOS Pup — Fedora 44 (Xfce)

Spin leve do **CapivaraOS**, baseada no ambiente **Xfce** oficial do
Fedora, pensada para computadores com **ao menos 4GB de RAM**. Usa as
mesmas ferramentas oficiais do projeto Fedora que a spin KDE do
CapivaraOS Marsh (`../capivaraos-marsh-fedora/`, usada aqui como
referência de estrutura): `kickstart` + `livemedia-creator` (lorax) para a
imagem, e **Anaconda** como instalador.

## Estrutura do projeto

```
capivaraos-pup/
├── PACKAGES.md                  # Seleção de pacotes (grupos comps do Xfce, exclusões)
├── README.md                    # Este arquivo
├── build-all.sh                 # Automatiza todos os passos abaixo
├── branding/                    # Assets de identidade visual (fonte para o RPM)
│   ├── backgrounds/              # Wallpapers da marca 2.x (moonlight/sunset/dev/comics/abstract)
│   ├── icons/                    # Logos do CapivaraOS (compartilhados com a Marsh)
│   └── skel/.config/             # Wallpaper padrão do Xfce (xfconf)
├── kickstart/
│   ├── capivaraos-pup.ks         # Kickstart principal (ponto de entrada)
│   ├── capivaraos-post-branding.ks  # %post: idioma/atalho de instalação
│   ├── ks-flatten.py             # Achata os %include num único arquivo
│   └── upstream/                 # Kickstarts base do Fedora Live (vendorizados/escritos)
│       ├── fedora-repo.ks
│       ├── fedora-live-base.ks
│       ├── fedora-xfce-common.ks
│       └── fedora-live-xfce-base.ks
└── rpm/
    ├── capivaraos-branding.spec  # Pacote RPM com toda a identidade visual
    └── build-rpm.sh               # Script auxiliar para gerar o RPM
```

## Visão geral da identidade visual

Todo o branding estático (wallpapers, ícones "Sobre o Sistema", tema de
boot Plymouth, fundo da tela de login LightDM, `/etc/os-release`,
`/etc/issue`, avatar padrão, wallpaper padrão do Xfce) é empacotado num
único RPM, **`capivaraos-branding`** (ver `rpm/capivaraos-branding.spec`),
que substitui o wallpaper padrão (`desktop-backgrounds-compat`) do Fedora
Xfce.

Diferente da spin KDE (CapivaraOS Marsh, que aplica o tema WhiteSur/macOS
de terceiros), o Pup **mantém o tema Greybird/Xfwm4 padrão do Fedora
Xfce** — decisão deliberada para manter a spin leve, rápida de buildar e
sem dependência de `git clone` de temas externos durante o build. A
personalização do Pup foca em: wallpapers, tela de boot, tela de login,
ícones e identificação do sistema (`os-release`).

### Wallpapers

- **8 wallpapers da marca do CapivaraOS 2.x**, os mesmos das spins Marsh e
  Snout — mesma identidade visual em todas as spins: *moonlight* (Luar,
  padrão), *sunset*, *dev*, *comics* e quatro *abstract*. Instalados em
  `/usr/share/backgrounds/capivaraos/` e visíveis diretamente no seletor de
  papel de parede do `xfdesktop`. O padrão é o **Luar** (moonlight), aplicado
  ao desktop e à tela de login LightDM (via `skel`/`%posttrans`).
- Os wallpapers "padrão" adicionais continuam vindo do pacote
  `xfce-backgrounds` da base.

> A série 1.x usava um conjunto próprio (planos sólidos com a logo + fotos de
> capivaras do Wikimedia Commons sob CC BY-SA). A partir da série 2.x esse
> conjunto foi **removido** em favor dos wallpapers da marca compartilhados
> entre as três spins.

## Pré-requisitos (máquina de build, Fedora 44 x86_64)

```bash
sudo dnf install -y lorax rpm-build ImageMagick git createrepo_c
```

- `lorax` fornece o `livemedia-creator`.
- `rpm-build` + `ImageMagick` são necessários para gerar o RPM
  `capivaraos-branding`.
- `createrepo_c` é usado para o repositório local do RPM.
- O build precisa de acesso à rede (pacotes do Fedora).
- `livemedia-creator --no-virt` precisa rodar como root (usa
  `dnf --installroot` e monta `/dev`, `/proc` etc. no diretório de
  instalação).

## Build rápido

```bash
./build-all.sh
```

Isso gera o RPM de branding, monta o repositório local em
`/var/tmp/capivaraos-pup-repo` e constrói a ISO com `livemedia-creator`,
deixando o resultado em `/var/tmp/capivaraos-pup-result/`.

## Build passo a passo

### Passo 1 — Construir o RPM `capivaraos-branding`

```bash
cd rpm
./build-rpm.sh
```

Gera `~/rpmbuild/RPMS/noarch/capivaraos-branding-1.1.8-1.*.noarch.rpm`.

### Passo 2 — Disponibilizar o RPM como repositório local

```bash
mkdir -p /var/tmp/capivaraos-pup-repo
cp ~/rpmbuild/RPMS/noarch/capivaraos-branding-*.rpm /var/tmp/capivaraos-pup-repo/
createrepo_c /var/tmp/capivaraos-pup-repo
```

(`kickstart/capivaraos-pup.ks` já referencia esse caminho via
`repo --name=capivaraos-local --baseurl=file:///var/tmp/capivaraos-pup-repo`.)

### Passo 3 — Gerar a ISO com `livemedia-creator`

```bash
cd kickstart
python3 ks-flatten.py capivaraos-pup.ks > /var/tmp/capivaraos-pup-flat.ks

sudo livemedia-creator --ks=/var/tmp/capivaraos-pup-flat.ks \
    --no-virt --resultdir=/var/tmp/capivaraos-pup-result \
    --project="CapivaraOS Pup" --make-iso --iso-only \
    --iso-name=CapivaraOS-Pup-1.1.8-x86_64.iso \
    --volid="CapivaraOS Pup 1.1.8" --variant="CapivaraOS Pup" \
    --releasever=44
```

A ISO final fica em
`/var/tmp/capivaraos-pup-result/CapivaraOS-Pup-1.1.8-x86_64.iso`.

## Testando a ISO

```bash
qemu-system-x86_64 -m 4096 -enable-kvm \
    -cdrom /var/tmp/capivaraos-pup-result/CapivaraOS-Pup-1.1.8-x86_64.iso
```

(`-m 4096` simula o requisito mínimo de 4GB RAM da spin.)

## Limitações conhecidas

- **RPM Fusion não está habilitado** (mesma postura do CapivaraOS Marsh):
  o VLC incluso roda com suporte de codecs reduzido.
- **Tema padrão do Xfce (Greybird)**: ao contrário da Marsh, o Pup não
  replica o layout/tema macOS-WhiteSur — ver `PACKAGES.md` e a seção
  "Visão geral da identidade visual" para o racional.

## Ver também

- `../capivaraos-marsh-fedora/` — spin KDE Plasma do CapivaraOS (tema
  WhiteSur/macOS), referência de estrutura usada para este projeto.
- `PACKAGES.md` — racional completo da seleção de pacotes desta spin.

## Comunidade

- Encontrou um bug ou tem uma sugestão? Abra uma [issue](../../issues/new/choose).
- Dúvidas gerais ou ideias em aberto? Use as [Discussions](../../discussions).
- Vulnerabilidade de segurança? Veja [`SECURITY.md`](SECURITY.md) — não abra issue pública.
- Quer contribuir com código? Veja [`CONTRIBUTING.md`](CONTRIBUTING.md).
- Este projeto segue o [Código de Conduta](CODE_OF_CONDUCT.md) do CapivaraOS.
- Licenciado sob [GPLv3](LICENSE).
