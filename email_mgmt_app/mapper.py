from pyramid.interfaces import IViewMapper, IViewMapperFactory
from pyramid.viewderivers import DefaultViewMapper
from zope.interface import implementer, provider


@implementer(IViewMapper)
@provider(IViewMapperFactory)
class MyViewMapper(DefaultViewMapper):
    pass
