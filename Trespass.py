#
# Trespass - regular expression engine
#
# Copyright (c) 2005 Jonathan Patrick Giddy
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

# Email jongiddy@gmail.com
# See the end of this file for examples of use

# Version 1.0.0
# Date 21 January 2005
#
# Version 1.1.0
# Date 24 January 2005
# - test for incomplete hex characters
# - handle {0,0} correctly
# - test for empty bracket ranges
# - make start and stop anchors repeatable
# - give a useful error for ?*+{} at start of sequence
# - add \e for escape character
# - remove extra branch for some zero-length repetitions
#
# Version 1.2.0
# Date 31 January 2005
# - fixes to ensure all repeated matches are greedy - we ensure
# the greediest repeats are earlier in the nodes list, so for
# any particular length, they get to call addMatch() first.
# - as a bonus, added reluctant matching for ?,*,+ and {}
# - in Matcher prevch was never set to anything other than its
# initial value - this means (^|a)b would have succeeded for 'xb'.
# - addChunk('') at position 0 now returns any matches rather than
# waiting for at least one character - this also required changing
# StartAnchor from a transition to a control - however,a match
# may not occur immediately if a transition may be hiding a higher
# priority match
#
# Version 2.0.0
# Date 4 March 2005
# - replace return value of addChunk/Final with a match object
# so we can make further changes without breaking compatibility,
# particularly re module compatibility
# - discovered existence of sre.Scanner, which supports simultaneous
# regexp matching
#
# Version 2.1.0
# Date 15 October 2014
# - update to support Python 3. Tests run OK in Python 2.7 and 3.4
# - not tested in earlier versions, but definitely won't work for
# Python earlier than 2.3

__version__ = '2.1'

TYPE_MATCH = 0
TYPE_CONTROL = 1
TYPE_TRANSITION = 2
TYPE_CHARACTER = 3

class MatchObject:

    def __init__(self, start, end, tags, value):
        self._start = start
        self._end = end
        self._tags = tags
        self._value = value

    def start(self):
        return self._start

    def end(self):
        return self._end

    def tags(self):
        return self._tags

    def value(self):
        return self._value

class Matcher:

    def __init__(self, pattern):
        self.debug = None

        self.prevch = ''

        self.start = pattern.start
        self.currpos = 0
        start0 = pattern.start0
        assert start0.type is TYPE_CONTROL, start0.type
        namespace = {'tags': ()}
        self.partials = [(0, [(start0, namespace)])]

        self.match = None

    def addMatch(self, startpos, endpos, match, tags):
        index = match.index()
        if self.debug:
            self.debug(' addMatch(%d, %d, %r, %d)' % (startpos, endpos,
                                                            tags, index))
        if (
            self.match is None or
            startpos < self.matchleft or (
                startpos == self.matchleft and (
                    endpos > self.matchright or (
                        endpos == self.matchright and
                        index < self.matchindex
                    )
                )
            )
        ):
            self.matchleft = startpos
            self.matchright = endpos
            self.matchindex = index
            self.match = match
            self.matchtags = tags

    def getMatch(self):
        tags = self.matchtags + (self.matchright,)
        return MatchObject(self.matchleft, self.matchright,
                    self.matchtags, self.match.value())

    def addChar(self, ch):
        if self.debug:
            self.debug('addChar(%s)\n' % repr(ch))
        partials = []
        for startpos, nodes in self.partials:
            if self.match is not None and startpos > self.matchleft:
                if self.debug:
                    self.debug('- remaining nodes pruned\n')
                break
            if self.debug:
                self.debug('- startpos = %d' % startpos)
            i = 0
            while i < len(nodes):
                node, namespace = nodes[i]
                if node.type is TYPE_MATCH:
                    self.addMatch(startpos, self.currpos, node,
                                                    namespace['tags'])
                    del nodes[i]
                elif node.type is TYPE_CHARACTER:
                    links = node.getMatchedLinks(ch)
                    nodes[i:i+1] = [(x, namespace.copy())
                                                        for x in links]
                    i += len(links)
                else:
                    if node.type is TYPE_CONTROL:
                        links = node.getMatchedLinks(namespace,
                                                        self.currpos)
                    else:
                        assert node.type is TYPE_TRANSITION
                        links = node.getMatchedLinks(self.prevch, ch)
                    nodes[i:i+1] = [(x, namespace.copy())
                                                        for x in links]
            if nodes:
                if self.debug:
                    self.debug(' not exhausted\n')
                partials.append((startpos, nodes))
            else:
                if self.debug:
                    self.debug(' exhausted\n')
        self.prevch = ch
        self.currpos += 1
        self.partials = partials

    def addText(self, text):
        for ch in text:
            self.addChar(ch)
            if not self.partials:
                if self.match is not None:
                    return self.getMatch()
            else:
                # self.partials must be less than or equal to any match,
                # since later partials are deleted
                assert self.match is None or \
                            self.partials[0][0] <= self.matchleft, \
                            repr((self.partials, self.matchleft))
            if self.match is None:
                namespace = {'tags': ()}
                self.partials.append(
                            (self.currpos, [(self.start, namespace)]))
            else:
                # no point adding another branch as we already know
                # the match will start left of the current position
                assert self.currpos > self.matchleft
        return None

    def addChunk(self, text):
        match = self.addText(text)
        if match is None:
            if self.debug:
                self.debug('zero-length match at end of text\n')
            partials = []
            for startpos, nodes in self.partials:
                if self.match is not None and startpos > self.matchleft:
                    if self.debug:
                        self.debug('- remaining nodes pruned\n')
                    break
                if self.debug:
                    self.debug('- startpos = %d' % startpos)
                i = 0
                tseen = 0
                while i < len(nodes):
                    node, namespace = nodes[i]
                    if node.type is TYPE_MATCH:
                        if tseen:
                            # if we've seen a transition node then
                            # we ignore the match for now, since an
                            # earlier transition is another
                            # zero-length node which may hide a
                            # higher priority match
                            i += 1
                        else:
                            self.addMatch(startpos, self.currpos, node,
                                                    namespace['tags'])
                            del nodes[i]
                    elif node.type is TYPE_CONTROL:
                        links = node.getMatchedLinks(namespace,
                                                            self.currpos)
                        nodes[i:i+1] = [(x, namespace.copy())
                                                        for x in links]
                    else:
                        assert node.type in (TYPE_CHARACTER,
                                                    TYPE_TRANSITION)
                        if node.type is TYPE_TRANSITION:
                            tseen = 1
                        i += 1
                if nodes:
                    if self.debug:
                        self.debug(' not exhausted\n')
                    partials.append((startpos, nodes))
                else:
                    if self.debug:
                        self.debug(' exhausted\n')
            self.partials = partials
            if not partials and self.match is not None:
                match = self.getMatch()
        return match

    def addFinal(self, text):
        match = self.addText(text)
        if match is None:
            if self.debug:
                self.debug('add $ metacharacter\n')
            for startpos, nodes in self.partials:
                if self.match is not None and \
                            startpos > self.matchleft:
                    if self.debug:
                        self.debug('- remaining nodes pruned\n')
                    break
                if self.debug:
                    self.debug('- startpos = %d' % startpos)
                i = 0
                while i < len(nodes):
                    node, namespace = nodes[i]
                    if node.type is TYPE_MATCH:
                        self.addMatch(startpos, self.currpos, node,
                                                    namespace['tags'])
                        del nodes[i]
                    elif node.type is TYPE_CHARACTER:
                        i += 1
                    else:
                        if node.type is TYPE_CONTROL:
                            links = node.getMatchedLinks(namespace,
                                                            self.currpos)
                        else:
                            assert node.type is TYPE_TRANSITION
                            links = node.getMatchedLinks(self.prevch, '')
                        nodes[i:i+1] = [(x, namespace.copy())
                                                        for x in links]
                if self.debug:
                    self.debug('\n')
            self.partials = None
            if self.match is not None:
                match = self.getMatch()
        return match

class Match:

    type = TYPE_MATCH

    def __init__(self, index, value):
        self._index = index
        self._value = value

    def index(self):
        return self._index

    def value(self):
        return self._value

def addLink(links, node):
    if not links:
        # optimisations below are based on merging nodes,
        # so we short-circuit the test here in the case
        # where there are no nodes to merge, which lets
        # us assume below that links[0] exists
        links.append(node)
    elif isinstance(node, CharacterMapNode):
        # merge together character maps
        # We don't replace the character map with
        # a mutable one immediately, since the immutable
        # ones may be shared between links, creating less
        # nodes overall.
        link = links[0]
        if isinstance(link, CharacterMapNode):
            if isinstance(link, MutableCharacterMap):
                map = link
            else:
                # replace immutable map with mutable map
                map = MutableCharacterMap()
                links[0] = map
                map.addMap(link)
            map.addMap(node)
        else:
            # there is only one character map per links list
            # and it goes in the first element
            links.insert(0, node)
    else:
        links.append(node)

# Uncomment to remove optimisations
#def addLink(links, node):
#    links.append(node)

def addLinks(links, nodes):
    for node in nodes:
        addLink(links, node)

class LinkedNode:

    def __init__(self, links=None):
        self.links = []
        if links:
            self.addLinks(links)

    def addLinks(self, links):
        for link in links:
            self.addLink(link)

    def addLink(self, link):
        addLink(self.links, link)

    def getAllLinks(self):
        return self.links

class FunctionNode(LinkedNode):

    def __init__(self, func, links=None):
        self.func = func
        LinkedNode.__init__(self, links)

    def getMatchedLinks(self, *args):
        if self.func(*args):
            return self.getAllLinks()
        else:
            return ()

class ControlNode(FunctionNode):

    type = TYPE_CONTROL

class TagControlNode(LinkedNode):

    type = TYPE_CONTROL

    def getMatchedLinks(self, namespace, currpos):
        namespace['tags'] += (currpos,)
        return self.getAllLinks()

class OptionalNode:

    type = TYPE_CONTROL

    def __init__(self, isgreedy):
        self.isgreedy = isgreedy
        self.opts = []
        self.links = []
        self.both = None

    def addLinks(self, links):
        for link in links:
            self.addLink(link)

    def addLink(self, link):
        addLink(self.links, link)
        self.both = None

    def addOptionalLinks(self, links):
        for link in links:
            self.addOptionalLink(link)

    def addOptionalLink(self, link):
        addLink(self.opts, link)
        self.both = None

    def getAllLinks(self):
        both = self.both
        if both is None:
            if self.isgreedy:
                both = self.opts + self.links
            else:
                both = self.links + self.opts
            self.both = both
        return both

    def getMatchedLinks(self, namespace, currpos):
        return self.getAllLinks()

class IterationExitNode(LinkedNode):

    type = TYPE_CONTROL

    def __init__(self, name, links=None):
        self.name = name
        LinkedNode.__init__(self, links)

    def getMatchedLinks(self, namespace, currpos):
        del namespace[self.name]
        return self.getAllLinks()

class IterationLoopNode:

    type = TYPE_CONTROL

    def __init__(self, name, lower, upper, exit, isgreedy=1):
        self.name = name
        self.lower = lower
        self.upper = upper
        self.exit = exit
        self.links = []
        self.both = None
        self.isgreedy = isgreedy

    def addLinks(self, links):
        for link in links:
            self.addLink(link)

    def addLink(self, link):
        addLink(self.links, link)
        self.both = None

    def getAllLinks(self):
        both = self.both
        if both is None:
            if self.isgreedy:
                both = self.links + [self.exit]
            else:
                both = [self.exit] + self.links
            self.both = both
        return both

    def getMatchedLinks(self, namespace, currpos):
        try:
            count, lastpos = namespace[self.name]
        except KeyError:
            count = 0
            lastpos = -1
        else:
            count += 1
        namespace[self.name] = (count, currpos)
        if self.upper is None or count < self.upper:
            if count >= self.lower:
                if currpos == lastpos:
                    # not advancing -> infinite loop ->
                    # once lower bound is met, do not repeat
                    if count == self.lower:
                        # needed this iteration to get minimum bound
                        links = (self.exit,)
                    else:
                        # this iteration was unnecessary, kill this
                        # branch
                        assert count > self.lower
                        links = ()
                else:
                    links = self.getAllLinks()
            else:
                links = self.links
        else:
            assert count == self.upper, (count, self.upper)
            links = (self.exit,)
        return links

class TransitionNode(FunctionNode):

    type = TYPE_TRANSITION

def StartAnchor(namespace, currpos):
    return currpos == 0

class StartAnchorNode(ControlNode):

    def __init__(self, links=None):
        ControlNode.__init__(self, StartAnchor, links)

def EndAnchor(prevch, ch):
    return ch == ''

class EndAnchorNode(TransitionNode):

    def __init__(self, links=None):
        TransitionNode.__init__(self, EndAnchor, links)

class CharacterNode(FunctionNode):

    type = TYPE_CHARACTER

def Always(*args):
    return 1

def IsAlnum(ch):
    return ch.isalnum()

def IsAlpha(ch):
    return ch.isalpha()

def IsCntrl(ch):
    code = ord(ch)
    return code < 32 or code == 127

def IsDigit(ch):
    return ch.isdigit()

def IsGraph(ch):
    return IsPrint(ch) and not IsSpace(ch)

def IsLower(ch):
    return ch.islower()

def IsPrint(ch):
    return not IsCntrl(ch)

def IsPunct(ch):
    return IsPrint(ch) and not IsAlnum(ch) and ch != ' '

def IsSpace(ch):
    return ch.isspace()

def IsUpper(ch):
    return ch.isupper()

def IsXDigit(ch):
    return ch in '0123456789abcdefABCDEF'

_class_functions = {
    'alnum': IsAlnum,
    'alpha': IsAlpha,
    'cntrl': IsCntrl,
    'digit': IsDigit,
    'graph': IsGraph, # all printable characters except space
    'lower': IsLower,
    'print': IsPrint, # all printable characters
    'punct': IsPunct,
    'space': IsSpace,
    'upper': IsUpper,
    'xdigit': IsXDigit
}

class ComplexCharacterComplement(LinkedNode):

    type = TYPE_CHARACTER

    def __init__(self, characters, classes, links=None):
        LinkedNode.__init__(self, links)
        self.dict = {}
        for ch in characters:
            self.dict[ch] = ch
        self.funcs = []
        for c in classes:
            self.funcs.append(_class_functions[c])

    def getMatchedLinks(self, ch):
        if ch in self.dict:
            return ()
        for func in self.funcs:
            if func(ch):
                return ()
        return self.getAllLinks()

class CharacterMapNode:

    type = TYPE_CHARACTER

    def __init__(self):
        self.dict = {}
        self.default = []

    def getAllLinks(self):
        linkmap = {}
        for link in self.default:
            linkmap[id(link)] = link
        for links in self.dict.values():
            for link in links:
                linkmap[id(link)] = link
        return linkmap.values()

    def getMatchedLinks(self, ch):
        links = self.dict.get(ch)
        if links is None:
            links = self.default
        return links

class MutableCharacterMap(CharacterMapNode):

    def addMap(self, map):
        for ch in self.dict.keys():
            if ch in map.dict:
                addLinks(self.dict[ch], map.dict[ch])
            else:
                addLinks(self.dict[ch], map.default)
        for ch in map.dict.keys():
            if ch not in self.dict:
                self.dict[ch] = self.default[:]
                addLinks(self.dict[ch], map.dict[ch])
        addLinks(self.default, map.default)

class CharacterMatchNode(CharacterMapNode):

    def __init__(self, chars, links):
        self.dict = {}
        links = tuple(links)
        for ch in chars:
            self.dict[ch] = links
        self.default = ()

class CharacterMatchNotNode(CharacterMapNode):

    def __init__(self, chars, links):
        self.dict = {}
        for ch in chars:
            self.dict[ch] = ()
        self.default = tuple(links)

def print_graph(write, links):
    cnt = 0
    map = {}
    links = links[:]
    for link in links:
        map[id(link)] = cnt
        cnt += 1
    cnt = 0
    prefix = '> '
    write('> %d\n' % len(links))
    while cnt < len(links):
        link = links[cnt]
        write('%s' % cnt)
        if link.type is TYPE_MATCH:
            write(' Match(%r)\n' % link.value())
        else:
            if link.type is TYPE_TRANSITION:
                write(' Transition')
            elif link.type is TYPE_CONTROL:
                if isinstance(link, TagControlNode):
                    write(' Tag')
                else:
                    write(' Control')
            else:
                assert link.type is TYPE_CHARACTER
                if isinstance(link, CharacterMatchNotNode):
                    write(' CharacterNot(%r)' % link.dict.keys())
                elif isinstance(link, CharacterMapNode):
                    write(' Character(%r)' % link.dict.keys())
                else:
                    write(' Character')
            for next in link.getAllLinks():
                nextid = id(next)
                if nextid in map:
                    idx = map[nextid]
                else:
                    idx = len(links)
                    links.append(next)
                    map[nextid] = idx
                write(' %d' % idx)
            write('\n')
        cnt += 1

class ParseError(Exception):
    pass

CHAR = 'CHAR'
BRACKET = '['
PAREN = '('
COMPLEMENT = '[^'
STAR = '*'
PLUS = '+'
QMARK = '?'
DOT = '.'
STARTANCHOR = '^'
ENDANCHOR = '$'
HASH = '#'
CLASS = '[:'
DASH = '-'
CHOICE = '|'
BRACE = '{}'
RELUCTANT = '{}?'

_OCT_MAP = {'0': 0, '1': 1, '2': 2, '3': 3,
            '4': 4, '5': 5, '6': 6, '7': 7}

_HEX_MAP = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4,
            '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
            'a': 10, 'b': 11, 'c': 12, 'd': 13, 'e': 14, 'f': 15,
            'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14, 'F': 15}

_TOKEN_ESCAPED = {
    'a': '\a',      # alert
    'b': '\b',      # backspace
    'e': '\x1b',    # escape
    'f': '\f',      # formfeed
    'n': '\n',      # newline
    'r': '\r',      # carriage return
    't': '\t',      # tab
    'v': '\v',      # vertical tab
}

_NORMAL_TOKEN = {
    '*': STAR,
    '+': PLUS,
    '?': QMARK,
    '.': DOT,
    '^': STARTANCHOR,
    '$': ENDANCHOR,
    '#': HASH
}

def escape(s):
    for ch in ('\\', '*', '+', '?', '.', '^', '$', '#',
                '(', ')', '[', '{'):
        s = s.replace(ch, '\\' + ch)
    return s

def scan(pattern):
    tree = None
    stack = []
    bracket = 0
    brace = 0
    escape = 0
    octal = 0
    hex = 0
    for ch in pattern:
        if octal and ch not in _OCT_MAP:
            octal = 0
            tree = (CHAR, chr(value), tree)
        if octal:
            value = 8 * value + _OCT_MAP[ch]
            if octal == 3:
                if value > 0o377:
                    raise ParseError('octal value greater than 377')
                tree = (CHAR, chr(value), tree)
                octal = 0
            else:
                octal += 1

        elif hex:
            if ch not in _HEX_MAP:
                raise ParseError('expected hexadecimal digit')
            value = 16 * value + _HEX_MAP[ch]
            if hex == 2:
                tree = (CHAR, chr(value), tree)
                hex = 0
            else:
                hex += 1
        elif escape:
            escape = 0
            if ch in _OCT_MAP:
                octal = 1
                value = _OCT_MAP[ch]
            elif ch == 'x':
                hex = 1
                value = 0
            else:
                token = _TOKEN_ESCAPED.get(ch)
                if token is None:
                    tree = (CHAR, ch, tree)
                elif isinstance(token, str):
                    tree = (CHAR, token, tree)
                else:
                    tree = (token, None, tree)
        elif bracket:
            if bracket == 1:
                # not read a character yet (apart from possibly ^)
                if tree is None and ch == '^':
                    tree = (COMPLEMENT, None, tree)
                else:
                    if ch == '\\':
                        escape = 1
                    else:
                        tree = (CHAR, ch, tree)
                    bracket = 2
            elif bracket == 2:
                if ch == ']':
                    if inclass and inclass is not tree and \
                            tree[0] is CHAR and tree[1] == ':':
                        chars = []
                        tree = tree[2]
                        token, ch, tree = tree
                        while ch != ':':
                            assert token in (CHAR, DASH)
                            chars.append(ch)
                            token, ch, tree = tree
                        token, ch, tree = tree
                        assert token is CHAR and ch == '[', (token, ch)
                        chars.reverse()
                        name = ''.join(chars)
                        tree = (CLASS, name, tree)
                    else:
                        assert stack
                        tree = (BRACKET, tree, stack.pop())
                        bracket = 0
                else:
                    if ch == '\\':
                        escape = 1
                    elif ch == ':' and not inclass and \
                                tree[0] is CHAR and tree[1] == '[':
                        tree = (CHAR, ch, tree)
                        # set inclass to true value - we set it to the
                        # tree pointing to the first colon so we can
                        # detect [[:] correctly as not a class
                        inclass = tree
                    elif ch == '-' and tree[0] is CHAR:
                        tree = (DASH, ch, tree)
                    else:
                        tree = (CHAR, ch, tree)
        elif brace:
            if brace == 1:
                if ch == ',':
                    if not brstart:
                        raise ParseError('missing value: '
                                    'expected integer between { and ,'
                                    % ch)
                    brace = 2
                    brend = ''
                elif ch == '}':
                    if not brstart:
                        raise ParseError('missing value: '
                                    'expected integer between { and }'
                                    %ch)
                    brace = 0
                    tree = (BRACE, (brstart, brend), tree)
                elif ch.isdigit():
                    brstart = brstart + ch
                else:
                    raise ParseError('invalid character %r: '
                                'expected integer after {'
                                % ch)
            else:
                assert brace == 2, repr(brace)
                if ch == '}':
                    brace = 0
                    tree = (BRACE, (brstart, brend), tree)
                elif ch.isdigit():
                    brend = brend + ch
                else:
                    raise ParseError('invalid character %r: expected '
                                'integer or nothing between , and }'
                                % ch)
        else:
            if ch == '\\':
                escape = 1
            elif ch == '[':
                bracket = 1
                inclass = 0
                stack.append(tree)
                tree = None
            elif ch == '{':
                brace = 1
                brstart = ''
                brend = None
            elif ch == '(':
                stack.append(tree)
                tree = None
            elif ch == ')':
                if stack and stack[-1] and stack[-1][0] is CHOICE:
                    stack[-1][1].append(tree)
                    tree = stack.pop()
                if stack:
                    tree = (PAREN, tree, stack.pop())
                else:
                    raise ParseError('too many close parentheses ")"')
            elif ch == '|':
                if stack and stack[-1] and stack[-1][0] is CHOICE:
                    stack[-1][1].append(tree)
                else:
                    stack.append((CHOICE, [tree], None))
                tree = None
            else:
                token = _NORMAL_TOKEN.get(ch)
                if token is None:
                    tree = (CHAR, ch, tree)
                else:
                    tree = (token, None, tree)
    if octal:
        tree = (CHAR, chr(value), tree)
    elif hex:
        raise ParseError('expected two hexadecimal digits after \\x')
    elif escape:
        raise ParseError('expression ends with escape character')
    if bracket:
        raise ParseError('missing close bracket "]"')
    if stack:
        if stack[-1] and stack[-1][0] is CHOICE:
            stack[-1][1].append(tree)
            tree = stack.pop()
        if stack:
            raise ParseError('missing close parentheses ")"')
    return tree

class Pattern:

    def __init__(self, pattern=None, match=None):
        self.debug = None
        self.seqno = 0
        self.start0 = ControlNode(Always)
        self.start = ControlNode(Always)
        if pattern:
            self.addRegExp(pattern, match)

    def clone(self):
        pat = Pattern()
        pat.debug = self.debug
        pat.seqno = self.seqno
        pat.start0.addLinks(self.start0.getAllLinks())
        pat.start.addLinks(self.start.getAllLinks())
        return pat

    def addRegExp(self, pattern, match=None):
        stack = scan(pattern)
        if self.debug:
            self.debug('%s\n' % (stack,))
        links = self._compile(stack, match)
        for link in links:
            if isinstance(link, StartAnchorNode):
                self.start0.addLinks(link.getAllLinks())
            else:
                self.start.addLink(link)
                self.start0.addLink(link)
        if self.debug:
            print_graph(self.debug, [self.start0])

    def match(self, text):
        matcher = Matcher(self)
        matcher.debug = self.debug
        return matcher.addFinal(text)

    def _compile(self, tree, match):
        seqno = self.seqno
        links = [Match(seqno, match)]
        self.seqno = seqno + 1
        links = self._comp(tree, links)
        return links

    def _comp(self, tree, links):
        while tree:
            token, data, tree = tree
            if token is BRACE or token is RELUCTANT:
                brstart, brend = data
                lower = int(brstart)
                if brend is None:
                    # {3}
                    upper = lower
                elif not brend:
                    # {3,}
                    upper = None
                else:
                    # {3,5}
                    upper = int(brend)
                    if upper < lower:
                        raise ParseError('brace upper limit greater '
                                                    'than lower limit')
                if tree is None:
                    raise ParseError('{ cannot appear at start'
                                                    ' of expression')
                if token is BRACE:
                    isgreedy = 1
                else:
                    assert token is RELUCTANT
                    isgreedy = 0
                token, data, tree = tree
                if upper == 0:
                    # {0} or {0,0} skip this node
                    pass
                elif upper == 1:
                    if lower == 0:
                        # ? or {0,1}
                        node = OptionalNode(isgreedy)
                        node.addLinks(links)
                        links = self._getatom(token, data, links)
                        node.addOptionalLinks(links)
                        links = [node]
                    else:
                        assert lower == 1
                        # {1} or {1,1}
                        links = self._getatom(token, data, links)
                else:
                    assert upper is None or upper > 1
                    seqno = self.seqno
                    self.seqno = seqno + 1
                    name = 'count%d' % seqno
                    exit = IterationExitNode(name, links)
                    loop = IterationLoopNode(name, lower, upper,
                                                        exit, isgreedy)
                    links = self._getatom(token, data, [loop])
                    loop.addLinks(links)
                    links = [loop]
            elif token is STAR:
                if tree is None:
                    raise ParseError('* cannot appear at start of '
                                                        'expression')
                tree = BRACE, (0, ''), tree
            elif token is PLUS:
                if tree is None:
                    raise ParseError('+ cannot appear at start of '
                                                        'expression')
                tree = BRACE, (1, ''), tree
            elif token is QMARK:
                if tree is None:
                    raise ParseError('? cannot appear at start of '
                                                        'expression')
                token, data, tree = tree
                if token is BRACE:
                    tree = RELUCTANT, data, tree
                elif token is STAR:
                    tree = RELUCTANT, (0, ''), tree
                elif token is PLUS:
                    tree = RELUCTANT, (1, ''), tree
                elif token is QMARK:
                    tree = RELUCTANT, (0, 1), tree
                else:
                    tree = token, data, tree
                    tree = BRACE, (0, 1), tree
            elif token is CHOICE:
                new = []
                for t in data:
                    new.extend(self._comp(t, links))
                links = new
            elif token is HASH:
                links = [TagControlNode(links)]
            else:
                links = self._getatom(token, data, links)
        return links

    # links - the links to which the atom should be connected
    # this list may be mutated, if the list is required by the
    # caller, a copy should be passed
    def _getatom(self, token, data, links):
        if token is CHAR:
            links = [CharacterMatchNode(data, links)]
        elif token is BRACKET:
            characters = []
            classes = []
            compl = 0
            while data:
                token, ch, data = data
                if token is CHAR:
                    if data and data[0] is DASH:
                        # we have a range
                        upper = ord(ch)
                        data = data[2]
                        token, ch1, data = data
                        assert token is CHAR
                        i = ord(ch1)
                        if i > upper:
                            raise ValueError('brace lower limit greater '
                                        'than upper limit [%s-%s]'
                                        % (ch1, ch))
                        while i <= upper:
                            characters.append(chr(i))
                            i += 1
                    else:
                        characters.append(ch)
                elif token is DASH:
                    characters.append(ch)
                elif token is CLASS:
                    if ch == 'blank':
                        characters.extend(' \t')
                    elif ch == 'digit':
                        characters.extend('0123456789')
                    elif ch == 'xdigit':
                        characters.extend('0123456789abcdefABCDEF')
                    else:
                        classes.append(ch)
                else:
                    assert token is COMPLEMENT
                    assert not data
                    compl = 1
            if compl:
                if classes:
                    links = [ComplexCharacterComplement(
                                characters, classes, links)]
                elif characters:
                    links = [CharacterMatchNotNode(characters, links)]
                else:
                    raise ParseError('empty bracket expression')
            else:
                nlinks = []
                if characters:
                    nlinks.append(CharacterMatchNode(characters, links))
                for c in classes:
                    func = _class_functions[c]
                    nlinks.append(CharacterNode(func, links))
                if nlinks:
                    links = nlinks
                else:
                    raise ParseError('empty bracket expression')
        elif token is PAREN:
            links = self._comp(data, links)
        elif token is STARTANCHOR:
            links = [StartAnchorNode(links)]
        elif token is ENDANCHOR:
            links = [EndAnchorNode(links)]
        elif token is DOT:
            links = [CharacterNode(Always, links)]
        else:
            raise ParseError('Misplaced %s token' % token)
        return links

if __name__ == '__main__':
    # Almost POSIX extended regular expressions, plus:

    # 1. Search multiple patterns simultaneously - return
    # longest-leftmost result - if results have same length
    # and startpos, pattern added earlier succeeds
    pattern = Pattern()
    pattern.addRegExp(r'(ab+c*)', 1)
    pattern.addRegExp(r'bf(ab+)*', 2)
    pattern.addRegExp(r'^(a(bc)?)*$', 3)
    pattern.addRegExp(r'01x?(ab+)*2', 'red')
    match = pattern.match('abbbabf')
    assert (match.start(), match.end(), match.value()) == (0, 4, 1)
    match = pattern.match('ddg01abb2s')
    assert (match.start(), match.end(), match.value()) == (3, 9, 'red')

    # 2. Add text in chunks
    pattern = Pattern('hello$', 'done')  # 2nd param can be anything
    pattern.addRegExp('hello', addLinks) # e.g. addLinks is a function
    matcher = Matcher(pattern)
    match = matcher.addChunk('hello')
    # matches second pattern, but may also match first pattern
    assert match is None
    match = matcher.addChunk(', world')
    # we now know text does not match first pattern so match to
    # second pattern succeeds
    assert (match.start(), match.end()) == (0, 5)
    assert match.value() == addLinks
    # After any successful match we need to create a new Matcher
    # Indexes start from 0 again
    matcher = Matcher(pattern)
    match = matcher.addChunk(' and again hello')
    # again, no match yet since text may match the first pattern
    assert match is None
    match = matcher.addFinal('')
    # we now know that both patterns match - same start and length
    # so pattern added first wins
    assert (match.start(), match.end()) == (11, 16)
    assert match.value() == 'done'

    # 3. Flexible capturing using tags (#)
    # positions 3,8 are limits of first alphanumeric sequence
    # positions 9,14 are limits of second alphanumeric sequence
    # Note: use \# to match a literal #
    pattern = Pattern('([[:space:]]+#[[:alnum:]]+#)+!')
    match = pattern.match('!\t\thello world!')
    assert match.start() == 1
    assert match.end() == 15
    assert match.tags() == (3, 8, 9, 14)

    # 4. Greedy and reluctant matching
    # a{2,4}? matches as few characters as possible (2)
    # a?? matches as few characters as possible (0)
    # a? matches as many characters as possible (1)
    # a* matches as many characters as possible (4)
    # a+ matches as many characters as possible (1)
    # (a* gets to be greedy before a+, so a* eats more characters,
    # however the requirement for a+ to match at least one, in order
    # that the entire match is successful, causes a* to match 4, not 5)
    pattern = Pattern('a{2,4}?#a??#a?#a*#a+#')
    assert pattern.match('aaaaaaaa').tags() == (2, 2, 3, 7, 8)
