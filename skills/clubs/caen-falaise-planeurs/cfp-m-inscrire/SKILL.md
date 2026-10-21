---
name: cfp-m-inscrire
description: À utiliser pour Caen Falaise Planeurs quand l'utilisateur veut s'inscrire lui-même (ou se désinscrire, ou modifier son inscription) sur le planning Click n' Glide un ou plusieurs jours : « inscris-moi samedi comme remorqueur », « mets-moi en maintenance le 14 », « nuit au club vendredi », « je viens en instructeur mercredi, j'arrive tard ».
---

# Caen Falaise Planeurs : m'inscrire sur le planning

Appliquer `clicknglide-self-signup` avec la configuration de `cfp-configuration-club`.

- **Identifiant de l'utilisateur** : ne pas l'écrire ici, ce dépôt est public. Le retrouver une fois via `get_users` (par son email de connexion ou ses prénom et nom), puis le garder dans les notes ou la mémoire **privées** du bot.
- **Rôles** : ses rôles, lus dans la même réponse, indiquent les cases auxquelles il a droit.

## Correspondance des cases (fieldId)

| Ce que dit l'utilisateur | Case (fieldId) | Rôle requis | Paramètre / remarque |
|---|---|---|---|
| remorqueur, « je remorque » | Pilotes remorqueurs (1) | Remorqueurs | aucun |
| pilote, « je vole », breveté | Pilotes brevetés (3) | Pilotes brevetés | aucun |
| instructeur, « je fais de l'instruction » | Instructeurs (4) | Instructeurs | « Nb d'elèves », 4 par défaut ; demander s'il veut moins |
| élève, « vol d'instruction », « double » | Élèves inscrits (5) | Élèves | 4 inscrits au maximum, ensuite liste d'attente |
| élève lâché, « solo » | Elèves lâchés (274) | Élèves lâchés | aucun |
| Pass Solo | Pass Solo (107) | Pass Solo | aucun |
| pilote VI, « je fais des VI » | Pilotes VI (7) | Pilotes VI | « Nb de VI », 4 par défaut |
| aide en piste, accueil des VI | Aide en piste / acceuil VI (275) | tous | aucun |
| maintenance, entretien, ménage, travaux | Entretien machine/locaux (20) | tous | aucun |
| nuit au club, « je dors au club » | Nuit au club-house (235) | tous | aucun |
| formule découverte, FFAM | Formule découverte 3, 6, 12 vols et FFAM (45) | Vols découverte 3/6/FFAM | aucun |
| événement (stage, repas, formation sécurité…) | id de l'événement via `get_next_events` | tous | change à chaque événement |

Si « pilote » est ambigu (breveté, élève lâché ou Pass Solo), choisir d'après ses rôles, et demander en cas de doute. Un commentaire (« j'arrive tard », « l'après-midi seulement ») est possible sur toutes ces cases sauf les vols d'initiation (champ 8, texte libre, réservé aux VI clients).

## Rappels club

- Les jours de vol habituels sont le week-end et le mercredi après-midi. Si la date demandée tombe un autre jour hors stage, le signaler sans bloquer.
- Lors d'une désinscription comme remorqueur ou instructeur, prévenir si c'était le seul ce jour-là. Proposer ensuite un message au groupe `Remorqueurs` ou `Instructeurs` (voir `cfp-messagerie-club`), jamais envoyé sans accord.
