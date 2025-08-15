from abc import ABC, abstractmethod
from typing import Any, Literal

Asset = Literal["BTC", "ETH", "XAU", "SOL"]
GenerateSimulationsOutput = list[list[dict[str, Any]]]

DEFAULT_SIGMA = 0.1


class SynthMiner(ABC):

    @abstractmethod
    def generate_simulations(
        self,
        asset: Asset,
        current_price: float,
        start_time: str,
        time_increment: int,
        time_length: int,
        num_simulations: int,
        sigma: float,
    ) -> GenerateSimulationsOutput:
        """
        Generate simulated price paths.

        Parameters:
            asset (str): The asset to simulate.
            current_price (float): The current price of the asset to simulate.
            start_time (str): The start time of the simulation. Defaults to current time.
            time_increment (int): Time increment in seconds.
            time_length (int): Total time length in seconds.
            num_simulations (int): Number of simulation runs.
            sigma (float): Standard deviation of the simulated price path.

        Returns:
            numpy.ndarray: Simulated price paths.
        """

        pass
