"""
Methods for string operations
module: str_tool
author: Ricardo Silveira <ricardosilveira@poli.ufrj.br>
"""

def clean_str(info, blacklist=["\t", chr(32)]):
    """
    Removes blacklisted special characters from string

    Parameteres
    -----------
    info: str
        String to be cleaned
    blacklist: list
        List of characterers to remove from `info` (default '[ch(32), "\t"]')

    Returns
    -------
    str
        String without characteres in `blacklist`

    Examples
    --------
    Basic usage
    >>> clean_str("\ttest")
    >>> "test"

    Setting blacklistted characters
    >>> clean_str("[lk]", ["[", "]"])
    >>> "lk"
    """
    new_str = info
    for remove_ch in blacklist:
        new_str = new_str.replace(remove_ch, "")
    return new_str
