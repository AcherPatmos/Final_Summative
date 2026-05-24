DROP DATABASE IF EXISTS campus_resource_db;
CREATE DATABASE campus_resource_db;
USE campus_resource_db;

CREATE TABLE Student (
    student_id   CHAR(4) NOT NULL,
    student_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL,
    CONSTRAINT pk_student  PRIMARY KEY (student_id),
    CONSTRAINT uq_student_email  UNIQUE (email),
    CONSTRAINT chk_student_email CHECK (email LIKE '%@alustudent.com')
);
CREATE TABLE Resource (
    resource_id   CHAR(4) NOT NULL,
    resource_name VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50)  NOT NULL,
    quantity  INT  NOT NULL DEFAULT 1,
    CONSTRAINT pk_resource  PRIMARY KEY (resource_id),
    CONSTRAINT chk_quantity CHECK (quantity >= 0)
);
CREATE TABLE BorrowingTransaction (
    transaction_id CHAR(4) NOT NULL,
    student_id     CHAR(4) NOT NULL,
    resource_id    CHAR(4) NOT NULL,
    borrow_date    DATE NOT NULL,
    due_date       DATE NOT NULL,
    return_date    DATE  NULL,
    status  VARCHAR(10) NOT NULL DEFAULT 'borrowed',
    CONSTRAINT pk_transaction  PRIMARY KEY (transaction_id),
    CONSTRAINT fk_trans_student FOREIGN KEY (student_id)
        REFERENCES Student(student_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_trans_resource  FOREIGN KEY (resource_id)
        REFERENCES Resource(resource_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_status  CHECK (status IN ('borrowed', 'returned')),
    CONSTRAINT chk_due_after_borrow CHECK (due_date >= borrow_date),
    CONSTRAINT chk_return_after_borrow CHECK (return_date IS NULL OR return_date >= borrow_date)
);
CREATE TABLE Admin (
    admin_id   CHAR(4)      NOT NULL,
    admin_name VARCHAR(100) NOT NULL,
    email      VARCHAR(150) NOT NULL,
    role       VARCHAR(50)  NOT NULL DEFAULT 'Staff Member',
    CONSTRAINT pk_admin        PRIMARY KEY (admin_id),
    CONSTRAINT uq_admin_email  UNIQUE      (email),
    CONSTRAINT chk_admin_email CHECK       (email LIKE '%@alueducation.com'),
    CONSTRAINT chk_admin_role  CHECK       (role IN ('Senior Administrator', 'Department Manager', 'Staff Member'))
);
CREATE TABLE AuditLog (
    log_id       CHAR(4)      NOT NULL,
    resource_id  CHAR(4)      NOT NULL,
    admin_id     CHAR(4)      NOT NULL,
    changes_made VARCHAR(300) NOT NULL,
    datetime     DATETIME     NOT NULL,
    CONSTRAINT pk_auditlog       PRIMARY KEY (log_id),
    CONSTRAINT fk_audit_resource FOREIGN KEY (resource_id)
        REFERENCES Resource(resource_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_audit_admin    FOREIGN KEY (admin_id)
        REFERENCES Admin(admin_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
);