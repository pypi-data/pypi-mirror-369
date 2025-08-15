import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

from hydesign.assembly.hpp_assembly import hpp_base
from hydesign.costs.costs_solarX import H2Cost_comp as H2Cost
from hydesign.costs.costs_solarX import cpv_cost_comp as cpv_cost
from hydesign.costs.costs_solarX import cst_cost_comp as cst_cost
from hydesign.costs.costs_solarX import sf_cost_comp as sf_cost
from hydesign.costs.costs_solarX import shared_cost_comp as shared_cost
from hydesign.cpv.cpv import cpv_comp as cpv
from hydesign.cst.cst import cst_comp as cst
from hydesign.ems.EmsSolarX import EmsSolarX_comp as EmsSolarX
from hydesign.finance.finance_solarX import finance_solarX_comp as finance_solarX
from hydesign.h2.h2 import BiogasH2_comp as BiogasH2
from hydesign.sf.sf import sf_comp as sf


class hpp_model_solarX(hpp_base):
    """
    HPP (Hybrid Power Plant) design evaluator class
    """

    def __init__(
        self,
        sim_pars_fn=None,
        # input_ts_fn=None,  # it includes DNI, price_el_t, WS_1_t, T_1_t
        verbose=True,
        batch_size=7 * 24,
        name="",
        **kwargs,
    ):
        """
        Initialization of the hybrid power plant evaluator with parameters for geographic location and simulation options.

        Parameters
        ----------
        latitude : Latitude at the chosen location
        longitude : Longitude at the chosen location
        altitude : Altitude at the chosen location; if not provided, elevation is calculated using elevation map datasets
        sim_pars_fn : Case study input values for the HPP, stored in a YAML file
        work_dir : Working directory path for input and output files
        weeks_per_season_per_year: Number of weeks per season to sample from input data to reduce computation time (default is None, which uses all data)
        input_ts_fn : User-provided weather time series; if None, weather data is generated from ERA5 datasets
        verbose : If True, prints status and loaded values
        """
        hpp_base.__init__(self, sim_pars_fn=sim_pars_fn, wpp_efficiency=1.0, **kwargs)

        N_time = self.N_time
        sim_pars = self.sim_pars
        weather = self.weather
        dni = (
            weather["dni"] / 1e6
        )  # scaling Direct Normal Irradiance (DNI) from [W/m2] to [MW/m2]
        WS_1 = weather["WS_1"]  # Wind Speed at 1 meter hight
        weeks_per_season_per_year = sim_pars["weeks_per_season_per_year"]
        N_life = sim_pars["N_life"]
        life_h = N_life * 365 * 24  # total hours in project lifetime
        # Extract necessary data series from weather data
        price_el_t = weather["Price"]
        price_h2_t = weather.get("Price_h2", pd.Series(0, index=price_el_t.index))
        demand_q_t = weather.get("demand_q", pd.Series(0, index=price_el_t.index))
        price_biogas_t = weather.get(
            "Price_biogas", pd.Series(0, index=price_el_t.index)
        )
        price_water_t = weather.get("Price_water", pd.Series(0, index=price_el_t.index))
        price_co2_t = weather.get("Price_co2", pd.Series(0, index=price_el_t.index))

        comps = [
            (
                "sf",
                sf(
                    N_time=N_time,
                    sf_azimuth_altitude_efficiency_table=sim_pars[
                        "sf_azimuth_altitude_efficiency_table"
                    ],
                    latitude=sim_pars["latitude"],
                    longitude=sim_pars["longitude"],
                    altitude=sim_pars["altitude"],
                    dni=dni,
                ),
            ),
            # cpv (Concentrated Photovoltaic) subsystem
            (
                "cpv",
                cpv(
                    N_time=N_time,
                    cpv_efficiency=sim_pars["cpv_efficiency"],
                    p_max_cpv_mw_per_m2=sim_pars["p_max_cpv_mw_per_m2"],
                ),
            ),
            # cst (Concentrated Solar Thermal) subsystem
            (
                "cst",
                cst(
                    N_time=N_time,
                    cst_ms_receiver_efficiency_table=sim_pars[
                        "cst_ms_receiver_efficiency_table"
                    ],
                    heat_exchanger_efficiency=sim_pars["heat_exchanger_efficiency"],
                    steam_turbine_efficiency=sim_pars["steam_turbine_efficiency"],
                    Hot_molten_salt_storage_temperature=sim_pars[
                        "Hot_molten_salt_storage_temperature"
                    ],  # °C
                    Cold_molten_salt_storage_temperature=sim_pars[
                        "Cold_molten_salt_storage_temperature"
                    ],  # °C
                    hot_molten_salt_density=sim_pars[
                        "hot_molten_salt_density"
                    ],  # kg/m3
                    Cold_molten_salt_density=sim_pars[
                        "Cold_molten_salt_density"
                    ],  # kg/m3
                    Hot_molten_salt_specific_q=sim_pars[
                        "Hot_molten_salt_specific_heat"
                    ],  # kJ/kg/K
                    Cold_molten_salt_specific_q=sim_pars[
                        "Cold_molten_salt_specific_heat"
                    ],  # kJ/kg/K
                    wind_speed=WS_1,
                    flow_ms_max_cst_receiver_per_m2=sim_pars[
                        "flow_ms_max_cst_receiver_per_m2"
                    ],
                ),
            ),
            # BiogasH2 subsystem
            (
                "BiogasH2",
                BiogasH2(
                    N_time=N_time,
                    heat_mwht_per_kg_h2=sim_pars["heat_mwht_per_kg_h2"],
                    biogas_h2_mass_ratio=sim_pars["biogas_h2_mass_ratio"],
                    water_h2_mass_ratio=sim_pars["water_h2_mass_ratio"],
                    co2_h2_mass_ratio=sim_pars["co2_h2_mass_ratio"],
                ),
            ),
            # Energy management system (EMS) subsystem - designed for SolarX project
            (
                "EmsSolarX",
                EmsSolarX(
                    N_time=N_time,
                    max_el_buy_from_grid_mw=sim_pars["max_el_buy_from_grid_mw"],
                    steam_turbine_efficiency=sim_pars["steam_turbine_efficiency"],
                    biogas_h2_reactor_dni_to_heat_efficiency=sim_pars[
                        "biogas_h2_reactor_dni_to_heat_efficiency"
                    ],
                    biogas_h2_reactor_el_to_heat_efficiency=sim_pars[
                        "biogas_h2_reactor_el_to_heat_efficiency"
                    ],
                    biogas_h2_reactor_efficiency_curve=sim_pars[
                        "biogas_h2_reactor_efficiency_curve"
                    ],
                    maximum_h2_production_reactor_kg_per_m2=sim_pars[
                        "maximum_h2_production_reactor_kg_per_m2"
                    ],
                    hot_tank_efficiency=sim_pars["hot_tank_efficiency"],
                    steam_specific_heat_capacity=sim_pars[
                        "steam_specific_heat_capacity"
                    ],
                    cold_steam_temp_ms=sim_pars["cold_steam_temp_ms"],
                    hot_steam_temp_ms=sim_pars["hot_steam_temp_ms"],
                    heat_exchanger_efficiency=sim_pars["heat_exchanger_efficiency"],
                    hot_molten_salt_density=sim_pars["hot_molten_salt_density"],
                    heat_penalty_euro_per_mwht=sim_pars["heat_penalty_euro_per_mwht"],
                    weeks_per_season_per_year=weeks_per_season_per_year,
                    life_h=life_h,
                    batch_size=batch_size,
                ),
            ),
            # Cost and Finance subsystems
            (
                "sf_cost",
                sf_cost(
                    heliostat_cost_per_m2=sim_pars["heliostat_cost_per_m2"],
                    sf_opex_cost_per_m2=sim_pars["sf_opex_cost_per_m2"],
                ),
            ),
            (
                "cpv_cost",
                cpv_cost(
                    cpv_cost_per_m2=sim_pars["cpv_cost_per_m2"],
                    inverter_cost_per_MW_DC=sim_pars["cpv_inverter_cost_per_MW_DC"],
                    cpv_fixed_opex_cost_per_m2=sim_pars["cpv_fixed_opex_cost_per_m2"],
                ),
            ),
            (
                "cst_cost",
                cst_cost(
                    cst_th_collector_cost_per_m2=sim_pars[
                        "cst_th_collector_cost_per_m2"
                    ],
                    ms_installation_cost_per_m3=sim_pars["ms_installation_cost_per_m3"],
                    steam_turbine_cost_per_MW=sim_pars["steam_turbine_cost_per_MW"],
                    heat_exchnager_cost_per_MW=sim_pars["heat_exchnager_cost_per_MW"],
                    fixed_opex_per_MW=sim_pars["fixed_opex_per_MW"],
                ),
            ),
            (
                "H2Cost",
                H2Cost(
                    reactor_cost_per_m2=sim_pars[
                        "reactor_cost_per_m2"
                    ],  # Waiting for Luc input
                    maximum_h2_production_reactor_kg_per_m2=sim_pars[
                        "maximum_h2_production_reactor_kg_per_m2"
                    ],
                    el_heater_cost_kg_per_h=sim_pars[
                        "el_heater_cost_kg_per_h"
                    ],  # Waiting for Luc input
                    pipe_pump_valves_cost_kg_per_h=sim_pars[
                        "pipe_pump_valves_cost_kg_per_h"
                    ],  # Waiting for Luc input
                    psa_cost_kg_per_h=sim_pars["psa_cost_kg_per_h"],
                    carbon_capture_cost_kg_per_h=sim_pars[
                        "carbon_capture_cost_kg_per_h"
                    ],
                    dni_installation_cost_kg_per_h=sim_pars[
                        "dni_installation_cost_kg_per_h"
                    ],
                    el_installation_cost_kg_per_h=sim_pars[
                        "el_installation_cost_kg_per_h"
                    ],
                    maintenance_cost_kg_per_h=sim_pars["maintenance_cost_kg_per_h"],
                    life_h=life_h,
                ),
                {"p_biogas_h2_t": "p_biogas_h2_t_ext"},
            ),
            (
                "shared_cost",
                shared_cost(
                    grid_connection_cost_per_mw=sim_pars["grid_connection_cost_mw"],
                    grid_h2_connection_cost_per_kg_h=sim_pars[
                        "grid_h2_connection_cost_per_kg_h"
                    ],
                    grid_thermal_connection_cost_per_mwt=sim_pars[
                        "grid_thermal_connection_cost_per_mwt"
                    ],
                    land_cost_m2=sim_pars["land_cost_m2"],
                    BOS_soft_cost=sim_pars["BOS_soft_cost_m2"],
                    tower_cost_per_m=sim_pars["tower_cost_per_m"],
                ),
            ),
            (
                "finance_solarX",
                finance_solarX(
                    N_time=N_time,
                    # Depreciation curve
                    depreciation_yr=sim_pars["depreciation_yr"],
                    depreciation=sim_pars["depreciation"],
                    # Inflation curve
                    inflation_yr=sim_pars["inflation_yr"],
                    inflation=sim_pars["inflation"],
                    ref_yr_inflation=sim_pars["ref_yr_inflation"],
                    # Early paying or CAPEX Phasing
                    phasing_yr=sim_pars["phasing_yr"],
                    phasing_CAPEX=sim_pars["phasing_CAPEX"],
                    life_h=life_h,
                ),
                {"cpv_t_ext": "p_cpv_t_ext"},
            ),
        ]

        # Set up the model in OpenMDAO
        prob = self.get_prob(comps)
        prob.setup()

        # Set initial parameter values, such as system capacities, prices, and efficiencies, from simulation parameters
        # prices
        prob.set_val("price_el_t", price_el_t)
        prob.set_val("price_h2_t", price_h2_t)
        prob.set_val("demand_q_t", demand_q_t)
        prob.set_val("price_biogas_t", price_biogas_t)
        prob.set_val("price_water_t", price_water_t)
        prob.set_val("price_co2_t", price_co2_t)

        # peak hours
        prob.set_val("peak_hr_quantile", sim_pars["peak_hr_quantile"])
        prob.set_val(
            "n_full_power_hours_expected_per_day_at_peak_price",
            sim_pars["n_full_power_hours_expected_per_day_at_peak_price"],
        )

        # finances
        prob.set_val("discount_rate", sim_pars["discount_rate"])
        prob.set_val("tax_rate", sim_pars["tax_rate"])

        # cpv
        prob.set_val("cpv_dc_ac_ratio", sim_pars["cpv_dc_ac_ratio"])

        # cst
        prob.set_val("v_max_hot_ms_percentage", sim_pars["v_max_hot_ms_percentage"])
        prob.set_val("v_min_hot_ms_percentage", sim_pars["v_min_hot_ms_percentage"])

        # grid
        prob.set_val("grid_el_capacity", sim_pars["grid_el_capacity"])
        prob.set_val("grid_h2_capacity", sim_pars["grid_h2_capacity"])

        prob.set_val("tower_diameter", sim_pars["tower_diameter"])

        # Store important attributes
        self.sim_pars = sim_pars
        self.prob = prob
        self.input_ts_fn = sim_pars["input_ts_fn"]
        self.altitude = sim_pars["altitude"]
        self.dni = dni

        # Define lists of output variables and design variables for later reference in evaluation
        self.list_out_vars = [
            "NPV_over_CAPEX",
            "NPV [MEuro]",
            "IRR",
            "LCOE [Euro/MWh]",
            "LCOVE [Euro/MWh]",
            "Revenues [MEuro]",
            "CAPEX [MEuro]",
            "OPEX [MEuro]",
            "SF CAPEX [MEuro]",
            "SF OPEX [MEuro]",
            "CPV CAPEX [MEuro]",
            "CPV OPEX [MEuro]",
            "CST CAPEX [MEuro]",
            "CST OPEX [MEuro]",
            "BiogasH2 CAPEX [MEuro]",
            "BiogasH2 OPEX [MEuro]",
            "Shared CAPEX [MEuro]",
            "Shared Opex [MEuro]",
            "penalty lifetime [MEuro]",
            "AEP [GWh]",
            "AH2P [T]",
            "GUF",
            "Total curtailment [GWh]",
            "Break-even PPA price el [Euro/MWh]",
            "Break-even PPA price H2 [Euro/kg]",
            # 'Break-even PPA price Heat [Euro/MWht]',
        ]

        self.list_vars = [  # all design variables
            # sf
            "sf_area",
            "tower_height",
            # cpv
            "area_cpv_receiver_m2",
            # cst
            "heat_exchanger_capacity",
            "p_rated_st",
            "v_molten_salt_tank_m3",
            "area_cst_receiver_m2",
            # bigas_h2
            "area_dni_reactor_biogas_h2",
            "area_el_reactor_biogas_h2",
        ]

    def evaluate(
        self,
        # sizing variables
        # sf
        sf_area,
        tower_height,
        # cpv
        area_cpv_receiver_m2,
        # cst
        heat_exchanger_capacity,
        p_rated_st,
        v_molten_salt_tank_m3,
        area_cst_receiver_m2,
        # bigas_h2
        area_dni_reactor_biogas_h2,
        area_el_reactor_biogas_h2,
    ):
        """Calculating the financial metrics of the hybrid power plant project.

        Parameters
        ----------
        clearance : Distance from the ground to the tip of the blade [m]
        sp : Specific power of the turbine [W/m2]
        p_rated : Rated powe of the turbine [MW]
        Nwt : Number of wind turbines
        wind_MW_per_km2 : Wind power installation density [MW/km2]
        solar_MW : Solar AC capacity [MW]
        surface_tilt : Surface tilt of the PV panels [deg]
        surface_azimuth : Surface azimuth of the PV panels [deg]
        DC_AC_ratio : DC  AC ratio
        b_P : Battery power [MW]
        b_E_h : Battery storage duration [h]
        cost_of_battery_P_fluct_in_peak_price_ratio : Cost of battery power fluctuations in peak price ratio [Eur]

        Returns
        -------
        prob['NPV_over_CAPEX'] : Net present value over the capital expenditures
        prob['NPV'] : Net present value
        prob['IRR'] : Internal rate of return
        prob['LCOE'] : Levelized cost of energy
        prob['CAPEX'] : Total capital expenditure costs of the HPP
        prob['OPEX'] : Operational and maintenance costs of the HPP
        prob['penalty_lifetime'] : Lifetime penalty
        prob['mean_AEP']/(self.sim_pars['grid_el_capacity']*365*24) : Grid utilization factor
        self.sim_pars['grid_el_capacity'] : Grid connection [MW]
        wind_MW : Wind power plant installed capacity [MW]
        solar_MW : Solar power plant installed capacity [MW]
        b_E : Battery power [MW]
        b_P : Battery energy [MW]
        prob['total_curtailment']/1e3 : Total curtailed power [GMW]
        d : wind turbine diameter [m]
        hh : hub height of the wind turbine [m]
        self.num_batteries : Number of allowed replacements of the battery
        """
        self.inputs = [
            sf_area,
            tower_height,
            # cpv
            area_cpv_receiver_m2,
            # cst
            heat_exchanger_capacity,
            p_rated_st,
            v_molten_salt_tank_m3,
            area_cst_receiver_m2,
            # bigas_h2
            area_dni_reactor_biogas_h2,
            area_el_reactor_biogas_h2,
        ]
        prob = self.prob
        self.dni_total = self.dni * sf_area

        # sizing variables
        # sf
        prob.set_val("sf_area", sf_area)
        prob.set_val("tower_height", tower_height)

        # cpv
        prob.set_val("area_cpv_receiver_m2", area_cpv_receiver_m2)

        # cst
        prob.set_val("p_rated_st", p_rated_st)
        prob.set_val("p_rated_st", p_rated_st)
        prob.set_val("heat_exchanger_capacity", heat_exchanger_capacity)
        prob.set_val("v_molten_salt_tank_m3", v_molten_salt_tank_m3)
        prob.set_val("area_cst_receiver_m2", area_cst_receiver_m2)

        # bigas_h2
        prob.set_val("area_dni_reactor_biogas_h2", area_dni_reactor_biogas_h2)
        prob.set_val("area_el_reactor_biogas_h2", area_el_reactor_biogas_h2)

        self.prob = prob

        prob.run_model()  # execute the OpenMDAO model

        # Collect and return financial metrics, converting units where necessary
        outputs = np.hstack(
            [
                prob["NPV_over_CAPEX"],
                prob["NPV"] / 1e6,
                prob["IRR"],
                prob["LCOE"],
                prob["lcove"],
                prob["revenues"] / 1e6,
                prob["CAPEX"] / 1e6,
                prob["OPEX"] / 1e6,
                prob.get_val("finance_solarX.CAPEX_sf") / 1e6,
                prob.get_val("finance_solarX.OPEX_sf") / 1e6,
                prob.get_val("finance_solarX.CAPEX_cpv") / 1e6,
                prob.get_val("finance_solarX.OPEX_cpv") / 1e6,
                prob.get_val("finance_solarX.CAPEX_cst") / 1e6,
                prob.get_val("finance_solarX.OPEX_cst") / 1e6,
                prob.get_val("finance_solarX.CAPEX_h2") / 1e6,
                prob.get_val("finance_solarX.OPEX_h2") / 1e6,
                prob.get_val("finance_solarX.CAPEX_sh") / 1e6,
                prob.get_val("finance_solarX.OPEX_sh") / 1e6,
                prob["penalty_lifetime"] / 1e6,
                prob["mean_AEP"] / 1e3,  # [GWh]
                prob["mean_AH2P"] / 1e3,  # [T]
                # Grid Utilization factor
                prob["mean_AEP"] / (self.sim_pars["grid_el_capacity"] * 365 * 24),
                prob["total_curtailment"] / 1e3,  # [GWh]
                prob["break_even_PPA_price"],
                prob["break_even_PPA_price_h2"],
            ]
        )
        self.outputs = outputs
        return outputs

    def plot_solarX_results(self, n_hours=1 * 24, index_hour_start=0):
        prob = self.prob
        flux_sf_t = prob["sf.flux_sf_t"]
        # get data from solved hpp model
        price_el = prob.get_val("EmsSolarX.price_el_t")
        price_h2 = prob.get_val("EmsSolarX.price_h2_t")
        alpha_cpv_t = prob.get_val("EmsSolarX.alpha_cpv_t_ext")
        alpha_cst_t = prob.get_val("EmsSolarX.alpha_cst_t_ext")
        alpha_h2_t = prob.get_val("EmsSolarX.alpha_h2_t_ext")
        p_hpp_t = prob.get_val("EmsSolarX.hpp_t_ext")
        cpv_t = prob.get_val("EmsSolarX.p_cpv_t_ext")
        # p_cpv_max_dni_t = prob.get_val('EmsSolarX.p_cpv_max_dni_t_ext')
        p_st_t = prob.get_val("EmsSolarX.p_st_t_ext")
        # p_st_max_dni = prob.get_val('EmsSolarX.p_st_max_dni_t_ext')
        # p_biogas_h2_t = prob.get_val('EmsSolarX.p_biogas_h2_t_ext')
        q_t = prob.get_val("EmsSolarX.q_t_ext")
        # q_max_dni = prob.get_val('EmsSolarX.q_max_dni_t_ext')
        biogas_h2_dni = prob.get_val(
            "EmsSolarX.biogas_h2_procuded_h2_kg_in_dni_reactor_t_ext"
        )
        biogas_h2_el = prob.get_val(
            "EmsSolarX.biogas_h2_procuded_h2_kg_in_el_reactor_t_ext"
        )
        V_hot_ms_t = prob.get_val("EmsSolarX.v_hot_ms_t_ext")
        # V_tot = prob.get_val('EmsSolarX.v_molten_salt_tank_m3')

        # Create a figure with 2x2 subplots
        plt.rcParams.update(
            {
                "axes.titlesize": 18,  # Title font size (slightly larger for emphasis)
                "axes.labelsize": 16,  # X and Y label font size
                "xtick.labelsize": 14,  # X-axis tick label font size
                "ytick.labelsize": 14,  # Y-axis tick label font size
                "legend.fontsize": 14,  # Legend font size
            }
        )

        h_start = index_hour_start
        h_end = index_hour_start + n_hours
        fig, axs = plt.subplots(2, 2, figsize=(15, 10))

        # ------------------------------
        # Plot 1: Prices for resources
        # ------------------------------
        axs[0][0].step(
            range(len(price_el[h_start:h_end])),
            price_el[h_start:h_end],
            where="mid",
            color="green",
            label="Electricity [€/MWh]",
        )
        axs[0][0].step(
            range(len(price_h2[h_start:h_end])),
            price_h2[h_start:h_end],
            where="mid",
            color="purple",
            linestyle="--",
            label="H2 [€/kg]",
        )

        axs[0][0].set_ylabel("Price [€]")
        axs[0][0].legend(loc="upper left")
        axs[0][0].set_xticklabels([])
        axs[0][0].set_xlim(0, n_hours - 1)

        y_min = min(0, min(price_el[h_start:h_end]), min(price_h2[h_start:h_end]))
        axs[0][0].set_ylim(bottom=y_min - 0.002)
        # ------------------------------
        # Plot 2: Share of solar on CPV and H2
        # ------------------------------
        axs[1][0].step(
            range(len(alpha_cpv_t[h_start:h_end])),
            alpha_cpv_t[h_start:h_end],
            where="mid",
            color="green",
            label="CPV",
        )
        axs[1][0].step(
            range(len(alpha_h2_t[h_start:h_end])),
            alpha_h2_t[h_start:h_end],
            where="mid",
            color="purple",
            label="H2",
        )
        axs[1][0].step(
            range(len(alpha_cst_t[h_start:h_end])),
            alpha_cst_t[h_start:h_end],
            where="mid",
            linestyle=":",
            color="orange",
            label="CST",
        )

        axs[1][0].set_xlim(0, n_hours - 1)
        axs[1][0].set_ylabel("Share of solar flux (α)")
        axs[1][0].set_xlabel("Time [h]")
        axs[1][0].legend(loc="upper left")
        axs[1][0].set_ylim(bottom=-0.002)

        # ------------------------------
        # Plot 3: Energy generation
        # ------------------------------
        axs[0][1].step(
            range(len(flux_sf_t[h_start:h_end])),
            flux_sf_t[h_start:h_end],
            where="mid",
            color="gray",
            linestyle=":",
            linewidth=0.5,
            label="DNI_sf",
        )
        axs[0][1].step(
            range(len(p_hpp_t[h_start:h_end])),
            p_hpp_t[h_start:h_end],
            where="mid",
            color="lightgreen",
            linestyle=":",
            linewidth=1.5,
            label="P_HPP",
        )
        axs[0][1].step(
            range(len(cpv_t[h_start:h_end])),
            cpv_t[h_start:h_end],
            where="mid",
            color="green",
            label="P_CPV",
        )
        axs[0][1].step(
            range(len(q_t[h_start:h_end])),
            q_t[h_start:h_end],
            where="mid",
            color="orange",
            label="Heat",
        )
        axs[0][1].step(
            range(len(p_st_t[h_start:h_end])),
            p_st_t[h_start:h_end],
            where="mid",
            color="orange",
            linestyle="--",
            label="P_ST",
        )
        # axs[0][1].step(range(len(p_biogas_h2_t[h_start:h_end])), -p_biogas_h2_t[h_start:h_end], where='mid', color='purple', linestyle=':', linewidth=0.8,
        #                label='P_H2 (consumed)')
        axs[0][1].set_ylabel("Energy (MWh & MWht)")

        # Secondary y-axis for hydrogen production
        ax2 = axs[0][1].twinx()
        ax2.step(
            range(len(biogas_h2_dni[h_start:h_end])),
            biogas_h2_dni[h_start:h_end] / 100,
            where="mid",
            color="purple",
            linestyle="-",
            label="H2 (DNI Reactor)",
        )
        ax2.step(
            range(len(biogas_h2_el[h_start:h_end])),
            biogas_h2_el[h_start:h_end] / 100,
            where="mid",
            color="purple",
            linestyle="--",
            label="H2 (EL Reactor)",
        )
        ax2.set_ylabel("Produced H2 (kg)")

        # Sync y-axis limits
        y_limits_primary = axs[0][1].get_ylim()
        y_limits_secondary = ax2.get_ylim()
        min_limit = min(y_limits_primary[0], y_limits_secondary[0])
        max_limit = max(y_limits_primary[1], y_limits_secondary[1])
        axs[0][1].set_ylim(min_limit, max_limit)
        ax2.set_ylim(min_limit, max_limit)

        # Format the right y-axis tick labels to show original values (multiplied by 10)
        ax2.yaxis.set_major_formatter(
            mticker.FuncFormatter(lambda x, _: f"{x * 100:.0f}")
        )

        # Synchronize zooming
        ax2.callbacks.connect(
            "ylim_changed", lambda ax: axs[0][1].set_ylim(ax.get_ylim())
        )
        axs[0][1].callbacks.connect(
            "ylim_changed", lambda ax: ax2.set_ylim(ax.get_ylim())
        )

        # Combine legends from both y-axes
        handles, labels = axs[0][1].get_legend_handles_labels()
        handles2, labels2 = ax2.get_legend_handles_labels()
        all_handles = handles + handles2
        all_labels = labels + labels2
        axs[0][1].legend(all_handles, all_labels, loc="upper left")
        axs[0][1].set_xticklabels([])
        axs[0][1].set_xlim(0, n_hours - 1)

        # ------------------------------
        # Plot 4: Volume of hot molten salt
        # ------------------------------
        axs[1][1].step(
            range(len(V_hot_ms_t[h_start:h_end])),
            V_hot_ms_t[h_start:h_end],
            where="mid",
            color="orange",
            label="Hot MS",
        )

        axs[1][1].set_xlim(0, n_hours - 1)
        axs[1][1].set_ylim(
            min(V_hot_ms_t[h_start:h_end]) - 0.002,
            round(max(V_hot_ms_t[h_start:h_end])) + 10,
        )
        axs[1][1].set_ylabel("Volume [m3]")
        axs[1][1].set_xlabel("Time [h]")
        axs[1][1].legend(loc="upper left")

        return fig


if __name__ == "__main__":
    import time

    from hydesign.examples import examples_filepath

    name = "Denmark_good_solar"
    examples_sites = pd.read_csv(
        f"{examples_filepath}examples_sites.csv", index_col=0, sep=";"
    )
    ex_site = examples_sites.loc[examples_sites.name == name]
    longitude = ex_site["longitude"].values[0]
    latitude = ex_site["latitude"].values[0]
    altitude = ex_site["altitude"].values[0]
    input_ts_fn = examples_filepath + ex_site["input_ts_fn"].values[0]
    H2_demand_fn = examples_filepath + ex_site["H2_demand_col"].values[0]
    batch_size = 1 * 24
    sim_pars_fn = examples_filepath + "solarX/hpp_pars.yml"
    hpp = hpp_model_solarX(
        latitude=latitude,
        longitude=longitude,
        altitude=altitude,  # Geographical data for the site
        sim_pars_fn=sim_pars_fn,  # Simulation parameters
        input_ts_fn=input_ts_fn,  # Input time series (weather, prices, etc.)
        batch_size=batch_size,
    )
    x = [10000.0, 100, 10, 10, 10, 1000, 10, 5, 5]
    start = time.time()

    outs = hpp.evaluate(*x)

    hpp.print_design()

    end = time.time()
    print("exec. time [min]:", (end - start) / 60)
