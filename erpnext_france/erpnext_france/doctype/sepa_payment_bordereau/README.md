# SEPA Payment System

Ce module implémente un système complet de gestion des paiements SEPA pour ERPNext France.

## Fonctionnalités

### 1. Mandat SEPA (SEPA Mandate)
- Gestion des mandats de prélèvement SEPA
- Support des types CORE et B2B
- Gestion des séquences FRST (premier prélèvement) et RCUR (récurrent)
- Validation : un seul mandat actif par client et compte bancaire

### 2. Bordereau de Paiement SEPA (SEPA Payment Bordereau)
- Regroupement de plusieurs factures en un seul fichier SEPA
- Support pour :
  - Prélèvements (SEPA Direct Debit / pain.008)
  - Virements (SEPA Credit Transfer / pain.001)
- Statuts : Brouillon → Validé → Exporté → Envoyé → Rejets partiels/Clôturé

### 3. Lignes de Bordereau (SEPA Payment Bordereau Line)
- Une ligne = une facture
- Génération automatique d'un End-to-End ID unique pour chaque paiement
- Statuts : En cours → Accepté/Rejeté

## Processus

### Ajout d'une facture au bordereau
1. Sur une facture validée avec un montant impayé
2. Cliquer sur "Add to SEPA Bordereau" (Actions)
3. La facture est ajoutée au bordereau en cours ou un nouveau est créé

### Validation et export
1. Ouvrir le bordereau SEPA
2. Cliquer sur "Validate Bordereau"
3. Contrôles automatiques (IBAN, BIC, mandats, montants)
4. Cliquer sur "Generate SEPA File"
5. Fichier XML généré (pain.008 ou pain.001)
6. Marquer comme "Sent" après envoi à la banque

### Rapprochement bancaire
- Les transactions bancaires sont rapprochées aux lignes via l'End-to-End ID
- Création automatique du Payment Entry
- Mise à jour des statuts et marquage de la facture comme payée

## Configuration requise

### Champs Client (Customer)
- `default_mode_of_payment` : Mode de paiement par défaut (Prélèvement/Virement)
- `sepa_mandate` : Lien vers le mandat SEPA actif

### Champs Compte Bancaire (Bank Account)
- IBAN et BIC (swift_number) requis

## Installation

Les DocTypes suivants sont créés :
- SEPA Mandate
- SEPA Payment Bordereau
- SEPA Payment Bordereau Line (Child Table)

Les custom fields pour Customer sont ajoutés via fixtures.

## Utilisation

### Créer un mandat SEPA
1. Aller dans SEPA Mandate
2. Créer un nouveau mandat
3. Sélectionner le client et le compte bancaire
4. Renseigner la RUM et la date de signature
5. Sauvegarder et activer

### Créer un bordereau de paiement
Les bordereaux sont créés automatiquement lors de l'ajout de factures via le bouton "Add to SEPA Bordereau".

### Générer un fichier SEPA
1. Ouvrir le bordereau
2. Valider le bordereau
3. Générer le fichier SEPA
4. Télécharger le fichier XML
5. Envoyer à la banque
6. Marquer comme envoyé

## Notes importantes

- Les mandats SEPA sont obligatoires uniquement pour les prélèvements
- Pour les virements, les comptes bancaires fournisseurs doivent être configurés
- La RUM (Référence Unique de Mandat) doit être unique
- Les End-to-End IDs sont générés automatiquement lors de la validation
- Format : COMPANY-YYYYMMDDHHMMSS-UUID8

## Support

Pour toute question ou problème, consulter la documentation officielle d'ERPNext France ou créer une issue sur GitHub.
