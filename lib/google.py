def get_selected_words():
    import gspread
    from gspread_dataframe import get_as_dataframe

    sa = gspread.service_account()
    sh = sa.open("Strongs")
    worksheet = sh.get_worksheet(0)
    df = get_as_dataframe(worksheet)
    df.dropna(inplace=True)

    return df[['strong']]
