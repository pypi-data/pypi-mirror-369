import logging
import os
import sys
from time import time, sleep
import asyncio
import signal

from wsctrl.sink_ctrl import SinkController, Nbor
from wmbc.mb_proto import mb_protocol_enums_pb2 as mb_enums
from wmbc.mb_proto.mb_protocol_iface import MBProto
from google.protobuf.json_format import MessageToJson


logging.basicConfig(level=logging.INFO)
   

def signal_exit(sig, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, signal_exit)


class WMBController():
    """
    Implementation of WMB controller
    """

    MB_PROTO_SRC_EP = 77
    MB_PROTO_DST_EP = 66

    def __init__(self, **kwargs):

        logging.info("Starting WMB Controller")
        self._sink_ids = kwargs.get("sink_ids")
        self._cmd_type = kwargs.get("cmd")
        self._dst_addr = kwargs.get("dst_addr")
        self._dev_mode = kwargs.get("dev_mode")
        self._ant_cfg = kwargs.get("ant_cfg")
        self._target_port = kwargs.get("target_port")
        self._port_cfg = kwargs.get("port_cfg")
        self._modbus_file = kwargs.get("modbus_file")
        self._modbus_frame = kwargs.get("modbus_frame")
        self._modbus_interval = kwargs.get("modbus_interval")
        self._modbus_cfg_idx = kwargs.get("modbus_cfg_idx")
        self._polling_only = self._cmd_type is None

        self._mbproto = MBProto()
        # Provide default sink_ids if not provided in init
        if (self._sink_ids is None):
            self._sink_ids = ["sink0", "sink1"]
        if (self._cmd_type is not None):
            assert self._dst_addr > 0, "Destination address cannot be 0!"
            self._client = SinkController(self._dst_addr & 0xFFFFFFFF, self.MB_PROTO_SRC_EP, self.MB_PROTO_DST_EP, sink_ids=self._sink_ids)
        else:
            self._client = SinkController(self._dst_addr, pm=True, sink_ids=self._sink_ids)
            return

        if self._cmd_type == "reset":
            self._payload_coded = self._mbproto.create_device_reset()
        elif self._cmd_type == "diag":
            self._payload_coded = self._mbproto.create_diagnostics()
        elif self._cmd_type == "dev_mode":
            self._mbproto.device_mode = self._dev_mode
            self._payload_coded = self._mbproto.create_device_mode()
        elif self._cmd_type == "ant_cfg":
            self._mbproto.antenna_config = self._ant_cfg
            self._payload_coded = self._mbproto.create_antenna_config()
        elif self._cmd_type == "port_cfg":
            self._mbproto.target_port = self._target_port
            self._mbproto.baudrate_config = int(self._port_cfg[0])
            self._mbproto.parity_bit = int(self._port_cfg[1])
            self._mbproto.stop_bits = int(self._port_cfg[2])
            self._payload_coded = self._mbproto.create_port_config()
        elif self._cmd_type == "modbus_1s":
            if (self._modbus_file is not None and self._modbus_frame is not None):
                raise ValueError("Both file and frame defined as payload")
            elif (self._modbus_file is not None or self._modbus_frame is not None):
                if (self._modbus_file is not None):
                    try:
                        with open(self._modbus_file, 'rb') as f:
                            self._payload_coded = f.read()
                    except FileNotFoundError:
                        raise FileNotFoundError(f"File {self._modbus_file} does not exist!")
                    except Exception as e:
                        raise e(f"Unhandled exception")
                    self._mbproto.target_port = self._target_port
                    self._payload_coded = self._mbproto.create_modbus_oneshot(self._payload_coded)
                else:
                    self._payload_coded = self._modbus_frame
                    self._mbproto.target_port = self._target_port
                    self._payload_coded = self._mbproto.create_modbus_oneshot(self._payload_coded)
            else:
                raise ValueError("No Modbus Payload!")
        elif self._cmd_type == "modbus_p":
            if (self._modbus_file is not None and self._modbus_frame is not None):
                raise ValueError("Both file and frame defined as payload")
            elif (self._modbus_file is not None or self._modbus_frame is not None):
                if (self._modbus_file is not None):
                    try:
                        with open(self._modbus_file, 'rb') as f:
                            self._payload_coded = f.read()
                    except FileNotFoundError:
                        raise FileNotFoundError(f"File {self._modbus_file} does not exist!")
                    except Exception as e:
                        raise e(f"Unhandled exception")
                    self._mbproto.target_port = self._target_port
                    self._payload_coded = self._mbproto.create_modbus_periodic(self._modbus_cfg_idx, self._modbus_interval,
                                                                               self._payload_coded)
                else:
                    self._payload_coded = self._modbus_frame
                    self._mbproto.target_port = self._target_port
                    self._payload_coded = self._mbproto.create_modbus_periodic(self._modbus_cfg_idx, self._modbus_interval,
                                                                               self._payload_coded)
            else:
                raise ValueError("No Modbus Payload!")
        else:
            raise ValueError("Unsupported command type!")

    def _stop_sinks(self):
        self._client.deinitialize_sink()

    def _start_sinks(self):
        self._client.initialize_sink()

    def send_command(self):
        if self._client and self._payload_coded:
            self._client.send(self._payload_coded)

    def initialize_sink(self):
        self._start_sinks()

    def deinitialize_sink(self):
        self._stop_sinks()

    async def run(self, quit=False):
        if self._cmd_type is not None:
            self.send_command()
        if not quit:
            logging.info("Entering infinite polling, press Ctrl+C to exit")
        while True:
            response = await self._client.async_receive()
            logging.info(f"Got message from: {response.src}")
            self._mbproto.print_decoded_msg(response.payload)
            if quit:
                return

    async def run_periodically(self, period=10, timeout=5, _callback=None, callback_args=None, print_default=False):
        if self._cmd_type is None:
            raise ValueError("Command not defined!")
        logging.info("Entering periodical command send with polling, press Ctrl+C to exit")
        while True:
            self.send_command()
            try:
                response = await asyncio.wait_for(self._client.async_receive(), timeout=timeout)
            except asyncio.TimeoutError:
                logging.warning("No response from the device!")
                await asyncio.sleep(period)
                continue
            if _callback != None:
                ret, err, msg = self._mbproto.decode_response(response.payload)
                if (not ret):
                    logging.error("Failed to decode frame!: %s", err)
                else:
                    _callback(msg, callback_args)
            elif print_default:
                logging.info(f"Got message from: {response.src}")
                self._mbproto.print_decoded_msg(response.payload, decode_modbus_frame=False)
            await asyncio.sleep(period)
