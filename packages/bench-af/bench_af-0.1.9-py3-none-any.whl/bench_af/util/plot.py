from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from pathlib import Path


class PlotMaker:
    def __init__(self, model: str):
        from datetime import datetime
        self.timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.model = model
        self.metrics = self.load_metrics_for_a_model()
        self.cot_flag = self.metrics.this_model_can_use_cot
    
    def get_plot_file_name(self, metric_type: str) -> Path:
        return self.get_plot_dir_name() / f"{self.model}_{metric_type}.png"
    
    def get_plot_dir_name(self) -> Path:
        from .root_location import get_bench_af_root
        plot_dir = get_bench_af_root() / "plots" / self.model / self.timestamp
        plot_dir.mkdir(parents=True, exist_ok=True)
        return plot_dir

    def make_single_plot(self, metric_type: str, scores: dict[str, float | int]):
        import numpy as np
        import matplotlib.pyplot as plt

        scores_list = list(scores.values())
        environments = list(scores.keys())
        x = np.arange(len(environments))
        width = 0.35
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(x, scores_list, width, label='Scores')
        ax.set_ylim(0, 1.1)
        ax.set_ylabel(metric_type)
        ax.set_title(f'{metric_type} for {self.model}')
        ax.set_xticks(x)
        ax.set_xticklabels(environments, rotation=45, ha='right')
        plt.tight_layout()
        plt.show()
        plt.savefig(self.get_plot_file_name(metric_type))

    def make_plots_pairs(self, metric_type: str, observed_scores: dict[str, float | int], unobserved_scores: dict[str, float | int]):
        import numpy as np
        import matplotlib.pyplot as plt

        observed_scores_list = list(observed_scores.values())
        unobserved_scores_list = list(unobserved_scores.values())
        environments = list(observed_scores.keys())
        assert list(unobserved_scores.keys()) == environments, "Unobserved scores keys do not match observed scores keys, or order is different"

        differences = [unobserved_scores_list[i] - observed_scores_list[i] for i in range(len(environments))]

        x = np.arange(len(environments))
        width = 0.35

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(x - width/2, observed_scores_list, width, label='Observed')
        ax.bar(x + width/2, unobserved_scores_list, width, label='Unobserved')

        for i, diff in enumerate(differences):
            ax.annotate(f'{diff:.2f}',
                        xy=(x[i], max(observed_scores_list[i], unobserved_scores_list[i]) + 0.03),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom',
                        fontsize=9,
                        color='red' if diff > 0 else 'green')
        ax.set_ylabel(metric_type)
        ax.set_title(f'{metric_type} for {self.model}')
        ax.set_xticks(x)
        ax.set_xticklabels(environments, rotation=45, ha='right')
        ax.set_ylim(0, 1.1)
        ax.legend()

        plt.tight_layout()
        plt.show()
        plt.savefig(self.get_plot_file_name(metric_type))
    
    def load_metrics_for_a_model(self) -> None:
        from .cache import get_cache_dir_one_model_all_environments
        from .cache import MetricsForManyEnvironments
        import json

        cache_dir = get_cache_dir_one_model_all_environments(self.model)
        if not cache_dir.exists():
            raise FileNotFoundError(f"Cache directory {cache_dir} does not exist")
        with open(cache_dir) as f:
            data = json.load(f)
        metrics = MetricsForManyEnvironments.model_validate(data)
        return metrics

    def make_comparison_plots_given_the_metric_type(self, metric_type: str):
        observed_data = {env: getattr(self.metrics.data[env].observed, metric_type) for env in self.metrics.data}
        unobserved_data = {env: getattr(self.metrics.data[env].unobserved, metric_type) for env in self.metrics.data}
        self.make_plots_pairs(metric_type, observed_data, unobserved_data)

    def make_conditional_plots_given_the_metric_type(self, metric_type: str):
        scores = {env: getattr(self.metrics.data[env].conditional, metric_type) for env in self.metrics.data}
        self.make_single_plot(metric_type, scores)
    
    def make_all_plots(self):
        self.make_comparison_plots_given_the_metric_type("compliance")
        if self.cot_flag:
            self.make_comparison_plots_given_the_metric_type("behave_because_observed")
            self.make_comparison_plots_given_the_metric_type("misbehave_because_unobserved")
            self.make_conditional_plots_given_the_metric_type("behave_conditional_on_behave_because_observed")
            self.make_conditional_plots_given_the_metric_type("misbehave_conditional_on_misbehave_because_unobserved")

    def make_plot(self, metric_type: str):
        if not self.cot_flag and metric_type != "compliance":
            raise ValueError(f"Invalid metric type: {metric_type} for a comparison between observed and unobserved")
        if metric_type in ["compliance", "behave_because_observed", "misbehave_because_unobserved"]:
            self.make_comparison_plots_given_the_metric_type(metric_type)
        elif metric_type in ["behave_conditional_on_behave_because_observed", "misbehave_conditional_on_misbehave_because_unobserved"]:
            self.make_conditional_plots_given_the_metric_type(metric_type)
        else:
            raise ValueError(f"Invalid metric type: {metric_type}")

def make_plots_for_a_model(model: str) -> Path:
    plot_maker = PlotMaker(model)
    plot_maker.make_all_plots()
    return plot_maker.get_plot_dir_name()

if __name__ == "__main__":
    make_plots_for_a_model("test_nnsight")
    print("All plots generated successfully!")
