from dataclasses import dataclass

from src.routers.device_types.router import router as device_types_router
from src.routers.devices.router import router as devices_router
from src.routers.locations.router import router as locations_router
from src.routers.people.router import router as people_router
from src.routers.root.router import router as root_router


@dataclass(frozen=True)
class Router:
    routers = [
        (root_router, "/api/root", ["root"]),
        (device_types_router, "/api/device-types", ["device-types"]),
        (locations_router, "/api/locations", ["locations"]),
        (people_router, "/api/people", ["people"]),
        (devices_router, "/api/devices", ["devices"]),
    ]
