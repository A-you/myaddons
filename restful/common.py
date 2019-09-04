"""Common methods"""
import ast
import json
import werkzeug.wrappers
from datetime import date, datetime


class CJsonEncoder(json.JSONEncoder):

    def default(self, obj):
        # 不是bool 但是为false，则返回空
        if not isinstance(obj, bool) and not obj:
            return None
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, bytes):
            return str(obj, encoding='utf-8');
        else:
            return json.JSONEncoder.default(self, obj)


def valid_response(data, status=200):
    """Valid Response
    This will be return when the http request was successfully processed."""
    data = {
        'count': len(data),
        'data': data
    }
    return werkzeug.wrappers.Response(
        status=status,
        content_type='application/json; charset=utf-8',
        response=json.dumps(data, cls=CJsonEncoder),
    )


def invalid_response(typ, message=None, status=400):
    """Invalid Response
    This will be the return value whenever the server runs into an error
    either from the client or the server."""
    return werkzeug.wrappers.Response(
        status=status,
        content_type='application/json; charset=utf-8',
        response=json.dumps({
            'type': typ,
            'message': message if message else 'wrong arguments (missing validation)',
        }),
    )


def extract_arguments(payload, offset=0, limit=0, order=None):
    """
    增加分页功能，传入page和limit（可选,默认10条）即可
    :param payload:
    :param offset:
    :param limit:
    :param order:
    :return:
    """
    fields, domain = [], []
    if payload.get('domain'):
        domain += ast.literal_eval(payload.get('domain'))
    if payload.get('fields'):
        fields += ast.literal_eval(payload.get('fields'))
    if payload.get('offset'):
        offset = int(payload['offset'])
    if payload.get('limit'):
        limit = int(payload['limit'])
    if payload.get('order'):
        order = payload.get('order')
    # 如果存在分页，则设置分页offset
    page = payload.get('page')
    if page and page.isnumeric():
        if not limit:
            limit = 10  # 如果不存在limit，则默认每页10条
        offset = int(page) * limit
    return [domain, fields, offset, limit, order]
