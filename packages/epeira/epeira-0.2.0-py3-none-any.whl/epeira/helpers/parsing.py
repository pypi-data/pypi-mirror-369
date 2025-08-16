"""String parsing tools."""
def get_default_archetype_prefix():
    """Return standard string prefix for archetype classes, to be replaced with domain strings."""
    return "ARCH"

def get_subcomponent_indicator():
    """Return string that indicates a model is meant to be a subcomponent."""
    return "subcomponent"

def get_model_input_suffix():
    """Return the expected suffix for models (component variants or mixins) from and input dictionary."""
    return "_model"

def get_model_catalog_suffix():
    """Return the expected suffix for a model grouping from a catalog."""
    return get_model_input_suffix()+'s'

def get_variant_indicator():
    """Return the indicator for a component variant, which will usually be succeeded by a suffix."""
    return "_variant"

def get_component_input_suffix():
    """Return the full suffix for a component variant parameter in an input dictionary."""
    return get_variant_indicator() + get_model_input_suffix()

def get_mixin_input_suffix(mixin_name:str):
    """Return the full suffix for a specific mixin type from an input dictionary."""
    return "_" + mixin_name + get_model_input_suffix()
