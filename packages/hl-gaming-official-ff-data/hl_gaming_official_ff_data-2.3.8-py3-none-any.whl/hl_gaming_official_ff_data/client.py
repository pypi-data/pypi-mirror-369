# hlff_client.py
import time
import json
import math
import random
from typing import Optional, Dict, Any

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException, HTTPError, Timeout
try:
    # urllib3 Retry for robust retries
    from urllib3.util.retry import Retry
except Exception:
    Retry = None

# Optional cache support using cachetools (install if you want caching)
try:
    from cachetools import TTLCache
except Exception:
    TTLCache = None


class HLFFClientError(Exception):
    """Base client error."""
    def __init__(self, message: str, code: str = "HLFF_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.code = code
        self.details = details or {}

    def to_dict(self):
        return {"message": str(self), "code": self.code, "details": self.details}


class APIError(HLFFClientError):
    pass


class AuthError(HLFFClientError):
    pass


class RateLimitError(HLFFClientError):
    pass


class NetworkError(HLFFClientError):
    pass


class InvalidResponseError(HLFFClientError):
    pass


class HLFFClient:
    """
    HL Gaming Official Free Fire API client (synchronous).

    Example:
        client = HLFFClient(api_key="YOUR_KEY", region="pk")
        data = client.get_all_data(player_uid="9351564274", user_uid="YOUR_USER_UID")
    """

    DEFAULT_BASE_URL = "https://developers2-hlgamingofficial.vercel.app/main/games/freefire/account/api"

    def __init__(
        self,
        api_key: str,
        region: str = "pk",
        *,
        base_url: Optional[str] = None,
        timeout: float = 10.0,
        retries: int = 3,
        backoff_factor: float = 0.3,
        jitter: bool = True,
        cache_ttl: int = 0,
        cache_max: int = 1024,
        ai_config: Optional[Dict[str, Any]] = None,
        session: Optional[requests.Session] = None,
        debug: bool = False
    ):
        if not api_key:
            raise ValueError("API key is required.")

        self.api_key = api_key
        self.region = region
        self.base_url = base_url or self.DEFAULT_BASE_URL
        self.timeout = float(timeout)
        self.retries = max(0, int(retries))
        self.backoff_factor = float(backoff_factor)
        self.jitter = bool(jitter)
        self.debug = bool(debug)

        # AI enrichment configuration (optional). Example:
        # {"enabled": True, "provider": "openai", "api_key": "...", "model": "gpt-4o-mini", "timeout": 5}
        self.ai_config = ai_config or {"enabled": False}

        # requests session with retry adapter
        self.session = session or requests.Session()
        self._configure_retries()

        # optional TTL cache if cachetools is available; otherwise caching disabled
        if cache_ttl and TTLCache:
            self.cache = TTLCache(maxsize=int(cache_max), ttl=int(cache_ttl))
        else:
            self.cache = None

    def _log_debug(self, *args):
        if self.debug:
            try:
                print("[hlff_client DEBUG]", *args)
            except Exception:
                pass

    def _configure_retries(self):
        # If urllib3 Retry is available, configure HTTPAdapter with retries
        if Retry is not None and self.retries > 0:
            # prefer allowed_methods for modern urllib3, fallback to method_whitelist
            retry_kwargs = dict(
                total=self.retries,
                backoff_factor=self.backoff_factor,
                status_forcelist=(429, 500, 502, 503, 504)
            )
            try:
                retry_kwargs["allowed_methods"] = frozenset(["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"])
            except Exception:
                # older urllib3 uses method_whitelist
                retry_kwargs["method_whitelist"] = frozenset(["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"])

            retry = Retry(**retry_kwargs)
            adapter = HTTPAdapter(max_retries=retry)
            self.session.mount("https://", adapter)
            self.session.mount("http://", adapter)
        else:
            # no retry adapter; we'll handle simple retries in wrapper
            pass

    def _cache_key(self, section_name: str, player_uid: str, user_uid: str, region: str):
        key_struct = {"section": section_name, "player": player_uid, "user": user_uid, "region": region}
        return json.dumps(key_struct, sort_keys=True)

    def _sleep_backoff(self, attempt: int):
        base = self.backoff_factor * (2 ** (attempt - 1))
        if self.jitter:
            # add jitter up to 0.1 * base
            jitter_val = random.random() * (0.1 * base)
        else:
            jitter_val = 0.0
        to_sleep = base + jitter_val
        # minimum floor
        to_sleep = max(0.0, to_sleep)
        self._log_debug(f"Sleeping for {to_sleep:.3f}s (attempt {attempt})")
        time.sleep(to_sleep)

    def _analyze_error_local(self, err: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Deterministic, local analysis of an exception. Returns a structured dict with:
        {summary, severity, probable_causes, suggestions, next_steps, debug}
        """
        ctx = context or {}
        out = {
            "summary": "Unknown error",
            "severity": "medium",
            "probable_causes": [],
            "suggestions": [],
            "next_steps": [],
            "debug": {"context": ctx}
        }

        # HTTP error with response
        if isinstance(err, HTTPError) and getattr(err, "response", None) is not None:
            resp = err.response
            status = getattr(resp, "status_code", None)
            out["debug"]["status_code"] = status
            try:
                out["debug"]["body"] = resp.json()
            except Exception:
                out["debug"]["body"] = getattr(resp, "text", None)

            if status in (401, 403):
                out["summary"] = "Authentication or authorization failure."
                out["severity"] = "high"
                out["probable_causes"].extend(["Invalid or missing API key", "Insufficient permissions", "API key restrictions"])
                out["suggestions"].extend(["Verify the API key provided to the client", "Confirm developer user UID and region are correct"])
                out["next_steps"].append("Test with a minimal curl request using the same credentials and check the API dashboard")
                return out

            if status == 404:
                out["summary"] = "Resource not found."
                out["severity"] = "low"
                out["probable_causes"].extend(["Player UID incorrect", "Wrong sectionName", "Region mismatch"])
                out["suggestions"].append("Try AllData section to confirm the account exists")
                return out

            if status == 429:
                out["summary"] = "Rate limit exceeded."
                out["severity"] = "high"
                out["probable_causes"].append("Too many requests in a short time window")
                out["suggestions"].extend(["Respect Retry-After header if present", "Use caching and exponential backoff"])
                return out

            if status and status >= 500:
                out["summary"] = "Server-side error."
                out["severity"] = "medium"
                out["probable_causes"].append("Temporary server outage or internal server error")
                out["suggestions"].append("Retry later with exponential backoff; log full request/response and contact support if persistent")
                return out

            out["summary"] = f"API returned HTTP {status}."
            out["severity"] = "high" if status and status >= 400 else "medium"
            out["suggestions"].append("Inspect response body for details and validate the request parameters")
            return out

        # Timeout
        if isinstance(err, Timeout) or (isinstance(err, RequestException) and "timed out" in str(err).lower()):
            out["summary"] = "Request timed out."
            out["severity"] = "medium"
            out["probable_causes"].extend(["Slow network", "Timeout configured too low"])
            out["suggestions"].append("Increase client timeout or try again on a stable network")
            out["next_steps"].append("Run a network check (ping/traceroute) to the API host")
            return out

        # Network no response
        if isinstance(err, RequestException) and not isinstance(err, HTTPError):
            out["summary"] = "No response from remote server."
            out["severity"] = "high"
            out["probable_causes"].extend(["Network unreachable", "Connection blocked by firewall or proxy"])
            out["suggestions"].append("Verify connectivity and proxy settings; try request from another network")
            return out

        # JSON parsing or invalid content
        if isinstance(err, ValueError) and "JSON" in str(err) or "decode" in str(err).lower():
            out["summary"] = "Failed to parse API response."
            out["severity"] = "medium"
            out["probable_causes"].extend(["API returned invalid JSON", "Unexpected HTML error page returned"])
            out["suggestions"].append("Log raw response body and check for HTML error pages")
            return out

        out["summary"] = str(err)
        out["severity"] = "medium"
        out["suggestions"].append("Enable debug mode and capture full exception details")
        return out

    def _enrich_with_ai(self, local_analysis: Dict[str, Any], err: Exception, context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Optional AI enrichment. Disabled by default. If ai_config is provided and enabled,
        this method attempts to call an OpenAI-compatible endpoint to get structured guidance.

        ai_config expected keys:
            enabled: bool
            provider: "openai" (currently only direct OpenAI REST compatible endpoint supported)
            api_key: str
            model: str (optional)
            timeout: float (optional)
        """
        cfg = self.ai_config or {}
        if not cfg.get("enabled"):
            return None

        provider = cfg.get("provider", "openai")
        api_key = cfg.get("api_key")
        model = cfg.get("model", "gpt-4o-mini")
        ai_timeout = float(cfg.get("timeout", 5.0))

        if provider != "openai" or not api_key:
            return {"ai_error": "AI provider not configured or unsupported."}

        # Compose a small structured prompt and call OpenAI chat completions endpoint
        try:
            prompt = (
                "You are an assistant that returns a JSON object with keys: summary, causes, remediation, verification, follow_up.\n"
                "Context:\n"
                + json.dumps({"local_analysis": local_analysis, "error": str(err), "context": context}, default=str)
            )
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "Produce only a JSON object as described."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 600,
                "temperature": 0.2
            }
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            resp = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=ai_timeout)
            resp.raise_for_status()
            text = resp.json()["choices"][0]["message"]["content"]
            # Try parsing result as JSON
            try:
                return json.loads(text)
            except Exception:
                return {"ai_raw": text}
        except Exception as e:
            return {"ai_error": str(e)}

    def _perform_request(self, params: Dict[str, Any], attempt_wrapper_retries: int = 0, signal_abort: Optional[Dict[str, Any]] = None) -> requests.Response:
        """
        Execute the HTTP GET request. If a session retry adapter is not available,
        this wrapper will perform simple retry/backoff.
        """
        # If cache is present and match found, calling function handles caching
        # If Retry was configured on session, a single request may be enough.
        last_exc = None
        # If urllib3 Retry is configured, session adapter will handle retrying.
        # We still provide a fallback simple retry loop when Retry is not present.
        if Retry is not None and self.retries > 0:
            resp = self.session.get(self.base_url, params=params, timeout=self.timeout)
            resp.raise_for_status()
            return resp

        max_tries = max(1, self.retries + 1)
        for attempt in range(1, max_tries + 1):
            try:
                self._log_debug("Request attempt", attempt, "params", params)
                resp = self.session.get(self.base_url, params=params, timeout=self.timeout)
                resp.raise_for_status()
                return resp
            except Exception as e:
                last_exc = e
                # If last attempt, break and propagate analysis
                if attempt >= max_tries:
                    break
                # Determine if retryable simple rules
                retryable = True
                if isinstance(e, HTTPError) and getattr(e, "response", None) is not None:
                    status = getattr(e.response, "status_code", None)
                    # Do not retry client errors except 429
                    if status and 400 <= status < 500 and status != 429:
                        retryable = False
                if not retryable:
                    break
                self._sleep_backoff(attempt)
                continue
        # If here, raise last exception
        raise last_exc

    def _call_section(self, section_name: str, player_uid: str, user_uid: str, *, region: Optional[str] = None, cache: bool = True, signal_abort: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not player_uid:
            raise ValueError("Player UID is required.")
        if not user_uid:
            raise ValueError("User UID is required.")

        use_region = region or self.region
        params = {
            "sectionName": section_name,
            "PlayerUid": player_uid,
            "region": use_region,
            "useruid": user_uid,
            "api": self.api_key
        }

        cache_key = None
        if self.cache and cache:
            cache_key = self._cache_key(section_name, player_uid, user_uid, use_region)
            if cache_key in self.cache:
                self._log_debug("Cache hit for", cache_key)
                return self.cache[cache_key]

        try:
            resp = self._perform_request(params)
            try:
                data = resp.json()
            except Exception as e:
                raise InvalidResponseError("Failed to parse API response as JSON.", "INVALID_RESPONSE", {"raw_text": getattr(resp, "text", None)}) from e

            if self.cache and cache:
                try:
                    self.cache[cache_key] = data
                except Exception:
                    pass

            return data

        except Exception as err:
            # Wrap and enrich error with structured diagnostics
            local_analysis = self._analyze_error_local(err, {"params": params})
            ai_enrichment = None
            try:
                ai_enrichment = self._enrich_with_ai(local_analysis, err, {"params": params})
            except Exception:
                ai_enrichment = None

            details = {"local": local_analysis}
            if ai_enrichment:
                details["ai"] = ai_enrichment

            # Map to specific error classes for common cases
            if isinstance(err, HTTPError) and getattr(err, "response", None) is not None:
                status = getattr(err.response, "status_code", None)
                if status in (401, 403):
                    raise AuthError(local_analysis["summary"], "AUTH_ERROR", details) from err
                if status == 429:
                    raise RateLimitError(local_analysis["summary"], "RATE_LIMIT", details) from err
                raise APIError(local_analysis["summary"], "API_ERROR", details) from err

            if isinstance(err, Timeout):
                raise NetworkError(local_analysis["summary"], "TIMEOUT", details) from err

            if isinstance(err, RequestException):
                raise NetworkError(local_analysis["summary"], "NETWORK_ERROR", details) from err

            # fallback
            raise HLFFClientError(local_analysis.get("summary", str(err)), "CLIENT_ERROR", details) from err

    # Public convenience methods

    def get_section(self, section_name: str, player_uid: str, user_uid: str, *, region: Optional[str] = None, cache: bool = True) -> Dict[str, Any]:
        """Generic section fetcher."""
        return self._call_section(section_name, player_uid, user_uid, region=region, cache=cache)

    def get_all_data(self, player_uid: str, user_uid: str, *, region: Optional[str] = None, cache: bool = True) -> Dict[str, Any]:
        return self.get_section("AllData", player_uid, user_uid, region=region, cache=cache)

    def get_account_info(self, player_uid: str, user_uid: str, *, region: Optional[str] = None, cache: bool = True) -> Dict[str, Any]:
        return self.get_section("AccountInfo", player_uid, user_uid, region=region, cache=cache)

    def get_account_profile(self, player_uid: str, user_uid: str, *, region: Optional[str] = None, cache: bool = True) -> Dict[str, Any]:
        return self.get_section("Account Profile Info", player_uid, user_uid, region=region, cache=cache)

    def get_guild_info(self, player_uid: str, user_uid: str, *, region: Optional[str] = None, cache: bool = True) -> Dict[str, Any]:
        return self.get_section("Guild Info", player_uid, user_uid, region=region, cache=cache)

    def get_pet_info(self, player_uid: str, user_uid: str, *, region: Optional[str] = None, cache: bool = True) -> Dict[str, Any]:
        return self.get_section("Pet Info", player_uid, user_uid, region=region, cache=cache)

    def get_social_info(self, player_uid: str, user_uid: str, *, region: Optional[str] = None, cache: bool = True) -> Dict[str, Any]:
        return self.get_section("Social Info", player_uid, user_uid, region=region, cache=cache)

    def ban_check(self, player_uid: str, user_uid: str, *, region: Optional[str] = None, cache: bool = True) -> Dict[str, Any]:
        return self.get_section("Ban Check", player_uid, user_uid, region=region, cache=cache)

    def api_status(self, user_uid: str, *, region: Optional[str] = None) -> Dict[str, Any]:
        """Simple health/status call; returns {'ok': True, 'info': ...} or {'ok': False, 'error': HLFFClientError}"""
        try:
            info = self.get_all_data("0", user_uid, region=region, cache=False)
            return {"ok": True, "info": info}
        except HLFFClientError as e:
            return {"ok": False, "error": e}

    def analyze_error(self, err: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Programmatic access to the local analyzer and optional AI enrichment."""
        local = self._analyze_error_local(err, context)
        ai = None
        try:
            ai = self._enrich_with_ai(local, err, context)
        except Exception:
            ai = None
        return {"local": local, "ai": ai}
