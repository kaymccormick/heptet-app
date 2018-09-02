from pyramid.interfaces import IViewMapper, IViewMapperFactory
from pyramid.viewderivers import DefaultViewMapper
from zope.interface import implementer, provider

# unimplemented view mapper

@implementer(IViewMapper)
@provider(IViewMapperFactory)
class MyViewMapper(DefaultViewMapper):
    pass
