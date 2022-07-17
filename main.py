from jacques.parser.dsl_parser import DslParser
from jacques.parser.python_parser import PythonParser
from jacques.problem_knowledge import ProblemKnowledge

import jacques.world_knowledge as wk


class Jacques:
    def __init__(self, world_knowledge):
        self.world_knowledge = world_knowledge
        self.problem_knowledge = ProblemKnowledge()
        self.dsl_parser = DslParser(
            world_knowledge=self.world_knowledge,
            problem_knowledge=self.problem_knowledge,
        )
        self.python_parser = PythonParser(
            world_knowledge=self.world_knowledge,
            problem_knowledge=self.problem_knowledge,
        )


dsl = "on data | drop columns 'Active', 'Country/Region' | select rows 'Confirmed' < 20 | group by 'Deaths' | union other_dataframe | join outer another_df on 'SNo' | sort by 'Recovered' descending | describe | show"
py = "print(pd.concat([data.drop(columns=['Active', 'Country/Region'])['Confirmed' < 20].groupby(['Deaths']), other_dataframe]).join(another_df, on=['SNo'], how='outer').sort_values(['Recovered'], axis='index', ascending=[False]).describe()) "
spark_py = "data.drop(['Active', 'Country/Region']).filter('Confirmed' < 20).groupBy(['Deaths']).unionByName(other_dataframe).join(another_df, on=['SNo'], how='outer').sort(['Recovered'], ascending=[False]).describe().show()"

j = Jacques(wk)
dsl_tree = j.dsl_parser.parse(dsl)
py_tree = j.python_parser.parse(spark_py)

py_tree.visualize("spark")
