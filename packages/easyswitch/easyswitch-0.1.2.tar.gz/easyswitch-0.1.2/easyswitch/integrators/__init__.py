from easyswitch.utils import import_module_from

# LOAD ADAPTER PLUGIN
def load_adapter(name: str):
    """ loads Aadapter module by name. """

    return import_module_from(
        f'easyswitch.integrators.{name.lower()}'
    )