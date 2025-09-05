-- =====================================================
-- MIGRATION AUTOMATIQUE - DONNÉES DE BASE DE DONNÉES
-- =====================================================
-- Généré automatiquement le: 2025-09-05 15:55:14
-- Source: data\condos1.db
-- Tables: 6
-- Lignes totales: 28

-- Configuration SQLite
PRAGMA foreign_keys = OFF;  -- Désactiver temporairement pour les inserts
BEGIN TRANSACTION;

-- Table system_config: Aucune donnée à insérer

-- ==================== DONNÉES TABLE: feature_flags ====================
-- 5 lignes à insérer

-- Insertion des données dans feature_flags
INSERT INTO feature_flags (id, flag_name, is_enabled, description, created_at, updated_at) VALUES (1, 'finance_module', 0, 'Active ou désactive le module finance complet', '2025-09-04 10:43:54', '2025-09-04T16:36:44.671856');
INSERT INTO feature_flags (id, flag_name, is_enabled, description, created_at, updated_at) VALUES (2, 'finance_calculations', 0, 'Active ou désactive les calculs financiers avancés', '2025-09-04 10:43:54', '2025-09-04 10:43:54');
INSERT INTO feature_flags (id, flag_name, is_enabled, description, created_at, updated_at) VALUES (3, 'finance_reports', 1, 'Active ou désactive les rapports financiers détaillés', '2025-09-04 10:43:54', '2025-09-04 10:43:54');
INSERT INTO feature_flags (id, flag_name, is_enabled, description, created_at, updated_at) VALUES (4, 'analytics_module', 1, 'Active ou désactive le module d''analytics et statistiques', '2025-09-04 10:43:54', '2025-09-04 10:43:54');
INSERT INTO feature_flags (id, flag_name, is_enabled, description, created_at, updated_at) VALUES (5, 'reporting_module', 1, 'Active ou désactive le module de rapports avancés', '2025-09-04 10:43:54', '2025-09-04 10:43:54');
-- feature_flags: 5 lignes insérées au total

-- ==================== DONNÉES TABLE: users ====================
-- 5 lignes à insérer

-- Insertion des données dans users
INSERT INTO users (id, username, email, password_hash, role, full_name, condo_unit, phone, is_active, created_at, last_login) VALUES (1, 'admin', 'admin@condos.com', 'a34cc6b0a57411071d7a6af751dbc010c8c54fe92f1260a28a0346827e08bd5c:ab335d935fa1d87595ac1f48943089ba', 'admin', 'Administrateur Principal', '', NULL, 1, '2025-08-29 23:35:44', NULL);
-- users: 1 ligne insérée au total

-- ==================== DONNÉES TABLE: projects ====================
-- 2 lignes à insérer

-- Insertion des données dans projects
INSERT INTO projects (id, project_id, name, address, building_area, land_area, construction_year, unit_count, constructor, creation_date, status, created_at, updated_at) VALUES (59, '9ff963ac-b55e-4219-aef4-8a7fe8ab389d', 'Résidence Le Mont-Royal', '5985 Av. Glengarry, Mont-Royal, QC H3R 0A5', 18000.0, 25000.0, 2018, 6, 'Construction ABC Inc', '2025-09-04T19:15:18.471224', 'ACTIVE', '2025-09-05 11:17:29', '2025-09-05 11:17:29');
INSERT INTO projects (id, project_id, name, address, building_area, land_area, construction_year, unit_count, constructor, creation_date, status, created_at, updated_at) VALUES (60, '375ee018-722d-4d67-983f-f3e12b672f94', 'Mont-Royal Plaza', '585 Av. Glengarry, Mont-Royal, QC H3R 0A5', 12000.0, 18000.0, 2025, 10, 'Construction ABC Inc', '2025-09-01T10:10:23.452066', 'ACTIVE', '2025-09-05 11:18:22', '2025-09-05 11:18:22');
-- projects: 2 lignes insérées au total

-- ==================== DONNÉES TABLE: units ====================
-- 16 lignes à insérer

-- Insertion des données dans units
INSERT INTO units (id, unit_number, project_id, area, condo_type, status, estimated_price, owner_name, calculated_monthly_fees, created_at, updated_at) VALUES (532, '101', '9ff963ac-b55e-4219-aef4-8a7fe8ab389d', 850.0, 'COMMERCIAL', 'none', NULL, 'Test101', '300.0', '2025-09-05 11:17:29', '2025-09-05 11:20:09');
INSERT INTO units (id, unit_number, project_id, area, condo_type, status, estimated_price, owner_name, calculated_monthly_fees, created_at, updated_at) VALUES (533, '102', '9ff963ac-b55e-4219-aef4-8a7fe8ab389d', 850.0, 'RESIDENTIAL', 'none', NULL, 'Test102', '300', '2025-09-05 11:17:29', '2025-09-05 11:17:29');
INSERT INTO units (id, unit_number, project_id, area, condo_type, status, estimated_price, owner_name, calculated_monthly_fees, created_at, updated_at) VALUES (534, '201', '9ff963ac-b55e-4219-aef4-8a7fe8ab389d', 850.0, 'RESIDENTIAL', 'none', NULL, 'Test201', '300', '2025-09-05 11:17:29', '2025-09-05 11:17:29');
INSERT INTO units (id, unit_number, project_id, area, condo_type, status, estimated_price, owner_name, calculated_monthly_fees, created_at, updated_at) VALUES (535, '202', '9ff963ac-b55e-4219-aef4-8a7fe8ab389d', 850.0, 'RESIDENTIAL', 'none', NULL, 'Test202', '300', '2025-09-05 11:17:29', '2025-09-05 11:17:29');
INSERT INTO units (id, unit_number, project_id, area, condo_type, status, estimated_price, owner_name, calculated_monthly_fees, created_at, updated_at) VALUES (536, '301', '9ff963ac-b55e-4219-aef4-8a7fe8ab389d', 850.0, 'RESIDENTIAL', 'none', NULL, 'Test301', '300', '2025-09-05 11:17:29', '2025-09-05 11:17:29');
INSERT INTO units (id, unit_number, project_id, area, condo_type, status, estimated_price, owner_name, calculated_monthly_fees, created_at, updated_at) VALUES (537, '302', '9ff963ac-b55e-4219-aef4-8a7fe8ab389d', 850.0, 'RESIDENTIAL', 'none', NULL, 'Test302', '300', '2025-09-05 11:17:29', '2025-09-05 11:17:29');
INSERT INTO units (id, unit_number, project_id, area, condo_type, status, estimated_price, owner_name, calculated_monthly_fees, created_at, updated_at) VALUES (538, '101', '375ee018-722d-4d67-983f-f3e12b672f94', 1500.0, 'COMMERCIAL', 'none', NULL, 'Test Owner', '300.0', '2025-09-05 11:18:22', '2025-09-05 11:18:22');
INSERT INTO units (id, unit_number, project_id, area, condo_type, status, estimated_price, owner_name, calculated_monthly_fees, created_at, updated_at) VALUES (539, '102', '375ee018-722d-4d67-983f-f3e12b672f94', 1100.0, 'RESIDENTIAL', 'none', NULL, 'Disponible', '300', '2025-09-05 11:18:22', '2025-09-05 11:20:46');
INSERT INTO units (id, unit_number, project_id, area, condo_type, status, estimated_price, owner_name, calculated_monthly_fees, created_at, updated_at) VALUES (540, 'UNIT-288', '375ee018-722d-4d67-983f-f3e12b672f94', 0.0, 'RESIDENTIAL', 'available', NULL, 'Disponible', NULL, '2025-09-05 11:18:22', '2025-09-05 11:18:22');
INSERT INTO units (id, unit_number, project_id, area, condo_type, status, estimated_price, owner_name, calculated_monthly_fees, created_at, updated_at) VALUES (541, 'UNIT-289', '375ee018-722d-4d67-983f-f3e12b672f94', 0.0, 'RESIDENTIAL', 'available', NULL, 'Disponible', NULL, '2025-09-05 11:18:22', '2025-09-05 11:18:22');
INSERT INTO units (id, unit_number, project_id, area, condo_type, status, estimated_price, owner_name, calculated_monthly_fees, created_at, updated_at) VALUES (542, 'UNIT-290', '375ee018-722d-4d67-983f-f3e12b672f94', 0.0, 'RESIDENTIAL', 'available', NULL, 'Disponible', NULL, '2025-09-05 11:18:22', '2025-09-05 11:18:22');
INSERT INTO units (id, unit_number, project_id, area, condo_type, status, estimated_price, owner_name, calculated_monthly_fees, created_at, updated_at) VALUES (543, 'UNIT-291', '375ee018-722d-4d67-983f-f3e12b672f94', 0.0, 'RESIDENTIAL', 'available', NULL, 'Disponible', NULL, '2025-09-05 11:18:22', '2025-09-05 11:18:22');
INSERT INTO units (id, unit_number, project_id, area, condo_type, status, estimated_price, owner_name, calculated_monthly_fees, created_at, updated_at) VALUES (544, 'UNIT-292', '375ee018-722d-4d67-983f-f3e12b672f94', 0.0, 'RESIDENTIAL', 'available', NULL, 'Disponible', NULL, '2025-09-05 11:18:22', '2025-09-05 11:18:22');
INSERT INTO units (id, unit_number, project_id, area, condo_type, status, estimated_price, owner_name, calculated_monthly_fees, created_at, updated_at) VALUES (545, 'UNIT-293', '375ee018-722d-4d67-983f-f3e12b672f94', 0.0, 'RESIDENTIAL', 'available', NULL, 'Disponible', NULL, '2025-09-05 11:18:22', '2025-09-05 11:18:22');
INSERT INTO units (id, unit_number, project_id, area, condo_type, status, estimated_price, owner_name, calculated_monthly_fees, created_at, updated_at) VALUES (546, 'UNIT-294', '375ee018-722d-4d67-983f-f3e12b672f94', 0.0, 'RESIDENTIAL', 'available', NULL, 'Disponible', NULL, '2025-09-05 11:18:22', '2025-09-05 11:18:22');
INSERT INTO units (id, unit_number, project_id, area, condo_type, status, estimated_price, owner_name, calculated_monthly_fees, created_at, updated_at) VALUES (547, 'UNIT-295', '375ee018-722d-4d67-983f-f3e12b672f94', 0.0, 'RESIDENTIAL', 'available', NULL, 'Disponible', NULL, '2025-09-05 11:18:22', '2025-09-05 11:18:22');
-- units: 16 lignes insérées au total

-- Table financial_records: Aucune donnée à insérer

-- Réactiver les clés étrangères
PRAGMA foreign_keys = ON;
COMMIT;

-- ==================== FIN MIGRATION DONNÉES ====================