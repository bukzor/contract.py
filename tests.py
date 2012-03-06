from contract import contract, InvalidContract, FailedContract
import unittest

class TestContracts(unittest.TestCase):
    
    def test_str_to_str(self):
        @contract(str, str)
        def exclaim(s):
            return s + '!'
        # this is ok
        self.assertEqual(exclaim('hello'), 'hello!')
        # this is not ok
        self.assertRaisesRegexp(FailedContract, r'^expected a str, got a int$', exclaim, 5)

    def test_str_to_str_to_str(self):
        @contract(str, contract(str, str))
        def prepender(s):
            @contract(str, str)
            def wrapper(s2):
                return s + s2
            return wrapper

        # this is ok
        self.assertEqual(prepender('hello, ')('dave'), 'hello, dave')
        # these are not ok
        self.assertRaisesRegexp(FailedContract, r'^expected a str, got a int$', prepender, 5)
        self.assertRaisesRegexp(FailedContract, r'^expected a str, got a int$', prepender('hello, '), 5)

        @contract(str, contract(str, str))
        def prepender(s):
            def wrapper(s2):
                return s + s2
            return wrapper

        self.assertRaisesRegexp(FailedContract, r'^expected a contract, got a function$', prepender, 'hello, ')

        @contract(str, contract(str, str))
        def prepender(s):
            @contract(str, int)
            def wrapper(s2):
                return ord(s) + ord(s2)
            return wrapper
        self.assertRaisesRegexp(FailedContract, r'^expected contract\(str, str\), got contract\(str, int\)$', prepender, 'hello, ')
        


    def test_argle_bargle(self):
        @contract(contract(str, str), str)
        def i_give_you_happy(f):
            return f('happy')
        @contract(str, str)
        def joy_joy(s):
            return s + ' ' + s + ' joy joy'
        # this is ok
        self.assertEqual(i_give_you_happy(joy_joy), 'happy happy joy joy')
        # these are not ok
        self.assertRaisesRegexp(TypeError, r'^i_give_you_happy\(\) takes exactly 1 argument \(0 given\)$', i_give_you_happy)
        self.assertRaisesRegexp(FailedContract, r'^expected a contract, got a str$', i_give_you_happy, 'joy joy')
        self.assertRaisesRegexp(FailedContract, r'^expected a contract, got a function$', i_give_you_happy, lambda s: s)

    def test_unit(self):
        @contract((), int)
        def f():
            return 42
        # this is ok
        self.assertEqual(f(), 42)
        # these are not ok
        self.assertRaisesRegexp(TypeError, r'^f\(\) takes no arguments \(1 given\)$', f, ())
        self.assertRaisesRegexp(TypeError, r'^f\(\) takes no arguments \(1 given\)$', f, (5,))

    def test_class(self):
        class C(object):
            pass
        @contract(C, int)
        def f(c):
            return 42
        # this is ok
        self.assertEqual(f(C()), 42)
        # these are not ok
        self.assertRaisesRegexp(FailedContract, r'^expected a C, got a type$', f, C)
        self.assertRaisesRegexp(FailedContract, r'^expected a C, got a int$', f, 42)
        self.assertRaisesRegexp(FailedContract, r'^expected a C, got a type$', f, object)
        self.assertRaisesRegexp(FailedContract, r'^expected a C, got a object$', f, object())

    def test_nested_unit(self):
        @contract((((),),), str)
        def f(unit_unit):
            return 'hello'
        # this is ok
        self.assertEqual(f(((),)), 'hello')
        # these are not ok
        self.assertRaisesRegexp(FailedContract, r'^expected a 1-ple, got a 0-ple$', f, ())
        self.assertRaisesRegexp(FailedContract, r'^expected a tuple, got a str$', f, ('hi'))

    def test_list_of_int(self):
        @contract([int], str)
        def f(l):
            return ','.join([str(i) for i in l])
        # this is ok
        self.assertEqual(f([1, 2, 3]), '1,2,3')
        self.assertEqual(f([]), '')
        # these are not ok
        self.assertRaisesRegexp(FailedContract, r'^expected a list, got a NoneType$', f, None)
        self.assertRaisesRegexp(FailedContract, r'^expected a int, got a str$', f, ['hi'])
        self.assertRaisesRegexp(FailedContract, r'^expected a int, got a str$', f, [42, 'hi'])

    def test_list_of_list_of_int(self):
        @contract([[int]], str)
        def f(l_o_l):
            return ';'.join([','.join([str(i) for i in l]) for l in l_o_l])
        # this is ok
        self.assertEqual(f([[1, 2, 3], [4, 5, 6]]), '1,2,3;4,5,6')
        self.assertEqual(f([[1, 2, 3]]), '1,2,3')
        self.assertEqual(f([[]]), '')
        self.assertEqual(f([]), '')
        # these are not ok
        self.assertRaisesRegexp(FailedContract, r'^expected a list, got a int$', f, [1, 2, 3])
        self.assertRaisesRegexp(FailedContract, r'^expected a int, got a str$', f, [[], ['hi']])

    def test_set_of_int(self):
        @contract(set([int]), int)
        def f(s):
            return len(s)
        # this is ok
        self.assertEqual(f(set([1, 2, 3])), 3)
        self.assertEqual(f(set()), 0)
        # these are not ok
        self.assertRaisesRegexp(FailedContract, r'^expected a set, got a list$', f, [1, 2, 3])
        self.assertRaisesRegexp(FailedContract, r'^expected a int, got a str$', f, set([1, 2, 'hi']))

    def test_list_of_set_of_int(self):
        @contract([set([int])], [int])
        def f(l_o_s):
            return [len(s) for s in l_o_s]
        # this is ok
        self.assertEqual(f([set([1, 2, 3]), set([4, 5]), set([1])]), [3, 2, 1])
        self.assertEqual(f([]), [])
        self.assertEqual(f([set()]), [0])
        # these are not ok
        self.assertRaisesRegexp(FailedContract, r'^expected a set, got a int$', f, [1, 2, 3])
        self.assertRaisesRegexp(FailedContract, r'^expected a int, got a str$', f, [set(), set(['hi'])])

    def test_dict(self):
        @contract({int:str}, None)
        def f(m): pass
            
        # this is ok
        self.assertEqual(f({5: 'hi'}), None)
        # this is not ok
        self.assertRaisesRegexp(FailedContract, r'^expected a str, got a int$', f, {5: 10})
        self.assertRaisesRegexp(FailedContract, r'^expected a int, got a str$', f, {'hello': 'hi'})

    def test_invalid_contracts(self):
        # that's just not a valid type.
        with self.assertRaises(TypeError):
            @contract({})
            def f():
                pass
        # this isn't a function type.
        with self.assertRaises(TypeError):
            @contract(str)
            def f():
                pass

if __name__ == '__main__':
    unittest.main()
