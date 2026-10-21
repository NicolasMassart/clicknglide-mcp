---
name: cfp-messagerie-club
description: À utiliser pour Caen Falaise Planeurs quand on veut lire ou résumer la messagerie ou le forum du club, ou préparer un message Click n' Glide à un groupe (remorqueurs, instructeurs, élèves, pilotes VI, tous les membres…), par exemple pour combler un manque sur une journée ou annoncer un événement.
---

# Caen Falaise Planeurs : messagerie et groupes

Suivre `clicknglide-messages-forum` : aperçu, accord explicite sur le message exact, premier envoi de test à soi-même, pas de renvoi si l'envoi n'est pas confirmé.

## Groupes de destinataires (clés de `send_message.groups`)

| Groupe | Usage typique |
|---|---|
| `*` (Tous les membres) | annonces générales : AG, repas, travaux, formation sécurité, fermeture |
| `Remorqueurs` | trouver un remorqueur pour une journée |
| `Instructeurs` | organiser l'instruction, les stages, trouver un instructeur |
| `Élève en formation` | infos aux élèves en cours de formation (théorie, stages, progression) |
| `Élèves` | presque tout le club : rôle de base, brevetés compris. Préférer `Élève en formation` pour viser les élèves |
| `Élèves lâchés`, `Pass Solo` | consignes aux élèves solo |
| `Pilotes brevetés` | vie des pilotes : machines, campagne, sécurité |
| `Pilotes VI` | trouver un pilote pour des vols d'initiation |
| `Vols découverte 3/6/FFAM`, `Pilotes DUO sans SPL` | suivi de ces formules |
| `CnGAdministrator`, `MemberManagementContact`, `BillingContact` | bureau et gestion : seulement si l'utilisateur le demande |

## Modèles de messages (à adapter, toujours relus par l'utilisateur)

- **Appel remorqueur** (groupe `Remorqueurs`) : « Bonjour à tous, il nous manque un pilote remorqueur le <jour date> (<n> élèves et <n> VI prévus). Qui serait disponible ? Merci de vous inscrire directement sur le planning. »
- **Appel pilote VI** (groupe `Pilotes VI`) : « <n> vols d'initiation sont prévus le <jour date> et aucun pilote VI n'est inscrit pour l'instant. Merci à ceux qui le peuvent de s'inscrire sur le planning en indiquant leur nombre de VI. »
- **Annonce d'événement** (groupe `*`) : titre, date, lieu (le terrain), inscription sur Click n' Glide dans le champ de l'événement.

Signer avec le nom et la fonction de l'utilisateur. Rappeler que le message part aussi par email à chaque destinataire. Pour les résumés, regrouper par sujet et mettre d'abord ce qui demande une action de l'utilisateur.
