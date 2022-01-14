import jsbeautifier
import json


def json_log(data):
    opts = jsbeautifier.default_options()
    opts.indent_size = 2
    return jsbeautifier.beautify(json.dumps(data), opts)