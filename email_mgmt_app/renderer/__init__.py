from pyramid.interfaces import IRenderer, IRendererFactory, IRendererInfo


#
#
# class HostRendererFactory(IRendererFactory):
#
#     def __call__(info):
#         return HostRenderer()
#
# class HostRenderer(IRenderer):
#     def __call__(value, system):
#         super().__call__(system)
from pyramid.renderers import get_renderer


class Renderer(IRenderer):
    def __call__(value, system):
        pass


class RendererFactory(IRendererFactory):
    def __call__(self, info: IRendererInfo):
        return Renderer()
