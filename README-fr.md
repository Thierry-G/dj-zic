# Dj.zic
[![English](https://img.shields.io/badge/Langue-Français-blue)](README.md)

<p align="center">
  <img src="Doc/logo-120.svg" alt="dj.Zic" width="120"/>
</p>

## Qu'est-ce que c'est ?
**DJ.Zic** est un système DIY portable de diffusion audio en direct en plein air alimenté par un Raspberry Pi sans écran (modèles 3 à 5 - 4Go).
Créé à l'origine pour une performance de protestation silencieuse festive en direct. Il peut être utilisé pour de petites à grandes fêtes en plein air (en mode relais) et aussi en cortège pour des protestations silencieuses/bruyantes, performances, événements festifs...

Il nécessite au minimum une carte son USB/jack et une alimentation. Dj.zic diffuse l'audio via un portail wifi-captif vers les propriétaires de smartphones qui peuvent utiliser leurs écouteurs/enceintes n'importe où.
De plus, le flux en direct est également diffusé sur le connecteur audio du Raspberry Pi (Modèles 3 et 4), et avec un connecteur USB/Jack pour le Raspberry Pi 5.

## Caractéristiques principales
- **Plug and play** sur n'importe quel appareil audio Jack.
  
- **Pas d'Internet requis :** Utilise un portail Wi-Fi captif pour la diffusion.
  **Aucuns frais de données** ni abonnement de données requis.

- **Informations de flux en temps réel :** Fournit aux utilisateurs des mises à jour (selon la connexion) sur le statut du flux et les infos système.
  
- **Panneau d'administration M.C. :** L'administrateur peut :
    - Modifier le **nom du DJ** ou afficher des messages à l'audience et changer l'image de fond depuis son smartphone.
      Les utilisateurs Android peuvent prendre la photo directement depuis l'appareil photo et les utilisateurs iOS doivent d'abord prendre la photo, puis la sélectionner dans la galerie.
    - Surveiller les **pics d'audience** et les **auditeurs**.
    - Surveiller le système et redémarrer les services ou les appareils.
    - Rendre les haut-parleurs muets/audibles pour passer d'un événement bruyant à un silence avec des écouteurs.
  
- **Invitations conviviales :** Les participants peuvent inviter n'importe qui à rejoindre la fête via :
  un **code QR** vers le point d'accès et l'url dj.zic.

- **Modes multiples**
  - Mode solo : diffusez avec des amis. 
  - Mode relais : Ajoutez des relais (Raspberry Pi 3/4/5) pour une plus grande portée d'audience ou d'espace ou diffusez en cortège pour des protestations silencieuses ou bruyantes, performances, événements festifs 🚴‍♂️🔊🎶...

- **Conçu pour les smartphones en FR et EN** Vous pouvez relayer le flux de votre smartphone vers vos appareils bluetooth (écouteurs, enceintes) ou écouter sur les haut-parleurs intégrés du smartphone.

## Mode Solo
### Exigences
- 1 Raspberry Pi Modèle 3, 4 ou 5
- 1 Audio USB/jack (peu coûteux)
- Alimentation externe :
  - Pi 3B/3B+ : 5V 2,5A minimum
  - Pi 4 : 5V 3A minimum
  - Pi 5 : 5V 5A minimum (via USB-C avec Power Delivery)
- Optionnel : Enceintes

![DJ.zic mode solo](Doc/SoloMode.svg)
*Figure 1 : Architecture du mode solo pour Pi3/4 ou Pi5*

## Mode Maître et Relais
### Wifi intégré du Raspberry Pi 
#### Exigences
- **Maître**
  - 1 Raspberry Pi Modèle 4 ou 5 (conseillé)
  - 1 Audio USB/jack (peu coûteux)
  - Alimentation externe :
  - Pi 3B/3B+ : 5V 2,5A minimum
  - Pi 4 : 5V 3A minimum
  - Pi 5 : 5V 5A minimum (via USB-C avec Power Delivery)
- Optionnel : Enceintes
- **Relais**
  -  1 Raspberry Pi Modèle 3, 4 ou 5 par relais
  -  1 Alimentation externe par relais
  -  Optionnel : enceintes par relais

![DJ.zic carte Wi-Fi intégrée](Doc/Wlan0Mode.svg)
*Figure 2 : Aperçu du système avec un Raspberry 3/4 ou 5 comme maître (L'ordre et les modèles des relais sont à titre d'illustration car ils sont gérés par le script d'installation.)*

### Wifi intégré du Raspberry Pi et Wi-fi USB supplémentaire
#### Exigences
- **Maître**
  - 1 Raspberry Pi Modèle 4 ou 5 (conseillé d'utiliser l'appareil le plus puissant comme maître).
  - 1 Audio USB/jack (peu coûteux)
  - 1 Wifi/USB 
  - Alimentation externe :
  
    Pi 3B/3B+ : 5V 2,5A minimum
  - Pi 4 : 5V 3A minimum
  - Pi 5 : 5V 5A minimum (via USB-C avec Power Delivery)
  - Optionnel : Enceintes

- **Relais**
  -  1 Raspberry Pi Modèle 3, 4 ou 5 par relais
  -  1 Wifi/USB par relais
  -  1 Alimentation externe par relais
  -  Optionnel : enceintes par relais
  
  ![DJ.zic mode solo](Doc/Wlan1Mode.svg)
  *Figure 3 : Aperçu du système avec un Raspberry 3/4 ou 5 comme maître (L'ordre et les modèles des relais sont à titre d'illustration car ils sont gérés par le script d'installation.)*

## Installation
L'installation nécessite d'installer d'abord le Raspberry maître quel que soit le mode que vous utiliserez. La détection du modèle Raspberry fait partie de l'installation qui adapte les paramètres en conséquence.

1. **Créez l'image Raspberry**
Créez une image pour votre modèle avec [Raspberry Pi Imager](https://www.raspberrypi.com/software/) et :
- sélectionnez : Raspberry PI OS (Autre) > **Pi OS Lite (64-bit)**
- **Configurer le LAN sans fil** et **Définir les paramètres régionaux** doivent être décochés.
- **Activer SSH** : **Autoriser uniquement l'authentification authorized_keys** avec la clé proposée par Raspberry Pi Imager ou créez-en une nouvelle.
  
  ⚠️ Si vous avez déjà une clé et que vous voulez en créer une nouvelle, faites une copie de l'existante `id_rsa` sinon elle sera écrasée !

Vous voulez utiliser plusieurs Raspberry Pi, si c'est le cas préparez une image par appareil avec les paramètres ci-dessus et donnez des noms d'hôte différents pour chacun, avec maître pour le premier appareil et relais_1, etc... Cela aide beaucoup à s'y retrouver.

1. **Configuration de l'appareil**
   
   **La carte son USB/jack du Raspberry maître doit être branchée sur le Raspberry Pi.** pendant l'installation.

   **Si vous prévoyez d'utiliser un adaptateur WI-FI/USB, ses pilotes doivent être installés avant ce qui suit.**

2. Copiez le répertoire d'installation de ce dépôt dans votre répertoire home du Raspberry Pi.
3. Modifiez les utilisateurs administrateurs par défaut et le mot de passe dans `lib_install\config.py`
4. Lancez l'installation

```bash
sudo python install.py
```

Le processus d'installation vous demandera :
```text
Prévoyez-vous d'utiliser d'autres Raspberry Pi comme relais pour celui-ci ?
(oui/non)
```
**non** pour le mode Solo, où aucun autre Raspberry n'est nécessaire.
Aucune autre interaction utilisateur requise.
Redémarrez l'appareil à la fin de l'installation 

**oui** si vous avez plusieurs appareils à ajouter, veuillez lire [Mode Relais](#mode-relais) et [Mode Relais Post-installation](#mode-relais-post-installation).
- ```text
    Combien de relais voulez-vous utiliser ?
    1-10:
  ```
  Vous pouvez ajouter plus d'appareils en modifiant la valeur de `max` **avant de lancer** install.py dans `lib_install\utils.py`

  ```python
  def selectAmountOfDevice():
        max = 10
  ```

- ```bash
  Utiliserez-vous une carte Wi-Fi USB ?
  (oui/non)
  ```
**non** : l'appareil Wi-Fi est la carte intégrée du Raspberry (wlan0).

**oui** : La carte intégrée du Raspberry est wlan0 et l'USB/Wi-Fi est wlan1.
⚠️ Vous aurez besoin d'une Wi-Fi par Rasberry, et les pilotes doivent être installés avant le processus d'installation.

Le processus d'installation configurera le système et les logiciels.

### Mode Relais
Lorsque le script d'installation se termine, il crée un fichier `install-Next-DjZic.tar.gz` dans votre répertoire home, déplacez ce fichier dans le répertoire home du prochain Raspberry et :

```bash
tar -xvf install-Next-DjZic.tar.gz
cd install
sudo python install.py
```
une fois l'installation terminée, un fichier `install-Next-DjZic.tar.gz` mis à jour sera créé dans votre répertoire home. Répétez cette opération pour chaque appareil à ajouter.

⚠️ `install-Next-DjZic.tar.gz` doit être copié depuis le dernier appareil installé vers le nouvel appareil que vous voulez installer et ainsi de suite.

#### Mode Relais Post-installation
Le réseau DJ.zic utilise ses propres certificats pour la sécurité.
Ils sont inclus dans `install-Next-DjZic.tar.gz` si vous en avez besoin pour accéder à distance (gardez-le sécurisé).

Donc, avec tous les appareils allumés, vous pouvez utiliser Terminator multi-view ou mobaXterm MultiExec pour lancer à la fois sur tous les appareils la commande suivante :

```bash
cd ~/install
python postinstall.py
```
Cela mettra à jour les known_hosts sur tous les appareils permettant les interconnexions du système dj.zic.

## Vous aimez ?
Aidez-moi à acheter de nouveaux appareils pour construire une architecture plus solide pour une grande quantité d'appareils, ou pour m'encourager à ajouter plus de fonctionnalités, ou simplement exprimer votre enthousiasme pour dj.zic (le site Web musical qui n'existe pas sur Internet 😁).

Je pense aussi à déployer cet outil pour les lanceurs d'alerte afin d'envoyer des photos/vidéos/enregistrements/diffusion en direct à leurs compagnons... pour qu'il n'y ait aucune trace sur votre smartphone lors de coups portés par les autorités...

[![Donate](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://paypal.me/TGrandsart?country.x=FR&locale.x=fr_FR)

## Licence

Ce projet est autorisé sous [Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)](https://creativecommons.org/licenses/by-nc/4.0/deed.fr).  
Vous êtes libre de partager et d'adapter ce contenu, à condition de créditer l'auteur et de ne pas l'utiliser à des fins commerciales.

**Pour un usage commercial** et pour un développement/améliorations particuliers, veuillez ✉️ [contacter l'auteur](mailto:thierry.grandsart@free.fr).

![Licence CC BY-NC](https://licensebuttons.net/l/by-nc/4.0/88x31.png)

## Remerciements
SVG Doc, réalisé en utilisant [Freepik](https://www.freepik.com), [Marz Gallery](https://www.flaticon.com/authors/marz-gallery), [Talha Dogar](https://www.flaticon.com/authors/talha-dogar), [logisstudio](https://www.flaticon.com/authors/logisstudio)
 de [www.flaticon.com](https://www.flaticon.com) sont autorisés par [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/) et l'image Raspberry de [efa2](https://commons.wikimedia.org/wiki/File:Raspberry_Pi_B%2B_rev_1.2.svg) autorisée par [CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/)