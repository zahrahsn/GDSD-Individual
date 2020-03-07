def dictfetchall(cursor):
    """Return all rows from a cursor as a dict"""
    desc = cursor.description
    columns = []
    for i in desc:
        columns.append(i[0])
    records = cursor.fetchall()
    result = []
    for rec in records:
        result.append(dict(zip(columns, rec)))

    return result
