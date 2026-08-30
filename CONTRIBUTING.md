# Contribuindo com o CapivaraOS Pup

Obrigado pelo interesse em contribuir! Este repositório contém o kickstart,
os scripts de build e o pacote RPM de branding usados para gerar a ISO do
**CapivaraOS Pup** (Fedora 44 + Xfce).

## Antes de abrir uma issue

- **Bugs e problemas de build**: abra uma [issue](../../issues/new/choose)
  usando o template de relato de bug. Inclua a versão do Fedora usada na
  máquina de build, o comando exato executado e os logs relevantes (veja
  "Logs úteis" no `README.md`).
- **Sugestões de pacote, tema ou funcionalidade**: abra uma issue com o
  template de solicitação de funcionalidade.
- **Dúvidas gerais, "como faço para...", ideias em aberto**: use as
  [Discussions](../../discussions) em vez de issues — issues ficam
  reservadas para itens de trabalho rastreáveis.
- **Vulnerabilidades de segurança**: não abra uma issue pública — siga o
  processo descrito em [`SECURITY.md`](SECURITY.md).

## Como contribuir com código

1. Dê um fork no repositório e crie uma branch a partir de `master`.
2. Siga a estrutura já documentada no `README.md` (kickstart, branding,
   rpm) — mudanças em branding (wallpapers, ícones, tema padrão) entram em
   `branding/` e são empacotadas via `rpm/capivaraos-branding.spec`.
3. Teste sua mudança localmente sempre que possível:
   - Para mudanças no RPM de branding: rode `rpm/build-rpm.sh` e confirme
     que o pacote é gerado sem erros.
   - Para mudanças no kickstart: gere a ISO com `livemedia-creator` (veja
     o `README.md`) e valide em uma VM (`qemu-system-x86_64`), lembrando do
     requisito mínimo de 4GB de RAM da spin.
4. Abra um Pull Request descrevendo a mudança e como foi testada. Use o
   template de PR como guia.
5. Um mantenedor vai revisar e pode pedir ajustes antes do merge.

## Fluxo de trabalho — branch + PR (regra do projeto)

Para **qualidade, rastreabilidade e auditoria**, todo o trabalho — **inclusive dos
mantenedores** — segue o mesmo fluxo. Não se faz `push` direto no branch padrão.

1. **Crie um branch** a partir do branch padrão, com nome descritivo
   (`feat/…`, `fix/…`, `chore/…`, `docs/…`).
2. **Commits pequenos e coesos**, explicando _o quê_ e _porquê_; referencie o
   ticket do Jira quando houver.
3. **Abra um Pull Request.** Deixe o CI verde (quando houver) antes de mesclar.
4. **O branch padrão fica sempre coerente e "releasável".** Um _release_ é uma
   **tag** + a **imagem (ISO) publicada** (SourceForge/site) — nunca "o que
   estiver no branch padrão".
5. **Segurança:** nunca commitar segredos/chaves; o histórico é varrido
   (gitleaks) e a push protection está ativa.

> O branch padrão é protegido: PRs são o único caminho de entrada — vale também
> para os mantenedores. É o que sustenta a auditabilidade do projeto.

## Licença

Ao contribuir, você concorda que sua contribuição será licenciada sob a
[GPLv3](LICENSE), a mesma licença do projeto.

Este projeto segue o [Código de Conduta](CODE_OF_CONDUCT.md) do
CapivaraOS.
