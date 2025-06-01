#!/bin/bash

echo "************ Install packages..."
sudo nala install -y cmake pkg-config libfreetype6-dev libfontconfig1-dev libxcb-xfixes0-dev libxkbcommon-dev python3
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
cargo install alacritty
mkdir $HOME/.config/alacritty
cp alacritty.yml $HOME/.config/alacritty/alacritty.yml

#END
