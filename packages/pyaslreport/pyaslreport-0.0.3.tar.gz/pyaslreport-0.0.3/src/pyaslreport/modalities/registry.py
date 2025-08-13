MODALITY_REGISTRY = {}

def register_modality(name, processor_cls=None, validator_cls=None):
    MODALITY_REGISTRY[name] = {
        "processor": processor_cls,
        "validator": validator_cls,
    }


def get_processor(name):
    """
    Retrieves the processor class for the given modality name.

    :param name: Name of the modality (e.g., "asl", "dsc").
    :return: Processor class if found, raises KeyError otherwise.
    """

    if name not in MODALITY_REGISTRY:
        raise KeyError(f"Processor for modality '{name}' not found.")
    return MODALITY_REGISTRY[name]["processor"]