####################################################################################################
#
# InSpice - A Spice Package for Python
# Copyright (C) 2021 Fabrice Salvaire
# Copyright (C) 2025 Innovoltive
# Modified by Innovoltive on April 18, 2025
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
####################################################################################################

__all__ = [
    'AnyPinElement',
    'DipoleElement',
    'Element',
    # 'ElementParameterMetaClass',
    'FixedPinElement',
    'NPinElement',
    'OptionalPin',
    'Pin',
    'PinDefinition',
    'TwoPortElement',
]

####################################################################################################

from collections import OrderedDict
import logging

####################################################################################################

from .ElementParameter import (
    ParameterDescriptor,
    PositionalElementParameter,
    FlagParameter, KeyValueParameter,
)
from .FakeDipole import FakeDipole
from .StringTools import join_list

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class PinDefinition:

    """This class defines a pin of an element."""

    ##############################################

    def __init__(self, position, name=None, alias=None, optional=False):
        self._position = position
        self._name = name
        self._alias = alias
        self._optional = optional

    ##############################################

    def clone(self):
        # Fixme: self.__class__ ???
        #  unused in code
        return PinDefinition(self._position, self._name, self._alias, self._optional)

    ##############################################

    def __repr__(self):
        _ = f"Pin #{self._position} {self._name}"
        if self._alias:
            _ += f"or {self._alias}"
        if self._optional:
            _ += " optional"
        return _

    ##############################################

    @property
    def position(self):
        return self._position

    @property
    def name(self):
        return self._name

    @property
    def alias(self):
        return self._alias

    @property
    def optional(self):
        return self._optional

####################################################################################################

class OptionalPin:

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

####################################################################################################

class Pin(PinDefinition):

    """This class implements a pin of an element.

    It stores a reference to the element, the name of the pin and the node.

    """

    _logger = _module_logger.getChild('Pin')

    ##############################################

    def __init__(self, element, pin_definition, node):
        super().__init__(pin_definition.position, pin_definition.name, pin_definition.alias)
        self._element = element
        self._node = node
        if self.connected:
            node.connect(self)

    ##############################################

    @property
    def element(self):
        return self._element

    @property
    def node(self):
        return self._node

    ##############################################

    @property
    def dangling(self):
        return self._node is None

    @property
    def connected(self):
        return self._node is not None

    # def __bool__(self):
    #     return self._node is not None

    ##############################################

    def __repr__(self):
        _ = f"Pin {self._name} of {self._element.name}"
        if self.dangling:
            return f"{_} is dangling"
        else:
            return f"{_} on node {self._node}"

    ##############################################

    def connect(self, node):
        # Fixme: if not isinstance(node, Node) ???
        # in ctor netlist.get_node(node, True)
        if self.connected:
            self.disconnect()
        node.connect(self)
        self._node = node

    def disconnect(self):
        # used in Element.detach
        if self.connected:
            self._node.disconnect(self)
            self._node = None

    def __iadd__(self, obj):
        """Connect a node or a pin to the node."""
        from .Netlist import Node
        if isinstance(obj, Node):
            # pin <= node  ===  node <= pin
            self.connect(obj)
        elif isinstance(obj, Pin):
            # pin <=> pin
            if self.connected:
                if obj.connected:
                    # connected <=> connected
                    self._node.merge(obj._node)
                else:
                    # connected <=> dangling
                    obj.connect(self._node)
            else:
                if obj.connected:
                    # dangling <=> connected
                    self.connect(obj._node)
                else:
                    # dangling <=> dangling
                    # Create a new node
                    name = f'{self._element.name}-{self._name}'
                    node = self._element.netlist.get_node(name, create=True)
                    self.connect(node)
                    obj.connect(node)
        else:
            raise ValueError(f"Invalid object {type(obj)}")
        return self

    ##############################################

    def add_current_probe(self, circuit, name=None):
        """Add a current probe between the node and the pin.

        The ammeter is named *ElementName_PinName*.

        """
        # Fixme: require a reference to circuit
        # Fixme: add it to a list
        if self.connected:
            node = self._node
            self._node = '_'.join((self._element.name, str(node), str(self.position) ))
            if name is None:
                name = self._node
            circuit.V(name, node, self._node, '0')
        else:
            raise NameError("Dangling pin")
    
    def add_esr(self, circuit, name= None, value=1e-3):

        """Add a series resistance between the node and the pin.

        The ammeter is named *ElementName_PinName*.

        """

        # Fixme: require a reference to circuit
        # Fixme: add it to a list
        if self.connected:
            node = self._node
            self._node = '_'.join((self._element.name, str(self._node), str(self.position)))
            if name is None:
                name = self._node
            return circuit.R(name, node, self._node, value)
        else:
            raise NameError("Dangling pin")

####################################################################################################

class ElementParameterMetaClass(type):

    # Metaclass to implements the element node and parameter machinery.

    """Metaclass to customise the element classes when they are created and to register SPICE prefix.

    Element classes are of type :class:`ElementParameterMetaClass` instead of :class:`type`

    .. code-block:: none

        class Resistor(metaclass=ElementParameterMetaClass):

        <=>

        Resistor = ElementParameterMetaClass('Foo', ...)

    """

    #: Dictionary for SPICE prefix -> [cls,]
    _classes = {}

    _logger = _module_logger.getChild('ElementParameterMetaClass')

    ##############################################

    def __new__(meta_cls, class_name, base_classes, namespace):

        # __new__ is called for the creation of a class depending of this metaclass, i.e. at module loading
        # It customises the namespace of the new class

        # Collect positional and optional parameters from class attribute dict
        positional_parameters = {}
        parameters = {}
        for attribute_name, obj in namespace.items():
            if isinstance(obj, ParameterDescriptor):
                obj.attribute_name = attribute_name
                if isinstance(obj, PositionalElementParameter):
                    d = positional_parameters
                elif isinstance(obj, (FlagParameter, KeyValueParameter)):
                    d = parameters
                # else:
                #     raise NotImplementedError
                d[attribute_name] = obj

        # Dictionary for positional parameters : attribute_name -> parameter
        namespace['_positional_parameters'] = OrderedDict(
            sorted(list(positional_parameters.items()), key=lambda t: t[1]))

        # Dictionary for optional parameters
        #   order is not required for SPICE, but for unit test
        namespace['_optional_parameters'] = OrderedDict(
            sorted(list(parameters.items()), key=lambda t: t[0]))

        # Positional parameter array
        namespace['_parameters_from_args'] = [
            parameter
            for parameter in sorted(positional_parameters.values())
            if not parameter.key_parameter]

        # Implement alias for parameters: spice name -> parameter
        namespace['_spice_to_parameters'] = {
            parameter.spice_name: parameter
            for parameter in namespace['_optional_parameters'].values()}
        for parameter in namespace['_spice_to_parameters'].values():
            if (parameter.spice_name in namespace
                and parameter.spice_name != parameter.attribute_name):
                _module_logger.error(f"Spice parameter '{parameter.spice_name}' clash with namespace")

        # Initialise pins

        def make_pin_getter(position):
            def getter(self):
                return self._pins[position]
            return getter

        def make_optional_pin_getter(position):
            def getter(self):
                return self._pins[position] if position < len(self._pins) else None
            return getter

        if 'PINS' in namespace and namespace['PINS'] is not None:
            number_of_optional_pins = 0
            pins = []
            for position, pin_definition in enumerate(namespace['PINS']):
                # ensure pin_definition is a tuple
                if isinstance(pin_definition, OptionalPin):
                    optional = True
                    number_of_optional_pins += 1
                    pin_definition = (pin_definition.name,)
                    pin_getter = make_optional_pin_getter(position)
                else:
                    optional = False
                    pin_getter = make_pin_getter(position)
                if not isinstance(pin_definition, tuple):
                    pin_definition = (pin_definition,)
                for name in pin_definition:
                    # Check for name clash
                    if name in namespace:
                        raise NameError(f"Pin {name} of element {class_name} clashes with another attribute")
                    # Add a pin getter in element class
                    namespace[name] = property(pin_getter)
                # Add pin
                pin = PinDefinition(position, *pin_definition, optional=optional)
                pins.append(pin)
            namespace['PINS'] = pins
            namespace['PIN_NAMES'] = [_.name for _ in pins]
            namespace['__number_of_optional_pins__'] = number_of_optional_pins
        else:
            _module_logger.debug(f"{class_name} don't define a PINS attribute")

        return type.__new__(meta_cls, class_name, base_classes, namespace)

    ##############################################

    def __init__(meta_cls, class_name, base_classes, namespace):

        # __init__ is called after the class is created (__new__)

        type.__init__(meta_cls, class_name, base_classes, namespace)

        # Collect basic element classes
        if 'PREFIX' in namespace:
            prefix = namespace['PREFIX']
            if prefix is not None:
                classes = ElementParameterMetaClass._classes
                if prefix in classes:
                    classes[prefix].append(meta_cls)
                else:
                    classes[prefix] = [meta_cls]

    ##############################################

    # Note: These properties are only available from the class object
    #       e.g. Resistor.number_of_pins or Resistor.__class__.number_of_pins

    @property
    def number_of_pins(cls):
        #! Fixme: many pins ???
        number_of_pins = len(cls.PINS)
        if cls.__number_of_optional_pins__:
            return slice(number_of_pins - cls.__number_of_optional_pins__, number_of_pins +1)
        else:
            return number_of_pins

    @property
    def number_of_positional_parameters(cls):
        return len(cls._positional_parameters)

    @property
    def positional_parameters(cls):
        return cls._positional_parameters

    @property
    def optional_parameters(cls):
        return cls._optional_parameters

    @property
    def parameters_from_args(cls):
        return cls._parameters_from_args

    @property
    def spice_to_parameters(cls):
        return cls._spice_to_parameters

####################################################################################################

class Element(metaclass=ElementParameterMetaClass):

    """This class implements a base class for an element.

    It use a metaclass machinery for the declaration of the parameters.

    """

    # These class attributes are defined in subclasses or via the metaclass.
    PINS = None
    _positional_parameters = None
    _optional_parameters = None
    _parameters_from_args = None
    _spice_to_parameters = None

    #: SPICE element prefix
    PREFIX = None

    ##############################################

    def __init__(self, netlist, name, *args, **kwargs):

        self._netlist = netlist
        self._name = str(name)
        self.raw_spice = ''
        self.enabled = True

        # Process remaining args
        if len(self._parameters_from_args) < len(args):
            raise NameError("Number of args mismatch")
        for parameter, value in zip(self._parameters_from_args, args):
            setattr(self, parameter.attribute_name, value)

        # Process kwargs
        for key, value in kwargs.items():
            key = key.lower()
            if key == 'raw_spice':
                self.raw_spice = value
            elif (key in self._positional_parameters or
                  key in self._optional_parameters or
                  key in self._spice_to_parameters):
                setattr(self, key, value)
            elif hasattr(self, 'VALID_KWARGS') and key in self.VALID_KWARGS:
                pass   # cf. NonLinearVoltageSource
            else:
                raise ValueError(f'Unknown argument {key}={value}')

        self._pins = ()
        netlist._add_element(self)

    ##############################################

    def has_parameter(self, name):
        return hasattr(self, '_' + name)

    ##############################################

    def copy_to(self, element):

        for parameter_dict in self._positional_parameters, self._optional_parameters:
            for parameter in parameter_dict.values():
                if hasattr(self, parameter.attribute_name):
                    value = getattr(self, parameter.attribute_name)
                    setattr(element, parameter.attribute_name, value)

        if hasattr(self, 'raw_spice'):
            element.raw_spice = self.raw_spice

    ##############################################

    @property
    def netlist(self):
        return self._netlist

    @property
    def name(self):
        return self.PREFIX + self._name

    @property
    def pins(self):
        return self._pins

    ##############################################

    def detach(self):
        for pin in self._pins:
            pin.disconnect()
        self._netlist._remove_element(self)
        self._netlist = None
        return self

    ##############################################

    @property
    def nodes(self):
        return [pin.node for pin in self._pins]

    @property
    def node_names(self):
        return [str(x) for x in self.nodes]

    ##############################################

    def __repr__(self):
        return self.__class__.__name__ + ' ' + self.name

    ##############################################

    def __setattr__(self, name, value):
        # Implement alias for parameters
        if name in self._spice_to_parameters:
            parameter = self._spice_to_parameters[name]
            object.__setattr__(self, parameter.attribute_name, value)
        elif name in self.PIN_NAMES:
            # __setattr__ is called just after __iadd__
            #   pin += node
            #   means Element.attribute = ( Element.attribute + obj )
            pass
        else:
            object.__setattr__(self, name, value)

    ##############################################

    def __getattr__(self, name):
        # Implement alias for parameters
        if name in self._spice_to_parameters:
            parameter = self._spice_to_parameters[name]
            return object.__getattribute__(self, parameter.attribute_name)
        else:
            raise AttributeError(name)

    ##############################################

    def format_node_names(self):
        """ Return the formatted list of nodes. """
        for pin in self.pins:
            if pin.dangling:
                # yield: NameError: Pin plus of C2 is dangling
                raise NameError(f"{pin}")
        return join_list((self.name, join_list(self.nodes)))

    ##############################################

    def parameter_iterator(self):
        """ This iterator returns the parameter in the right order. """
        # Fixme: .parameters ???
        for parameter_dict in self._positional_parameters, self._optional_parameters:
            for parameter in parameter_dict.values():
                if parameter.nonzero(self):
                    yield parameter

    ##############################################

    # @property
    # def parameters(self):
    #     return self._parameters

    ##############################################

    def format_spice_parameters(self):
        """ Return the formatted list of parameters. """
        return join_list([parameter.to_str(self) for parameter in self.parameter_iterator()])

    ##############################################

    def __str__(self):
        """ Return the SPICE element definition. """
        return join_list((self.format_node_names(), self.format_spice_parameters(), self.raw_spice))

####################################################################################################

class AnyPinElement(Element):

    PINS = ()

    ##############################################

    def copy_to(self, netlist):
        element = self.__class__(netlist, self._name)
        super().copy_to(element)
        return element

####################################################################################################

class FixedPinElement(Element):

    ##############################################

    def __init__(self, netlist, name, *args, **kwargs):

        # Get nodes
        # Usage: if pins are passed using keywords then args must be empty
        #        optional pins are passed as keyword
        pin_definition_nodes = []
        number_of_args = len(args)
        if number_of_args:
            expected_number_of_pins = self.__class__.number_of_pins   # Fixme:
            if isinstance(expected_number_of_pins, slice):
                expected_number_of_pins = expected_number_of_pins.start
            if number_of_args < expected_number_of_pins:
                raise NameError(f"Incomplete node list for element {self.name}")
            else:
                nodes = args[:expected_number_of_pins]
                args = args[expected_number_of_pins:]
                pin_definition_nodes = zip(self.PINS, nodes)
        else:
            for pin_definition in self.PINS:
                if pin_definition.name in kwargs:
                    node = kwargs[pin_definition.name]
                    del kwargs[pin_definition.name]
                elif pin_definition.alias is not None and pin_definition.alias in kwargs:
                    node = kwargs[pin_definition.alias]
                    del kwargs[pin_definition.alias]
                elif pin_definition.optional:
                    continue
                else:
                    raise NameError(f"Node '{pin_definition.name}' is missing for element {self.name}")
                pin_definition_nodes.append((pin_definition, node))

        super().__init__(netlist, name, *args, **kwargs)

        self._pins = [Pin(self, pin_definition, netlist.get_node(node, True))
                      for pin_definition, node in pin_definition_nodes]

    ##############################################

    def copy_to(self, netlist):
        element = self.__class__(netlist, self._name, *self.nodes)
        super().copy_to(element)
        return element

####################################################################################################

class NPinElement(Element):

    PINS = '*'

    ##############################################

    def __init__(self, netlist, name, nodes, *args, **kwargs):
        super().__init__(netlist, name, *args, **kwargs)
        self._pins = [Pin(self, PinDefinition(position), netlist.get_node(node, True))
                      for position, node in enumerate(nodes)]

    ##############################################

    def copy_to(self, netlist):
        nodes = [str(x) for x in self.nodes]
        element = self.__class__(netlist, self._name, nodes)
        super().copy_to(element)
        return element

####################################################################################################

class DipoleElement(FixedPinElement, FakeDipole):
    """This class implements a base class for dipole element."""
    PINS = ('plus', 'minus')

####################################################################################################

class TwoPortElement(FixedPinElement):
    """This class implements a base class for two-port element."""
    PINS = ('output_plus', 'output_minus', 'input_plus', 'input_minus')
