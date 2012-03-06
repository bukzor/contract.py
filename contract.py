import re

class InvalidContract(Exception):
    pass

class FailedContract(Exception):
    pass

def check_value(schema, value, debug=False):
    from collections import deque

    # We'll be using this queue in a leftward manner, ie append and popleft
    q = deque()
    q.append((schema, value))
    # No need to check argument count at the top level, python functions do this.
    check_length = ''
    while q:
        schema, value = q.popleft()
        if debug:
            print 'CHECKING:', schema, value, check_length
        if isinstance(schema, type):
            expected_type = schema
        else:
            expected_type = type(schema)

        if not isinstance(value, expected_type):
            if debug:
                print 'type miss-match\n'
            raise FailedContract('expected a %s, got a %s' % (
                    expected_type.__name__, type(value).__name__)
            )

        if schema is expected_type or schema is None:
            # We just wanted to check types. All done.
            pass
        elif expected_type is tuple:
            if check_length:
                schema_len = len(schema)
                value_len = len(value)
                if schema_len != value_len:
                    raise FailedContract('expected a %s-ple, got a %s-ple' % (
                        schema_len, value_len
                    ))

            # check the contained values too
            #TODO: use izip, for memory efficiency
            for schema, value in zip(schema, value):
                q.append((schema, value))
        elif hasattr(expected_type, '__iter__'):
            # check the contained values too
            if len(schema) != 1:
                raise InvalidContract("Expected just one type to be checked: %r" % schema)

            if hasattr(schema, 'items'):
                schema = schema.items()
                # No need to worry about the "no value.items" case.
                # We've already shown that isinstance(expected_type, value)
                value = value.items()

            s = iter(schema).next()
            for v in value:
                q.append((s, v))
        elif isinstance(schema, contract):
            if schema != value:
                raise FailedContract('expected %s, got %s' % (schema, value))
        else:
            raise ValueError('Unhandled: %r' % ((schema, value),))

        # We do check tuple lengths on all but the top level
        check_length = 'check-length'

class contract(object):
    def __init__(self, input_schema, output_schema, debug=False):
        if not isinstance(input_schema, tuple):
            input_schema = (input_schema,)
        self.__args = (input_schema, output_schema)
        self.debug = debug
        self.func = None

    def __call__(self, *args):
        """This object is often used as a decorator"""
        if self.func is None:
            assert len(args) == 1, \
                    "Doesn't look like a decorator call: %r" % args
            self.func = args[0]
            return self
        else:
            return self.check(self.func, args)

    def check(self, func, args):
        """
        Check that the function (with these args) follows the contract
        This calls the function, and returns the resulting value
        """
        input_schema, output_schema = self.__args
        if self.debug:
            print self.__args

        check_value(input_schema, args, debug=self.debug)
        # check the output..
        output = func(*args)
        check_value(output_schema, output, debug=self.debug)
        # if it got this far, we're good.
        return output
    
    def __eq__(self, other):
        if isinstance(other, contract):
            return self.__args == other.__args
        else:
            return False

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        """It's often useful for repr(x) to give an executable contructor form"""
        (input_schema, output_schema) = self.__args
        if isinstance(input_schema, tuple) and len(input_schema) == 1:
            input_schema = input_schema[0]
        if hasattr(input_schema, '__name__'):
            input_schema = input_schema.__name__
        if hasattr(output_schema, '__name__'):
            output_schema = output_schema.__name__
        return 'contract(%s, %s)' % (input_schema, output_schema)

