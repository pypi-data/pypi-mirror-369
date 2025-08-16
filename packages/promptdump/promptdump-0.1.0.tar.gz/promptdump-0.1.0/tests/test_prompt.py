import argparse
from promptdump import make_prompt


def test_prompt():
    args = argparse.Namespace(
        directory=".", extensions=[".py", ".md"], output="-", exclude=".gitignore", verbose=False, files=[]
    )
    result = make_prompt(args)
    assert len(result) > 10_000
