
CREATE DATABASE library_db;
USE library_db;

CREATE TABLE  books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    author VARCHAR(100) NOT NULL,
    category VARCHAR(60) NOT NULL
) ;

CREATE TABLE members (
    member_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(150) NOT NULL 
) ;

CREATE TABLE  borrowings (
    loan_id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    member_id INT NOT NULL,
    borrowed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    returned_at DATETIME NULL,
    CONSTRAINT fk_borrowings_book FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE RESTRICT,
    CONSTRAINT fk_borrowings_member FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE RESTRICT
) ;

INSERT INTO books values (NULL,'Python Basics', 'A. Smith', 'Programming');

INSERT INTO books values (NULL,'Database Design', 'M. Brown', 'Computing');

INSERT INTO members values (NULL,'Sara Ahmed', 'sara@example.com');

INSERT INTO members values (NULL,'Noor Ali', 'noor@example.com');
