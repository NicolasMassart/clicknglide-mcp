---
name: cfp-configuration-club
description: À utiliser avant toute tâche Click n' Glide pour le club Caen Falaise Planeurs (planning, inscriptions, membres, messages, événements) : donne les ids des rôles et des champs du planning du club, le rythme des journées et les règles maison, en complément des skills génériques clicknglide-*.
---

# Caen Falaise Planeurs : configuration Click n' Glide

S'appuie sur `clicknglide-getting-started` : aperçu puis accord explicite avant toute écriture, quota de 300 appels/jour, données personnelles. Configuration relevée en octobre 2026. Si un id ne correspond plus, refaire la découverte (`get_roles`, `get_signups_range`) et le signaler.

## Rôles (`get_roles`)

| id | Rôle | Remarque |
|---|---|---|
| 1 | Remorqueurs | pilotes remorqueurs |
| 3 | Pilotes brevetés | titulaires du SPL |
| 5 | Élèves | rôle de base porté par presque tous les pilotes, brevetés compris (accès au champ « Élèves inscrits ») |
| 13 | Élève en formation | élèves en cours de formation (groupe de messagerie) |
| 6 | Élèves lâchés | élèves autorisés à voler seuls |
| 12 | Pass Solo | élèves sous formule Pass Solo |
| 4 | Instructeurs | |
| 7 | Pilotes VI | pilotes habilités aux vols d'initiation |
| 10 | Pilotes DUO sans SPL | usage à confirmer par le secrétariat |
| 11 | Vols découverte 3/6/FFAM | formules découverte 3, 6 ou 12 vols et FFAM |
| 0 | CnGAdministrator | **privilégié**, jamais sans demande explicite |
| -1 | MemberManagementContact | **privilégié** (gestion des membres) |
| -2 | BillingContact | **privilégié** (facturation) |

## Champs récurrents du planning (`get_signups`)

| fieldId | Intitulé | Type | Rôle autorisé | Paramètre |
|---|---|---|---|---|
| 1 | Pilotes remorqueurs | inscription | Remorqueurs (1) | aucun |
| 3 | Pilotes brevetés | inscription | Pilotes brevetés (3) | aucun |
| 4 | Instructeurs | inscription | Instructeurs (4) | « Nb d'elèves », 4 par défaut |
| 5 | Élèves inscrits | inscription | Élèves (5) | limite de 4 inscrits |
| 274 | Elèves lâchés | inscription | Élèves lâchés (6) | aucun |
| 107 | Pass Solo | inscription | Pass Solo (12) | aucun |
| 45 | Formule découverte 3, 6, 12 vols et FFAM | inscription | Vols découverte (11) | aucun |
| 96 | Pilotes DUO sans SPL | inscription | Pilotes DUO sans SPL (10) | aucun |
| 7 | Pilotes VI | inscription | Pilotes VI (7) | « Nb de VI », 4 par défaut |
| 8 | Vols d'Initiation | **texte libre** | Pilotes VI (7) | sans commentaire |
| 275 | Aide en piste / acceuil VI | inscription | tous les membres | aucun |
| 20 | Entretien machine/locaux | inscription | tous les membres | aucun |
| 235 | Nuit au club-house | inscription | tous les membres | aucun |

Les événements (stages, repas, formation sécurité, arrosage…) sont des champs ponctuels avec une `eventDuration` et un id qui change à chaque fois : toujours les lire via `get_next_events`. Sur les champs sans paramètre, la valeur `signupParameter` (0 ou 4) est sans signification : l'ignorer.

## Rythme du club

- On vole surtout **le week-end et le mercredi après-midi**, selon la météo. Il y a aussi des **stages** : stage d'été en juillet-août (activité quasi quotidienne) et stages d'instruction ponctuels (par exemple sur plusieurs jours en octobre).
- Une journée de vol a besoin de **la météo**, d'**un pilote remorqueur** (champ 1) et de **camarades pour sortir les machines**. Les élèves ont aussi besoin d'**un instructeur** (champ 4).
- Les membres s'inscrivent eux-mêmes aux journées sur Click n' Glide.
- Les tarifs peuvent évoluer lors de l'assemblée générale, en général début mars.
