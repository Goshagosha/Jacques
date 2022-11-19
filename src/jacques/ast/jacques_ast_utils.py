import ast
from typing import List
from ..ast.jacques_ast import JAST, CodeJAST
from ..core.arguments import Pipe


class SubtreeBuilder:
    """Takes a list of CodeJAST nodes and reassembles it into a CodeJAST subtree.
    The nodes in the input list have ALL of their original children, but only the nodes in the list are included in the output tree."""

    def __init__(self):
        pass

    def build(self, reference_list: List[CodeJAST]):
        self.reference_list = reference_list
        root = self._find_root()
        return self._recursive_parse(root)

    def _find_root(self):
        root_codejast = self.reference_list[0]
        for each in self.reference_list:
            if each.depth < root_codejast.depth:
                root_codejast = each
        return root_codejast

    def _recursive_parse(self, node: JAST):
        new_node = None
        if node in self.reference_list:
            new_node = node.childfree_copy()
            for child in node.children:
                new_child = self._recursive_parse(child)
                if new_child != None:
                    new_node.add_child(new_child)
        return new_node


def clone_matched(target: CodeJAST, reference: CodeJAST) -> CodeJAST:
    """Takes a CodeJAST subtree from SubtreeBuilder, and a complete CodeJAST, and extracts matching subtree as a clone"""
    matched = True
    if target.command == reference.command:
        ref_child_dict = {r.command: r for r in reference.children}
        clone = target.childfree_copy()
        for child in target.children:
            if child.command in ref_child_dict.keys():
                child_match = clone_matched(child, ref_child_dict[child.command])
                if not child_match:
                    matched = False
                    break
                else:
                    clone.add_child(child_match)
            else:
                matched = False
                break
        return clone if matched else None


def extract_subtree_by_ref_as_ref_list(
    target: CodeJAST, reference: CodeJAST
) -> List[CodeJAST]:
    """Same as clone_matched, but extracts the match as a list with direct references in target

    Args:
        target (CodeJAST): _description_
        reference (CodeJAST): _description_

    Returns:
        List[CodeJAST]: _description_
    """
    matched = True
    if target.command == reference.command:
        ref_child_dict = {r.command: r for r in reference.children}
        list = [target]
        if ref_child_dict:
            for child in target.children:
                if child.command in ref_child_dict.keys():
                    child_match = extract_subtree_by_ref_as_ref_list(
                        child, ref_child_dict[child.command]
                    )
                    if not child_match:
                        matched = False
                        break
                    else:
                        list.extend(child_match)
                # else:
                #     matched = False
                #     break
        if matched:
            return list
    return []


class CodeExtractor(ast.NodeTransformer):
    """Takes a CodeJAST subtree and extracts proper AST subtree"""

    def __init__(self, jacques) -> None:
        self.jacques = jacques
        self.pipe_nodes = None
        super().__init__()

    def extract(self, root_code_jast: CodeJAST, pipe_nodes: List[CodeJAST]) -> ast.AST:
        self.asts: List[ast.AST] = [jast.code_ast for jast in root_code_jast]
        self.pipe_nodes: List[ast.AST] = [jast.code_ast for jast in pipe_nodes]
        return super().visit(root_code_jast.code_ast)

    def pipe(self, node):
        if node in self.pipe_nodes:
            return Pipe(placeholding_for=node)
        return self.generic_visit(node)

    def visit_Name(self, node: ast.Call):
        if isinstance(node.ctx, ast.Load) and (
            node.id in self.jacques.encountered_objects
        ):
            return self.pipe(node)
        else:
            return self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        return self.pipe(node)

    def visit_Assign(self, node: ast.Assign):
        return self.pipe(node)

    def visit_Subscript(self, node: ast.Subscript):
        return self.pipe(node)

    def generic_visit(self, node: ast.AST) -> ast.AST:
        if isinstance(node, Pipe):
            return None
        return super().generic_visit(node)
