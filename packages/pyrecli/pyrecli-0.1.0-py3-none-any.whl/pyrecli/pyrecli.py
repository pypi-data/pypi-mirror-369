import sys
import argparse

from pyrecli.command.scan import scan_command
from pyrecli.command.send import send_command
from pyrecli.command.script import script_command
from pyrecli.command.rename import rename_command
from pyrecli.command.grabinv import grabinv_command
from pyrecli.command.docs import docs_command


def main():
    parser = argparse.ArgumentParser(prog='pyrecli', description='Command line utilities for DiamondFire templates')
    subparsers = parser.add_subparsers(dest='command', help='Available commands:', required=True, metavar='<command>')

    parser_scan = subparsers.add_parser('scan', help='Scan the current plot templates with CodeClient')
    parser_scan.add_argument('output_path', help='The file to output template data to', type=str)

    parser_send = subparsers.add_parser('send', help='Send templates to DiamondFire with CodeClient')
    parser_send.add_argument('input_path', help='The file containing template data', type=str)

    parser_script = subparsers.add_parser('script', help='Create python scripts from template data')
    parser_script.add_argument('input_path', help='The file containing template data', type=str)
    parser_script.add_argument('output_path', help='The file or directory to output to', type=str)
    parser_script.add_argument('--onefile', help='Output template data as a single script', action='store_true')
    parser_script.add_argument('--indent_size', '-i', help='The multiple of spaces to add when indenting lines', type=int, default=4)
    parser_script.add_argument('--literal_shorthand', '-ls', help='Output Text and Number items as strings and ints respectively', action='store_false')
    parser_script.add_argument('--var_shorthand', '-vs', help='Write all variables using variable shorthand', action='store_true')
    parser_script.add_argument('--preserve_slots', '-s', help='Save the positions of items within chests', action='store_true')
    parser_script.add_argument('--build_and_send', '-b', help='Add `.build_and_send()` to the end of the generated template(s)', action='store_true')

    parser_rename = subparsers.add_parser('rename', help='Rename a variable')
    parser_rename.add_argument('input_path', help='The file containing template data', type=str)
    parser_rename.add_argument('var_to_rename', help='The variable to rename', type=str)
    parser_rename.add_argument('new_var_name', help='The new name for the variable', type=str)
    parser_rename.add_argument('--var_to_rename_scope', '-s', help='The scope to match', type=str, default=None)
    parser_rename.add_argument('--output_path', '-o', help='The file or directory to output to', type=str, default=None)

    parser_grabinv = subparsers.add_parser('grabinv', help='Save all templates in the inventory to a file with CodeClient')
    parser_grabinv.add_argument('output_path', help='The file to output template data to', type=str)

    parser_docs = subparsers.add_parser('docs', help='Generate markdown documentation from template data')
    parser_docs.add_argument('input_path', help='The file containing template data', type=str)
    parser_docs.add_argument('output_path', help='The file or directory to output to', type=str)
    parser_docs.add_argument('title', help='The title for the docs', type=str)
    parser_docs.add_argument('--include_hidden', '-ih', help='Include hidden functions and processes', action='store_true')
    parser_docs.add_argument('--notoc', help='Omit the table of contents', action='store_true')

    parsed_args = parser.parse_args()

    match parsed_args.command:
        case 'scan':
            command_result = scan_command(parsed_args.output_path)
        
        case 'send':
            command_result = send_command(parsed_args.input_path)
        
        case 'script':
            scriptgen_flags = {
                'indent_size': parsed_args.indent_size, 
                'literal_shorthand': parsed_args.literal_shorthand,
                'var_shorthand': parsed_args.var_shorthand,
                'preserve_slots': parsed_args.preserve_slots,
                'build_and_send': parsed_args.build_and_send
            }
            command_result = script_command(parsed_args.input_path, parsed_args.output_path, parsed_args.onefile, scriptgen_flags)
        
        case 'rename':
            command_result = rename_command(
                parsed_args.input_path, parsed_args.output_path,
                parsed_args.var_to_rename, parsed_args.new_var_name, parsed_args.var_to_rename_scope
            )
        
        case 'grabinv':
            command_result = grabinv_command(parsed_args.output_path)
        
        case 'docs':
            command_result = docs_command(
                parsed_args.input_path, parsed_args.output_path,
                parsed_args.title, parsed_args.include_hidden, parsed_args.notoc
            )
    
    if command_result.is_err():
        print(command_result.err_value)
        sys.exit(1)
    
    sys.exit(0)

if __name__ == '__main__':
    main()
