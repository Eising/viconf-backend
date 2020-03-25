import pystache
import re
from .constants import DEFAULT_TAGS, FORM_TAGS


class ViconfMustacheTagException(Exception):
    pass


class ViconfMustache(object):

    def __init__(self, template):
        self.template = template

    def parse_keys(self):
        # fragile, relies on pystache internals
        parsed_template = pystache.parse(self.template)
        keys = []
        parse_tree = parsed_template._parse_tree
        keyed_classes = (pystache.parser._EscapeNode,
                         pystache.parser._LiteralNode,
                         pystache.parser._InvertedNode,
                         pystache.parser._SectionNode)
        for token in parse_tree:
            if isinstance(token, keyed_classes):
                keys.append(token.key)
        # return list of unique items
        # (json does not like sets)
        return list(set(keys))

    def get_configurable_tags(self):
        tags = self.parse_keys()
        for defaulttag in DEFAULT_TAGS:
            if defaulttag in tags:
                tags.remove(defaulttag)

        return tags

    def list_tags(self):
        # This is a bit of a dirty monkey patch, and should probably
        # be rewritten in to a full parser.
        tags = re.compile(r'\{\{\s*#([^}]+\s*)\}\}')
        return tags.findall(self.template)

    def parse_template_tags(self):
        result = {
            'form_tags': set(),
            'list_tags': self.list_tags()
        }
        tags = self.parse_keys()
        result['all_tags'] = list(tags)
        result['user_tags'] = list(tags)

        for tag in FORM_TAGS:
            if tag in tags:
                result['user_tags'].remove(tag)
                result['form_tags'].add(tag)

        result['all_tags'] = tags

        return result

    def compile(self, params, service_params):
        # validate whether all tags are filled out
        tags = self.parse_template_tags()
        param_tags = list(params.keys())

        for tag in tags['user_tags']:
            if tag not in param_tags:
                raise ViconfMustacheTagException(f"Missing tag {tag}")

        for param, value in service_params.items():
            params[param] = value

        return pystache.render(self.template, params)
