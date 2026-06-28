#!/bin/zsh
# Roda no Mac as 10h: baixa os leads novos do GitHub e abre o painel no navegador.
cd "/Users/stefanoraphael/prospeccao-instagram" || exit 1
/usr/bin/git pull --quiet 2>/dev/null
/usr/bin/open "docs/index.html"
