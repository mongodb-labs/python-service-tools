from unittest.mock import patch

import miscutils.testing as under_test


class TestPatcher:
    # Its tempting to use the utility to test itself...
    @patch("miscutils.testing.patch")
    def test_creates_relative_patches(self, mock_patch):
        mock_patch.return_value = "patch_context"
        relative_patch = under_test.relative_patch_maker("some_namespace")
        patch_context = relative_patch("some_relative_thing_to_replace")
        mock_patch.assert_called_once()
        mock_patch.assert_called_with("some_namespace.some_relative_thing_to_replace")
        assert patch_context == "patch_context"
