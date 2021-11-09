from uuid import uuid4
from questlib import *


def generate_new_chapter() -> Chapter:
    c = Chapter()
    c.title = 'Новая глава'

    b0 = generate_new_branch()

    be = Branch()
    be.id = '@endings'
    s = Segment()
    s.id = str(uuid4())
    s.text = 'Новая концовка'
    be.segments = [s]

    c.branches = [b0, be]

    b0.segments[0].options[0].goto.branch_id = b0.id
    b0.segments[0].options[0].goto.segment_id = b0.segments[0].id

    return c


def generate_new_branch() -> Branch:
    b = Branch()
    b.id = str(uuid4())
    b.title = 'Новая ветвь'
    b.segments = [generate_new_segment()]
    return b


def generate_new_segment() -> Segment:
    s = Segment()
    s.id = str(uuid4())
    s.text = 'Новый сегмент'
    s.options = [generate_new_option()]
    return s


def generate_new_option() -> Option:
    o = Option()
    o.text = 'Новая опция'
    o.goto = GotoDestination()
    return o
