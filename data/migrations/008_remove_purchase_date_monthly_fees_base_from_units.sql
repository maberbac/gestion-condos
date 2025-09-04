-- Migration 008: Suppression des colonnes purchase_date et monthly_fees_base de la table units

-- Supprimer la colonne purchase_date de la table units
ALTER TABLE units DROP COLUMN purchase_date;

-- Supprimer la colonne monthly_fees_base de la table units
ALTER TABLE units DROP COLUMN monthly_fees_base;
