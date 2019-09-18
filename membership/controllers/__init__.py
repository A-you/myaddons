from . import main
from . import my
from . import member_product
from . import member_service
from . import member_event
from . import member_desire
from types import MethodType


from odoo.http import root, JsonRequest, HttpRequest


def get_request(self, httprequest):
    if 'User-Agent' in httprequest.headers and 'MicroMessenger' in httprequest.headers['User-Agent']:
        return HttpRequest(httprequest)
    if httprequest.args.get('jsonp'):
        return JsonRequest(httprequest)
    if httprequest.mimetype in ("application/json", "application/json-rpc"):
        return JsonRequest(httprequest)
    else:
        return HttpRequest(httprequest)

root.get_request = MethodType(get_request, root)
