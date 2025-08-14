"""
XML utilities
"""


class XML:
    """
    A thin wrapper around [xmltodict]_.

    References:
        .. [xmltodict] https://pypi.org/project/xmltodict/

    Example:
        >>> # xdoctest: +REQUIRES(module:xmltodict)
        >>> from kwutil.util_xml import *  # NOQA
        >>> import ubelt as ub
        >>> text = ub.codeblock(
            '''
            <mydocument has="an attribute">
              <and>
                <many>elements</many>
                <many>more elements</many>
              </and>
              <plus a="complex">
                element as well
              </plus>
            </mydocument>
            ''')
        >>> data = XML.loads(text)
        >>> print(f'data = {ub.urepr(data, nl=-1)}')
        >>> recon = XML.dumps(data, pretty=True)
        >>> print(recon)
    """
    @staticmethod
    def loads(text, process_namespaces=False, backend='xmltodict'):
        import xmltodict
        data = xmltodict.parse(text, process_namespaces=process_namespaces)
        return data

    @staticmethod
    def load(file, process_namespaces=False, backend='xmltodict'):
        import xmltodict
        inferred_type = _infer_maybe_path_type(file, path_policy='always')
        if inferred_type == 'path':
            with open(file, 'rb') as file_:
                data = xmltodict.parse(file_, process_namespaces=process_namespaces)
        else:
            data = xmltodict.parse(file, process_namespaces=process_namespaces)
        return data

    @staticmethod
    def dump(data, fp, pretty=False, backend='xmltodict'):
        import xmltodict
        text = xmltodict.unparse(data, output=fp, pretty=pretty)
        return text

    @staticmethod
    def dumps(data, pretty=False, backend='xmltodict'):
        import xmltodict
        text = xmltodict.unparse(data, pretty=pretty)
        return text


def _infer_maybe_path_type(maybe_path, path_policy='existing_file_with_extension'):
    """
    input might be a pathlib object, a string that represents a path, a string
    that represents text, an open file, or some other unknown object.
    """
    import os
    inferred_type = None

    if isinstance(maybe_path, os.PathLike):
        inferred_type = 'path'
    elif isinstance(maybe_path, str):
        if path_policy == 'always':
            inferred_type = 'path'
        elif path_policy == 'never' or '\n' in maybe_path or not maybe_path.strip():
            inferred_type = 'text'
        else:
            path_requires_extension = path_policy == 'existing_file_with_extension'
            if os.path.isfile(maybe_path):
                inferred_type = 'path' if not path_requires_extension or '.' in os.path.basename(maybe_path) else 'text'
            else:
                inferred_type = 'text'
    elif hasattr(maybe_path, 'read'):
        inferred_type = 'file'

    return inferred_type
