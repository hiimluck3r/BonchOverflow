CREATE TABLE questions(id SERIAL PRIMARY KEY, userid BIGINT, header VARCHAR, question VARCHAR, status BOOLEAN, solverid BIGINT, solution VARCHAR);

CREATE TABLE solutions(id SERIAL PRIMARY KEY, questionid INT, solverid BIGINT, solution VARCHAR);

CREATE TABLE banned(id SERIAL PRIMARY KEY, userid BIGINT, reason VARCHAR);

INSERT INTO solutions(questionid, solverid, solution) VALUES (0, 1, 'Решение не найдено');