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
# Only one input file must be passed as agument. The input file is assumed to be
# well-formed.
#

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
def pad_space(str, head = None, tail = None):
    s = str
    if len(s) == 0:
        return ""
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
    if (lines > 0 and not prev_line.isspace()):
        print()

# Print a single line of comment. Put a blank line beforehand, if there wasn't
# one
def print_one_comment(pre, post, blank):
    if (blank):
        print_blank()
    print(pre + "/*" + pad_space(safe_string(post), head = " ") + " */")

# Flush all comments collected so far.  If there's only one line, print that
# alone; otherwise print a block comment with a blank line before
def flush_comments():
    global comments
    global indent

    l = len(comments)
    if l == 0:
        # Nothing to print
        return
    elif l == 1:
        # Only one comment
        print_one_comment(indent, comments[0], False)
    else:
        # Print a block comment
        print_blank()
        print(indent + "/*")
        for c in comments:
            print(indent + " *" + pad_space(safe_string(c)))
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
        # someting // blah blah
        # Trailing comment. Flush pending comments and print this alone
        flush_comments()
        print_one_comment(pad_space(pre, tail = " "), post, False);
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

        # Partition line at the comment
        pre, c, post = line.partition("//")
        if len(c) == 0:
            # This line doesn't have comment. Print as is
            flush_comments()
            print(pre, end="")

            # Save the current line
            prev_line = line

        elif len(comments) == 0:
            # If we haven't captured any comments yet
            add_comment(pre, post.rstrip())

        else:
            # Check the indent of this comment
            if len(indent) != len(pre):
                # Indent of this comment doesn't match that of captured comments
                # Flush comments captured so far
                flush_comments()

            # Start a new capture
            add_comment(pre, post.rstrip())

    flush_comments()


# vim: set sw=4 sts=4 et tw=80:
