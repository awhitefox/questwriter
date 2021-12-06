from questlib import *


def default_chapter() -> Chapter:
    c = Chapter('Новая глава')
    c.branches.insert(0, default_branch())
    c.branches[-1].segments.append(default_ending())
    return c


def default_branch() -> Branch:
    b = Branch('Новая ветвь')
    b.segments.append(default_segment(b.id))
    return b


def default_ending() -> Segment:
    return Segment('Новая концовка', has_options=False)


def default_segment(branch_id: str) -> Segment:
    s = Segment('Новый сегмент')
    s.options.append(default_option(branch_id, s.id))
    return s


def default_option(goto_branch_id: str, goto_segment_id: str) -> Option:
    goto = GotoDestination(goto_branch_id, goto_segment_id)
    return Option('Новая опция', goto)


def default_variable_definition(initial_value: T_VariableValue) -> VariableDefinition:
    return VariableDefinition('Новая переменная', initial_value)


def default_variable_operation(var: VariableDefinition) -> VariableOperation:
    return VariableOperation(var.id, OperationType.Set, var.initial_value)


def default_condition(var: VariableDefinition) -> Condition:
    return Condition(CompareTo.Constant, ComparisonType.Equal, var.id, var.initial_value)
