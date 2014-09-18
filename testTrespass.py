
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
        assert match == ((0, 0), None), `match`

    def test2(self):
        match = self.matcher.addChunk('ab')
        assert match == ((0, 0), None), `match`

    def test3(self):
        match = self.matcher.addFinal('hello')
        assert match == ((0, 0), None), `match`

    def test4(self):
        match = self.matcher.addFinal('llo')
        assert match == ((0, 2), 6), `match`

class RE1TestCase(unittest.TestCase):

    def setUp(self):
        pat = Trespass.Pattern()
        pat.addRegExp(r'(ab+)*', 34)
        self.matcher = Trespass.Matcher(pat)

    def test1(self):
        match = self.matcher.addFinal('')
        assert match == ((0, 0), 34), `match`

    def test2(self):
        match = self.matcher.addChunk('ab')
        assert match is None, `match`
        match = self.matcher.addChunk('bbabc')
        assert match == ((0, 6), 34), `match`

    def test3(self):
        match = self.matcher.addFinal('abbbbabab')
        assert match == ((0, 9), 34), `match`

class RE2TestCase(unittest.TestCase):

    def setUp(self):
        pat = Trespass.Pattern()
        #pat.debug = sys.stderr.write
        pat.addRegExp(r'01x?#(ab+)*2', 'red')
        pat.addRegExp(r'1x2*', 'blue')
        self.matcher = Trespass.Matcher(pat)

    def test1(self):
        match = self.matcher.addFinal('')
        assert match is None, `match`

    def test2(self):
        match = self.matcher.addChunk('ddf01a')
        assert match is None, `match`
        match = self.matcher.addChunk('bb2')
        assert match == ((3, 5, 9), 'red'), `match`

    def test3(self):
        match = self.matcher.addFinal('01x2g')
        assert match == ((0, 3, 4), 'red'), `match`

    def test4(self):
        match = self.matcher.addChunk('Hello, World!\n')
        assert match is None, `match`
        match = self.matcher.addChunk('two1x')
        assert match is None, `match`
        match = self.matcher.addChunk('f')
        assert match == ((17, 19), 'blue'), `match`

class RE3TestCase(unittest.TestCase):

    def setUp(self):
        pat = Trespass.Pattern()
        pat.addRegExp(r'hello$', 4)
        self.matcher = Trespass.Matcher(pat)

    def test1(self):
        match = self.matcher.addFinal('')
        assert match is None, `match`

    def test2(self):
        match = self.matcher.addChunk('hello, world')
        assert match is None, `match`
        match = self.matcher.addChunk('hello')
        assert match is None, `match`
        match = self.matcher.addFinal('')
        assert match == ((12, 17), 4), `match`

class RE4TestCase(unittest.TestCase):

    def setUp(self):
        pat = Trespass.Pattern()
        pat.addRegExp(r'^test', 4)
        self.matcher = Trespass.Matcher(pat)

    def test1(self):
        match = self.matcher.addChunk('testing')
        assert match == ((0, 4), 4), `match`

    def test2(self):
        #self.assertRaises(Trespass.NoMatchPossible,
        #            self.matcher.addChunk, 'still testing')
        match = self.matcher.addChunk('still testing')
        assert match is None, `match`

    def test3(self):
        match = self.matcher.addFinal('')
        assert match is None, `match`

class RE5TestCase(unittest.TestCase):

    def setUp(self):
        pat = Trespass.Pattern()
        self.matcher = Trespass.Matcher(pat)

    def test1(self):
        #self.assertRaises(Trespass.NoMatchPossible,
        #            self.matcher.addChunk, 'testing')
        match = self.matcher.addChunk('testing')
        assert match is None, `match`

    def test2(self):
        match = self.matcher.addFinal('')
        assert match is None, `match`

class RE6TestCase(unittest.TestCase):

    def setUp(self):
        pat = Trespass.Pattern()
        pat.debug = sys.stderr.write
        pat.addRegExp(r'^[ \t]*(\#[^\n]*)?\n', 56)
        self.matcher = Trespass.Matcher(pat)

    def test1(self):
        match = self.matcher.addChunk(' \n')
        assert match == ((0, 2), 56), `match`

    def test2(self):
        match = self.matcher.addChunk('\t# comment\n')
        assert match == ((0, 11), 56), `match`

    def test3(self):
        match = self.matcher.addChunk('\n    pass')
        assert match == ((0, 1), 56), `match`

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
        assert match == ((2, 2, 3, 4), 5), `match`

    def test2(self):
        match = self.matcher.addChunk('o, World!')
        assert match == ((6, 6, 7), 5), `match`

    def test3(self):
        match = self.matcher.addFinal('d!')
        assert match == ((2, 2, 2), 6), `match`

class RE8TestCase(unittest.TestCase):

    def setUp(self):
        pat = Trespass.Pattern()
        pat.addRegExp(r'a(bc|d+)f', 5)
        self.matcher = Trespass.Matcher(pat)

    def test1(self):
        match = self.matcher.addChunk('dabcf')
        assert match == ((1,5), 5), `match`

    def test2(self):
        match = self.matcher.addChunk('caddddf')
        assert match == ((1, 7), 5), `match`

    def test3(self):
        match = self.matcher.addFinal('abcdf')
        assert match is None, `match`

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
        assert match == ((0,0), 5), `match`

class RE9BTestCase(unittest.TestCase):

    def setUp(self):
        pat = Trespass.Pattern()
        #pat.debug = sys.stderr.write
        pat.addRegExp(r'(#){4,}', 5)
        self.matcher = Trespass.Matcher(pat)

    def test1(self):
        match = self.matcher.addChunk('dabcf')
        assert match == ((0,0,0,0,0,0), 5), `match`

class RE10TestCase(unittest.TestCase):

    def setUp(self):
        pat = Trespass.Pattern()
        #pat.debug = sys.stderr.write
        pat.addRegExp(r'(^|[^[:alnum:]])#[[:alnum:]]+', 5)
        self.matcher = Trespass.Matcher(pat)

    def test1(self):
        match = self.matcher.addChunk('Hello, World!')
        assert match == ((0,0,5), 5), `match`

    def test2(self):
        match = self.matcher.addChunk('./Hello, World!')
        assert match == ((1,2,7), 5), `match`

    def test3(self):
        match = self.matcher.addChunk('World')
        assert match is None, `match`
        match = self.matcher.addFinal('')
        assert match == ((0,0,5), 5), `match`

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
#        assert match is None, `match`

class RE12TestCase(unittest.TestCase):

    def setUp(self):
        pat = Trespass.Pattern()
        #pat.debug = sys.stderr.write
        pat.addRegExp(r'^([ \t][^\n]*)?\n', 5)
        self.matcher = Trespass.Matcher(pat)

    def test1(self):
        match = self.matcher.addChunk('\thello\n')
        assert match == ((0,7), 5), `match`

    def test2(self):
        match = self.matcher.addChunk('\n\n')
        assert match == ((0,1), 5), `match`

    def test3(self):
        match = self.matcher.addFinal('World\n')
        assert match is None, `match`

class RE13TestCase(unittest.TestCase):

    def setUp(self):
        pat = Trespass.Pattern()
        #pat.debug = sys.stderr.write
        pat.addRegExp(r' +#[^\n]+\n', 5)
        self.matcher = Trespass.Matcher(pat)

    def test1(self):
        match = self.matcher.addChunk('    hello\n')
        assert match == ((0, 4, 10), 5), `match`

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
        assert match == ((0, 3, 4), 5), `match`


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
        assert match == ((0, 4, 4), 5), `match`

class RE16TestCase(unittest.TestCase):

    def setUp(self):
        pat = Trespass.Pattern()
        #pat.debug = sys.stderr.write
        pat.addRegExp('', 7)
        self.matcher = Trespass.Matcher(pat)

    def test1(self):
        match = self.matcher.addChunk('')
        assert match == ((0, 0), 7), `match`

class RE17TestCase(unittest.TestCase):

    def setUp(self):
        pat = Trespass.Pattern()
        #pat.debug = sys.stderr.write
        pat.addRegExp('a+#a+?', 7)
        self.matcher = Trespass.Matcher(pat)

    def test1(self):
        match = self.matcher.addChunk('aaaaaaaaaabb')
        assert match == ((0, 9, 10), 7), `match`

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
        assert match is None, `match`
        match = self.matcher.addFinal('')
        assert match == ((0, 5, 5), 7), `match`

class RE19TestCase(unittest.TestCase):

    def setUp(self):
        pat = Trespass.Pattern()
        #pat.debug = sys.stderr.write
        pat.addRegExp('f*?#f+', 7)
        self.matcher = Trespass.Matcher(pat)
        #self.matcher.debug = sys.stderr.write

    def test1(self):
        match = self.matcher.addFinal('ffff')
        assert match == ((0, 0, 4), 7), `match`

class RE20TestCase(unittest.TestCase):

    def setUp(self):
        pat = Trespass.Pattern()
        pat.debug = sys.stderr.write
        pat.addRegExp('[ab]?[cd[:space:]]', 7)
        self.matcher = Trespass.Matcher(pat)
        #self.matcher.debug = sys.stderr.write

    def test1(self):
        match = self.matcher.addFinal('abcd')
        assert match == ((1, 3), 7), `match`


def suite():
    suite = unittest.makeSuite(RE0TestCase, '')
    return suite

if __name__ == "__main__":
    unittest.main()
