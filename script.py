from selenium import webdriver
from axe_selenium_python import Axe

def test_site(url: str):
    # Add the path the geckodriver you downloaded earlier
    # The following is an example
    driver = webdriver.Firefox()
    driver.get(url)
    axe = Axe(driver)
    # Inject axe-core javascript into page.
    axe.inject()
    # Run axe accessibility checks.
    results = axe.run()
    # Write results to file
    axe.write_results(results, 'pleasework.json')
    driver.close()
    # Assert no violations are found
    assert len(results["violations"]) == 0, axe.report(results["violations"])



test_site("http://natalieisawesome.com/")
