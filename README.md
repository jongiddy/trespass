trespass
========

Regular Expression Engine

Almost POSIX extended regular expressions, plus:

1. Search multiple patterns simultaneously
    ```python
    pattern = Pattern()
    pattern.addRegExp(r'(ab+c*)', 1)
    pattern.addRegExp(r'bf(ab+)*', 2)
    pattern.addRegExp(r'^(a(bc)?)*$', 3)
    pattern.addRegExp(r'01x?(ab+)*2', 'red')
    assert pattern.match('abbbabf') == ((0, 4), 1)
    assert pattern.match('ddg01abb2s') == ((3, 9), 'red')
    ```

2. Add text in chunks
    ```python
    pattern = Pattern('hello$', 'done')
    matcher = Matcher(pattern)
    assert matcher.addChunk('hello, world') is None
    assert matcher.addChunk(' and again hello') is None
    assert matcher.addFinal('') == ((23, 28), 'done')
    ```

3. Flexible capturing using tags (#)
    ```python
    # positions 1,15 are start and end of matching segment
    # positions 3,9 are start of alphanumeric sequences
    # positions 8,14 are end of alphanumeric sequences
    # Note: use \# to match a literal #
    pattern = Pattern('([[:space:]]+#[[:alnum:]]+#)+!')
    assert pattern.match('!\t\thello world!') \
                == ((1, 3, 8, 9, 14, 15), None)
    ```

4. Greedy and reluctant matching
    ```python
    pattern = Pattern('a{2,4}?#a??#a?#a+#a*')
    assert pattern.match('aaaaaaaa') == ((0, 2, 2, 3, 8, 8), None)
    ```
