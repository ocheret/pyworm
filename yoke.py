class Yoke(object):
    """Yoke implements a doubly linked list. The various algorithms
    used to manipulate the Yokes in the linked list have some
    interesting properties that make this implementation more useful
    than more naive doubly linked list implementations. The algorithms
    for this implementation originally come from an article from
    Niklaus Wirth (XXX - can't find the reference).  This class is
    very powerful but is likely to blow your mind.  It is recommended
    to work out a few examples by hand to reach an enjoyable epiphany
    or two.

    Some of the features include:

    - Reversible insert operations (e.g. a.InsertLeft(b); a.InsertLeft(b)
    done together is a no-op).

    - Commutative insert and append operations (i.e. a.InsertLeft(b)
    and b.InsertLeft(a) produce identical results).

    - The ability to splice together multiple doubly linked lists
    at any point.

    - The ability to divide a doubly linked list in two from any
    two points in the list.

    The following examples with string values should illustrate how
    InsertLeft and InsertRight work.

    If you have the list segment

    ...->a->b->c->... (only showing right pointers)

    and you invoke b.InsertLeft(Yoke("x")) you get...

    ...->a->x->b->c->...

    However, if you invoke b.InsertRight(Yoke("x")) you get...

    ...->a->b->x->c->...

    If you have 2 lists (showing circular lists here by repeating
    the end elements)...

    a->b->c->d->e->a
    ================

    p->q->r->s->t->p
    ----------------

    and you do either a.InsertLeft(p) or p.InsertLeft(a), you get

    p->q->r->s->t->a->b->c->d->e->p
    -------------  =============  _

    Invoking a.InsertLeft(p) again, or invoking p.InsertLeft(a)
    splits the long list back into the original 2 lists again.

    Calling a.InsertRight(p) or p.InsertRight(a) gives you

    a->q->r->s->t->p->b->c->d->e->a

    Invoking a.InsertRight(p) again, or p.InsertRight(a) splits the
    long lists back into the original 2 lists. Very Cool!

    Another way to think of it is that when operating on the two
    separate lists with a and p, a.InsertLeft(p) splices the entire
    list attached to p to the left of a.  What's more, this splicing
    is done in such a way that p is the element from its original
    list that is furthest to the left away from a.

    When there is just one big list, calling a.InsertLeft(p), splits
    the list in two by separating a from its left neighbor and
    separating p from its left neighbor to form two smaller circular
    lists.  Magic.
    """

    def __init__(self, value):
        self.value = value
        self.left = self
        self.right = self

    def insert_left(self, x):
        """
        Inserts Yokes into each other's lists. This can be used to
        splice two lists together. The operation is also reversible.
        Weird, huh?

        If you have 2 lists(showing circular lists here by repeating
        the end elements)...

        a -> b -> c -> d -> e -> a
        ==========================

        p -> q -> r -> s -> t -> p
        --------------------------

        and you do either a.InsertLeft(p) or p.InsertLeft(a), you get

        p -> q -> r -> s -> t -> a -> b -> c -> d -> e -> p
        ---------------------    =====================    _

        Invoking a.InsertLeft(p) again, or invoking p.InsertLeft(a)
        splits the long list back into the original 2 lists again.

        x is the Yoke to insert in our list.  If x is None then nothing
        is done.
        """
        if x != None:
            t = self.left
            self.left.right = x
            self.left = x.left
            x.left.right = self
            x.left = t
        return self

    def insert_right(self, x):
        """
        Appends Yokes onto each other's lists. This can be used to splice two
        lists together. The operation is also reversible. Weird, huh?

        If you have 2 lists(showing circular lists here by
        repeating the end elements)...

        a -> b -> c -> d -> e -> a
        ==========================

        p -> q -> r -> s -> t -> p
        --------------------------

        Calling a.InsertRight(p) or p.InsertRight(a) gives you

        a -> q -> r -> s -> t -> p -> b -> c -> d -> e -> a
        =    ---------------------    =====================

        Invoking a.InsertRight(p) again, or p.InsertRight(a) splits
        the long lists back into the original 2 lists. Very
        Cool!

        x the Yoke to append to our list.  If x is None then
        nothing is done.
        """
        if x != None:
            t = self.right
            self.right.left = x
            self.right = x.right
            x.right.left = self
            x.right = t
        return self

    def remove(self):
        """Removes a Yoke from a list so it forms its own single element list."""
        self.left.right = self.right
        self.right.left = self.left
        self.left = self
        self.right = self
        return self
