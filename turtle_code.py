import turtle
from types import FunctionType
from typing import Generator, Iterable, Tuple


def _begin_capture_state(name, state):
    state[None] = name

def _end_capture_state(state: dict):
    if None in state:
        del state[None]


functions = {
    # Move and draw
    'forward': turtle.forward,
    'back': turtle.back,
    'right': turtle.right,
    'left': turtle.left,
    'goto': turtle.goto,
    'setx': turtle.setx,
    'sety': turtle.sety,
    'setheading': turtle.setheading,
    'home': turtle.home,
    'circle': turtle.circle,
    'dot': turtle.dot,
    'stamp': turtle.stamp,
    'clearstamp': turtle.clearstamp,
    'clearstamps': turtle.clearstamps,
    'undo': turtle.undo,
    'speed': turtle.speed,

    'wait': turtle.mainloop,

    'capture': _begin_capture_state,
    'endcapture': _end_capture_state,
}


duplicates = {
    'fd': 'forward',
    'bk': 'back',
    'backward': 'back',
    'rt': 'right',
    'lt': 'left',
    'setpos': 'goto',
    'setpositon': 'goto',
    'seth': 'setheading',

    'cap': 'capture',
    'nocap': 'endcapture',
}


functions_types = {
    'forward': (['num'], 1, {}),
    'back': (['num'], 1, {}),
    'right': (['num'], 1, {}),
    'left': (['num'], 1, {}),
    'goto': (['num', 'num'], 2, {}),
    'setx': (['num'], 1, {}),
    'sety': (['num'], 1, {}),
    'setheading': (['num'], 1, {}),
    'home': ([], 0, {}),
    'circle': (['num', 'num', 'num'], 1, {}),
    'dot': (['num', 'color'], 0, {}),
    'stamp': ([], 0, {}),
    'clearstamp': (['num'], 1, {}),
    'clearstamps': (['num'], 0, {}),
    'undo': ([], 0, {}),
    'speed': (['num?raw'], 0, {}),

    'wait': ([], 0, {}),

    'capture': (['raw', 'state'], 1, {}),
    'endcapture': (['state'], 0, {}),
}


def _parse_num(value, state):
    fresult = float(value)
    iresult = int(fresult)
    if iresult != fresult:
        return fresult
    return iresult

def _parse_color(value: str, state):
    if value.startswith('rgb(') and value.endswith(')'):
        return tuple(_parse_num(sub, state=state) for sub in value[4:-1].split(','))
    return value

type_parsers = {
    'num': _parse_num,
    'color': _parse_color,
    'state': (lambda x, state: state),
    'raw': (lambda value, y: value),
}


def parse_argstr(argtype: str, arg: str, state: dict = None):
    if arg.startswith('cap::') and state is not None:
        return state.get(arg[5:])
    if '?' in argtype:
        for subtype in argtype.split('?'):
            try:
                result = parse_argstr(subtype, arg, state=state)
            except Exception:
                continue
            else:
                return result
    return type_parsers[argtype](arg, state)


def parse_single_line(line: str, state=None, debug: bool = False) -> Tuple[FunctionType, tuple, dict]:
    if not line.strip():
        if debug:
            print('turtle_code.py:21\tSkipping blank line:', repr(line))
        return (lambda: None), (), {}
    function, *args = line.split()
    if function in duplicates:
        function = duplicates[function]
    if function in functions:
        argtypes, pargcount, kwargtypes = functions_types[function]
        if len(args) > len(argtypes):
            if debug:
                print('turtle_code.py:14\tWarning:', repr(function), 'got extra args:', repr(args[len(argtypes):]))
        elif len(args) < pargcount:
            if debug:
                print('turtle_code.py:14\tWarning:', repr(function), 'missing', pargcount - len(args), 'args')
        else:
            args = list(args)
            for (i, (arg, argtype)) in enumerate(zip(args, argtypes)):
                args[i] = parse_argstr(argtype, arg, state=state)
            for argtype in argtypes[pargcount:]:
                if argtype == 'state':
                    args.append(state)
            return functions[function], tuple(args), {}
    if debug:
        print('turtle_code.py:14\tWarning: Got invalid function:', repr(function))
    return (lambda: None), (), {}


def parse_script(it: Iterable[str], state=None, debug: bool = False) -> Generator[Tuple[FunctionType, tuple, dict], None, None]:
    for line in it:
        if debug:
            print('turtle_code.py:21\tGot line:', repr(line))
        yield parse_single_line(line, state=state, debug=debug)


def run_script(script: Iterable[str], state=None, debug: bool = False) -> None:
    if state is None:
        state = {}
    for (function, args, kwargs) in parse_script(script, state=state, debug=debug):
        if debug:
            print('turtle_code.py:28\tGot function:', repr(function), repr(args), repr(kwargs))
        ret = function(*args)
        if state.get(None):
            state[state[None]] = ret
            if debug:
                print('turtle_code.py:28\tCopied value', repr(ret), 'to state var', repr(state[None]))


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
