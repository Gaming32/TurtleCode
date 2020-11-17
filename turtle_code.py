import turtle
from types import FunctionType
from typing import Generator, Iterable, Tuple


functions = {
    'goto': turtle.goto,
    'circle': turtle.circle,
    'wait': turtle.mainloop,
}


functions_types = {
    'goto': (['num', 'num'], {}),
    'circle': (['num'], {}),
    'wait': ([], {}),
}


def _parse_num(value):
    fresult = float(value)
    iresult = int(fresult)
    if iresult != fresult:
        return fresult
    return iresult

type_parsers = {
    'num': _parse_num,
}


def parse_single_line(line: str, debug: bool = False) -> Tuple[FunctionType, tuple, dict]:
    if not line.strip():
        if debug:
            print('turtle_code.py:21\tSkipping blank line:', repr(line))
        return (lambda: None), (), {}
    function, *args = line.split()
    if function in functions:
        argtypes, kwargtypes = functions_types[function]
        if len(args) > len(argtypes):
            if debug:
                print('turtle_code.py:14\tWarning: Got extra args:', repr(args[len(argtypes):]))
        args = list(args)
        for (i, (arg, argtype)) in enumerate(zip(args, argtypes)):
            args[i] = type_parsers[argtype](arg)
        return functions[function], tuple(args[:len(argtypes)]), {}
    if debug:
        print('turtle_code.py:14\tWarning: Got invalid function:', repr(function))
    return (lambda: None), (), {}


def parse_script(it: Iterable[str], debug: bool = False) -> Generator[Tuple[FunctionType, tuple, dict], None, None]:
    for line in it:
        if debug:
            print('turtle_code.py:21\tGot line:', repr(line))
        yield parse_single_line(line, debug=debug)


def run_script(script: Iterable[str], debug: bool = False) -> None:
    for (function, args, kwargs) in parse_script(script, debug=debug):
        if debug:
            print('turtle_code.py:28\tGot function:', repr(function), repr(args), repr(kwargs))
        function(*args)


def main():
    if len(sys.argv) < 2:
        fp = sys.stdin
    else:
        fp = open(sys.argv[1])
    with fp:
        run_script(fp, debug=True)


if __name__ == '__main__':
    import sys
    main()
