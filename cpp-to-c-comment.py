#!/usr/bin/env python3
#
# Script to transform C++ comments into C-style
#
# blah blah // this comment      TO            blah blah /* this comment */
#
# // this comment                              /*
# // and this comment            TO             * this comment
#                                               * and this comment
#                                               */
#
# A blank line will inserted before single or block comments (not trailing ones, as the first
# above), if the comment indent is <= than that of previous line
#
# Only one input file must be passed as argument. The following are assumed:
#
#   - The file is well-formed
#   - No CPP comments inside already existing C comments, and vice versa
#   - All indents are uniformly made with either tabs or spaces, but not mixed
#
# Output is printed to stdout

import sys

if len(sys.argv) != 2:
    print(sys.argv[0] + ": needs at exactly one argument")
    sys.exit(1)

comments = []       # Pending comments are captured here
prev_line = ""      # Last printed line
indent = ""         # Indent string of captured comments so far
lines = 0

# Make sure @str is padded by @head and @tail at both ends if there isn't white
# space already
def pad_space(str, head = " ", tail = " "):
    s = str
    if len(s) > 0:
        if head and not s[0].isspace():
            s = head + s
        if tail and not s[-1].isspace():
            s = s + tail
    return s

# Replace all "*/" in @str so that it can be placed inside a C comment
safe_string = lambda str: str.replace("*/", " ")

# Print a blank line if the previous line wasn't blank. Ignore at the at the
# beginning of the file
def print_blank():
    if lines > 1 and not prev_line.isspace():
        print()

# Print a single line of comment. Put a blank line beforehand, if there wasn't
# one
def print_one_comment(pre, post):
    print(pre + "/*" + pad_space(safe_string(post)) + "*/")

# Flush all comments collected so far. If there's only one line, print that
# alone; otherwise print a block comment with a blank line before
def flush_comments():
    global comments
    global indent

    l = len(comments)
    if l == 0:
        # Nothing to print
        return

    # Calculate the indent of previous line
    prev_indent = len(prev_line) - len(prev_line.lstrip())

    # If the indent of the previous line matches with that of the current
    # one, we print a blank line, to make the comment stand out
    # Additionally, we ignore previous lines that at column zero, so that we don't insert a
    # blank line immediately after a label and such
    if prev_indent > 0 and len(indent) <= prev_indent:
        print_blank()

    if l == 1:
        # Only one comment
        print_one_comment(indent, comments[0])
    else:
        # Block comment. Print a blank line only after a line at non-zero indent
        print(indent + "/*")
        for c in comments:
            print(indent + " *" + pad_space(safe_string(c), tail = ""))
        print(indent + " */")

    # Clear all comments
    comments = []
    indent = ""

# Capture a comment
def add_comment(pre, post):
    global indent
    global prev_line
    global line

    if len(pre) > 0 and not pre.isspace():
        # something // blah blah
        # Trailing comment. Flush pending comments and print this alone
        flush_comments()
        print_one_comment(pre, post);
        prev_line = line
    else:
        # Standalone comment
        indent = pre
        comments.append(post)

#
# Start processing input file
#
with open(sys.argv[1]) as f:
    for line in f:
        lines += 1

        # Partition line (stripped off tailing new line) at the comment
        pre, c, post = line.rstrip('\r\n').partition("//")

        if len(c) == 0:
            # This line doesn't have comment. Print as is
            flush_comments()
            print(pre)

            # Save the current line
            prev_line = line
            continue

        elif len(comments) > 0:
            # Check the indent of this comment
            if len(indent) != len(pre):
                # Indent of this comment doesn't match that of captured comments
                # Flush comments captured so far
                flush_comments()

        # Capture comment
        add_comment(pre, post)

    # Flush all comments
    flush_comments()


# vim: set sw=4 sts=4 et tw=80:
