# todo: create website for each chapter using strong numbers
# todo: highlight selected strong numbers based on google sheets

import lib.bible
import lib.database
import lib.globals

con = lib.database.get_connection()
df_chapters = lib.database.get_table(con=con, table=lib.globals.db_chapters)
lib.bible.generate_chapters(df_chapters=df_chapters[0:1], con=con)
# lib.bible.generate_chapters(df_chapters=df_chapters[0:2], con=con)
lib.bible.generate_toc(df_chapters=df_chapters, con=con)
df_words = lib.database.get_table(con=con, table=lib.globals.db_words)
lib.bible.generate_words(df_words=df_words[921:922], con=con)
# lib.bible.generate_words(df_words=df_words[9907:9909], con=con)
con.close()
