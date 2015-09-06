import logging
import sys
import traceback


class BaseConvertor(object):
    InStoreClass = None
    OutStoreClass = None

    def __init__(self, options):
        self.options = options
        self.files_to_convert = self.handle_in_out(options.input, options.output)

    def convert(self):
        for input_file, output_file in self.files_to_convert:
            target_store = self.OutStoreClass()
            try:
                with open(input_file, 'rb') as fp:
                    input_store = self.InStoreClass(inputfile=fp)
            except Exception:
                self.warning("Error processing input %s" % input_file, sys.exc_info())
                success = False
                continue
            for source_unit in input_store.units:
                # This will need a common structure for source units!
                target_store.from_source_unit(source_unit)
            with open(output_file, 'wb') as fp:
                target_store.serialize(fp)

    def handle_in_out(self, in_opt, out_opt):
        """
        Handle input and output options received on the command line and
        normalize them to a list of tuples `(input_file, output_file)`.
        """
        # FIXME: to be implemented
        return [(in_opt[0], out_opt[0])]

    def warning(self, msg, exc_info=None):
        """Print a warning message incorporating 'msg' to stderr and exit."""
        if exc_info:
            if self.options.errorlevel == "traceback":
                errorinfo = "\n".join(traceback.format_exception(exc_info[0],
                                      exc_info[1], exc_info[2]))
            elif self.options.errorlevel == "exception":
                errorinfo = "\n".join(traceback.format_exception_only(exc_info[0], exc_info[1]))
            elif self.options.errorlevel == "message":
                errorinfo = str(exc_info[1])
            else:
                errorinfo = ""
            if errorinfo:
                msg += ": " + errorinfo
        logging.getLogger(self.prog_name).warning(msg)
