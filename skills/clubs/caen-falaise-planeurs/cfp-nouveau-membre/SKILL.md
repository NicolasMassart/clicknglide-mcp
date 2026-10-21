---
name: cfp-nouveau-membre
description: À utiliser pour Caen Falaise Planeurs quand on demande d'ajouter un nouveau membre dans Click n' Glide (« ajoute un nouvel élève / passager découverte 3/6 vols / stagiaire FFAM / pilote breveté / remorqueur / instructeur ») avec les bons rôles, de faire évoluer les rôles d'un membre (lâché, Pass Solo, breveté, VI…), ou de donner un rôle administrateur, gestion ou facturation.
---

# Caen Falaise Planeurs : nouveau membre et évolution des rôles

Suivre `clicknglide-members` (doublons, aperçu, accord explicite, email d'activation, vérification) avec les rôles de `cfp-configuration-club`. Langue par défaut : `fr` (`en` pour les membres anglophones).

## Les 6 profils de création

L'utilisateur peut dire simplement « ajoute un nouvel élève / un nouveau passager découverte 3/6 vols / un stagiaire FFAM / un pilote breveté / un remorqueur / un instructeur ». Correspondances validées par le secrétariat (octobre 2026). Les lignes encore marquées ⚠️ sont à confirmer : demander confirmation à l'utilisateur au moment de l'aperçu.

| Profil (formulation) | Rôles à la création (ids) |
|---|---|
| **Nouvel élève** | Élèves (5) + Élève en formation (13) |
| **Passager découverte 3/6 vols** | Vols découverte 3/6/FFAM (11) seul |
| **Stagiaire FFAM** | Vols découverte 3/6/FFAM (11) seul |
| **Pilote breveté** | Pilotes brevetés (3) + Élèves (5) |
| **Remorqueur** | Remorqueurs (1). C'est un statut à part, sans lien avec la qualité de pilote ou d'élève planeur : on l'ajoute à côté des rôles planeur que la personne a par ailleurs, sans en déduire aucun. |
| **Instructeur** | Instructeurs (4) + Pilotes brevetés (3) + Élèves (5) + Pilotes VI (7) : tous les instructeurs peuvent être pilotes VI. |

Ne jamais ajouter à la création les rôles CnGAdministrator (0), MemberManagementContact (-1) ou BillingContact (-2), même sur demande : créer le membre d'abord.

Profils hors création rapide (évolutions) : élève lâché = 5 + 13 + 6 ; Pass Solo = 5 + 13 + 6 + 12 (⚠️ à confirmer : on voit aussi 5 + 13 + 12) ; pilote VI = 3 + 5 + 7 ; Pilotes DUO sans SPL (10) ⚠️ définition à confirmer.

## Rôles administrateur, gestion des membres, facturation (0, -1, -2)

- Jamais à la création.
- Seulement pour un membre **existant, au compte validé, qui s'est connecté récemment** : `lastVisit` dans `get_users` différent de `0000-00-00 00:00:00` et datant de moins de **30 jours** (seuil validé par le secrétariat).
- Seulement sur **demande explicite** qui nomme la personne et le rôle, avec un aperçu « avant → après » de `update_user` et un accord explicite.
- Sinon, refuser en expliquant pourquoi (compte non activé ou inactif).

## Évolutions courantes (`update_user` remplace TOUTE la liste de rôles)

- Débutant → lâché : ajouter 6.
- Élève → breveté : ajouter 3 et garder seulement 5 parmi les rôles élève (retirer 13, 6 et 12).
- Devient remorqueur : ajouter 1, indépendamment du statut planeur.
- Breveté → pilote VI : ajouter 7. Breveté → instructeur : ajouter 4 et 7.
- Formule découverte → élève : ajouter 5 + 13 (⚠️ à confirmer : garde-t-on 11 jusqu'à la fin de la formule ?).

Toujours montrer « avant → après » avec les noms des rôles, et rappeler qu'à la création Click n' Glide envoie un email d'activation au membre.
