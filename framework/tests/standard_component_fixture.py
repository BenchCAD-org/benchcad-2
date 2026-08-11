from bench2.geomlib import make_iso_hex_bolt


def build(nominal_d, length, thread_length):
    result = make_iso_hex_bolt(
        nominal_d,
        length,
        thread_length,
        modeled_thread=1,
    )
    return result
