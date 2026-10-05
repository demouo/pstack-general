def csv_export(rows):
    return '\n'.join(rows)


def json_export(rows):
    import json
    return json.dumps(rows)


EXPORTERS = {'csv': csv_export, 'json': json_export}
