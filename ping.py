from threading import Thread, RLock

from pythonping import ping
from time import time
from interfaces.sender_interface import SenderInterface

TIMEOUT_IN_SECONDS = 60

msg = "Success!\nRound Trip Times min/avg/max is {}/{}/{} ms"

cache = {}
lock = RLock()


def ping_host_and_cache(host, count_rp, sender: SenderInterface):
    try:
        response_list = ping(host, count=count_rp)
        with lock:
            cache[host] = (response_list, time())
        sender.send_message(
            msg.format(
                response_list.rtt_min_ms,
                response_list.rtt_avg_ms,
                response_list.rtt_max_ms,
            )
        )
    except RuntimeError:
        sender.send_message("Failure! Connection error!")


def get_statistics(host, count_rp, sender: SenderInterface):
    with lock:
        if host in cache:
            response = cache[host]
            response_time = response[1]
            response_list = response[0]
            if time() - response_time < TIMEOUT_IN_SECONDS:
                sender.send_message(
                    msg.format(
                        response_list.rtt_min_ms,
                        response_list.rtt_avg_ms,
                        response_list.rtt_max_ms,
                    )
                )
                return
    thread = Thread(target=ping_host_and_cache, args=(host, count_rp, sender))
    thread.start()
