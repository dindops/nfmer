import json

from nfmer.api.v1.api import api


def main() -> None:
    openapi_schema = api.openapi()
    with open("openapi.json", "w") as f:
        json.dump(openapi_schema, f, indent=2)


if __name__ == "__main__":
    main()
