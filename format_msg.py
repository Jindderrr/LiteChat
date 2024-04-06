def format(msg):
    msg = list(msg)
    for n, w in enumerate(msg):
        if w == "<":
            msg[n] = "&lt;"
        elif w == ">":
            msg[n] = "&gt;"
    msg = "".join(msg)
    return str(msg)
