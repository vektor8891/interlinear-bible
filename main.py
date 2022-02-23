# todo: create website for each chapter using strong numbers
# todo: highlight selected strong numbers based on google sheets

import lib.bible
import lib.database

con = lib.database.get_connection()
lib.bible.generate_chapter_content(con=con, chapter_ind=1)
lib.bible.generate_verses(con=con)
lib.bible.generate_toc(con=con)
con.close()
