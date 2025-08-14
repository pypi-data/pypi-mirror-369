"""Formula execution logic for the evaluator."""

from __future__ import annotations

import logging
from typing import Any

from .config_models import FormulaConfig, SensorConfig
from .core_formula_evaluator import CoreFormulaEvaluator
from .enhanced_formula_evaluation import EnhancedSimpleEvalHelper
from .evaluator_error_handler import EvaluatorErrorHandler
from .evaluator_handlers import HandlerFactory
from .exceptions import BackingEntityResolutionError
from .type_definitions import ContextValue, EvaluationResult

_LOGGER = logging.getLogger(__name__)


class FormulaExecutionEngine:
    """Handles the core formula execution logic for the evaluator."""

    def __init__(
        self,
        handler_factory: HandlerFactory,
        error_handler: EvaluatorErrorHandler,
        enhanced_helper: EnhancedSimpleEvalHelper,
    ):
        """Initialize the formula execution engine.

        Args:
            handler_factory: Factory for creating formula handlers
            error_handler: Error handler for circuit breaker pattern
            enhanced_helper: Enhanced evaluation helper (clean slate design - always required)
        """
        self._handler_factory = handler_factory
        self._error_handler = error_handler
        self._enhanced_helper = enhanced_helper
        # Create the core formula evaluator that implements CLEAN SLATE routing
        self._core_evaluator = CoreFormulaEvaluator(handler_factory, enhanced_helper)

    def execute_formula_evaluation(
        self,
        config: FormulaConfig,
        resolved_formula: str,
        handler_context: dict[str, ContextValue],
        eval_context: dict[str, ContextValue],
        sensor_config: SensorConfig | None,
    ) -> float | str | bool:
        """Execute formula evaluation with proper handler routing.

        This is the core evaluation method that handles the clean slate routing
        architecture with enhanced SimpleEval as the primary path.

        Args:
            config: Formula configuration
            resolved_formula: Formula with variables resolved
            handler_context: Context for handlers (ReferenceValue objects)
            eval_context: Context for evaluation (mixed types)
            sensor_config: Optional sensor configuration

        Returns:
            Evaluation result

        Raises:
            ValueError: If evaluation fails
        """
        _LOGGER.debug("🔥 FORMULA_EXECUTION_ENGINE: Delegating to core evaluator: %s", resolved_formula)

        original_formula = config.formula

        # Delegate to the extracted core formula evaluator
        return self._core_evaluator.evaluate_formula(resolved_formula, original_formula, handler_context)

    def handle_value_error(self, error: ValueError, formula_name: str) -> EvaluationResult:
        """Handle ValueError during formula evaluation."""
        error_msg = str(error)

        # Enhanced error handling with more specific checks
        if any(keyword in error_msg.lower() for keyword in ["undefined", "not defined", "name", "variable"]):
            # Variable/name resolution errors
            _LOGGER.warning("Variable resolution error in formula '%s': %s", formula_name, error_msg)
            self._error_handler.increment_error_count(formula_name)
            return EvaluationResult(success=False, value="unavailable", error=error_msg)

        if "division by zero" in error_msg.lower():
            # Mathematical errors that might be transitory
            _LOGGER.warning("Mathematical error in formula '%s': %s", formula_name, error_msg)
            self._error_handler.increment_transitory_error_count(formula_name)
            return EvaluationResult(success=False, value="unknown", error=error_msg)

        # Default: treat as fatal error
        _LOGGER.warning("Fatal error in formula '%s': %s", formula_name, error_msg)
        self._error_handler.increment_error_count(formula_name)
        return EvaluationResult(success=False, value="unavailable", error=error_msg)

    def handle_backing_entity_error(self, error: BackingEntityResolutionError, formula_name: str) -> EvaluationResult:
        """Handle BackingEntityResolutionError - these are always fatal (missing entities)."""
        _LOGGER.warning("Backing entity resolution error in formula '%s': %s", formula_name, error)
        self._error_handler.increment_error_count(formula_name)
        return EvaluationResult(success=False, value="unavailable", error=str(error))

    def convert_handler_result(self, result: Any) -> bool | str | float | int:
        """Convert handler result to expected types."""
        if isinstance(result, bool | str | float | int):
            return result
        # Convert other types to string representation
        return str(result)
