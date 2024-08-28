# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s edi.jsonforms -t test_complex.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src edi.jsonforms.testing.EDI_JSONFORMS_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/edi/jsonforms/tests/robot/test_complex.robot
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

Scenario: As a site administrator I can add a Complex
  Given a logged-in site administrator
    and an add Form form
   When I type 'My Complex' into the title field
    and I submit the form
   Then a Complex with the title 'My Complex' has been created

Scenario: As a site administrator I can view a Complex
  Given a logged-in site administrator
    and a Complex 'My Complex'
   When I go to the Complex view
   Then I can see the Complex title 'My Complex'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add Form form
  Go To  ${PLONE_URL}/++add++Form

a Complex 'My Complex'
  Create content  type=Form  id=my-complex  title=My Complex

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the Complex view
  Go To  ${PLONE_URL}/my-complex
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a Complex with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the Complex title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
