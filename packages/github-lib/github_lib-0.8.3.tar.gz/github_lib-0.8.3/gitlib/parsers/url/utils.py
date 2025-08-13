import re


def clean_commit_url(ref: str) -> str:
    """
        Normalizes commit reference
    """
    if "CONFIRM:" in ref:
        # e.g., https://github.com/{owner}/{repo}/commit/{sha}CONFIRM:
        ref = ref.replace("CONFIRM:", '')

    if 'git://' in ref and 'github.com' in ref:
        ref = ref.replace('git://', 'https://')

    if '#' in ref and ('#comments' in ref or '#commitcomment' in ref):
        # e.g., https://github.com/{owner}/{repo}/commit/{sha}#commitcomment-{id}
        ref = ref.split('#')[0]

    if '.patch' in ref:
        # e.g., https://github.com/{owner}/{repo}/commit/{sha}.patch
        ref = ref.replace('.patch', '')
    if '%23' in ref:
        # e.g., https://github.com/absolunet/kafe/commit/c644c798bfcdc1b0bbb1f0ca59e2e2664ff3fdd0%23diff
        # -f0f4b5b19ad46588ae9d7dc1889f681252b0698a4ead3a77b7c7d127ee657857
        ref = ref.replace('%23', '#')

    # the #diff part in the url is used to specify the section of the page to display, for now is not relevant
    if "#diff" in ref:
        ref = ref.split("#")[0]
    if "?w=1" in ref:
        ref = ref.replace("?w=1", "")
    if "?branch=" in ref:
        ref = ref.split("?branch=")[0]
    if "?diff=split" in ref:
        ref = ref.replace("?diff=split", "")
    if re.match(r".*(,|/)$", ref):
        if "/" in ref:
            ref = ref[0:-1]
        else:
            ref = ref.replace(",", "")
    elif ")" in ref:
        ref = ref.replace(")", "")

    return ref
