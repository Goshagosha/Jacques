from jacques.matcher import Matcher
from jacques.parser.dsl_parser import DslParser
from jacques.parser.python_parser import PythonParser
from jacques.problem_knowledge import ProblemKnowledge

import jacques.world_knowledge as world_knowledge
from jacques.ruleset_synthesizer import generate_mock_rule as rule_synth


class Jacques:
    def __init__(self, world_knowledge, rule_synth):
        self.rule_synth = rule_synth
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
        self.matcher = Matcher(jacques=self)
        self.rule_set = None

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

    def infer_ruleset(self):
        self.rule_set = self.matcher.generate_rules()
        return self.rule_set


dsl = "on data | drop columns 'Active', 'Country/Region' | select rows 'Confirmed' < 20 | group by 'Deaths' | union other_dataframe | join outer another_df on 'SNo' | sort by 'Recovered' descending | describe | show"
py = "print(pd.concat([data.drop(columns=['Active', 'Country/Region'])['Confirmed' < 20].groupby(['Deaths']), other_dataframe]).join(another_df, on=['SNo'], how='outer').sort_values(['Recovered'], axis='index', ascending=[False]).describe()) "
spark_py = "data.drop(['Active', 'Country/Region']).filter('Confirmed' < 20).groupBy(['Deaths']).unionByName(other_dataframe).join(another_df, on=['SNo'], how='outer').sort(['Recovered'], ascending=[False]).describe().show()"

branched_py = 'data.join(other_df, on=["Confirmed"], how="left").withColumn("Active", "Confirmed" - "Deaths").agg(sum("Active").alias("Total Active"))'

j = Jacques(world_knowledge, rule_synth)

# j.load_example_file("training_examples/spark/no_logical_inference.py")
# ruleset = j.infer_ruleset()


t = j.python_parser.parse(py)
t.visualize("branched_tree")
