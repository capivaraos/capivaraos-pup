# Vendorizado de fedora-kickstarts (fedora-repo-not-rawhide.ks), branch de
# release (não-rawhide). Fonte original:
# https://forge.fedoraproject.org/releng/spin-kickstarts
# (histórico anterior à migração para kiwi, commit d93b2ac)
#
# NOTA CapivaraOS (2026-07-21): divergimos do upstream em duas coisas.
#
# 1) O repo de updates NÃO pode se chamar "updates". Segundo a documentação do
#    livemedia-creator (lorax), o nome "updates" é RESERVADO para uso interno
#    do Anaconda; um "repo --name=updates" no kickstart é ignorado
#    silenciosamente. Foi esse o bug que fez as ISOs 1.1.2/1.1.3 da spin Marsh
#    saírem só com o Fedora 44 GA, levando a ~1068 pacotes / 7,4 GiB de
#    atualização no primeiro boot. Renomeamos para "fedora-updates". Ver
#    BUG-29 — o mesmo defeito estava aqui, apenas nunca chegou a uma ISO
#    pública porque esta spin ainda não foi publicada.
#      https://weldr.io/lorax/livemedia-creator.html
#
# 2) Usamos valores literais (f45/x86_64) nas linhas "repo" em vez de
#    $releasever/$basearch. Isto NÃO era a causa do bug acima (o nome era),
#    mas mantém as linhas inequívocas. Ao mexer aqui, confira que o
#    build-all.sh usa o mesmo releasever (--releasever=45).

repo --name=fedora --mirrorlist=https://mirrors.fedoraproject.org/mirrorlist?repo=fedora-45&arch=x86_64
repo --name=fedora-updates --mirrorlist=https://mirrors.fedoraproject.org/mirrorlist?repo=updates-released-f45&arch=x86_64
#repo --name=fedora-updates-testing --mirrorlist=https://mirrors.fedoraproject.org/mirrorlist?repo=updates-testing-f45&arch=x86_64
url --mirrorlist=https://mirrors.fedoraproject.org/mirrorlist?repo=fedora-$releasever&arch=$basearch
