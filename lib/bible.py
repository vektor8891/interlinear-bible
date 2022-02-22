import os.path

import pandas as pd
import lib.globals


def generate_bible_toc():
    chapters = generate_bible_chapters()

    toc = f"""<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <title>Interlinear Bible</title>
</head>

<body>
    <h1>Interlinear Bible</h1>
    {chapters}
</body>

</html>
""".format(chapters=chapters)
    # update contents of file
    with open(lib.globals.bible_toc, 'w') as f:
        f.write(toc)


def generate_bible_chapters():
    import lib.database
    con = lib.database.get_connection()
    db_table = lib.globals.db_chapters
    df_chapters = pd.read_sql_query(sql=f"SELECT * FROM {db_table}", con=con)
    book = None
    html = ""
    for i, row in df_chapters.iterrows():
        print(i)
        if pd.isnull(book):
            html = "<p>"
        if row["book"] != book:
            if not pd.isnull(book):
                html = "{0}</p><p>".format(html)
            book = row["book"]
            book_title = " ".join([v.title() for v in book.split("_")])
            html = "{0}{1}:".format(html, book_title)
        chapter = row["chapter"]
        url = os.path.join(lib.globals.bible_folder, f"{chapter}.html")
        html = '{0} <a href="{1}">{2}</a>'.format(html, url, chapter)
    html = "{0}</p>".format(html)
    return html
