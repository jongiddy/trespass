
import sys
import unittest

import Trespass

class RE0TestCase(unittest.TestCase):

    def setUp(self):
        pat = Trespass.Pattern()
        pat.addRegExp(r'', None)
        pat.addRegExp(r'l+', 6)
        self.matcher = Trespass.Matcher(pat)

    def test1(self):
        match = self.matcher.addFinal('')
        assert ((match.start(), match.end()), match.value()) == ((0, 0), None), repr(match)

    def test2(self):
        match = self.matcher.addChunk('ab')
        assert ((match.start(), match.end()), match.value()) == ((0, 0), None), repr(match)

    def test3(self):
        match = self.matcher.addFinal('hello')
        assert ((match.start(), match.end()), match.value()) == ((0, 0), None), repr(match)

    def test4(self):
        match = self.matcher.addFinal('llo')
        assert ((match.start(), match.end()), match.value()) == ((0, 2), 6), repr(match)

class RE1TestCase(unittest.TestCase):

    def setUp(self):
        pat = Trespass.Pattern()
        pat.addRegExp(r'(ab+)*', 34)
        self.matcher = Trespass.Matcher(pat)

    def test1(self):
        match = self.matcher.addFinal('')
        assert ((match.start(), match.end()), match.value()) == ((0, 0), 34), repr(match)

    def test2(self):
        match = self.matcher.addChunk('ab')
        assert match is None, repr(match)
        match = self.matcher.addChunk('bbabc')
        assert ((match.start(), match.end()), match.value()) == ((0, 6), 34), repr(match)

    def test3(self):
        match = self.matcher.addFinal('abbbbabab')
        assert ((match.start(), match.end()), match.value()) == ((0, 9), 34), repr(match)

class RE2TestCase(unittest.TestCase):

    def setUp(self):
        pat = Trespass.Pattern()
        #pat.debug = sys.stderr.write
        pat.addRegExp(r'01x?#(ab+)*2', 'red')
        pat.addRegExp(r'1x2*', 'blue')
        self.matcher = Trespass.Matcher(pat)

    def test1(self):
        match = self.matcher.addFinal('')
        assert match is None, repr(match)

    def test2(self):
        match = self.matcher.addChunk('ddf01a')
        assert match is None, repr(match)
        match = self.matcher.addChunk('bb2')
        assert match.start() == 3
        assert match.end() == 9
        assert match.tags() == (5,)
        assert match.value() == 'red'

    def test3(self):
        match = self.matcher.addFinal('01x2g')
        assert match.start() == 0
        assert match.end() == 4
        assert match.tags() == (3,)
        assert match.value() == 'red'

    def test4(self):
        match = self.matcher.addChunk('Hello, World!\n')
        assert match is None, repr(match)
        match = self.matcher.addChunk('two1x')
        assert match is None, repr(match)
        match = self.matcher.addChunk('f')
        assert ((match.start(), match.end()), match.value()) == ((17, 19), 'blue'), repr(match)

class RE3TestCase(unittest.TestCase):

    def setUp(self):
        pat = Trespass.Pattern()
        pat.addRegExp(r'hello$', 4)
        self.matcher = Trespass.Matcher(pat)

    def test1(self):
        match = self.matcher.addFinal('')
        assert match is None, repr(match)

    def test2(self):
        match = self.matcher.addChunk('hello, world')
        assert match is None, repr(match)
        match = self.matcher.addChunk('hello')
        assert match is None, repr(match)
        match = self.matcher.addFinal('')
        assert match.start() == 12
        assert match.end() == 17
        assert match.tags() == ()
        assert match.value() == 4

class RE4TestCase(unittest.TestCase):

    def setUp(self):
        pat = Trespass.Pattern()
        pat.addRegExp(r'^test', 4)
        self.matcher = Trespass.Matcher(pat)

    def test1(self):
        match = self.matcher.addChunk('testing')
        assert ((match.start(), match.end()), match.value()) == ((0, 4), 4), repr(match)

    def test2(self):
        #self.assertRaises(Trespass.NoMatchPossible,
        #            self.matcher.addChunk, 'still testing')
        match = self.matcher.addChunk('still testing')
        assert match is None, repr(match)

    def test3(self):
        match = self.matcher.addFinal('')
        assert match is None, repr(match)

class RE5TestCase(unittest.TestCase):

    def setUp(self):
        pat = Trespass.Pattern()
        self.matcher = Trespass.Matcher(pat)

    def test1(self):
        #self.assertRaises(Trespass.NoMatchPossible,
        #            self.matcher.addChunk, 'testing')
        match = self.matcher.addChunk('testing')
        assert match is None, repr(match)

    def test2(self):
        match = self.matcher.addFinal('')
        assert match is None, repr(match)

class RE6TestCase(unittest.TestCase):

    def setUp(self):
        pat = Trespass.Pattern()
        pat.debug = sys.stderr.write
        pat.addRegExp(r'^[ \t]*(\#[^\n]*)?\n', 56)
        self.matcher = Trespass.Matcher(pat)

    def test1(self):
        match = self.matcher.addChunk(' \n')
        assert ((match.start(), match.end()), match.value()) == ((0, 2), 56), repr(match)

    def test2(self):
        match = self.matcher.addChunk('\t# comment\n')
        assert ((match.start(), match.end()), match.value()) == ((0, 11), 56), repr(match)

    def test3(self):
        match = self.matcher.addChunk('\n    pass')
        assert ((match.start(), match.end()), match.value()) == ((0, 1), 56), repr(match)

class RE7TestCase(unittest.TestCase):

    def setUp(self):
        pat = Trespass.Pattern()
        #pat.debug = sys.stderr.write
        pat.addRegExp(r'(#l)+', 5)
        pat.addRegExp(r'#$', 6)
        self.matcher = Trespass.Matcher(pat)
        #self.matcher.debug = sys.stderr.write

    def test1(self):
        match = self.matcher.addChunk('Hello, World!')
        assert match.start() == 2
        assert match.end() == 4
        assert match.tags() == (2, 3)
        assert match.value() == 5

    def test2(self):
        match = self.matcher.addChunk('o, World!')
        assert match.start() == 6
        assert match.end() == 7
        assert match.tags() == (6,)
        assert match.value() == 5

    def test3(self):
        match = self.matcher.addFinal('d!')
        assert match.start() == 2
        assert match.end() == 2
        assert match.tags() == (2,)
        assert match.value() == 6

class RE8TestCase(unittest.TestCase):

    def setUp(self):
        pat = Trespass.Pattern()
        pat.addRegExp(r'a(bc|d+)f', 5)
        self.matcher = Trespass.Matcher(pat)

    def test1(self):
        match = self.matcher.addChunk('dabcf')
        assert ((match.start(), match.end()), match.value()) == ((1,5), 5), repr(match)

    def test2(self):
        match = self.matcher.addChunk('caddddf')
        assert ((match.start(), match.end()), match.value()) == ((1, 7), 5), repr(match)

    def test3(self):
        match = self.matcher.addFinal('abcdf')
        assert match is None, repr(match)

class RE9TestCase(unittest.TestCase):

    def setUp(self):
        pat = Trespass.Pattern()
        #pat.debug = sys.stderr.write
        #pat.addRegExp(r'(#)*', 5)
        #pat.addRegExp(r'(sd|)*', 5)
        #pat.addRegExp(r'()*', 5)
        pat.addRegExp(r'(a?)*', 5)
        self.matcher = Trespass.Matcher(pat)

    def test1(self):
        match = self.matcher.addChunk('dabcf')
        assert ((match.start(), match.end()), match.value()) == ((0,0), 5), repr(match)

class RE9BTestCase(unittest.TestCase):

    def setUp(self):
        pat = Trespass.Pattern()
        #pat.debug = sys.stderr.write
        pat.addRegExp(r'(#){4,}', 5)
        self.matcher = Trespass.Matcher(pat)

    def test1(self):
        match = self.matcher.addChunk('dabcf')
        assert match.start() == 0
        assert match.end() == 0
        assert match.tags() == (0,0,0,0)
        assert match.value() == 5

class RE10TestCase(unittest.TestCase):

    def setUp(self):
        pat = Trespass.Pattern()
        #pat.debug = sys.stderr.write
        pat.addRegExp(r'(^|[^[:alnum:]])#[[:alnum:]]+', 5)
        self.matcher = Trespass.Matcher(pat)

    def test1(self):
        match = self.matcher.addChunk('Hello, World!')
        assert match.start() == 0
        assert match.end() == 5
        assert match.tags() == (0,)
        assert match.value() == 5

    def test2(self):
        match = self.matcher.addChunk('./Hello, World!')
        assert match.start() == 1
        assert match.end() == 7
        assert match.tags() == (2,)
        assert match.value() == 5

    def test3(self):
        match = self.matcher.addChunk('World')
        assert match is None, repr(match)
        match = self.matcher.addFinal('')
        assert match.start() == 0
        assert match.end() == 5
        assert match.tags() == (0,)
        assert match.value() == 5

# In PCRE, this is documented as taking exponential time
# It does for us too
#class RE11TestCase(unittest.TestCase):

#    def setUp(self):
#        pat = Trespass.Pattern()
#        #pat.debug = sys.stderr.write
#        pat.addRegExp(r'([^[:digit:]]+|<[[:digit:]]+>)*[!?]', 5)
#        self.matcher = Trespass.Matcher(pat)

#    def test1(self):
#        match = self.matcher.addChunk('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
#        #match = self.matcher.addChunk('aaaaaaaaaaaaa')
#        assert match is None, repr(match)

class RE12TestCase(unittest.TestCase):

    def setUp(self):
        pat = Trespass.Pattern()
        #pat.debug = sys.stderr.write
        pat.addRegExp(r'^([ \t][^\n]*)?\n', 5)
        self.matcher = Trespass.Matcher(pat)

    def test1(self):
        match = self.matcher.addChunk('\thello\n')
        assert ((match.start(), match.end()), match.value()) == ((0,7), 5), repr(match)

    def test2(self):
        match = self.matcher.addChunk('\n\n')
        assert ((match.start(), match.end()), match.value()) == ((0,1), 5), repr(match)

    def test3(self):
        match = self.matcher.addFinal('World\n')
        assert match is None, repr(match)

class RE13TestCase(unittest.TestCase):

    def setUp(self):
        pat = Trespass.Pattern()
        #pat.debug = sys.stderr.write
        pat.addRegExp(r' +#[^\n]+\n', 5)
        self.matcher = Trespass.Matcher(pat)

    def test1(self):
        match = self.matcher.addChunk('    hello\n')
        assert match.start() == 0
        assert match.end() == 10
        assert match.tags() == (4,)
        assert match.value() == 5

class RE14TestCase(unittest.TestCase):

    def setUp(self):
        pat = Trespass.Pattern()
        #pat.debug = sys.stderr.write
        # this pattern succeeds test1
        # pat.addRegExp(r'a+(#b|ab)', 5)
        # this pattern fails test1
        pat.addRegExp(r'a+(#b|ab#)', 5)
        #pat.addRegExp(r'a+(#b+|ab)#b+', 5)
        self.matcher = Trespass.Matcher(pat)

    def test1(self):
        match = self.matcher.addFinal('aaabbb')
        assert match.start() == 0
        assert match.end() == 4
        assert match.tags() == (3,)
        assert match.value() == 5

class RE15TestCase(unittest.TestCase):

    def setUp(self):
        pat = Trespass.Pattern()
        #pat.debug = sys.stderr.write
        # this pattern succeeds test1
        # pat.addRegExp(r'a+(#b|ab)', 5)
        # this pattern fails test1
        pat.addRegExp(r'a+?(#b|ab#)', 5)
        #pat.addRegExp(r'a+(#b+|ab)#b+', 5)
        self.matcher = Trespass.Matcher(pat)

    def test1(self):
        match = self.matcher.addFinal('aaabbb')
        assert match.start() == 0
        assert match.end() == 4
        assert match.tags() == (4,)
        assert match.value() == 5

class RE16TestCase(unittest.TestCase):

    def setUp(self):
        pat = Trespass.Pattern()
        #pat.debug = sys.stderr.write
        pat.addRegExp('', 7)
        self.matcher = Trespass.Matcher(pat)

    def test1(self):
        match = self.matcher.addChunk('')
        assert ((match.start(), match.end()), match.value()) == ((0, 0), 7), repr(match)

class RE17TestCase(unittest.TestCase):

    def setUp(self):
        pat = Trespass.Pattern()
        #pat.debug = sys.stderr.write
        pat.addRegExp('a+#a+?', 7)
        self.matcher = Trespass.Matcher(pat)

    def test1(self):
        match = self.matcher.addChunk('aaaaaaaaaabb')
        assert match.start() == 0
        assert match.end() == 10
        assert match.tags() == (9,)
        assert match.value() == 7

class RE18TestCase(unittest.TestCase):

    def setUp(self):
        pat = Trespass.Pattern()
        #pat.debug = sys.stderr.write
        pat.addRegExp('hello(#$)?', 7)
        self.matcher = Trespass.Matcher(pat)
        #self.matcher.debug = sys.stderr.write

    def test1(self):
        # test that the greediest pattern is found
        match = self.matcher.addChunk('hello')
        assert match is None, repr(match)
        match = self.matcher.addFinal('')
        assert match.start() == 0
        assert match.end() == 5
        assert match.tags() == (5,)
        assert match.value() == 7

class RE19TestCase(unittest.TestCase):

    def setUp(self):
        pat = Trespass.Pattern()
        #pat.debug = sys.stderr.write
        pat.addRegExp('f*?#f+', 7)
        self.matcher = Trespass.Matcher(pat)
        #self.matcher.debug = sys.stderr.write

    def test1(self):
        match = self.matcher.addFinal('ffff')
        assert match.start() == 0
        assert match.end() == 4
        assert match.tags() == (0,)
        assert match.value() == 7

class RE20TestCase(unittest.TestCase):

    def setUp(self):
        pat = Trespass.Pattern()
        pat.debug = sys.stderr.write
        pat.addRegExp('[ab]?[cd[:space:]]', 7)
        self.matcher = Trespass.Matcher(pat)
        #self.matcher.debug = sys.stderr.write

    def test1(self):
        match = self.matcher.addFinal('abcd')
        assert ((match.start(), match.end()), match.value()) == ((1, 3), 7), repr(match)


def suite():
    suite = unittest.makeSuite(RE0TestCase, '')
    return suite

if __name__ == "__main__":
    unittest.main()
