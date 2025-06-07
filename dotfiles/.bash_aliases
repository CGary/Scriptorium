#!/usr/bin/env bash

# DOCKER
alias deit='docker exec -it'
alias de='docker exec'
alias dl='docker logs --tail 10000 -f'
alias dr='docker restart'
alias ds='docker stop'
alias dcud='docker compose up -d'
alias dcd='docker compose down'
alias dcs='docker compose stop'
alias dcr='docker compose restart'
alias dcp='docker pause $(docker compose ps -q)'
alias dcu='docker unpause $(docker compose ps -q)'

# APT_GET
alias agd='_ apt-get update'
alias agg='_ apt-get upgrade -y'

# SYSTEM
alias rb='_ reboot'
alias sus='systemctl suspend'
alias locksus='i3lock -c 000000 && systemctl suspend'
alias lock='i3lock --blur 0 --ring-width 7.0 --inside-color=00000000 --ring-color=ffffffff --insidever-color=00000000 --ringver-color=ffffffff --insidewrong-color=00000000 --ringwrong-color=ffffffff --line-color=00000000 --keyhl-color=ffffffff --bshl-color=ffffffff --separator-color=00000000 --verif-color=ffffffff --wrong-color=ffffffff --modif-color=ffffffff'
alias bat='batcat'
alias ll='exa -lhG'
alias la='exa -lhGa'
alias clr='clear'
alias cl='clear && cd'
alias clip='xclip -sel c'
alias compress='tar czvf'
alias decompress='tar xzvf'

cursor() {
  /opt/cursor.appimage "$@" </dev/null &>/dev/null &!
}

#END
