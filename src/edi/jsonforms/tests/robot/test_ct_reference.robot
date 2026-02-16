# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s edi.jsonforms -t test_reference.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src edi.jsonforms.testing.EDI_JSONFORMS_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/edi/jsonforms/tests/robot/test_reference.robot
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

Scenario: As a site administrator I can add a Reference
  Given a logged-in site administrator
    and an add Form form
   When I type 'My Reference' into the title field
    and I submit the form
   Then a Reference with the title 'My Reference' has been created

Scenario: As a site administrator I can view a Reference
  Given a logged-in site administrator
    and a Reference 'My Reference'
   When I go to the Reference view
   Then I can see the Reference title 'My Reference'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add Form form
  Go To  ${PLONE_URL}/++add++Form

a Reference 'My Reference'
  Create content  type=Form  id=my-reference  title=My Reference

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the Reference view
  Go To  ${PLONE_URL}/my-reference
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a Reference with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the Reference title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
