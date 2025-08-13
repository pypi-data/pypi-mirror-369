import abc as _abc


class CreateFromBuilderMixin(_abc.ABC):
    """
    A mixin for creating and configuring instances of composite modules.  Users have
    three options for creating instances of classes that inherit from this mixin:

    (1) Instantiate the object directly through the :meth:`__init__` method.  Generally
        :meth:`__init__` should accept full child layers (or child builders) as
        arguments, providing the user with maximal flexibility for configuring the
        layer.  While this provides a lot of control, it is often tedious for the user
        to create instances in this way due to complexity of the arguments.
    (2) Create the object by calling the :meth:`create` method.  The :meth:`create`
        method should have a simpler signature and return a "default" instance of the
        class.  This provides much less flexibility compared to option 1, but the
        simpler signature makes it easier to create objects that have common
        configurations.
    (3) Create a builder using the :meth:`create_builder` method, then update the
        builder before using it to create a new instance.  This provides a
        middle-ground between options 1 and 2.  The user provides a simple set of
        arguments to create a builder, and then the user can configure the builder
        arbitrarily before building the composite layer.
    """

    @classmethod
    def create(cls, *args, **kwargs):
        """
        Creates and returns an instance of the class using a builder returned by
        ``cls.create_builder(*args, **kwargs)``.  Please see :meth:`create_builder`
        for a description of supported arguments.

        Args:
            *args: Variable arguments for :meth:`create_builder`.
            *kwargs: Variable keyword arguments for :meth:`create_builder`.
        """
        builder = cls.create_builder(*args, **kwargs)
        return builder()

    @classmethod
    @_abc.abstractmethod
    def create_builder(cls):
        """
        Return a :class:`Builder` for creating instances of the class.  Subclasses
        should add arguments to this method for configuring the builder.
        """
