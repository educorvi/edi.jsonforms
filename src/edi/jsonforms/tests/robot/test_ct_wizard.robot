# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s edi.jsonforms -t test_wizard.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src edi.jsonforms.testing.EDI_JSONFORMS_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/edi/jsonforms/tests/robot/test_wizard.robot
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

Scenario: As a site administrator I can add a Wizard
  Given a logged-in site administrator
    and an add Wizard form
   When I type 'My Wizard' into the title field
    and I submit the form
   Then a Wizard with the title 'My Wizard' has been created

Scenario: As a site administrator I can view a Wizard
  Given a logged-in site administrator
    and a Wizard 'My Wizard'
   When I go to the Wizard view
   Then I can see the Wizard title 'My Wizard'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add Wizard form
  Go To  ${PLONE_URL}/++add++Wizard

a Wizard 'My Wizard'
  Create content  type=Wizard  id=my-wizard  title=My Wizard

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the Wizard view
  Go To  ${PLONE_URL}/my-wizard
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a Wizard with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the Wizard title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
