# ChatBot 🤖 **de réservation de vaccances** 🏖

---
## Dossiers présents

**1. bot.py **

```
https://github.com/Mickevin/ChatBot
Les scripts développés stockés sur Github permettant l’exécution du pipeline complet pour générer l’application web chatbot, entraîner et évaluer le modèle :
    - Créer un nouveau Bot
    - Se connecter à un bot existant
    - Configurer des entités et intention
    - Envoyer des phrase d'exemple
    - Entrainer le bot
    - Publier le Bot
    - Effectuer des prédiction
    - Evaluer les performances du Bot.
```
**2. P10_Développement d'un chatbot de réservation vacances **
```
Fichier notebook présantant la démarche méthodologique de création du bot LUIS et la connexion à Azure Insights
```

**3. P10_Méthodologie_pilotage_des_performances_Kevin_Duranty  **

```
Fichier présentant la méthodologie de mise à jour du modèle LUIS ainsi que les métric et seuil d'alerte du bot en phase de production
```

** P10_Présentation_Kevin_Duranty **
```
Présentation pdf du projet flybot
```


** P10_flybot_application **
```
https://github.com/Mickevin/FlyBot 
application web chatbot développée à l’aide de la version Python du Microsoft Bot Builder SDK

Pour la construction du bot nous avons utilisé le dossier "21.corebot-app-insights" du répertoir botbuilder-samples proposé par Microsoft.

Les fichiers modifiés :
- booking_details : qui contient les entités à détecter par le modèle LUIS

- config où les identifiants de connexion au MOdèle LUIS et à l'app Insights ont été ajoutés

-requirements : certains package ont été modifiés en raison de conflit de dépendances
 
- booking_dialog : le scénario du dialogue a été configuré

- main_dialog : la configuration des erreurs et de la fin de la conversation a été paramétrée,


-dialog_and_welcome_bot : le message de bienvenu a été changé,

-luis_helper : déétection des entité à été paramétrées.


```
 
