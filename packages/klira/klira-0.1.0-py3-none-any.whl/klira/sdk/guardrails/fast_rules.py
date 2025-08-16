"""Fast, pattern-based rules engine for Klira AI guardrail policy enforcement.

This module implements a simple engine that evaluates text against predefined
patterns (regex) and keywords/domains specified in policy files (YAML or JSON).
It's designed for quick checks before potentially involving more complex LLM evaluations.
"""
# mypy: disable-error-code=unreachable

import os
import re
import json
import logging
import asyncio
from functools import lru_cache
from typing import Dict, List, Any, Optional, Union, TypedDict, Pattern

# Handle yaml import with proper error handling
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    yaml = None  # type: ignore[assignment]

# Handle async file I/O import with proper error handling
try:
    import aiofiles  # type: ignore[import-untyped]
    AIOFILES_AVAILABLE = True
except ImportError:
    AIOFILES_AVAILABLE = False
    aiofiles = None

logger = logging.getLogger("klira.guardrails.fast_rules")  # Specific logger

# --- Pattern Compilation Cache (Memory Optimization) ---

@lru_cache(maxsize=1000)
def compile_pattern(pattern: str) -> Optional[Pattern[str]]:
    """Compile regex pattern with LRU caching to prevent memory leaks.
    
    Args:
        pattern: Raw regex pattern string
        
    Returns:
        Compiled Pattern object or None if compilation fails
    """
    try:
        return re.compile(pattern, re.IGNORECASE)
    except re.error as e:
        logger.warning(f"Invalid regex pattern '{pattern}': {e}")
        return None

@lru_cache(maxsize=500)
def compile_domain_pattern(domain: str) -> Optional[Pattern[str]]:
    """Compile domain pattern with word boundaries and LRU caching.
    
    Args:
        domain: Domain string to convert to word-boundary regex
        
    Returns:
        Compiled Pattern object or None if compilation fails
    """
    try:
        # Use word boundaries for better matching
        domain_pattern = r"\b" + re.escape(domain) + r"\b"
        return re.compile(domain_pattern, re.IGNORECASE)
    except re.error as e:
        logger.warning(f"Error creating regex for domain '{domain}': {e}")
        return None

# --- Type Definitions ---


class PolicyRule(TypedDict, total=False):
    """Structure of a single policy rule definition."""

    id: str  # Required
    description: Optional[str]
    action: str  # 'block', 'warn', 'allow' (default: allow if matched)
    direction: Optional[str]  # 'inbound', 'outbound', or 'both' (default: 'both')
    patterns: Optional[List[str]]  # List of raw regex strings
    compiled_patterns: Optional[List[Pattern[str]]]  # Pre-compiled regex objects
    domains: Optional[List[str]]  # List of keywords/domains
    compiled_domains: Optional[List[Pattern[str]]]  # Pre-compiled domain regex objects
    confidence_pattern: float  # Confidence score for pattern match (default: 0.8)
    confidence_domain: float  # Confidence score for domain match (default: 0.3)
    guidelines: Optional[List[str]]  # List of guideline strings for policy augmentation


class FastRuleViolation(TypedDict):
    """Details of a specific policy violation found by the engine."""

    policy_id: str
    confidence: float
    matched_patterns: List[str]
    action: str


class FastRulesEvaluationResult(TypedDict):
    """Structure of the result returned by the FastRulesEngine evaluate method."""

    allowed: bool
    confidence: (
        float  # Highest confidence score among matched blocking/warning policies
    )
    matched_policies: List[str]  # IDs of all policies that had any match
    violations: List[FastRuleViolation]  # Details of matched blocking/warning policies
    matched_patterns: List[
        str
    ]  # All specific patterns/domains that matched across policies


# Default confidence levels
DEFAULT_CONFIDENCE_PATTERN = 0.8  # High confidence - immediate blocking
DEFAULT_CONFIDENCE_DOMAIN = 0.4  # Moderate confidence - triggers augmentation
# Confidence threshold for determining 'allowed' status
BLOCKING_THRESHOLD = 0.5


class FastRulesEngine:
    """Evaluates text against fast-matching rules defined in policies.

    Loads policies from a specified path (directory or file) containing
    YAML or JSON definitions. Each policy can define patterns (regex)
    or domains/keywords to match against input text.

    Attributes:
        policies_path (str): The path where policy files are located.
        policies (List[Dict[str, Any]]): The loaded policy rules.
    """

    def __init__(self, policies_path: str):
        """Initializes the FastRulesEngine and loads policies.

        Args:
            policies_path: The path to a directory containing policy files
                (YAML/JSON) or a single policy file.

        Raises:
            FileNotFoundError: If the provided policies_path does not exist.
        """
        self.policies_path = policies_path
        self.policies: List[PolicyRule] = []
        logger.info(
            f"Initializing FastRulesEngine with policies path: {self.policies_path}"
        )

        if not os.path.exists(self.policies_path):
            logger.error(f"Policies path does not exist: {self.policies_path}")
            raise FileNotFoundError(f"Policies path not found: {self.policies_path}")

        # Try async loading first, fall back to sync if needed
        if AIOFILES_AVAILABLE:
            try:
                import asyncio
                # Check if there's a running event loop
                try:
                    asyncio.get_running_loop()
                    # If we're in an async context, schedule the async loading
                    asyncio.create_task(self._load_and_process_policies_async())
                    logger.debug("Scheduled async policy loading")
                    return
                except RuntimeError:
                    # No running loop, use sync loading
                    pass
            except Exception as e:
                logger.debug(f"Failed to schedule async policy loading: {e}, falling back to sync")
        
        # Fall back to synchronous loading
        self._load_and_process_policies()

    def _compile_patterns(
        self, patterns: List[str], policy_id: str
    ) -> List[Pattern[str]]:
        """Compiles raw regex strings into Pattern objects using LRU cache."""
        compiled = []
        for pattern_str in patterns:
            if not isinstance(pattern_str, str):
                logger.warning(
                    f"Invalid pattern type ({type(pattern_str)}) in policy {policy_id}, expected string. Skipping."
                )
                continue
            
            # Use cached compilation to prevent memory leaks
            compiled_pattern = compile_pattern(pattern_str)
            if compiled_pattern is not None:
                compiled.append(compiled_pattern)
            else:
                logger.error(
                    f"Invalid regex pattern '{pattern_str}' in policy {policy_id}: failed to compile. Skipping."
                )
        return compiled

    def _compile_domains(
        self, domains: List[str], policy_id: str
    ) -> List[Pattern[str]]:
        """Compiles domain strings into word-boundary regex Pattern objects using LRU cache."""
        compiled = []
        for domain_str in domains:
            if not isinstance(domain_str, str):
                logger.warning(
                    f"Invalid domain type ({type(domain_str)}) in policy {policy_id}, expected string. Skipping."
                )
                continue
            
            # Use cached compilation to prevent memory leaks
            compiled_pattern = compile_domain_pattern(domain_str)
            if compiled_pattern is not None:
                compiled.append(compiled_pattern)
            else:
                logger.error(
                    f"Error creating regex for domain '{domain_str}' in policy {policy_id}: failed to compile. Skipping."
                )
        return compiled

    def _validate_and_process_policy(
        self, policy_data: Dict[str, Any], file_basename: str
    ) -> Optional[PolicyRule]:
        """Validates raw policy data and processes it into PolicyRule format."""
        if not isinstance(policy_data, dict):
            logger.warning(
                f"Policy item in {file_basename} is not a dictionary. Skipping."
            )
            return None

        policy_id = policy_data.get("id")
        if not policy_id or not isinstance(policy_id, str):
            logger.warning(
                f"Policy in {file_basename} is missing a valid string 'id'. Skipping: {policy_data}"
            )
            return None

        processed_policy: PolicyRule = {
            "id": policy_id,
            "description": policy_data.get("description"),
            "action": policy_data.get(
                "action", "allow"
            ).lower(),  # Default action is allow
            "direction": policy_data.get("direction", "both").lower(),  # Default direction is both
            "confidence_pattern": policy_data.get(
                "confidence_pattern", DEFAULT_CONFIDENCE_PATTERN
            ),
            "confidence_domain": policy_data.get(
                "confidence_domain", DEFAULT_CONFIDENCE_DOMAIN
            ),
        }

        raw_patterns = policy_data.get("patterns", [])
        if isinstance(raw_patterns, list):
            processed_policy["compiled_patterns"] = self._compile_patterns(
                raw_patterns, policy_id
            )
        elif raw_patterns:
            logger.warning(
                f"'patterns' field in policy {policy_id} is not a list. Ignoring."
            )

        raw_domains = policy_data.get("domains", [])
        if isinstance(raw_domains, list):
            processed_policy["compiled_domains"] = self._compile_domains(
                raw_domains, policy_id
            )
        elif raw_domains:
            logger.warning(
                f"'domains' field in policy {policy_id} is not a list. Ignoring."
            )

        if not processed_policy.get("compiled_patterns") and not processed_policy.get(
            "compiled_domains"
        ):
            logger.warning(
                f"Policy {policy_id} has no valid patterns or domains defined. It will not match anything."
            )
            # Optionally skip adding such policies, or keep them (might be intended for future use)

        # Validate action
        if processed_policy["action"] not in ["block", "warn", "allow"]:
            logger.warning(
                f"Invalid action '{processed_policy['action']}' for policy {policy_id}. Defaulting to 'allow'."
            )
            processed_policy["action"] = "allow"

        return processed_policy

    def _load_and_process_policies(self) -> None:
        """Loads policies from files and processes them (validation, compilation)."""
        try:
            # Use asyncio.run to call the async version from sync context
            asyncio.run(self._load_and_process_policies_async())
        except RuntimeError:
            # Already in async context, fallback to sync implementation
            self._load_and_process_policies_sync()

    def _load_and_process_policies_sync(self) -> None:
        """Synchronous fallback for policy loading."""
        files_processed = 0
        policies_added = 0

        if os.path.isfile(self.policies_path):
            files_to_process = [self.policies_path]
        elif os.path.isdir(self.policies_path):
            files_to_process = [
                os.path.join(self.policies_path, f)
                for f in os.listdir(self.policies_path)
                if os.path.isfile(os.path.join(self.policies_path, f))
                and f.lower().endswith((".json", ".yaml", ".yml"))
            ]
        else:
            # This case should be caught by __init__, but defensively check again
            logger.error(
                f"Policies path is neither a file nor a directory: {self.policies_path}"
            )
            return

        if not files_to_process:
            logger.warning(
                f"No policy files (.json, .yaml, .yml) found in path: {self.policies_path}"
            )
            return

        for file_path in files_to_process:
            files_processed += 1
            file_basename = os.path.basename(file_path)
            raw_data: Optional[Union[Dict[str, Any], List[Any]]] = None
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    if file_path.lower().endswith(".json"):
                        raw_data = json.load(f)
                    elif file_path.lower().endswith((".yaml", ".yml")):
                        if not YAML_AVAILABLE or yaml is None:
                            logger.warning(
                                f"Cannot load YAML policy '{file_basename}': PyYAML not installed. Skipping."
                            )
                            continue
                        raw_data = yaml.safe_load(f)
                    else:
                        # Should not happen due to file filtering, but good practice
                        logger.warning(
                            f"Skipping unsupported file format: {os.path.basename(file_path)}"
                        )
                        continue

                policy_list_raw: List[Dict[str, Any]] = []
                if isinstance(raw_data, list):
                    policy_list_raw = raw_data
                elif isinstance(raw_data, dict) and isinstance(
                    raw_data.get("policies"), list
                ):
                    policy_list_raw = raw_data["policies"]
                elif isinstance(raw_data, dict):
                    # Treat dict itself as a single policy definition
                    policy_list_raw = [raw_data]
                else:
                    logger.warning(
                        f"Unexpected data structure in policy file {file_basename}. Expected list or dict."
                    )
                    continue

                for policy_item in policy_list_raw:
                    processed = self._validate_and_process_policy(
                        policy_item, file_basename
                    )
                    if processed:
                        self.policies.append(processed)
                        policies_added += 1

            except json.JSONDecodeError as e:
                logger.error(f"Error decoding JSON from {file_basename}: {e}")
            except Exception as e:
                # Handle YAML errors and other exceptions
                if (
                    YAML_AVAILABLE
                    and yaml is not None
                    and hasattr(yaml, "YAMLError")
                    and isinstance(e, yaml.YAMLError)
                ):
                    logger.error(f"Error parsing YAML from {file_basename}: {e}")
                else:
                    logger.error(
                        f"Unexpected error loading policy from {file_basename}: {e}",
                        exc_info=True,
                    )

        logger.info(
            f"Processed {files_processed} policy file(s). Loaded and processed {policies_added} policies."
        )

    async def _load_and_process_policies_async(self) -> None:
        """Async version of policy loading for better performance."""
        files_processed = 0
        policies_added = 0

        if os.path.isfile(self.policies_path):
            files_to_process = [self.policies_path]
        elif os.path.isdir(self.policies_path):
            files_to_process = [
                os.path.join(self.policies_path, f)
                for f in os.listdir(self.policies_path)
                if os.path.isfile(os.path.join(self.policies_path, f))
                and f.lower().endswith((".json", ".yaml", ".yml"))
            ]
        else:
            # This case should be caught by __init__, but defensively check again
            logger.error(
                f"Policies path is neither a file nor a directory: {self.policies_path}"
            )
            return

        if not files_to_process:
            logger.warning(
                f"No policy files (.json, .yaml, .yml) found in path: {self.policies_path}"
            )
            return

        for file_path in files_to_process:
            files_processed += 1
            file_basename = os.path.basename(file_path)
            raw_data: Optional[Union[Dict[str, Any], List[Any]]] = None
            try:
                if AIOFILES_AVAILABLE and aiofiles:
                    # Use async file I/O when available
                    async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                        content = await f.read()
                        if file_path.lower().endswith(".json"):
                            raw_data = json.loads(content)
                        elif file_path.lower().endswith((".yaml", ".yml")):
                            if not YAML_AVAILABLE or yaml is None:
                                logger.warning(
                                    f"Cannot load YAML policy '{file_basename}': PyYAML not installed. Skipping."
                                )
                                continue
                            raw_data = yaml.safe_load(content)
                        else:
                            # Should not happen due to file filtering, but good practice
                            logger.warning(
                                f"Skipping unsupported file format: {os.path.basename(file_path)}"
                            )
                            continue
                else:
                    # Fallback to sync file I/O
                    with open(file_path, "r", encoding="utf-8") as f:
                        if file_path.lower().endswith(".json"):
                            raw_data = json.load(f)
                        elif file_path.lower().endswith((".yaml", ".yml")):
                            if not YAML_AVAILABLE or yaml is None:
                                logger.warning(
                                    f"Cannot load YAML policy '{file_basename}': PyYAML not installed. Skipping."
                                )
                                continue
                            raw_data = yaml.safe_load(f)
                        else:
                            # Should not happen due to file filtering, but good practice
                            logger.warning(
                                f"Skipping unsupported file format: {os.path.basename(file_path)}"
                            )
                            continue

                policy_list_raw: List[Dict[str, Any]] = []
                if isinstance(raw_data, list):
                    policy_list_raw = raw_data
                elif isinstance(raw_data, dict) and isinstance(
                    raw_data.get("policies"), list
                ):
                    policy_list_raw = raw_data["policies"]
                elif isinstance(raw_data, dict):
                    # Treat dict itself as a single policy definition
                    policy_list_raw = [raw_data]
                else:
                    logger.warning(
                        f"Unexpected data structure in policy file {file_basename}. Expected list or dict."
                    )
                    continue

                for policy_item in policy_list_raw:
                    processed = self._validate_and_process_policy(
                        policy_item, file_basename
                    )
                    if processed:
                        self.policies.append(processed)
                        policies_added += 1

            except json.JSONDecodeError as e:
                logger.error(f"Error decoding JSON from {file_basename}: {e}")
            except Exception as e:
                # Handle YAML errors and other exceptions
                if (
                    YAML_AVAILABLE
                    and yaml is not None
                    and hasattr(yaml, "YAMLError")
                    and isinstance(e, yaml.YAMLError)
                ):
                    logger.error(f"Error parsing YAML from {file_basename}: {e}")
                else:
                    logger.error(
                        f"Unexpected error loading policy from {file_basename}: {e}",
                        exc_info=True,
                    )

        logger.info(
            f"Processed {files_processed} policy file(s). Loaded and processed {policies_added} policies."
        )

    def evaluate(
        self, message: str, context: Optional[Dict[str, Any]] = None, direction: str = "inbound"
    ) -> FastRulesEvaluationResult:
        """Evaluates a message against the loaded fast rule policies.

        Iterates through loaded policies. If context provides specific `policy_ids`,
        only those are evaluated. Otherwise, all policies are checked.
        Matches based on regex `patterns` or keyword/domain strings in `domains`.
        Assigns confidence scores based on match type (pattern > domain).

        Args:
            message: The text message string to evaluate.
            context: An optional dictionary containing additional context.
                     Currently uses `policy_ids` (List[str]) to filter policies.
            direction: Direction of evaluation ("inbound", "outbound", or "both")

        Returns:
            A FastRulesEvaluationResult dictionary summarizing the outcome.
        """
        # Automatic performance instrumentation
        try:
            from klira.sdk.performance import timed_operation

            with timed_operation(
                "evaluate",
                "guardrails.fast_rules",
                {"policies_count": str(len(self.policies)), "direction": direction},
            ):
                return self._evaluate_internal(message, context, direction)
        except ImportError:
            # Fallback if performance module not available
            return self._evaluate_internal(message, context, direction)

    def _evaluate_internal(
        self, message: str, context: Optional[Dict[str, Any]] = None, direction: str = "inbound"
    ) -> FastRulesEvaluationResult:
        """Internal evaluation method (extracted for performance instrumentation)."""
        violations: List[FastRuleViolation] = []
        all_matched_patterns: List[str] = []
        all_matched_policy_ids: List[str] = []  # Track all matched policies
        max_confidence = 0.0
        context = context or {}

        # Handle empty or non-string message
        if not message or not isinstance(message, str):
            logger.debug(
                "evaluate received empty or non-string message, returning default allowed."
            )
            return FastRulesEvaluationResult(
                allowed=True,
                confidence=0.0,
                matched_policies=[],
                violations=[],
                matched_patterns=[],
            )

        # Check if evaluation should be limited to specific policies from context
        context_policy_ids: Optional[List[str]] = context.get("policy_ids")
        if context_policy_ids is not None and not isinstance(context_policy_ids, list):
            logger.warning(
                f"Context key 'policy_ids' should be a list, got {type(context_policy_ids)}. Ignoring."
            )
            context_policy_ids = None

        if not self.policies:
            logger.debug("No policies loaded, returning default allowed.")
            # Return structure consistent with normal operation
            return FastRulesEvaluationResult(
                allowed=True,
                confidence=0.0,
                matched_policies=[],
                violations=[],
                matched_patterns=[],
            )

        # Evaluate each policy
        for policy in self.policies:
            policy_id = policy["id"]
            action = policy.get("action", "allow")

            # Skip if context specifies IDs and this policy is not included
            if context_policy_ids is not None and policy_id not in context_policy_ids:
                continue

            # Skip if policy direction does not match the specified direction
            policy_direction = policy.get("direction", "both")
            if policy_direction is None:
                policy_direction = "both"
            if policy_direction.lower() not in ("both", direction.lower()):
                continue

            current_policy_match_score = 0.0
            current_policy_matched_patterns: List[str] = []

            # Check compiled patterns - these should immediately block if matched
            compiled_patterns = policy.get("compiled_patterns")
            if compiled_patterns is not None:  # Explicit None check
                for pattern in compiled_patterns:
                    match = pattern.search(message)
                    if match:
                        # Pattern match = immediate high confidence (blocking)
                        current_policy_match_score = policy.get(
                            "confidence_pattern", DEFAULT_CONFIDENCE_PATTERN
                        )
                        # Store the actual matched text, not the regex pattern
                        matched_text = match.group(0)
                        current_policy_matched_patterns.append(matched_text)
                        break  # One pattern match is enough for high confidence

            # Check compiled domains - these trigger policy augmentation
            compiled_domains = policy.get("compiled_domains")
            if compiled_domains is not None:  # Explicit None check
                for domain_pattern in compiled_domains:
                    match = domain_pattern.search(message)
                    if match:
                        # Domain match = moderate confidence (triggers augmentation)
                        if (
                            current_policy_match_score == 0.0
                        ):  # Only set if no pattern matched
                            current_policy_match_score = policy.get(
                                "confidence_domain", DEFAULT_CONFIDENCE_DOMAIN
                            )
                        # Use the actual matched text from the message
                        matched_domain = match.group(0)
                        if matched_domain not in current_policy_matched_patterns:
                            current_policy_matched_patterns.append(matched_domain)

            if current_policy_match_score > 0:
                all_matched_policy_ids.append(policy_id)
                all_matched_patterns.extend(current_policy_matched_patterns)

                # Create violation entry only for block/warn policies (not allow)
                if action in ["block", "warn"]:
                    violations.append(
                        FastRuleViolation(
                            policy_id=policy_id,
                            confidence=current_policy_match_score,
                            matched_patterns=current_policy_matched_patterns,
                            action=action,
                        )
                    )
                    # Update max confidence only for block/warn policies
                    max_confidence = max(max_confidence, current_policy_match_score)

                logger.debug(
                    f"Policy '{policy_id}' ({action}) matched with confidence {current_policy_match_score:.2f}. Patterns: {current_policy_matched_patterns}"
                )

        # Determine final allowed status based on policy actions (not confidence)
        # Block only if any matched policy has action "block"
        blocking_policies = [v for v in violations if v["action"] == "block"]
        is_allowed = len(blocking_policies) == 0

        # Remove duplicates from all_matched_patterns if desired (preserves order)
        unique_matched_patterns = list(dict.fromkeys(all_matched_patterns))

        result = FastRulesEvaluationResult(
            allowed=is_allowed,
            confidence=max_confidence,  # Highest score from any matched policy
            matched_policies=list(
                dict.fromkeys(all_matched_policy_ids)
            ),  # Unique matched policy IDs
            violations=violations,
            matched_patterns=unique_matched_patterns,
        )
        logger.info(
            f"Fast rules evaluation result: Allowed={result['allowed']}, Confidence={result['confidence']:.2f}, MatchedPolicies={result['matched_policies']}, Violations={len(result['violations'])}, BlockingPolicies={len(blocking_policies)}"
        )

        return result
