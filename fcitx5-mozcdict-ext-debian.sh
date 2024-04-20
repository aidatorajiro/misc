mkdir build
pushd build
apt-src update
apt-src install fcitx-mozc
git clone https://github.com/reasonset/mozcdict-ext
pushd mozcdict-ext
pushd neologd
export MOZC_ID_FILE=$(echo "$(pwd)"/../../mozc-*/src/data/dictionary_oss/id.def)
zsh mkdict.zsh > ../../out_neologd
popd
pushd sudachi
zsh mkdict.zsh > ../../out_sudachi
popd
popd
ruby mozcdict-ext/.dev.utils/uniqword.rb out_neologd out_sudachi > out_unified
cat out_unified >> mozc-*/src/data/dictionary_oss/dictionary09.txt
apt-src build fcitx-mozc
popd
# dpkg --install build/fcitx-mozc-data_* build/fcitx5-mozc_* build/mozc-data_* build/mozc-server_* build/mozc-utils-gui_*
