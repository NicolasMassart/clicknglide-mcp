---
name: cfp-planning-et-vols-initiation
description: À utiliser pour Caen Falaise Planeurs quand on demande qui vole ou ce qui manque un jour ou un week-end, quand il faut ajouter, déplacer ou retirer un vol d'initiation (VI) dans le planning, ou répondre à une demande de vol d'initiation ou de bon cadeau.
---

# Caen Falaise Planeurs : planning et vols d'initiation

Complète `clicknglide-planning-summary` et `clicknglide-signups`, avec les ids de `cfp-configuration-club`.

## Résumé d'une journée ou d'un week-end

1. Un seul `get_signups_range` pour la période (week-end : samedi et dimanche ; penser au mercredi).
2. Pour chaque jour, contrôler dans cet ordre :
   - **Remorqueur** (champ 1) : s'il n'y en a pas, pas de vol. C'est le manque le plus important.
   - **Instructeur** (champ 4) si des élèves sont inscrits (champ 5, max 4 ; champs 274 et 107). Comparer avec le paramètre « Nb d'elèves » des instructeurs.
   - **VI** : lignes du champ 8 face aux pilotes VI du champ 7 et à leur « Nb de VI ». Un VI sans pilote VI est à signaler immédiatement.
   - **Monde sur le terrain** : brevetés (3), élèves et aide en piste / accueil VI (275). Peu de monde, c'est un risque pour sortir les machines.
3. Ajouter les événements du jour (`get_next_events`), les stages notamment.
4. Pour combler un manque, proposer un message au groupe concerné (voir `cfp-messagerie-club`), sans jamais l'envoyer sans accord.

## Ajouter un vol d'initiation (champ 8, texte libre)

Convention du club pour chaque ligne : `<n° du bon HelloAsso> - <Prénom Nom> - <téléphone>`, avec l'heure si elle est convenue (par exemple `14h30`).

1. Vérifier la date : jour de vol, VI déjà inscrits, pilote VI présent (champ 7).
2. Aperçu `add_freetext_signup(date, 8, "<ligne>")`, ou `add_freetext_signups_bulk` pour plusieurs VI, puis accord explicite, puis `confirm: true`.
3. S'il n'y a pas encore de pilote VI ce jour-là, le dire. Proposer un message au groupe « Pilotes VI » et, si besoin, « Aide en piste / accueil VI ».
4. Pour déplacer un VI : supprimer la ligne (`delete_signup` avec son `signupId`), puis la recréer à la nouvelle date. Ce sont deux aperçus et deux accords.

## Réponse type à une demande de VI ou de bon cadeau

Infos validées par le club :
- Le VI coûte 130 €, dure environ 30 minutes en planeur biplace, assurance FFVP comprise.
- Il s'achète en **bon cadeau sur HelloAsso** depuis https://caenfalaiseplaneurs.fr/fr/discovery, valable 1 an.
- Le bénéficiaire contacte ensuite le club, et un pilote bénévole fixe la date avec lui.
- Le VI est l'occasion de découvrir le club et de poser ses questions sur place.

Pour un futur élève de plus de 25 ans (tarifs 2027, révisables à l'AG de début mars) :
- cotisation + licence-assurance FFVP : 419,06 €, payables en une fois en début d'année ;
- cours théoriques en ligne FFVP : 75 € ;
- une journée de vol avec instructeur : environ 55 €, remorquage compris ;
- forfait de 15 h : 255 €, payable en trois fois ;
- brevet : en moyenne 2 saisons, soit environ 3 100 € au total ;
- pas de bourse FFVP après 25 ans.

On s'inscrit aux journées sur l'outil de planning. Un élève fait d'abord un vol par jour, plusieurs en fin de formation, et peut venir aussi souvent qu'il le souhaite, selon la météo et les instructeurs.

Rester bref et chaleureux. Signer avec le nom et la fonction de l'utilisateur, suivis de « Caen Falaise Planeurs ». Ne jamais envoyer de réponse sans accord.
