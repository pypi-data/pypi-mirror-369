from __future__ import annotations

from dataclasses import dataclass

from momotor.bundles import RecipeBundle, ConfigBundle, ProductBundle, ResultsBundle
from momotor.bundles.elements.steps import Step
from momotor.options.task_id import StepTaskId


@dataclass(frozen=True)
class Providers:
    """ A data class that contains all bundles and a `task_id` used to resolve
    :ref:`references <references>`
    """
    #: The :py:class:`~momotor.bundles.RecipeBundle`
    recipe: RecipeBundle | None = None

    #: The :py:class:`~momotor.bundles.ConfigBundle`
    config: ConfigBundle | None = None

    #: The :py:class:`~momotor.bundles.ProductBundle`
    product: ProductBundle | None = None

    #: The :py:class:`~momotor.bundles.ResultsBundle`
    results: ResultsBundle | None = None

    #: The current task id
    task_id: StepTaskId | None = None

    @property
    def step(self) -> Step | None:
        """ The step """
        if self.recipe and self.task_id:
            return self.recipe.steps[self.task_id.step_id]

        return None
