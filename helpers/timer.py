#encoding: UTF-8
from libs.timer import Timer

_instance = None

def instance(every=None):
    global _instance
    if not _instance:
        if every:
            _instance = Timer(every)
            _instance.start()
            print("Timers started to loop every", every, "s")
        else:
            raise ValueError("No timer set up.")
    return _instance


