from typing import List, Tuple
import numpy as np
from jacques.j_ast import JastFamily
from jacques.utils import gaussian
from sklearn.preprocessing import normalize


class Matcher:
    def __init__(self, jacques):
        self.world_knowledge = jacques.world_knowledge
        self.problem_knowledge = jacques.problem_knowledge
        self.rule_synth = jacques.rule_synth
        self.dsl_family_header: List[JastFamily] = []
        self.code_family_header: List[JastFamily] = []
        self.DEPTH_REWARD = 5
        self.theory_matrix = np.empty(shape=(0, 0))

    def generate_rules(self):
        result = []
        to_align = min(len(self.dsl_family_header), len(self.code_family_header))
        while to_align > 0:
            i, j = self.next_most_probable_pairing()
            dsl_jast = self.dsl_family_header[i].samples[0]
            code_jast = self.code_family_header[j].samples[0]
            result.append(self.rule_synth(dsl_jast, code_jast))

            self.theory_matrix[i, :] = 0
            self.theory_matrix[:, j] = 0
            to_align -= 1
        return result

    def put_dsl_jast_into_family(self, jast) -> int:
        for i, jast_family in enumerate(self.dsl_family_header):
            if jast_family.command == jast.command:
                if jast not in jast_family.samples:
                    jast_family.append_sample(jast)
                return i
        new_family = JastFamily(from_jast=jast)
        self.dsl_family_header.append(new_family)
        self.theory_matrix = np.pad(
            self.theory_matrix, [(0, 1), (0, 0)], mode="constant", constant_values=0
        )
        return len(self.dsl_family_header) - 1

    def put_code_jast_into_family(self, jast) -> int:
        for i, jast_family in enumerate(self.code_family_header):
            if jast_family.command == jast.command:
                if jast not in jast_family.samples:
                    jast_family.append_sample(jast)
                return i
        new_family = JastFamily(from_jast=jast)
        self.code_family_header.append(new_family)
        self.theory_matrix = np.pad(
            self.theory_matrix, [(0, 0), (0, 1)], mode="constant", constant_values=0
        )
        return len(self.code_family_header) - 1

    def load_sample(self, dsl_jast, code_jast) -> None:
        dsl_header = []
        code_header = []
        while dsl_jast != None:
            dsl_header.append(dsl_jast)
            dsl_jast = dsl_jast.child

        while code_jast != None:
            code_header.append(code_jast)
            code_jast = code_jast.child

        x = len(dsl_header)
        y = len(code_header)

        for i, dsl_jast in enumerate(dsl_header):
            in_dsl_family_header_at = self.put_dsl_jast_into_family(dsl_jast)
            for j, code_jast in enumerate(code_header):
                in_code_family_header_at = self.put_code_jast_into_family(code_jast)

                # reward matching depth:
                deviation_from_diagonal = abs(j - y / x * i)
                self.theory_matrix[
                    in_dsl_family_header_at, in_code_family_header_at
                ] += int(self.DEPTH_REWARD * gaussian(deviation_from_diagonal))
                self.theory_matrix[
                    in_dsl_family_header_at, in_code_family_header_at
                ] += dsl_jast.compare(code_jast)

    def _normalized_matrix(self):
        hnorm = normalize(self.theory_matrix, axis=1, norm="l1")
        vnorm = normalize(self.theory_matrix, axis=0, norm="l1")
        result = hnorm + vnorm
        return result

    def next_most_probable_pairing(self) -> Tuple[int, int]:
        norm_matrix = self._normalized_matrix()
        indices = np.where(norm_matrix == np.amax(norm_matrix))
        i, j = indices[0][0], indices[1][0]
        most_probable_rating = norm_matrix[i, j]
        row_contender = 0
        column_contender = 0
        if len(norm_matrix[i]) > 1:
            row_contender_j = np.argsort(norm_matrix[i])[-2]
            row_contender = norm_matrix[i, row_contender_j]
        if len(norm_matrix[:, j]) > 1:
            column_contender_i = np.argsort(norm_matrix[:, j])[-2]
            column_contender = norm_matrix[column_contender_i, j]
        if row_contender > column_contender:
            if (
                row_contender / most_probable_rating
                > self.world_knowledge.INCONFIDENCE_THRESHOLD
            ):
                print(f"CONTENDER AT {i}:{row_contender_j} with {row_contender}")
        elif (
            column_contender / most_probable_rating
            > self.world_knowledge.INCONFIDENCE_THRESHOLD
        ):
            print(f"CONTENDER AT {column_contender_i}:{j} with {column_contender}")

        return i, j
