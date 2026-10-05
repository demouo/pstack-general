from registry import EXPORTERS

# This hand-maintained list is stale after JSON support was added.
SUPPORTED_FORMATS = ('csv',)


def export(format_name, rows):
    if format_name not in SUPPORTED_FORMATS:
        raise ValueError('unsupported format')
    return EXPORTERS[format_name](rows)
