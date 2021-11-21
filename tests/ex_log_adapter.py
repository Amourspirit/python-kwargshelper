# coding: utf-8
import logging
import textwrap

class LogIndentAdapter(logging.LoggerAdapter):
    """
    Custom Logging adapter
    
    This adapter indents ``msg`` string that have more than one line.
    The frist line is not indented unless the frist line starts with ``\n``.
    """

    def _process_msg(self, msg: str) -> str:
        # first line is special and does not get indented
        # unless it starts with \n
        s = msg
        prefix = ''
        if s[:1] == "\n":  # starts with newline
            s = s[1:]
            lines = ['\n']
            multi_str = s
        else:
            prefix = '\n'
            lines = s.splitlines(keepends=False)
            if len(lines) <= 1:
                return msg
            multi = lines[1:]
            multi_str = "\n".join(multi)
        indent_str = self._indent_str(multi_str)
        result = lines[0] + prefix + indent_str
        if result[-1:] == "\n":
            result = result[:-1]  # remove trailing \n
        return result

    def _indent_str(self, text: str) -> str:
        indent_str = ' ' * 2
        lines = str(text).splitlines(keepends=False)
        indent_lines = []
        for line in lines:
            indent_lines.append(textwrap.indent(line, indent_str))

        return "\n".join(indent_lines)

    def process(self, msg, kwargs):
        """
        Process the logging message and keyword arguments passed in to
        a logging call to insert contextual information. You can either
        manipulate the message itself, the keyword args or both. Return
        the message and kwargs modified (or not) to suit your needs.
        """
        _msg, _kwargs = super().process(msg=msg, kwargs=kwargs)
        if not isinstance(_msg, str) or len(_msg) <= 1:
            return _msg, _kwargs
        result = self._process_msg(_msg)
        return result, _kwargs
