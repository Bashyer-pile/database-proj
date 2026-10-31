
CREATE DATABASE library_db;
USE library_db;

CREATE TABLE books (
    book_id INT AUTO_INCREMENT,
    title VARCHAR(150) NOT NULL,
    author VARCHAR(100) NOT NULL,
    category VARCHAR(60) NOT NULL,
    PRIMARY KEY (book_id)
);

CREATE TABLE members (
    member_id INT AUTO_INCREMENT,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    PRIMARY KEY (member_id)
);

CREATE TABLE borrowings (
    loan_id INT AUTO_INCREMENT,
    book_id INT NOT NULL,
    member_id INT NOT NULL,
    borrowed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    returned_at DATETIME NULL,
    PRIMARY KEY (loan_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id) ,
    FOREIGN KEY (member_id) REFERENCES members(member_id) 
);


INSERT INTO books (title, author, category)
VALUES ('Python Basics', 'A. Smith', 'Programming');

INSERT INTO books (title, author, category)
VALUES ('Database Design', 'M. Brown', 'Computing');

INSERT INTO members (full_name, email)
VALUES ('Sara Ahmed', 'sara@example.com');

INSERT INTO members (full_name, email)
VALUES ('Noor Ali', 'noor@example.com');


