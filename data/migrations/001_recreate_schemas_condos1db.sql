-- =====================================================
-- MIGRATION AUTOMATIQUE - SCHÉMAS DE BASE DE DONNÉES
-- =====================================================
-- Généré automatiquement le: 2025-09-05 15:54:59
-- Source: data\condos1.db

-- Configuration SQLite
PRAGMA foreign_keys = ON;

-- Table: system_config
CREATE TABLE system_config (
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

-- Table: feature_flags
CREATE TABLE feature_flags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    flag_name TEXT UNIQUE NOT NULL,
    is_enabled BOOLEAN NOT NULL DEFAULT 1,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table: projects
CREATE TABLE "projects" (
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

-- Table: units
CREATE TABLE units (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_number TEXT NOT NULL,
    project_id TEXT NOT NULL,
    area REAL,
    condo_type TEXT,
    status TEXT DEFAULT 'active',
    estimated_price REAL,
    owner_name TEXT,
    calculated_monthly_fees TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
);

-- Table: users
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    full_name TEXT NOT NULL,
    condo_unit TEXT,
    phone TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    last_login TEXT,
    
    -- Contraintes de validation
    CONSTRAINT chk_role CHECK (role IN ('admin', 'resident', 'guest')),
    CONSTRAINT chk_username_length CHECK (length(trim(username)) >= 3),
    CONSTRAINT chk_email_format CHECK (email LIKE '%@%'),
    CONSTRAINT chk_full_name_length CHECK (length(trim(full_name)) >= 2),
    CONSTRAINT chk_password_hash_not_empty CHECK (length(trim(password_hash)) > 0)
);

-- Table: financial_records
CREATE TABLE financial_records (
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

-- ==================== CRÉATION DES INDEX ====================
-- Index: idx_feature_flags_enabled
CREATE INDEX idx_feature_flags_enabled ON feature_flags(is_enabled);

-- Index: idx_feature_flags_name
CREATE INDEX idx_feature_flags_name ON feature_flags(flag_name);

-- Index: idx_financial_records_calculation_date
CREATE INDEX idx_financial_records_calculation_date ON financial_records(calculation_date);

-- Index: idx_financial_records_condo_id
CREATE INDEX idx_financial_records_condo_id ON financial_records(condo_id);

-- Index: idx_financial_records_status
CREATE INDEX idx_financial_records_status ON financial_records(status);

-- Index: idx_projects_building_area
CREATE INDEX idx_projects_building_area ON projects(building_area);

-- Index: idx_projects_land_area
CREATE INDEX idx_projects_land_area ON projects(land_area);

-- Index: idx_projects_project_id
CREATE INDEX idx_projects_project_id ON projects(project_id);

-- Index: idx_projects_status
CREATE INDEX idx_projects_status ON projects(status);

-- Index: idx_system_config_key
CREATE INDEX idx_system_config_key ON system_config(config_key);

-- Index: idx_units_project_id
CREATE INDEX idx_units_project_id ON units(project_id);

-- Index: idx_units_status
CREATE INDEX idx_units_status ON units(status);

-- Index: idx_units_unit_number
CREATE INDEX idx_units_unit_number ON units(unit_number);

-- Index: idx_users_active
CREATE INDEX idx_users_active ON users(is_active);

-- Index: idx_users_condo_unit
CREATE INDEX idx_users_condo_unit ON users(condo_unit);

-- Index: idx_users_email
CREATE INDEX idx_users_email ON users(email);

-- Index: idx_users_role
CREATE INDEX idx_users_role ON users(role);

-- Index: idx_users_username
CREATE INDEX idx_users_username ON users(username);

-- ==================== CRÉATION DES TRIGGERS ====================
-- Trigger: trigger_financial_records_updated_at
CREATE TRIGGER trigger_financial_records_updated_at 
    AFTER UPDATE ON financial_records
    FOR EACH ROW
BEGIN
    UPDATE financial_records SET updated_at = datetime('now') WHERE id = NEW.id;
END;

-- Trigger: trigger_system_config_updated_at
CREATE TRIGGER trigger_system_config_updated_at 
    AFTER UPDATE ON system_config
    FOR EACH ROW
BEGIN
    UPDATE system_config SET updated_at = datetime('now') WHERE id = NEW.id;
END;

-- Trigger: update_projects_timestamp
CREATE TRIGGER update_projects_timestamp 
    AFTER UPDATE ON projects
    FOR EACH ROW
BEGIN
    UPDATE projects SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Trigger: update_units_timestamp
CREATE TRIGGER update_units_timestamp 
    AFTER UPDATE ON units
    FOR EACH ROW
BEGIN
    UPDATE units SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- ==================== FIN MIGRATION SCHÉMAS ====================