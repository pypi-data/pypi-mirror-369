from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Any, Union

from pydantic import Field
from pydantic.dataclasses import dataclass


if TYPE_CHECKING:
    from inspect_ai import Task
    from inspect_ai.solver import Solver
    from nnsight import LanguageModel
    from inspect_ai.dataset import Dataset, Sample
    from inspect_ai.log import EvalLog
    from inspect_ai.model import Model
    from inspect_ai.scorer import Scorer
    from inspect_ai.tool import Tool
    from collections.abc import Callable
else:
    # At runtime, use Any to avoid expensive imports and pydantic errors
    Model = Any
    Solver = Any
    Task = Any
    Dataset = Any
    Sample = Any
    EvalLog = Any
    Scorer = Any
    Tool = Any
    LanguageModel = Any
    Callable = Any


@dataclass(config={"arbitrary_types_allowed": True})
class ModelOrganism:
    """Model organism configuration with validation."""

    name: str
    model: Model
    solver: Union[Solver, list[Solver]]
    supported_environments: set[str]
    inspect_load_name: str | None = None

    def update_solver(self, tools: list[Tool]) -> None:
        """
        Update the solver to use the provided tools.

        Overwrite this method to update the solver to use the provided tools in a way that is compatible with the model organism.
        """
        from inspect_ai.solver import use_tools
        
        if not tools:
            return

        if isinstance(self.solver, list):
            self.solver = [use_tools(tools), *self.solver]
        else:
            self.solver = [use_tools(tools), self.solver]
    
    def get_nnsight_model(self) -> LanguageModel:
        """Returns the nnsight model within the model organism's inspect ai model."""
        from nnsight import LanguageModel

        assert "nnsight_model" in self.model.model_args, "Model does not have an nnsight model"
        assert isinstance(self.model.model_args["nnsight_model"], LanguageModel), "nnsight model is not a LanguageModel"
        return self.model.model_args["nnsight_model"]
    
    def set_nnsight_hook(self, hook: Callable[[LanguageModel, str, Any], None]) -> None:
        """Overwrites the hook for the nnsight model within the model organism."""
        self.model.model_args["nnsight_args"]["hook"] = hook


@dataclass(config={"arbitrary_types_allowed": True})
class Environment:
    name: str
    observed_dataset: Union[Dataset, list[Sample]]
    unobserved_dataset: Union[Dataset, list[Sample]]
    tools: list[Tool] = Field(default_factory=list)
    scorers: list[Scorer] = Field(default_factory=list)
    task_config: dict[str, Any] = Field(default_factory=dict)
    type: str | None = None

    def get_observed_task(self, head: int = 50) -> Task:
        """Returns a Task using the observed dataset."""
        from inspect_ai import Task
        return Task(name=f"{self.name}_observed_task", dataset=self.observed_dataset[:min(head, len(self.observed_dataset))], scorer=self.scorers, **self.task_config)

    def get_unobserved_task(self, head: int = 50) -> Task:
        """Returns a Task using the unobserved dataset."""
        from inspect_ai import Task
        return Task(name=f"{self.name}_unobserved_task", dataset=self.unobserved_dataset[:min(head, len(self.unobserved_dataset))], scorer=self.scorers, **self.task_config)

    def get_tools(self) -> list[Tool]:
        """Returns the list of available tools."""
        return self.tools

    def get_scorers(self) -> list[Scorer] | None:
        """Returns the scorer"""
        if not self.scorers:
            raise ValueError("This environment does not have scorers")
        return self.scorers


@dataclass(config={"arbitrary_types_allowed": True})
class Detector(abc.ABC):
    """Abstract base detector with validation."""

    name: str
    supported_model_organisms: set[str]
    supported_environments: set[str]

    def _check_model_supported(self, model_organism: ModelOrganism) -> None:
        if model_organism.name not in self.supported_model_organisms:
            raise ValueError(
                f"Model organism {model_organism.name} not supported by detector {self.name}"
            )

    def _check_environment_supported(self, environment: Environment) -> None:
        if environment.name not in self.supported_environments:
            raise ValueError(
                f"Environment {environment.name} not supported by detector {self.name}"
            )

    def check_model_and_environment_supported(self, model_organism: ModelOrganism, environment: Environment) -> None:
        """
        Check if the model organism and environment are supported by the detector.
        """
        self._check_model_supported(model_organism)
        self._check_environment_supported(environment)
    
    def modify_environment(self, environment: Environment) -> None:
        """
        Given an environment, modifies it to make it more suitable for the detector.

        Default implementation does nothing.
        """
        pass
    
    def modify_model_organism(self, model_organism: ModelOrganism) -> None:
        """
        Given a model organism, adds whatever modifications to the model organism
        that are needed for the detector to detect deceptive alignment.

        Default implementation does nothing.
        """
        pass

    @abc.abstractmethod
    def get_prediction(self, eval_logs: list[EvalLog]) -> tuple[float, str]:
        """
        Returns a probability of the model organism being deceptively aligned and a string explaining the prediction.
        """
        ...
