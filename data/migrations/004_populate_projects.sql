-- Migration 004: Initialisation des projets de base
-- Création des 4 projets de démonstration pour une nouvelle instance
-- 
-- Ce script initialise la base de données avec les projets de base
-- pour les démonstrations et nouvelles instances du système.

-- Insérer les 4 projets de base pour démonstration (uniquement s'ils n'existent pas)

-- Projet 1: Centre-Ville Plaza (8 unités de stationnement)
INSERT OR IGNORE INTO projects (project_id, name, address, total_area, construction_year, unit_count, constructor, creation_date, status) VALUES
('p1q2r3s4-t5u6-7890-abcd-123456789xyz', 'Centre-Ville Plaza', '123 Rue Principale, Montréal, QC H3A 1B1', 1600.0, 2020, 8, 'Construction Moderne Inc.', '2020-03-15', 'active');

-- Projet 2: Complexe Rivière (15 unités mixtes résidentiel/commercial)
INSERT OR IGNORE INTO projects (project_id, name, address, total_area, construction_year, unit_count, constructor, creation_date, status) VALUES
('x9y8z7w6-v5u4-3210-9876-543210abcdef', 'Complexe Rivière', '456 Boulevard de la Rivière, Québec, QC G1R 2B3', 12750.0, 2019, 15, 'Bâtisseurs Rivière Ltée', '2019-08-22', 'active');

-- Projet 3: Résidence Les Érables (12 unités résidentielles)
INSERT OR IGNORE INTO projects (project_id, name, address, total_area, construction_year, unit_count, constructor, creation_date, status) VALUES
('f8c4dc0b-f1ce-4492-b15f-5ebaa3c018f5', 'Résidence Les Érables', '789 Avenue des Érables, Sherbrooke, QC J1H 3C4', 9600.0, 2021, 12, 'Érables Construction', '2021-05-10', 'active');

-- Projet 4: Tour Horizon (20 unités mixtes résidentiel/commercial)
INSERT OR IGNORE INTO projects (project_id, name, address, total_area, construction_year, unit_count, constructor, creation_date, status) VALUES
('a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'Tour Horizon', '101 Rue du Horizon, Gatineau, QC J8X 4D5', 22000.0, 2022, 20, 'Horizon Développement', '2022-01-30', 'active');

-- Vérification de l'insertion des projets
SELECT 'Migration 004 terminée: ' || COUNT(*) || ' projets créés' as status FROM projects;