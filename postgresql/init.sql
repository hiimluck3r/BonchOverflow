CREATE TABLE questions(id SERIAL PRIMARY KEY, userid INT, header VARCHAR, question VARCHAR, status BOOLEAN, solverid INT, solution VARCHAR);

CREATE TABLE solutions(id SERIAL PRIMARY KEY, questionid INT, solverid INT, solution VARCHAR);

CREATE TABLE banned(id SERIAL PRIMARY KEY, userid INT, reason VARCHAR);