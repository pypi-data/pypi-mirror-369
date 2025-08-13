from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest

from niquests import Session
from niquests._compat import HAS_LEGACY_URLLIB3
from niquests.exceptions import ConnectionError
from niquests.utils import is_ipv4_address, is_ipv6_address

if not HAS_LEGACY_URLLIB3:
    from urllib3 import HttpVersion, ResolverDescription
else:
    from urllib3_future import HttpVersion, ResolverDescription

try:
    import qh3
except ImportError:
    qh3 = None


@pytest.mark.usefixtures("requires_wan")
class TestLiveStandardCase:
    def test_ensure_ipv4(self) -> None:
        with Session(disable_ipv6=True, resolver="doh+google://") as s:
            r = s.get("https://httpbingo.org/get")

            assert r.conn_info.destination_address is not None
            assert is_ipv4_address(r.conn_info.destination_address[0])

    def test_ensure_ipv6(self) -> None:
        if os.environ.get("CI", None) is not None:
            # GitHub hosted runner can't reach external IPv6...
            with pytest.raises(ConnectionError, match="No route to host|unreachable"):
                with Session(disable_ipv4=True, resolver="doh+google://") as s:
                    s.get("https://httpbingo.org/get")
            return

        with Session(disable_ipv4=True, resolver="doh+google://") as s:
            r = s.get("https://httpbingo.org/get")

            assert r.conn_info.destination_address is not None
            assert is_ipv6_address(r.conn_info.destination_address[0])

    def test_ensure_http2(self) -> None:
        with Session(disable_http3=True, base_url="https://httpbingo.org") as s:
            r = s.get("/get")
            assert r.conn_info.http_version is not None
            assert r.conn_info.http_version == HttpVersion.h2
            assert r.url == "https://httpbingo.org/get"

    @pytest.mark.skipif(qh3 is None, reason="qh3 unavailable")
    def test_ensure_http3_default(self) -> None:
        with Session(resolver="doh+cloudflare://") as s:
            r = s.get("https://1.1.1.1")
            assert r.conn_info.http_version is not None
            assert r.conn_info.http_version == HttpVersion.h3

    @patch(
        "urllib3.contrib.resolver.doh.HTTPSResolver.getaddrinfo"
        if not HAS_LEGACY_URLLIB3
        else "urllib3_future.contrib.resolver.doh.HTTPSResolver.getaddrinfo"
    )
    def test_manual_resolver(self, getaddrinfo_mock: MagicMock) -> None:
        with Session(resolver="doh+cloudflare://") as s:
            with pytest.raises(ConnectionError):
                s.get("https://httpbingo.org/get")

        assert getaddrinfo_mock.call_count

    def test_not_owned_resolver(self) -> None:
        resolver = ResolverDescription.from_url("doh+cloudflare://").new()

        with Session(resolver=resolver) as s:
            s.get("https://httpbingo.org/get")

            assert resolver.is_available()

        assert resolver.is_available()

    def test_owned_resolver_must_close(self) -> None:
        with Session(resolver="doh+cloudflare://") as s:
            s.get("https://httpbingo.org/get")

            assert s.resolver.is_available()

        assert not s.resolver.is_available()

    def test_owned_resolver_must_recycle(self) -> None:
        s = Session(resolver="doh+cloudflare://")

        s.get("https://httpbingo.org/get")

        s.resolver.close()

        assert not s.resolver.is_available()

        s.get("https://httpbingo.org/get")

        assert s.resolver.is_available()

    @pytest.mark.skipif(os.environ.get("CI") is None, reason="Worth nothing locally")
    def test_happy_eyeballs(self) -> None:
        """A bit of context, this test, running it locally does not get us
        any confidence about Happy Eyeballs. This test is valuable in Github CI where IPv6 addresses are unreachable.
        We're using a custom DNS resolver that will yield the IPv6 addresses and IPv4 ones.
        If this hang in CI, then you did something wrong...!"""
        with Session(resolver="doh+cloudflare://", happy_eyeballs=True) as s:
            r = s.get("https://httpbingo.org/get")

            assert r.ok

    def test_early_response(self) -> None:
        received_early_response: bool = False

        def callback_on_early(early_resp) -> None:
            nonlocal received_early_response
            if early_resp.status_code == 103:
                received_early_response = True

        with Session() as s:
            resp = s.get(
                "https://early-hints.fastlylabs.com/",
                hooks={"early_response": [callback_on_early]},
            )

            assert resp.status_code == 200
            assert received_early_response is True

    @pytest.mark.skipif(qh3 is None, reason="qh3 unavailable")
    def test_preemptive_add_http3_domain(self) -> None:
        with Session() as s:
            s.quic_cache_layer.add_domain("one.one.one.one")

            resp = s.get("https://one.one.one.one")

            assert resp.http_version == 30

    @pytest.mark.skipif(qh3 is None, reason="qh3 unavailable")
    def test_preemptive_add_http3_domain_wrong_port(self) -> None:
        with Session() as s:
            s.quic_cache_layer.add_domain("one.one.one.one", 6666)

            resp = s.get("https://one.one.one.one")

            assert resp.http_version == 20

    @pytest.mark.skipif(qh3 is None, reason="qh3 unavailable")
    def test_preemptive_exclude_http3_domain(self) -> None:
        with Session() as s:
            s.quic_cache_layer.exclude_domain("one.one.one.one")

            for _ in range(2):
                resp = s.get("https://one.one.one.one")
                assert resp.http_version == 20
