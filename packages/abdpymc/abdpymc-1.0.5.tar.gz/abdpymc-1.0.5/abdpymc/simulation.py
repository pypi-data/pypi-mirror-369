from collections import namedtuple
from numbers import Number
from typing import Optional
import dataclasses

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pydantic import (
    BaseModel,
    ConfigDict,
    field_validator,
    FiniteFloat,
    NegativeFloat,
    NonNegativeFloat,
    PositiveFloat,
)

import abdpymc as abd

InfectionResponses = namedtuple(
    "InfectionResponses", ("infections", "s_response", "n_response")
)


class BaseModelNoExtra(BaseModel):
    """
    Prevent additional fields being passed to a pydantic model.
    """

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)


class Protection(BaseModelNoExtra):
    """
    Parameters of a protection curve

    Args:
        a: 50% protective titer
        b: Slope of protection curve
    """

    a: FiniteFloat = 0.0
    b: PositiveFloat = 1.0

    def p_protection(self, titer: float) -> float:
        """
        Probability of protection from infection at a given titer.
        """
        return 1 / (1 + np.exp(-self.b * (titer - self.a)))

    def is_protected(self, titer: float) -> float:
        """
        Is an individual with a given titer protected from infection?
        """
        return np.random.uniform() < self.p_protection(titer)

    def plot_curve(self, lo: FiniteFloat = -5, hi: FiniteFloat = 5, **kwds) -> None:
        """
        Plot the protection curve between lo and hi.
        """
        grid = np.linspace(lo, hi)
        plt.plot(grid, self.p_protection(grid), **kwds)


class Elisa(BaseModelNoExtra):
    """
    Parameters of an ELISA titration curve.

    Args:
        b: Slope of the OD sigmoid curve.
        d: Maximum response of the OD curve.
        sd: Standard deviation of the error on an OD reading.
    """

    b: NegativeFloat = -2.2
    d: PositiveFloat = 1.6
    sd: PositiveFloat = 0.1

    def model_od(self, dilution: FiniteFloat, titer: FiniteFloat) -> float:
        """
        What is the measured OD of a sample with a particular titer at a given dilution?

        Args:
            dilution: The dilution of the sample.
            titer: The titer of the sample.
        """
        return np.random.normal(
            loc=abd.logistic(x=dilution, a=titer, b=self.b, d=self.d), scale=self.sd
        )


class Dynamics(BaseModelNoExtra):
    """
    How antibody titers change over time.

    Args:
        init: The initial value.
        perm_rise: Permanent rise after any infection or vaccination.
        temp_rise_{i,v}: Temporary rise after an infection or vaccination.
        temp_wane: Waning rate
    """

    init: FiniteFloat = -2.0
    perm_rise: NonNegativeFloat = 2.0
    temp_rise_i: NonNegativeFloat = 1.5
    temp_rise_v: NonNegativeFloat = 2.0
    temp_wane: PositiveFloat = 0.95

    @field_validator("temp_wane")
    @classmethod
    def wane_must_be_between_0_1(cls, value) -> float:
        if not 0.0 <= value <= 1.0:
            raise ValueError("waning parameter must be between 0-1")
        return value

    def next_temp_response(
        self, prev: float, is_infected: bool, is_vaccinated: bool = False
    ) -> float:
        """
        Calculate the next temporary response given a previous temporary response.

        Args:
            prev: The previous temporary response.
            is_infected: Did this individual just get infected?
            is_vaccinated: Did this individual just get vaccinated?
        """
        return (
            prev * self.temp_wane
            + is_infected * self.temp_rise_i
            + is_vaccinated * self.temp_rise_v
        )

    def perm_response(
        self, infections: np.ndarray, vaccinations: Optional[np.array] = None
    ) -> float:
        """
        Calculate a permanent response, given an array of infections and optional
        vaccinations.

        Args:
            infections: Binary array indicating when infections occurred.
            vaccinations: Binary array indicating when vaccinations occurred. Passing
                None implies that this permanent response is not affected by vaccination
                (i.e. for the N antigen).
        """
        if infections.any():
            return self.perm_rise
        elif vaccinations is not None and vaccinations.any():
            return self.perm_rise
        else:
            return 0.0


class Antibody(BaseModelNoExtra):
    """
    Behaviour of an antibody defined by titer mediated protection from infection, ELISA
    characteristics and how titers change in response to vaccination or infection
    (dynamics).
    """

    protection: Protection = Protection()
    elisa: Elisa = Elisa()
    dynamics: Dynamics = Dynamics()


class Antibodies(BaseModelNoExtra):
    """
    S and N antibodies.
    """

    s: Antibody = Antibody()
    n: Antibody = Antibody()

    def is_protected(self, s_titer: Number, n_titer: Number) -> bool:
        """
        Is an individual protected by either an S or N response?

        Args:
            {s,n}_titer: Titers.
        """
        protected_by_s = self.s.protection.is_protected(s_titer)
        protected_by_n = self.n.protection.is_protected(n_titer)
        return protected_by_n or protected_by_s

    def plot_protection_curves(self, lo=-5, hi=5, **kwds) -> None:
        """
        Plot protection curves for both antibodies.

        Args:
            lo: Titer minimum (x-axis).
            hi: Titer maximum (y-axis).
        """
        self.s.protection.plot_curve(lo=lo, hi=hi, label="S", c=abd.DARKORANGE, **kwds)
        self.n.protection.plot_curve(lo=lo, hi=hi, label="N", c=abd.BLUEGREY, **kwds)


@dataclasses.dataclass
class Individual:
    """
    An individual.

    Args:
        {pcrpos,vacs}: (n_gaps,) binary arrays indicating when individuals had a PCR+
            result or were vaccinated.
        ab: Antibody responses.
    """

    pcrpos: np.ndarray
    vacs: np.ndarray
    ab: Antibodies = dataclasses.field(default_factory=Antibodies)

    def __post_init__(self) -> None:
        self.pcrpos = np.array(self.pcrpos)
        self.vacs = np.array(self.vacs)
        if self.pcrpos.shape != self.vacs.shape:
            raise ValueError("vaccination and pcrpos are different shapes")
        if self.pcrpos.ndim != 1:
            raise ValueError("vaccination and pcrpos should be 1 dimensional")
        self.n_gaps = len(self.pcrpos)

    def infection_responses(self, lam0: np.ndarray) -> InfectionResponses:
        """
        Simulate infections and responses.

        Args:
            lam0: Per-time gap infection probability (baseline infection rate).
        """
        if lam0.ndim != 1:
            raise ValueError("lam0 should be 1D")

        if len(lam0) != self.n_gaps:
            raise ValueError("must have single infection rate for each time gap")

        s = np.empty(self.n_gaps)
        n = np.empty(self.n_gaps)
        infections = np.zeros(self.n_gaps)

        s_temp = 0
        n_temp = 0

        for t in range(self.n_gaps):
            exposed = np.random.uniform() < lam0[t]

            s_prev = s[t - 1] if t > 0 else self.ab.s.dynamics.init
            n_prev = n[t - 1] if t > 0 else self.ab.n.dynamics.init

            if self.pcrpos[t] == 1:
                is_infected = True

            elif exposed and not self.ab.is_protected(s_titer=s_prev, n_titer=n_prev):
                is_infected = True

            else:
                is_infected = False

            if is_infected:
                infections[t] = 1.0

            is_vaccinated = self.vacs[t] == 1.0

            s_temp = self.ab.s.dynamics.next_temp_response(
                s_temp, is_infected=is_infected, is_vaccinated=is_vaccinated
            )
            n_temp = self.ab.n.dynamics.next_temp_response(
                n_temp, is_infected=is_infected
            )

            s_perm = self.ab.s.dynamics.perm_response(
                infections[: t + 1], vaccinations=self.vacs[: t + 1]
            )
            n_perm = self.ab.n.dynamics.perm_response(
                infections[: t + 1], vaccinations=None
            )

            s[t] = self.ab.s.dynamics.init + s_temp + s_perm
            n[t] = self.ab.n.dynamics.init + n_temp + n_perm

        return InfectionResponses(infections=infections, s_response=s, n_response=n)


@dataclasses.dataclass
class Cohort:
    """
    Args:
        random_seed: Passed to np.random.seed.
        cohort_data_path: See abdpymc.abd.TiterData.
        antibodies: Defines antibody responses.

    Attributes:
        n_inds: Number of individuals.
        n_gaps: Number of time gaps.
    """

    random_seed: int
    cohort_data_path: str
    antibodies: Antibodies = dataclasses.field(default_factory=Antibodies)

    def __post_init__(self) -> None:
        np.random.seed(self.random_seed)
        self.true = abd.TiterData.from_disk(self.cohort_data_path)
        self.n_inds, self.n_gaps = self.true.vacs.shape
        self.individuals = [
            Individual(
                pcrpos=self.true.pcrpos[i],
                vacs=self.true.vacs[i],
                ab=self.antibodies,
            )
            for i in range(self.n_inds)
        ]

    def simulate_responses(self, lam0: np.ndarray) -> None:
        """
        Simulate responses for all individuals. This method updates self.s_titer,
        self.n_titer and self.infections.

        Args:
            lam0: (n_gaps,) array containing baseline infection rates for each time gap.
        """
        infection_responses = [
            self.individuals[i].infection_responses(lam0=lam0)
            for i in range(self.n_inds)
        ]
        self.s_titer = np.array([value.s_response for value in infection_responses])
        self.n_titer = np.array([value.n_response for value in infection_responses])
        self.infections = np.array([value.infections for value in infection_responses])

    def simulate_row(self, row: pd.Series) -> dict:
        """
        Simulate an OD reading given this simulation's parameters and a row of data from
        the main cohort dataset (abdpymc.abd.TiterData.data). See
        self.simulate_dataset for more details.

        Args:
            row: pd.Series containing "measurement", "individual_i", "elapsed_months",
                "dilution", "record_id", "log_dilution", "sample_i" and "sample".
        """
        measurement = row["measurement"]
        ab = {"10222020-S": "s", "40588-V08B": "n"}[measurement]
        arr = getattr(self, f"{ab}_titer")
        simulated_titer = arr[row["individual_i"], row["elapsed_months"]]
        elisa = getattr(self.antibodies, ab).elisa
        return dict(
            od=elisa.model_od(dilution=row["log_dilution"], titer=simulated_titer),
            measurement=measurement,
            dilution=row["dilution"],
            record_id=row["record_id"],
            elapsed_months=row["elapsed_months"],
            individual_i=row["individual_i"],
            log_dilution=row["log_dilution"],
            sample_i=row["sample_i"],
            sample=row["sample"],
        )

    def simulate_dataset(self, df_true: pd.DataFrame) -> pd.DataFrame:
        """
        Simulate OD readings for an entire dataset.

        df_true provides the timing of when samples were taken ('elapsed_months' column)
        and the individual this sample was taken from ('individual_i') which are used to
        lookup the associated simulated titers. Sample dilutions and simulated titer are
        then used to model OD measurements. Other columns from df_true are also retained.

        Args:
            df_true: Dataset to model the characteristics of the simulation measurements
                on. Columns must contain "measurement", "individual_i", "elapsed_months",
                "dilution", "record_id", "log_dilution", "sample_i" and "sample".
        """
        return pd.DataFrame([self.simulate_row(row) for _, row in df_true.iterrows()])
