-- Migration 007: Renommer total_area en building_area et réorganiser les colonnes
-- Cette migration renomme total_area en building_area et réorganise l'ordre des colonnes

-- SQLite ne supporte pas ALTER COLUMN RENAME, donc on doit recréer la table

-- 1. Créer une nouvelle table avec la structure correcte
CREATE TABLE projects_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    building_area REAL NOT NULL,  -- Renommé de total_area
    land_area REAL DEFAULT 0.0,   -- Maintenant juste après building_area
    construction_year INTEGER NOT NULL,
    unit_count INTEGER NOT NULL,
    constructor TEXT NOT NULL,
    creation_date TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Copier toutes les données de l'ancienne table vers la nouvelle
INSERT INTO projects_new (
    id, project_id, name, address, building_area, land_area, 
    construction_year, unit_count, constructor, creation_date, 
    status, created_at, updated_at
)
SELECT 
    id, project_id, name, address, total_area, land_area,
    construction_year, unit_count, constructor, creation_date,
    status, created_at, updated_at
FROM projects;

-- 3. Supprimer l'ancienne table
DROP TABLE projects;

-- 4. Renommer la nouvelle table
ALTER TABLE projects_new RENAME TO projects;

-- 5. Recréer les index
CREATE INDEX IF NOT EXISTS idx_projects_project_id ON projects(project_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_building_area ON projects(building_area);
CREATE INDEX IF NOT EXISTS idx_projects_land_area ON projects(land_area);

-- 6. Recréer les triggers
CREATE TRIGGER IF NOT EXISTS update_projects_timestamp 
    AFTER UPDATE ON projects
    FOR EACH ROW
BEGIN
    UPDATE projects SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
