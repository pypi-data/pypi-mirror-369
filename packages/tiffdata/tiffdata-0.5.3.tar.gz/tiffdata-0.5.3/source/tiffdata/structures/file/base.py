from __future__ import annotations

from tiffdata.logging import logger
from tiffdata.enumerations.format import Format
from tiffdata.structures.offset import Offset

logger = logger.getChild(__name__)


class Element(object):
    """The Element class provides base functionality for the TIFF structure subclasses."""

    _label: str = None
    _length: int = None
    _offset: Offset = None
    _carrier: Element = None
    _carries: Element = None
    _datum: Data = None

    def __init__(
        self,
        label: str = None,
        offset: Offset | int = 0,
        length: int = 0,
        carrier: Element = None,
    ):
        self.label = label
        self.offset = offset
        self.length = length
        self.carrier = carrier

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}({self.label})>"

    @property
    def klass(self) -> str:
        return self.__class__.__name__

    @property
    def label(self) -> str:
        return self._label or "?"

    @label.setter
    def label(self, label: str):
        if label is None:
            self._label = None
        elif isinstance(label, str):
            self._label = label
        else:
            raise TypeError(
                "The 'label' argument, if specified, must have a string value!"
            )

    @property
    def length(self) -> int:
        """Support getting the element's data length."""

        return self._length

    @length.setter
    def length(self, length: int):
        """Support setting the element's data length."""

        if not isinstance(length, int):
            raise TypeError("The 'length' argument must have an integer value!")
        elif not length >= 0:
            raise ValueError(
                "The 'length' argument must have a positive integer value!"
            )
        else:
            self._length = length

    @property
    def offset(self) -> Offset:
        """Support getting the node's source and later target offsets within the file"""

        return self._offset

    @offset.setter
    def offset(self, offset: Offset | int):
        """Support setting the node's source and later target offsets within the file"""

        if isinstance(offset, Offset):
            self._offset = offset
        elif isinstance(offset, int):
            if not offset >= 0:
                raise ValueError(
                    "The 'offset' argument must have a positive integer value!"
                )
            self._offset = Offset(source=offset)
        else:
            raise TypeError(
                "The 'offset' argument must have a positive integer value or reference an Offset class instance!"
            )

    @property
    def root(self) -> Element:
        """Support getting the linked-list root (first) node."""

        node: Element = self

        while isinstance(carrier := node.carrier, Element):
            node = carrier

        return node

    @property
    def tip(self) -> Element:
        """Support getting the linked-list tip (last) node."""

        node: Element = self

        while isinstance(carries := node.carries, Element):
            node = carries

        return node

    @property
    def carrier(self) -> Element | None:
        """Support getting the carrier node if any."""

        return self._carrier

    @carrier.setter
    def carrier(self, carrier: Element):
        """Support setting the carrier node."""

        if carrier is None:
            self._carrier = None
        elif isinstance(carrier, Element):
            self._carrier = carrier
        else:
            raise TypeError(
                "The 'carrier' argument must reference a Element class instance!"
            )

    @property
    def carries(self) -> Element | None:
        """Support getting the carries node if any."""

        return self._carries

    @carries.setter
    def carries(self, carries: Element):
        """Support setting the carries node."""

        if carries is None:
            self._carries = None
        elif isinstance(carries, Element):
            self._carries = carries
        else:
            raise TypeError(
                "The 'carries' argument must reference a Element class instance!"
            )

    def chain(self, other: Element) -> Element:
        """Support chaining the current element to the specifed element."""

        if not isinstance(other, Element):
            raise TypeError(
                "The 'other' argument must reference a Element class instance!"
            )

        logger.debug(
            "%s[%s].chain(other: %s[%s])"
            % (
                self.klass,
                self.label,
                other.klass,
                other.label,
            )
        )

        self.carrier = other

        other.carries = self

        return self

    def replace(self, other: Element):
        """Support replacing the current element in the chain with the provided element."""

        if not isinstance(other, Element):
            raise TypeError(
                "The 'other' argument must reference a Element class instance!"
            )

        logger.debug(
            "%s[%s].replace(other: %s[%s])"
            % (
                self.klass,
                self.label,
                other.klass,
                other.label,
            )
        )

        if isinstance(self.offset, Offset) and not (
            isinstance(other.offset, Offset) and other.offset.source > 0
        ):
            other.offset = self.offset.copy()
        else:
            logger.debug(" >>> did not copy self.offset to other.offset <<<")
            logger.debug(" >>> self.offset:  %s" % (isinstance(self.offset, Offset)))
            logger.debug(" >>> other.offset: %s" % (isinstance(other.offset, Offset)))

        carrier = self.carrier
        carries = self.carries

        if carrier:
            carrier.carries = other
            other.carrier = carrier

        if carries:
            carries.carrier = other
            other.carries = carries

        self.carrier = None
        self.carries = None

        return self

    def insert(self, other: Element):
        """Support inserting the provided element into the chain at the current element."""

        if not isinstance(other, Element):
            raise TypeError(
                "The 'other' argument must reference a Element class instance!"
            )

        logger.debug(
            "%s[%s].insert(other: %s[%s])"
            % (
                self.klass,
                self.label,
                other.klass,
                other.label,
            )
        )

        logger.debug("Carrier => %s" % (self.carrier))
        logger.debug("Carries => %s" % (self.carries))

        # Assign whatever self carries to other
        other.carries = self.carries

        # Assign self as the carrier for other
        other.carrier = self

        # Reassign self carries to other
        self.carries = other

        logger.debug("Carrier => %s" % (self.carrier))
        logger.debug("Carries => %s" % (self.carries))

        return self

    def unchain(self):
        """Support unchaining the current element's carried element, if any."""

        self.carries = None

    def reset(self) -> Element:
        """Support resetting the linked-list between the elements."""

        element: Element = self.tip  # find the tip (last) element

        while True:
            element.unchain()  # Unlink the carried element (if any)

            if not (
                element := element.carrier
            ):  # Find its carrier, working up to the root
                break

        return self

    @property
    def datum(self) -> Data | None:
        """The data value itself, if it fits in the four bytes available, or a pointer
        to the data if it won't fit, which could be to the beginning of another IFD."""

        return self._datum

    @datum.setter
    def datum(self, datum: Data):
        from tiffdata.structures.file.data import Data

        if datum is None:
            self._datum = None
        elif isinstance(datum, Data):
            self._datum = datum
        else:
            raise TypeError(
                "The 'datum' argument, if specified, must reference a Data class instance!"
            )

    def external(self, format: Format) -> bool:
        """Determine if the element has needs to store any data externally or not, given
        the target file format, which affects how many bytes are available within some
        elements such as Tags to store data (32 bytes for Classic, 64 bytes for Big)."""

        return False
