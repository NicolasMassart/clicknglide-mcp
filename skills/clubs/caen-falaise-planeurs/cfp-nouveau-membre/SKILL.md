---
name: cfp-nouveau-membre
description: À utiliser pour Caen Falaise Planeurs quand on demande d'ajouter un nouveau membre dans Click n' Glide (« ajoute un nouvel élève / passager découverte 3/6 vols / stagiaire FFAM / pilote breveté / remorqueur / instructeur ») avec les bons rôles, de faire évoluer les rôles d'un membre (lâché, Pass Solo, breveté, VI…), ou de donner un rôle administrateur, gestion ou facturation.
---

# Caen Falaise Planeurs : nouveau membre et évolution des rôles

Suivre `clicknglide-members` (doublons, aperçu, accord explicite, email d'activation, vérification) avec les rôles de `cfp-configuration-club`. Langue par défaut : `fr` (`en` pour les membres anglophones).

## Les 6 profils de création

L'utilisateur peut dire simplement « ajoute un nouvel élève / un nouveau passager découverte 3/6 vols / un stagiaire FFAM / un pilote breveté / un remorqueur / un instructeur ». Les rôles sont déduits des combinaisons portées par les membres actuels (statistiques anonymes, octobre 2026). Les lignes ⚠️ sont **à confirmer par le secrétariat** : tant qu'elles ne sont pas validées, demander confirmation à l'utilisateur au moment de l'aperçu.

| Profil (formulation) | Rôles à la création (ids) | Statut |
|---|---|---|
| **Nouvel élève** | Élèves (5) + Élève en formation (13) | sûr (combinaison la plus fréquente chez les élèves) |
| **Passager découverte 3/6 vols** | Vols découverte 3/6/FFAM (11) seul | ⚠️ à confirmer : 11 seul est observé, mais aussi 11 + 5 + 13 et 11 + 5 |
| **Stagiaire FFAM** | Vols découverte 3/6/FFAM (11) seul | ⚠️ à confirmer : le même rôle 11 couvre FFAM ; faut-il aussi 5 + 13 ? |
| **Pilote breveté** | Pilotes brevetés (3) + Élèves (5) | sûr (5 est gardé pour réserver des vols d'instruction) |
| **Remorqueur** (breveté planeur) | 3 + 5 + Remorqueurs (1) | sûr ; se cumule avec breveté comme observé |
| **Remorqueur** (pas encore breveté planeur) | 1 + 5, ou 1 + 5 + 13 + 6 s'il est élève lâché | ⚠️ à confirmer : demander si la personne est brevetée planeur |
| **Instructeur** | Instructeurs (4) + 3 + 5 + Pilotes VI (7) | ⚠️ à confirmer : 7 est porté par 4 instructeurs sur 5 ; 1 (remorqueur) seulement s'il remorque |

Ne jamais ajouter à la création les rôles CnGAdministrator (0), MemberManagementContact (-1) ou BillingContact (-2), même sur demande : créer le membre d'abord.

Profils hors création rapide (évolutions) : élève lâché = 5 + 13 + 6 ; Pass Solo = 5 + 13 + 6 + 12 (⚠️ à confirmer : on voit aussi 5 + 13 + 12) ; pilote VI = 3 + 5 + 7 ; Pilotes DUO sans SPL (10) ⚠️ définition à confirmer.

## Rôles administrateur, gestion des membres, facturation (0, -1, -2)

- Jamais à la création.
- Seulement pour un membre **existant, au compte validé, qui s'est connecté récemment** : `lastVisit` dans `get_users` différent de `0000-00-00 00:00:00` et datant de moins de **30 jours**. Ce seuil est proposé, ⚠️ à valider par le secrétariat.
- Seulement sur **demande explicite** qui nomme la personne et le rôle, avec un aperçu « avant → après » de `update_user` et un accord explicite.
- Sinon, refuser en expliquant pourquoi (compte non activé ou inactif).

## Évolutions courantes (`update_user` remplace TOUTE la liste de rôles)

- Débutant → lâché : ajouter 6.
- Lâché → breveté : ajouter 3 ; retirer 13 et 6 (⚠️ à confirmer : retire-t-on « Élève en formation » et « Élèves lâchés » au brevet ?) ; garder 5.
- Breveté → remorqueur, pilote VI ou instructeur : ajouter respectivement 1, 7 ou 4.
- Formule découverte → élève : ajouter 5 + 13 (⚠️ à confirmer : garde-t-on 11 jusqu'à la fin de la formule ?).

Toujours montrer « avant → après » avec les noms des rôles, et rappeler qu'à la création Click n' Glide envoie un email d'activation au membre.
