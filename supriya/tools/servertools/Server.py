import signal
import subprocess
import time


class Server(object):
    r'''An scsynth server proxy.

    ::

        >>> from supriya import servertools
        >>> server = servertools.Server.get_default_server()
        >>> server.boot()
        <Server: udp://127.0.0.1:57751, 8i8o>

    ::

        >>> server.quit()
        RECV: OscMessage('/done', '/quit')
        <Server: offline>

    '''

    ### CLASS VARIABLES ###

    __slots__ = (
        '_audio_bus_allocator',
        '_audio_busses',
        '_buffer_allocator',
        '_buffers',
        '_control_bus_allocator',
        '_control_busses',
        '_default_group',
        '_ip_address',
        '_is_running',
        '_node_id_allocator',
        '_nodes',
        '_osc_controller',
        '_osc_dispatcher',
        '_port',
        '_root_node',
        '_server_options',
        '_server_process',
        '_server_status',
        '_status_watcher',
        '_synthdefs',
        )

    _default_server = None

    _servers = {}

    ### CONSTRUCTOR ###

    def __new__(cls, ip_address='127.0.0.1', port=57751):
        key = (ip_address, port)
        if key not in cls._servers:
            instance = object.__new__(cls)
            instance.__init__(
                ip_address=ip_address,
                port=port,
                )
            cls._servers[key] = instance
        return cls._servers[key]

    ### INITIALIZER ###

    def __init__(self, ip_address='127.0.0.1', port=57751):
        self._audio_bus_allocator = None
        self._audio_busses = None
        self._buffer_allocator = None
        self._buffers = None
        self._control_bus_allocator = None
        self._control_busses = None
        self._default_group = None
        self._ip_address = ip_address
        self._is_running = False
        self._node_id_allocator = None
        self._nodes = None
        self._osc_controller = None
        self._osc_dispatcher = None
        self._port = port
        self._root_node = None
        self._server_options = None
        self._server_process = None
        self._server_status = None
        self._status_watcher = None
        self._synthdefs = None

    ### SPECIAL METHODS ###

    def __repr__(self):
        if not self.is_running:
            return '<Server: offline>'
        string = '<Server: {protocol}://{ip}:{port}, '
        string += '{inputs}i{outputs}o>'
        return string.format(
            protocol=self.server_options.protocol,
            ip=self.ip_address,
            port=self.port,
            inputs=self.server_options.input_bus_channel_count,
            outputs=self.server_options.output_bus_channel_count,
            )

    ### PRIVATE METHODS ###

    def _setup_server_state(self):
        from supriya.tools import servertools
        self._audio_bus_allocator = servertools.BlockAllocator()
        self._buffer_allocator = servertools.BlockAllocator()
        self._control_bus_allocator = servertools.BlockAllocator()
        self._node_id_allocator = servertools.NodeIDAllocator()
        self._audio_busses = {}
        self._buffers = {}
        self._control_busses = {}
        self._nodes = {}
        self._synthdefs = {}
        self._root_node = servertools.RootNode()
        self._default_group = servertools.DefaultGroup()
        self._default_group._parent_group = self._root_node
        self._server_status = None
        self.send_message(("/g_new", 1, 0, 0))

    def _teardown_server_state(self):
        self._audio_bus_allocator = None
        self._buffer_allocator = None
        self._control_bus_allocator = None
        self._node_id_allocator = None
        for x in self._audio_busses.values():
            x.free()
        for x in self._buffers.values():
            x.free()
        for x in self._control_busses.values():
            x.free()
        for x in self._nodes.values():
            x.free()
        self._default_group = None
        self._root_node = None
        self._server_status = None

    ### PUBLIC METHODS ###

    def boot(
        self,
        server_options=None,
        ):
        from supriya.tools import servertools
        from supriya.tools import osctools
        if self.is_running:
            return
        self._osc_controller = osctools.OscController(
            server_ip_address=self.ip_address,
            server_port=self.port,
            )
        self._server_options = server_options or servertools.ServerOptions()
        options_string = self._server_options.as_options_string(self.port)
        command = 'scsynth {}'.format(options_string)
        self._server_process = subprocess.Popen(
            command.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            )
        time.sleep(0.25)
        self._is_running = True
        self._setup_server_state()
        return self

    @staticmethod
    def get_default_server():
        if Server._default_server is None:
            Server._default_server = Server(
                ip_address='127.0.0.1',
                port=57751,
                )
        return Server._default_server

    def quit(self):
        from supriya.tools import servertools
        if not self.is_running:
            return
        with servertools.WaitForServer('/(done|fail)', ['/quit']):
            self.send_message(r'/quit')
        self._is_running = False
        self._server_process.send_signal(signal.SIGINT)
        self._server_process.kill()
        self._teardown_server_state()
        return self

    def register_osc_callback(self, osc_callback):
        self._osc_controller.register_callback(osc_callback)

    def send_message(self, message):
        if not self.is_running:
            return
        self._osc_controller.send(message)

    def unregister_osc_callback(self, osc_callback):
        self._osc_controller.unregister_callback(osc_callback)

    ### PUBLIC PROPERTIES ###

    @property
    def audio_bus_allocator(self):
        return self._audio_bus_allocator

    @property
    def buffer_allocator(self):
        return self._buffer_allocator

    @property
    def control_bus_allocator(self):
        return self._control_bus_allocator

    @property
    def ip_address(self):
        return self._ip_address

    @property
    def is_running(self):
        return self._is_running

    @property
    def node_id_allocator(self):
        return self._node_id_allocator

    @property
    def port(self):
        return self._port

    @property
    def root_node(self):
        return self._root_node

    @property
    def server_options(self):
        return self._server_options