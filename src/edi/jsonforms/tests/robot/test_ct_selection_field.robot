# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s edi.jsonforms -t test_selection_field.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src edi.jsonforms.testing.EDI_JSONFORMS_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/edi/jsonforms/tests/robot/test_selection_field.robot
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

Scenario: As a site administrator I can add a SelectionField
  Given a logged-in site administrator
    and an add Form form
   When I type 'My SelectionField' into the title field
    and I submit the form
   Then a SelectionField with the title 'My SelectionField' has been created

Scenario: As a site administrator I can view a SelectionField
  Given a logged-in site administrator
    and a SelectionField 'My SelectionField'
   When I go to the SelectionField view
   Then I can see the SelectionField title 'My SelectionField'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add Form form
  Go To  ${PLONE_URL}/++add++Form

a SelectionField 'My SelectionField'
  Create content  type=Form  id=my-selection_field  title=My SelectionField

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the SelectionField view
  Go To  ${PLONE_URL}/my-selection_field
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a SelectionField with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the SelectionField title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
