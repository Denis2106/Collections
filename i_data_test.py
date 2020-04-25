import unittest

from i_data import Data

class TestClassData(unittest.TestCase):
    def test_init(self):
        self.assertEqual(Data()._items, {})
        self.assertEqual(Data({'a':1}).a, 1)
        self.assertEqual(Data(Data({'a':1})).a, 1)

    def test_use(self):
        d = Data()
        d.use('a', 1)
        self.assertEqual(d.defaults['a'], 1)

    def test_clear(self):
        d = Data()
        d.use('a', 1)
        d.a = 2
        d.clear('a')
        self.assertEqual(d.a, 1)

    def test_parse(self):
        d = Data()
        d.use('a', 0.0)
        d.parse('a', '1.0')
        self.assertEqual(d.a, 1.0)
        self.assertEqual(type(d.a), float)

    def test_section(self):
        d = Data()
        d.a = 1
        d.section('b').c = 2
        self.assertEqual(d.section('').a, 1)
        self.assertEqual(d.section('b').c, 2)
        self.assertEqual(len(d.section('b').keys()), 1)

    def test_select(self):
        d = Data()
        d.a = 1
        d.select('b')
        d.a = 2
        self.assertEqual(d.a, 2)
        d.select()
        self.assertEqual(d.a, 1)

    def test_get_caller_module(self):
        d = Data()
        self.assertEqual(d.get_caller_module(), 'i_data_test.py')

    def test_get_caller(self):
        d = Data()
        self.assertEqual(d.get_caller(), 'i_data_test.py.test_get_caller')

    def test_get_prefix(self):
        d = Data()
        self.assertEqual(d.get_prefix(), '')
        d.select('a')
        self.assertEqual(d.get_prefix(), 'a_')

    def test_find_prefix(self):
        print('test_find_prefix not implemented')

    def test_make_key(self):
        d = Data()
        self.assertEqual(d.make_key('a'), 'a')
        d.select('s')
        self.assertEqual(d.make_key('a'), 's_a')

    def test_keys(self):
        d = Data()
        d.a = 1
        d.a_b = 2
        self.assertEqual(len(d.keys()), 2)
        d.select('a')
        res = d.keys()
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], 'b')

    def test_items(self):
        d = Data()
        d.a = 1
        d.a_b = 2
        self.assertEqual(len(d.items()), 2)
        d.select('a')
        res = d.items()
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0][0], 'b')
        self.assertEqual(res[0][1], 2)

    def test_get(self):
        d = Data()
        d.a = 1
        d.b = 2
        d.a_a = 3
        self.assertEqual(d.get('a', 0), 1)
        self.assertEqual(d.get('c', 0), 0)
        d.select('a')
        self.assertEqual(d.get('a', 0), 3)
        self.assertEqual(d.get('b', 0), 0)

    def test_setdefault(self):
        d = Data()
        d.setdefault('a', []).append(1)
        self.assertEqual(d.a[0], 1)

    def test_update(self):
        d = Data()
        d.update({'a':1})
        self.assertEqual(d.a, 1)
        self.assertEqual(d.assigns['a'], '.update')

        d1 = Data()
        d1.b = 1
        d1.use('c', 2)
        d.update(d1)
        self.assertEqual(d.b, 1)
        self.assertEqual(d.c, 2)

    def test_getattr(self):
        d = Data()
        d.a = 1
        d.a_a = 2
        self.assertEqual(d.a, 1)
        d.select('a')
        self.assertEqual(d.a, 2)

    def test_getitem(self):
        d = Data()
        d.a = 1
        d.a_a = 2
        self.assertEqual(d['a'], d.a)
        d.select('a')
        self.assertEqual(d['a'], d.a)

    def test_setattr(self):
        d = Data()
        d.a = 1
        d.select('a')
        d.a = 2
        self.assertEqual(d.a, 2)
        d.select('')
        self.assertEqual(d.a, 1)

    def test_setitem(self):
        d = Data()
        d['a'] = 1
        d.select('a')
        d['a'] = 2
        self.assertEqual(d['a'], 2)
        d.select('')
        self.assertEqual(d['a'], 1)

    def test_delattr(self):
        d = Data()
        d.a = 1
        self.assertEqual(d.get('a',0), 1)
        del d.a
        self.assertEqual(d.get('a',0), 0)

    def test_delitem(self):
        d = Data()
        d['a'] = 1
        self.assertEqual(d.get('a',0), 1)
        del d['a']
        self.assertEqual(d.get('a',0), 0)

    def test_repr(self):
        d = Data()
        d.a = 1
        self.assertEqual(str(d), "[('a', 1)]")

    def test_history(self):
        d = Data()
        d.history['a'] = {}
        d.a = 1
        self.assertEqual(d.history['a'][-1][1], 1)

        d.select('a')
        d.a = 0
        d.history['a_a'] = {}
        d.a = 2
        self.assertEqual(d.history['a_a'][-1][1], 2)



if __name__ == '__main__':
    unittest.main()
