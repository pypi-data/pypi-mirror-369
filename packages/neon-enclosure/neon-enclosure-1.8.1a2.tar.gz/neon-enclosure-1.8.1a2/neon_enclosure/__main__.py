# NEON AI (TM) SOFTWARE, Software Development Kit & Application Framework
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2025 Neongecko.com Inc.
# Contributors: Daniel McKnight, Guy Daniels, Elon Gasper, Richard Leeds,
# Regina Bloomstine, Casimiro Ferreira, Andrii Pernatii, Kirill Hrymailo
# BSD-3 License
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from neon_utils.log_utils import init_log
from neon_utils.process_utils import (
    start_malloc,
    snapshot_malloc,
    print_malloc,
)
from neon_utils.signal_utils import init_signal_bus, init_signal_handlers
from ovos_bus_client.util import get_mycroft_bus
from ovos_utils.process_utils import reset_sigint_handler
from ovos_utils.log import LOG
from ovos_utils import wait_for_exit_signal

from neon_enclosure.service import NeonHardwareAbstractionLayer


def main(*args, **kwargs):
    kwargs.setdefault("skill_id", "neon.phal")
    init_log(log_name="enclosure")
    malloc_running = start_malloc(stack_depth=4)

    if "bus" not in kwargs:
        bus = get_mycroft_bus()
        kwargs["bus"] = bus
    else:
        bus = kwargs["bus"]
    init_signal_bus(bus)
    init_signal_handlers()
    reset_sigint_handler()
    health_check_server_port = kwargs.pop("health_check_server_port", None)
    service = NeonHardwareAbstractionLayer(*args, **kwargs)
    if health_check_server_port is not None:
        from neon_utils.process_utils import start_health_check_server

        start_health_check_server(
            service.status, health_check_server_port, service.check_health
        )
    service.start()
    wait_for_exit_signal()
    if malloc_running:
        try:
            print_malloc(snapshot_malloc())
        except Exception as e:
            LOG.error(e)
    service.shutdown()


def deprecated_entrypoint():
    from ovos_utils.log import log_deprecation

    log_deprecation(
        "Use `neon-enclosure run` in place of `neon_enclosure_client`", "2.0.0"
    )
    main()


if __name__ == "__main__":
    main()
