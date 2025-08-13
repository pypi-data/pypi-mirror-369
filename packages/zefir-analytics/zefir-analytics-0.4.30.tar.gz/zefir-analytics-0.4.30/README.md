# Zefir Analytics

The Zefir Analytics module was created by the authors of PyZefir for relatively inexpensive processing or 
conversion of raw data into user-friendly condition, such as a report or a set of graphs. Also, this module is a set 
of computational methods used in the endpoints of the Zefir Backend repository.

## Setup Development Environment

Install repository from global pip index:
```bash
pip install zefir-analytics
```

### Make setup

Check if make is already installed
```bash
make --version
```
If not, install make
```bash
sudo apt install make 
```

## Make stages

Install virtual environment and all dependencies
```bash
make install
```
Run linters check (black, pylama)
```bash
make lint
```
Run unit and fast integration tests (runs lint stage before)
```bash
Make unit
```
Run integration tests (runs lint and unit stages before)
```bash
make test
```
Remove temporary directories such as .venv, .mypy_cache, .pytest_cache etc.
```bash
make clean
```
## Available methods in Zefir Engine objects
* source_params:
  * get_capex_opex
  * get_costs_per_tech_type
  * get_dump_energy_sum
  * get_emission
  * get_ets_cost
  * get_fuel_availability_per_tech
  * get_fuel_cost
  * get_fuel_cost_per_tech
  * get_fuel_usage
  * get_generation_demand
  * get_generation_sum
  * get_installed_capacity
  * get_load_sum
  * get_var_costs
* aggregated_consumer_params:
  * get_aggregate_elements_type_attachments
  * get_aggregate_parameters
  * get_fractions
  * get_n_consumers
  * get_total_yearly_energy_usage
  * get_yearly_energy_usage
* lbs_params:
  * get_lbs_capacity
  * get_lbs_fraction
* line_params:
  * get_capacity
  * get_flow
  * get_transmission_fee
