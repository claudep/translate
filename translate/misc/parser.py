import argparse
import logging
import sys

from translate import __version__
from translate.misc.dictutils import ordereddict as OrderedDict
from translate.misc import progressbar


class ManPageAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        sys.stdout.write(self.format_manpage(parser))
        sys.exit(0)

    def format_manpage(self, parser):
        """returns a formatted manpage"""
        result = []
        prog = parser.prog
        ttk_version = "Translate Toolkit %s " % __version__.sver
        result.append('.\\" Autogenerated manpage\n')
        result.append('.TH %s 1 "%s" "" "%s"\n' % (prog,
            ttk_version, ttk_version))
        result.append('.SH NAME\n')
        result.append('%s \\- %s\n' % (prog,
                                       parser.description.split('\n\n')[0]))
        result.append('.SH SYNOPSIS\n')
        result.append('.PP\n')
        usage = "\\fB%s " % parser.prog
        usage += " ".join([parser.getusageman(option) for option in parser.option_list])
        usage += "\\fP"
        result.append('%s\n' % usage)
        description_lines = parser.description.split('\n\n')[1:]
        if description_lines:
            result.append('.SH DESCRIPTION\n')
            result.append('\n\n'.join([re.sub('\.\. note::', 'Note:', l)
                                              for l in description_lines]))
        result.append('.SH OPTIONS\n')
        ManHelpFormatter().store_option_strings(self)
        result.append('.PP\n')
        for option in parser.option_list:
            result.append('.TP\n')
            result.append('%s\n' % str(option).replace('-', '\-'))
            result.append('%s\n' % option.help.replace('-', '\-'))
        return "".join(result)


class BaseParser(object):
    # A list of additional CLI options, possible options are:
    # 'threshold', 'fuzzy', 'duplicates', 'multifile'
    common_options = []
    progress_types = OrderedDict([
        ("none", progressbar.NoProgressBar),
        ("bar", progressbar.HashProgressBar),
        ("dots", progressbar.DotsProgressBar),
        ("names", progressbar.MessageProgressBar),
        ("verbose", progressbar.VerboseProgressBar),
    ])
    error_level_types = [
        "none", "message", "exception", "traceback",
    ]
    # extract = True: from source to translation format,
    # extract = False: from translation to source using templates
    extract = True

    def __init__(self, description=None):
        logging.basicConfig(format="%(name)s: %(levelname)s: %(message)s")
        self.parser = argparse.ArgumentParser(description=description)
        # CLI options that are common to all commands
        self.parser.add_argument("input", nargs=1,
                                 help="input file/directory to read from")
        self.parser.add_argument("output", nargs=1,
                                 help="output file/directory to write to")
        self.parser.add_argument('--version', action='version',
                                 version='%(prog)s ' + __version__.sver)
        self.parser.add_argument("--manpage", action=ManPageAction, nargs=0,
                                 help="output a manpage based on the help")
        self.parser.add_argument("--progress", choices=list(self.progress_types.keys()),
                                 default="bar",
                                 help="show progress as: %s" % (", ".join(self.progress_types.keys())))
        self.parser.add_argument("--errorlevel", choices=self.error_level_types, default="message",
                                 help="show errorlevel as: %s" % (", ".join(self.error_level_types)))
        self.parser.add_argument("-x", "--exclude", action='append', metavar='EXCLUDE',
                                 default=["CVS", ".svn", "_darcs", ".git", ".hg", ".bzr"],
                                 help="exclude names matching EXCLUDE from input paths")
        if not self.extract:
            self.parser.add_argument("-t", "--template", nargs=1,
                                     help="template file/directory for merging translations")
        self.parser.add_argument("-S", "--timestamp", action='store_true',
                                 help="skip conversion if the output file has newer timestamp")

        # CLI options specific to more than one command
        if 'threshold' in self.common_options:
            # Add an option to output only stores where translation percentage
            # exceeds the threshold.
            self.parser.add_argument(
                "--threshold", dest="output_threshold", metavar="PERCENT", type=int,
                help="only convert files where the translation completion is above PERCENT")

        if 'fuzzy' in self.common_options:
            # Add an option to include fuzzy translations.
            self.parser.add_argument(
                "--fuzzy", dest="includefuzzy", action="store_true",
                help="use translations marked fuzzy")
            self.parser.add_argument(
                "--nofuzzy", dest="includefuzzy", action="store_false",
                help="don't use translations marked fuzzy (default)")

        if 'duplicates' in self.common_options:
            # Add an option to say what to do with duplicate strings.
            self.parser.add_argument(
                "--duplicates", dest="duplicate_style", default='msgctxt',
                choices=["msgctxt", "merge"],
                help="what to do with duplicate strings (identical source text): merge, msgctxt")

        if 'multifile' in self.common_options:
            # Add an option to say how to split the po/pot files.
            self.parser.add_argument(
                "--multifile", dest="multifile_style", default='single',
                choices=["single", "toplevel", "onefile"],
                help="how to split po/pot files (single, toplevel or onefile)")

    def parse_args(self):
        return self.parser.parse_args()
