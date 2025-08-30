-- Migration 001: Schéma Initial
-- Création des tables principales pour le système de gestion de condos
-- Date: 2025-08-28
-- Description: Tables de base pour condos, résidents et enregistrements financiers

-- Table des condos (unités)
CREATE TABLE IF NOT EXISTS condos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_number TEXT NOT NULL UNIQUE,
    owner_name TEXT NOT NULL,
    square_feet REAL NOT NULL CHECK(square_feet > 0),
    condo_type TEXT NOT NULL DEFAULT 'residential',
    status TEXT NOT NULL DEFAULT 'active',
    purchase_date TEXT,  -- Format ISO 8601
    monthly_fees_base DECIMAL(10,2),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    
    -- Contraintes
    CONSTRAINT chk_condo_type CHECK (condo_type IN ('residential', 'commercial', 'parking', 'storage')),
    CONSTRAINT chk_status CHECK (status IN ('active', 'inactive', 'maintenance', 'sold')),
    CONSTRAINT chk_unit_number_format CHECK (length(unit_number) <= 10 AND trim(unit_number) != '')
);

-- Table des résidents (propriétaires et locataires)
CREATE TABLE IF NOT EXISTS residents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    condo_id INTEGER NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    resident_type TEXT NOT NULL DEFAULT 'owner',
    move_in_date TEXT,  -- Format ISO 8601
    move_out_date TEXT, -- Format ISO 8601
    is_primary BOOLEAN NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    
    -- Clés étrangères
    FOREIGN KEY (condo_id) REFERENCES condos(id) ON DELETE CASCADE,
    
    -- Contraintes
    CONSTRAINT chk_resident_type CHECK (resident_type IN ('owner', 'tenant', 'contact')),
    CONSTRAINT chk_names_not_empty CHECK (trim(first_name) != '' AND trim(last_name) != ''),
    CONSTRAINT chk_email_format CHECK (email IS NULL OR email LIKE '%@%'),
    CONSTRAINT chk_move_dates CHECK (move_out_date IS NULL OR move_in_date IS NULL OR move_in_date <= move_out_date)
);

-- Table des enregistrements financiers
CREATE TABLE IF NOT EXISTS financial_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    condo_id INTEGER NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    record_type TEXT NOT NULL DEFAULT 'monthly_fee',
    calculation_method TEXT NOT NULL DEFAULT 'standard',
    calculation_date TEXT NOT NULL,  -- Format ISO 8601
    due_date TEXT,  -- Format ISO 8601
    paid_date TEXT, -- Format ISO 8601
    status TEXT NOT NULL DEFAULT 'pending',
    details TEXT,  -- JSON avec détails du calcul
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    
    -- Clés étrangères
    FOREIGN KEY (condo_id) REFERENCES condos(id) ON DELETE CASCADE,
    
    -- Contraintes
    CONSTRAINT chk_amount_positive CHECK (amount >= 0),
    CONSTRAINT chk_record_type CHECK (record_type IN ('monthly_fee', 'special_assessment', 'penalty', 'refund')),
    CONSTRAINT chk_calculation_method CHECK (calculation_method IN ('standard', 'progressive', 'flat_rate', 'custom')),
    CONSTRAINT chk_financial_status CHECK (status IN ('pending', 'paid', 'overdue', 'cancelled'))
);

-- Table de configuration du système
CREATE TABLE IF NOT EXISTS system_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_key TEXT NOT NULL UNIQUE,
    config_value TEXT NOT NULL,
    config_type TEXT NOT NULL DEFAULT 'string',
    description TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    
    -- Contraintes
    CONSTRAINT chk_config_type CHECK (config_type IN ('string', 'number', 'boolean', 'json'))
);

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_condos_unit_number ON condos(unit_number);
CREATE INDEX IF NOT EXISTS idx_condos_status ON condos(status);
CREATE INDEX IF NOT EXISTS idx_condos_type ON condos(condo_type);
CREATE INDEX IF NOT EXISTS idx_residents_condo_id ON residents(condo_id);
CREATE INDEX IF NOT EXISTS idx_residents_type ON residents(resident_type);
CREATE INDEX IF NOT EXISTS idx_financial_records_condo_id ON financial_records(condo_id);
CREATE INDEX IF NOT EXISTS idx_financial_records_status ON financial_records(status);
CREATE INDEX IF NOT EXISTS idx_financial_records_calculation_date ON financial_records(calculation_date);
CREATE INDEX IF NOT EXISTS idx_system_config_key ON system_config(config_key);

-- Triggers pour mettre à jour updated_at automatiquement
CREATE TRIGGER IF NOT EXISTS trigger_condos_updated_at 
    AFTER UPDATE ON condos
    FOR EACH ROW
BEGIN
    UPDATE condos SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trigger_residents_updated_at 
    AFTER UPDATE ON residents
    FOR EACH ROW
BEGIN
    UPDATE residents SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trigger_financial_records_updated_at 
    AFTER UPDATE ON financial_records
    FOR EACH ROW
BEGIN
    UPDATE financial_records SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trigger_system_config_updated_at 
    AFTER UPDATE ON system_config
    FOR EACH ROW
BEGIN
    UPDATE system_config SET updated_at = datetime('now') WHERE id = NEW.id;
END;

-- Insérer configuration de base
INSERT OR IGNORE INTO system_config (config_key, config_value, config_type, description) VALUES
('app_version', '1.0.0', 'string', 'Version de l application'),
('schema_version', '001', 'string', 'Version du schéma de base de données'),
('default_rate_residential', '0.45', 'number', 'Taux par pied carré pour unités résidentielles'),
('default_rate_commercial', '0.60', 'number', 'Taux par pied carré pour unités commerciales'),
('default_rate_parking', '0.15', 'number', 'Taux par pied carré pour stationnements'),
('default_rate_storage', '0.25', 'number', 'Taux par pied carré pour espaces de rangement'),
('currency', 'CAD', 'string', 'Devise utilisée pour les calculs');

-- Données de test (optionnel, pour développement)
INSERT OR IGNORE INTO condos (unit_number, owner_name, square_feet, condo_type, status) VALUES
('A-101', 'Jean Dupont', 850.0, 'residential', 'active'),
('A-102', 'Marie Tremblay', 950.0, 'residential', 'active'),
('B-001', 'Entreprise ABC Inc.', 1200.0, 'commercial', 'active'),
('P-001', 'Pierre Martin', 150.0, 'parking', 'active'),
('S-001', 'Louise Gagnon', 100.0, 'storage', 'active');

-- Résidents correspondants
INSERT OR IGNORE INTO residents (condo_id, first_name, last_name, email, resident_type, is_primary) VALUES
(1, 'Jean', 'Dupont', 'jean.dupont@email.com', 'owner', 1),
(2, 'Marie', 'Tremblay', 'marie.tremblay@email.com', 'owner', 1),
(3, 'Robert', 'Entreprise', 'contact@entrepriseabc.com', 'owner', 1),
(4, 'Pierre', 'Martin', 'pierre.martin@email.com', 'owner', 1),
(5, 'Louise', 'Gagnon', 'louise.gagnon@email.com', 'owner', 1);

-- Validation finale
PRAGMA foreign_key_check;
PRAGMA integrity_check;
