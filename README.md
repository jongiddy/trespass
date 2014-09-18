trespass
========

Regular Expression Engine

Almost POSIX extended regular expressions, plus:

1. Search multiple patterns simultaneously - return longest-leftmost result - 
   if results have same length and startpos, pattern added earlier succeeds
    ```python
    pattern = Pattern()
    pattern.addRegExp(r'(ab+c*)', 1)
    pattern.addRegExp(r'bf(ab+)*', 2)
    pattern.addRegExp(r'^(a(bc)?)*$', 3)
    pattern.addRegExp(r'01x?(ab+)*2', 'red')
    match = pattern.match('abbbabf')
    assert (match.start(), match.end(), match.value()) == (0, 4, 1)
    match = pattern.match('ddg01abb2s')
    assert (match.start(), match.end(), match.value()) == (3, 9, 'red')
    ```

2. Add text in chunks
    ```python
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
    ```

3. Flexible capturing using tags (#)
    ```python
    # positions 3,8 are limits of first alphanumeric sequence
    # positions 9,14 are limits of second alphanumeric sequence
    # Note: use \# to match a literal #
    pattern = Pattern('([[:space:]]+#[[:alnum:]]+#)+!')
    match = pattern.match('!\t\thello world!')
    assert match.start() == 1
    assert match.end() == 15
    assert match.tags() == (3, 8, 9, 14)
    ```

4. Greedy and reluctant matching
    ```python
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
    ```    
