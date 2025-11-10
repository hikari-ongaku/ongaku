from __future__ import annotations

from ongaku.internal.routes import BuiltRoute
from ongaku.internal.routes import Route


class TestRoute:
    def test_properties(self):
        route = Route("GET", "/test/{param}", include_version=False)

        assert route.method == "GET"
        assert route.path == "/test/{param}"
        assert route.include_version is False

    def test_build(self):
        route = Route("GET", "/test/{param}", include_version=False)

        assert route.build(param="beanos") == BuiltRoute(
            route=route,
            path="/test/beanos",
        )

    def test_build_with_version(self):
        route = Route("GET", "/test/{param}", include_version=True)

        assert route.build(param="beanos") == BuiltRoute(
            route=route,
            path="/v4/test/beanos",
        )


class TestBuiltRoute:
    def test_properties(self):
        route = Route("GET", "/test/{param}", include_version=False)
        built_route = BuiltRoute(route=route, path="/test/beanos")

        assert built_route.route == route
        assert built_route.path == "/test/beanos"
