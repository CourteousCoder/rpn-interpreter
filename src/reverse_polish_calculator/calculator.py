from typing import List

from .operator import Operator, pure_operations
from .token import Token, TokenType
import bitstring
import re


def float_to_bin(x):
    sign = '-' if x < 0 else ''
    return sign + bitstring.BitArray(float=abs(x)).bin


def float_to_oct(x):
    sign = '-' if x < 0 else ''
    return sign + bitstring.BitArray(float=abs(x)).oct


def identity(x):
    return x


class Calculator:
    def __init__(self, display_mode_number_base=10, scripting=False):
        self._show_stack = False
        self._display_mode_number_base = 0
        self.set_display_mode_number_base(display_mode_number_base)
        self._clear_stack()
        self._clear_symbols()
        self.operations = {}
        self._include_operation_groups(pure_operations.values())
        if scripting:
            self._include_operation_groups(self._get_scripting_operations().values())

    def set_display_mode_number_base(self, base):
        options = (2, 8, 10, 16)
        if base not in options:
            options = ', '.join(options)
            raise ValueError(f'Unsupported number base: {base}. Please use any one of: {options}.')
        self._display_mode_number_base = base

    def format_stack(self) -> List[str]:
        return [self._format_output(item) for item in self._stack]

    def evaluate(self, expression_string) -> str:
        """
        Evaluates the given expression_string thus:

        Preprocess any macro definitions.
        Parse the expresion into a stack of tokens.
        Pop off items from the token stack, expanding references to defined macros.
        Values are pushed to the memory stack.
        Operators pop values from the memory stack and push their return values (if any)

        :param expression_string:
        :return: The top value of the memory stack, formatted as a string.
        """
        expression_string = self._preprocess_comments(expression_string).strip()
        expression_string = self._preprocess_macros(expression_string).strip()
        tokens = Token.parse_expression(expression_string, self.operations)

        # Reverse the list because Python appends and removes from the end more efficiently than from the beginning.
        tokens = tokens[::-1]
        while tokens:
            contents, token_type = tuple(tokens.pop())
            if token_type == TokenType.SYMBOL:
                if contents not in self._symbol_table:
                    raise RuntimeError(f'Undefined symbol: {contents}.')
                # Expand the macro / substitute the variable's value.
                symbol_expansion = self._symbol_table[contents].strip()
                # Parse, reverse, and add the expansion to the token list.
                symbol_expansion = Token.parse_expression(symbol_expansion, self.operations)
                symbol_expansion = symbol_expansion[::-1]
                tokens.extend(symbol_expansion)
            elif token_type == TokenType.OPERATOR:
                calculated_value = self._compute(contents)
                if calculated_value is not None:
                    self._stack.append(calculated_value)
            else:
                self._stack.append(contents)

        return self._format_output(self._stack[-1]) if self._stack else ''

    def _compute(self, operation: Operator):
        if len(self._stack) < operation.arity:
            raise TypeError(f'Not enough arguments to compute: {operation.description}.')
        args = self._pop_many(operation.arity)
        return operation.operate(*args)

    @staticmethod
    def _preprocess_comments(expression_string):
        """
        Remove comments from expression_string.
        :return: This returns a new string and does not modify the original.
        """
        return re.sub(r'/\*.*?\*/', '', expression_string, flags=re.DOTALL)

    def _preprocess_macros(self, expression_string):
        """
        Removes all macro declarations expression_string and saves them to the symbol table.
        :param expression_string: 
        :return: 
        """

        def save_match_as_macro_and_remove_from_expression(regex_match):
            groups = regex_match.groups()
            symbol_name, expansion = groups
            self._symbol_table[symbol_name] = expansion
            return ''

        return re.sub(r'#define\s+(\$[a-zA-Z0-9_]+)\s+([^#]+)\s+#save',
                      save_match_as_macro_and_remove_from_expression,
                      expression_string,
                      flags=re.DOTALL)

    def _push(self, *items):
        self._stack.extend(items)

    def _pop_many(self, items: int = 1) -> list:
        """
        Pop `items` number of items off the stack
        :param items:
        :return: The removed items as a list.
        """
        if items == 0:
            return []
        popped_items = self._stack[-1 - items:]  # the last `items` number of items
        self._stack = self._stack[:-items]  # everything but the last `items` number of items.
        return popped_items

    def _include_operation_groups(self, operation_groups):
        for operation_group in operation_groups:
            self.operations.update(operation_group)

    def _format_output(self, stack_item):
        if stack_item in (float('inf'), float('-inf')):
            return str(stack_item)
        format_int = identity
        format_float = identity
        if self._display_mode_number_base == 2:
            format_int = bin
            format_float = float_to_bin
        elif self._display_mode_number_base == 8:
            format_int = oct
            format_float = float_to_oct
        elif self._display_mode_number_base == 10:
            format_int = str
            format_float = str
        elif self._display_mode_number_base == 16:
            format_int = hex
            format_float = float.hex

        data_type = type(stack_item)
        # Truncate '.0' if present.
        stack_item = int(stack_item) if int(stack_item) * 1.0 == stack_item else stack_item
        if data_type == int:
            return format_int(stack_item)
        elif data_type == float:
            return format_float(stack_item)
        else:
            email = 'daniel.schetritt@gmail.com'
            raise TypeError(f'An unexpected value got onto the stack. Please submit a bug report to {email}')

    def _clear_stack(self):
        self._stack = []

    def _clear_symbols(self):
        self._symbol_table = {}

    def _clear_all_memory(self):
        self._clear_stack()
        self._clear_symbols()

    def _depth(self):
        return len(self._stack)

    def _peek(self, n=1):
        return self._stack[-int(n)]

    def _duplicate(self, n=1):
        """
        Duplicates the top n items on the stack, in order
        :param n:
        :return:
        """
        items = self._stack[-1 - n:]
        self._push(*items)

    def _drop(self, n=1):
        self._pop_many(n)

    def _swap(self):
        a, b = self._pop_many(2)
        self._push(b, a)

    def _roll_up(self, n):
        rotations = n % len(self._stack)
        self._stack = self._stack[-rotations:] + self._stack[:-rotations]

    def _roll_down(self, n):
        rotations = n % len(self._stack)
        self._stack = self._stack[rotations:] + self._stack[:rotations]

    def _toggle_display_stack(self):
        self._show_stack = not self._show_stack

    def _get_scripting_operations(self):
        return {
            'Display Mode': {
                'dec': Operator(0, lambda: self.set_display_mode_number_base(10), 'Display decimal values'),
                'bin': Operator(0, lambda: self.set_display_mode_number_base(2), 'Display binary values'),
                'oct': Operator(0, lambda: self.set_display_mode_number_base(8), 'Display octal values'),
                'hex': Operator(0, lambda: self.set_display_mode_number_base(16), 'Display hexadecimal values'),
                'stack': Operator(0, lambda: self._toggle_display_stack, 'Toggle stack display'),
            },
            'Memory Manipulation': {
                'clr': Operator(0, self._clear_stack, 'Clear the stack'),
                'cls': Operator(0, self._clear_symbols, 'Clear all defined symbols'),
                'cla': Operator(0, self._clear_all_memory, 'Clear all defined symbols and the stack'),
                'depth': Operator(0, self._depth, 'Push the current depth of the stack to the stack'),
                'peek': Operator(1, self._peek, 'Duplicate the n-th item from the top of the stack'),
                'dup': Operator(0, self._peek, 'Duplicate the top item from the stack'),
                'dupn': Operator(1, self._duplicate, 'Duplicate the top n items on the stack, in order'),
                'drop': Operator(0, self._drop, 'Drop the top item from the stack'),
                'dropn': Operator(1, self._drop, 'Drop the top n items from the stack'),
                'swap': Operator(0, self._swap, 'Swap the top 2 items on the top of the stack'),
                'roll': Operator(1, self._roll_up, 'Roll the stack upwards by n'),
                'rolld': Operator(1, self._roll_down, 'Roll the stack downwards by n'),
            },
            # Preprocessor commands are defined here only for documentation purposes.
            'Preprocessor': {
                '/* comment */': Operator(0, lambda: None,
                                          "Multiline comment, ignore everything between '/*' and '*/'."),
                '#define $var expr #save': Operator(0, lambda: None, "Define a macro called '$x' to be 'expr', "
                                                                     "e.g. 'define $kb 1024 * save'"),
                'help': Operator(0, lambda: None, 'Print this help text'),
            },

        }
