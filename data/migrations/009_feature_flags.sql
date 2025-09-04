-- Migration 009: Système de Feature Flags
-- Objectif: Ajouter une table pour gérer les feature flags en base de données
-- Scope: Modules non-essentiels uniquement (finance, rapports, analytics)

-- Création de la table feature_flags
CREATE TABLE IF NOT EXISTS feature_flags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    flag_name TEXT UNIQUE NOT NULL,
    is_enabled BOOLEAN NOT NULL DEFAULT 1,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Insertion des feature flags pour les modules optionnels uniquement
INSERT OR IGNORE INTO feature_flags (flag_name, is_enabled, description) VALUES
('finance_module', 1, 'Active ou désactive le module finance complet'),
('finance_calculations', 1, 'Active ou désactive les calculs financiers avancés'),
('finance_reports', 1, 'Active ou désactive les rapports financiers détaillés'),
('analytics_module', 1, 'Active ou désactive le module d''analytics et statistiques'),
('reporting_module', 1, 'Active ou désactive le module de rapports avancés');

-- NOTE: Les modules de base (dashboard, projets, unités, utilisateurs) 
-- ne nécessitent PAS de feature flags car ils font partie du MVP minimum

-- Index pour optimiser les requêtes
CREATE INDEX IF NOT EXISTS idx_feature_flags_name ON feature_flags(flag_name);
CREATE INDEX IF NOT EXISTS idx_feature_flags_enabled ON feature_flags(is_enabled);
