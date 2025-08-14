"""
Defines a safer eval function. See references for related work. It is possible
that one of those libraries may be better suited.

We currently vendor code from [evalidate]_.

References:
    .. [pure-eval] https://pypi.org/project/pure-eval/
    .. [safeeval] https://pypi.org/project/safeeval/
    .. [evalidate] https://pypi.org/project/evalidate/
    .. [PythonSafeEval] https://pypi.org/project/PythonSafeEval/
    .. [numexpr] https://pypi.org/project/numexpr/2.6.1/
"""
import ast


class RestrictedSyntaxError(Exception):
    """
    An exception raised by restricted_eval if a disallowed expression is given
    """


def restricted_eval(expr, max_chars=32, local_dict=None, builtins_passlist=None):
    """
    A restricted form of Python's eval that is meant to be slightly safer

    Args:
        expr (str): the expression to evaluate
        max_char (int): expression cannot be more than this many characters
        local_dict (Dict[str, Any]): a list of variables allowed to be used
        builtins_passlist (List[str] | None) : if specified, only allow use of certain builtins

    References:
        https://realpython.com/python-eval-function/#minimizing-the-security-issues-of-eval

    Notes:
        This function may not be safe, but it has as many mitigation measures
        that I know about. This function should be audited and possibly made
        even more restricted. The idea is that this should just be used to
        evaluate numeric expressions.

    Example:
        >>> from kwutil.util_eval import *  # NOQA
        >>> builtins_passlist = ['min', 'max', 'round', 'sum']
        >>> local_dict = {}
        >>> max_chars = 32
        >>> expr = 'max(3 + 2, 9)'
        >>> result = restricted_eval(expr, max_chars, local_dict, builtins_passlist)
        >>> expr = '3 + 2'
        >>> result = restricted_eval(expr, max_chars, local_dict, builtins_passlist)
        >>> expr = '3 + 2'
        >>> result = restricted_eval(expr, max_chars)
        >>> import pytest
        >>> with pytest.raises(RestrictedSyntaxError):
        >>>     expr = 'max(a + 2, 3)'
        >>>     result = restricted_eval(expr, max_chars, dict(a=3))
    """
    import builtins
    if type(expr) is not str:
        raise TypeError(f'expr must be a pure str. Got {type(expr)}')
    if len(expr) > max_chars:
        raise RestrictedSyntaxError(
            'num-workers-hueristic should be small text. '
            'We want to disallow attempts at crashing python '
            'by feeding nasty input into eval. But this may still '
            'be dangerous.'
        )
    if local_dict is None:
        local_dict = {}

    if builtins_passlist is None:
        builtins_passlist = []

    _builtins_passlist = set(builtins_passlist)
    allowed_builtins = {k: v for k, v in builtins.__dict__.items()
                        if k in _builtins_passlist}

    local_dict['__builtins__'] = allowed_builtins
    allowed_names = list(allowed_builtins.keys()) + list(local_dict.keys())
    code = compile(expr, "<string>", "eval")
    # Step 3
    for name in code.co_names:
        if name not in allowed_names:
            raise RestrictedSyntaxError(f"Use of {name} not allowed")
    # result = eval(code, local_dict, local_dict)

    result = safeeval(expr, local_dict, addnodes=['Call'],
                      funcs=builtins_passlist)

    return result


class EvalException(Exception):
    ...


class ValidationException(EvalException):
    ...


class CompilationException(EvalException):
    exc = None
    def __init__(self, exc):
        super().__init__(exc)
        self.exc = exc


class ExecutionException(EvalException):
    exc = None
    def __init__(self, exc):
        super().__init__(exc)
        self.exc = exc


class SafeAST(ast.NodeVisitor):

    """AST-tree walker class."""

    allowed = {}

    def __init__(self, safenodes=None, addnodes=None, funcs=None, attrs=None):
        """create whitelist of allowed operations."""
        if safenodes is not None:
            self.allowed = safenodes
        else:
            """
            To generate these:

                # Get all subclasses of ast.AST recursively
                nodes = set()

                def recurse(cls):
                    nodes.add(cls.__name__)
                    for subclass in cls.__subclasses__():
                        recurse(subclass)

                blocklist = {
                    # Base classes / abstract or special typing constructs not actual AST nodes
                    'AST',             # base class, not a node type itself
                    'EnhancedAST',     # not a standard ast node (likely custom or invalid)

                    # Typing / parameter constructs, not AST nodes
                    'ParamSpec',
                    'TypeAlias',
                    'TypeIgnore',
                    'TypeVar',
                    'TypeVarTuple',
                    'Param',
                    'type_param',
                    'type_ignore',

                    # Possibly ambiguous or internal helpers (not node classes)
                    'AugLoad',
                    'AugStore',

                    # Special pseudo nodes or deprecated
                    'FunctionType',  # not an AST node
                    'Suite',         # does not exist in Python ast

                    # Others that are unlikely to be AST nodes
                    'Div',           # should be 'Div' operator but actually no class named Div; it's 'Div' operator type
                }
                recurse(ast.AST)
                final_list = [n for n in nodes if n not in blocklist and n.lower() != n]
                print(f'final_list = {ub.urepr(final_list, nl=1)}')

                [
                'Not', 'YieldFrom', 'Pass', 'BitAnd', 'DictComp', 'TryStar',
                'LShift', 'Dict', 'AsyncWith', 'Num', 'MatMult', 'BinOp',
                'AsyncFor', 'Ellipsis', 'MatchClass', 'NotIn', 'Del',
                'MatchValue', 'GtE', 'ClassDef', 'Slice', 'NotEq', 'Constant',
                'Starred', 'UAdd', 'Compare', 'Break', 'FloorDiv',
                'GeneratorExp', 'Assert', 'Global', 'RShift', 'Set', 'Match',
                'Str', 'UnaryOp', 'While', 'Add', 'MatchStar', 'AugAssign',
                'Interactive', 'MatchSingleton', 'Is', 'Return', 'Expression',
                'Lt', 'Attribute', 'Name', 'USub', 'Call', 'Continue', 'Await',
                'Import', 'Nonlocal', 'BitOr', 'ListComp', 'Raise', 'Bytes',
                'Mod', 'Lambda', 'If', 'Sub', 'Index', 'BoolOp', 'Module',
                'MatchAs', 'AnnAssign', 'And', 'MatchSequence', 'IsNot',
                'Delete', 'Load', 'LtE', 'FunctionDef', 'Subscript', 'List',
                'FormattedValue', 'Invert', 'Yield', 'ImportFrom', 'Expr',
                'BitXor', 'SetComp', 'Try', 'NameConstant', 'Pow', 'IfExp',
                'With', 'Mult', 'ExtSlice', 'NamedExpr', 'MatchOr',
                'ExceptHandler', 'For', 'Or', 'MatchMapping', 'In', 'Assign',
                'Store', 'Gt', 'AsyncFunctionDef', 'Tuple', 'Eq', 'JoinedStr',
                ]

            """

            # 123, 'asdf'
            values = ['Num', 'Str']
            # any expression or constant
            expression = ['Expression']
            constant = ['Constant', 'NameConstant']
            # == ...
            compare = ['Compare', 'Eq', 'NotEq', 'Gt', 'GtE', 'Lt', 'LtE']
            # variable name
            variables = ['Name', 'Load']
            binop = ['BinOp']
            arithmetics = ['Add', 'Sub', 'Mult', 'Div', 'FloorDiv', 'Mod', 'Pow', 'MatMult']  # added common arith ops, including MatMult and FloorDiv
            subscript = ['Subscript', 'Index', 'Slice']  # person['name']
            boolop = ['BoolOp', 'And', 'Or', 'UnaryOp', 'Not', 'Invert', 'UAdd', 'USub']  # added Invert and unary +/-
            inop = ["In", "NotIn"]  # "aaa" in i['list']
            ifop = ["IfExp"]  # for if expressions, like: expr1 if expr2 else expr3
            div = ["Div", "Mod", "FloorDiv"]

            self.allowed = expression + constant + values + compare + \
                variables + binop + arithmetics + subscript + boolop + \
                inop + ifop + div

        self.allowed_funcs = funcs or list()
        self.allowed_attrs = attrs or list()

        if addnodes is not None:
            self.allowed = self.allowed + addnodes

    def generic_visit(self, node):
        """Check node, raise exception if node is not in whitelist."""

        if type(node).__name__ in self.allowed:

            if isinstance(node, ast.Attribute):
                if node.attr not in self.allowed_attrs:
                    raise ValidationException(
                        "Attribute {aname} is not allowed".format(
                            aname=node.attr))

            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id not in self.allowed_funcs:
                        raise ValidationException(
                            "Call to function {fname}() is not allowed".format(
                                fname=node.func.id))
                    else:
                        # Call to allowed function. good. No exception
                        pass
                elif isinstance(node.func, ast.Attribute):
                    pass
                    # print("attr:", node.func.attr)
                else:
                    raise ValidationException('Indirect function call')

            ast.NodeVisitor.generic_visit(self, node)
        else:
            raise ValidationException(
                "Operation type {optype} is not allowed".format(
                    optype=type(node).__name__))


def evalidate(expression, safenodes=None, addnodes=None, funcs=None, attrs=None):
    """Validate expression.

    return node if it passes our checks
    or pass exception from SafeAST visit.
    """
    try:
        node = ast.parse(expression, '<usercode>', 'eval')
    except SyntaxError as e:
        raise CompilationException(e)

    v = SafeAST(safenodes, addnodes, funcs, attrs)
    v.visit(node)
    return node


def safeeval(expression, context={}, safenodes=None, addnodes=None, funcs=None, attrs=None):
    """C-style simplified wrapper, eval() replacement.

    Args:
        expr (str): the expression to evaluate

        context (dict):
            Optional dictionary of variables to make available during evaluation.

        safenodes (List[str] | None):
            Specify the name of allowed AST nodes, if unspecified a default list is used.

        addnodes (List[str] | None):
            List of additional AST node names to allow in addition to safenodes.

        funcs (List[str]):
            list of allowed function names.

        attrs (List[str]):
            list of allowed attribute names.

    Returns:
        Any: the result of the expression

    Raises:
        ExecutionException - if the expression fails to execute
        CompilationException - if the expression fails to parse
        ValidationException - if the expression fails safety checks

    Example:
        >>> from kwutil.util_eval import safeeval
        >>> safeeval('3 + 2')
        5
        >>> safeeval('max(3, 2)', addnodes=['Call'], funcs=['max'])
        3
        >>> safeeval('x * 2', context={'x': 5})
        10
        >>> safeeval('len(lst)', context={'lst': [1, 2, 3]}, addnodes=['Call'], funcs=['len'])
        3
        >>> safeeval('obj.value', context={'obj': type("O", (), {"value": 42})()}, addnodes=['Attribute'], attrs=['value'])
        42
        >>> import pytest
        >>> with pytest.raises(ValidationException):
        ...     safeeval('exec("import os")')
        >>> with pytest.raises(ValidationException):
        ...     safeeval('os.system("ls")', context={'os': __import__('os')}, addnodes=['Call', 'Attribute'], funcs=[])
    """

    # ValidationException thrown here
    node = evalidate(expression, safenodes, addnodes, funcs, attrs)

    code = compile(node, '<usercode>', 'eval')

    wcontext = context.copy()
    try:
        result = eval(code, wcontext)
    except Exception as e:
        raise ExecutionException(e)

    return result
