import importlib.resources

JS_STRING = ""

with importlib.resources.files('cr_to_stryker.resources').joinpath('mutation-testing-elements.js').open('r', encoding='utf-8') as f:
        JS_STRING = f.read()