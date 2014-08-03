# -*- encoding: utf-8 -*-
from supriya.tools.servertools.Node import Node


class Group(Node):
    r'''A group.

    ::

        >>> from supriya import servertools
        >>> server = servertools.Server()
        >>> server.boot()
        <Server: udp://127.0.0.1:57751, 8i8o>

    ::

        >>> group = servertools.Group()
        >>> group.allocate()
        <Group: 1000>

    ::

        >>> group.free()
        <Group: ???>

    ::

        >>> server.quit()
        <Server: offline>

    '''

    ### CLASS VARIABLES ###

    __slots__ = (
        '_children',
        '_named_children',
        )

    ### INITIALIZER ###

    def __init__(self):
        Node.__init__(self)
        self._children = []
        self._named_children = {}

    ### SPECIAL METHODS ###

    def __contains__(self, expr):
        for x in self._children:
            if x is expr:
                return True
        return False

    def __delitem__(self, expr):
        expr.free()

    def __getitem__(self, expr):
        return self._children[expr]

    def __iter__(self):
        for child in self._children:
            yield child

    def __len__(self):
        return len(self._children)

    def __setitem__(self, i, expr):
        from supriya.tools import requesttools
        from supriya.tools import servertools

        assert self.is_allocated
        raise NotImplementedError

        if isinstance(i, int):
            if i < 0:
                i = len(self) + i
            i = slice(i, i + 1)
            expr = [expr]
        assert all(isinstance(_, servertools.Node) for _ in expr)
        start, stop, _ = i.indices(len(self))

        del(self[start:stop])
        self._children.__setitem__(slice(start, start), expr)
        for node in expr:
            node._set_parent(self)

        message_bundler = servertools.MessageBundler(
            server=self.server,
            sync=True,
            )

        with message_bundler:

            if not start or not self:
                target_node = self
            else:
                target_node = self[start - 1]

            for node in expr:
                node._set_parent(self)
                if node.is_allocated:
                    if target_node is self:
                        request = requesttools.GroupHeadRequest(
                            group_id=self.node_id,
                            node_id=node.node_id,
                            )
                    else:
                        request = requesttools.NodeAfterRequest(
                            node_id=node.node_id,
                            target_node_id=target_node.node_id,
                            )
                    message_bundler.add_message(request)
                else:
                    if target_node is self:
                        add_action = servertools.AddAction.ADD_TO_HEAD
                    else:
                        add_action = servertools.AddAction.ADD_AFTER
                    add_action, node_id, target_node_id = Node.allocate(
                        node,
                        add_action=add_action,
                        target_node=target_node,
                        )
                    if isinstance(node, servertools.Group):
                        request = requesttools.GroupNewRequest(
                            add_action=add_action,
                            node_id=node,
                            target_node_id=target_node,
                            )
                    else:
                        request = requesttools.SynthNewRequest(
                            add_action=add_action,
                            node_id=node,
                            synthdef=node.synthdef,
                            target_node_id=target_node,
                            )
                        # handle synth control settings too?
                        # handle synth controls which are buses?
                    message_bundler.add_message(request)
                            
                target_node = node

    ### PRIVATE METHODS ###

    @staticmethod
    def _iterate_children(group):
        from supriya.tools import servertools
        for child in group.children:
            if isinstance(child, servertools.Group):
                for subchild in Group._iterate_children(child):
                    yield subchild
            yield child

    ### PUBLIC METHODS ###

    def allocate(
        self,
        add_action=None,
        node_id_is_permanent=False,
        sync=False,
        target_node=None,
        ):
        from supriya.tools import requesttools
        add_action, node_id, target_node_id = Node.allocate(
            self,
            add_action=add_action,
            node_id_is_permanent=node_id_is_permanent,
            target_node=target_node,
            )
        request = requesttools.GroupNewRequest(
            add_action=add_action,
            node_id=node_id,
            target_node_id=target_node_id,
            )
        request.communicate(
            server=self.server,
            sync=sync,
            )
        return self

    def append(self, expr):
        self.__setitem__(
            slice(len(self), len(self)),
            [expr]
            )

    def extend(self, expr):
        self.__setitem__(
            slice(len(self), len(self)),
            expr
            )

    def free(
        self,
        send_to_server=True,
        ):
        for child in self.children:
            child.free(
                send_to_server=False,
                )
        Node.free(
            self,
            send_to_server=send_to_server,
            )
        return self

    def index(self, expr):
        for i, child in enumerate(self._children):
            if child is expr:
                return i
        else:
            message = '{!r} not in {!r}.'
            message = message.format(expr, self)
            raise ValueError(message)

    def insert(self, i, expr):
        self.__setitem__(
            slice(i, i),
            [expr]
            )

    def pop(self, i=-1):
        node = self[i]
        del(self[i])
        return node

    def remove(self, node):
        i = self.index(node)
        del(self[i])

    ### PUBLIC PROPERTIES ###

    @property
    def children(self):
        return tuple(self._children)