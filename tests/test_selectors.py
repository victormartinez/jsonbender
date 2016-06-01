import unittest

from jsonbender.selectors import F, ProtectedF, K, S, OptionalS


class TestK(unittest.TestCase):
    selector_cls = K

    def test_k(self):
        self.assertEqual(K(1)({}), 1)
        self.assertEqual(K('string')({}), 'string')


class STestsMixin(object):
    def test_no_selector_raises_value_error(self):
        self.assertRaises(ValueError, self.selector_cls)

    def test_single_existing_field(self):
        source = {'a': 'val'}
        self.assertEqual(self.selector_cls('a')(source), 'val')

    def test_deep_existing_path(self):
        source = {'a': [{}, {'b': 'ok!'}]}
        self.assertEqual(self.selector_cls('a', 1, 'b')(source), 'ok!')


class TestS(unittest.TestCase, STestsMixin):
    selector_cls = S

    def test_missing_field(self):
        self.assertRaises(KeyError, self.selector_cls('k'), {})


class TestOptionalS(unittest.TestCase, STestsMixin):
    selector_cls = OptionalS

    def test_opts(self):
        opts = OptionalS('key', 'missing')
        self.assertEqual(opts({'key': {'missing': 23}}), 23)
        self.assertEqual(opts({'key': {}}), None)
        self.assertEqual(opts({}), None)

    def test_opts_with_default_value(self):
        default = 27
        opts = OptionalS('key', 'missing', default=default)
        self.assertEqual(opts({'key': {'missing': 23}}), 23)
        self.assertEqual(opts({'key': {}}), default)
        self.assertEqual(opts({}), default)


class FTestsMixin(object):
    def test_f(self):
        self.assertEqual(self.selector_cls(len)(range(5)), 5)

    def test_curry_kwargs(self):
        f = self.selector_cls(sorted, key=lambda d: d['v'])
        source = [{'v': 2}, {'v': 3}, {'v': 1}]
        self.assertEqual(f(source), [{'v': 1}, {'v': 2}, {'v': 3}])

    def test_protect(self):
        protected = self.selector_cls(int).protect(protect_against='bad')
        self.assertIsInstance(protected, ProtectedF)
        self.assertEqual(protected('123'), 123)
        self.assertEqual(protected('bad'), 'bad')

    # TODO: move this to a more general Bender test
    def test_composition(self):
        s = S('val')
        f = self.selector_cls(len)
        source = {'val': 'hello'}
        self.assertEqual((f << s)(source), 5)
        self.assertEqual((s >> f)(source), 5)


class TestF(unittest.TestCase, FTestsMixin):
    selector_cls = F


class TestProtectedF(unittest.TestCase, FTestsMixin):
    selector_cls = ProtectedF

    def test_protectedf(self):
        protected = ProtectedF(int)
        self.assertEqual(protected('123'), 123)
        self.assertEqual(protected(None), None)


if __name__ == '__main__':
    unittest.main()

