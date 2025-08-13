from tamm import _helpers


class PrettyPrintListedEntities:
    def __init__(self, listing_function):
        self.listing_function = listing_function

    def print(self, include_descriptions=False, filter_deprecated=False, wide=False):
        entities = self.listing_function(
            include_descriptions=include_descriptions,
            filter_deprecated=filter_deprecated,
        )
        if not entities:
            print(
                "\n(No non-deprecated models found, check that you have permission "
                "to list them.\nUse -a to include deprecated models.)\n"
            )
            return
        if include_descriptions:
            max_len_names = max(len(name) for name in entities)
            paddings = (" " * (max_len_names + 4 - len(name)) for name in entities)
            lines = [
                name + padding + descr
                for padding, (name, descr) in zip(paddings, entities.items())
            ]
        else:
            lines = entities

        if not wide:
            lines = _helpers.truncate_lines_for_terminal(*lines)
        print("\n".join(lines))
