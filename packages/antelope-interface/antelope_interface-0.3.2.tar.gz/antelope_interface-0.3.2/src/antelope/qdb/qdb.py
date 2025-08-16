"""
An interface specification for a quantity database.  This was originally conceived as being *the* quantity
interface, but as things have developed it's become clear that the qdb does more (and less) than the
quantity interface governs, and many (even most) of the operations of qdb are not even part of the antelope
interface spec.

For that reason, we are putting this *still in* antelope interface but *outside of* the abstract query framework,
and making it a straight abstract base class.
"""

from abc import ABC


class QdbInterface(ABC):
    """
    The main purpose of the qdb is to maintain a free-standing database of quantities and flows.  This will
    most likely be implemented as a graph, but the interface for interacting with it is not going to care about
    that.  Here we brainstorm about all the things we would want the qdb to do.

    # quantities

    Quantities are a fundamental concept in physical science; yet my implementation of them is basically made up
    based on my experience and intuition.  We distinguish between reference quantities, which are directly measurable,
    and which are [within qdb] *strictly* canonical and can therefore only be created or altered by privileged users,
    and *indicators*, which are quantities that may or may not be directly measurable but are owned by users and
    therefore not canonical.


    In qdb, we only store *reference* quantities (right? or do we allow users
    to make their own quantities?  we allow users to make their own *indicators*.  Only privileged users can c
    """
    pass
