# url_parser
Parcours une table de paires de sites pour repérer les urls communes.

# Utilisation

## Récupération du dépôt
On récupère le dépôt avec:
```
git clone git@github.com:epfl-sdf/url_parser.git
```

## Installation des outils nécessaires
Simplement avec la commande:
```
./install.sh
```

## Lancer le vérificateur
Simplement avec la commande:
```
./parser.py fichier_des_sites addresse_du_proxy port_du_proxy
```

`fichier_des_sites` est le fichier contenant les sites a tester. Il doit aussi contenir les informations de connexion pour acceder aux sites.
