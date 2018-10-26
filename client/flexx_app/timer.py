from pscript.stubs import RawJS

# local time + desync = server time
DESYNC = 0


def calculate_desync(server_time):
    return int(RawJS("server_time - Math.round(Date.now() / 1000)"))


def current_server_time():
    return DESYNC + int(RawJS("Math.round(Date.now() / 1000)"))


def get_human_delay(timestamp):
    current_time = current_server_time()
    delay_seconds = int(current_time) - int(timestamp)
    if delay_seconds >= 3600:
        return ">1h"
    if delay_seconds > 60:
        return str(int(delay_seconds / 60)) + "m"
    return str(delay_seconds) + "s"


def start_task_update_timers():
    human_delay_func = get_human_delay
    return RawJS(
        """
        function() {
            setInterval(function() {
                var timers = document.getElementsByClassName("timer-update");
                for (var i = 0; i < timers.length; i++) {
                    var timerElem = timers[i];
                    if (timerElem.getAttribute("timestamp") != null) {
                        var timestamp = Number(timerElem.getAttribute("timestamp"));
                        timerElem.innerHTML = human_delay_func(timestamp);
                    }
                }
            }, 5000);
        }();
        """
    )
