from __future__ import annotations

import asyncio
import json
import os

import pytest

from niquests import AsyncResponse, AsyncSession, Response
from niquests.exceptions import MultiplexingError


@pytest.mark.usefixtures("requires_wan")
@pytest.mark.asyncio
class TestAsyncWithoutMultiplex:
    async def test_awaitable_get(self):
        async with AsyncSession(base_url="https://httpbingo.org") as s:
            resp = await s.get("/get")

            assert resp.lazy is False
            assert resp.status_code == 200

    async def test_awaitable_redirect_chain(self):
        async with AsyncSession() as s:
            resp = await s.get("https://httpbingo.org/redirect/2")

            assert resp.lazy is False
            assert resp.status_code == 200

    async def test_awaitable_redirect_chain_stream(self):
        async with AsyncSession() as s:
            resp = await s.get("https://httpbingo.org/redirect/2", stream=True)

            assert resp.lazy is False
            assert resp.status_code == 200
            assert await resp.json()

    async def test_async_session_cookie_dummylock(self):
        async with AsyncSession() as s:
            await s.get("https://httpbingo.org/cookies/set?hello=world")
            assert len(s.cookies)
            assert "hello" in s.cookies

    async def test_concurrent_task_get(self):
        async def emit():
            responses = []

            async with AsyncSession() as s:
                responses.append(await s.get("https://httpbingo.org/get"))
                responses.append(await s.get("https://httpbingo.org/delay/5"))

            return responses

        foo = asyncio.create_task(emit())
        bar = asyncio.create_task(emit())

        responses_foo = await foo
        responses_bar = await bar

        assert len(responses_foo) == 2
        assert len(responses_bar) == 2

        assert all(r.status_code == 200 for r in responses_foo + responses_bar)

    async def test_with_async_iterable(self):
        async with AsyncSession() as s:

            async def fake_aiter():
                await asyncio.sleep(0.01)
                yield b"foo"
                await asyncio.sleep(0.01)
                yield b"bar"

            r = await s.post("https://httpbingo.org/post", data=fake_aiter())

            assert r.status_code == 200
            assert r.json()["data"] == "data:application/octet-stream;base64,Zm9vYmFy"

    async def test_with_async_auth(self):
        async with AsyncSession() as s:

            async def fake_aauth(p):
                await asyncio.sleep(0.01)
                p.headers["X-Async-Auth"] = "foobar"
                return p

            r = await s.get("https://httpbingo.org/get", auth=fake_aauth)

            assert r.status_code == 200
            assert "X-Async-Auth" in r.json()["headers"]

    async def test_early_response(self) -> None:
        received_early_response: bool = False

        async def callback_on_early(early_resp) -> None:
            nonlocal received_early_response
            if early_resp.status_code == 103:
                received_early_response = True

        async with AsyncSession() as s:
            resp = await s.get(
                "https://early-hints.fastlylabs.com/",
                hooks={"early_response": [callback_on_early]},
            )

            assert resp.status_code == 200
            assert received_early_response is True

    async def test_iter_line(self) -> None:
        async with AsyncSession() as s:
            r = await s.get("https://httpbingo.org/html", stream=True)
            content = b""

            async for line in r.iter_lines():
                assert isinstance(line, bytes)
                content += line

            assert content
            assert b"Herman Melville - Moby-Dick" in content

    async def test_iter_line_decode(self) -> None:
        async with AsyncSession() as s:
            r = await s.get("https://httpbingo.org/html", stream=True)
            content = ""

            async for line in r.iter_lines(decode_unicode=True):
                assert isinstance(line, str)
                content += line

            assert content
            assert "Herman Melville - Moby-Dick" in content

    async def test_explicit_close_in_streaming_response(self) -> None:
        async with AsyncSession() as s:
            try:
                r = await s.get("https://httpbingo.org/html", stream=True)
            finally:
                await r.close()


@pytest.mark.usefixtures("requires_wan")
@pytest.mark.asyncio
class TestAsyncWithMultiplex:
    async def test_awaitable_get(self):
        async with AsyncSession(multiplexed=True) as s:
            resp = await s.get("https://httpbingo.org/get")

            assert resp.lazy is True
            await s.gather()
            assert resp.status_code == 200

    async def test_awaitable_redirect_with_lazy(self):
        async with AsyncSession(multiplexed=True) as s:
            resp = await s.get("https://httpbingo.org/redirect/3")

            assert resp.lazy is True
            await s.gather()
            assert resp.status_code == 200

    async def test_awaitable_redirect_direct_access_with_lazy(self):
        async with AsyncSession(multiplexed=True) as s:
            resp = await s.get("https://httpbingo.org/redirect/3")

            assert resp.lazy is True

            with pytest.raises(MultiplexingError):
                resp.status_code

            await s.gather(resp)

            assert resp.status_code == 200
            assert len(resp.history) == 3
            assert all(isinstance(_, Response) for _ in resp.history)

    async def test_awaitable_stream_redirect_direct_access_with_lazy(self):
        async with AsyncSession(multiplexed=True) as s:
            resp = await s.get("https://httpbingo.org/redirect/3", stream=True)

            assert isinstance(resp, AsyncResponse)
            assert resp.lazy is True

            await resp.json()

            assert resp.lazy is False

            assert resp.status_code == 200
            assert len(resp.history) == 3
            assert all(isinstance(_, Response) for _ in resp.history)

    async def test_awaitable_get_direct_access_lazy(self):
        async with AsyncSession(multiplexed=True) as s:
            resp = await s.get("https://httpbingo.org/get")

            assert resp.lazy is True
            assert isinstance(resp, Response)

            with pytest.raises(MultiplexingError):
                resp.status_code == 200

            await s.gather(resp)
            assert resp.status_code == 200

            resp = await s.get("https://httpbingo.org/get", stream=True)

            assert isinstance(resp, AsyncResponse)

            with pytest.raises(MultiplexingError):
                resp.status_code

            await resp.content
            assert resp.status_code == 200

    async def test_concurrent_task_get(self):
        async def emit():
            responses = []

            async with AsyncSession(multiplexed=True) as s:
                responses.append(await s.get("https://httpbingo.org/get"))
                responses.append(await s.get("https://httpbingo.org/delay/5"))

                await s.gather()

            return responses

        foo = asyncio.create_task(emit())
        bar = asyncio.create_task(emit())

        responses_foo = await foo
        responses_bar = await bar

        assert len(responses_foo) == 2
        assert len(responses_bar) == 2

        assert all(r.status_code == 200 for r in responses_foo + responses_bar)

    async def test_with_stream_json(self):
        async with AsyncSession() as s:
            r = await s.get("https://httpbingo.org/get", stream=True)
            assert isinstance(r, AsyncResponse)
            assert r.ok
            payload = await r.json()
            assert payload

    async def test_with_stream_text(self):
        async with AsyncSession() as s:
            r = await s.get("https://httpbingo.org/get", stream=True)
            assert isinstance(r, AsyncResponse)
            assert r.ok
            payload = await r.text
            assert payload is not None

    async def test_with_stream_iter_decode(self):
        async with AsyncSession() as s:
            r = await s.get("https://httpbingo.org/get", stream=True)
            assert isinstance(r, AsyncResponse)
            assert r.ok
            payload = ""

            async for chunk in await r.iter_content(16, decode_unicode=True):
                payload += chunk

            assert json.loads(payload)

    async def test_with_stream_iter_raw(self):
        async with AsyncSession() as s:
            r = await s.get("https://httpbingo.org/get", stream=True)
            assert isinstance(r, AsyncResponse)
            assert r.ok
            payload = b""

            async for chunk in await r.iter_content(16):
                payload += chunk

            assert json.loads(payload.decode())

    async def test_concurrent_task_get_with_stream(self):
        async def emit():
            responses = []

            async with AsyncSession(multiplexed=True) as s:
                responses.append(await s.get("https://httpbingo.org/get", stream=True))
                responses.append(await s.get("https://httpbingo.org/delay/5", stream=True))

                await s.gather()

                for response in responses:
                    await response.content

            return responses

        foo = asyncio.create_task(emit())
        bar = asyncio.create_task(emit())

        responses_foo = await foo
        responses_bar = await bar

        assert len(responses_foo) == 2
        assert len(responses_bar) == 2

        assert all(r.status_code == 200 for r in responses_foo + responses_bar)

    @pytest.mark.skipif(os.environ.get("CI") is None, reason="Worth nothing locally")
    async def test_happy_eyeballs(self) -> None:
        """A bit of context, this test, running it locally does not get us
        any confidence about Happy Eyeballs. This test is valuable in Github CI where IPv6 addresses are unreachable.
        We're using a custom DNS resolver that will yield the IPv6 addresses and IPv4 ones.
        If this hang in CI, then you did something wrong...!"""
        async with AsyncSession(resolver="doh+cloudflare://", happy_eyeballs=True) as s:
            r = await s.get("https://httpbingo.org/get")

            assert r.ok
