"""
Tests for the hooks functionality.
"""

import torch
from tensordict import TensorDict
import pytest

from tdhook.hooks import (
    register_hook_to_module,
    MultiHookManager,
    MultiHookHandle,
    HookFactory,
    EarlyStoppingException,
)


class TestHookRegistration:
    """Test hook registration functionality."""

    def test_register_forward_hook(self, default_test_model):
        """Test registering a forward hook."""

        def forward_hook(module, args, output):
            return output + 1

        input = torch.randn(2, 10)
        original_output = default_test_model(input)
        handle = register_hook_to_module(default_test_model.linear1, forward_hook, direction="fwd")
        assert handle is not None
        model_output = default_test_model(input)
        assert not torch.allclose(model_output, original_output)
        handle.remove()
        output = default_test_model(input)
        assert torch.allclose(output, original_output)

    def test_multi_hook_manager(self, default_test_model):
        """Test MultiHookManager."""

        def hook_factory(name: str):
            def hook(module, args, output):
                return output + 1

            return hook

        input = torch.randn(2, 10)
        original_output = default_test_model(input)

        manager = MultiHookManager(pattern=r"linear\d+")
        handle = manager.register_hook(default_test_model, hook_factory, direction="fwd")
        assert isinstance(handle, MultiHookHandle)
        mod_output = default_test_model(input)
        assert not torch.allclose(mod_output, original_output)
        handle.remove()
        output = default_test_model(input)
        assert torch.allclose(output, original_output)


class TestHookFactory:
    """Test hook factory functionality."""

    def test_make_caching_hook(self, default_test_model):
        """Test making a caching hook."""
        cache = TensorDict()
        hook = HookFactory.make_caching_hook("key", cache)
        assert hook is not None
        hook(default_test_model, None, 1)
        assert cache["key"] == 1

    def test_make_setting_hook(self, default_test_model):
        """Test making a setting hook."""

        def callback(value, module, args, output):
            return value + 1

        hook = HookFactory.make_setting_hook(1, callback=callback)
        assert hook is not None
        output = hook(default_test_model, None, 1)
        assert output == 2

    def test_make_stopping_hook(self, default_test_model):
        """Test making a stopping hook."""

        hook = HookFactory.make_stopping_hook("key")
        assert hook is not None
        with pytest.raises(EarlyStoppingException):
            hook(default_test_model, None, 1)


class TestMultiHookHandle:
    """Tests specific to MultiHookHandle behaviors."""

    def test_add_handles_and_remove_all(self, default_test_model):
        import torch

        input = torch.randn(2, 10)
        original_output = default_test_model(input)

        def hook_factory(_name: str):
            def hook(module, args, output):
                return output + 1

            return hook

        manager1 = MultiHookManager(pattern=r"linear1$")
        handle1 = manager1.register_hook(default_test_model, hook_factory, direction="fwd")

        manager2 = MultiHookManager(pattern=r"linear2$|linear3$")
        handle2 = manager2.register_hook(default_test_model, hook_factory, direction="fwd")

        combined = handle1 + handle2
        assert isinstance(combined, MultiHookHandle)

        # Hooks active -> output should differ
        changed_output = default_test_model(input)
        assert not torch.allclose(changed_output, original_output)

        # Removing combined should remove all underlying hooks
        combined.remove()
        restored_output = default_test_model(input)
        assert torch.allclose(restored_output, original_output)

        # Type safety on addition
        import pytest

        with pytest.raises(TypeError):
            _ = combined + 123  # not a MultiHookHandle

    def test_context_manager_removes_on_exit(self, default_test_model):
        import torch

        input = torch.randn(2, 10)
        original_output = default_test_model(input)

        def hook_factory(_name: str):
            def hook(module, args, output):
                return output + 1

            return hook

        manager = MultiHookManager(pattern=r"linear1$")
        handle = manager.register_hook(default_test_model, hook_factory, direction="fwd")

        with handle:
            changed_output = default_test_model(input)
            assert not torch.allclose(changed_output, original_output)

        # After exiting context, hooks should be removed
        restored_output = default_test_model(input)
        assert torch.allclose(restored_output, original_output)

    def test_empty_handle_remove_noop(self):
        # Should not raise
        handle = MultiHookHandle()
        handle.remove()


class TestMultiHookManagerPattern:
    def test_pattern_setter_changes_selection(self, default_test_model):
        import torch

        input = torch.randn(2, 10)
        original_output = default_test_model(input)

        def hook_factory(_name: str):
            def hook(module, args, output):
                return output + 1

            return hook

        manager = MultiHookManager(pattern=r"linear1$")
        assert manager.pattern == r"linear1$"

        handle1 = manager.register_hook(default_test_model, hook_factory, direction="fwd")
        out1 = default_test_model(input)
        assert not torch.allclose(out1, original_output)
        handle1.remove()
        out1_restored = default_test_model(input)
        assert torch.allclose(out1_restored, original_output)

        manager.pattern = r"linear2$"
        assert manager.pattern == r"linear2$"

        handle2 = manager.register_hook(default_test_model, hook_factory, direction="fwd")
        out2 = default_test_model(input)
        assert not torch.allclose(out2, original_output)
        handle2.remove()
        out2_restored = default_test_model(input)
        assert torch.allclose(out2_restored, original_output)


class TestHookRegistrationKwargsAndBackward:
    """Covers hooks registration with kwargs and backward directions."""

    def test_register_forward_hook_with_kwargs(self, default_test_model):
        """Forward hook with with_kwargs=True can modify output."""
        import torch

        def forward_hook(module, args, kwargs, output):
            return output + 1

        x = torch.randn(2, 10)
        original = default_test_model(x)
        handle = register_hook_to_module(default_test_model.linear1, forward_hook, direction="fwd_kwargs")
        out = default_test_model(x)
        assert not torch.allclose(out, original)
        handle.remove()
        out2 = default_test_model(x)
        assert torch.allclose(out2, original)

    def test_register_forward_pre_hook_with_kwargs(self, default_test_model):
        """Forward pre hook with kwargs can modify inputs."""
        import torch

        def pre_hook(module, args, kwargs):
            return (args[0] + 1,), kwargs

        x = torch.randn(2, 10)
        original = default_test_model(x)
        handle = register_hook_to_module(default_test_model.linear1, pre_hook, direction="fwd_pre_kwargs")
        out = default_test_model(x)
        assert not torch.allclose(out, original)
        handle.remove()
        out2 = default_test_model(x)
        assert torch.allclose(out2, original)

    def test_register_backward_and_backward_pre_hooks(self, default_test_model):
        """Backward and backward pre hooks are invoked during autograd."""
        import torch

        calls = []

        def bwd_hook(module, grad_input, grad_output):
            calls.append("bwd")
            return grad_input

        def bwd_pre_hook(module, grad_output):
            calls.append("bwd_pre")
            return grad_output

        handle_bwd = register_hook_to_module(default_test_model.linear2, bwd_hook, direction="bwd")
        handle_bwd_pre = register_hook_to_module(default_test_model.linear2, bwd_pre_hook, direction="bwd_pre")

        x = torch.randn(4, 10, requires_grad=True)
        y = default_test_model(x).sum()
        y.backward()

        assert "bwd" in calls and "bwd_pre" in calls
        handle_bwd.remove()
        handle_bwd_pre.remove()


class TestHookSignatureValidation:
    """Input validation for hook signatures and callbacks."""

    def test_invalid_hook_signature_raises(self, default_test_model):
        """Incorrect forward hook signature should raise at registration."""

        def bad_hook(module, output):
            return output

        import pytest

        with pytest.raises(ValueError):
            register_hook_to_module(default_test_model.linear1, bad_hook, direction="fwd")

    def test_callback_missing_params_raises(self):
        """Callback missing required named params is rejected."""
        from tensordict import TensorDict

        def bad_cb(module):
            return 0

        cache = TensorDict()
        import pytest

        with pytest.raises(ValueError):
            HookFactory.make_caching_hook("k", cache, callback=bad_cb, direction="fwd")

    def test_caching_hook_fwd_pre_kwargs_value_index(self):
        """Caching hook for fwd_pre_kwargs can use callback to store a non-tuple value."""
        from tensordict import TensorDict

        cache = TensorDict()
        hook = HookFactory.make_caching_hook(
            "k",
            cache,
            direction="fwd_pre_kwargs",
            callback=lambda module, args, kwargs, key: args[0],
        )
        module = object()
        args = ("A",)
        kwargs = {"unused": 1}
        hook(module, args, kwargs)
        assert cache["k"] == "A"


class TestHookEdgeCases:
    """Targeted edge cases for hooks internals."""

    def test_register_invalid_direction_raises(self, default_test_model):
        """Registering with an invalid direction fails early."""
        import pytest

        def some_hook(module, args, output):
            return output

        with pytest.raises(ValueError):
            register_hook_to_module(default_test_model.linear1, some_hook, direction="nope")

    def test_varargs_too_many_positional_params_raises(self, default_test_model):
        """Varargs hooks with too many fixed params are rejected."""
        import pytest

        def bad_varargs_hook(module, a, b, c, d, *args):
            return None

        with pytest.raises(ValueError):
            register_hook_to_module(default_test_model.linear1, bad_varargs_hook, direction="fwd")

    def test_multihookmanager_default_pattern_matches_nothing(self, default_test_model):
        """Default manager pattern matches no modules."""
        import torch

        def hook_factory(name: str):
            def hook(module, args, output):
                return output + 1

            return hook

        x = torch.randn(2, 10)
        original = default_test_model(x)
        manager = MultiHookManager()
        handle = manager.register_hook(default_test_model, hook_factory, direction="fwd")
        out = default_test_model(x)
        assert torch.allclose(out, original)
        handle.remove()

    def test_cacheproxy_dead_reference_raises(self):
        """Resolving a CacheProxy with a dead cache reference raises."""
        import gc
        from tensordict import TensorDict
        from tdhook.hooks import CacheProxy

        def make_proxy():
            cache = TensorDict()
            return CacheProxy("k", cache)

        proxy = make_proxy()
        gc.collect()
        import pytest

        with pytest.raises(ValueError):
            proxy.resolve()

    def test_callback_positional_only_params_rejected(self):
        """Callbacks with positional-only parameters are not allowed."""
        import pytest

        def cb(module, /, args=None, output=None, value=None):
            return value

        with pytest.raises(ValueError):
            HookFactory.make_setting_hook(1, callback=cb, direction="fwd")

    def test_make_caching_hook_invalid_direction_raises(self):
        """Invalid direction for caching hook raises."""
        from tensordict import TensorDict
        import pytest

        with pytest.raises(ValueError):
            HookFactory.make_caching_hook("k", TensorDict(), direction="nope")

    def test_make_setting_hook_cacheproxy_resolve_branch(self):
        """Setting hook resolves CacheProxy and can return a proxy via callback."""
        from tensordict import TensorDict
        from tdhook.hooks import CacheProxy

        cache = TensorDict({"k": 123})
        proxy = CacheProxy("k", cache)

        def cb(module, args, output, value):
            return CacheProxy("k", cache)

        hook = HookFactory.make_setting_hook(proxy, callback=cb, direction="fwd")
        result = hook(object(), None, None)
        assert isinstance(result, CacheProxy)

    def test_make_setting_hook_type_mismatch_raises(self):
        """Setting hook raises when callback changes the value type."""
        import pytest

        def cb(module, args, output, value):
            return 1.0

        hook = HookFactory.make_setting_hook(1, callback=cb, direction="fwd")
        with pytest.raises(RuntimeError):
            hook(object(), None, None)
