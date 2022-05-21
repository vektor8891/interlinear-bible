import os.path
import sqlite3

import pandas as pd

import lib.database
import lib.globals


def generate_toc(df_chapters: pd.DataFrame, con: sqlite3.Connection):
    book = None
    chapters = ""
    print("Generate TOC")
    for i, row in df_chapters.iterrows():
        if pd.isnull(book):
            chapters = "<p>"
        if row["book"] != book:
            if not pd.isnull(book):
                chapters = f"{chapters}</p><p>"
            book = row["book"]
            book_title = " ".join([v.title() for v in book.split("_")])
            chapters = f"{chapters}{book_title}:"
        chapter = row["chapter"]
        url = os.path.join(lib.globals.chapters_folder, f"{row['ind']}.html")
        chapters = f'{chapters} <a href="{url}">{chapter}</a>'
    chapters = f"{chapters}</p>"

    with open(lib.globals.template_path, 'r') as f_template:
        template = f_template.read().replace('\n', '')
        toc = template.format(title="Interlinear Bible",
                              index_url=lib.globals.index_url,
                              index_words_url=lib.globals.index_words_url,
                              header="Interlinear Bible",
                              content=chapters,
                              path="")

        # update contents of file
        with open(lib.globals.index_url, 'w') as f_toc:
            f_toc.write(toc)


def generate_chapters(df_chapters: pd.DataFrame, con: sqlite3.Connection, selected_words: list):
    for i, row in df_chapters.reset_index().iterrows():
        verses = generate_chapter_content(con=con, chapter_ind=row['ind'], selected_words=selected_words)
        book_title = " ".join([v.title() for v in row["book"].split("_")])
        chapter = row['chapter']
        print(f"Generate html for {book_title} {chapter} ({i + 1}/{len(df_chapters)})")
        chapter_prev = 1189 if row["ind"] == 1 else row["ind"] - 1
        chapter_next = 1 if row["ind"] == 1189 else row["ind"] + 1

        with open(lib.globals.template_path, 'r') as f_template:
            template = f_template.read().replace('\n', '')
            title = f'{book_title} {chapter}'
            content = f'<p><a href="{chapter_prev}.html">< Previous</a>&nbsp;&nbsp;' \
                      f'<a href="../{lib.globals.index_url}">Home</a>&nbsp;&nbsp;' \
                      f'<a href="{chapter_next}.html">Next ></a></p>' \
                      f'{verses}'
            html = template.format(title=title,
                                   header=title,
                                   content=content,
                                   path="../")

            f_path = os.path.join(lib.globals.chapters_folder, f"{row['ind']}.html")
            with open(f_path, 'w') as f:
                f.write(html)


def generate_chapter_content(con: sqlite3.Connection, chapter_ind: int, selected_words: list):
    df_all = lib.database.get_table(con=con, table=lib.globals.db_interlinear)
    df_words = lib.database.get_table(con=con, table=lib.globals.db_words)
    df_chapter = df_all[df_all["chapter_ind"] == chapter_ind].copy()
    verse = None
    html = "<p>"
    for i, row in df_chapter.iterrows():
        if row["verse"] != verse:
            if not pd.isnull(verse):
                html = f"{html}</p><p>"
            verse = row["verse"]
            html = f'{html}<strong id="{verse}">{verse}</strong>:'
        punct = "" if pd.isnull(row["punct"]) else row["punct"]
        strong = row["strong_id"]
        word = row["word_eng"] if strong not in selected_words else f'<mark>{row["word_eng"]}</mark>'
        if strong != "H0000":
            strong_ind = df_words.loc[df_words['strong_id'] == row["strong_id"]].ind.values[0]
            html = f'{html} {word}{punct}<sub><a href="../{lib.globals.words_folder}/{strong_ind}.html">' \
                   f'{strong}</a></sub>'
    html = f"{html}</p>"
    return html


def generate_words(df_words: pd.DataFrame, con: sqlite3.Connection):
    for i, row in df_words.iterrows():
        strong_id = row["strong_id"]
        translit = row['transliteration']
        definition = row['definition']
        print(f"Generate occurrences for {strong_id}")
        strong_prev = 14298 if row["ind"] == 1 else row["ind"] - 1
        strong_next = 1 if row["ind"] == 14298 else row["ind"] + 1
        strong_html = generate_occurrences(strong_id=strong_id, con=con)

        with open(lib.globals.template_path, 'r') as f_template:
            template = f_template.read().replace('\n', '')
            title = f'{strong_id}: {definition}'
            header = f'{strong_id}: {translit} - {definition}'
            content = f'<p><a href="{strong_prev}.html">< Previous</a>&nbsp;&nbsp;' \
                      f'<a href="../{lib.globals.index_url}">Home</a>&nbsp;&nbsp;' \
                      f'<a href="{strong_next}.html">Next ></a></p>' \
                      f'{strong_html}'
            html = template.format(title=title,
                                   header=header,
                                   content=content,
                                   path="../")

            f_path = os.path.join(lib.globals.words_folder, f"{row['ind']}.html")
            with open(f_path, 'w') as f:
                f.write(html)


def generate_occurrences(strong_id: str, con: sqlite3.Connection):
    df_verses = lib.database.get_table(con=con, table=lib.globals.db_interlinear)
    df_books = lib.database.get_table(con=con, table=lib.globals.db_chapters)
    df_chapters = df_verses[df_verses["strong_id"] == strong_id]
    html = ""
    for i, row in df_chapters.iterrows():
        df_book = df_books.loc[df_books['ind'] == row["chapter_ind"]]
        book = df_book.iloc[0].book
        chapter = df_book.iloc[0].chapter
        book_title = " ".join([v.title() for v in book.split("_")])
        df_verse = df_verses[(df_verses["chapter_ind"] == row["chapter_ind"]) & (df_verses["verse"] == row['verse'])]
        verse_html = generate_verse(df_verse=df_verse, con=con, strong_id=strong_id)
        html = f'{html}<p><strong><a href="../{lib.globals.chapters_folder}/{row["chapter_ind"]}.html' \
               f'#{row["verse"]}">{book_title} {chapter}:{row["verse"]}</a></strong> {verse_html}</p>'
    return html


def generate_verse(df_verse: pd.DataFrame, con: sqlite3.Connection, strong_id: str):
    df_words = lib.database.get_table(con=con, table=lib.globals.db_words)
    html = ""
    for i, row in df_verse.iterrows():
        punct = "" if pd.isnull(row["punct"]) else row["punct"]
        strong = row["strong_id"]
        if strong != "H0000":
            word = f'<mark>{row["word_eng"]}</mark>' if strong_id == strong else row["word_eng"]
            strong_ind = df_words.loc[df_words['strong_id'] == row["strong_id"]].ind.values[0]
            html = f'{html} {word}{punct}<sub>' \
                   f'<a href="../{lib.globals.words_folder}/{strong_ind}.html">{strong}</a></sub>'
    return html


def update_chapters(con: sqlite3.Connection):
    import lib.google
    # find list of selected words
    df_new_words = lib.google.get_selected_words()  # from Google sheet
    df_old_words = pd.read_csv(lib.globals.selected_words_path)  # from local file
    words_to_add = df_new_words[~df_new_words['strong'].isin(df_old_words['strong'].values)]
    words_to_remove = df_old_words[~df_old_words['strong'].isin(df_new_words['strong'].values)]
    words_to_change = pd.concat([words_to_add, words_to_remove])['strong'].values

    # get list of affected chapters
    df_verses = lib.database.get_table(con=con, table=lib.globals.db_interlinear)
    df_verses_filt = df_verses.loc[df_verses["strong_id"].isin(words_to_change)]
    df_chapters = lib.database.get_table(con=con, table=lib.globals.db_chapters)
    df_chapters_filt = df_chapters[df_chapters['ind'].isin(df_verses_filt['chapter_ind'].values)]
    generate_chapters(df_chapters=df_chapters_filt, con=con, selected_words=df_new_words['strong'].values)

    # save new list
    df_new_words.to_csv(lib.globals.selected_words_path, index=False)
