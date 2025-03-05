import argparse

from .._case_style import CaseStyle, to_case_style


def main():
    case_names = [s.name for s in CaseStyle]

    parser = argparse.ArgumentParser(description='Convert a string to a different case style')
    parser.add_argument(
        '--case', type=str, required=True,
        choices=case_names,
        help='The case style to convert to',
    )
    parser.add_argument(
        'input', nargs='+',
        help='The input string'
    )

    args = parser.parse_args()

    assert args.case in case_names, f'Unknown case style {args.case}'

    case_style = CaseStyle[args.case]
    output = to_case_style(' '.join(args.input), case_style)

    print(output, end='')
