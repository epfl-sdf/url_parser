#!/bin/bash
if (( $# < 3 ));
then
    echo "Erreur : pas assez d'arguments 
usage : ./start.sh fichier_des_sites addresse_du_proxy port_du_proxy"
    exit
fi
source venvParser/bin/activate
./parser.py $1 $2 $3 
