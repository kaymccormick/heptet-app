import abc
import logging
from typing import AnyStr, Dict

from lxml import html

from interfaces import INamespaceStore
from impl import NamespaceStore

logger = logging.getLogger(__name__)


class IMappingTarget(metaclass=abc.ABCMeta):
    pass


# The caption can be associated with a specific form control, either using the for attribute, or by putting the form
# control inside the label element itself.


class MyHtmlElement:
    def __init__(self, name: AnyStr, attr: dict = {}, template=None):
        self._element = html.Element(name, attr)
        self._prepared = False
        self._template = template

    def as_html(self):
        if self._template:
            pass
        else:
            self.prepare_element()
            return html.tostring(self.element, encoding='unicode')

    def prepare_element(self):
        pass

    @property
    def element(self):
        return self._element


class DivElement(MyHtmlElement):
    pass


class FormElement(MyHtmlElement):
    def __init__(self, name: AnyStr, attr: dict = {}):
        super().__init__(name, attr)


class FormControl(FormElement):
    def __init__(self, name: AnyStr, attr: dict = {}):
        super().__init__(name, attr)


class FormOptionElement(FormElement):
    def __init__(self, content, value):
        attrs = {}
        if value is not None:
            attrs['value'] = str(value)
        super().__init__('option', attrs)
        self.element.text = content


class FormButton(FormControl):
    def __init__(self, name: AnyStr = 'button', attr: dict = {}):
        super().__init__(name, attr)


# this does not necessarily mean 'input' tags only
class FormInputElement(FormControl):
    pass


class FormTextInputElement(FormInputElement):
    def __init__(self, attr: dict = {}):
        super().__init__('input', {'type': 'text', **attr})


class FormSelect(FormInputElement):
    def __init__(self, name: AnyStr, id: AnyStr, options=[], attr: dict = {}):
        super().__init__('select', {**attr, 'name': name, 'id': id})
        self._name = name
        self._id = id
        self._options = options

    def prepare_element(self):
        super().prepare_element()
        assert not self._prepared
        for option in self._options:
            option.prepare_element()
            self.element.append(option.element)
        self._prepared = True


class FormLabel(FormElement):
    def __init__(self, form_control: FormControl, label_contents, contains_form: bool = False, attr=None) -> None:
        super().__init__('label', attr)
        self._form_control = form_control
        self._contains_form = contains_form
        self.element.append(html.fromstring(label_contents))
        pass

    def prepare_element(self):
        assert not self._prepared
        super().prepare_element()
        # this cant be done more than once!!
        if self.contains_form:
            self.element.append(self.form_control.element)
        else:
            self.element.set('for', self.form_control.element.get('id'))

        self._prepared = True

    @property
    def form_control(self) -> FormControl:
        return self._form_control

    @property
    def contains_form(self) -> bool:
        return self._contains_form

    @property
    def attrs(self) -> Dict[AnyStr, AnyStr]:
        attrs = {}
        if not self.contains_form:
            attrs['for'] = self.form_control.id
        return {**self.attrs, **attrs}


class FormVariableMapping:
    def __init__(self, form_var: 'FormVariable',
                 target: IMappingTarget):
        self._form_var = form_var
        self._target = target

    @property
    def form_var(self) -> 'FormVariable':
        return self._form_var


class FormVariable:
    def __init__(self, name, id):
        self._name = name
        self._id = id

    @property
    def name(self) -> AnyStr:
        return self._name

    @name.setter
    def name(self, new: AnyStr) -> None:
        self._name = new

    @property
    def id(self) -> AnyStr:
        return self._id

    @id.setter
    def id(self, new: AnyStr) -> None:
        self.id = new


class Form(FormElement):
    def __init__(
            self,
            namespace_id, # this is used to make a namespace if not provided? messy!! what do we pass here ?!?!
            root_namespace,
            namespace: NamespaceStore = None,
            outer_form=False) -> None:
        name = 'div'
        if outer_form:
            name = 'form'

        super().__init__(name)
        # assert '.' not in namespace_id, "namespace_id %s should not contain ." % namespace_id
        self._outer_form = outer_form
        self._variables = {}
        self._labels = []
        self._mapper_infos = {}

        assert root_namespace is not None
        self._root_namespace = root_namespace
        self._form_namespace = self._root_namespace.get_namespace('form', True)
        if namespace is None:
            logger.warning("making namespace in form namepsace %s", namespace_id)
            self._namespace = self._form_namespace.make_namespace(namespace_id)
        else:
            self._namespace = namespace

    def get_html_id(self, html_id, *args, **kwargs):
        return self._namespace.get_namespace(html_id)

    def get_html_form_name(self, name, *args, **kwargs):
        return self._namespace.get_namespace(name)

    @property
    def name_store(self) -> INamespaceStore:
        return self._name_store

    @property
    def namespace(self) -> INamespaceStore:
        return self._namespace

    @property
    def namespace_id(self):
        return self._namespace_id


class ProcessingUnit:
    pass
