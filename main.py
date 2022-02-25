import lib.bible
import lib.database
import lib.globals

con = lib.database.get_connection()
lib.bible.update_chapters(con=con)
df_chapters = lib.database.get_table(con=con, table=lib.globals.db_chapters)
lib.bible.generate_chapters(df_chapters=df_chapters[0:2], con=con, selected_words=[])
lib.bible.generate_toc(df_chapters=df_chapters, con=con)
df_words = lib.database.get_table(con=con, table=lib.globals.db_words)
lib.bible.generate_words(df_words=df_words[9:10], con=con)
con.close()
