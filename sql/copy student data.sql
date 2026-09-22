WITH RECURSIVE n(i) AS (
    SELECT 1
    UNION ALL
    SELECT i + 1 FROM n WHERE i < 20
)
INSERT INTO students (
    name, affiliation, major, degree, about,
    interests, preferred_degree, preferred_field, photo_path
)
SELECT
    s.name || ' (test ' || n.i || ')',
    s.affiliation, s.major, s.degree, s.about,
    s.interests, s.preferred_degree, s.preferred_field, s.photo_path
FROM (SELECT * FROM students ORDER BY rowid DESC LIMIT 1) AS s,
     n;