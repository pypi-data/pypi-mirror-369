import pandas as pd


def dtale_start(df: pd.DataFrame, precision=None) -> str:
    """利用Vscode端口映射启动dtale

    Args:
        df (pd.DataFrame): 目标DF

    Returns:
        str: dtale内部地址
    """
    import dtale
    d = dtale.show(df, precision=precision)
    # return f"http://localhost:{d._main_url.split(':')[-1]}"
    return [
        f"https://dtale.home.laye.wang:18443/dtale{d._main_url.split('dtale')[-1]}",
        f"http://192.168.1.85:{d._main_url.split(':')[-1]}"
    ]
