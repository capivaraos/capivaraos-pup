# Chave de assinatura do repositório do CapivaraOS (desktop)

Este diretório guarda a **chave pública** que valida os pacotes e o índice do
repositório de atualizações do CapivaraOS desktop (Marsh/Pup/Pup). A **chave
privada NUNCA entra no git** — ela é o ativo mais sensível do projeto.

Chave **própria do desktop**, separada da chave do Herd (servidor): as linhas
comunidade/.org (desktop) e servidor/.com (Herd) têm confiança independente.

## Como funciona a confiança
- Cada RPM é assinado (`gpgcheck=1` no cliente valida a assinatura do pacote).
- O índice do repo (`repomd.xml`) é assinado (`repomd.xml.asc`); `repo_gpgcheck=1`
  no cliente valida a assinatura do índice. Update forjado/adulterado é recusado.
- A pública viaja no pacote `capivaraos-repos` → instalada em
  `/etc/pki/rpm-gpg/RPM-GPG-KEY-capivaraos` e importada no chaveiro do rpm.
- Por isso o **host dos arquivos é irrelevante** para a integridade: object
  storage/CDN público serve sem risco (um host comprometido não consegue assinar).

## Cerimônia (uma vez, OFFLINE)
```bash
./keys/gen-signing-key.sh
```
Gera RSA 4096/SHA-512 num GNUPGHOME temporário (não suja o seu `~/.gnupg`),
exporta a **pública** para `keys/RPM-GPG-KEY-capivaraos` (COMMITAR) e a **privada**
para um arquivo fora do repo. Depois:
1. Guarde a privada em HSM/YubiKey ou no cofre (Bitwarden) com passphrase forte.
2. `shred -u` o arquivo privado da máquina.
3. Publique o **fingerprint** na página de Segurança do site/docs (o usuário confere).
4. Commite **apenas** `keys/RPM-GPG-KEY-capivaraos`.

## Na máquina de publicação (assinar o repo)
Importe a privada só na hora (ou use o agente do YubiKey/HSM) e diga ao rpm qual
chave usar:
```bash
gpg --import /caminho/seguro/privada.asc
cat >> ~/.rpmmacros <<'EOF'
%_gpg_name CapivaraOS (repo signing key)
%_gpg_digest_algo sha512
EOF
```
Depois rode `./publish-repo.sh add|promote|upload`. Ao terminar, remova a privada
da máquina de novo (reimportar só quando for assinar).

## Rotação
Sem expiração na chave-mestra; rotação é decisão de processo. Ao rotacionar,
publique a nova pública num `capivaraos-repos` novo e mantenha a antiga no
chaveiro por um período de transição (pacotes antigos ainda validam).
