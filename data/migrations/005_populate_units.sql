-- Migration 005: Initialisation des unités de base
-- Création des 55 unités de démonstration réparties sur les 4 projets
-- 
-- Ce script initialise la base de données avec les unités de base
-- pour les démonstrations et nouvelles instances du système.

-- Insérer les unités de base pour démonstration (uniquement si elles n'existent pas)

-- Projet 1: Centre-Ville Plaza (8 unités: P-001 à P-008)
INSERT OR IGNORE INTO units (unit_number, project_id, area, condo_type, status, estimated_price, monthly_fees_base) VALUES
('P-001', 'p1q2r3s4-t5u6-7890-abcd-123456789xyz', 200.0, 'parking', 'available', 25000.0, 75.0),
('P-002', 'p1q2r3s4-t5u6-7890-abcd-123456789xyz', 200.0, 'parking', 'available', 25000.0, 75.0),
('P-003', 'p1q2r3s4-t5u6-7890-abcd-123456789xyz', 200.0, 'parking', 'available', 25000.0, 75.0),
('P-004', 'p1q2r3s4-t5u6-7890-abcd-123456789xyz', 200.0, 'parking', 'available', 25000.0, 75.0),
('P-005', 'p1q2r3s4-t5u6-7890-abcd-123456789xyz', 200.0, 'parking', 'available', 25000.0, 75.0),
('P-006', 'p1q2r3s4-t5u6-7890-abcd-123456789xyz', 200.0, 'parking', 'available', 25000.0, 75.0),
('P-007', 'p1q2r3s4-t5u6-7890-abcd-123456789xyz', 200.0, 'parking', 'available', 25000.0, 75.0),
('P-008', 'p1q2r3s4-t5u6-7890-abcd-123456789xyz', 200.0, 'parking', 'available', 25000.0, 75.0);

-- Projet 2: Complexe Rivière (15 unités: C-001 à C-015)
INSERT INTO units (unit_number, project_id, area, condo_type, status, estimated_price, monthly_fees_base) VALUES
('C-001', 'x9y8z7w6-v5u4-3210-9876-543210abcdef', 850.0, 'residential', 'available', 285000.0, 450.0),
('C-002', 'x9y8z7w6-v5u4-3210-9876-543210abcdef', 750.0, 'residential', 'available', 255000.0, 400.0),
('C-003', 'x9y8z7w6-v5u4-3210-9876-543210abcdef', 900.0, 'residential', 'available', 310000.0, 480.0),
('C-004', 'x9y8z7w6-v5u4-3210-9876-543210abcdef', 800.0, 'residential', 'available', 275000.0, 430.0),
('C-005', 'x9y8z7w6-v5u4-3210-9876-543210abcdef', 1200.0, 'commercial', 'available', 450000.0, 680.0),
('C-006', 'x9y8z7w6-v5u4-3210-9876-543210abcdef', 850.0, 'residential', 'available', 285000.0, 450.0),
('C-007', 'x9y8z7w6-v5u4-3210-9876-543210abcdef', 750.0, 'residential', 'available', 255000.0, 400.0),
('C-008', 'x9y8z7w6-v5u4-3210-9876-543210abcdef', 900.0, 'residential', 'available', 310000.0, 480.0),
('C-009', 'x9y8z7w6-v5u4-3210-9876-543210abcdef', 800.0, 'residential', 'available', 275000.0, 430.0),
('C-010', 'x9y8z7w6-v5u4-3210-9876-543210abcdef', 1100.0, 'commercial', 'available', 420000.0, 650.0),
('C-011', 'x9y8z7w6-v5u4-3210-9876-543210abcdef', 850.0, 'residential', 'available', 285000.0, 450.0),
('C-012', 'x9y8z7w6-v5u4-3210-9876-543210abcdef', 750.0, 'residential', 'available', 255000.0, 400.0),
('C-013', 'x9y8z7w6-v5u4-3210-9876-543210abcdef', 900.0, 'residential', 'available', 310000.0, 480.0),
('C-014', 'x9y8z7w6-v5u4-3210-9876-543210abcdef', 800.0, 'residential', 'available', 275000.0, 430.0),
('C-015', 'x9y8z7w6-v5u4-3210-9876-543210abcdef', 1000.0, 'commercial', 'available', 380000.0, 600.0);

-- Projet 3: Résidence Les Érables (12 unités: R-001 à R-012)
INSERT INTO units (unit_number, project_id, area, condo_type, status, estimated_price, monthly_fees_base) VALUES
('R-001', 'f8c4dc0b-f1ce-4492-b15f-5ebaa3c018f5', 650.0, 'residential', 'available', 220000.0, 350.0),
('R-002', 'f8c4dc0b-f1ce-4492-b15f-5ebaa3c018f5', 750.0, 'residential', 'available', 255000.0, 400.0),
('R-003', 'f8c4dc0b-f1ce-4492-b15f-5ebaa3c018f5', 850.0, 'residential', 'available', 285000.0, 450.0),
('R-004', 'f8c4dc0b-f1ce-4492-b15f-5ebaa3c018f5', 950.0, 'residential', 'available', 320000.0, 500.0),
('R-005', 'f8c4dc0b-f1ce-4492-b15f-5ebaa3c018f5', 700.0, 'residential', 'available', 240000.0, 375.0),
('R-006', 'f8c4dc0b-f1ce-4492-b15f-5ebaa3c018f5', 800.0, 'residential', 'available', 275000.0, 430.0),
('R-007', 'f8c4dc0b-f1ce-4492-b15f-5ebaa3c018f5', 900.0, 'residential', 'available', 310000.0, 480.0),
('R-008', 'f8c4dc0b-f1ce-4492-b15f-5ebaa3c018f5', 650.0, 'residential', 'available', 220000.0, 350.0),
('R-009', 'f8c4dc0b-f1ce-4492-b15f-5ebaa3c018f5', 750.0, 'residential', 'available', 255000.0, 400.0),
('R-010', 'f8c4dc0b-f1ce-4492-b15f-5ebaa3c018f5', 850.0, 'residential', 'available', 285000.0, 450.0),
('R-011', 'f8c4dc0b-f1ce-4492-b15f-5ebaa3c018f5', 950.0, 'residential', 'available', 320000.0, 500.0),
('R-012', 'f8c4dc0b-f1ce-4492-b15f-5ebaa3c018f5', 700.0, 'residential', 'available', 240000.0, 375.0);

-- Projet 4: Tour Horizon (20 unités: T-001 à T-020)
INSERT INTO units (unit_number, project_id, area, condo_type, status, estimated_price, monthly_fees_base) VALUES
('T-001', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 1000.0, 'residential', 'available', 380000.0, 550.0),
('T-002', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 1100.0, 'residential', 'available', 420000.0, 600.0),
('T-003', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 1200.0, 'residential', 'available', 460000.0, 650.0),
('T-004', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 900.0, 'residential', 'available', 340000.0, 500.0),
('T-005', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 1000.0, 'residential', 'available', 380000.0, 550.0),
('T-006', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 1100.0, 'residential', 'available', 420000.0, 600.0),
('T-007', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 1200.0, 'residential', 'available', 460000.0, 650.0),
('T-008', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 900.0, 'residential', 'available', 340000.0, 500.0),
('T-009', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 1500.0, 'commercial', 'available', 650000.0, 850.0),
('T-010', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 1000.0, 'residential', 'available', 380000.0, 550.0),
('T-011', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 1100.0, 'residential', 'available', 420000.0, 600.0),
('T-012', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 1200.0, 'residential', 'available', 460000.0, 650.0),
('T-013', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 900.0, 'residential', 'available', 340000.0, 500.0),
('T-014', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 1000.0, 'residential', 'available', 380000.0, 550.0),
('T-015', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 1100.0, 'residential', 'available', 420000.0, 600.0),
('T-016', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 1200.0, 'residential', 'available', 460000.0, 650.0),
('T-017', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 900.0, 'residential', 'available', 340000.0, 500.0),
('T-018', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 1400.0, 'commercial', 'available', 580000.0, 800.0),
('T-019', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 1000.0, 'residential', 'available', 380000.0, 550.0),
('T-020', 'a1b2c3d4-e5f6-7890-abcd-ef1234567890', 1100.0, 'residential', 'available', 420000.0, 600.0);

-- Vérification de l'insertion des unités
SELECT 'Migration 005 terminée: ' || COUNT(*) || ' unités créées' as status FROM units;
SELECT 
    p.name, 
    p.unit_count as attendu, 
    COUNT(u.id) as reel,
    CASE WHEN p.unit_count = COUNT(u.id) THEN 'OK' ELSE 'ERREUR' END as statut
FROM projects p 
LEFT JOIN units u ON p.project_id = u.project_id 
GROUP BY p.project_id, p.name, p.unit_count;
