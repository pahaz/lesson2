import logging
import re

__author__ = 'pahaz'
logger = logging.getLogger(__name__)


def debug(ctx, vars):
    print(vars)
    return ''


EXPRESSION_PATTERN = '{{ (?P<expression>.+?) }}'
FOR_BLOCK_PATTERN = '{% for (?P<var>[a-zA-Z0-9]+?) in ' \
                    '(?P<iterator>.+?) %}' \
                    '(?P<body>.+)' \
                    '{% endfor %}'
IF_BLOCK_PATTERN = '{% if (?P<condition>.+?) %}' \
                   '(?P<body_true>.+?)' \
                   '(?:{% else %}(?P<body_false>.+?))?' \
                   '{% endif %}'


BLOCK_SPECIFICATION = [
    ('FOR', FOR_BLOCK_PATTERN.replace(' ', '\\s*'), debug),
    ('IF', IF_BLOCK_PATTERN.replace(' ', '\\s*'), debug),
    ('EXPRESSION', EXPRESSION_PATTERN.replace(' ', '\\s*'), debug),
    ('OTHER', '(?P<other>.+?)', lambda ctx, vars, render: vars['other']),
]

BLOCK_REGEXP = '|'.join(
    '(?P<' + name + '>' + regexp + ')'
    for name, regexp, _ in BLOCK_SPECIFICATION
)


def render(template, context=None):
    if not context:
        context = {}

    tokens = re.finditer(BLOCK_REGEXP, template, re.MULTILINE | re.DOTALL)
    for token in tokens:
        group = token.lastgroup
        value = token.group(0)
        variables = token.groupdict()
        print('TOKEN name=%s value=%s vars=%r', group, value, variables)


