import lib.globals


def generate_bible_toc():
    toc = f"""<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <title>Interlinear Bible</title>
</head>

<body>
    <h1>Interlinear Bible</h1>
    <p>hello world</p>
</body>

</html>
"""
    # update contents of file
    with open(lib.globals.bible_toc, 'w') as f:
        f.write(toc)
