from __future__ import annotations
from typing import TypeVar, Type

from typing_extensions import Any, Optional, Union, Iterable

from .symbolic import SymbolicExpression, And, Entity, SetOf, The, An, Variable
from .utils import render_tree

T = TypeVar('T')  # Define type variable "T"


def an(entity_: Union[SetOf[T], Entity[T]], show_tree: bool = False) -> An[T]:
    return an_or_the(entity_, An, show_tree)


def the(entity_: Union[SetOf[T], Entity[T]], show_tree: bool = False) -> The[T]:
    return an_or_the(entity_, The, show_tree)


def an_or_the(entity_: Entity[T], func: Union[Type[An], Type[The]],
              show_tree: bool = False) -> Union[An[T], The[T]]:
    root = func(entity_)
    if show_tree:
        render_tree(root._node_, True, view=True)
    return root


def entity(selected_variable: T, *properties: Union[SymbolicExpression, bool]) -> Entity[T]:
    expression = And(*properties) if len(properties) > 1 else properties[0]
    return Entity(_child_=expression, selected_variable_=selected_variable)


def set_of(selected_variables: Iterable[T], *properties: Union[SymbolicExpression, bool]) -> SetOf[T]:
    expression = And(*properties) if len(properties) > 1 else properties[0]
    return SetOf(_child_=expression, selected_variables_=selected_variables)

def let(type_: Type[T], domain: Optional[Any] = None) -> T:
    return Variable._from_domain_((v for v in domain if isinstance(v, type_)), clazz=type_)
