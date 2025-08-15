# import glob
# import os
# import time

import matplotlib.pyplot as plt

# basic libraries
import numpy as np

# from numpy import newaxis as na
import numpy_financial as npf

# import seaborn as sns
import openmdao.api as om
import pandas as pd

from hydesign.finance.finance import calculate_revenues, get_inflation_index

# import yaml
# import scipy as sp
from hydesign.openmdao_wrapper import ComponentWrapper


class finance:
    """Pure Python Hybrid power plant financial model to estimate the overall profitability of the hybrid power plant.
    It considers different weighted average costs of capital (WACC) for wind, PV and battery. The model calculates
    the yearly cashflow as a function of the average revenue over the year, the tax rate and WACC after tax
    ( = weighted sum of the wind, solar, battery, and electrical infrastracture WACC). Net present value (NPV)
    and levelized cost of energy (LCOE) and Cost of valued energy (COVE) are then be calculated using the calculates WACC as the discount rate, as well
    as the internal rate of return (IRR).
    """

    def __init__(
        self,
        N_limit,
        life_y,
        N_time,
        life_h,
        # Depreciation curve
        depreciation_yr,
        depreciation,
        depre_rate,
        # Inflation curve
        inflation_yr,
        inflation,
        ref_yr_inflation,
        # # Early paying or CAPEX Phasing
        # phasing_yr,
        # phasing_CAPEX,
    ):
        """Initialization of the HPP finance model

        Parameters
        ----------
        N_limit : Maximum number of year of delta_life (15 years)
        life_y : Number in years of the lifetime of each plant (25 years)
        N_time : Number of hours in the representative dataset
        life_h : Lifetime of the plant in hours
        delta_life : difference beteewn the two plants in years

        """
        # super().__init__()
        self.N_limit = int(N_limit)
        self.life_y = int(life_y)
        self.N_time = int(N_time)
        self.life_h = int(life_h)

        # Depreciation curve
        self.depreciation_yr = depreciation_yr
        self.depreciation = depreciation
        self.depre_rate = depre_rate

        # Inflation curve
        self.inflation_yr = inflation_yr
        self.inflation = inflation
        self.ref_yr_inflation = ref_yr_inflation

        # # Early paying or CAPEX Phasing
        # self.phasing_yr = phasing_yr
        # self.phasing_CAPEX = phasing_CAPEX

    # def setup(self):
    #     self.add_input(
    #         'life_h',
    #         desc="Lifetime length in hours",
    #         units='h')

    #     self.add_input('delta_life',
    #                    desc="Years between the starting of operations of the existing plant and the new plant",
    #                    val=1)

    #     self.add_input('price_t_ext',
    #                    desc="Electricity price time series",
    #                    shape=[self.life_h])

    #     self.add_input('hpp_t_with_deg',
    #                    desc="HPP power time series",
    #                    units='MW',
    #                    shape=[self.life_h])

    #     self.add_input('penalty_t',
    #                    desc="penalty for not reaching expected energy productin at peak hours",
    #                    shape=[self.life_h])

    #     self.add_input('CAPEX_w',
    #                    desc="CAPEX wpp")
    #     self.add_input('OPEX_w',
    #                    desc="OPEX wpp")

    #     self.add_input('CAPEX_s',
    #                    desc="CAPEX solar pvp")
    #     self.add_input('OPEX_s',
    #                    desc="OPEX solar pvp")

    #     self.add_input('CAPEX_b',
    #                    desc="CAPEX battery")
    #     self.add_input('OPEX_b',
    #                    desc="OPEX battery")

    #     self.add_input('CAPEX_el_w',
    #                    desc="CAPEX electrical infrastructure for wind and batteries")
    #     self.add_input('CAPEX_el_s',
    #                    desc="CAPEX electrical infrastructure for PV")
    #     self.add_input('OPEX_el',
    #                    desc="OPEX electrical infrastructure")

    #     self.add_input('decommissioning_cost_tot_w',
    #                     desc="Decommissioning cost of the entire wind plant")
    #     self.add_input('decommissioning_cost_tot_s',
    #                     desc="Decommissioning cost of the entire PV plant")

    #     self.add_input('hpp_WACC',
    #                    desc="After tax WACC for hybrid power plant")

    #     self.add_input('tax_rate',
    #                    desc="Corporate tax rate")

    #     self.add_output('CAPEX',
    #                     desc="CAPEX")

    #     self.add_output('OPEX',
    #                     desc="OPEX")

    #     self.add_output('NPV',
    #                     desc="NPV")

    #     self.add_output('IRR',
    #                     desc="IRR")

    #     self.add_output('NPV_over_CAPEX',
    #                     desc="NPV/CAPEX")

    #     self.add_output('mean_AEP',
    #                     desc="mean AEP")

    #     self.add_output('LCOE',
    #                     desc="LCOE")

    #     self.add_output('COVE',
    #                     desc="COVE")

    #     self.add_output('penalty_lifetime',
    #                     desc="penalty_lifetime")

    #     self.add_output('break_even_PPA_price',
    #                     desc='PPA price of electricity that results in NPV=0 with the given hybrid power plant configuration and operation',
    #                     val=0)

    # def setup_partials(self):
    #     self.declare_partials('*', '*', method='fd')

    def compute(
        self,
        life_h,
        delta_life,
        price_t_ext,
        hpp_t_with_deg,
        penalty_t,
        CAPEX_w,
        OPEX_w,
        CAPEX_s,
        OPEX_s,
        CAPEX_b,
        OPEX_b,
        CAPEX_el_w,
        CAPEX_el_s,
        decommissioning_cost_tot_s,
        hpp_WACC,
        tax_rate,
        **kwargs,
    ):
        """Calculating the financial metrics of the hybrid power plant project.

        Parameters
        ----------
        price_t_ext : Electricity price time series [Eur]
        hpp_t_with_deg : HPP power time series [MW]
        penalty_t : penalty for not reaching expected energy productin at peak hours [Eur]
        CAPEX_w : CAPEX of the wind power plant
        OPEX_w : OPEX of the wind power plant
        CAPEX_s : CAPEX of the solar power plant
        OPEX_s : OPEX of solar power plant
        CAPEX_b : CAPEX of the battery
        OPEX_b : OPEX of the battery
        CAPEX_sh :  CAPEX of the shared electrical infrastracture
        OPEX_sh : OPEX of the shared electrical infrastracture

        decommissioning_cost_tot_w : Decommissioning cost of the entire wind plant
        decommissioning_cost_tot_w : Decommissioning cost of the entire PV plant

        wind_WACC : After tax WACC for onshore WT
        solar_WACC : After tax WACC for solar PV
        battery_WACC: After tax WACC for stationary storge li-ion batteries
        tax_rate : Corporate tax rate

        Returns
        -------
        CAPEX : Total capital expenditure costs of the HPP
        OPEX : Operational and maintenance costs of the HPP
        NPV : Net present value
        IRR : Internal rate of return
        NPV_over_CAPEX : NPV over CAPEX
        mean_AEP : Mean annual energy production
        LCOE : Levelized cost of energy
        COVE : Cost of valued energy
        penalty_lifetime : total penalty
        """

        # delta_life = int(inputs['delta_life'][0])
        delta_life = int(delta_life)

        N_limit = int(self.N_limit)
        life_y = int(self.life_y)
        N_time = int(self.N_time)
        life_h = self.life_h
        life_yr = int(np.ceil(life_h / N_time))

        depreciation_yr = self.depreciation_yr
        depreciation = self.depreciation
        depre_rate = self.depre_rate

        inflation_yr = self.inflation_yr
        inflation = self.inflation
        ref_yr_inflation = self.ref_yr_inflation

        # phasing_yr = self.phasing_yr
        # phasing_CAPEX = self.phasing_CAPEX

        df = pd.DataFrame()

        # df['hpp_t'] = inputs['hpp_t_with_deg']
        df["hpp_t"] = hpp_t_with_deg
        # df['price_t'] = inputs['price_t_ext']
        # df['penalty_t'] = inputs['penalty_t']
        df["penalty_t"] = penalty_t
        # df['revenue'] = df['hpp_t'] * df['price_t'] - df['penalty_t']

        df["i_year"] = np.hstack([np.array([ii] * N_time) for ii in range(life_yr)])[
            :life_h
        ]

        # Compute yearly revenues and cashflow
        # revenues = calculate_revenues(inputs['price_t_ext'], df)
        revenues = calculate_revenues(price_t_ext, df)

        # Construction of the OPEX vector along the lifetime
        # OPEX_only_pv = inputs['OPEX_s']

        # OPEX_wind = inputs['OPEX_w'] + \
        #             inputs['OPEX_b']

        OPEX_only_pv = OPEX_s

        OPEX_wind = OPEX_w + OPEX_b

        OPEX = OPEX_only_pv + OPEX_wind  # Total OPEX

        # Definition of the CAPEX and OPEX as vectors
        OPEX_vec = np.concatenate(
            (
                np.zeros(1),
                np.ones(delta_life) * OPEX_only_pv,
                np.ones(life_y - delta_life) * OPEX,
                np.ones(delta_life) * OPEX_wind,
                np.zeros(N_limit - delta_life),
            )
        )

        # Construction of the CAPEX vector along the lifetime
        # CAPEX_only_pv = inputs['CAPEX_s'] + \
        #                   inputs['CAPEX_el_s']

        # CAPEX_wind = inputs['CAPEX_w'] + inputs['CAPEX_el_w'] + inputs['CAPEX_b']

        CAPEX_only_pv = CAPEX_s + CAPEX_el_s

        CAPEX_wind = CAPEX_w + CAPEX_el_w + CAPEX_b

        CAPEX = (
            CAPEX_only_pv + CAPEX_wind
        )  # This is the total CAPEX, used to calculate NPV/CAPEX

        CAPEX_vec = np.zeros(len(OPEX_vec))
        CAPEX_vec[delta_life] = CAPEX_wind[0]
        CAPEX_vec[0] = CAPEX_only_pv[0]

        # Definition of the CAPEX vector to calculate the depraciation (batteries are depreciated just the first 25 years)
        CAPEX_for_depre = np.insert(
            np.concatenate(
                (
                    np.ones(delta_life) * CAPEX_only_pv,
                    np.ones(life_y - delta_life) * CAPEX,
                    np.ones(delta_life) * CAPEX_wind,
                    np.zeros(N_limit - delta_life),
                )
            ),
            0,
            0,
        )

        # Definition of the decommissioning cost vector
        # decommissioning_vec = np.concatenate((np.zeros(life_y), np.ones(1) * inputs['decommissioning_cost_tot_s'], np.zeros(N_limit)))
        decommissioning_vec = np.concatenate(
            (
                np.zeros(life_y),
                np.ones(1) * decommissioning_cost_tot_s,
                np.zeros(N_limit),
            )
        )

        # Discount rate
        # hpp_discount_factor = inputs['hpp_WACC']
        hpp_discount_factor = hpp_WACC

        # len of revenues = years of life
        iy = (
            np.arange(len(revenues)) + 1
        )  # Plus becasue the year zero is added externally in the NPV and IRR calculations

        # Compute inflation, all cahsflow are in nominal prices
        inflation_index = get_inflation_index(
            yr=np.arange(
                len(revenues) + 1
            ),  # It includes t=0, to compute the reference
            inflation_yr=inflation_yr,
            inflation=inflation,
            ref_yr_inflation=ref_yr_inflation,
        )

        revenues = revenues.values.flatten()
        outputs = {}
        outputs["CAPEX"] = CAPEX
        outputs["OPEX"] = OPEX

        # We need to add DEVEX
        DEVEX = 0

        # Calculate the
        NPV, IRR = calculate_NPV_IRR(
            delta_life=delta_life,
            Net_revenue_t=np.insert(revenues, 0, 0),
            investment_cost=CAPEX,
            maintenance_cost_per_year=OPEX_vec,
            capex_vector=CAPEX_vec,
            capex_for_depreciation=CAPEX_for_depre,
            # tax_rate=inputs['tax_rate'][0],
            tax_rate=tax_rate,
            discount_rate=hpp_discount_factor,
            depreciation_yr=depreciation_yr,
            depreciation=depreciation,
            depre_rate=depre_rate,
            development_cost=DEVEX,
            decommissioning_vec=decommissioning_vec,
            inflation_index=inflation_index,
        )

        outputs["NPV"] = NPV
        outputs["IRR"] = IRR
        outputs["NPV_over_CAPEX"] = NPV / CAPEX

        level_costs = np.sum(OPEX / (1 + hpp_discount_factor) ** iy) + CAPEX
        AEP_per_year = df.groupby("i_year").hpp_t.mean() * 365 * 24
        level_AEP = np.sum(AEP_per_year / (1 + hpp_discount_factor) ** iy)

        mean_AEP_per_year = np.mean(AEP_per_year)
        if level_AEP > 0:
            outputs["LCOE"] = level_costs / (level_AEP)  # in Euro/MWh
        else:
            outputs["LCOE"] = 1e6

        revenue_per_year = df.groupby("i_year").revenue.mean() * 365 * 24
        mean_revenue_per_year = np.mean(revenue_per_year[revenue_per_year != 0])

        outputs["COVE"] = level_costs / (mean_revenue_per_year)
        outputs["mean_AEP"] = mean_AEP_per_year

        outputs["penalty_lifetime"] = df["penalty_t"].sum()
        outputs["break_even_PPA_price"] = 5  # break_even_PPA_price
        output_keys = [
            "CAPEX",
            "OPEX",
            "NPV",
            "IRR",
            "NPV_over_CAPEX",
            "mean_AEP",
            "LCOE",
            "COVE",
            "penalty_lifetime",
            "break_even_PPA_price",
        ]
        return [outputs[o] for o in output_keys]


class finance_comp(ComponentWrapper):
    def __init__(self, **inst_inp):
        life_h = inst_inp["life_h"]
        model = finance(**inst_inp)
        # key_map_dict = {'CAPEX_sh_w':'CAPEX_el_w','CAPEX_sh_s':'CAPEX_el_s','penalty_t_with_deg':'penalty_t',}
        # def func(**inputs):
        #     inputs = {(key_map_dict[k] if k in key_map_dict else k):v  for (k,v) in inputs.items()}
        #     return Finance.compute(**inputs)
        super().__init__(
            inputs=[
                ("life_h", {"units": "h", "desc": "Lifetime length in hours"}),
                (
                    "delta_life",
                    {
                        "desc": "Years between the starting of operations of the existing plant and the new plant",
                        "val": 1,
                    },
                ),
                (
                    "price_t_ext",
                    {"desc": "Electricity price time series", "shape": [life_h]},
                ),
                (
                    "hpp_t_with_deg",
                    {"desc": "HPP power time series", "units": "MW", "shape": [life_h]},
                ),
                (
                    "penalty_t",
                    {
                        "desc": "penalty for not reaching expected energy productin at peak hours",
                        "shape": [life_h],
                    },
                ),
                ("CAPEX_w", {"desc": "CAPEX wpp"}),
                ("OPEX_w", {"desc": "OPEX wpp"}),
                ("CAPEX_s", {"desc": "CAPEX solar pvp"}),
                ("OPEX_s", {"desc": "OPEX solar pvp"}),
                ("CAPEX_b", {"desc": "CAPEX battery"}),
                ("OPEX_b", {"desc": "OPEX battery"}),
                (
                    "CAPEX_el_w",
                    {"desc": "CAPEX electrical infrastructure for wind and batteries"},
                ),
                ("CAPEX_el_s", {"desc": "CAPEX electrical infrastructure for PV"}),
                (
                    "decommissioning_cost_tot_w",
                    {"desc": "Decommissioning cost of the entire wind plant"},
                ),
                (
                    "decommissioning_cost_tot_s",
                    {"desc": "Decommissioning cost of the entire PV plant"},
                ),
                ("hpp_WACC", {"desc": "After tax WACC for hybrid power plant"}),
                ("tax_rate", {"desc": "Corporate tax rate"}),
            ],
            outputs=[
                ("CAPEX", {"desc": "Total capital expenditure costs of the HPP"}),
                ("OPEX", {"desc": "Operational and maintenance costs of the HPP"}),
                ("NPV", {"desc": "Net present value"}),
                ("IRR", {"desc": "Internal rate of return"}),
                ("NPV_over_CAPEX", {"desc": "NPV over CAPEX"}),
                ("mean_AEP", {"desc": "Mean annual energy production"}),
                ("LCOE", {"desc": "Levelized cost of energy"}),
                ("COVE", {"desc": "Cost of valued energy"}),
                ("penalty_lifetime", {"desc": "total penalty"}),
                (
                    "break_even_PPA_price",
                    {
                        "desc": "PPA price of electricity that results in NPV=0 with the given hybrid power plant configuration and operation",
                        "val": 0,
                    },
                ),
            ],
            function=model.compute,
            partial_options=[{"dependent": False, "val": 0}],
        )


# -----------------------------------------------------------------------
# Auxiliar functions for financial modelling
# -----------------------------------------------------------------------


def calculate_NPV_IRR(
    delta_life,
    Net_revenue_t,
    investment_cost,
    maintenance_cost_per_year,
    capex_vector,
    capex_for_depreciation,
    tax_rate,
    discount_rate,
    depreciation_yr,
    depreciation,
    depre_rate,
    development_cost,
    decommissioning_vec,
    inflation_index,
    plot=False,
):
    """A function to estimate the yearly cashflow using the net revenue time series, and the yearly OPEX costs.
    It then calculates the NPV and IRR using the yearly cashlow, the CAPEX, the WACC after tax, and the tax rate.

    Parameters
    ----------
    delta_life : Number of years between the start of operations of the first and second plants
    Net_revenue_t : Net revenue time series
    investment_cost : Capital costs
    maintenance_cost_per_year : yearly operation and maintenance costs
    tax_rate : tax rate
    discount_rate : Discount rate
    depreciation_yr : Depreciation curve (x-axis) time in years
    depreciation : Depreciation curve at the given times
    depre_rate : Straight line depreciation rate
    development_cost : DEVEX
    decommissioning_vec : vector containing the decommissioning costs over time
    inflation_index : Yearly Inflation index time-sereis

    Returns
    -------
    NPV : Net present value
    IRR : Internal rate of return
    """

    # yr = np.arange(len(Net_revenue_t))  # extra year to start at 0 and end at end of lifetime.

    # EBITDA: earnings before interest and taxes in nominal prices
    EBITDA = (Net_revenue_t - maintenance_cost_per_year) * inflation_index

    # EBIT taxable income
    depreciation_on_each_year = depre_rate * capex_for_depreciation
    EBIT = EBITDA - depreciation_on_each_year

    # Taxes
    Taxes = np.zeros(len(EBIT))

    for ii in range(1, len(EBIT)):
        if EBIT[ii] <= 0:
            Taxes[ii] = 0
        else:
            Taxes[ii] = EBIT[ii] * tax_rate

    Net_income = EBITDA - Taxes

    Income_minus_capex = Net_income - capex_vector
    Cashflow = Income_minus_capex - decommissioning_vec

    # Bar plot for the cashflows
    if plot:
        opex = -maintenance_cost_per_year * inflation_index
        revenue = Net_revenue_t * inflation_index
        tax_vec = -Taxes
        capex_vec_p = np.zeros(len(capex_vector))
        capex_vec_p[0] = -capex_vector[0]
        capex_vec_w = np.zeros(len(capex_vector))
        capex_vec_w[delta_life] = -capex_vector[delta_life]

        indices = np.arange(len(Cashflow))
        plt.figure(figsize=(10, 6))
        plt.bar(indices, revenue, color="green", label="Revenues", alpha=0.7)
        plt.bar(indices, opex, color="orange", label="OPEX", alpha=0.7)
        plt.bar(indices, tax_vec, bottom=opex, color="blue", label="Taxes", alpha=0.7)
        plt.bar(indices, capex_vec_w, color="red", label="CAPEX wind", alpha=0.7)
        plt.bar(
            indices,
            capex_vec_p,
            bottom=tax_vec + opex,
            color="magenta",
            label="CAPEX PV and batteries",
            alpha=0.7,
        )
        plt.bar(
            indices,
            -decommissioning_vec,
            bottom=tax_vec + opex,
            color="purple",
            label="Decommissioning of WT",
            alpha=0.7,
        )
        plt.title("Cashflows by Year")
        plt.xlabel("Year")
        plt.ylabel("Amount (MEur)")
        plt.legend()
        plt.grid(axis="y")
        plt.show()

    NPV = npf.npv(discount_rate, Cashflow)
    if NPV > 0:
        IRR = npf.irr(Cashflow)
    else:
        IRR = 0
    return NPV, IRR
