import logging
from importlib.metadata import version

import torch
from omegaconf import OmegaConf

import duo_ai
from duo_ai.core.config import MasterConfig, configure
from duo_ai.core.environment import CoordEnv, GeneralCoordEnv
from duo_ai.core.evaluator import Evaluator
from duo_ai.utils.global_variables import get_global_variable

__version__ = version("duo")


def make_config(args: object, dotlist_args: object = None) -> MasterConfig:
    """
    Create and configure a MasterConfig object from command-line arguments.

    Parameters
    ----------
    args : object
        Arguments object with a 'config' attribute.
    dotlist_args : object, optional
        Additional dotlist arguments for configuration.

    Returns
    -------
    MasterConfig
        Configured MasterConfig object.

    Examples
    --------
    >>> config = make_config(args)
    """
    config = OmegaConf.load(args.config) if args.config else OmegaConf.create()
    if dotlist_args is not None:
        cli_config = OmegaConf.from_dotlist(dotlist_args)
        config = OmegaConf.merge(config, cli_config)
    config = MasterConfig(**OmegaConf.to_container(config, resolve=True))

    configure(config)

    return config


def make_algorithm(config: object) -> object:
    """
    Instantiate an algorithm from the registry using the provided config.

    Parameters
    ----------
    config : object
        Algorithm configuration object with a 'name' attribute.

    Returns
    -------
    object
        Instantiated algorithm.

    Examples
    --------
    >>> algo = make_algorithm(config)
    """
    return duo_ai.algorithms.registry[config.name](config)


def make_policy(config: object, env: object) -> object:
    """
    Instantiate a policy from the registry using the provided config and environment.

    Parameters
    ----------
    config : object
        Policy configuration object with a 'name' attribute.
    env : object
        Environment instance.

    Returns
    -------
    object
        Instantiated policy.

    Examples
    --------
    >>> policy = make_policy(config, env)
    """
    return duo_ai.policies.registry[config.name](config, env)


def load_policy(path: str, env: object) -> object:
    """
    Load a policy from a checkpoint file.

    Parameters
    ----------
    path : str
        Path to the checkpoint file.
    env : object
        Environment instance.

    Returns
    -------
    object
        Loaded policy.

    Examples
    --------
    >>> policy = load_policy("checkpoint.ckpt", env)
    """
    ckpt = torch.load(
        path, map_location=get_global_variable("device"), weights_only=False
    )
    config = ckpt["policy_config"]

    policy = make_policy(config, env)
    policy.set_params(ckpt["model_state_dict"])
    logging.info(f"Loaded policy from {path}")

    return policy


def register_environment(name: str, config_cls: object) -> None:
    """
    Register an environment configuration class in the registry.

    Parameters
    ----------
    name : str
        Name of the environment.
    config_cls : object
        Environment configuration class.

    Returns
    -------
    None

    Examples
    --------
    >>> register_environment("myenv", MyEnvConfig)
    """
    duo_ai.environments.registry[name] = config_cls


def register_algorithm(name: str, algorithm_cls: object) -> None:
    """
    Register an algorithm class in the registry.

    Parameters
    ----------
    name : str
        Name of the algorithm.
    algorithm_cls : object
        Algorithm class.

    Returns
    -------
    None

    Examples
    --------
    >>> register_algorithm("ppo", PPOAlgorithm)
    """
    duo_ai.algorithms.registry[name] = algorithm_cls


def register_policy(name: str, policy_cls: object) -> None:
    """
    Register a policy class in the registry.

    Parameters
    ----------
    name : str
        Name of the policy.
    policy_cls : object
        Policy class.

    Returns
    -------
    None

    Examples
    --------
    >>> register_policy("ppo", PPOPolicy)
    """
    duo_ai.policies.registry[name] = policy_cls


def register_model(name: str, model_cls: object) -> None:
    """
    Register a model class in the registry.

    Parameters
    ----------
    name : str
        Name of the model.
    model_cls : object
        Model class.

    Returns
    -------
    None

    Examples
    --------
    >>> register_model("mlp", MLPModel)
    """
    duo_ai.models.registry[name] = model_cls
