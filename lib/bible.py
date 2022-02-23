import os.path
import sqlite3

import pandas as pd

import lib.database
import lib.globals


def generate_toc(con: sqlite3.Connection):
    chapters = generate_toc_chapter_links(con=con)

    toc = """<!DOCTYPE html>
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
    with open(lib.globals.index_url, 'w') as f:
        f.write(toc)


def generate_toc_chapter_links(con: sqlite3.Connection):
    df_chapters = lib.database.get_table(con=con, table=lib.globals.db_chapters)
    book = None
    html = ""
    for i, row in df_chapters.iterrows():
        if pd.isnull(book):
            html = "<p>"
        if row["book"] != book:
            if not pd.isnull(book):
                html = "{0}</p><p>".format(html)
            book = row["book"]
            book_title = " ".join([v.title() for v in book.split("_")])
            html = "{0}{1}:".format(html, book_title)
        chapter = row["chapter"]
        url = os.path.join(lib.globals.chapters_folder, f"{chapter}.html")
        html = '{0} <a href="{1}">{2}</a>'.format(html, url, chapter)
    html = "{0}</p>".format(html)
    return html


def generate_verses(con: sqlite3.Connection):
    df_chapters = lib.database.get_table(con=con, table=lib.globals.db_chapters)
    for i, row in df_chapters[0:1].iterrows():
        verses = generate_chapter_content(con=con, chapter_ind=row['ind'])
        book_title = " ".join([v.title() for v in row["book"].split("_")])
        chapter = row['chapter']
        chapter_prev = max(df_chapters['ind']) if row["ind"] == 1 else row["ind"] - 1
        chapter_next = 1 if row["ind"] == max(df_chapters['ind']) else row["ind"] + 1
        index_url = lib.globals.index_url
        html = '''<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <title>{book_title} {chapter}</title>
    <style type="text/css" media="Screen">
        sub {{
            vertical-align: sub;
            font-size: 0.6em;
        }}
    </style>
</head>

<body>
    <h1>{book_title} {chapter}</h1>
    <p><a href="{chapter_prev}.html">< Previous</a>&nbsp;
    <a href="../{index_url}">Home</a>&nbsp;
    <a href="{chapter_next}.html">Next ></a></p> 
    {verses}
</body>

</html>
'''.format(book_title=book_title, chapter=chapter, verses=verses, chapter_next=chapter_next, chapter_prev=chapter_prev,
           index_url=index_url)
        f_path = os.path.join(lib.globals.chapters_folder, f"{row['ind']}.html")
        with open(f_path, 'w') as f:
            f.write(html)


def generate_chapter_content(con: sqlite3.Connection, chapter_ind: int):
    df_all = lib.database.get_table(con=con, table=lib.globals.db_interlinear)
    df_chapter = df_all[df_all["chapter_ind"] == chapter_ind].copy()
    df_chapter['verse'] = df_chapter['verse'].astype(int)
    df_chapter['word_order'] = df_chapter['word_order'].astype(int)
    df_chapter.sort_values(by=["verse", "word_order"], inplace=True)
    verse = None
    html = ""
    for i, row in df_chapter.iterrows():
        if pd.isnull(verse):
            html = "<p>"
        if row["verse"] != verse:
            if not pd.isnull(verse):
                html = "{0}</p><p>".format(html)
            verse = row["verse"]
            html = "{0}{1}:".format(html, verse)
        punct = "" if pd.isnull(row["punct"]) else row["punct"]
        word = row["word_eng"]
        strong = row["strong_id"]
        html = '{0} {1}{2}<sub>{3}</sub>'.format(html, word, punct, strong)
    html = "{0}</p>".format(html)
    return html
