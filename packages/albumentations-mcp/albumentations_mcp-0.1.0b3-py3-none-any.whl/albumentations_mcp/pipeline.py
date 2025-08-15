"""Complete augmentation workflow orchestration with hook system integration."""

import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from .hooks import (
    HookContext,
    HookStage,
    execute_stage,
    get_hook_registry,
    register_hook,
)
from .hooks.post_mcp import PostMCPHook
from .hooks.post_transform_verify import post_transform_verify_hook
from .hooks.pre_mcp import PreMCPHook
from .parser import PromptParsingError, parse_prompt

logger = logging.getLogger(__name__)


class AugmentationPipeline:
    """Complete augmentation pipeline with hook system integration."""

    def __init__(self):
        """Initialize pipeline and register default hooks."""
        self._setup_default_hooks()

    def _setup_default_hooks(self):
        """Register default hooks for the pipeline."""
        from .hooks.post_save import PostSaveHook
        from .hooks.post_transform import PostTransformHook
        from .hooks.pre_save import PreSaveHook
        from .hooks.pre_transform import PreTransformHook

        # Register pre-MCP hook
        register_hook(HookStage.PRE_MCP, PreMCPHook())

        # Register post-MCP hook
        register_hook(HookStage.POST_MCP, PostMCPHook())

        # Register pre-transform hook
        register_hook(HookStage.PRE_TRANSFORM, PreTransformHook())

        # Register post-transform hook
        register_hook(HookStage.POST_TRANSFORM, PostTransformHook())

        # Register post-transform verification hook
        register_hook(HookStage.POST_TRANSFORM_VERIFY, post_transform_verify_hook)

        # Register pre-save hook
        register_hook(HookStage.PRE_SAVE, PreSaveHook())

        # Register post-save hook
        register_hook(HookStage.POST_SAVE, PostSaveHook())

        logger.info("All 7 hooks registered successfully")

    async def process_image_with_hooks(
        self,
        image_b64: str,
        prompt: str,
        seed: int | None = None,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        """Process image using the complete 7-stage hook system."""
        import uuid

        from .image_utils import base64_to_pil, pil_to_base64
        from .processor import get_processor

        if session_id is None:
            session_id = str(uuid.uuid4())

        # Convert base64 to PIL Image
        image = base64_to_pil(image_b64)

        # Initialize context
        context = HookContext(
            session_id=session_id,
            original_prompt=prompt,
            image_data=image_b64.encode(),
            metadata={
                "timestamp": datetime.now(UTC).isoformat(),
                "pipeline_version": "1.0.0",
                "seed": seed,
            },
        )

        logger.info(f"Starting full image processing pipeline for session {session_id}")

        try:
            # Stage 1: Pre-MCP processing
            result = await execute_stage(HookStage.PRE_MCP, context)
            if not result.success or not result.should_continue:
                return self._format_error_response(context, "Pre-MCP stage failed")
            context = result.context

            # Stage 2: Parse the prompt (core functionality)
            try:
                parse_result = parse_prompt(context.original_prompt)
                context.parsed_transforms = [
                    {
                        "name": transform.name.value,
                        "parameters": transform.parameters,
                        "probability": transform.probability,
                    }
                    for transform in parse_result.transforms
                ]
                context.metadata.update(
                    {
                        "parser_confidence": parse_result.confidence,
                        "parser_warnings": parse_result.warnings,
                        "parser_suggestions": parse_result.suggestions,
                    },
                )
                context.warnings.extend(parse_result.warnings)
            except PromptParsingError as e:
                error_msg = f"Prompt parsing failed: {e!s}"
                logger.error(error_msg)
                context.errors.append(error_msg)
                return self._format_error_response(context, error_msg)

            # Stage 3: Post-MCP processing
            result = await execute_stage(HookStage.POST_MCP, context)
            if not result.success:
                logger.warning("Post-MCP stage failed, but continuing")
            context = result.context

            # Stage 4: Pre-transform validation
            result = await execute_stage(HookStage.PRE_TRANSFORM, context)
            if not result.success or not result.should_continue:
                return self._format_error_response(
                    context,
                    "Pre-transform validation failed",
                )
            context = result.context

            # Stage 5: Apply transforms (core processing)
            processor = get_processor()
            processing_result = processor.process_image(
                image,
                context.parsed_transforms,
                seed=seed,
            )

            if not processing_result.success:
                error_msg = (
                    f"Image processing failed: {processing_result.error_message}"
                )
                context.errors.append(error_msg)
                return self._format_error_response(context, error_msg)

            # Add processing results to context
            context.augmented_image = pil_to_base64(
                processing_result.augmented_image,
            ).encode()
            context.metadata.update(
                {
                    "processing_result": {
                        "applied_transforms": processing_result.applied_transforms,
                        "skipped_transforms": processing_result.skipped_transforms,
                        "execution_time": processing_result.execution_time,
                        "success": processing_result.success,
                    },
                    "original_image": image,
                    "augmented_image": processing_result.augmented_image,
                },
            )

            # Stage 6: Post-transform metadata generation
            result = await execute_stage(HookStage.POST_TRANSFORM, context)
            if not result.success:
                logger.warning("Post-transform stage failed, but continuing")
            context = result.context

            # Stage 7: Visual verification
            result = await execute_stage(HookStage.POST_TRANSFORM_VERIFY, context)
            if not result.success:
                logger.warning("Visual verification failed, but continuing")
            context = result.context

            # Stage 8: Pre-save file management
            result = await execute_stage(HookStage.PRE_SAVE, context)
            if not result.success:
                logger.warning("Pre-save stage failed, but continuing")
            context = result.context

            # Stage 9: Post-save cleanup
            result = await execute_stage(HookStage.POST_SAVE, context)
            if not result.success:
                logger.warning("Post-save stage failed, but continuing")
            context = result.context

            # Format successful response
            response = {
                "success": True,
                "session_id": context.session_id,
                "augmented_image": pil_to_base64(processing_result.augmented_image),
                "metadata": context.metadata,
                "warnings": context.warnings,
                "errors": context.errors,
                "message": f"Successfully processed image with {len(context.parsed_transforms or [])} transforms",
            }
            logger.info(
                f"Full pipeline completed successfully for session {session_id}",
            )
            return response

        except Exception as e:
            error_msg = f"Pipeline execution failed: {e!s}"
            logger.error(error_msg, exc_info=True)
            context.errors.append(error_msg)
            return self._format_error_response(context, error_msg)

    async def parse_prompt_with_hooks(
        self,
        prompt: str,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        """Parse prompt using the complete hook system."""
        if session_id is None:
            session_id = str(uuid.uuid4())

        # Initialize context
        context = HookContext(
            session_id=session_id,
            original_prompt=prompt,
            metadata={
                "timestamp": datetime.now(UTC).isoformat(),
                "pipeline_version": "1.0.0",
            },
        )

        logger.info(f"Starting prompt parsing pipeline for session {session_id}")

        try:
            # Stage 1: Pre-MCP processing
            result = await execute_stage(HookStage.PRE_MCP, context)
            if not result.success or not result.should_continue:
                return self._format_error_response(context, "Pre-MCP stage failed")
            context = result.context

            # Stage 2: Parse the prompt (core functionality)
            try:
                parse_result = parse_prompt(context.original_prompt)

                # Convert parser result to hook context format
                context.parsed_transforms = [
                    {
                        "name": transform.name.value,
                        "parameters": transform.parameters,
                        "probability": transform.probability,
                    }
                    for transform in parse_result.transforms
                ]

                # Add parser metadata
                context.metadata.update(
                    {
                        "parser_confidence": parse_result.confidence,
                        "parser_warnings": parse_result.warnings,
                        "parser_suggestions": parse_result.suggestions,
                    },
                )
                context.warnings.extend(parse_result.warnings)

            except PromptParsingError as e:
                error_msg = f"Prompt parsing failed: {e!s}"
                logger.error(error_msg)
                context.errors.append(error_msg)
                return self._format_error_response(context, error_msg)

            # Stage 3: Post-MCP processing
            result = await execute_stage(HookStage.POST_MCP, context)
            if not result.success:
                logger.warning("Post-MCP stage failed, but continuing")
            context = result.context

            # Format successful response
            response = self._format_success_response(context)
            logger.info(f"Pipeline completed successfully for session {session_id}")
            return response

        except Exception as e:
            error_msg = f"Pipeline execution failed: {e!s}"
            logger.error(error_msg, exc_info=True)
            context.errors.append(error_msg)
            return self._format_error_response(context, error_msg)

    def _format_success_response(self, context: HookContext) -> dict[str, Any]:
        """Format successful pipeline response."""
        return {
            "success": True,
            "session_id": context.session_id,
            "transforms": context.parsed_transforms,
            "metadata": context.metadata,
            "warnings": context.warnings,
            "errors": context.errors,
            "message": f"Successfully parsed {len(context.parsed_transforms or [])} transforms",
        }

    def _format_error_response(
        self,
        context: HookContext,
        error: str,
    ) -> dict[str, Any]:
        """Format error pipeline response."""
        return {
            "success": False,
            "session_id": context.session_id,
            "transforms": context.parsed_transforms or [],
            "metadata": context.metadata,
            "warnings": context.warnings,
            "errors": context.errors,
            "message": error,
        }

    def get_pipeline_status(self) -> dict[str, Any]:
        """Get current pipeline status and registered hooks."""
        registry = get_hook_registry()
        return {
            "registered_hooks": registry.list_hooks(),
            "pipeline_version": "1.0.0",
            "supported_stages": [stage.value for stage in HookStage],
        }


# Global pipeline instance
_pipeline_instance = None


def get_pipeline() -> AugmentationPipeline:
    """Get global pipeline instance."""
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = AugmentationPipeline()
    return _pipeline_instance


async def parse_prompt_with_hooks(
    prompt: str,
    session_id: str | None = None,
) -> dict[str, Any]:
    """Convenience function to parse prompt with hooks."""
    return await get_pipeline().parse_prompt_with_hooks(prompt, session_id)


async def process_image_with_hooks(
    image_b64: str,
    prompt: str,
    seed: int | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """Convenience function to process image with full hook pipeline."""
    return await get_pipeline().process_image_with_hooks(
        image_b64,
        prompt,
        seed,
        session_id,
    )
