-- Migration 002: Table Users pour Authentification
-- Création de la table des utilisateurs avec mots de passe chiffrés
-- Date: 2025-08-29
-- Description: Système d'authentification basé sur SQLite avec rôles

-- Table des utilisateurs
CREATE TABLE IF NOT EXISTS users (
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

-- Index pour optimiser les recherches fréquentes
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_users_condo_unit ON users(condo_unit);

-- Insertion de l'administrateur principal uniquement
-- Note: Hash généré avec User.hash_password() - mot de passe sécurisé
-- Ce hash est sécurisé avec salt aléatoire généré
INSERT OR IGNORE INTO users (username, email, password_hash, role, full_name, condo_unit, is_active) VALUES 
('admin', 'admin@condos.com', 'aa2dd5f3238db1eec58fbe4da8648b77f80af0da72b5c8fbeab333ea81ebdd4e:38962e22b63b896b9b3f60fa58b5543d', 'admin', 'Administrateur Principal', NULL, 1);
