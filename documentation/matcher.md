matcher.theory_matrix is a List[JastFamily] X List[JastFamily]

- Each tuple code-dsl is parsed into JAST
- We build sample_matrix and grade the probability of matching
- Then for each row in sample_matrix: for each column in row: find the row and column in theory_matrix, add the score values