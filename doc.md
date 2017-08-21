# url_parser
Le but de ce logiciel est de créer un mapping entre les URL Jahia et les url
WordPress. Pour notre travail de test, il serait utile de non seulement avoir
le mapping des URL Jahia et WordPress des pages principales de chaque site
mais aussi de tous les sous pages de chaque site. Ce logiciel est utilisé
pour obtenir ce mapping. En partant du mapping des URL des pages principales
de chaque site, il obtient le mapping de la majorité des URL des sous pages.

# Utilisation
## Récupération du dépôt
On récupère le dépôt avec:
```
git clone git@github.com:epfl-sdf/url_parser.git
```
(cette commande nécessite la présence de `git` sur l'ordinateur)

Pour executer les commandes des sections suivantes, il faut se mettre dans
le dossier du dépôt.

## Installation des outils nécessaires
Simplement avec la commande:
```
./install.sh
```
Pour que cette commande marche, il faut être sous Ubuntu ou une autre
distribution utilisant `apt-get` comme gestionnaire de paquets et qui a les
mêmes noms de packets que sur les dépôts Ubuntu.

De plus, cet outil utilise des utilitaires communs sur les systèmes
Linux mais qui peuvent ne pas être installés sur tous les ordinateurs.
Ces outils sont:
* `wget`
* `curl`

## Lancer le parser
Simplement avec la commande:
```
./parser.py fichier_des_sites
```

`fichier_des_sites` doit être un fichier au format .csv dont les colonnes sont
séparées par des virgules. Les colonnes présentes peuvent varier mais pour que
ce script marche correctement, il faut au moins les colonnes suivantes:
* Première colonne: URL du site Jahia
* Deuxième colonne: URL du site WordPress
* Sixième colonne: le username utilisé pour se connecter sur le site WordPress
* Septième colonne: le mot de passe utilisé pour se connecter sur le site WordPress

Le script va alors écrire dans au moins un fichier: `result-[date].csv` ou `[date]`
est la date et l'heure à laquelle le script est lancé. Ce fichier sera également
un fichier .csv dont les colonnes sont séparées par des virgules. Les colonnes de
ce fichier sont les suivantes:
* l'index de la sous page, elle montre l'ordre avec lequel le script a trouvé les
  liens sur le site.
* le niveau de la page sur le site qui corréspond au niveau de cette page dans la
  hierarche du plan-du-site du site en question.
* l'URL Jahia de la page
* l'URL WordPress de la page

De plus, le script peut créer un autre fichier qui s'apelle `warnings-[date].log`.
Dans ce fichier, on retrouve des problèmes que le script a encontré pendant son
execution. Il y a 3 types de problèmes:
* Si un site n'a pas pu être chargé correctement, il sera signalé içi.
* Si une langue manque sur un site alors qu'elle est présente sur l'autre CMS
* Si dans le même niveau de la hiérarchie des sous-pages il y a deux liens ou plus
  qui ont le même nom. Dans ce cas, le script n'est pas capable de les différencier
  et ne peux pas faire de mapping.

Il est aussi possible de lancer le logiciel avec les options suivantes:
* `-h --help` pour affichier une petite aide sur comment lancer le logiciel
* `-v --version` pour afficher le numéro de version du script

# Expliquation du logiciel

Ce logiciel sert a faire un mapping entre tout les pages Jahia et WordPress.
De base, nous avons une liste qui lie les pages principales des sites Jahia et
WordPress. Le problème qu'on a, c'est que l'on voudrait avoir directement le lien
entre les sous-pages de chaque site. Il y a 600+ sites en tout et chaque site a
beaucoup de sous-pages. Cet outil sers donc a lier ces sous-pages entre les deux
versions.

Pour cela, on utilise les plan-du-site présentes sur les sites afin d'avoir tout
les sous-pages du site. De plus, on charge le site dans toutes les langues possibles
et on fait les liens avec les sous-pages dans les mêmes langues.

Les sites sont chargé directement avec la commande `wget`. On utilise cette commande
directement au lieu d'une librairie car on utlise aussi un script bash `aspi.sh`
qui utilise `wget` également. Ceci est nécessaire car pour acceder aux sites Wordpress,
il faut se connecter. Le script `aspi.sh` se connecte donc sur les sites WordPress
pour obtenir les cookies de la connection.

Pour parcourir le plan-du-site, on va sur la page de celui-ci et on lit la page
en utilisant la librairie BeautifulSoup qui permet d'organiser et de facilement
parcourir le contenu d'une page HTML.

Il existe certaines subtilités liées au fait que les URL qu'on a au départ ne sont
pas toujours les vraies URL de ce qu'on aimerait avoir. Il faut tout d'abord,
regarder si l'URL n'est pas redirigé quelque part. Ensuite on doit se mettre sûr
qu'on compare les plan-du-site des sites dans la même langue. Il faut aussi prendre
la page dans l'autre langue et refaire les comparaison entre les mêmes langues.

Des informations plus spécifiques se trouvent dans la documentation et les commentaires
directement présentes dans le code source.
