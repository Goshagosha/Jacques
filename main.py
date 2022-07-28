from jacques.matcher import Matcher
from jacques.parser.dsl_parser import DslParser
from jacques.parser.new_python_parser import PythonParser
from jacques.problem_knowledge import ProblemKnowledge

import jacques.world_knowledge as world_knowledge


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
        self.matcher = Matcher(
            world_knowledge=self.world_knowledge,
            problem_knowledge=self.problem_knowledge,
        )

    def load_example_data(self, dsl_string, code_string):
        dsl_tree = self.dsl_parser.parse(dsl_string)
        code_tree = self.python_parser.parse(code_string)
        self.matcher.load_sample(dsl_tree, code_tree)
        print(self.matcher.next_most_probable_pairing())

    def load_example_file(self, path):
        dsl = None
        with open(path, "r") as file:
            next_line_is_code = False
            for line in file.readlines():
                if next_line_is_code:
                    self.load_example_data(dsl, line)
                    next_line_is_code = False
                    dsl = None
                elif line.startswith("##"):
                    dsl = line[3:]
                    next_line_is_code = True


dsl = "on data | drop columns 'Active', 'Country/Region' | select rows 'Confirmed' < 20 | group by 'Deaths' | union other_dataframe | join outer another_df on 'SNo' | sort by 'Recovered' descending | describe | show"
py = "print(pd.concat([data.drop(columns=['Active', 'Country/Region'])['Confirmed' < 20].groupby(['Deaths']), other_dataframe]).join(another_df, on=['SNo'], how='outer').sort_values(['Recovered'], axis='index', ascending=[False]).describe()) "
spark_py = "data.drop(['Active', 'Country/Region']).filter('Confirmed' < 20).groupBy(['Deaths']).unionByName(other_dataframe).join(another_df, on=['SNo'], how='outer').sort(['Recovered'], ascending=[False]).describe().show()"

j = Jacques(world_knowledge)

j.load_example_data(dsl, py)
j.matcher.code_family_header[0].samples[0].visualize(f"dsls/new_dsl")


# j.load_example_file("training_examples/spark/advanced.py")
