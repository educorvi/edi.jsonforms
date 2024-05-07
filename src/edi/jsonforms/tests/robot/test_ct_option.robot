# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s edi.jsonforms -t test_option.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src edi.jsonforms.testing.EDI_JSONFORMS_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/edi/jsonforms/tests/robot/test_option.robot
#
# See the http://docs.plone.org for further details (search for robot
# framework).
#
# ============================================================================

*** Settings *****************************************************************

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***************************************************************

Scenario: As a site administrator I can add a Option
  Given a logged-in site administrator
    and an add SelectionField form
   When I type 'My Option' into the title field
    and I submit the form
   Then a Option with the title 'My Option' has been created

Scenario: As a site administrator I can view a Option
  Given a logged-in site administrator
    and a Option 'My Option'
   When I go to the Option view
   Then I can see the Option title 'My Option'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add SelectionField form
  Go To  ${PLONE_URL}/++add++SelectionField

a Option 'My Option'
  Create content  type=SelectionField  id=my-option  title=My Option

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the Option view
  Go To  ${PLONE_URL}/my-option
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a Option with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the Option title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
