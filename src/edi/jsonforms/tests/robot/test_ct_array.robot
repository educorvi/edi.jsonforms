# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s edi.jsonforms -t test_array.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src edi.jsonforms.testing.EDI_JSONFORMS_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/edi/jsonforms/tests/robot/test_array.robot
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

Scenario: As a site administrator I can add a Array
  Given a logged-in site administrator
    and an add Form form
   When I type 'My Array' into the title field
    and I submit the form
   Then a Array with the title 'My Array' has been created

Scenario: As a site administrator I can view a Array
  Given a logged-in site administrator
    and a Array 'My Array'
   When I go to the Array view
   Then I can see the Array title 'My Array'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add Form form
  Go To  ${PLONE_URL}/++add++Form

a Array 'My Array'
  Create content  type=Form  id=my-array  title=My Array

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the Array view
  Go To  ${PLONE_URL}/my-array
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a Array with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the Array title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
