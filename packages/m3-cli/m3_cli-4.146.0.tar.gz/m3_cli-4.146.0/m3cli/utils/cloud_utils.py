import enum


class Cloud(enum.Enum):
    """
      The enumeration of the possible cloud names matched on the flag that
      means whether cloud public or private.
    """
    # Public cloud providers
    AWS = ('AWS', False)
    AZURE = ('AZURE', False)
    GOOGLE = ('GOOGLE', False)
    YANDEX = ('YANDEX', False)
    # Private cloud providers
    OPEN_STACK = ('OPEN_STACK', True)
    HPOO = ('HPOO', True)
    CSA = ('CSA', True)
    EXOSCALE = ('EXOSCALE', True)
    HARDWARE = ('HARDWARE', True)
    ENTERPRISE = ('ENTERPRISE', True)
    VMWARE = ('VMWARE', True)
    VSPHERE = ('VSPHERE', True)
    NUTANIX = ('NUTANIX', True)
    WORKSPACE = ('WORKSPACE', True)
    AOS = ('AOS', True)

    def __init__(self, cloud_name, is_private):
        self.cloud_name = cloud_name
        self.is_private = is_private


def cloud_exist(cloud_name):
    return cloud_name in Cloud.__members__


def assert_cloud_exist(cloud_name):
    if not cloud_exist(cloud_name):
        raise AssertionError(f'Cloud \'{cloud_name}\' does not exists')


def is_public(cloud_name):
    assert_cloud_exist(cloud_name)
    for c in Cloud:
        if c.cloud_name == cloud_name:
            return not c.is_private
