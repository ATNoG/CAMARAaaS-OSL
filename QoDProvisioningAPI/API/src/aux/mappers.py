from database.base_models import Provisioning, Device

# Helper Function
def map_device_to_dict(device: Device) -> dict:
    return {
        "phone_number": device.phone_number,
        "network_access_identifier": device.network_access_identifier,
        "ipv4_address": {
            "public_address": device.ipv4_public_address,
            "private_address": device.ipv4_private_address,
            "public_port": device.ipv4_public_port
        },
        "ipv6_address": device.ipv6_address
    }