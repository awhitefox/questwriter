from uuid import uuid4


def generate_new_chapter() -> dict:
    data = {
        'title': 'Новая глава',
        'branches': [
            generate_new_branch(),
            {
                'id': '@endings',
                'segments': [
                    {
                        'id': str(uuid4()),
                        'text': 'Новая концовка'
                    }
                ]
            }
        ]
    }
    # noinspection PyTypeChecker,PyUnresolvedReferences
    data['branches'][0]['segments'][0]['options'][0]['goto']['branch_id'] = data['branches'][0]['id']
    # noinspection PyTypeChecker,PyUnresolvedReferences
    data['branches'][0]['segments'][0]['options'][0]['goto']['segment_id'] = data['branches'][0]['segments'][0]['id']
    return data


def generate_new_branch() -> dict:
    return {
        'id': str(uuid4()),
        'title': 'Новая ветвь',
        'segments': [
            generate_new_segment()
        ]
    }


def generate_new_segment() -> dict:
    return {
        'id': str(uuid4()),
        'text': 'Новый сегмент',
        'options': [
            generate_new_option()
        ]
    }


def generate_new_option() -> dict:
    return {
        'text': 'Новая опция',
        'goto': {
            'branch_id': None,
            'segment_id': None
        }
    }
