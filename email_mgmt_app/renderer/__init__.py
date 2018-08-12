from pyramid.interfaces import IRenderer, IRendererFactory
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


class Renderer(IRenderer):
    def __call__(value, system):
        pass

class RendererFactory(IRendererFactory):
    def __call__(info):
        return Renderer()
