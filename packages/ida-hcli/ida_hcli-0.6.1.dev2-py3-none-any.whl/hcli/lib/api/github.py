"""GitHub API client for release management and binary updates."""

from __future__ import annotations

import platform
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
from packaging.version import Version, parse

from hcli.env import ENV
from hcli.lib.api.common import APIClient, APIError, AuthenticationError, NotFoundError


class GitHubRelease:
    """Represents a GitHub release."""

    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.tag_name: str = data["tag_name"]
        self.name: str = data["name"]
        self.prerelease: bool = data["prerelease"]
        self.draft: bool = data["draft"]
        self.assets: List[Dict[str, Any]] = data["assets"]

    @property
    def version(self) -> Optional[Version]:
        """Parse version from tag name."""
        try:
            # Remove 'v' prefix if present
            version_str = self.tag_name.lstrip("v")
            return parse(version_str)
        except Exception:
            return None

    def get_binary_asset(self, binary_name: str = "hcli") -> Optional[Dict[str, Any]]:
        """Find the appropriate binary asset for current platform."""
        system = platform.system().lower()
        arch = platform.machine().lower()

        # Normalize architecture names
        if arch in ("x86_64", "amd64"):
            arch = "x86_64"
        elif arch in ("aarch64", "arm64"):
            arch = "arm64"

        # Platform-specific patterns
        patterns = []
        if system == "windows":
            patterns = [
                f"{binary_name}-windows-{arch}.exe",
                f"{binary_name}-win-{arch}.exe",
                f"{binary_name}.exe",
            ]
        elif system == "darwin":
            patterns = [
                f"{binary_name}-macos-{arch}",
                f"{binary_name}-darwin-{arch}",
                f"{binary_name}-mac-{arch}",
                f"{binary_name}",
            ]
        elif system == "linux":
            patterns = [
                f"{binary_name}-linux-{arch}",
                f"{binary_name}-{arch}",
                f"{binary_name}",
            ]

        # Find matching asset
        for asset in self.assets:
            asset_name = asset["name"].lower()
            for pattern in patterns:
                if pattern.lower() in asset_name:
                    return asset

        return None


class GitHubAPI:
    """GitHub API client with authentication support."""

    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub API client.

        Args:
            token: GitHub personal access token or fine-grained token
        """
        self.token = token or ENV.GITHUB_TOKEN
        self.base_url = "https://api.github.com"

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(60.0),
            headers=self._get_headers(),
        )

    def _get_headers(self) -> Dict[str, str]:
        """Get headers with GitHub authentication."""
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "ida-hcli",
        }

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        return headers

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def _handle_response(self, response: httpx.Response) -> httpx.Response:
        """Handle GitHub API response with proper error context."""
        if response.status_code == 401:
            if self.token:
                error_msg = "GitHub authentication failed. Check your token permissions."
            else:
                error_msg = "GitHub authentication required. Set GITHUB_TOKEN or GH_TOKEN environment variable."
            raise AuthenticationError(error_msg, response.status_code, response)
        elif response.status_code == 403:
            rate_limit_remaining = response.headers.get("X-RateLimit-Remaining", "0")
            if rate_limit_remaining == "0":
                reset_time = response.headers.get("X-RateLimit-Reset", "unknown")
                raise APIError(f"GitHub rate limit exceeded. Resets at {reset_time}", response.status_code, response)
            raise AuthenticationError("Access forbidden. Check repository permissions.", response.status_code, response)
        elif response.status_code == 404:
            if self.token:
                error_msg = "Repository or release not found. Check repository name and token permissions."
            else:
                error_msg = "Repository not found. If this is a private repository, set GITHUB_TOKEN or GH_TOKEN environment variable."
            raise NotFoundError(error_msg, response.status_code, response)
        elif response.status_code >= 400:
            error_msg = f"GitHub API request failed: {response.status_code}"
            try:
                error_data = response.json()
                if "message" in error_data:
                    error_msg = error_data["message"]
            except:
                pass
            raise APIError(error_msg, response.status_code, response)

        return response

    async def get_latest_release(
        self, owner: str, repo: str, include_prereleases: bool = False
    ) -> Optional[GitHubRelease]:
        """Get the latest release from a GitHub repository.

        Args:
            owner: Repository owner (user or organization)
            repo: Repository name
            include_prereleases: Include pre-releases in search

        Returns:
            GitHubRelease object or None if not found
        """
        if include_prereleases:
            # Get all releases and find the latest
            releases = await self.get_releases(owner, repo, limit=10)
            if not releases:
                return None
            return releases[0]
        else:
            # Use GitHub's latest release endpoint
            url = f"/repos/{owner}/{repo}/releases/latest"
            try:
                response = await self.client.get(url)
                await self._handle_response(response)
                return GitHubRelease(response.json())
            except NotFoundError:
                return None

    async def get_releases(self, owner: str, repo: str, limit: int = 10) -> List[GitHubRelease]:
        """Get releases from a GitHub repository.

        Args:
            owner: Repository owner
            repo: Repository name
            limit: Maximum number of releases to fetch

        Returns:
            List of GitHubRelease objects
        """
        url = f"/repos/{owner}/{repo}/releases"
        params = {"per_page": min(limit, 100)}

        response = await self.client.get(url, params=params)
        await self._handle_response(response)

        releases_data = response.json()
        return [GitHubRelease(data) for data in releases_data if not data["draft"]]

    async def get_release_by_tag(self, owner: str, repo: str, tag: str) -> Optional[GitHubRelease]:
        """Get a specific release by tag name.

        Args:
            owner: Repository owner
            repo: Repository name
            tag: Release tag name

        Returns:
            GitHubRelease object or None if not found
        """
        url = f"/repos/{owner}/{repo}/releases/tags/{tag}"
        try:
            response = await self.client.get(url)
            await self._handle_response(response)
            return GitHubRelease(response.json())
        except NotFoundError:
            return None

    async def download_asset(self, asset: Dict[str, Any], target_path: Path, show_progress: bool = True) -> str:
        """Download a release asset.

        Args:
            asset: Asset dictionary from GitHub API
            target_path: Path where to save the file
            show_progress: Whether to show download progress

        Returns:
            Path to downloaded file
        """
        download_url = asset["browser_download_url"]

        # Use the existing download functionality from APIClient
        api_client = APIClient()
        try:
            return await api_client.download_file(
                url=download_url,
                target_dir=target_path.parent,
                target_filename=target_path.name,
                auth=bool(self.token),  # Use auth if token is available
            )
        finally:
            await api_client.client.aclose()

    def requires_authentication(self, owner: str, repo: str) -> bool:
        """Check if repository requires authentication (heuristic).

        This is a heuristic check - the definitive way is to try accessing the repo.
        """
        return bool(self.token)  # If token is provided, assume private repo access needed
