from __future__ import annotations

import sys
from dataclasses import dataclass, field
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType, SimpleNamespace
from uuid import uuid4

import pytest

PACKAGE_DIR = Path(__file__).resolve().parents[1]
SPEC = spec_from_file_location(
    "hermes_token_router_plugin",
    PACKAGE_DIR / "__init__.py",
    submodule_search_locations=[str(PACKAGE_DIR)],
)
assert SPEC is not None and SPEC.loader is not None
router = module_from_spec(SPEC)
sys.modules.setdefault("hermes_token_router_plugin", router)
SPEC.loader.exec_module(router)


TEST_PROFILE_CONFIG = {
    "enabled": True,
    "long_message_decline_chars": 10_000,
    "short_message_bypass_chars": 0,
    "floor_toolsets": [],
    "deterministic_rules_enabled": True,
    "confidence_threshold": 0.0,
    "router_hard_timeout_ms": 1_200,
    "classifier": {"enabled": False},
}

# These tests exercise only the observed sticky-surface behavior.
# routing_scope, expansion_mode, and shrink_mid_session stay intentionally unused.


@dataclass
class FakeRegistry:
    toolsets: dict[str, list[str]] = field(
        default_factory=lambda: {
            "web": ["web_search"],
            "file": ["read_file"],
            "router_recovery": ["request_toolset"],
        }
    )

    def __post_init__(self) -> None:
        self.definitions = {
            name: {"type": "function", "function": {"name": name}}
            for names in self.toolsets.values()
            for name in names
        }
        self.entries = {
            name: SimpleNamespace(toolset=toolset)
            for toolset, names in self.toolsets.items()
            for name in names
        }

    def get_registered_toolset_names(self):
        return list(self.toolsets)

    def get_tool_names_for_toolset(self, toolset):
        return list(self.toolsets.get(toolset, []))

    def get_definitions(self, tool_names, quiet=True):
        return [self.definitions[name] for name in sorted(tool_names) if name in self.definitions]

    def get_entry(self, tool_name):
        return self.entries.get(tool_name)

    def get_toolset_alias_target(self, name):
        return name

    def register(self, **kwargs):
        return kwargs


@dataclass
class FakeAgent:
    session_id: str
    _current_turn_id: str
    tools: list[dict]
    valid_tool_names: set[str]
    enabled_toolsets: list[str]


def _new_agent(registry: FakeRegistry, *, session_id: str | None = None) -> FakeAgent:
    return FakeAgent(
        session_id=session_id or f"session-{uuid4().hex}",
        _current_turn_id="",
        tools=registry.get_definitions({"web_search", "read_file", "request_toolset"}),
        valid_tool_names={"web_search", "read_file", "request_toolset"},
        enabled_toolsets=["web", "file", "router_recovery"],
    )


@pytest.fixture()
def router_harness(monkeypatch):
    original_sys_path = sys.path[:]
    sys.path[:] = [
        entry
        for entry in sys.path
        if Path(entry or ".").resolve() != PACKAGE_DIR
    ]
    from contextlib import contextmanager
    from contextvars import ContextVar

    active_parent = ContextVar(f"active_subagent_parent_{uuid4().hex}", default=None)

    @contextmanager
    def bind_subagent_parent(agent):
        token = active_parent.set(agent)
        try:
            yield
        finally:
            active_parent.reset(token)

    lifecycle_module = ModuleType("agent.subagent_lifecycle")
    lifecycle_module.bind_subagent_parent = bind_subagent_parent
    lifecycle_module.get_active_subagent_parent = active_parent.get
    agent_module = ModuleType("agent")
    agent_module.__path__ = []
    agent_module.subagent_lifecycle = lifecycle_module
    monkeypatch.setitem(sys.modules, "agent", agent_module)
    monkeypatch.setitem(sys.modules, "agent.subagent_lifecycle", lifecycle_module)
    sys.path[:] = original_sys_path

    registry = FakeRegistry()
    tools_pkg = ModuleType("tools")
    tools_pkg.__path__ = []
    registry_mod = ModuleType("tools.registry")
    registry_mod.registry = registry  # type: ignore[attr-defined]
    tools_pkg.registry = registry_mod  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "tools", tools_pkg)
    monkeypatch.setitem(sys.modules, "tools.registry", registry_mod)

    monkeypatch.setattr(router, "_is_router_active", lambda *args, **kwargs: True)
    monkeypatch.setattr(router, "_load_config", lambda: {"global": TEST_PROFILE_CONFIG})
    monkeypatch.setattr(
        router,
        "_get_profile_config",
        lambda cfg, profile_name=None: dict(TEST_PROFILE_CONFIG, _profile_name="router-test"),
    )
    tools_module = sys.modules[router._apply_predicted_tools.__module__]
    monkeypatch.setattr(tools_module, "_load_config", lambda: {"global": TEST_PROFILE_CONFIG})
    monkeypatch.setattr(
        tools_module,
        "_get_profile_config",
        lambda cfg, profile_name=None: dict(TEST_PROFILE_CONFIG, _profile_name="router-test"),
    )

    call_log: list[tuple[str, frozenset[str]]] = []
    real_predict = router._predict_toolsets_by_rules

    def predict_spy(user_message, available_toolsets):
        call_log.append((user_message, frozenset(available_toolsets)))
        return real_predict(user_message, available_toolsets)

    monkeypatch.setattr(router, "_predict_toolsets_by_rules", predict_spy)

    agent = _new_agent(registry)

    yield SimpleNamespace(
        agent=agent,
        registry=registry,
        calls=call_log,
        bind_subagent_parent=bind_subagent_parent,
        get_active_subagent_parent=active_parent.get,
    )

    router.on_session_end(session_id=agent.session_id)


def _tool_names(agent: FakeAgent) -> set[str]:
    return {
        tool.get("function", {}).get("name", "")
        for tool in agent.tools
        if tool.get("function", {}).get("name")
    }


def _call_late(agent: FakeAgent, message: str, turn_id: str):
    agent._current_turn_id = turn_id
    return router.pre_llm_call(session_id=agent.session_id, turn_id=turn_id, user_message=message)


def _call_early(agent: FakeAgent, message: str, turn_id: str):
    agent._current_turn_id = turn_id
    return router.pre_turn_context_build(
        agent=agent,
        session_id=agent.session_id,
        turn_id=turn_id,
        user_message=message,
    )


def test_late_hook_classifies_once_across_web_then_file_turns(router_harness):
    agent = router_harness.agent

    _call_late(agent, "search the web for the current docs", "turn-1")
    first_tools = _tool_names(agent)

    _call_late(agent, "read this file for the answer", "turn-2")

    assert len(router_harness.calls) == 1
    assert _tool_names(agent) == first_tools
    assert "web_search" in first_tools
    assert "read_file" not in first_tools


def test_recovery_keeps_web_and_file_available_after_late_reentry(router_harness):
    agent = router_harness.agent

    _call_late(agent, "search the web for the current docs", "turn-1")
    _call_late(agent, "read this file for the answer", "turn-2")

    response = router.tool_request_middleware(
        session_id=agent.session_id,
        tool_name="read_file",
        args={},
    )
    assert response == {"args": {}, "router_recovered": "file"}

    assert len(router_harness.calls) == 1
    assert {"web_search", "read_file"} <= _tool_names(agent)
    assert {"web", "file"} <= set(agent.enabled_toolsets)
    assert {"web", "file"} <= router._get_router_state(agent).active_toolsets


def test_early_then_late_hook_same_turn_does_not_reroute(router_harness):
    agent = router_harness.agent

    _call_early(agent, "search the web for the current docs", "turn-3")
    early_tools = _tool_names(agent)

    _call_late(agent, "read this file for the answer", "turn-3")

    assert len(router_harness.calls) == 1
    assert _tool_names(agent) == early_tools
    assert "web_search" in early_tools
    assert "read_file" not in early_tools


def test_unused_routing_options_are_not_part_of_the_test_fixture(router_harness):
    assert {"routing_scope", "expansion_mode", "shrink_mid_session"}.isdisjoint(TEST_PROFILE_CONFIG)
    assert {"routing_scope", "expansion_mode", "shrink_mid_session"}.isdisjoint(
        router._get_profile_config({}, profile_name="router-test")
    )


def test_late_hook_uses_context_bound_agent_in_copied_worker(router_harness):
    from concurrent.futures import ThreadPoolExecutor
    from contextvars import copy_context

    agent = router_harness.agent
    session_id = agent.session_id
    turn_id = "worker-turn-1"
    assert router._get_agent_ref(session_id) is None

    def invoke_late_hook(
        session_id=session_id,
        turn_id=turn_id,
    ):
        return router.pre_llm_call(
            session_id=session_id,
            turn_id=turn_id,
            user_message="search the web for the current docs",
        )

    with router_harness.bind_subagent_parent(agent):
        copied_context = copy_context()
        with ThreadPoolExecutor(max_workers=1) as executor:
            result = executor.submit(copied_context.run, invoke_late_hook).result()

    assert result is None
    assert _tool_names(agent) == {"web_search", "request_toolset"}
    assert len(router_harness.calls) == 1
    assert router._get_agent_ref(session_id) is agent


def test_copied_context_lifecycle_isolated_by_session(router_harness):
    from concurrent.futures import ThreadPoolExecutor
    from contextvars import copy_context

    first = router_harness.agent
    second = _new_agent(router_harness.registry)

    def invoke_late_hook(session_id: str, turn_id: str):
        return router.pre_llm_call(
            session_id=session_id,
            turn_id=turn_id,
            user_message="search the web for the current docs",
        )

    try:
        with router_harness.bind_subagent_parent(first):
            first_context = copy_context()
        with router_harness.bind_subagent_parent(second):
            second_context = copy_context()

        assert first_context.run(router_harness.get_active_subagent_parent) is first
        assert second_context.run(router_harness.get_active_subagent_parent) is second

        with ThreadPoolExecutor(max_workers=1) as executor:
            wrong_session = executor.submit(
                first_context.run,
                invoke_late_hook,
                second.session_id,
                "cross-session",
            ).result()
            second_result = executor.submit(
                second_context.run,
                invoke_late_hook,
                second.session_id,
                "second-turn",
            ).result()
            first_result = executor.submit(
                first_context.run,
                invoke_late_hook,
                first.session_id,
                "first-turn",
            ).result()

        assert wrong_session is None
        assert second_result is None
        assert first_result is None
        assert _tool_names(first) == {"web_search", "request_toolset"}
        assert _tool_names(second) == {"web_search", "request_toolset"}
        assert router._get_agent_ref(first.session_id) is first
        assert router._get_agent_ref(second.session_id) is second
        assert len(router_harness.calls) == 2
    finally:
        router.on_session_end(session_id=first.session_id)
        router.on_session_end(session_id=second.session_id)
