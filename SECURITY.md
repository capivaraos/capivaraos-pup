# Política de Segurança · Security Policy

## Versões suportadas · Supported versions

O **CapivaraOS Pup** recebe correções de segurança na série estável atual
(**2.x**, base Fedora 45). Mantenha o sistema atualizado com `dnf upgrade`.

A Série 1 (Fedora 44) foi **encerrada em novembro de 2026** e não recebe mais
correções. / Series 1 (Fedora 44) **reached end of support in November 2026** and no
longer receives fixes.

| Versão / Version | Suporte / Support |
|---|---|
| 2.x | ✅ |
| 1.x | ❌ |

---

## Como reportar uma vulnerabilidade (PT)

**Não abra uma issue pública para falhas de segurança.** Use um canal privado:

1. **GitHub — _Report a vulnerability_** (recomendado): na aba **Security** deste
   repositório, clique em *Report a vulnerability* (Private Vulnerability
   Reporting). É privado e estruturado.
2. **Alternativa:** se você não usa GitHub, fale com o projeto pelo
   [formulário de contato](https://capivaraos.org/pt/contato.html) **apenas para
   estabelecer contato** — não inclua os detalhes técnicos da falha ali;
   combinaremos um canal privado para os detalhes.

Ajuda muito incluir: a versão (`cat /etc/os-release`), o componente afetado, passos
para reproduzir, o impacto potencial e, se possível, uma prova de conceito.

**O que esperar:** confirmamos o recebimento assim que possível, avaliamos o impacto
e, se a falha for confirmada, trabalhamos numa correção e combinamos com você um prazo
de **divulgação coordenada**, pelo mesmo canal do relato. Por ser um projeto
comunitário, respondemos em regime de **melhor esforço** — por favor, dê um prazo
razoável antes de divulgar publicamente.

Não há programa de recompensas (bug bounty).

---

## How to report a vulnerability (EN)

**Do not open a public issue for security flaws.** Use a private channel:

1. **GitHub — _Report a vulnerability_** (recommended): in this repository's
   **Security** tab, click *Report a vulnerability* (Private Vulnerability
   Reporting). It is private and structured.
2. **Alternative:** if you don't use GitHub, reach out via our
   [contact form](https://capivaraos.org/en/contact.html) **only to establish
   contact** — do not include the technical details of the flaw there; we'll agree on
   a private channel for the specifics.

Helpful details: the version (`cat /etc/os-release`), the affected component, steps to
reproduce, potential impact and, if possible, a proof of concept.

**What to expect:** we acknowledge reports as soon as possible, assess the impact and,
if confirmed, work on a fix and agree a **coordinated disclosure** date with you,
through the same channel used to report. As a community project, we respond on a
**best-effort** basis — please allow a reasonable time before public disclosure.

There is no bug bounty programme.

---

## Escopo · Scope

**PT —** Cobre o conteúdo deste repositório: os kickstarts, os scripts `%post`,
o pacote RPM `capivaraos-branding`, o app `capivara-central` e os scripts de build (`build-rpm.sh`, `build-all.sh`), além das
ferramentas de publicação do repositório assinado. Vulnerabilidades no Fedora em si,
nas ferramentas upstream (`livemedia-creator`, `anaconda`, `lorax`) ou em dependências
de terceiros devem ser reportadas diretamente aos respectivos projetos.

**EN —** Covers the contents of this repository: the kickstarts, the `%post` scripts,
the `capivaraos-branding` RPM, the `capivara-central` app and the build scripts (`build-rpm.sh`, `build-all.sh`), plus the tooling
that publishes the signed package repository. Vulnerabilities in Fedora itself, in
upstream tools (`livemedia-creator`, `anaconda`, `lorax`) or in third-party
dependencies should be reported directly to those projects.
