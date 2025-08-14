# pyInjection
pyInjector is a .Net style dependency injection container built for Python3 and utilising the typing module.

- Register `type`, `instance` and `lambda` functions against a base type for constructor injecting.
- Supports `ABC` base types and mock interfaces.
- Validates container for duplicate registrations, missing registrations and inconsistent scope registrations at runtime.

## Table of Contents
1. [Class Setup (for Injectables)](#class-setup-for-injectables)
2. [Constructor Setup (for accepting Injectables)](#constructor-setup-for-accepting-injectables)
3. [Registration](#registration)
3.1. [Type Registration](#type-registration)
3.2. [Instance Registration](#instance-registration)
3.3. [Lambda Registration (for decorators)](#lambda-registration-for-decorators)
4. [Resolving](#resolving)
4.1. [Lambda Registration with a Resolve](#lambda-registration-with-a-resolve)
4.2. [Resolve for application execution](#resolve-for-application-execution)
5. [Validation](#validation)

-------
## Class Setup (for Injectables)
In order for pyInjection to register and inject a class into a constructor, classes must extend a base class. This class can be an abstract class (using ABC) or a mock interface:

```python
from abc import ABC, abstractmethod

class IFoo(ABC):
    @abstractmethod
    def do_something(self) -> None:
	    pass
```
or
```python
class IFoo:
	def do_something(self) -> None:
		pass
```

## Constructor Setup (for accepting Injectables)
In order for pyInjection to inject objects into class constructors, the constructor must be decorated with `@Container.inject`:

```python
from pjInjection import Container

class Bar:
	__foo: IFoo

	@Container.inject
	def __init__(self, foo: IFoo):
		self.__foo = foo

	def run(self) -> None:
		self.__foo.do_something()
```
## Registration
pyInjection supports 3 types of injectable registration across both `transient` and `singleton` lifetimes.
```python
from pyInjection import Container

Container.add_transient(interface= IFoo, implementation= Foo)
Container.add_singleton(interface= IBar, implementation= Bar)
```
Container registrations (like in .Net) maps an `implementation` to the `interface` base within supported constructors.

#### Type Registration:
```python
Container.add_transient(interface= IFoo, implementation= Foo)
```
#### Instance Registration:
```python
# Note this is registered as transient but will be resolved as a singleton
Container.add_transient(interface= IFoo, implementation= Foo())
```
#### Lambda Registration (for decorators):
```python
Container.add_transient(interface= IFoo, implementation= lambda: Foo())
```

## Resolving
In some cases you may wish to resolve an instance from the container (for a lambda function or running the application).
#### Lambda Registration with a Resolve
```python
...

Container.add_transient(interface= IFoo, implementation= Foo)
Container.add_transient(
    interface= IBar,
    implementation= lambda: Bar(foo= Container.resolve(interface= IFoo)
)
```
#### Resolve for application execution
```python
...

Container.add_singleton(interface= IFoo, implementation= Foo)
Container.add_singleton(interface= IBar, implementation= Bar)

bar: IBar = Container.resolve(interface= IBar)
bar.run()
```
## Validation
In order to ensure that the container has been configured correctly and has everything necessary to build all injectable dependencies run the `validate` method in the composition root:

```python
...

Container.validate()
```

Any issues found within the container will be raised as an Exception. Exceptions will be raised for the following:
- Duplicate registrations
- Missing registrations
- Type registrations for constructors with primitive types (these should be an instance registration)

---
