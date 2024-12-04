from flask import Flask, render_template
from data_fetching.fetch_openalex import fetch_latest_research_papers
from data_fetching.fetch_world_bank import fetch_gender_equality_data, fetch_gender_equality_data_for_neighbors
# from data_fetching.fetch_dbpedia import fetch_ukrainian_gender_activists
from data_fetching.fetch_wikidata import fetch_gender_named_counts

app = Flask(__name__)

# Main country to analyze
MAIN_COUNTRY = "Ukraine"
MAIN_COUNTRY_CODE = "UA"

# Indicator codes
INDICATORS = {
    "female_population": "SP.POP.TOTL.FE.ZS",  # Female population as a percentage of total population
    "labor_force_participation_female": "SL.TLF.CACT.FE.ZS",  # Female labor force participation rate
    "labor_force_participation_male": "SL.TLF.CACT.MA.ZS",  # Male labor force participation rate
    "women_in_parliament": "SG.GEN.PARL.ZS",  # Proportion of seats held by women in national parliaments
    "unemployment_rate_female": "SL.UEM.TOTL.FE.ZS",  # Female unemployment rate
    "unemployment_rate_male": "SL.UEM.TOTL.MA.ZS",  # Male unemployment rate
    "employment_in_agriculture_female": "SL.AGR.EMPL.FE.ZS",  # Female employment in agriculture (% of female employment)
    "employment_in_industry_female": "SL.IND.EMPL.FE.ZS",  # Female employment in industry (% of female employment)
    "employment_in_services_female": "SL.SRV.EMPL.FE.ZS",  # Female employment in services (% of female employment)
    "vulnerable_employment_female": "SL.EMP.VULN.FE.ZS",  # Vulnerable employment, female (% of female employment)
    "vulnerable_employment_male": "SL.EMP.VULN.MA.ZS",  # Vulnerable employment, male (% of male employment)
    "wage_and_salaried_workers_female": "SL.EMP.WORK.FE.ZS",  # Wage and salaried workers, female (% of female employment)
    "wage_and_salaried_workers_male": "SL.EMP.WORK.MA.ZS",  # Wage and salaried workers, male (% of male employment)
    "self_employed_female": "SL.EMP.SELF.FE.ZS",  # Self-employed, female (% of female employment)
    "self_employed_male": "SL.EMP.SELF.MA.ZS",  # Self-employed, male (% of male employment)
    "literacy_rate_female_youth": "SE.ADT.1524.LT.FE.ZS",  # Literacy rate, youth female (% of females ages 15-24)
    "literacy_rate_male_youth": "SE.ADT.1524.LT.MA.ZS",  # Literacy rate, youth male (% of males ages 15-24)
    "primary_completion_rate_female": "SE.PRM.CMPT.FE.ZS",  # Primary completion rate, female (% of relevant age group)
    "primary_completion_rate_male": "SE.PRM.CMPT.MA.ZS",  # Primary completion rate, male (% of relevant age group)
    "maternal_mortality_ratio": "SH.STA.MMRT",  # Maternal mortality ratio (modeled estimate, per 100,000 live births)
    "account_ownership_female": "FX.OWN.TOTL.FE.ZS",  # Account ownership at a financial institution or with a mobile-money-service provider, female (% of female population ages 15+)
}

indicator_labels = {
    "female_population": "Female Population (%)",
    "labor_force_participation_female": "Female Labor Force Participation (%)",
    "labor_force_participation_male": "Male Labor Force Participation (%)",
    "women_in_parliament": "Women in Parliament (%)",
    "unemployment_rate_female": "Female Unemployment Rate (%)",
    "unemployment_rate_male": "Male Unemployment Rate (%)",
    "employment_in_agriculture_female": "Employment in Agriculture (Female, %)",
    "employment_in_industry_female": "Employment in Industry (Female, %)",
    "employment_in_services_female": "Employment in Services (Female, %)",
    "vulnerable_employment_female": "Vulnerable Employment (Female, %)",
    "vulnerable_employment_male": "Vulnerable Employment (Male, %)",
    "wage_and_salaried_workers_female": "Wage and Salaried Workers (Female, %)",
    "wage_and_salaried_workers_male": "Wage and Salaried Workers (Male, %)",
    "self_employed_female": "Self-Employed (Female, %)",
    "self_employed_male": "Self-Employed (Male, %)",
    "literacy_rate_female_youth": "Youth Literacy Rate (Female, %)",
    "literacy_rate_male_youth": "Youth Literacy Rate (Male, %)",
    "primary_completion_rate_female": "Primary Completion Rate (Female, %)",
    "primary_completion_rate_male": "Primary Completion Rate (Male, %)",
    "maternal_mortality_ratio": "Maternal Mortality Ratio (per 100,000)",
    "account_ownership_female": "Account Ownership (Female, %)",
}

indicator_colors = {
    "female_population": "#f48fb1",
    "labor_force_participation_female": "#81d4fa",
    "labor_force_participation_male": "#90caf9",
    "women_in_parliament": "#a5d6a7",
    "unemployment_rate_female": "#ffcc80",
    "unemployment_rate_male": "#ffab91",
    "employment_in_agriculture_female": "#c5e1a5",
    "employment_in_industry_female": "#80cbc4",
    "employment_in_services_female": "#b39ddb",
    "vulnerable_employment_female": "#e57373",
    "vulnerable_employment_male": "#fe3bc5",
    "wage_and_salaried_workers_female": "#4db6ac",
    "wage_and_salaried_workers_male": "#ceb0bd",
    "self_employed_female": "#ff8a65",
    "self_employed_male": "#f06292",
    "literacy_rate_female_youth": "#ba68c8",
    "literacy_rate_male_youth": "#9575cd",
    "primary_completion_rate_female": "#aed581",
    "primary_completion_rate_male": "#fff176",
    "maternal_mortality_ratio": "#e57373",
    "account_ownership_female": "#81c784",
}


def calculate_quick_overview_metrics(country_data, main_country):
    """
    Calculate analytical metrics for the Quick Overview section, comparing Ukraine vs. regional averages.
    :param country_data: Dictionary with data for all countries.
    :param main_country: Main country's name (e.g., "Ukraine").
    :return: Dictionary with analytical metrics for the Quick Overview section.
    """
    main_country_data = country_data.get(main_country, {})
    
    # Calculate regional averages for indicators
    regional_totals = {key: 0 for key in INDICATORS.keys()}
    regional_counts = {key: 0 for key in INDICATORS.keys()}
    
    for country, data in country_data.items():
        if country != main_country:
            for key, value in data.items():
                if value != "N/A":
                    regional_totals[key] += value
                    regional_counts[key] += 1

    regional_averages = {
        key: (regional_totals[key] / regional_counts[key] if regional_counts[key] > 0 else None)
        for key in INDICATORS.keys()
    }

    metrics = {
        "female_population": {
            "value": main_country_data.get("female_population", "N/A"),
            "difference": None,
            "ranking": None,
        },
        "labor_force_participation": {
            "female": main_country_data.get("labor_force_participation_female", "N/A"),
            "male": main_country_data.get("labor_force_participation_male", "N/A"),
            "gap": None,
        },
        "women_in_parliament": {
            "value": main_country_data.get("women_in_parliament", "N/A"),
            "regional_position": None,
        },
        "unemployment_rate": {
            "female": main_country_data.get("unemployment_rate_female", "N/A"),
            "male": main_country_data.get("unemployment_rate_male", "N/A"),
            "trend": None,
        },
        "sector_employment": {
            "most_common": None, 
            "comparison_to_region": None,
        },
        "wage_and_salaried_workers": {
            "female": main_country_data.get("wage_and_salaried_workers_female", "N/A"),
            "context": None,
        },
        "maternal_mortality_comparison": {
            "value": main_country_data.get("maternal_mortality_ratio", "N/A"),
            "comparison_to_region": (
                "Higher than region" if main_country_data.get("maternal_mortality_ratio", 0) > regional_averages.get("maternal_mortality_ratio", float('inf')) else "Lower than region"
            ),
        },
        "youth_literacy_gap": {
            "female": main_country_data.get("literacy_rate_female_youth", "N/A"),
            "male": main_country_data.get("literacy_rate_male_youth", "N/A"),
            "gap": (
                main_country_data.get("literacy_rate_female_youth", 0) - main_country_data.get("literacy_rate_male_youth", 0)
            ),
        },
        "self_employment": {
            "female": main_country_data.get("self_employed_female", "N/A"),
            "male": main_country_data.get("self_employed_male", "N/A"),
            "context": (
                f"Self-employment is higher among {'women' if main_country_data.get('self_employed_female', 0) > main_country_data.get('self_employed_male', 0) else 'men'}."
            ),
        },
        "financial_access": {
            "value": main_country_data.get("account_ownership_female", "N/A"),
            "context": f"Percentage of women with bank accounts: {main_country_data.get('account_ownership_female', 'N/A')}%",
        },
        "vulnerable_employment": {
            "female": main_country_data.get("vulnerable_employment_female", "N/A"),
            "male": main_country_data.get("vulnerable_employment_male", "N/A"),
            "context": (
                f"Women are {'more' if main_country_data.get('vulnerable_employment_female', 0) > main_country_data.get('vulnerable_employment_male', 0) else 'less'} likely to have vulnerable employment than men."
            ),
        },
    }

    # Calculate ranking for female population
    regional_female_populations = {
        country: data.get("female_population", 0)
        for country, data in country_data.items()
        if data.get("female_population", "N/A") != "N/A"
    }
    metrics["female_population"]["ranking"] = (
        sorted(regional_female_populations, key=regional_female_populations.get, reverse=True).index(main_country) + 1
    )

    # Calculate gender labor force participation gap
    if metrics["labor_force_participation"]["female"] != "N/A" and metrics["labor_force_participation"]["male"] != "N/A":
        metrics["labor_force_participation"]["gap"] = (
            metrics["labor_force_participation"]["female"] - metrics["labor_force_participation"]["male"]
        )

    # Analyze women in parliament for regional position
    if metrics["women_in_parliament"]["value"] != "N/A":
        above_region = metrics["women_in_parliament"]["value"] > regional_averages["women_in_parliament"]
        metrics["women_in_parliament"]["regional_position"] = (
            "Above Regional Average" if above_region else "Below Regional Average"
        )

    # Unemployment trend analysis
    if metrics["unemployment_rate"]["female"] != "N/A" and metrics["unemployment_rate"]["male"] != "N/A":
        if metrics["unemployment_rate"]["female"] > metrics["unemployment_rate"]["male"]:
            metrics["unemployment_rate"]["trend"] = "Higher unemployment among women"
        else:
            metrics["unemployment_rate"]["trend"] = "Lower unemployment among women"

    # Most common sector for female employment
    sectors = {
        "Agriculture": main_country_data.get("employment_in_agriculture_female", 0),
        "Industry": main_country_data.get("employment_in_industry_female", 0),
        "Services": main_country_data.get("employment_in_services_female", 0),
    }
    metrics["sector_employment"]["most_common"] = max(sectors, key=sectors.get)
    metrics["sector_employment"]["comparison_to_region"] = (
        f"More women work in {metrics['sector_employment']['most_common']} compared to other sectors regionally."
    )

    # Wage and salaried workers context
    if metrics["wage_and_salaried_workers"]["female"] != "N/A":
        metrics["wage_and_salaried_workers"]["context"] = (
            f"{metrics['wage_and_salaried_workers']['female']}% of women are in salaried positions."
        )

    return metrics

def clean_data(data, default_value=0):
    """Replace None values in data with a default value for JSON serialization."""
    if data is None:
        return {}  # Return an empty dictionary if data is None
    return {key: (value if value is not None else default_value) for key, value in data.items()}

def generate_world_bank_insights(data):
    """Generate highlights based on World Bank data."""
    highlights = {
        "top_female_population_country": None,
        "top_female_population": None,
        "top_parliament_country": None,
        "top_parliament": None,
        "lowest_labor_force_country": None,
        "lowest_labor_force": None
    }

    # Calculate highlights
    top_female_population_country = max(data, key=lambda x: data[x]['female_population'] or 0)
    top_female_population = data[top_female_population_country]['female_population']

    top_parliament_country = max(data, key=lambda x: data[x]['women_in_parliament'] or 0)
    top_parliament = data[top_parliament_country]['women_in_parliament']

    lowest_labor_force_country = min(data, key=lambda x: data[x]['labor_force_participation_female'] or float('inf'))
    lowest_labor_force = data[lowest_labor_force_country]['labor_force_participation_female']

    # Assign highlights
    highlights.update({
        "top_female_population_country": top_female_population_country,
        "top_female_population": top_female_population,
        "top_parliament_country": top_parliament_country,
        "top_parliament": top_parliament,
        "lowest_labor_force_country": lowest_labor_force_country,
        "lowest_labor_force": lowest_labor_force
    })

    return highlights


from concurrent.futures import ThreadPoolExecutor

@app.route('/')
def index():
    # Define the tasks to run concurrently
    with ThreadPoolExecutor() as executor:
        # Fetch main country data
        main_country_future = executor.submit(
            lambda: clean_data({
                indicator: fetch_gender_equality_data(MAIN_COUNTRY_CODE, code)
                for indicator, code in INDICATORS.items()
            })
        )

        # Fetch neighboring countries' data
        neighbors_data_future = executor.submit(
            lambda: fetch_gender_equality_data_for_neighbors(MAIN_COUNTRY_CODE, INDICATORS)
        )

        # Fetch activists from DBPedia
        # activists_future = executor.submit(fetch_ukrainian_gender_activists)

        # Fetch counts of streets/buildings named after genders
        gender_named_counts_future = executor.submit(fetch_gender_named_counts)

        # Fetch latest research papers
        research_papers_future = executor.submit(fetch_latest_research_papers)

    # Collect the results
    main_country_data = main_country_future.result()
    neighbors_data = neighbors_data_future.result() or {}
    # activists = activists_future.result()
    gender_named_counts = gender_named_counts_future.result()
    research_papers = research_papers_future.result()

    # Clean and update the country data
    cleaned_neighbors_data = {country: clean_data(metrics) for country, metrics in neighbors_data.items()}
    country_data = {MAIN_COUNTRY: main_country_data}
    country_data.update(cleaned_neighbors_data)

    # Calculate Quick Overview Metrics
    quick_overview_metrics = calculate_quick_overview_metrics(country_data, MAIN_COUNTRY)

    # Generate insights and highlights
    world_bank_highlights = generate_world_bank_insights(country_data)

    # Pass the data to the HTML template for rendering
    return render_template(
        'index.html',
        data=country_data,
        # activists=activists,
        gender_named_counts=gender_named_counts,
        research_papers=research_papers,
        world_bank_highlights=world_bank_highlights,
        indicator_labels=indicator_labels,
        indicator_colors=indicator_colors,
        quick_overview_metrics=quick_overview_metrics,
    )

if __name__ == '__main__':
    app.run(debug=True)
