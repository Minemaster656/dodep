def error(msg: str, uclass: str = "", umsg: str = "") -> dict:
    out = {"message": msg}
    if uclass != "":
        out["class"] = uclass
    if umsg != "":
        out["user_message"] = umsg
    return out
