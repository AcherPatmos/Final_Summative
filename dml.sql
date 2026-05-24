USE campus_resource_db;
INSERT INTO Student (student_id, student_name, email) VALUES
('S001', 'Joseph Manu',  'j.manu@alustudent.com'),
('S002', 'Kwame Mensah', 'k.mensah@alustudent.com'),
('S003', 'Ama Owusu',  'a.owusu@alustudent.com'),
('S004', 'Kofi Boateng','k.boateng@alustudent.com'),
('S005', 'Abena Asante','a.asante@alustudent.com'),
('S006', 'Yaw Darko', 'y.darko@alustudent.com'),
('S007', 'Efua Amponsah', 'e.amponsah@alustudent.com');

INSERT INTO Resource (resource_id, resource_name, resource_type, quantity) VALUES
('R001', 'HP Laptop','tech tools', 5),
('R002', 'Scientific Calculator','stationery', 10),
('R003', 'Introduction to Algorithms', 'books',3),
('R004', 'USB Flash Drive','IT',20),
('R005', 'Whiteboard Marker Set','stationery', 50);

INSERT INTO BorrowingTransaction
    (transaction_id, student_id, resource_id, borrow_date, due_date, return_date, status)
VALUES
('T001', 'S001', 'R001', '2026-05-01', '2026-05-04', '2026-05-03', 'returned'),
('T002', 'S002', 'R002', '2026-05-05', '2026-05-08',  NULL, 'borrowed'),
('T003', 'S003', 'R003', '2026-05-06', '2026-05-09', '2026-05-08', 'returned'),
('T004', 'S004', 'R004', '2026-05-07', '2026-05-10',  NULL, 'borrowed'),
('T005', 'S005', 'R001', '2026-05-08', '2026-05-11', NULL, 'borrowed'),
('T006', 'S006', 'R005', '2026-05-09', '2026-05-12', NULL, 'borrowed'),
('T007', 'S007', 'R002', '2026-05-10', '2026-05-13', '2026-05-12', 'returned');

INSERT INTO BorrowingTransaction
    (transaction_id, student_id, resource_id, borrow_date, due_date, return_date, status)
VALUES
('T001', 'S001', 'R001', '2026-05-01', '2026-05-04', '2026-05-03', 'returned'),
('T002', 'S002', 'R002', '2026-05-05', '2026-05-08',  NULL,        'borrowed'),
('T003', 'S003', 'R003', '2026-05-06', '2026-05-09', '2026-05-08', 'returned'),
('T004', 'S004', 'R004', '2026-05-07', '2026-05-10',  NULL,        'borrowed'),
('T005', 'S005', 'R001', '2026-05-08', '2026-05-11',  NULL,        'borrowed'),
('T006', 'S006', 'R005', '2026-05-09', '2026-05-12',  NULL,        'borrowed'),
('T007', 'S007', 'R002', '2026-05-10', '2026-05-13', '2026-05-12', 'returned');

INSERT INTO Admin (admin_id, admin_name, email, role) VALUES
('A001', 'Yoovin Poorun', 'y.poorun@alueducation.com', 'Department Manager'),
('A002', 'Kwame Mensah',  'k.mensah@alueducation.com', 'Staff Member');

INSERT INTO AuditLog (log_id, resource_id, admin_id, changes_made, datetime) VALUES
('L001', 'R002', 'A001', 'Added 5 new books in the system',    '2026-05-17 09:00:00'),
('L002', 'R004', 'A002', 'Removed 5 computers from the system','2026-05-20 11:00:00'),
('L003', 'R001', 'A001', 'Updated HP Laptop quantity',         '2026-05-18 10:00:00');