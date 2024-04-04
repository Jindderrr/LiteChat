DOMAINS = (".ru", ".рф", ".com", ".net", ".org", ".info", ".biz", ".online", ".shop", ".site", ".site", ".xyz", ".uk", ".de", ".cn", ".nl", ".br", ".au", ".fr", ".eu")

def format(msg):
    msg = list(msg)
    for n, w in enumerate(msg):
        if w == "<":
            msg[n] = "&lt;"
        elif w == ">":
            msg[n] = "&gt;"
    msg = "".join(msg)
    msg = msg.split(" ")
    for n, i1 in enumerate(msg):
        i = i1
        i.lower()
        for d in DOMAINS:
            ref = d in i
            if ref:
                if i.index(d) != 0:
                    msg[n] = '<a href=' + i + '>' + i + "</a>"
                    break
    msg = " ".join(msg)
    ch = {"\n": "<br>", "T^{": "<i>", "}^T": "</i>", "T-{": "<b>", "}-T": "</b>", "T_{": "<u>", "}_T": "</u>"}
    for i in ch:
        msg = msg.split(i)
        msg = ch[i].join(msg)
    return str(msg)