#!/usr/bin/env bash
#Petit script pour avoir le code source d'un site qui necessite une connextion
#rd170803.14:58
#source: https://stackoverflow.com/questions/22614331/authenticate-on-wordpress-with-wget


#test si l'argument est vide
if [ -z "$1" ]
  then
    echo -e "\nSyntax: ./aspi.sh proxy port url user passwd new_cookie\n\n"
    exit
fi

proxy=$1
port=$2
site=$3
login_address="$site/wp-login.php"
log=$4
pwd=$5
cookies="cookies.txt"
agent="Mozilla/5.0"
new_cookie=$6

if [ ! -z "$new_cookie" ]
then
    rm -Rf $cookies
fi

# authenticate and save cookies
if [ ! -f "$cookies" ]
then
    wget \
        --user-agent="$agent" \
        --save-cookies $cookies \
        --keep-session-cookies \
        --delete-after \
        --post-data="log=$log&pwd=$pwd&testcookie=1" \
        -q -e http_proxy="http://"$proxy":"$port"/" "$login_address"
fi

# access home page with authenticated cookies
wget \
    --user-agent="$agent" \
    --load-cookies $cookies \
    -qO- -e http_proxy="http://"$proxy":"$port"/" "$site"
