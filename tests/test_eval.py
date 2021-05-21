import textwrap

from tylaireum.api.backends import cpp


class TestCPP:
    def test_hello_world(self):
        DOC = textwrap.dedent(
            R"""
            main:
                println("Hello world!")
             """
        ).strip()
        assert cpp.evaluate(DOC).stdout.decode() == "Hello world!\n"
