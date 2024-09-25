import pytest
from utils.test_data.example_of_external_data import *
from utils.browser_init import init_browser, close_browser

@pytest.fixture(scope="module")
def browser_context():
    """Initialize and yield a browser context."""
    context = init_browser(headless=False)
    yield context
    close_browser(context)

def test_vue_input_in_iframe(browser_context):
    """Test to interact with an input field inside an iframe in a Vue.js app."""
    page = browser_context.new_page()
    page.goto(url)

    #Accessing iframe so we can interact with the site
    #It might be possible to set this as a selector prefix.
    iframe_locate = page.wait_for_selector('iframe')
    iframe_content = iframe_locate.content_frame()
    
    #Text input
    #Text vedle pole se vstupem bz mel být stejný jako text v poli
    iframe_content.wait_for_selector('#app input')

    input_field = iframe_content.query_selector('#app input')
    input_field.fill(input_field_value_updated)

    #Revisiting this code to comment it properly. No clue why I did this. Likely while trying literally everything and nothing worked.
    #Then I realized everything is wrapped into an inframe..
    updated_value_form = iframe_content.evaluate("() => document.querySelector('#app input').value")
    assert updated_value_form == input_field_value_updated, "The input value was not updated correctly."

    updated_value_paragraph = iframe_content.query_selector('#app p').inner_text()
    assert updated_value_paragraph == input_field_value_updated, "The input value was not updated correctly."

    #Checkbox
    #By měl zobrazovat true když je zaškrtnuté
    #By měl zobrazovat false když není zaškrtnuté

    selector = iframe_content.query_selector('input[id="checkbox"]')
    assert selector.is_checked() == True, "Checkbox not checked. Expecting: Checked."

    selector.click()
    assert selector.is_checked() == False, "Checkbox checked. Expecting: Not checked."

    #Multi checkbox
    #Text “Checked names” by mel vždy zobrazovat zaškrtnuté jméno

    checkbox_multi_1 = iframe_content.wait_for_selector('input[id="jack"]')
    checkbox_multi_2 = iframe_content.wait_for_selector('input[id="john"]')
    checkbox_multi_3 = iframe_content.wait_for_selector('input[id="mike"]')

    # Default state (first selected)
    assert checkbox_multi_1.is_checked() == True, "{checkbox_multi_1} is not checked."
    assert checkbox_multi_2.is_checked() == False, "{checkbox_multi_2} is checked."
    assert checkbox_multi_3.is_checked() == False, "{checkbox_multi_3} is checked."

    #Tried covering combinations, but the result is a bit lazy I admit.

    # None is selected
    checkbox_multi_1.click()
    assert checkbox_multi_1.is_checked() == False, "{checkbox_multi_1} is not checked. It should be."
    actual_text = iframe_content.query_selector('#app p:nth-of-type(2)').inner_text().strip()
    assert "[]" in actual_text, "Something is selected. Nothing should be selected."

    # Second is selected
    checkbox_multi_2.click()
    assert checkbox_multi_2.is_checked() == True, "{checkbox_multi_2} is checked. It shouldn't be."
    actual_text = iframe_content.query_selector('#app p:nth-of-type(2)').inner_text().strip()
    assert multi_check_list[1] in actual_text

    # Second and Third is selected
    checkbox_multi_3.click()
    assert checkbox_multi_3.is_checked() == True, "{checkbox_multi_3} is checked. It shouldn't be."
    actual_text = iframe_content.query_selector('#app p:nth-of-type(2)').inner_text().strip()
    assert multi_check_list[2] in actual_text

    #Radio
    #Text “Picked:” by mel zobrazovat vybranou možnost
    for selector_id, val in zip(input_radio_selectors, input_radio_vals):
        iframe_content.query_selector(f'input[id="{selector_id}"]').is_visible()
        picked_val = iframe_content.query_selector(f'input[id="{selector_id}"]').input_value()
        assert picked_val == val, f'Expected {picked_val} to eq {val}.'

    iframe_content.query_selector(f'input[id="{input_radio_selectors[1]}"]').click()
    assert iframe_content.query_selector(f'input[id="{selector_id}"]').input_value() == input_radio_vals[1]

    #Select
    #Text “Selected” by mel obsahovat vybranou možnost

    #Default state

    selector = iframe_content.query_selector_all('select')[0]
    assert selector.input_value() == select_vals[1], f"Expected {select_vals[1]} to be selected. Got {selector('select')[0].input_value()} instead."
    for option in select_vals:
        #Check if first option is disabled, probably not the most performance efficient approach
        if option == select_vals[0]:
            assert iframe_content.query_selector_all('select')[0].query_selector_all('option')[0].get_attribute('disabled') is not None, 'Attribute {select_vals[0]} not disabled.'
        else:
            iframe_content.query_selector_all('select')[0].select_option(option)
            assert iframe_content.locator(f"text='Selected: {option}'")

    #Multi select
    #Text “Selected” by mel vždy obsahovat vzbrané možnosti

    # Multi-option selector
    selector = iframe_content.query_selector_all('select')[1]

    multi_select_default_val = selector.input_value()
    assert multi_select_default_val == multi_select_vals[0], f"Expected value {multi_select_vals[0]} to be selected. Got {multi_select_default_val} instead."

    selector.select_option(value=multi_select_vals)
    assert iframe_content.locator(f"text='Selected: {multi_select_vals}'")

    # Due to this being just a demo, it's missing tags allowing for good selectors.
    # My choice of selectors and approaches in general isn't ideal, mostly because I was learning everything while working on this assignment. 
    # I realize there are inconsistencies and already have a few ideas how to improve the solution.

    page.close()
