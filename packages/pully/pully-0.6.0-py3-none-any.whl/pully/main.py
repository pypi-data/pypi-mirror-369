# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from .cli.parser import get_parser


def main():
    parser = get_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except FileNotFoundError as excinfo:
        parser.error(f"file not found: {excinfo}")
