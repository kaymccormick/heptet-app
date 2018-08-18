from pyramid.view import notfound_view_config
from email_mgmt_app.util import munge_dict


@notfound_view_config(renderer='../templates/404.jinja2')
def notfound_view(request):
    request.response.status = 404
    return munge_dict(request, {})
