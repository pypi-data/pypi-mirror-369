import logging
from dataclasses import dataclass, field
from typing import Dict, List

import numpy as np
import torch

from duo_ai.core import Algorithm
from duo_ai.utils.global_variables import get_global_variable


@dataclass
class RandomAlgorithmConfig:
    """
    Configuration dataclass for RandomAlgorithm.

    Parameters
    ----------
    name : str, optional
        Name of the algorithm class. Default is "random".
    probs : list of float, optional
        List of probabilities to search. Default is np.arange(0, 1.01, 0.1).

    Examples
    --------
    >>> config = RandomAlgorithmConfig()
    """

    name: str = "random"
    probs: List[float] = field(default_factory=lambda: np.arange(0, 1.01, 0.1).tolist())


class RandomAlgorithm(Algorithm):
    """
    Algorithm that searches for the best probability parameter to maximize evaluation reward.

    Examples
    --------
    >>> algo = RandomAlgorithm(RandomAlgorithmConfig())
    """

    config_cls = RandomAlgorithmConfig

    def __init__(self, config: RandomAlgorithmConfig) -> None:
        """
        Initialize the RandomAlgorithm.

        Parameters
        ----------
        config : RandomAlgorithmConfig
            Configuration object for the RandomAlgorithm.

        Returns
        -------
        None

        Examples
        --------
        >>> algo = RandomAlgorithm(RandomAlgorithmConfig())
        """
        self.config = config

    def train(
        self,
        policy: "duo.policies.PPOPolicy",
        env: "gym.Env",
        validators: Dict[str, "duo.core.Evaluator"],
    ) -> None:
        """
        Train the RandomAlgorithm by searching for the best probability parameter that maximizes evaluation reward.

        Parameters
        ----------
        policy : duo.policies.PPOPolicy
            The policy to be evaluated and tuned.
        env : gym.Env
            The environment instance for training and data generation.
        validators : dict of str to duo.core.Evaluator
            Dictionary mapping split names to evaluator instances for evaluation.

        Returns
        -------
        None

        Examples
        --------
        >>> algorithm = RandomAlgorithm(RandomAlgorithmConfig())
        >>> algorithm.train(policy, env, validators)
        """
        config = self.config
        self.save_dir = get_global_variable("experiment_dir")

        best_prob = {}
        best_result = {}
        for split in validators:
            best_result[split] = {"reward_mean": -float("inf")}

        for prob in config.probs:
            logging.info(f"Prob: {prob}")

            policy.set_params({"prob": prob})

            eval_result = {}
            for split, validator in validators.items():
                logging.info(f"Evaluating on {split} split")
                eval_result[split] = validator.evaluate(policy)
                if (
                    eval_result[split]["reward_mean"]
                    > best_result[split]["reward_mean"]
                ):
                    best_prob[split] = prob
                    best_result[split] = eval_result[split]
                    self.save_checkpoint(policy, f"best_{split}")

            # Log best result so far
            for split, validator in validators.items():
                logging.info(f"BEST {split} so far")
                logging.info(f"Prob: {best_prob[split]}")
                validator.summarizer.write(best_result[split])

    def save_checkpoint(self, policy: "duo.policies.PPOPolicy", name: str) -> None:
        """
        Save the current policy configuration and parameters to a checkpoint file.

        Parameters
        ----------
        policy : duo.policies.PPOPolicy
            The policy whose parameters are to be saved.
        name : str
            Name for the checkpoint file.

        Returns
        -------
        None

        Examples
        --------
        >>> self.save_checkpoint(policy, "best_test")
        """
        save_path = f"{self.save_dir}/{name}.ckpt"
        torch.save(
            {
                "policy_config": policy.config,
                "model_state_dict": policy.get_params(),
            },
            save_path,
        )
        logging.info(f"Saved checkpoint to {save_path}")
