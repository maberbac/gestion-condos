-- Migration 006: Ajout du champ land_area à la table projects
-- Cette migration ajoute une colonne séparée pour la superficie du terrain

-- Ajouter la colonne land_area à la table projects
ALTER TABLE projects ADD COLUMN land_area REAL DEFAULT 0.0;

-- Mettre à jour les enregistrements existants pour que land_area = total_area par défaut
-- (l'utilisateur pourra ensuite modifier ces valeurs selon ses besoins)
UPDATE projects SET land_area = total_area WHERE land_area = 0.0;

-- Créer un index pour améliorer les performances sur land_area
CREATE INDEX IF NOT EXISTS idx_projects_land_area ON projects(land_area);
